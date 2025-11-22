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
        vol.Required("time_num"): vol.All(vol.Coerce(int), vol.Range(min=1, max=4)),
        vol.Required("start_time"): cv.time,
        vol.Required("end_time"): cv.time,
        vol.Required("week_set"): vol.All(vol.Coerce(int), vol.Range(min=1, max=127)),
        vol.Required("power"): vol.Coerce(int),
        vol.Optional("enable", default=True): cv.boolean,
    }
)

SERVICE_SET_PASSIVE_MODE_SCHEMA = vol.Schema(
    {
        vol.Required("power"): vol.Coerce(int),
        vol.Optional("cd_time", default=0): vol.All(vol.Coerce(int), vol.Range(min=0)),
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
        power = call.data.get("power")
        enable = call.data.get("enable", True)
        
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
                    "Set manual schedule: time_num=%s, start=%s, end=%s, power=%s",
                    time_num,
                    start_time,
                    end_time,
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

    _LOGGER.debug("Services registered for %s", DOMAIN)
