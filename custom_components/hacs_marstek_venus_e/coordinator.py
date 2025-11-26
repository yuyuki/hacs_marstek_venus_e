"""Data update coordinator for Marstek Venus E."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL, CONF_IP_ADDRESS, CONF_PORT, CONF_SCAN_INTERVAL
from .udp_client import MarstekUDPClient

_LOGGER = logging.getLogger(__name__)


class MarstekDataUpdateCoordinator(DataUpdateCoordinator):
    """Data update coordinator for Marstek Venus E."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator.
        
        Args:
            hass: Home Assistant instance
            entry: Configuration entry
        """
        # Get scan interval from options (in minutes) or use default (in seconds)
        scan_interval_minutes = entry.options.get(CONF_SCAN_INTERVAL)
        if scan_interval_minutes is not None:
            # Convert minutes to seconds
            scan_interval_seconds = scan_interval_minutes * 60
        else:
            # Use default (already in seconds)
            scan_interval_seconds = DEFAULT_SCAN_INTERVAL
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval_seconds),
        )
        
        self.entry = entry
        self.client = MarstekUDPClient(
            ip_address=entry.data[CONF_IP_ADDRESS],
            port=entry.data.get(CONF_PORT, 30000),
        )
        self.data: dict[str, Any] = {}
        # Storage for manual API call results
        self.battery_data: dict[str, Any] = {}
        self.mode_data: dict[str, Any] = {}

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from device.
        
        Returns:
            Dictionary containing device data
            
        Raises:
            UpdateFailed: If data fetch fails
        """
        try:
            # Get energy system status - this includes all key metrics
            data = await self.client.get_energy_system_status()
            return data
        except Exception as err:
            _LOGGER.error("Failed to get device data: %s", err)
            raise UpdateFailed(f"Failed to update data: {err}")

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator."""
        await super().async_shutdown()

    async def set_mode(self, mode: str) -> None:
        """Set operating mode.
        
        Args:
            mode: Operating mode
        """
        await self.client.set_mode(mode)
        await self.async_request_refresh()

    async def set_manual_schedule(
        self,
        time_num: int,
        start_time: str,
        end_time: str,
        week_set: int,
        power: int,
        enable: bool = True,
    ) -> None:
        """Set manual schedule.
        
        Args:
            time_num: Time slot number
            start_time: Start time
            end_time: End time
            week_set: Week bitmask
            power: Power in watts
            enable: Enable schedule
        """
        await self.client.set_manual_schedule(
            time_num=time_num,
            start_time=start_time,
            end_time=end_time,
            week_set=week_set,
            power=power,
            enable=enable,
        )
        await self.async_request_refresh()

    async def set_passive_mode(self, power: int, cd_time: int = 0) -> None:
        """Set passive mode.
        
        Args:
            power: Target power
            cd_time: Countdown time
        """
        await self.client.set_passive_mode(power=power, cd_time=cd_time)
        await self.async_request_refresh()

    async def clear_all_manual_schedules(self) -> dict[str, Any]:
        """Clear all manual schedules.
        
        Returns:
            Dictionary with operation results
        """
        results = await self.client.clear_all_manual_schedules()
        await self.async_request_refresh()
        return results

    async def refresh_battery_data(self) -> dict[str, Any]:
        """Manually refresh battery data.
        
        Returns:
            Battery data dictionary
        """
        self.battery_data = await self.client.get_battery_status()
        self.async_update_listeners()
        return self.battery_data

    async def refresh_mode_data(self) -> dict[str, Any]:
        """Manually refresh mode and CT data.
        
        Returns:
            Mode data dictionary
        """
        self.mode_data = await self.client.get_energy_system_mode()
        self.async_update_listeners()
        return self.mode_data
