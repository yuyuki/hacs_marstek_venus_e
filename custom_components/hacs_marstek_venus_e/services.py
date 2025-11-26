"""Service handlers for Marstek Venus E integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    API_SET_MODE,
    API_SET_MANUAL_SCHEDULE,
    API_SET_PASSIVE_MODE,
    VALID_MODES,
)

_LOGGER = logging.getLogger(__name__)

# Service schemas
SERVICE_SET_MODE_SCHEMA = vol.Schema(
    {
        vol.Required("mode"): vol.In(VALID_MODES),
    }
)

SERVICE_SET_MANUAL_SCHEDULE_SCHEMA = vol.Schema(
    {
        vol.Required("time_num"): vol.All(vol.Coerce(int), vol.Range(min=0, max=9)),
        vol.Required("start_time"): cv.time,
        vol.Required("end_time"): cv.time,  # Note: end_time must be > start_time (validated by device)
        vol.Required("week_set"): vol.All(vol.Coerce(int), vol.Range(min=1, max=127)),
        vol.Required("mode"): vol.In(["Charging", "Discharging"]),  # Charging or Discharging
        vol.Required("power"): vol.All(vol.Coerce(int), vol.Range(min=100, max=800)),  # Power magnitude (always positive)
        vol.Optional("enable", default=True): cv.boolean,
    }
)

SERVICE_SET_PASSIVE_MODE_SCHEMA = vol.Schema(
    {
        vol.Required("power"): vol.Coerce(int),
        vol.Optional("cd_time", default=0): vol.All(vol.Coerce(int), vol.Range(min=0)),
    }
)

# Schema for change_operating_mode service (mode change + optional manual schedules)
SERVICE_CHANGE_OPERATING_MODE_SCHEMA = vol.Schema(
    {
        vol.Required("mode"): vol.In(VALID_MODES),
        # Slot 0
        vol.Optional("slot_0_enable", default=False): cv.boolean,
        vol.Optional("slot_0_start_time"): cv.time,
        vol.Optional("slot_0_end_time"): cv.time,
        vol.Optional("slot_0_power", default=100): vol.All(vol.Coerce(int), vol.Range(min=100, max=800)),
        vol.Optional("slot_0_mode", default="Discharging"): vol.In(["Charging", "Discharging"]),
        vol.Optional("slot_0_days", default=127): vol.All(vol.Coerce(int), vol.Range(min=1, max=127)),
        # Slot 1
        vol.Optional("slot_1_enable", default=False): cv.boolean,
        vol.Optional("slot_1_start_time"): cv.time,
        vol.Optional("slot_1_end_time"): cv.time,
        vol.Optional("slot_1_power", default=100): vol.All(vol.Coerce(int), vol.Range(min=100, max=800)),
        vol.Optional("slot_1_mode", default="Discharging"): vol.In(["Charging", "Discharging"]),
        vol.Optional("slot_1_days", default=127): vol.All(vol.Coerce(int), vol.Range(min=1, max=127)),
        # Slot 2
        vol.Optional("slot_2_enable", default=False): cv.boolean,
        vol.Optional("slot_2_start_time"): cv.time,
        vol.Optional("slot_2_end_time"): cv.time,
        vol.Optional("slot_2_power", default=100): vol.All(vol.Coerce(int), vol.Range(min=100, max=800)),
        vol.Optional("slot_2_mode", default="Discharging"): vol.In(["Charging", "Discharging"]),
        vol.Optional("slot_2_days", default=127): vol.All(vol.Coerce(int), vol.Range(min=1, max=127)),
        # Slot 3
        vol.Optional("slot_3_enable", default=False): cv.boolean,
        vol.Optional("slot_3_start_time"): cv.time,
        vol.Optional("slot_3_end_time"): cv.time,
        vol.Optional("slot_3_power", default=100): vol.All(vol.Coerce(int), vol.Range(min=100, max=800)),
        vol.Optional("slot_3_mode", default="Discharging"): vol.In(["Charging", "Discharging"]),
        vol.Optional("slot_3_days", default=127): vol.All(vol.Coerce(int), vol.Range(min=1, max=127)),
        # Slot 4
        vol.Optional("slot_4_enable", default=False): cv.boolean,
        vol.Optional("slot_4_start_time"): cv.time,
        vol.Optional("slot_4_end_time"): cv.time,
        vol.Optional("slot_4_power", default=100): vol.All(vol.Coerce(int), vol.Range(min=100, max=800)),
        vol.Optional("slot_4_mode", default="Discharging"): vol.In(["Charging", "Discharging"]),
        vol.Optional("slot_4_days", default=127): vol.All(vol.Coerce(int), vol.Range(min=1, max=127)),
        # Slot 5
        vol.Optional("slot_5_enable", default=False): cv.boolean,
        vol.Optional("slot_5_start_time"): cv.time,
        vol.Optional("slot_5_end_time"): cv.time,
        vol.Optional("slot_5_power", default=100): vol.All(vol.Coerce(int), vol.Range(min=100, max=800)),
        vol.Optional("slot_5_mode", default="Discharging"): vol.In(["Charging", "Discharging"]),
        vol.Optional("slot_5_days", default=127): vol.All(vol.Coerce(int), vol.Range(min=1, max=127)),
        # Slot 6
        vol.Optional("slot_6_enable", default=False): cv.boolean,
        vol.Optional("slot_6_start_time"): cv.time,
        vol.Optional("slot_6_end_time"): cv.time,
        vol.Optional("slot_6_power", default=100): vol.All(vol.Coerce(int), vol.Range(min=100, max=800)),
        vol.Optional("slot_6_mode", default="Discharging"): vol.In(["Charging", "Discharging"]),
        vol.Optional("slot_6_days", default=127): vol.All(vol.Coerce(int), vol.Range(min=1, max=127)),
        # Slot 7
        vol.Optional("slot_7_enable", default=False): cv.boolean,
        vol.Optional("slot_7_start_time"): cv.time,
        vol.Optional("slot_7_end_time"): cv.time,
        vol.Optional("slot_7_power", default=100): vol.All(vol.Coerce(int), vol.Range(min=100, max=800)),
        vol.Optional("slot_7_mode", default="Discharging"): vol.In(["Charging", "Discharging"]),
        vol.Optional("slot_7_days", default=127): vol.All(vol.Coerce(int), vol.Range(min=1, max=127)),
        # Slot 8
        vol.Optional("slot_8_enable", default=False): cv.boolean,
        vol.Optional("slot_8_start_time"): cv.time,
        vol.Optional("slot_8_end_time"): cv.time,
        vol.Optional("slot_8_power", default=100): vol.All(vol.Coerce(int), vol.Range(min=100, max=800)),
        vol.Optional("slot_8_mode", default="Discharging"): vol.In(["Charging", "Discharging"]),
        vol.Optional("slot_8_days", default=127): vol.All(vol.Coerce(int), vol.Range(min=1, max=127)),
        # Slot 9
        vol.Optional("slot_9_enable", default=False): cv.boolean,
        vol.Optional("slot_9_start_time"): cv.time,
        vol.Optional("slot_9_end_time"): cv.time,
        vol.Optional("slot_9_power", default=100): vol.All(vol.Coerce(int), vol.Range(min=100, max=800)),
        vol.Optional("slot_9_mode", default="Discharging"): vol.In(["Charging", "Discharging"]),
        vol.Optional("slot_9_days", default=127): vol.All(vol.Coerce(int), vol.Range(min=1, max=127)),
    }
)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for Marstek Venus E.
    
    Args:
        hass: Home Assistant instance
    """

    async def set_mode_handler(call: ServiceCall) -> None:
        """Handle set_mode service call.
        
        Args:
            call: Service call object
        """
        mode = call.data.get("mode")
        
        for entry_id, coordinator in hass.data[DOMAIN].items():
            try:
                await coordinator.set_mode(mode)
                _LOGGER.info("Set mode to %s", mode)
            except Exception as err:
                _LOGGER.error("Error setting mode: %s", err)

    async def set_manual_schedule_handler(call: ServiceCall) -> None:
        """Handle set_manual_schedule service call.
        
        Args:
            call: Service call object
        """
        time_num = call.data.get("time_num")
        start_time = call.data.get("start_time").strftime("%H:%M")
        end_time = call.data.get("end_time").strftime("%H:%M")
        week_set = call.data.get("week_set")
        mode = call.data.get("mode")
        power_magnitude = call.data.get("power")
        enable = call.data.get("enable", True)
        
        # Convert power based on mode: Charging = negative, Discharging = positive
        power = -power_magnitude if mode == "Charging" else power_magnitude
        
        for entry_id, coordinator in hass.data[DOMAIN].items():
            try:
                await coordinator.set_manual_schedule(
                    time_num=time_num,
                    start_time=start_time,
                    end_time=end_time,
                    week_set=week_set,
                    power=power,
                    enable=enable,
                )
                _LOGGER.info(
                    "Set manual schedule: time_num=%s, start=%s, end=%s, mode=%s, power=%s",
                    time_num,
                    start_time,
                    end_time,
                    mode,
                    power,
                )
            except Exception as err:
                _LOGGER.error("Error setting manual schedule: %s", err)

    async def set_passive_mode_handler(call: ServiceCall) -> None:
        """Handle set_passive_mode service call.
        
        Args:
            call: Service call object
        """
        power = call.data.get("power")
        cd_time = call.data.get("cd_time", 0)
        
        for entry_id, coordinator in hass.data[DOMAIN].items():
            try:
                await coordinator.set_passive_mode(power=power, cd_time=cd_time)
                _LOGGER.info("Set passive mode: power=%s, cd_time=%s", power, cd_time)
            except Exception as err:
                _LOGGER.error("Error setting passive mode: %s", err)

    # Register services
    hass.services.async_register(
        DOMAIN,
        "set_mode",
        set_mode_handler,
        schema=SERVICE_SET_MODE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        "set_manual_schedule",
        set_manual_schedule_handler,
        schema=SERVICE_SET_MANUAL_SCHEDULE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        "set_passive_mode",
        set_passive_mode_handler,
        schema=SERVICE_SET_PASSIVE_MODE_SCHEMA,
    )

    async def clear_all_schedules_handler(call: ServiceCall) -> None:
        """Handle clear_all_schedules service call.
        
        Args:
            call: Service call object
        """
        for entry_id, coordinator in hass.data[DOMAIN].items():
            try:
                results = await coordinator.clear_all_manual_schedules()
                _LOGGER.info(
                    "Cleared manual schedules: %d/%d slots disabled",
                    results["success_count"],
                    results["total_slots"],
                )
                if results["failed_slots"]:
                    _LOGGER.warning("Failed to disable slots: %s", results["failed_slots"])
            except Exception as err:
                _LOGGER.error("Error clearing manual schedules: %s", err)

    hass.services.async_register(
        DOMAIN,
        "clear_all_schedules",
        clear_all_schedules_handler,
    )

    async def change_operating_mode_handler(call: ServiceCall) -> None:
        """Handle change_operating_mode service call.
        
        This service changes the operating mode and optionally configures manual schedules.
        
        Args:
            call: Service call object
        """
        mode = call.data.get("mode")
        
        for entry_id, coordinator in hass.data[DOMAIN].items():
            try:
                # First, set the operating mode
                await coordinator.set_mode(mode)
                _LOGGER.info("Changed operating mode to %s", mode)
                
                # If Manual mode is selected, configure schedules for enabled slots
                if mode == "Manual":
                    for slot_num in range(10):
                        enable_key = f"slot_{slot_num}_enable"
                        
                        if call.data.get(enable_key, False):
                            # This slot is enabled, configure it
                            start_time_key = f"slot_{slot_num}_start_time"
                            end_time_key = f"slot_{slot_num}_end_time"
                            power_key = f"slot_{slot_num}_power"
                            mode_key = f"slot_{slot_num}_mode"
                            days_key = f"slot_{slot_num}_days"
                            
                            start_time = call.data.get(start_time_key)
                            end_time = call.data.get(end_time_key)
                            power_magnitude = call.data.get(power_key, 100)
                            slot_mode = call.data.get(mode_key, "Discharging")
                            week_set = call.data.get(days_key, 127)
                            
                            if start_time and end_time:
                                # Convert datetime.time to string format
                                start_time_str = start_time.strftime("%H:%M")
                                end_time_str = end_time.strftime("%H:%M")
                                
                                # Convert power based on mode
                                power = -power_magnitude if slot_mode == "Charging" else power_magnitude
                                
                                await coordinator.set_manual_schedule(
                                    time_num=slot_num,
                                    start_time=start_time_str,
                                    end_time=end_time_str,
                                    week_set=week_set,
                                    power=power,
                                    enable=True,
                                )
                                
                                _LOGGER.info(
                                    "Configured slot %d: %s-%s, %s, %dW, days=%d",
                                    slot_num,
                                    start_time_str,
                                    end_time_str,
                                    slot_mode,
                                    power,
                                    week_set,
                                )
                            else:
                                _LOGGER.warning(
                                    "Slot %d is enabled but missing start_time or end_time",
                                    slot_num,
                                )
                        else:
                            # Slot is disabled, explicitly disable it
                            await coordinator.set_manual_schedule(
                                time_num=slot_num,
                                start_time="00:00",
                                end_time="00:01",
                                week_set=127,
                                power=100,
                                enable=False,
                            )
                            _LOGGER.debug("Disabled slot %d", slot_num)
                
            except Exception as err:
                _LOGGER.error("Error in change_operating_mode: %s", err)
                raise

    hass.services.async_register(
        DOMAIN,
        "change_operating_mode",
        change_operating_mode_handler,
        schema=SERVICE_CHANGE_OPERATING_MODE_SCHEMA,
    )

    _LOGGER.debug("Services registered for %s", DOMAIN)
