"""Binary sensors for Marstek Venus E integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN, BINARY_SENSORS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensor platform.
    
    Args:
        hass: Home Assistant instance
        entry: Configuration entry
        async_add_entities: Callback to add entities
    """
    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[MarstekBinarySensor] = []
    
    for sensor_id, sensor_config in BINARY_SENSORS.items():
        entities.append(
            MarstekBinarySensor(
                coordinator=coordinator,
                entry_id=entry.entry_id,
                sensor_id=sensor_id,
                sensor_config=sensor_config,
            )
        )

    async_add_entities(entities)


class MarstekBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Marstek Venus E binary sensor entity."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry_id: str,
        sensor_id: str,
        sensor_config: dict[str, Any],
    ) -> None:
        """Initialize the binary sensor.
        
        Args:
            coordinator: Data update coordinator
            entry_id: Configuration entry ID
            sensor_id: Sensor identifier
            sensor_config: Sensor configuration dictionary
        """
        super().__init__(coordinator)
        
        self.coordinator = coordinator
        self.entry_id = entry_id
        self.sensor_id = sensor_id
        self.sensor_config = sensor_config
        
        self._attr_name = sensor_config["name"]
        self._attr_icon = sensor_config.get("icon")
        self._attr_device_class = sensor_config.get("device_class")
        
        # Create unique ID
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_{sensor_id}"
        
        # Device info for grouping
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": f"Marstek Venus E",
            "manufacturer": "Marstek",
            "model": "Venus E",
        }

    @property
    def is_on(self) -> bool | None:
        """Return the binary sensor state.
        
        Returns:
            True if sensor is on, False if off, None if unavailable
        """
        attr_path = self.sensor_config.get("attr")
        source = self.sensor_config.get("source", "auto")
        
        # Check appropriate data source based on sensor configuration
        if source == "battery" and self.coordinator.battery_data:
            # From Bat.GetStatus (manual refresh)
            if attr_path in self.coordinator.battery_data:
                value = self.coordinator.battery_data[attr_path]
                return bool(value)
        elif source == "mode" and self.coordinator.mode_data:
            # From ES.GetMode (manual refresh)
            if attr_path in self.coordinator.mode_data:
                value = self.coordinator.mode_data[attr_path]
                return bool(value)
        elif source == "auto" and self.coordinator.data:
            # From ES.GetStatus (automatic updates)
            if attr_path in self.coordinator.data:
                value = self.coordinator.data[attr_path]
                return bool(value)
        
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available.
        
        Returns:
            True if data is available
        """
        return self.coordinator.last_update_success

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
