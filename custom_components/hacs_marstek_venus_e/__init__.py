"""The Marstek Venus E integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import MarstekDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SELECT,
    Platform.BUTTON,
]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Marstek Venus E integration.
    
    Args:
        hass: Home Assistant instance
        config: Configuration dictionary
        
    Returns:
        True if setup successful
    """
    # Initialize domain data
    hass.data.setdefault(DOMAIN, {})
    
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Marstek Venus E from a config entry.
    
    Args:
        hass: Home Assistant instance
        entry: Configuration entry
        
    Returns:
        True if setup successful
        
    Raises:
        ConfigEntryNotReady: If device is not ready
    """
    coordinator = MarstekDataUpdateCoordinator(hass, entry)
    
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        raise ConfigEntryNotReady(f"Unable to connect to device: {err}") from err

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    await async_setup_services(hass)

    # Setup reload listener
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry.
    
    Args:
        hass: Home Assistant instance
        entry: Configuration entry
        
    Returns:
        True if unload successful
    """
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown()

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload a config entry.
    
    Args:
        hass: Home Assistant instance
        entry: Configuration entry
    """
    await hass.config_entries.async_reload(entry.entry_id)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for Marstek Venus E.
    
    Args:
        hass: Home Assistant instance
    """
    from .services import async_setup_services as setup_services
    
    await setup_services(hass)
