"""Base entity for Flukso sensors."""

from __future__ import annotations

from homeassistant.components import mqtt
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import DOMAIN
from .discovery import FluksoEntityConfig


class FluksoEntity(Entity):
    """An entity that follows one Flukso sensor topic over MQTT."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, device_hash: str, config: FluksoEntityConfig) -> None:
        """Initialize the entity."""
        self._config = config
        self._attr_unique_id = config.unique_id
        self._attr_name = config.name
        self._attr_icon = config.icon
        self._attr_entity_category = config.entity_category
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, device_hash)})

    async def async_added_to_hass(self) -> None:
        """Subscribe to the sensor topic and the broker connection state."""
        self._attr_available = mqtt.is_connected(self.hass)
        self.async_on_remove(
            mqtt.async_subscribe_connection_status(self.hass, self._connection_changed)
        )
        self.async_on_remove(
            await mqtt.async_subscribe(
                self.hass, self._config.state_topic, self._message_received
            )
        )

    @callback
    def _connection_changed(self, connected: bool) -> None:
        self._attr_available = connected
        self.async_write_ha_state()

    @callback
    def _message_received(self, msg: mqtt.ReceiveMessage) -> None:
        raise NotImplementedError
