"""The Flukso integration."""

from __future__ import annotations

import json
import logging

from homeassistant.components import mqtt
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr

from .const import CONF_DEVICE_HASH, DOMAIN
from .discovery import CONFTYPES, FluksoConfig, async_fetch_config

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]

type FluksoConfigEntry = ConfigEntry[FluksoConfig]


async def async_setup_entry(hass: HomeAssistant, entry: FluksoConfigEntry) -> bool:
    """Set up Flukso from a config entry."""
    if not await mqtt.async_wait_for_mqtt_client(hass):
        raise ConfigEntryNotReady("MQTT integration is not available")

    device_hash: str = entry.data[CONF_DEVICE_HASH]
    try:
        config = await async_fetch_config(hass, device_hash)
    except TimeoutError as err:
        raise ConfigEntryNotReady(
            f"No sensor config received on /device/{device_hash}/config/sensor; "
            "check the MQTT bridge to the Flukso"
        ) from err
    entry.runtime_data = config

    device_registry = dr.async_get(hass)
    device = device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, device_hash)},
        manufacturer="Flukso",
        model="FLM03" if config.is_flm03 else "FLM02",
        name=config.serial or device_hash,
        serial_number=config.serial,
        sw_version=config.firmware,
    )
    # Versions before 2.0 created their entities through the MQTT integration,
    # which registered the Flukso under a mangled ("mqtt", "{('flukso', ...)}")
    # identifier. Remove such devices; they no longer have entities.
    for stale in dr.async_entries_for_config_entry(device_registry, entry.entry_id):
        if stale.id != device.id:
            _LOGGER.info("Removing stale Flukso device %s", stale.identifiers)
            device_registry.async_remove_device(stale.id)

    @callback
    def config_changed(msg: mqtt.ReceiveMessage) -> None:
        """Reload when the Flukso publishes a different config."""
        conftype = msg.topic.split("/")[4]
        if conftype not in CONFTYPES:
            return
        try:
            new = json.loads(msg.payload)
        except ValueError:
            return
        if new != getattr(config, conftype):
            _LOGGER.info(
                "Flukso %s %s config changed, reloading", device_hash, conftype
            )
            hass.config_entries.async_schedule_reload(entry.entry_id)

    entry.async_on_unload(
        await mqtt.async_subscribe(
            hass, f"/device/{device_hash}/config/+", config_changed
        )
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: FluksoConfigEntry) -> bool:
    """Unload a Flukso config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
