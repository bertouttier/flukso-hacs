"""Tests for the Flukso sensors and binary sensors."""

from datetime import timedelta

import pytest
from homeassistant.const import STATE_OFF, STATE_ON, STATE_UNKNOWN, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)

from .conftest import setup_entry
from .flukso_simulator import FluksoSimulator
from .test_common import DEVICE_HASH

PPLUS = "d5fec1970bd1d88d029116f21cb03c79"
Q1 = "58e09e396968b58f8cc2f865456a3834"
PF = "12652edace9590f31665f1033624663d"
WATER = "b620c48665f630b4e0b42a3afa503f40"
GAS = "58f44d69532bafa2777737318c388885"
PRESSURE = "183837ba8cb9175abfc11e21094935c6"
TEMPERATURE = "c0fae2f4c224502f36ab9ee6c952a385"
BATTERY = "d3e903b6c46bed83767114c5b6701ab2"
MOVEMENT = "4d418f8149203518274a4fefd3c4de43"
ERROR = "eb16b48a6fb5e4ad6b93f3209feec5b3"


@pytest.fixture
async def flukso_entry(
    hass: HomeAssistant, flukso: FluksoSimulator, config_entry: MockConfigEntry
) -> FluksoSimulator:
    """Boot the simulated FLM03 and set up its config entry."""
    flukso.boot()
    await setup_entry(hass, config_entry)
    return flukso


@pytest.mark.parametrize(
    ("entity_id", "topic", "payload", "state", "unit", "device_class", "state_class"),
    [
        (
            "sensor.fl01234567_l1_electricity_pplus_counter",
            f"/sensor/{PPLUS}/counter",
            '[1632134400,123456,"Wh"]',
            "123456.0",
            "Wh",
            "energy",
            "total_increasing",
        ),
        (
            "sensor.fl01234567_l1_electricity_pplus_gauge",
            f"/sensor/{PPLUS}/gauge",
            '[1632134400,230,"W"]',
            "230.0",
            "W",
            "power",
            "measurement",
        ),
        (
            "sensor.fl01234567_zonnepanelen_electricity_q1_counter",
            f"/sensor/{Q1}/counter",
            '[1632134400,42,"varh"]',
            "42.0",
            "varh",
            "reactive_energy",
            "total_increasing",
        ),
        (
            "sensor.fl01234567_zonnepanelen_electricity_pf_gauge",
            f"/sensor/{PF}/gauge",
            "[1632134400,0.9567]",
            "95.7",
            "%",
            "power_factor",
            "measurement",
        ),
        (
            "sensor.fl01234567_water_water_gauge",
            f"/sensor/{WATER}/gauge",
            '[1632134400,0.5,"L/s"]',
            "0.5",
            "L/s",
            "volume_flow_rate",
            "measurement",
        ),
        (
            "sensor.fl01234567_gas_gas_counter",
            f"/sensor/{GAS}/counter",
            '[1632134400,1500,"L"]',
            "1.5",
            "m³",
            "gas",
            "total_increasing",
        ),
        (
            "sensor.fl01234567_keuken_pressure",
            f"/sensor/{PRESSURE}/gauge",
            '[1632134400,1013.4,"hPa"]',
            "1013.0",
            "hPa",
            "pressure",
            "measurement",
        ),
        (
            "sensor.fl01234567_slaapkamer_temperature",
            f"/sensor/{TEMPERATURE}/gauge",
            '[1632134400,21.36,"°C"]',
            "21.4",
            "°C",
            "temperature",
            "measurement",
        ),
        (
            "sensor.fl01234567_keuken_battery",
            f"/sensor/{BATTERY}/gauge",
            '[1632134400,3.0,"V"]',
            "91.0",
            "%",
            "battery",
            "measurement",
        ),
    ],
)
async def test_sensor_values(
    hass: HomeAssistant,
    flukso_entry: FluksoSimulator,
    entity_id,
    topic,
    payload,
    state,
    unit,
    device_class,
    state_class,
) -> None:
    """Payloads are converted to the right state and unit."""
    assert hass.states.get(entity_id).state == STATE_UNKNOWN

    flukso_entry.broker.publish(topic, payload)
    await hass.async_block_till_done()

    entity = hass.states.get(entity_id)
    assert entity.state == state
    assert entity.attributes.get("unit_of_measurement") == unit
    assert entity.attributes.get("device_class") == device_class
    assert entity.attributes.get("state_class") == state_class


async def test_unique_ids_are_stable(
    hass: HomeAssistant, flukso_entry: FluksoSimulator
) -> None:
    """Unique ids keep the format of earlier versions."""
    registry = er.async_get(hass)
    assert registry.async_get_entity_id(
        "sensor", "flukso", f"{DEVICE_HASH}_{PPLUS}_counter"
    )
    assert registry.async_get_entity_id(
        "binary_sensor", "flukso", f"{DEVICE_HASH}_{MOVEMENT}_counter"
    )


async def test_entity_categories(
    hass: HomeAssistant, flukso_entry: FluksoSimulator
) -> None:
    """Measurements are primary entities, battery and errors diagnostic."""
    registry = er.async_get(hass)
    assert (
        registry.async_get(
            "sensor.fl01234567_l1_electricity_pplus_counter"
        ).entity_category
        is None
    )
    assert (
        registry.async_get("sensor.fl01234567_keuken_battery").entity_category
        is EntityCategory.DIAGNOSTIC
    )


async def test_unchanged_value_is_not_written(
    hass: HomeAssistant, flukso_entry: FluksoSimulator
) -> None:
    """Repeating the same (rounded) value does not write a new state."""
    entity_id = "sensor.fl01234567_slaapkamer_temperature"
    topic = f"/sensor/{TEMPERATURE}/gauge"

    flukso_entry.broker.publish(topic, "[1,21.36]")
    await hass.async_block_till_done()
    first = hass.states.get(entity_id)

    flukso_entry.broker.publish(topic, "[2,21.41]")
    await hass.async_block_till_done()
    second = hass.states.get(entity_id)

    assert second.state == "21.4"
    assert second.last_reported == first.last_reported


async def test_invalid_payload_is_ignored(
    hass: HomeAssistant, flukso_entry: FluksoSimulator
) -> None:
    """A garbage payload does not crash or change the state."""
    entity_id = "sensor.fl01234567_slaapkamer_temperature"

    flukso_entry.broker.publish(f"/sensor/{TEMPERATURE}/gauge", "garbage")
    await hass.async_block_till_done()

    assert hass.states.get(entity_id).state == STATE_UNKNOWN


async def test_movement(hass: HomeAssistant, flukso_entry: FluksoSimulator) -> None:
    """Movement turns on for every message and off after a delay."""
    entity_id = "binary_sensor.fl01234567_living_movement"
    assert hass.states.get(entity_id).state == STATE_OFF
    assert hass.states.get(entity_id).attributes["device_class"] == "motion"

    flukso_entry.kube_event(MOVEMENT)
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == STATE_ON

    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=11))
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == STATE_OFF


async def test_error(hass: HomeAssistant, flukso_entry: FluksoSimulator) -> None:
    """The error sensor follows the reported error code."""
    entity_id = "binary_sensor.fl01234567_kelder_error"
    assert hass.states.get(entity_id).attributes["device_class"] == "problem"

    flukso_entry.reading(ERROR, "gauge", 3)
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == STATE_ON

    flukso_entry.reading(ERROR, "gauge", 0)
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == STATE_OFF
