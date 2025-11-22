"""Config flow for Marstek Venus E integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_IP_ADDRESS, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_BLE_MAC, CONF_TIMEOUT
from .udp_client import MarstekUDPClient

_LOGGER = logging.getLogger(__name__)


class MarstekConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Marstek Venus E."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initiated by the user.
        
        Args:
            user_input: Input from the user
            
        Returns:
            Config flow result
        """
        errors: dict[str, str] = {}

        # Attempt automatic discovery to pre-fill IP address
        default_ip: str | None = None
        try:
            discovered = await MarstekUDPClient.discover(timeout=2.0, port=30000)
            if discovered:
                # discovered is list of tuples (ip, port, payload)
                default_ip = discovered[0][0]
                _LOGGER.debug("Discovered Marstek device at %s", default_ip)
        except Exception:
            _LOGGER.debug("Device discovery failed or returned no devices")

        if user_input is not None:
            # Validate connection
            try:
                client = MarstekUDPClient(
                    ip_address=user_input[CONF_IP_ADDRESS],
                    port=user_input.get(CONF_PORT, 30000),
                )
                await client.get_realtime_data()
                
            except Exception as err:
                _LOGGER.error("Failed to connect to device: %s", err)
                errors["base"] = "cannot_connect"
            else:
                # Check if already configured
                await self.async_set_unique_id(user_input[CONF_IP_ADDRESS])
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(
                    title=f"Marstek Venus E ({user_input[CONF_IP_ADDRESS]})",
                    data=user_input,
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_IP_ADDRESS, default=default_ip or ""): str,
                vol.Optional(CONF_PORT, default=30000): int,
                vol.Optional(CONF_BLE_MAC, default=""): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "docs_url": "https://github.com/YOUR-USERNAME/marstek-venus-e"
            },
        )

    async def async_step_import(self, import_data: dict[str, Any]) -> FlowResult:
        """Import config from configuration.yaml.
        
        Args:
            import_data: Configuration data to import
            
        Returns:
            Config flow result
        """
        return await self.async_step_user(import_data)
