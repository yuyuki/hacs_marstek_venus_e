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
    CONF_BLE_MAC,
    CONF_TIMEOUT,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MODE_AUTO,
    MODE_AI,
    MODE_MANUAL,
    MODE_PASSIVE,
    VALID_MODES,
)
from .udp_client import MarstekUDPClient

_LOGGER = logging.getLogger(__name__)

ACTION_MANUAL = "manual"
ACTION_RETRY_DISCOVERY = "retry_discovery"


class MarstekConfigFlow(config_entries.ConfigFlow, domain="hacs_marstek_venus_e"):
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

        schema = vol.Schema(
            {
                vol.Required("confirm", default=True): bool,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
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

        if not self.discovered_devices:
            _LOGGER.warning(
                "No Marstek devices responded to broadcast discovery; falling back to manual IP entry"
            )
            return await self.async_step_manual_ip()

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

            if selected == ACTION_RETRY_DISCOVERY:
                return await self.async_step_discovery()

            # If user chose manual entry, present a dedicated form
            if selected == ACTION_MANUAL:
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
                
                return self._create_device_entry()
        
        # Build device list for selection
        device_options: dict[str, str] = {}
        if self.discovered_devices:
            for ip, port, payload in self.discovered_devices:
                device_info = payload.get("result", {})
                device_name = device_info.get("device", "Unknown")
                device_ip = device_info.get("ip", ip)
                src = payload.get("src", "Unknown")
                # Format: Device IP - Device Name [src]
                label = f"{device_ip} - {device_name} [{src}]"
                device_options[device_ip] = label
        
        # Add setup actions.
        device_options[ACTION_RETRY_DISCOVERY] = "Retry device discovery"
        device_options[ACTION_MANUAL] = "Enter IP manually"
        
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
                
                return self._create_device_entry()

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

    def _create_device_entry(self) -> FlowResult:
        """Create the device without changing its existing schedules."""
        ip_address = self.context["ip_address"]
        return self.async_create_entry(
            title=f"Marstek Venus E ({ip_address})",
            data={
                CONF_IP_ADDRESS: ip_address,
                CONF_PORT: self.context["port"],
                CONF_BLE_MAC: self.context["ble_mac"],
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
        self._config_entry = config_entry
        self.current_schedule: dict[str, Any] = {}
    
    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options - show menu."""
        return self.async_show_menu(
            step_id="init",
            menu_options=["configure_manual_mode", "configure_update_interval"],
        )
    
    async def async_step_configure_manual_mode(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure manual mode schedules."""
        if user_input is not None:
            # Save the schedule configuration
            time_num = user_input.get("time_slot")
            
            # Get coordinator to send the configuration
            coordinator = self.hass.data[DOMAIN].get(self._config_entry.entry_id)
            if coordinator:
                try:
                    await coordinator.set_manual_schedule(
                        time_num=time_num,
                        start_time=str(user_input["start_time"])[:5],
                        end_time=str(user_input["end_time"])[:5],
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
                vol.Required("time_slot", default=0): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0,
                        max=9,
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
                        min=-2500,
                        max=2500,
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
    
    async def async_step_configure_update_interval(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure the update interval."""
        if user_input is not None:
            # Get the new interval
            new_interval = user_input.get("scan_interval")
            
            # Update the options
            new_options = {**self._config_entry.options}
            new_options[CONF_SCAN_INTERVAL] = new_interval
            
            # Get coordinator and update its interval
            coordinator = self.hass.data.get(DOMAIN, {}).get(self._config_entry.entry_id)
            if coordinator:
                from datetime import timedelta
                # Convert minutes to seconds for the coordinator
                coordinator.update_interval = timedelta(seconds=new_interval * 60)
                _LOGGER.info(
                    "Update interval changed to %d minutes (%d seconds)",
                    new_interval,
                    new_interval * 60,
                )
            
            return self.async_create_entry(title="", data=new_options)
        
        # Get current interval (in minutes, converting from seconds if stored that way)
        current_interval_options = self._config_entry.options.get(
            CONF_SCAN_INTERVAL,
            5,  # Default is 5 minutes
        )
        
        # Define the form schema
        schema = vol.Schema(
            {
                vol.Required(
                    "scan_interval",
                    default=current_interval_options,
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1,
                        max=60,
                        step=1,
                        unit_of_measurement="minutes",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
            }
        )
        
        return self.async_show_form(
            step_id="configure_update_interval",
            data_schema=schema,
            description_placeholders={
                "info": "Configure how often the integration polls the device for data updates. Lower values provide more real-time data but may increase network traffic."
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
