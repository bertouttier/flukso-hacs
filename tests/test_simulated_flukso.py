"""End-to-end tests against a simulated Flukso on a fake MQTT broker."""

from datetime import timedelta

from freezegun.api import FrozenDateTimeFactory
from homeassistant.config_entries import SOURCE_MQTT, ConfigEntryState
from homeassistant.const import (
    EVENT_STATE_CHANGED,
    STATE_OFF,
    STATE_ON,
    STATE_UNAVAILABLE,
)
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    MockMqttReasonCode,
    async_fire_time_changed,
)

from custom_components.flukso.const import DOMAIN

from .conftest import make_entry, setup_entry
from .flukso_simulator import FLM02_SENSOR_CONFIG, FakeBroker, FluksoSimulator

OTHER_HASH = "fedcba9876543210fedcba9876543210"


def _expected_entity_count(flukso: FluksoSimulator) -> tuple[int, int]:
    """Count the sensors and binary sensors the Flukso config should produce."""
    sensors = binary_sensors = 0
    for sensor in flukso.config["sensor"].values():
        if not isinstance(sensor, dict) or not sensor.get("enable"):
            continue
        if not sensor.get("id"):
            continue
        sensor_type = sensor.get("type")
        if sensor.get("class") == "kube" and sensor_type in (
            "movement",
            "vibration",
            "error",
        ):
            binary_sensors += 1
        elif sensor["data_type"] == "counter" and sensor_type in (
            "electricity",
            "gas",
            "water",
        ):
            sensors += 2  # a flow/power gauge and a counter
        else:
            sensors += 1
    return sensors, binary_sensors


def _state_changes(hass: HomeAssistant, entity_id: str) -> list[Event]:
    events: list[Event] = []

    @callback
    def listener(event: Event) -> None:
        if event.data["entity_id"] == entity_id:
            events.append(event)

    hass.bus.async_listen(EVENT_STATE_CHANGED, listener)
    return events


async def test_flm03_creates_every_enabled_sensor(
    hass: HomeAssistant, flukso: FluksoSimulator
) -> None:
    """Every enabled sensor in the Flukso config becomes an entity on one device."""
    flukso.boot()
    entry = make_entry(flukso.device_hash)
    await setup_entry(hass, entry)

    entities = er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id)
    sensors, binary_sensors = _expected_entity_count(flukso)
    assert len([e for e in entities if e.domain == "sensor"]) == sensors
    assert len([e for e in entities if e.domain == "binary_sensor"]) == binary_sensors
    assert len({e.device_id for e in entities}) == 1

    # Sensor "33" (power factor on port 3) is disabled on the Flukso.
    disabled_id = flukso.config["sensor"]["33"]["id"]
    assert not any(disabled_id in e.unique_id for e in entities)


async def test_energy_meter_stream(
    hass: HomeAssistant, flukso: FluksoSimulator
) -> None:
    """A steady 1 kW load for 6 minutes adds up to 100 Wh."""
    flukso.boot()
    await setup_entry(hass, make_entry(flukso.device_hash))
    power = "sensor.fl01234567_l1_electricity_pplus_gauge"
    energy = "sensor.fl01234567_l1_electricity_pplus_counter"
    power_changes = _state_changes(hass, power)
    energy_changes = _state_changes(hass, energy)

    pplus = flukso.sensor_id(type="electricity", subtype="pplus", port=[2])
    flukso.consume(pplus, 1000, 360)
    await hass.async_block_till_done()

    assert hass.states.get(power).state == "1000.0"
    assert hass.states.get(energy).state == "100.0"
    # 360 identical power readings result in a single state change, and the
    # counter only changes when it crosses the next Wh (plus unknown -> 0 Wh).
    assert len(power_changes) == 1
    assert len(energy_changes) == 101


async def test_flukso_comes_online_after_home_assistant(
    hass: HomeAssistant, flukso: FluksoSimulator
) -> None:
    """Setup is retried until the Flukso publishes its config."""
    entry = make_entry(flukso.device_hash)
    await setup_entry(hass, entry)
    assert entry.state is ConfigEntryState.SETUP_RETRY

    flukso.boot()
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=10))
    await hass.async_block_till_done(wait_background_tasks=True)

    assert entry.state is ConfigEntryState.LOADED
    assert hass.states.get("sensor.fl01234567_keuken_pressure") is not None


async def test_retained_config_does_not_cause_reload_loop(
    hass: HomeAssistant, flukso: FluksoSimulator
) -> None:
    """The replayed retained configs equal the loaded ones, so nothing reloads."""
    flukso.boot()
    entry = make_entry(flukso.device_hash)
    await setup_entry(hass, entry)

    reloads: list[str] = []
    hass.config_entries.async_schedule_reload = reloads.append
    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    flukso.boot()  # the Flukso restarts and republishes the same configs
    await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED
    assert reloads == []


async def test_renaming_a_kube_updates_names_not_entity_ids(
    hass: HomeAssistant, flukso: FluksoSimulator
) -> None:
    """Renaming a kube on the Flukso reloads the entry with the new name."""
    flukso.boot()
    entry = make_entry(flukso.device_hash)
    await setup_entry(hass, entry)
    entity_id = "sensor.fl01234567_keuken_pressure"
    assert hass.states.get(entity_id).name == "FL01234567 keuken pressure"

    flukso.update_config("kube", lambda kube: kube["1"].update(name="kitchen"))
    await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED
    assert hass.states.get(entity_id).name == "FL01234567 kitchen pressure"


async def test_disabling_a_sensor_removes_its_entities(
    hass: HomeAssistant, flukso: FluksoSimulator
) -> None:
    """A sensor disabled on the Flukso no longer has a live entity."""
    flukso.boot()
    entry = make_entry(flukso.device_hash)
    await setup_entry(hass, entry)
    entity_id = "sensor.fl01234567_l1_electricity_pplus_counter"
    assert hass.states.get(entity_id) is not None

    flukso.update_config("sensor", lambda sensor: sensor["13"].update(enable=0))
    await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED
    state = hass.states.get(entity_id)
    assert state is None or state.state == STATE_UNAVAILABLE


async def test_broker_connection_loss(
    hass: HomeAssistant, flukso: FluksoSimulator, mqtt_client_mock
) -> None:
    """Entities are unavailable while the MQTT broker is disconnected."""
    flukso.boot()
    await setup_entry(hass, make_entry(flukso.device_hash))
    entity_id = "sensor.fl01234567_slaapkamer_temperature"
    temperature = flukso.sensor_id(type="temperature", kid=4)
    flukso.reading(temperature, "gauge", 20.5, "°C")
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == "20.5"

    mqtt_client_mock.on_disconnect(None, None, 0, MockMqttReasonCode())
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == STATE_UNAVAILABLE

    mqtt_client_mock.on_connect(None, None, 0, MockMqttReasonCode())
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == "20.5"


async def test_movement_retrigger_extends_on_time(
    hass: HomeAssistant, flukso: FluksoSimulator, freezer: FrozenDateTimeFactory
) -> None:
    """Each movement restarts the off delay."""
    flukso.boot()
    await setup_entry(hass, make_entry(flukso.device_hash))
    entity_id = "binary_sensor.fl01234567_living_movement"
    movement = flukso.sensor_id(type="movement", kid=2)

    flukso.kube_event(movement)
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == STATE_ON

    freezer.tick(timedelta(seconds=8))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    flukso.kube_event(movement)
    await hass.async_block_till_done()

    # 12 seconds after the first event, but only 4 after the second.
    freezer.tick(timedelta(seconds=4))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == STATE_ON

    freezer.tick(timedelta(seconds=7))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == STATE_OFF


async def test_flm02(hass: HomeAssistant, broker: FakeBroker) -> None:
    """An FLM02 publishes no TAP report and no kube or flx config."""
    flukso = FluksoSimulator(broker, OTHER_HASH, flm03=False)
    flukso.boot()
    entry = make_entry(OTHER_HASH)
    await setup_entry(hass, entry)

    device = dr.async_get(hass).async_get_device_by_identifier(
        (DOMAIN, OTHER_HASH), entry.entry_id
    )
    assert device.model == "FLM02"
    assert device.name == OTHER_HASH
    assert device.sw_version is None

    entities = er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id)
    assert len(entities) == _expected_entity_count(flukso)[0]

    main = flukso.sensor_id(function="main")
    flukso.consume(main, 2000, 9)
    water = flukso.sensor_id(type="water")
    flukso.reading(water, "counter", 1234, "L")
    await hass.async_block_till_done()

    assert hass.states.get(f"sensor.{OTHER_HASH}_main_electricity_gauge").state == (
        "2000.0"
    )
    assert hass.states.get(f"sensor.{OTHER_HASH}_main_electricity_counter").state == (
        "5.0"
    )
    water_state = hass.states.get(f"sensor.{OTHER_HASH}_water_water_counter")
    assert water_state.state == "1234.0"
    assert water_state.attributes["device_class"] == "water"


async def test_two_fluksos_are_isolated(
    hass: HomeAssistant, broker: FakeBroker, flukso: FluksoSimulator
) -> None:
    """Readings of one Flukso do not leak into the other."""
    other_config = {
        key: {**sensor, "id": sensor["id"].replace("f", "e", 1)}
        for key, sensor in FLM02_SENSOR_CONFIG.items()
        if "id" in sensor
    }
    other = FluksoSimulator(broker, OTHER_HASH, flm03=False, sensor=other_config)
    flukso.boot()
    other.boot()
    await setup_entry(hass, make_entry(flukso.device_hash))
    await setup_entry(hass, make_entry(OTHER_HASH))

    other.consume(other.sensor_id(function="main"), 500, 1)
    await hass.async_block_till_done()

    assert hass.states.get(f"sensor.{OTHER_HASH}_main_electricity_gauge").state == (
        "500.0"
    )
    assert hass.states.get("sensor.fl01234567_l1_electricity_pplus_gauge").state == (
        "unknown"
    )
    for entry in hass.config_entries.async_entries(DOMAIN):
        assert (
            len(dr.async_entries_for_config_entry(dr.async_get(hass), entry.entry_id))
            == 1
        )


async def test_discovery_end_to_end(
    hass: HomeAssistant, flukso: FluksoSimulator
) -> None:
    """A booting Flukso is discovered once and set up after confirmation."""
    flukso.boot()
    await hass.async_block_till_done()

    flows = hass.config_entries.flow.async_progress_by_handler(DOMAIN)
    assert len(flows) == 1
    assert flows[0]["context"]["source"] == SOURCE_MQTT
    assert flows[0]["step_id"] == "discovery_confirm"

    result = await hass.config_entries.flow.async_configure(flows[0]["flow_id"], {})
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.CREATE_ENTRY

    entry = result["result"]
    assert entry.state is ConfigEntryState.LOADED
    assert hass.states.get("sensor.fl01234567_keuken_pressure") is not None

    # Rebooting the Flukso does not offer it again.
    flukso.boot()
    await hass.async_block_till_done()
    assert hass.config_entries.flow.async_progress_by_handler(DOMAIN) == []
