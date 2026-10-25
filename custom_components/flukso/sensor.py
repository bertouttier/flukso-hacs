"""Flukso sensor."""

from __future__ import annotations

import logging

from homeassistant.components import mqtt
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import FluksoConfigEntry
from .discovery import FluksoEntityConfig, get_sensor_configs, parse_value
from .entity import FluksoEntity

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: FluksoConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Flukso sensors."""
    config = entry.runtime_data
    async_add_entities(
        FluksoSensor(config.device_hash, entity_config)
        for entity_config in get_sensor_configs(config)
    )


class FluksoSensor(FluksoEntity, SensorEntity):
    """A numeric Flukso sensor."""

    def __init__(self, device_hash: str, config: FluksoEntityConfig) -> None:
        """Initialize the sensor."""
        super().__init__(device_hash, config)
        self._attr_device_class = (
            SensorDeviceClass(config.device_class) if config.device_class else None
        )
        self._attr_state_class = config.state_class
        self._attr_native_unit_of_measurement = config.unit_of_measurement
        self._attr_suggested_display_precision = config.precision

    @callback
    def _message_received(self, msg: mqtt.ReceiveMessage) -> None:
        try:
            value = self._config.value_fn(parse_value(msg.payload))
        except (ValueError, IndexError, UnicodeDecodeError):
            _LOGGER.debug("Ignoring invalid payload on %s: %s", msg.topic, msg.payload)
            return
        if self._config.precision is not None:
            value = round(value, self._config.precision)
        if value == self._attr_native_value:
            # Unchanged: skip the state write so nothing is recorded.
            return
        self._attr_native_value = value
        self.async_write_ha_state()
