"""Flukso sensor."""
from homeassistant.components.mqtt.sensor import MqttSensor
from homeassistant.const import Platform

from .const import DOMAIN
from .discovery import get_entities_for_platform


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up MQTT sensor."""
    configs = get_entities_for_platform(
        Platform.SENSOR, hass.data[DOMAIN][config_entry.entry_id]
    )
    async_add_entities([MqttSensor(hass, c, config_entry, None) for c in configs])
