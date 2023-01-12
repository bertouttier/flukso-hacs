"""Flukso binary sensor."""
from homeassistant.components.mqtt.binary_sensor import MqttBinarySensor
from homeassistant.const import Platform

from .const import DOMAIN
from .discovery import get_entities_for_platform


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up MQTT binary sensor."""
    configs = get_entities_for_platform(
        Platform.BINARY_SENSOR, hass.data[DOMAIN][config_entry.entry_id]
    )
    async_add_entities([MqttBinarySensor(hass, c, config_entry, None) for c in configs])
