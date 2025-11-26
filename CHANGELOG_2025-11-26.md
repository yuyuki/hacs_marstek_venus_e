# Changelog - November 26, 2025

## Changes Summary

### 1. Default Update Interval Changed to 5 Minutes

**Changed Files:**
- `custom_components/hacs_marstek_venus_e/const.py`
- `custom_components/hacs_marstek_venus_e/config_flow.py`

**Details:**
- Changed `DEFAULT_SCAN_INTERVAL` from 5 seconds to 300 seconds (5 minutes)
- This reduces network traffic and device polling frequency
- Users can still customize this interval in the integration options

### 2. New Service: `change_operating_mode`

**Changed Files:**
- `custom_components/hacs_marstek_venus_e/services.yaml`
- `custom_components/hacs_marstek_venus_e/services.py`
- `custom_components/hacs_marstek_venus_e/strings.json`
- `custom_components/hacs_marstek_venus_e/translations/en.json`
- `custom_components/hacs_marstek_venus_e/translations/fr.json`

**Purpose:**
This new service replaces the need for multiple separate operating mode actions in automations. It provides a single action that:
- Changes the operating mode (Auto, AI, Manual, or Passive)
- When Manual mode is selected, allows configuration of all 10 schedule slots

**Features:**
Each of the 10 time slots (0-9) can be configured with:
- **Enable/Disable**: Toggle whether the slot is active
- **Start Time**: When the schedule begins (HH:MM format)
- **End Time**: When the schedule ends (HH:MM format)
- **Power**: Power magnitude (100-800W)
- **Mode**: Charging or Discharging
- **Days**: Week bitmask (1=Mon, 2=Tue, 4=Wed, 8=Thu, 16=Fri, 32=Sat, 64=Sun, 127=All days)

**How It Works:**
1. The service first changes the operating mode
2. If Manual mode is selected:
   - For each enabled slot (where `slot_X_enable` is true), it configures the schedule
   - For each disabled slot, it explicitly disables that time slot
3. If a different mode is selected (Auto, AI, Passive), it only changes the mode

**Usage in Automations:**
When creating an automation in Home Assistant:
1. Choose action: "Marstek Venus E: Change Operating Mode"
2. Select the desired mode
3. If "Manual" is selected, you'll see all 10 slot configurations
4. Enable and configure the slots you want to use

**Example Automation YAML:**
```yaml
service: hacs_marstek_venus_e.change_operating_mode
data:
  mode: Manual
  slot_0_enable: true
  slot_0_start_time: "23:00"
  slot_0_end_time: "07:00"
  slot_0_power: 500
  slot_0_mode: Charging
  slot_0_days: 127  # All days
  slot_1_enable: true
  slot_1_start_time: "16:00"
  slot_1_end_time: "20:00"
  slot_1_power: 300
  slot_1_mode: Discharging
  slot_1_days: 31  # Weekdays only (Mon-Fri)
  # Other slots remain disabled by default
```

### 3. Automation Dropdown Simplification

The new `change_operating_mode` service consolidates all mode-changing actions into one. In the automation UI:
- **Old**: Multiple "Change Operating Mode to..." options
- **New**: Single "Change Operating Mode" option with all configuration in one place

This makes automation setup cleaner and more intuitive, especially for Manual mode which requires schedule configuration.

## Benefits

1. **Reduced Network Traffic**: 5-minute update interval by default (was 5 seconds)
2. **Simplified Automation Setup**: Single action for mode changes with integrated schedule configuration
3. **Complete Manual Mode Control**: All 10 slots configurable directly in automations
4. **Better User Experience**: Cleaner dropdown menu with fewer confusing options
5. **Atomic Operations**: Mode change and schedule configuration happen together, preventing inconsistent states

## Migration Notes

- Existing automations using separate mode change services will continue to work
- The new `change_operating_mode` service is recommended for new automations
- Update interval change takes effect on integration reload or Home Assistant restart
- Existing custom update intervals in options are preserved

## Technical Details

**Week Bitmask Reference:**
- Monday: 1
- Tuesday: 2
- Wednesday: 4
- Thursday: 8
- Friday: 16
- Saturday: 32
- Sunday: 64
- All days: 127 (sum of all)
- Weekdays: 31 (Mon-Fri)
- Weekend: 96 (Sat-Sun)

**Power Values:**
- Positive values = Discharging (battery to home/grid)
- Negative values = Charging (grid/PV to battery)
- Range: 100W to 800W (magnitude)

**Days Calculation Examples:**
- Monday only: 1
- Monday + Tuesday: 3 (1+2)
- Monday + Wednesday + Friday: 21 (1+4+16)
- All days: 127
