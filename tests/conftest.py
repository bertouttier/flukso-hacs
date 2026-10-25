"""Fixtures for testing."""

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.flukso.const import CONF_DEVICE_HASH, DOMAIN

from .flukso_simulator import FakeBroker, FluksoSimulator, subscribe_patch
from .test_common import DEVICE_HASH


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations."""
    return


@pytest.fixture
def expected_lingering_timers() -> bool:
    """The mocked MQTT client leaves its misc loop timer running."""
    return True


@pytest.fixture(autouse=True)
def short_timeouts(monkeypatch):
    """Do not wait for configs that are not going to arrive."""
    monkeypatch.setattr("custom_components.flukso.discovery.CONFIG_TIMEOUT", 0.5)
    monkeypatch.setattr(
        "custom_components.flukso.discovery.OPTIONAL_CONFIG_TIMEOUT", 0.1
    )


@pytest.fixture
def config_entry() -> MockConfigEntry:
    """Return a config entry for the default simulated Flukso."""
    return make_entry()


def make_entry(device_hash: str = DEVICE_HASH) -> MockConfigEntry:
    """Return a config entry for the Flukso with the given device hash."""
    return MockConfigEntry(
        domain=DOMAIN,
        unique_id=f"{DOMAIN}_{device_hash}",
        title=f"Flukso {device_hash}",
        data={CONF_DEVICE_HASH: device_hash},
    )


async def setup_entry(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    """Add and set up a config entry."""
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


@pytest.fixture
def broker(hass: HomeAssistant, mqtt_mock, monkeypatch) -> FakeBroker:
    """Return a fake broker that replays retained messages to new subscribers."""
    fake_broker = FakeBroker(hass)
    monkeypatch.setattr(
        "homeassistant.components.mqtt.async_subscribe", subscribe_patch(fake_broker)
    )
    return fake_broker


@pytest.fixture
def flukso(broker: FakeBroker) -> FluksoSimulator:
    """Return a simulated FLM03 that has not booted yet."""
    return FluksoSimulator(broker)
