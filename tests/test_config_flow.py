"""Tests for the Flukso config flow."""

from homeassistant.config_entries import SOURCE_MQTT, SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers.service_info.mqtt import MqttServiceInfo
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.flukso.const import CONF_DEVICE_HASH, DOMAIN

from .test_common import DEVICE_HASH


def _discovery(topic: str) -> MqttServiceInfo:
    return MqttServiceInfo(
        topic=topic,
        payload="{}",
        qos=0,
        retain=True,
        subscribed_topic="/device/+/config/+",
        timestamp=None,
    )


async def test_user_flow(hass: HomeAssistant, mqtt_mock) -> None:
    """A valid device hash creates an entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_DEVICE_HASH: "not a hash"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {CONF_DEVICE_HASH: "invalid_device_hash"}

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_DEVICE_HASH: f" {DEVICE_HASH.upper()} "}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_DEVICE_HASH: DEVICE_HASH}
    assert result["result"].unique_id == f"{DOMAIN}_{DEVICE_HASH}"


async def test_user_flow_already_configured(hass: HomeAssistant, mqtt_mock) -> None:
    """The same Flukso cannot be added twice."""
    MockConfigEntry(domain=DOMAIN, unique_id=f"{DOMAIN}_{DEVICE_HASH}").add_to_hass(
        hass
    )
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_DEVICE_HASH: DEVICE_HASH}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_mqtt_discovery(hass: HomeAssistant, mqtt_mock) -> None:
    """A discovered Flukso is added after confirmation."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_MQTT},
        data=_discovery(f"/device/{DEVICE_HASH}/config/sensor"),
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "discovery_confirm"

    # The kube/flx configs of the same Flukso do not start another flow.
    second = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_MQTT},
        data=_discovery(f"/device/{DEVICE_HASH}/config/kube"),
    )
    assert second["type"] is FlowResultType.ABORT
    assert second["reason"] == "already_in_progress"

    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_DEVICE_HASH: DEVICE_HASH}


async def test_mqtt_discovery_invalid_topic(hass: HomeAssistant, mqtt_mock) -> None:
    """Topics that do not carry a device hash are ignored."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_MQTT},
        data=_discovery("/device/nothash/config/sensor"),
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "invalid_discovery_info"
