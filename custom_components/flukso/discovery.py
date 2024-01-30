"""Flukso MQTT discovery."""
import asyncio
import json
import logging
import re

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.mqtt import (CONF_QOS, CONF_STATE_TOPIC,
                                           subscription)
from homeassistant.components.mqtt.binary_sensor import CONF_OFF_DELAY
from homeassistant.components.mqtt.binary_sensor import \
    PLATFORM_SCHEMA_MODERN as MQTT_BINARY_SENSOR_PLATFORM_SCHEMA
from homeassistant.components.mqtt.mixins import (CONF_CONNECTIONS,
                                                  CONF_ENABLED_BY_DEFAULT,
                                                  CONF_IDENTIFIERS,
                                                  CONF_MANUFACTURER,
                                                  CONF_OBJECT_ID,
                                                  CONF_SW_VERSION)
from homeassistant.components.mqtt.sensor import CONF_STATE_CLASS
from homeassistant.components.mqtt.sensor import \
    PLATFORM_SCHEMA_MODERN as MQTT_SENSOR_PLATFORM_SCHEMA
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import (CONF_DEVICE, CONF_DEVICE_CLASS,
                                 CONF_ENTITY_CATEGORY, CONF_FORCE_UPDATE,
                                 CONF_ICON, CONF_NAME, CONF_UNIQUE_ID,
                                 CONF_UNIT_OF_MEASUREMENT, CONF_VALUE_TEMPLATE,
                                 UnitOfElectricCurrent,
                                 UnitOfElectricPotential, UnitOfEnergy,
                                 LIGHT_LUX, PERCENTAGE,
                                 POWER_VOLT_AMPERE_REACTIVE, UnitOfPower,
                                 UnitOfPressure, UnitOfTemperature,
                                 UnitOfVolume, UnitOfVolume, Platform)
from homeassistant.core import callback
from homeassistant.helpers.entity import EntityCategory

from .const import (CONF_DEVICE_FIRMWARE, CONF_DEVICE_HASH, CONF_DEVICE_SERIAL,
                    CONF_FLM03, DEFAULT_TIMEOUT, DOMAIN)

_LOGGER = logging.getLogger(__name__)

CONFTYPE_KUBE = "kube"
CONFTYPE_FLX = "flx"
CONFTYPE_SENSOR = "sensor"
CONFTYPES = [
    CONFTYPE_KUBE,
    CONFTYPE_FLX,
    CONFTYPE_SENSOR
]

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

UNIT_OF_MEASUREMENT_MAP_FLM03 = {
    "electricity": {
        "gauge": {
            "pf": PERCENTAGE,
            "q1": POWER_VOLT_AMPERE_REACTIVE,
            "q2": POWER_VOLT_AMPERE_REACTIVE,
            "q3": POWER_VOLT_AMPERE_REACTIVE,
            "q4": POWER_VOLT_AMPERE_REACTIVE,
            "pplus": UnitOfPower.WATT,
            "pminus": UnitOfPower.WATT,
            "vrms": UnitOfElectricPotential.VOLT,
            "irms": UnitOfElectricCurrent.AMPERE,
        },
        "counter": {
            "q1": "VARh",
            "q2": "VARh",
            "q3": "VARh",
            "q4": "VARh",
            "pplus": UnitOfEnergy.WATT_HOUR,
            "pminus": UnitOfEnergy.WATT_HOUR,
        },
    },
    "temperature": UnitOfTemperature.CELSIUS,
    "pressure": UnitOfPressure.HPA,
    "battery": PERCENTAGE,
    "water": {
        "gauge": "L/s",
        "counter": UnitOfVolume.LITERS,
    },
    "light": LIGHT_LUX,
    "humidity": PERCENTAGE,
    "gas":  {
        "gauge": "m³/s",
        "counter": UnitOfVolume.CUBIC_METERS,
    },
}

UNIT_OF_MEASUREMENT_MAP_FLM02 = {
    "electricity": {
        "gauge": UnitOfPower.WATT,
        "counter": UnitOfEnergy.WATT_HOUR
    },
    "temperature": UnitOfTemperature.CELSIUS,
    "pressure": UnitOfPressure.HPA,
    "battery": PERCENTAGE,
    "water": {
        "gauge": "L/s",
        "counter": UnitOfVolume.LITERS,
    },
    "light": LIGHT_LUX,
    "humidity": PERCENTAGE,
    "gas":  {
        "gauge": "m³/s",
        "counter": UnitOfVolume.CUBIC_METERS,
    },
}

DEVICE_CLASS_MAP_FLM03 = {
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
            "pplus": SensorDeviceClass.ENERGY,
            "pminus": SensorDeviceClass.ENERGY
        },
    },
    "water": SensorDeviceClass.WATER,
    "temperature": SensorDeviceClass.TEMPERATURE,
    "pressure": SensorDeviceClass.PRESSURE,
    "battery": SensorDeviceClass.BATTERY,
    "light": SensorDeviceClass.ILLUMINANCE,
    "humidity": SensorDeviceClass.HUMIDITY,
    "gas": SensorDeviceClass.GAS,
    "error": BinarySensorDeviceClass.PROBLEM,
}

DEVICE_CLASS_MAP_FLM02 = {
    "electricity": {
        "gauge": SensorDeviceClass.POWER,
        "counter": SensorDeviceClass.ENERGY,
    },
    "water": SensorDeviceClass.WATER,
    "temperature": SensorDeviceClass.TEMPERATURE,
    "pressure": SensorDeviceClass.PRESSURE,
    "battery": SensorDeviceClass.BATTERY,
    "light": SensorDeviceClass.ILLUMINANCE,
    "humidity": SensorDeviceClass.HUMIDITY,
    "gas": SensorDeviceClass.GAS,
    "error": BinarySensorDeviceClass.PROBLEM,
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
        "gauge": SensorStateClass.MEASUREMENT
    },
    "temperature": SensorStateClass.MEASUREMENT,
    "pressure": SensorStateClass.MEASUREMENT,
    "battery": SensorStateClass.MEASUREMENT,
    "light": SensorStateClass.MEASUREMENT,
    "humidity": SensorStateClass.MEASUREMENT,
    "error": SensorStateClass.MEASUREMENT,
    "proximity": SensorStateClass.MEASUREMENT,
    "movement": SensorStateClass.MEASUREMENT,
    "vibration": SensorStateClass.MEASUREMENT,
}


def _get_sensor_detail(sensor, detail_map):
    m = detail_map
    levels = ["type", "data_type", "subtype"]
    while isinstance(m, dict) and levels:
        level = levels.pop(0)
        if level in sensor:
            if sensor[level] in m:
                m = m[sensor[level]]
            else:
                m = None
    return m


def _get_sensor_name(sensor, entry_data):
    """Generate a name based on the kube and flx config, and the data type and sub type."""
    name = "unknown"
    if "class" in sensor and sensor["class"] == "kube":
        name = "unknown kube"
        if (
            CONFTYPE_KUBE in entry_data
            and "name" in entry_data[CONFTYPE_KUBE][str(sensor["kid"])]
            and entry_data[CONFTYPE_KUBE][str(sensor["kid"])]["name"]
        ):
            name = entry_data[CONFTYPE_KUBE][str(sensor["kid"])]["name"]
    else:
        "unknown sensor"
        if "port" in sensor:
            if "function" in sensor:
                name = sensor["function"]
            elif (
                CONFTYPE_FLX in entry_data
                and "name" in entry_data[CONFTYPE_FLX][str(sensor["port"][0])]
                and entry_data[CONFTYPE_FLX][str(sensor["port"][0])]["name"]
            ):
                name = entry_data[CONFTYPE_FLX][str(sensor["port"][0])]["name"]
    return name


def _get_sensor_object_id(sensor, entry_data):
    """Generate a name based on the kube and flx config, and the data type and sub type."""
    name = "unknown"
    if "class" in sensor and sensor["class"] == "kube":
        if (
            CONFTYPE_KUBE in entry_data
            and "name" in entry_data[CONFTYPE_KUBE][str(sensor["kid"])]
            and entry_data[CONFTYPE_KUBE][str(sensor["kid"])]["name"]
        ):
            name = entry_data[CONFTYPE_KUBE][str(sensor["kid"])]["name"]
    else:
        if "port" in sensor:
            if "function" in sensor:
                name = sensor["function"]
            elif (
                CONFTYPE_FLX in entry_data
                and "name" in entry_data[CONFTYPE_FLX][str(sensor["port"][0])]
                and entry_data[CONFTYPE_FLX][str(sensor["port"][0])]["name"]
            ):
                name = entry_data[CONFTYPE_FLX][str(sensor["port"][0])]["name"]

    if "type" in sensor:
        name = f'{name} {sensor["type"]}'
        if "data_type" in sensor:
            if sensor["type"] == "electricity":
                if "subtype" in sensor:
                    name = f'{name} {sensor["subtype"]} {sensor["data_type"]}'
                else:
                    name = f'{name} {sensor["data_type"]}'
            elif sensor["type"] == "water":
                name = f'{name} {sensor["data_type"]}'
            elif sensor["type"] == "gas":
                name = f'{name} {sensor["data_type"]}'
    return name


def _is_binary_sensor(sensor):
    if "class" in sensor and "type" in sensor:
        return (sensor["class"] == "kube") and (
            sensor["type"] in ("movement", "vibration", "error")
        )
    return False


def _get_binary_sensor_entities(entry_data, device_info):
    """Generate binary sensor configuration."""
    entities = []

    for sensor in entry_data[CONFTYPE_SENSOR].values():
        if "enable" not in sensor or sensor["enable"] == 0:
            continue

        if not _is_binary_sensor(sensor):
            continue

        sensorconfig = {}
        sensorconfig[CONF_NAME] = _get_sensor_name(sensor, entry_data)
        sensorconfig[CONF_OBJECT_ID] = _get_sensor_object_id(sensor, entry_data)
        sensorconfig[CONF_DEVICE] = device_info
        sensorconfig[CONF_ENTITY_CATEGORY] = EntityCategory.DIAGNOSTIC
        sensorconfig[CONF_ENABLED_BY_DEFAULT] = True
        sensorconfig[CONF_STATE_TOPIC] = f'/sensor/{sensor["id"]}/{sensor["data_type"]}'
        sensorconfig[CONF_QOS] = 0
        sensorconfig[CONF_FORCE_UPDATE] = False
        discovery_hash = (
            entry_data[CONF_DEVICE_HASH],
            sensor["id"],
            sensor["data_type"],
        )
        sensorconfig[CONF_UNIQUE_ID] = "_".join(discovery_hash)
        if entry_data[CONF_FLM03]:
            device_class = _get_sensor_detail(sensor, DEVICE_CLASS_MAP_FLM03)
        else:
            device_class = _get_sensor_detail(sensor, DEVICE_CLASS_MAP_FLM02)
        if device_class:
            sensorconfig[CONF_DEVICE_CLASS] = device_class
        icon = _get_sensor_detail(sensor, ICON_MAP)
        if icon:
            sensorconfig[CONF_ICON] = icon
        if entry_data[CONF_FLM03]:
            uom = _get_sensor_detail(sensor, UNIT_OF_MEASUREMENT_MAP_FLM03)
        else:
            uom = _get_sensor_detail(sensor, UNIT_OF_MEASUREMENT_MAP_FLM02)
        if uom:
            sensorconfig[CONF_UNIT_OF_MEASUREMENT] = uom
        if device_class and (device_class == BinarySensorDeviceClass.PROBLEM):
            sensorconfig[
                CONF_VALUE_TEMPLATE
            ] = """
                    {% if (value.split(",")[1]|int) > 0 %}
                        ON
                    {% else %}
                        OFF
                    {% endif %}"""
        else:
            sensorconfig[CONF_OFF_DELAY] = DEFAULT_TIMEOUT
            sensorconfig[
                CONF_VALUE_TEMPLATE
            ] = """
                    {% if value %}
                        ON
                    {% else %}
                        OFF
                    {% endif %}"""

        try:
            entities.append(MQTT_BINARY_SENSOR_PLATFORM_SCHEMA(sensorconfig))
        except:
            _LOGGER.error(f'Could not convert config to to MQTT binary sensor config for id  {sensor["id"]}')
            _LOGGER.debug(sensorconfig)

    return entities


def _get_sensor_config(sensor, entry_data, device_info):
    sensorconfig = {}
    sensorconfig[CONF_NAME] = _get_sensor_name(sensor, entry_data)
    sensorconfig[CONF_OBJECT_ID] = _get_sensor_object_id(sensor, entry_data)
    sensorconfig[CONF_DEVICE] = device_info
    sensorconfig[CONF_ENTITY_CATEGORY] = EntityCategory.DIAGNOSTIC
    sensorconfig[CONF_ENABLED_BY_DEFAULT] = True
    sensorconfig[CONF_STATE_TOPIC] = f'/sensor/{sensor["id"]}/{sensor["data_type"]}'
    sensorconfig[CONF_STATE_CLASS] = _get_sensor_detail(sensor, STATE_CLASS_MAP)
    sensorconfig[CONF_QOS] = 0
    sensorconfig[CONF_FORCE_UPDATE] = True
    discovery_hash = (
        entry_data[CONF_DEVICE_HASH],
        sensor["id"],
        sensor["data_type"],
    )
    sensorconfig[CONF_UNIQUE_ID] = "_".join(discovery_hash)
    if entry_data[CONF_FLM03]:
        device_class = _get_sensor_detail(sensor, DEVICE_CLASS_MAP_FLM03)
    else:
        device_class = _get_sensor_detail(sensor, DEVICE_CLASS_MAP_FLM02)
    if device_class:
        sensorconfig[CONF_DEVICE_CLASS] = device_class
    icon = _get_sensor_detail(sensor, ICON_MAP)
    if icon:
        sensorconfig[CONF_ICON] = icon
    if entry_data[CONF_FLM03]:
        uom = _get_sensor_detail(sensor, UNIT_OF_MEASUREMENT_MAP_FLM03)
    else:
        uom = _get_sensor_detail(sensor, UNIT_OF_MEASUREMENT_MAP_FLM02)
    if uom:
        sensorconfig[CONF_UNIT_OF_MEASUREMENT] = uom

    sensorconfig[CONF_VALUE_TEMPLATE] = """{{ value.split(",")[1] | float }}"""
    if "type" in sensor:
        if sensor["type"] == "temperature":
            sensorconfig[
                CONF_VALUE_TEMPLATE
            ] = """{{ value.split(",")[1] | float | round(1) }}"""
        elif sensor["type"] == "battery":
            sensorconfig[
                CONF_VALUE_TEMPLATE
            ] = """{{ (((value.split(",")[1] | float) / 3.3) * 100) | round(2) }}"""
        elif sensor["type"] == "gas":
            sensorconfig[
                CONF_VALUE_TEMPLATE
            ] = """{{ ((value.split(",")[1] | float) / 1000) }}"""
        elif sensor["type"] == "electricity":
            if "subtype" in sensor and sensor["subtype"] == "pf":
                sensorconfig[
                    CONF_VALUE_TEMPLATE
                ] = """{{ ((value.split(",")[1] | float) * 100) | round(1) }}"""

    return sensorconfig


def _get_sensor_entities(entry_data, device_info):
    entities = []

    for sensor in entry_data[CONFTYPE_SENSOR].values():
        if "enable" not in sensor or sensor["enable"] == 0:
            continue

        if _is_binary_sensor(sensor):
            continue

        if entry_data[CONF_FLM03]:
            dts = _get_sensor_detail(sensor, DATA_TYPE_MAP_FLM03)
        else:
            dts = _get_sensor_detail(sensor, DATA_TYPE_MAP_FLM02)

        for dt in dts:
            s = sensor.copy()
            s["data_type"] = dt
            config = _get_sensor_config(s, entry_data, device_info)
            try:
                entities.append(MQTT_SENSOR_PLATFORM_SCHEMA(config))
            except:
                _LOGGER.error(f'Could not convert config to to MQTT sensor config for id  {s["id"]}')
                _LOGGER.debug(config)

    return entities


def _get_device_info(entry_data):
    return {
        CONF_CONNECTIONS: [],
        CONF_IDENTIFIERS: {
            (DOMAIN, entry_data[CONF_DEVICE_HASH]),
        },
        CONF_MANUFACTURER: "Flukso",
        CONF_NAME: entry_data.get(CONF_DEVICE_SERIAL, entry_data[CONF_DEVICE_HASH]),
        CONF_SW_VERSION: entry_data.get(CONF_DEVICE_FIRMWARE, "unknown"),
    }


def get_entities_for_platform(platform, entry_data):
    """Generate configuration for the given platform."""
    entities = []
    device_info = _get_device_info(entry_data)
    if platform == Platform.BINARY_SENSOR:
        entities.extend(_get_binary_sensor_entities(entry_data, device_info))
    elif platform == Platform.SENSOR:
        entities.extend(_get_sensor_entities(entry_data, device_info))
    return entities


async def async_discover_device(hass, entry):
    """Get the Flukso configs JSON's using MQTT."""
    config_futures = {conftype: asyncio.Future() for conftype in CONFTYPES}
    tap_future = asyncio.Future()
    sub_state = None

    @callback
    def config_message_received(msg):
        splitted_topic = msg.topic.split("/")

        device = splitted_topic[2]
        conftype = splitted_topic[4]

        if conftype in config_futures:
            _LOGGER.debug("storing config type %s for device %s", conftype, device)
            hass.data[DOMAIN][entry.entry_id][conftype] = json.loads(msg.payload)
            config_futures[conftype].set_result(True)
        else:
            _LOGGER.warning("unexpected config type: %s", conftype)

    @callback
    def tap_message_received(msg):
        _LOGGER.debug("TAP received:")
        _LOGGER.debug(msg.payload)
        serial = re.findall("# serial: (.*)", msg.payload)[0]
        firmware = re.findall("# firmware: (.*)", msg.payload)[0]

        hass.data[DOMAIN][entry.entry_id][CONF_DEVICE_SERIAL] = serial
        hass.data[DOMAIN][entry.entry_id][CONF_DEVICE_FIRMWARE] = firmware

        tap_future.set_result(True)

    sub_state = subscription.async_prepare_subscribe_topics(
        hass,
        sub_state,
        {
            f"tap_topic_{hass.data[DOMAIN][entry.entry_id][CONF_DEVICE_HASH]}": {
                "topic": f"/device/{hass.data[DOMAIN][entry.entry_id][CONF_DEVICE_HASH]}/test/tap",
                "msg_callback": tap_message_received,
            },
            f"config_topic_{hass.data[DOMAIN][entry.entry_id][CONF_DEVICE_HASH]}": {
                "topic": f"/device/{hass.data[DOMAIN][entry.entry_id][CONF_DEVICE_HASH]}/config/+",
                "msg_callback": config_message_received,
            },
        },
    )

    await subscription.async_subscribe_topics(
        hass,
        sub_state
    )

    done, _ = await asyncio.wait(config_futures.values(), timeout=2)
    assert config_futures[CONFTYPE_SENSOR] in done
    config_futures[CONFTYPE_SENSOR].result()
    _LOGGER.debug(hass.data[DOMAIN][entry.entry_id][CONFTYPE_SENSOR])

    if config_futures[CONFTYPE_KUBE] in done:
        _LOGGER.debug(hass.data[DOMAIN][entry.entry_id][CONFTYPE_KUBE])
    else:
        _LOGGER.info("kube config not received")

    if config_futures[CONFTYPE_FLX] in done:
        _LOGGER.debug(hass.data[DOMAIN][entry.entry_id][CONFTYPE_FLX])
    else:
        _LOGGER.info("flx config not received")

    done, _ = await asyncio.wait([tap_future], timeout=2)
    if tap_future in done:
        sn = hass.data[DOMAIN][entry.entry_id][CONF_DEVICE_SERIAL]
        version = hass.data[DOMAIN][entry.entry_id][CONF_DEVICE_FIRMWARE]
        _LOGGER.info("We found an FLM03 with serial %s and version %s", sn, version)
        hass.data[DOMAIN][entry.entry_id][CONF_FLM03] = True
    else:
        _LOGGER.info("No TAP information received, we found an FLM02")
        hass.data[DOMAIN][entry.entry_id][CONF_FLM03] = False

    subscription.async_unsubscribe_topics(hass, sub_state)
