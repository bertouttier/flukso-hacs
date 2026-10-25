"""Config flow for Flukso."""

from __future__ import annotations

import logging
import re
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.service_info.mqtt import MqttServiceInfo

from .const import CONF_DEVICE_HASH, DOMAIN

_LOGGER = logging.getLogger(__name__)

DEVICE_HASH_RE = re.compile(r"^[0-9a-f]{32}$")


class FluksoConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a Flukso config flow."""

    VERSION = 1

    _device_hash: str

    async def _async_set_device(self, device_hash: str) -> None:
        # Keep the "flukso_" prefix so existing entries keep matching.
        await self.async_set_unique_id(f"{DOMAIN}_{device_hash}")
        self._abort_if_unique_id_configured()
        self._device_hash = device_hash

    def _async_create_flukso(self) -> ConfigFlowResult:
        return self.async_create_entry(
            title=f"Flukso {self._device_hash}",
            data={CONF_DEVICE_HASH: self._device_hash},
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}
        if user_input is not None:
            device_hash = user_input[CONF_DEVICE_HASH].strip().lower()
            if DEVICE_HASH_RE.match(device_hash):
                await self._async_set_device(device_hash)
                return self._async_create_flukso()
            errors[CONF_DEVICE_HASH] = "invalid_device_hash"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_DEVICE_HASH): str}),
            errors=errors,
        )

    async def async_step_mqtt(
        self, discovery_info: MqttServiceInfo
    ) -> ConfigFlowResult:
        """Handle a flow initialized by a retained /device/<hash>/config/+ message."""
        splitted_topic = discovery_info.topic.split("/")
        if len(splitted_topic) != 5 or not DEVICE_HASH_RE.match(splitted_topic[2]):
            return self.async_abort(reason="invalid_discovery_info")

        device_hash = splitted_topic[2]
        _LOGGER.debug("Discovered Flukso %s", device_hash)
        await self._async_set_device(device_hash)
        self.context["title_placeholders"] = {"device_hash": device_hash}
        return await self.async_step_discovery_confirm()

    async def async_step_discovery_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask the user to confirm a discovered Flukso."""
        if user_input is not None:
            return self._async_create_flukso()

        self._set_confirm_only()
        return self.async_show_form(
            step_id="discovery_confirm",
            description_placeholders={"device_hash": self._device_hash},
        )
