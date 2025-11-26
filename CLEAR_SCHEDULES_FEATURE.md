# Clear Manual Schedules Feature

## Overview
Added comprehensive functionality to clear all manual schedules through multiple interfaces, making it easy for users to reset their device configuration.

## Features Implemented

### 1. Service Call (For Automations)
**Service:** `marstek_venus_e.clear_all_schedules`

**Usage in automations:**
```yaml
service: marstek_venus_e.clear_all_schedules
```

**Usage in Developer Tools:**
- Go to Developer Tools → Services
- Select `marstek_venus_e.clear_all_schedules`
- Click "Call Service"

### 2. Button Entity (UI Control)
**Entity:** `button.marstek_venus_e_clear_all_schedules`

- Appears automatically in the device page
- Click to clear all 10 time slots (0-9)
- Icon: `mdi:calendar-remove`
- Provides instant feedback in logs

**Dashboard usage:**
```yaml
type: button
entity: button.marstek_venus_e_clear_all_schedules
name: Clear All Schedules
icon: mdi:calendar-remove
tap_action:
  action: call-service
  service: button.press
  target:
    entity_id: button.marstek_venus_e_clear_all_schedules
```

### 3. Setup Flow Option
During initial device configuration:
1. Enter device IP address
2. A new step appears: "Clear Manual Schedules?"
3. Check the box to clear all existing schedules
4. Schedules are cleared before completing setup

This is useful for:
- Fresh installations
- Resetting a device with unknown schedules
- Starting with a clean slate

## Technical Details

### Files Modified/Created:

1. **`udp_client.py`** - Added `clear_all_manual_schedules()` method
   - Loops through slots 0-9
   - Sends disable command for each slot
   - Returns success/failure statistics

2. **`coordinator.py`** - Added coordinator method
   - Wraps client method
   - Refreshes data after clearing

3. **`services.py`** - Added service handler
   - Registers `clear_all_schedules` service
   - Logs success/failure for each device

4. **`services.yaml`** - Added service definition
   - No parameters required
   - Simple one-click operation

5. **`button.py`** (NEW) - Button entity platform
   - Clear schedules button
   - Integrated with device info

6. **`__init__.py`** - Added Button platform
   - Registered in PLATFORMS list

7. **`config_flow.py`** - Added setup step
   - New `async_step_clear_schedules()`
   - Optional checkbox during setup

8. **`strings.json`** - Added translations
   - Config flow strings
   - Service descriptions

### Updated Ranges:
- Time slot range: **0-9** (was 1-4)
- Power range: **100-800W** documented

## How It Works

The clear operation:
1. Loops through all 10 time slots (0-9)
2. For each slot, sends:
   ```json
   {
     "id": X,
     "method": "ES.SetMode",
     "params": {
       "id": 0,
       "config": {
         "mode": "Manual",
         "manual_cfg": {
           "time_num": N,
           "start_time": "00:00",
           "end_time": "23:59",
           "week_set": 127,
           "power": 100,
           "enable": 0
         }
       }
     }
   }
   ```
3. Returns statistics:
   - `success_count`: Number of successfully disabled slots
   - `failed_slots`: List of slots that failed
   - `total_slots`: Always 10

## Testing

Test scripts available:
- `tests/test_es_set_mode.py` - Test individual mode changes and schedules
- `tests/test_clear_all_schedules.py` - Test clearing all schedules

Run tests:
```powershell
# Clear all schedules
python tests/test_clear_all_schedules.py --ip 192.168.0.225

# Set specific schedule
python tests/test_es_set_mode.py --ip 192.168.0.225 --mode Manual --mtimenum 1 --mpower 500

# Disable specific slot
python tests/test_es_set_mode.py --ip 192.168.0.225 --mode Manual --disable --mtimenum 5
```

## User Guide

### Method 1: Use the Button (Easiest)
1. Go to your Marstek Venus E device page in Home Assistant
2. Find "Clear all schedules" button
3. Click it
4. All 10 time slots will be disabled

### Method 2: Use the Service in Automation
```yaml
automation:
  - alias: "Clear schedules at midnight"
    trigger:
      - platform: time
        at: "00:00:00"
    action:
      - service: marstek_venus_e.clear_all_schedules
```

### Method 3: During Initial Setup
1. Add new Marstek Venus E integration
2. Enter IP address
3. Check "Clear all manual schedules"
4. Complete setup

## Logs
Check Home Assistant logs for results:
```
INFO: Cleared manual schedules: 10/10 slots disabled
```

Or if there are failures:
```
INFO: Cleared manual schedules: 8/10 slots disabled
WARNING: Failed to disable slots: [3, 7]
```
