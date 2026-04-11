"""Data update coordinator for Marstek Venus E."""
from __future__ import annotations

import logging
from datetime import timedelta, datetime
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
        # Track last battery data update (every 10 minutes instead of 30 seconds)
        self._last_battery_update: datetime | None = None
        self._battery_update_interval = timedelta(minutes=10)

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from device.
        
        Returns:
            Dictionary containing device data
            
        Raises:
            UpdateFailed: If data fetch fails
        """
        try:
            # Get energy system status - this includes all key metrics (every 30 seconds)
            data = await self.client.get_energy_system_status()
            
            # Get battery status every 10 minutes to avoid draining battery with frequent requests
            now = datetime.now()
            if self._last_battery_update is None or (now - self._last_battery_update) >= self._battery_update_interval:
                try:
                    self.battery_data = await self.client.get_battery_status()
                    self._last_battery_update = now
                    _LOGGER.debug("Battery data updated: %s", self.battery_data)
                except Exception as battery_err:
                    _LOGGER.debug("Failed to get battery data: %s", battery_err)
                    # Battery data is optional, don't fail the entire update
            
            # Also get mode data - ES.GetMode returns mode, ongrid_power, offgrid_power, bat_soc, CT data
            # Store in mode_data for sensors that need it
            try:
                self.mode_data = await self.client.get_energy_system_mode()
                # Add mode to main data for easy access
                if "mode" in self.mode_data:
                    data["mode"] = self.mode_data["mode"]
                
                # Add CT meter data to mode_data (ES.GetMode includes it)
                # Apply scaling for energy values (*0.1 as per API documentation)
                if "input_energy" in self.mode_data:
                    self.mode_data["input_energy"] = round(self.mode_data.get("input_energy", 0) * 0.1, 1)
                if "output_energy" in self.mode_data:
                    self.mode_data["output_energy"] = round(self.mode_data.get("output_energy", 0) * 0.1, 1)
            except Exception as mode_err:
                _LOGGER.warning("Failed to get mode data: %s", mode_err)
                # Don't fail the entire update if mode fetch fails
            
            # Also try to get EM status for additional meter data
            try:
                em_data = await self.client.get_energy_meter_status()
                # Merge EM data into mode_data if available
                if em_data:
                    # Apply scaling for EM energy values too
                    if "input_energy" in em_data:
                        em_data["input_energy"] = round(em_data.get("input_energy", 0) * 0.1, 1)
                    if "output_energy" in em_data:
                        em_data["output_energy"] = round(em_data.get("output_energy", 0) * 0.1, 1)
                    
                    # Merge with mode_data
                    # For CT power data (a_power, b_power, c_power, total_power), prefer EM.GetStatus
                    # as ES.GetMode may return zeros if CT is not in active mode
                    if self.mode_data:
                        ct_fields = {"a_power", "b_power", "c_power", "total_power"}
                        for k, v in em_data.items():
                            # Prefer EM data for CT fields, otherwise prefer mode_data
                            if k not in self.mode_data or (k in ct_fields and self.mode_data.get(k) == 0):
                                self.mode_data[k] = v
                    else:
                        self.mode_data = em_data
            except Exception as em_err:
                _LOGGER.debug("Failed to get EM status (expected if not available): %s", em_err)
                # EM.GetStatus is optional and may not be available on all devices
            
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
