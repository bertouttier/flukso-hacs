"""Fetch and interpret the Flukso device configuration published over MQTT."""

from __future__ import annotations

import asyncio
import json
import logging
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from homeassistant.components import mqtt
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    LIGHT_LUX,
    PERCENTAGE,
    EntityCategory,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfPressure,
    UnitOfReactiveEnergy,
    UnitOfReactivePower,
    UnitOfTemperature,
    UnitOfVolume,
    UnitOfVolumeFlowRate,
)
from homeassistant.core import HomeAssistant, callback

from .const import CONFIG_TIMEOUT, OPTIONAL_CONFIG_TIMEOUT

_LOGGER = logging.getLogger(__name__)

CONFTYPE_KUBE = "kube"
CONFTYPE_FLX = "flx"
CONFTYPE_SENSOR = "sensor"
CONFTYPES = (CONFTYPE_KUBE, CONFTYPE_FLX, CONFTYPE_SENSOR)

BINARY_SENSOR_TYPES = ("movement", "vibration", "error")

DATA_TYPE_MAP_FLM03 = {
    "electricity": {
        "gauge": {
            "pf": ["gauge"],
            "vrms": ["gauge"],
            "irms": ["gauge"],
            "vthd": ["gauge"],
            "ithd": ["gauge"],
            "alpha": ["gauge"],
        },
        "counter": {
            "q1": ["gauge", "counter"],
            "q2": ["gauge", "counter"],
            "q3": ["gauge", "counter"],
            "q4": ["gauge", "counter"],
            "pplus": ["gauge", "counter"],
            "pminus": ["gauge", "counter"],
        },
    },
    "gas": {"counter": ["gauge", "counter"]},
    "water": {"counter": ["gauge", "counter"]},
    "temperature": {"gauge": ["gauge"]},
    "pressure": {"gauge": ["gauge"]},
    "battery": {"gauge": ["gauge"]},
    "light": {"gauge": ["gauge"]},
    "humidity": {"gauge": ["gauge"]},
    "error": {"gauge": ["gauge"]},
    "proximity": {"counter": ["gauge"]},
    "movement": {"counter": ["gauge"]},
    "vibration": {"counter": ["gauge"]},
}

DATA_TYPE_MAP_FLM02 = {
    "electricity": {"counter": ["gauge", "counter"]},
    "gas": {"counter": ["gauge", "counter"]},
    "water": {"counter": ["gauge", "counter"]},
    "temperature": {"gauge": ["gauge"]},
    "pressure": {"gauge": ["gauge"]},
    "battery": {"gauge": ["gauge"]},
    "light": {"gauge": ["gauge"]},
    "humidity": {"gauge": ["gauge"]},
    "error": {"gauge": ["gauge"]},
    "proximity": {"counter": ["gauge"]},
    "movement": {"counter": ["gauge"]},
    "vibration": {"counter": ["gauge"]},
}

_UNIT_OF_MEASUREMENT_MAP_COMMON = {
    "temperature": UnitOfTemperature.CELSIUS,
    "pressure": UnitOfPressure.HPA,
    "battery": PERCENTAGE,
    "water": {
        "gauge": UnitOfVolumeFlowRate.LITERS_PER_SECOND,
        "counter": UnitOfVolume.LITERS,
    },
    "light": LIGHT_LUX,
    "humidity": PERCENTAGE,
    "gas": {
        "gauge": UnitOfVolumeFlowRate.CUBIC_METERS_PER_SECOND,
        "counter": UnitOfVolume.CUBIC_METERS,
    },
}

UNIT_OF_MEASUREMENT_MAP_FLM03 = {
    **_UNIT_OF_MEASUREMENT_MAP_COMMON,
    "electricity": {
        "gauge": {
            "pf": PERCENTAGE,
            "q1": UnitOfReactivePower.VOLT_AMPERE_REACTIVE,
            "q2": UnitOfReactivePower.VOLT_AMPERE_REACTIVE,
            "q3": UnitOfReactivePower.VOLT_AMPERE_REACTIVE,
            "q4": UnitOfReactivePower.VOLT_AMPERE_REACTIVE,
            "pplus": UnitOfPower.WATT,
            "pminus": UnitOfPower.WATT,
            "vrms": UnitOfElectricPotential.VOLT,
            "irms": UnitOfElectricCurrent.AMPERE,
        },
        "counter": {
            "q1": UnitOfReactiveEnergy.VOLT_AMPERE_REACTIVE_HOUR,
            "q2": UnitOfReactiveEnergy.VOLT_AMPERE_REACTIVE_HOUR,
            "q3": UnitOfReactiveEnergy.VOLT_AMPERE_REACTIVE_HOUR,
            "q4": UnitOfReactiveEnergy.VOLT_AMPERE_REACTIVE_HOUR,
            "pplus": UnitOfEnergy.WATT_HOUR,
            "pminus": UnitOfEnergy.WATT_HOUR,
        },
    },
}

UNIT_OF_MEASUREMENT_MAP_FLM02 = {
    **_UNIT_OF_MEASUREMENT_MAP_COMMON,
    "electricity": {
        "gauge": UnitOfPower.WATT,
        "counter": UnitOfEnergy.WATT_HOUR,
    },
}

_DEVICE_CLASS_MAP_COMMON = {
    "water": {
        "gauge": SensorDeviceClass.VOLUME_FLOW_RATE,
        "counter": SensorDeviceClass.WATER,
    },
    "temperature": SensorDeviceClass.TEMPERATURE,
    "pressure": SensorDeviceClass.PRESSURE,
    "battery": SensorDeviceClass.BATTERY,
    "light": SensorDeviceClass.ILLUMINANCE,
    "humidity": SensorDeviceClass.HUMIDITY,
    "gas": {
        "gauge": SensorDeviceClass.VOLUME_FLOW_RATE,
        "counter": SensorDeviceClass.GAS,
    },
    "error": BinarySensorDeviceClass.PROBLEM,
    "movement": BinarySensorDeviceClass.MOTION,
    "vibration": BinarySensorDeviceClass.VIBRATION,
}

DEVICE_CLASS_MAP_FLM03 = {
    **_DEVICE_CLASS_MAP_COMMON,
    "electricity": {
        "gauge": {
            "pf": SensorDeviceClass.POWER_FACTOR,
            "q1": SensorDeviceClass.REACTIVE_POWER,
            "q2": SensorDeviceClass.REACTIVE_POWER,
            "q3": SensorDeviceClass.REACTIVE_POWER,
            "q4": SensorDeviceClass.REACTIVE_POWER,
            "pplus": SensorDeviceClass.POWER,
            "pminus": SensorDeviceClass.POWER,
            "vrms": SensorDeviceClass.VOLTAGE,
            "irms": SensorDeviceClass.CURRENT,
        },
        "counter": {
            "q1": SensorDeviceClass.REACTIVE_ENERGY,
            "q2": SensorDeviceClass.REACTIVE_ENERGY,
            "q3": SensorDeviceClass.REACTIVE_ENERGY,
            "q4": SensorDeviceClass.REACTIVE_ENERGY,
            "pplus": SensorDeviceClass.ENERGY,
            "pminus": SensorDeviceClass.ENERGY,
        },
    },
}

DEVICE_CLASS_MAP_FLM02 = {
    **_DEVICE_CLASS_MAP_COMMON,
    "electricity": {
        "gauge": SensorDeviceClass.POWER,
        "counter": SensorDeviceClass.ENERGY,
    },
}

ICON_MAP = {
    "electricity": "mdi:lightning-bolt",
    "water": "mdi:water",
    "proximity": "mdi:ruler",
    "gas": "mdi:fire",
}

STATE_CLASS_MAP = {
    "electricity": {
        "counter": SensorStateClass.TOTAL_INCREASING,
        "gauge": SensorStateClass.MEASUREMENT,
    },
    "water": {
        "counter": SensorStateClass.TOTAL_INCREASING,
        "gauge": SensorStateClass.MEASUREMENT,
    },
    "gas": {
        "counter": SensorStateClass.TOTAL_INCREASING,
        "gauge": SensorStateClass.MEASUREMENT,
    },
    "temperature": SensorStateClass.MEASUREMENT,
    "pressure": SensorStateClass.MEASUREMENT,
    "battery": SensorStateClass.MEASUREMENT,
    "light": SensorStateClass.MEASUREMENT,
    "humidity": SensorStateClass.MEASUREMENT,
    "proximity": SensorStateClass.MEASUREMENT,
}

# Rounding applied to the published value. Noisy sensors (temperature, battery
# voltage, power factor) are rounded so tiny fluctuations do not produce a new
# state, and therefore a new recorder row, on every message.
DISPLAY_PRECISION_MAP = {
    "temperature": 1,
    "humidity": 0,
    "pressure": 0,
    "battery": 0,
    "light": 0,
}


@dataclass
class FluksoConfig:
    """The configuration a Flukso publishes on /device/<hash>/config/+ and TAP."""

    device_hash: str
    sensor: dict[str, Any] = field(default_factory=dict)
    kube: dict[str, Any] = field(default_factory=dict)
    flx: dict[str, Any] = field(default_factory=dict)
    serial: str | None = None
    firmware: str | None = None

    @property
    def is_flm03(self) -> bool:
        """Only the FLM03 publishes a TAP report."""
        return self.serial is not None


@dataclass(frozen=True, kw_only=True)
class FluksoEntityConfig:
    """Everything needed to create one Flukso entity."""

    unique_id: str
    name: str
    state_topic: str
    sensor_type: str | None
    subtype: str | None
    data_type: str
    device_class: str | None = None
    state_class: SensorStateClass | None = None
    unit_of_measurement: str | None = None
    icon: str | None = None
    entity_category: EntityCategory | None = None
    precision: int | None = None
    value_fn: Callable[[float], float] = lambda value: value


def _get_sensor_detail(sensor: dict[str, Any], detail_map: dict[str, Any]) -> Any:
    """Walk detail_map by the sensor's type, data_type and subtype."""
    m: Any = detail_map
    levels = ["type", "data_type", "subtype"]
    while isinstance(m, dict) and levels:
        level = levels.pop(0)
        if level in sensor:
            m = m.get(sensor[level])
    return m


def _get_base_name(sensor: dict[str, Any], config: FluksoConfig) -> str:
    """Name a sensor after its kube or flx port, as configured on the Flukso."""
    if sensor.get("class") == "kube":
        kube = config.kube.get(str(sensor.get("kid")), {})
        return kube.get("name") or "unknown kube"
    if "port" in sensor:
        if "function" in sensor:
            return sensor["function"]
        port = config.flx.get(str(sensor["port"][0]), {})
        if port.get("name"):
            return port["name"]
    return "unknown"


def _get_entity_name(sensor: dict[str, Any], config: FluksoConfig) -> str:
    """Combine the base name with the type, subtype and data type."""
    name = _get_base_name(sensor, config)
    sensor_type = sensor.get("type")
    if sensor_type is None:
        return name
    name = f"{name} {sensor_type}"
    if sensor_type == "electricity" and "subtype" in sensor:
        return f"{name} {sensor['subtype']} {sensor['data_type']}"
    if sensor_type in ("electricity", "water", "gas"):
        return f"{name} {sensor['data_type']}"
    return name


def _get_value_fn(sensor: dict[str, Any]) -> Callable[[float], float]:
    """Convert the raw Flukso value to the unit Home Assistant expects."""
    match sensor.get("type"), sensor.get("subtype"):
        case "battery", _:
            # The kube reports its battery voltage; 3.3V is a full battery.
            return lambda value: value / 3.3 * 100
        case "gas", _:
            return lambda value: value / 1000
        case "electricity", "pf":
            return lambda value: value * 100
    return lambda value: value


def _is_binary_sensor(sensor: dict[str, Any]) -> bool:
    return sensor.get("class") == "kube" and sensor.get("type") in BINARY_SENSOR_TYPES


def _enabled_sensors(config: FluksoConfig) -> list[dict[str, Any]]:
    """Return the sensors that are enabled and registered (have an id)."""
    return [
        sensor
        for sensor in config.sensor.values()
        if isinstance(sensor, dict) and sensor.get("enable") and sensor.get("id")
    ]


def _build_entity_config(
    sensor: dict[str, Any], config: FluksoConfig
) -> FluksoEntityConfig:
    if config.is_flm03:
        device_class = _get_sensor_detail(sensor, DEVICE_CLASS_MAP_FLM03)
        uom = _get_sensor_detail(sensor, UNIT_OF_MEASUREMENT_MAP_FLM03)
    else:
        device_class = _get_sensor_detail(sensor, DEVICE_CLASS_MAP_FLM02)
        uom = _get_sensor_detail(sensor, UNIT_OF_MEASUREMENT_MAP_FLM02)

    sensor_type = sensor.get("type")
    subtype = sensor.get("subtype")
    precision = DISPLAY_PRECISION_MAP.get(sensor_type)
    if sensor_type == "electricity" and subtype == "pf":
        precision = 1

    return FluksoEntityConfig(
        unique_id=f"{config.device_hash}_{sensor['id']}_{sensor['data_type']}",
        name=_get_entity_name(sensor, config),
        state_topic=f"/sensor/{sensor['id']}/{sensor['data_type']}",
        sensor_type=sensor_type,
        subtype=subtype,
        data_type=sensor["data_type"],
        device_class=device_class if isinstance(device_class, str) else None,
        state_class=_get_sensor_detail(sensor, STATE_CLASS_MAP),
        unit_of_measurement=uom if isinstance(uom, str) else None,
        icon=_get_sensor_detail(sensor, ICON_MAP),
        entity_category=(
            EntityCategory.DIAGNOSTIC if sensor_type in ("battery", "error") else None
        ),
        precision=precision,
        value_fn=_get_value_fn(sensor),
    )


def get_sensor_configs(config: FluksoConfig) -> list[FluksoEntityConfig]:
    """Return the configs of all numeric sensors."""
    data_type_map = DATA_TYPE_MAP_FLM03 if config.is_flm03 else DATA_TYPE_MAP_FLM02
    entities = []
    for sensor in _enabled_sensors(config):
        if _is_binary_sensor(sensor):
            continue
        data_types = _get_sensor_detail(sensor, data_type_map)
        if not isinstance(data_types, list):
            _LOGGER.debug("Skipping unsupported sensor %s", sensor)
            continue
        for data_type in data_types:
            entities.append(
                _build_entity_config({**sensor, "data_type": data_type}, config)
            )
    return entities


def get_binary_sensor_configs(config: FluksoConfig) -> list[FluksoEntityConfig]:
    """Return the configs of all kube binary sensors."""
    return [
        _build_entity_config(sensor, config)
        for sensor in _enabled_sensors(config)
        if _is_binary_sensor(sensor)
    ]


def parse_value(payload: str | bytes) -> float:
    """Extract the value from a '[timestamp,value,unit]' Flukso payload."""
    if isinstance(payload, bytes):
        payload = payload.decode()
    return float(payload.strip().strip("[]").split(",")[1])


async def async_fetch_config(hass: HomeAssistant, device_hash: str) -> FluksoConfig:
    """Collect the retained Flukso configs and TAP report over MQTT.

    Raises TimeoutError when the sensor config does not arrive.
    """
    config = FluksoConfig(device_hash)
    loop = hass.loop
    received: dict[str, asyncio.Future[None]] = {
        conftype: loop.create_future() for conftype in CONFTYPES
    }
    tap_received: asyncio.Future[None] = loop.create_future()

    @callback
    def config_message_received(msg: mqtt.ReceiveMessage) -> None:
        conftype = msg.topic.split("/")[4]
        if conftype not in received:
            _LOGGER.debug("Ignoring config type %s for %s", conftype, device_hash)
            return
        try:
            setattr(config, conftype, json.loads(msg.payload))
        except ValueError:
            _LOGGER.warning("Invalid %s config received from %s", conftype, device_hash)
            return
        if not received[conftype].done():
            received[conftype].set_result(None)

    @callback
    def tap_message_received(msg: mqtt.ReceiveMessage) -> None:
        serial = re.search(r"# serial: (.*)", msg.payload)
        firmware = re.search(r"# firmware: (.*)", msg.payload)
        if serial:
            config.serial = serial.group(1).strip()
        if firmware:
            config.firmware = firmware.group(1).strip()
        if not tap_received.done():
            tap_received.set_result(None)

    unsubscribes = [
        await mqtt.async_subscribe(
            hass, f"/device/{device_hash}/config/+", config_message_received
        ),
        await mqtt.async_subscribe(
            hass, f"/device/{device_hash}/test/tap", tap_message_received
        ),
    ]
    try:
        await asyncio.wait([received[CONFTYPE_SENSOR]], timeout=CONFIG_TIMEOUT)
        if not received[CONFTYPE_SENSOR].done():
            raise TimeoutError
        await asyncio.wait(
            [received[CONFTYPE_KUBE], received[CONFTYPE_FLX], tap_received],
            timeout=OPTIONAL_CONFIG_TIMEOUT,
        )
    finally:
        for unsubscribe in unsubscribes:
            unsubscribe()

    if config.is_flm03:
        _LOGGER.debug(
            "Found FLM03 %s with serial %s and firmware %s",
            device_hash,
            config.serial,
            config.firmware,
        )
    else:
        _LOGGER.debug("No TAP report received, %s is an FLM02", device_hash)
    return config
