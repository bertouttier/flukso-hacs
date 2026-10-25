"""Tests for setting up and unloading Flukso entries."""

import copy

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.flukso.const import DOMAIN

from .conftest import setup_entry
from .flukso_simulator import FakeBroker, FluksoSimulator
from .test_common import DEVICE_HASH, FLM02_SENSOR_CONFIG


async def test_setup_flm03(
    hass: HomeAssistant, flukso: FluksoSimulator, config_entry: MockConfigEntry
) -> None:
    """An FLM03 creates a device with its serial and firmware."""
    flukso.boot()
    await setup_entry(hass, config_entry)

    assert config_entry.state is ConfigEntryState.LOADED
    assert config_entry.runtime_data.is_flm03

    device = dr.async_get(hass).async_get_device_by_identifier(
        (DOMAIN, DEVICE_HASH), config_entry.entry_id
    )
    assert device is not None
    assert device.manufacturer == "Flukso"
    assert device.model == "FLM03"
    assert device.serial_number == "FL01234567"
    assert device.sw_version == "380"

    entities = er.async_entries_for_config_entry(
        er.async_get(hass), config_entry.entry_id
    )
    assert entities
    assert all(entity.device_id == device.id for entity in entities)


async def test_setup_flm02_device_dump(
    hass: HomeAssistant, broker: FakeBroker, config_entry: MockConfigEntry
) -> None:
    """The sensor config dumped from a real FLM02 is set up without a TAP report."""
    sensor_config = copy.deepcopy(FLM02_SENSOR_CONFIG)
    sensor_config["1"]["id"] = "0123456789abcdef0123456789abcd01"
    FluksoSimulator(broker, flm03=False, sensor=sensor_config).boot()
    await setup_entry(hass, config_entry)

    assert config_entry.state is ConfigEntryState.LOADED
    assert not config_entry.runtime_data.is_flm03
    state = hass.states.get(f"sensor.{DEVICE_HASH}_l_flm02_electricity_counter")
    assert state is not None
    assert state.attributes["unit_of_measurement"] == "Wh"


async def test_setup_retry_without_config(
    hass: HomeAssistant, flukso: FluksoSimulator, config_entry: MockConfigEntry
) -> None:
    """The entry retries when the Flukso does not publish its config."""
    await setup_entry(hass, config_entry)

    assert config_entry.state is ConfigEntryState.SETUP_RETRY


async def test_unload_keeps_device(
    hass: HomeAssistant, flukso: FluksoSimulator, config_entry: MockConfigEntry
) -> None:
    """Unloading must not remove the device and its customizations."""
    flukso.boot()
    await setup_entry(hass, config_entry)

    assert await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()

    assert config_entry.state is ConfigEntryState.NOT_LOADED
    assert dr.async_get(hass).async_get_device_by_identifier(
        (DOMAIN, DEVICE_HASH), config_entry.entry_id
    )


async def test_reload_on_config_change(
    hass: HomeAssistant, flukso: FluksoSimulator, config_entry: MockConfigEntry
) -> None:
    """A changed config on the Flukso reloads the entry; an identical one not."""
    flukso.boot()
    await setup_entry(hass, config_entry)

    reloads: list[str] = []
    hass.config_entries.async_schedule_reload = reloads.append

    flukso.publish_config("sensor")
    await hass.async_block_till_done()
    assert reloads == []

    flukso.update_config("sensor", lambda sensor: sensor["13"].update(enable=0))
    await hass.async_block_till_done()
    assert reloads == [config_entry.entry_id]


async def test_stale_device_from_v1_is_removed(
    hass: HomeAssistant, flukso: FluksoSimulator, config_entry: MockConfigEntry
) -> None:
    """The device v1 registered through the MQTT integration is cleaned up."""
    config_entry.add_to_hass(hass)
    device_registry = dr.async_get(hass)
    stale = device_registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        identifiers={("mqtt", f"{{('flukso', '{DEVICE_HASH}')}}")},
        manufacturer="Flukso",
        name="FL01234567",
    )

    flukso.boot()
    await setup_entry(hass, config_entry)

    assert config_entry.state is ConfigEntryState.LOADED
    assert device_registry.async_get(stale.id) is None
    devices = dr.async_entries_for_config_entry(device_registry, config_entry.entry_id)
    assert [device.identifiers for device in devices] == [{(DOMAIN, DEVICE_HASH)}]
