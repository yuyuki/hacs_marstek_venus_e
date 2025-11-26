"""Select platform for Marstek Venus E."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    ATTR_OPERATING_MODE,
    MODE_AUTO,
    MODE_AI,
    MODE_MANUAL,
    MODE_PASSIVE,
    VALID_MODES,
)
from .coordinator import MarstekDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Marstek Venus E select entities.
    
    Args:
        hass: Home Assistant instance
        entry: Configuration entry
        async_add_entities: Callback to add entities
    """
    coordinator: MarstekDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        MarstekOperatingModeSelect(coordinator, entry),
    ]
    
    async_add_entities(entities)


class MarstekOperatingModeSelect(CoordinatorEntity, SelectEntity):
    """Select entity for Marstek Venus E operating mode."""
    
    def __init__(
        self,
        coordinator: MarstekDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the select entity.
        
        Args:
            coordinator: Data update coordinator
            entry: Configuration entry
        """
        super().__init__(coordinator)
        self._attr_name = "Operating Mode"
        self._attr_unique_id = f"{entry.entry_id}_operating_mode"
        self._attr_options = VALID_MODES
        self._attr_icon = "mdi:cog"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Marstek",
            "model": "Venus E",
        }
    
    @property
    def current_option(self) -> str | None:
        """Return the current operating mode."""
        # First try to get mode from mode_data (ES.GetMode response)
        if self.coordinator.mode_data and "mode" in self.coordinator.mode_data:
            mode = self.coordinator.mode_data["mode"]
            if mode in VALID_MODES:
                return mode
        
        # Fallback to main data (mode was copied there in coordinator update)
        if self.coordinator.data and "mode" in self.coordinator.data:
            mode = self.coordinator.data["mode"]
            if mode in VALID_MODES:
                return mode
        
        return None
    
    async def async_select_option(self, option: str) -> None:
        """Change the operating mode.
        
        Args:
            option: New operating mode
        """
        if option not in VALID_MODES:
            _LOGGER.error("Invalid mode: %s", option)
            return
        
        try:
            await self.coordinator.set_mode(option)
            _LOGGER.info("Changed operating mode to: %s", option)
        except Exception as err:
            _LOGGER.error("Failed to set mode to %s: %s", option, err)
            raise
