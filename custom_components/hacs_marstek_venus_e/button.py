"""Button platform for Marstek Venus E integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.button import ButtonEntity, ButtonDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MarstekDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Marstek Venus E button entities.
    
    Args:
        hass: Home Assistant instance
        entry: Config entry
        async_add_entities: Callback to add entities
    """
    coordinator: MarstekDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([
        MarstekClearSchedulesButton(coordinator, entry),
        MarstekRefreshBatteryButton(coordinator, entry),
        MarstekRefreshEnergyStatusButton(coordinator, entry),
        MarstekRefreshModeButton(coordinator, entry),
    ])


class MarstekClearSchedulesButton(CoordinatorEntity, ButtonEntity):
    """Button to clear all manual schedules."""

    _attr_device_class = ButtonDeviceClass.RESTART
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MarstekDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the button.
        
        Args:
            coordinator: Data coordinator
            entry: Config entry
        """
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_clear_schedules"
        self._attr_name = "Clear all schedules"
        self._attr_icon = "mdi:calendar-remove"

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information.
        
        Returns:
            Device information dictionary
        """
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "Marstek Venus E",
            "manufacturer": "Marstek",
            "model": "Venus E",
        }

    async def async_press(self) -> None:
        """Handle button press."""
        try:
            _LOGGER.info("Clearing all manual schedules via button")
            results = await self.coordinator.clear_all_manual_schedules()
            
            _LOGGER.info(
                "Cleared manual schedules: %d/%d slots disabled",
                results["success_count"],
                results["total_slots"],
            )
            
            if results["failed_slots"]:
                _LOGGER.warning("Failed to disable slots: %s", results["failed_slots"])
                
        except Exception as err:
            _LOGGER.error("Error clearing manual schedules: %s", err)
            raise


class MarstekRefreshBatteryButton(CoordinatorEntity, ButtonEntity):
    """Button to manually call Bat.GetStatus."""

    _attr_device_class = ButtonDeviceClass.UPDATE
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MarstekDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the button.
        
        Args:
            coordinator: Data coordinator
            entry: Config entry
        """
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_refresh_battery"
        self._attr_name = "Refresh Battery Status"
        self._attr_icon = "mdi:battery-sync"

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information.
        
        Returns:
            Device information dictionary
        """
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "Marstek Venus E",
            "manufacturer": "Marstek",
            "model": "Venus E",
        }

    async def async_press(self) -> None:
        """Handle button press."""
        try:
            _LOGGER.info("Manual Bat.GetStatus call via button")
            data = await self.coordinator.refresh_battery_data()
            _LOGGER.info("Battery Status: %s", data)
            
            # Log key fields for user visibility
            if data:
                _LOGGER.info(
                    "Battery: SOC=%s%%, Temp=%s°C, Capacity=%sWh, Rated=%sWh, Charging=%s, Discharging=%s",
                    data.get("soc"),
                    data.get("bat_temp"),
                    data.get("bat_capacity"),
                    data.get("rated_capacity"),
                    data.get("charg_flag"),
                    data.get("dischrg_flag"),
                )
                
        except Exception as err:
            _LOGGER.error("Error calling Bat.GetStatus: %s", err)
            raise


class MarstekRefreshEnergyStatusButton(CoordinatorEntity, ButtonEntity):
    """Button to manually call ES.GetStatus."""

    _attr_device_class = ButtonDeviceClass.UPDATE
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MarstekDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the button.
        
        Args:
            coordinator: Data coordinator
            entry: Config entry
        """
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_refresh_energy_status"
        self._attr_name = "Refresh Energy Status"
        self._attr_icon = "mdi:flash-sync"

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information.
        
        Returns:
            Device information dictionary
        """
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "Marstek Venus E",
            "manufacturer": "Marstek",
            "model": "Venus E",
        }

    async def async_press(self) -> None:
        """Handle button press."""
        try:
            _LOGGER.info("Manual ES.GetStatus call via button")
            data = await self.coordinator.client.get_energy_system_status()
            _LOGGER.info("Energy System Status: %s", data)
            
            # Log key fields for user visibility
            if data:
                _LOGGER.info(
                    "Energy System: Battery=%s%% (%sWh), PV=%sW, Grid=%sW, OffGrid=%sW",
                    data.get("bat_soc"),
                    data.get("bat_cap"),
                    data.get("pv_power"),
                    data.get("ongrid_power"),
                    data.get("offgrid_power"),
                )
                
        except Exception as err:
            _LOGGER.error("Error calling ES.GetStatus: %s", err)
            raise


class MarstekRefreshModeButton(CoordinatorEntity, ButtonEntity):
    """Button to manually call ES.GetMode."""

    _attr_device_class = ButtonDeviceClass.UPDATE
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MarstekDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the button.
        
        Args:
            coordinator: Data coordinator
            entry: Config entry
        """
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_refresh_mode"
        self._attr_name = "Refresh Mode & CT Data"
        self._attr_icon = "mdi:cog-sync"

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information.
        
        Returns:
            Device information dictionary
        """
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "Marstek Venus E",
            "manufacturer": "Marstek",
            "model": "Venus E",
        }

    async def async_press(self) -> None:
        """Handle button press."""
        try:
            _LOGGER.info("Manual ES.GetMode call via button")
            data = await self.coordinator.refresh_mode_data()
            _LOGGER.info("Mode & CT Data: %s", data)
            
            # Log key fields for user visibility
            if data:
                ct_state = "Connected" if data.get("ct_state") else "Disconnected"
                _LOGGER.info(
                    "Mode: %s, Battery=%s%%, Grid=%sW, OffGrid=%sW, CT=%s (A=%sW, B=%sW, C=%sW, Total=%sW)",
                    data.get("mode"),
                    data.get("bat_soc"),
                    data.get("ongrid_power"),
                    data.get("offgrid_power"),
                    ct_state,
                    data.get("a_power"),
                    data.get("b_power"),
                    data.get("c_power"),
                    data.get("total_power"),
                )
                
        except Exception as err:
            _LOGGER.error("Error calling ES.GetMode: %s", err)
            raise
