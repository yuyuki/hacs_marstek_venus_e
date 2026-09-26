"""Service handlers for Marstek Venus E integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .const import (
    DOMAIN,
    API_SET_MODE,
    API_SET_MANUAL_SCHEDULE,
    API_SET_PASSIVE_MODE,
    VALID_MODES,
)

_LOGGER = logging.getLogger(__name__)

TARGET_FIELDS = {
    vol.Optional("entity_id"): vol.All(cv.ensure_list, [cv.string]),
    vol.Optional("device_id"): vol.All(cv.ensure_list, [cv.string]),
    vol.Optional("area_id"): vol.All(cv.ensure_list, [cv.string]),
}


def _target_coordinators(hass: HomeAssistant, data: dict) -> dict:
    """Resolve explicit HA targets to this integration's config entries."""
    coordinators = hass.data.get(DOMAIN, {})
    if not any(key in data for key in ("entity_id", "device_id", "area_id")):
        return dict(coordinators)

    entities = er.async_get(hass)
    devices = dr.async_get(hass)
    entry_ids = set()
    for entity_id in data.get("entity_id", []):
        if (entity := entities.async_get(entity_id)) is not None:
            if entity.config_entry_id:
                entry_ids.add(entity.config_entry_id)
    for device_id in data.get("device_id", []):
        if (device := devices.async_get(device_id)) is not None:
            entry_ids.update(device.config_entries)
    for area_id in data.get("area_id", []):
        for entity in entities.entities.values():
            if entity.area_id == area_id and entity.config_entry_id:
                entry_ids.add(entity.config_entry_id)
        for device in dr.async_entries_for_area(devices, area_id):
            entry_ids.update(device.config_entries)

    selected = {key: value for key, value in coordinators.items() if key in entry_ids}
    if not selected:
        raise ValueError("No Marstek Venus E battery matches the selected target")
    return selected


async def _execute_targeted(hass: HomeAssistant, call: ServiceCall, operation) -> dict | None:
    """Report each device result and fail normal service calls on errors."""
    results = {}
    selected = _target_coordinators(hass, call.data)
    if not selected:
        raise ValueError("No configured Marstek Venus E batteries are available")
    for entry_id, coordinator in selected.items():
        try:
            await operation(coordinator)
            results[entry_id] = {"ok": True}
        except Exception as err:
            _LOGGER.warning("Command failed for battery %s: %s", entry_id, err)
            results[entry_id] = {"ok": False, "error": str(err)}
    if not call.return_response and any(not result["ok"] for result in results.values()):
        raise ValueError(f"Marstek command failed: {results}")
    return {"results": results} if call.return_response else None

# Service schemas
SERVICE_SET_MODE_SCHEMA = vol.Schema(
    {
        vol.Required("mode"): vol.In(VALID_MODES),
        **TARGET_FIELDS,
    }
)

SERVICE_SET_MANUAL_SCHEDULE_SCHEMA = vol.Schema(
    {
        vol.Required("time_num"): vol.All(vol.Coerce(int), vol.Range(min=0, max=9)),
        vol.Required("start_time"): cv.time,
        vol.Required("end_time"): cv.time,  # Note: end_time must be > start_time (validated by device)
        vol.Required("week_set"): vol.All(vol.Coerce(int), vol.Range(min=1, max=127)),
        vol.Required("mode"): vol.In(["Charging", "Discharging"]),  # Charging or Discharging
        vol.Required("power"): vol.All(vol.Coerce(int), vol.Range(min=0, max=2500)),
        vol.Optional("enable", default=True): cv.boolean,
        **TARGET_FIELDS,
    }
)

SERVICE_SET_PASSIVE_MODE_SCHEMA = vol.Schema(
    {
        vol.Required("power"): vol.All(vol.Coerce(int), vol.Range(min=-2500, max=2500)),
        vol.Optional("cd_time", default=0): vol.All(vol.Coerce(int), vol.Range(min=0, max=86400)),
        **TARGET_FIELDS,
    }
)

# Schema for set_ble_adv service
SERVICE_SET_BLE_ADV_SCHEMA = vol.Schema(
    {
        vol.Required("enable"): cv.boolean,
        **TARGET_FIELDS,
    }
)

# Schema for set_led_ctrl service
SERVICE_SET_LED_CTRL_SCHEMA = vol.Schema(
    {
        vol.Required("enabled"): cv.boolean,
        **TARGET_FIELDS,
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
        vol.Optional("slot_0_power", default=100): vol.All(vol.Coerce(int), vol.Range(min=0, max=2500)),
        vol.Optional("slot_0_mode", default="Discharging"): vol.In(["Charging", "Discharging"]),
        vol.Optional("slot_0_days", default=127): vol.All(vol.Coerce(int), vol.Range(min=1, max=127)),
        # Slot 1
        vol.Optional("slot_1_enable", default=False): cv.boolean,
        vol.Optional("slot_1_start_time"): cv.time,
        vol.Optional("slot_1_end_time"): cv.time,
        vol.Optional("slot_1_power", default=100): vol.All(vol.Coerce(int), vol.Range(min=0, max=2500)),
        vol.Optional("slot_1_mode", default="Discharging"): vol.In(["Charging", "Discharging"]),
        vol.Optional("slot_1_days", default=127): vol.All(vol.Coerce(int), vol.Range(min=1, max=127)),
        # Slot 2
        vol.Optional("slot_2_enable", default=False): cv.boolean,
        vol.Optional("slot_2_start_time"): cv.time,
        vol.Optional("slot_2_end_time"): cv.time,
        vol.Optional("slot_2_power", default=100): vol.All(vol.Coerce(int), vol.Range(min=0, max=2500)),
        vol.Optional("slot_2_mode", default="Discharging"): vol.In(["Charging", "Discharging"]),
        vol.Optional("slot_2_days", default=127): vol.All(vol.Coerce(int), vol.Range(min=1, max=127)),
        # Slot 3
        vol.Optional("slot_3_enable", default=False): cv.boolean,
        vol.Optional("slot_3_start_time"): cv.time,
        vol.Optional("slot_3_end_time"): cv.time,
        vol.Optional("slot_3_power", default=100): vol.All(vol.Coerce(int), vol.Range(min=0, max=2500)),
        vol.Optional("slot_3_mode", default="Discharging"): vol.In(["Charging", "Discharging"]),
        vol.Optional("slot_3_days", default=127): vol.All(vol.Coerce(int), vol.Range(min=1, max=127)),
        # Slot 4
        vol.Optional("slot_4_enable", default=False): cv.boolean,
        vol.Optional("slot_4_start_time"): cv.time,
        vol.Optional("slot_4_end_time"): cv.time,
        vol.Optional("slot_4_power", default=100): vol.All(vol.Coerce(int), vol.Range(min=0, max=2500)),
        vol.Optional("slot_4_mode", default="Discharging"): vol.In(["Charging", "Discharging"]),
        vol.Optional("slot_4_days", default=127): vol.All(vol.Coerce(int), vol.Range(min=1, max=127)),
        # Slot 5
        vol.Optional("slot_5_enable", default=False): cv.boolean,
        vol.Optional("slot_5_start_time"): cv.time,
        vol.Optional("slot_5_end_time"): cv.time,
        vol.Optional("slot_5_power", default=100): vol.All(vol.Coerce(int), vol.Range(min=0, max=2500)),
        vol.Optional("slot_5_mode", default="Discharging"): vol.In(["Charging", "Discharging"]),
        vol.Optional("slot_5_days", default=127): vol.All(vol.Coerce(int), vol.Range(min=1, max=127)),
        # Slot 6
        vol.Optional("slot_6_enable", default=False): cv.boolean,
        vol.Optional("slot_6_start_time"): cv.time,
        vol.Optional("slot_6_end_time"): cv.time,
        vol.Optional("slot_6_power", default=100): vol.All(vol.Coerce(int), vol.Range(min=0, max=2500)),
        vol.Optional("slot_6_mode", default="Discharging"): vol.In(["Charging", "Discharging"]),
        vol.Optional("slot_6_days", default=127): vol.All(vol.Coerce(int), vol.Range(min=1, max=127)),
        # Slot 7
        vol.Optional("slot_7_enable", default=False): cv.boolean,
        vol.Optional("slot_7_start_time"): cv.time,
        vol.Optional("slot_7_end_time"): cv.time,
        vol.Optional("slot_7_power", default=100): vol.All(vol.Coerce(int), vol.Range(min=0, max=2500)),
        vol.Optional("slot_7_mode", default="Discharging"): vol.In(["Charging", "Discharging"]),
        vol.Optional("slot_7_days", default=127): vol.All(vol.Coerce(int), vol.Range(min=1, max=127)),
        # Slot 8
        vol.Optional("slot_8_enable", default=False): cv.boolean,
        vol.Optional("slot_8_start_time"): cv.time,
        vol.Optional("slot_8_end_time"): cv.time,
        vol.Optional("slot_8_power", default=100): vol.All(vol.Coerce(int), vol.Range(min=0, max=2500)),
        vol.Optional("slot_8_mode", default="Discharging"): vol.In(["Charging", "Discharging"]),
        vol.Optional("slot_8_days", default=127): vol.All(vol.Coerce(int), vol.Range(min=1, max=127)),
        # Slot 9
        vol.Optional("slot_9_enable", default=False): cv.boolean,
        vol.Optional("slot_9_start_time"): cv.time,
        vol.Optional("slot_9_end_time"): cv.time,
        vol.Optional("slot_9_power", default=100): vol.All(vol.Coerce(int), vol.Range(min=0, max=2500)),
        vol.Optional("slot_9_mode", default="Discharging"): vol.In(["Charging", "Discharging"]),
        vol.Optional("slot_9_days", default=127): vol.All(vol.Coerce(int), vol.Range(min=1, max=127)),
        **TARGET_FIELDS,
    }
)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for Marstek Venus E.
    
    Args:
        hass: Home Assistant instance
    """

    async def set_mode_handler(call: ServiceCall) -> dict | None:
        """Handle set_mode service call.
        
        Args:
            call: Service call object
        """
        mode = call.data.get("mode")
        
        return await _execute_targeted(hass, call, lambda coordinator: coordinator.set_mode(mode))

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
        
        async def apply(coordinator):
            await coordinator.set_manual_schedule(
                    time_num=time_num,
                    start_time=start_time,
                    end_time=end_time,
                    week_set=week_set,
                    power=power,
                    enable=enable,
            )

        await _execute_targeted(hass, call, apply)

    async def set_passive_mode_handler(call: ServiceCall) -> dict | None:
        """Handle set_passive_mode service call.
        
        Args:
            call: Service call object
        """
        power = call.data.get("power")
        cd_time = call.data.get("cd_time", 0)
        
        return await _execute_targeted(
            hass, call,
            lambda coordinator: coordinator.set_passive_mode(power=power, cd_time=cd_time),
        )

    # Register services
    hass.services.async_register(
        DOMAIN,
        "set_mode",
        set_mode_handler,
        schema=SERVICE_SET_MODE_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
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
        supports_response=SupportsResponse.OPTIONAL,
    )

    async def clear_all_schedules_handler(call: ServiceCall) -> None:
        """Handle clear_all_schedules service call.
        
        Args:
            call: Service call object
        """
        async def apply(coordinator):
            results = await coordinator.clear_all_manual_schedules()
            if results["failed_slots"]:
                raise ValueError(f"Failed to disable slots: {results['failed_slots']}")

        await _execute_targeted(hass, call, apply)

    hass.services.async_register(
        DOMAIN,
        "clear_all_schedules",
        clear_all_schedules_handler,
        schema=vol.Schema(TARGET_FIELDS),
    )

    async def set_ble_adv_handler(call: ServiceCall) -> None:
        """Handle set_ble_adv service call.
        
        Args:
            call: Service call object
        """
        enable = call.data.get("enable")
        
        await _execute_targeted(hass, call, lambda coordinator: coordinator.client.set_ble_adv(enable))

    hass.services.async_register(
        DOMAIN,
        "set_ble_adv",
        set_ble_adv_handler,
        schema=SERVICE_SET_BLE_ADV_SCHEMA,
    )

    async def set_led_ctrl_handler(call: ServiceCall) -> None:
        """Handle set_led_ctrl service call.
        
        Args:
            call: Service call object
        """
        enabled = call.data.get("enabled")
        
        await _execute_targeted(hass, call, lambda coordinator: coordinator.client.set_led_ctrl(enabled))

    hass.services.async_register(
        DOMAIN,
        "set_led_ctrl",
        set_led_ctrl_handler,
        schema=SERVICE_SET_LED_CTRL_SCHEMA,
    )

    async def change_operating_mode_handler(call: ServiceCall) -> None:
        """Handle change_operating_mode service call.
        
        This service changes the operating mode and optionally configures manual schedules.
        
        Args:
            call: Service call object
        """
        mode = call.data.get("mode")
        
        selected = _target_coordinators(hass, call.data)
        if not selected:
            raise ValueError("No configured Marstek Venus E batteries are available")
        for entry_id, coordinator in selected.items():
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
