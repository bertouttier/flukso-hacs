"""Flukso sensor."""
import functools

from homeassistant.components import sensor
from homeassistant.components.mqtt.mixins import async_setup_entry_helper
from homeassistant.components.mqtt.sensor import DISCOVERY_SCHEMA, MqttSensor
from homeassistant.const import Platform

from .const import DOMAIN
from .discovery import get_entities_for_platform


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up MQTT sensor through configuration.yaml and dynamically through MQTT discovery."""
    setup = functools.partial(
        _async_setup_entity, hass, async_add_entities, config_entry=config_entry
    )
    await async_setup_entry_helper(hass, sensor.DOMAIN, setup, DISCOVERY_SCHEMA)


async def _async_setup_entity(hass, async_add_entities, config, config_entry=None, discovery_data=None):
    """Add a Flukso sensor."""
    configs = get_entities_for_platform(
        Platform.SENSOR,
        hass.data[DOMAIN][config_entry.entry_id]
    )
    async_add_entities(
        [MqttSensor(hass, c, config_entry, discovery_data) for c in configs]
    )
