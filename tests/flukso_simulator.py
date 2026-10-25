"""A simulated Flukso publishing on a fake MQTT broker.

The broker keeps retained messages and replays them to every new subscription,
like a real broker (and an MQTT bridge to a Flukso) does. Live messages are
delivered through the mocked MQTT client of pytest-homeassistant-custom-component.
"""

from __future__ import annotations

import copy
import json
import time
from collections.abc import Callable
from typing import Any

from homeassistant.components import mqtt
from homeassistant.components.mqtt.models import ReceiveMessage
from homeassistant.core import HomeAssistant
from paho.mqtt.client import topic_matches_sub
from pytest_homeassistant_custom_component.common import async_fire_mqtt_message

from .test_common import (
    DEVICE_HASH,
    FLM03_FLX_CONFIG,
    FLM03_KUBE_CONFIG,
    FLM03_SENSOR_CONFIG,
)

TAP_TEMPLATE = """
1..3
# date: Mon, 20 Sep 2021 10:19:33 +0000
# serial: {serial}
# firmware: {firmware}
ok 1 - flxd daemon running
ok 2 - sensor board communication
ok 3 - sensor config loaded
"""

FLM02_SENSOR_CONFIG = {
    "main": {"hw_major": "2", "hw_minor": "1"},
    "1": {
        "id": "f0000000000000000000000000000001",
        "class": "analog",
        "type": "electricity",
        "function": "main",
        "port": [1],
        "enable": 1,
        "data_type": "counter",
    },
    "2": {
        "id": "f0000000000000000000000000000002",
        "class": "analog",
        "type": "electricity",
        "function": "solar",
        "port": [2],
        "enable": 1,
        "data_type": "counter",
    },
    "3": {
        "id": "f0000000000000000000000000000003",
        "class": "analog",
        "type": "electricity",
        "function": "spare",
        "port": [3],
        "enable": 0,
        "data_type": "counter",
    },
    "4": {
        "id": "f0000000000000000000000000000004",
        "class": "pulse",
        "type": "water",
        "function": "water",
        "port": [4],
        "enable": 1,
        "data_type": "counter",
    },
}


class FakeBroker:
    """Keeps retained messages and replays them to new subscriptions."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the broker."""
        self.hass = hass
        self.retained: dict[str, str] = {}

    def publish(self, topic: str, payload: str, retain: bool = False) -> None:
        """Publish a message, delivering it to the current subscribers.

        Like a real broker, the retain flag is only set when a retained message
        is replayed to a new subscription, not when it is forwarded live.
        """
        if retain:
            self.retained[topic] = payload
        async_fire_mqtt_message(self.hass, topic, payload)

    def clear_retained(self, prefix: str) -> None:
        """Remove the retained messages under a topic prefix."""
        for topic in [t for t in self.retained if t.startswith(prefix)]:
            del self.retained[topic]

    async def async_subscribe(
        self,
        original: Callable[..., Any],
        hass: HomeAssistant,
        topic: str,
        msg_callback: Callable[[ReceiveMessage], None],
        *args: Any,
        **kwargs: Any,
    ) -> Callable[[], None]:
        """Subscribe and replay the matching retained messages to this subscriber only."""
        unsubscribe = await original(hass, topic, msg_callback, *args, **kwargs)
        subscribed = True

        def deliver(msg: ReceiveMessage) -> None:
            if subscribed:
                msg_callback(msg)

        for retained_topic, payload in list(self.retained.items()):
            if topic_matches_sub(topic, retained_topic):
                msg = ReceiveMessage(
                    retained_topic, payload, 0, True, topic, time.monotonic()
                )
                hass.loop.call_soon(deliver, msg)

        def unsubscribe_wrapper() -> None:
            nonlocal subscribed
            subscribed = False
            unsubscribe()

        return unsubscribe_wrapper


class FluksoSimulator:
    """A Flukso (FLM02 or FLM03) that publishes its config and readings."""

    def __init__(
        self,
        broker: FakeBroker,
        device_hash: str = DEVICE_HASH,
        *,
        flm03: bool = True,
        sensor: dict[str, Any] | None = None,
        kube: dict[str, Any] | None = None,
        flx: dict[str, Any] | None = None,
        serial: str = "FL01234567",
        firmware: str = "380",
    ) -> None:
        """Initialize the simulated Flukso."""
        self.broker = broker
        self.device_hash = device_hash
        self.flm03 = flm03
        default_sensor = FLM03_SENSOR_CONFIG if flm03 else FLM02_SENSOR_CONFIG
        self.config: dict[str, dict[str, Any]] = {
            "sensor": copy.deepcopy(sensor or default_sensor),
            "kube": copy.deepcopy(kube or (FLM03_KUBE_CONFIG if flm03 else {})),
            "flx": copy.deepcopy(flx or (FLM03_FLX_CONFIG if flm03 else {})),
        }
        self.serial = serial
        self.firmware = firmware
        self.timestamp = 1_632_134_400
        self.counters: dict[tuple[str, str], float] = {}

    # Device lifecycle

    def boot(self) -> None:
        """Publish the retained configs and, on an FLM03, the TAP report."""
        for conftype in ("flx", "kube", "sensor"):
            if self.config[conftype]:
                self.publish_config(conftype)
        if self.flm03:
            self.broker.publish(
                f"/device/{self.device_hash}/test/tap",
                TAP_TEMPLATE.format(serial=self.serial, firmware=self.firmware),
                retain=True,
            )

    def publish_config(self, conftype: str) -> None:
        """(Re)publish one retained config."""
        self.broker.publish(
            f"/device/{self.device_hash}/config/{conftype}",
            json.dumps(self.config[conftype]),
            retain=True,
        )

    def update_config(
        self, conftype: str, change: Callable[[dict[str, Any]], None]
    ) -> None:
        """Change a config like the Flukso web UI does, and publish it."""
        change(self.config[conftype])
        self.publish_config(conftype)

    def factory_reset(self) -> None:
        """Forget everything the Flukso published."""
        self.broker.clear_retained(f"/device/{self.device_hash}/")

    # Lookups

    def sensor_id(self, **match: Any) -> str:
        """Return the id of the single sensor matching all given fields."""
        found = [
            s["id"]
            for s in self.config["sensor"].values()
            if isinstance(s, dict) and all(s.get(k) == v for k, v in match.items())
        ]
        assert len(found) == 1, f"{match} matches {found}"
        return found[0]

    # Readings

    def tick(self, seconds: int = 1) -> int:
        """Advance the Flukso clock."""
        self.timestamp += seconds
        return self.timestamp

    def reading(
        self, sensor_id: str, data_type: str, value: float, unit: str | None = None
    ) -> None:
        """Publish one '[timestamp,value,unit]' reading."""
        parts = [str(self.timestamp), repr(value)]
        if unit is not None:
            parts.append(json.dumps(unit))
        self.broker.publish(f"/sensor/{sensor_id}/{data_type}", f"[{','.join(parts)}]")

    def consume(self, sensor_id: str, watts: float, seconds: int) -> float:
        """Draw constant power, publishing the gauge and the Wh counter each second."""
        key = (sensor_id, "counter")
        for _ in range(seconds):
            self.tick()
            self.counters[key] = self.counters.get(key, 0.0) + watts / 3600
            self.reading(sensor_id, "gauge", watts, "W")
            self.reading(sensor_id, "counter", round(self.counters[key]), "Wh")
        return self.counters[key]

    def kube_event(self, sensor_id: str) -> None:
        """A movement or vibration kube fires."""
        self.tick()
        self.reading(sensor_id, "counter", 1)


def subscribe_patch(broker: FakeBroker) -> Callable[..., Any]:
    """Return a replacement for mqtt.async_subscribe that replays retained messages."""
    original = mqtt.async_subscribe

    async def async_subscribe(
        hass: HomeAssistant, topic: str, msg_callback: Any, *args: Any, **kwargs: Any
    ) -> Callable[[], None]:
        return await broker.async_subscribe(
            original, hass, topic, msg_callback, *args, **kwargs
        )

    return async_subscribe
