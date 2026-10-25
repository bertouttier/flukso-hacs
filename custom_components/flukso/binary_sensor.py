"""Flukso binary sensor."""

from __future__ import annotations

import logging
from datetime import datetime

from homeassistant.components import mqtt
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.event import async_call_later

from . import FluksoConfigEntry
from .const import MOTION_OFF_DELAY
from .discovery import FluksoEntityConfig, get_binary_sensor_configs, parse_value
from .entity import FluksoEntity

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: FluksoConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Flukso binary sensors."""
    config = entry.runtime_data
    async_add_entities(
        FluksoBinarySensor(config.device_hash, entity_config)
        for entity_config in get_binary_sensor_configs(config)
    )


class FluksoBinarySensor(FluksoEntity, BinarySensorEntity):
    """A kube movement, vibration or error sensor.

    Movement and vibration kubes only publish when they trigger, so the sensor
    turns on for every message and off again after MOTION_OFF_DELAY seconds.
    """

    _cancel_off: CALLBACK_TYPE | None = None

    def __init__(self, device_hash: str, config: FluksoEntityConfig) -> None:
        """Initialize the binary sensor."""
        super().__init__(device_hash, config)
        self._attr_device_class = (
            BinarySensorDeviceClass(config.device_class)
            if config.device_class
            else None
        )
        if config.sensor_type != "error":
            self._attr_is_on = False

    async def async_will_remove_from_hass(self) -> None:
        """Cancel a pending off timer."""
        self._cancel_off_timer()

    @callback
    def _cancel_off_timer(self) -> None:
        if self._cancel_off is not None:
            self._cancel_off()
            self._cancel_off = None

    @callback
    def _turn_off(self, _now: datetime) -> None:
        self._cancel_off = None
        self._attr_is_on = False
        self.async_write_ha_state()

    @callback
    def _message_received(self, msg: mqtt.ReceiveMessage) -> None:
        if self._config.sensor_type == "error":
            try:
                is_on = parse_value(msg.payload) > 0
            except (ValueError, IndexError, UnicodeDecodeError):
                _LOGGER.debug(
                    "Ignoring invalid payload on %s: %s", msg.topic, msg.payload
                )
                return
            if is_on == self._attr_is_on:
                return
            self._attr_is_on = is_on
            self.async_write_ha_state()
            return

        self._cancel_off_timer()
        self._cancel_off = async_call_later(self.hass, MOTION_OFF_DELAY, self._turn_off)
        if not self._attr_is_on:
            self._attr_is_on = True
            self.async_write_ha_state()
