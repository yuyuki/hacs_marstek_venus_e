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
