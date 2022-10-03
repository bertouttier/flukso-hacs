"""Flukso binary sensor."""
import functools

from homeassistant.components import binary_sensor
from homeassistant.components.mqtt.binary_sensor import (DISCOVERY_SCHEMA,
                                                         MqttBinarySensor)
from homeassistant.components.mqtt.mixins import async_setup_entry_helper
from homeassistant.const import Platform

from .const import DOMAIN
from .discovery import get_entities_for_platform


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up MQTT binary sensor through configuration.yaml and dynamically through MQTT discovery."""
    setup = functools.partial(
        _async_setup_entity, hass, async_add_entities, config_entry=config_entry
    )
    await async_setup_entry_helper(hass, binary_sensor.DOMAIN, setup, DISCOVERY_SCHEMA)


async def _async_setup_entity(hass, async_add_entities, config, config_entry=None, discovery_data=None):
    """Set up MQTT binary sensor."""
    configs = get_entities_for_platform(
        Platform.BINARY_SENSOR,
        hass.data[DOMAIN][config_entry.entry_id]
    )
    async_add_entities(
        [MqttBinarySensor(hass, c, config_entry, discovery_data) for c in configs]
    )
