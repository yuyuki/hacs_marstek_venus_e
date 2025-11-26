"""Config flow for Marstek Venus E integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_IP_ADDRESS, CONF_PORT
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_BLE_MAC,
    CONF_TIMEOUT,
    MODE_AUTO,
    MODE_AI,
    MODE_MANUAL,
    MODE_PASSIVE,
    VALID_MODES,
)
from .udp_client import MarstekUDPClient

_LOGGER = logging.getLogger(__name__)


class MarstekConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Marstek Venus E."""

    VERSION = 1
    
    def __init__(self):
        """Initialize config flow."""
        super().__init__()
        self.discovered_devices: list[tuple[str, int, dict[str, Any]]] = []
    
    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> MarstekOptionsFlow:
        """Get the options flow for this handler."""
        return MarstekOptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initiated by the user.
        
        Starts the discovery process.
        
        Args:
            user_input: Input from the user
            
        Returns:
            Config flow result
        """
        if user_input is not None:
            # User clicked continue, move to discovery
            return await self.async_step_discovery()
        
        return self.async_show_form(
            step_id="user",
            description_placeholders={},
        )

    async def async_step_discovery(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle discovery step.
        
        Attempts to discover Marstek devices on the local network.
        
        Args:
            user_input: Input from the user
            
        Returns:
            Config flow result
        """
        errors: dict[str, str] = {}
        
        # Attempt automatic discovery
        try:
            _LOGGER.debug("Starting Marstek device discovery...")
            self.discovered_devices = await MarstekUDPClient.discover(timeout=15.0, port=30000)
            _LOGGER.debug("Found %d device(s)", len(self.discovered_devices))
        except Exception as err:
            _LOGGER.error("Device discovery failed: %s", err)
            self.discovered_devices = []

        # Move to selection step
        return await self.async_step_select_device()

    async def async_step_select_device(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle device selection step.
        
        Allows user to select from discovered devices or enter IP manually.
        
        Args:
            user_input: Input from the user
            
        Returns:
            Config flow result
        """
        errors: dict[str, str] = {}
        
        if user_input is not None:
            selected = user_input.get(CONF_IP_ADDRESS)
            port = user_input.get(CONF_PORT, 30000)
            ble_mac = user_input.get(CONF_BLE_MAC, "")

            _LOGGER.debug("User selected device value: %s (port %s)", selected, port)

            # If user chose manual entry, present a dedicated form
            if selected == "manual":
                return await self.async_step_manual_ip()

            # Otherwise selected should be an IP (from device_options) or direct input
            ip_address = selected

            if not ip_address:
                errors["base"] = "no_device_selected"
            else:
                # For discovered devices, extract BLE MAC from the discovery response
                # Since the device only responds to broadcast, we can't verify unicast connection
                # But if it responded to discovery, it's reachable
                for disc_ip, disc_port, payload in self.discovered_devices:
                    if disc_ip == ip_address:
                        device_info = payload.get("result", {})
                        if not ble_mac:
                            ble_mac = device_info.get("ble_mac", "")
                        break
                
                # Check if already configured
                await self.async_set_unique_id(ip_address)
                self._abort_if_unique_id_configured()
                
                # Store the data for potential schedule clearing
                self.context["ip_address"] = ip_address
                self.context["port"] = port
                self.context["ble_mac"] = ble_mac
                
                # Ask if user wants to clear schedules
                return await self.async_step_clear_schedules()
        
        # Build device list for selection
        device_options: dict[str, str] = {}
        if self.discovered_devices:
            for ip, port, payload in self.discovered_devices:
                device_info = payload.get("result", {})
                device_name = device_info.get("device", "Unknown")
                src = payload.get("src", "Unknown")
                # Format: IP - Device Name [src]
                label = f"{ip} - {device_name} [{src}]"
                device_options[ip] = label
        
        # Add manual entry option
        device_options["manual"] = "Enter IP manually"
        
        # Build schema
        schema = {}
        
        if device_options:
            schema[vol.Required(CONF_IP_ADDRESS)] = vol.In(device_options)
        else:
            schema[vol.Required(CONF_IP_ADDRESS)] = str
        
        schema[vol.Optional(CONF_PORT, default=30000)] = int
        schema[vol.Optional(CONF_BLE_MAC, default="")] = str
        
        return self.async_show_form(
            step_id="select_device",
            data_schema=vol.Schema(schema),
            errors=errors,
            description_placeholders={
                "device_count": str(len(self.discovered_devices)),
            },
        )

    async def async_step_manual_ip(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle manual IP entry when user chooses to enter an IP manually.
        
        Note: Connection validation is skipped for manual entry since the device
        only responds to UDP broadcasts, not to unicast requests. The connection
        will be verified when the integration attempts to retrieve data after
        configuration is saved.
        """
        errors: dict[str, str] = {}

        if user_input is not None:
            ip_address = user_input.get(CONF_IP_ADDRESS)
            port = user_input.get(CONF_PORT, 30000)
            ble_mac = user_input.get(CONF_BLE_MAC, "")

            _LOGGER.debug("Manual IP provided: %s:%s", ip_address, port)

            if not ip_address:
                errors["base"] = "invalid_ip"
            else:
                # Check if already configured
                await self.async_set_unique_id(ip_address)
                self._abort_if_unique_id_configured()
                
                # Store the data for potential schedule clearing
                self.context["ip_address"] = ip_address
                self.context["port"] = port
                self.context["ble_mac"] = ble_mac
                
                # Ask if user wants to clear schedules
                return await self.async_step_clear_schedules()

        schema = vol.Schema(
            {
                vol.Required(CONF_IP_ADDRESS): str,
                vol.Optional(CONF_PORT, default=30000): int,
                vol.Optional(CONF_BLE_MAC, default=""): str,
            }
        )

        return self.async_show_form(
            step_id="manual_ip",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_clear_schedules(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Ask user if they want to clear all manual schedules.
        
        Args:
            user_input: Input from the user
            
        Returns:
            Config flow result
        """
        errors: dict[str, str] = {}
        
        if user_input is not None:
            clear_schedules = user_input.get("clear_schedules", False)
            
            # Get device info from context
            ip_address = self.context.get("ip_address")
            port = self.context.get("port", 30000)
            ble_mac = self.context.get("ble_mac", "")
            
            # If user wants to clear schedules, do it now
            if clear_schedules:
                try:
                    _LOGGER.info("Clearing all manual schedules for %s:%s", ip_address, port)
                    client = MarstekUDPClient(ip_address, port, timeout=10.0)
                    results = await client.clear_all_manual_schedules()
                    _LOGGER.info(
                        "Cleared schedules: %d/%d slots disabled",
                        results["success_count"],
                        results["total_slots"],
                    )
                except Exception as err:
                    _LOGGER.error("Failed to clear schedules: %s", err)
                    errors["base"] = "clear_failed"
            
            if not errors:
                # Create the config entry
                return self.async_create_entry(
                    title=f"Marstek Venus E ({ip_address})",
                    data={
                        CONF_IP_ADDRESS: ip_address,
                        CONF_PORT: port,
                        CONF_BLE_MAC: ble_mac,
                    },
                )
        
        schema = vol.Schema(
            {
                vol.Optional("clear_schedules", default=False): bool,
            }
        )
        
        return self.async_show_form(
            step_id="clear_schedules",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "info": "This will disable all 10 time slots (0-9) for manual schedules."
            },
        )

    async def async_step_import(self, import_data: dict[str, Any]) -> FlowResult:
        """Import config from configuration.yaml.
        
        Args:
            import_data: Configuration data to import
            
        Returns:
            Config flow result
        """

        return await self.async_step_select_device(import_data)


class MarstekOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Marstek Venus E."""
    
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self.current_schedule: dict[str, Any] = {}
    
    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        # Go directly to configure manual mode (API doesn't support reading schedules)
        return await self.async_step_configure_manual_mode()
    
    async def async_step_configure_manual_mode(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure manual mode schedules."""
        if user_input is not None:
            # Save the schedule configuration
            time_num = user_input.get("time_slot")
            
            # Get coordinator to send the configuration
            coordinator = self.hass.data[DOMAIN].get(self.config_entry.entry_id)
            if coordinator:
                try:
                    await coordinator.set_manual_schedule(
                        time_num=time_num,
                        start_time=user_input.get("start_time"),
                        end_time=user_input.get("end_time"),
                        week_set=self._calculate_week_set(user_input.get("days", [])),
                        power=user_input.get("power"),
                        enable=user_input.get("enable", True),
                    )
                    return self.async_create_entry(title="", data={})
                except Exception as err:
                    _LOGGER.error("Error setting manual schedule: %s", err)
                    return self.async_abort(reason="schedule_failed")
        
        # Define the form schema
        schema = vol.Schema(
            {
                vol.Required("time_slot", default=1): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1,
                        max=4,
                        step=1,
                        mode=selector.NumberSelectorMode.SLIDER,
                    )
                ),
                vol.Required("start_time"): selector.TimeSelector(),
                vol.Required("end_time"): selector.TimeSelector(),
                vol.Required("days", default=[]): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            {"label": "Monday", "value": "monday"},
                            {"label": "Tuesday", "value": "tuesday"},
                            {"label": "Wednesday", "value": "wednesday"},
                            {"label": "Thursday", "value": "thursday"},
                            {"label": "Friday", "value": "friday"},
                            {"label": "Saturday", "value": "saturday"},
                            {"label": "Sunday", "value": "sunday"},
                        ],
                        multiple=True,
                        mode=selector.SelectSelectorMode.LIST,
                    )
                ),
                vol.Required("power", default=0): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=-10000,
                        max=10000,
                        step=100,
                        unit_of_measurement="W",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional("enable", default=True): selector.BooleanSelector(),
            }
        )
        
        return self.async_show_form(
            step_id="configure_manual_mode",
            data_schema=schema,
            description_placeholders={
                "power_info": "Use negative values to charge (e.g., -1000W), positive to discharge (e.g., 1000W). Note: The API does not support reading back schedules, so configure carefully."
            },
        )
    
    def _calculate_week_set(self, days: list[str]) -> int:
        """Calculate week_set bitmask from day names."""
        day_map = {
            "monday": 1,
            "tuesday": 2,
            "wednesday": 4,
            "thursday": 8,
            "friday": 16,
            "saturday": 32,
            "sunday": 64,
        }
        
        week_set = 0
        for day in days:
            week_set |= day_map.get(day, 0)
        
        return week_set if week_set > 0 else 127  # Default to all days if none selected
