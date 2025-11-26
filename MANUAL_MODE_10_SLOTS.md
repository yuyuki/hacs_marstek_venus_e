# Manual Mode - 10 Schedule Slots Support

## Overview

The Marstek Venus E integration now supports configuring up to **10 schedule slots (0-9)** for Manual mode, instead of the previous 4 slots (1-4).

## Changes Made

### 1. Config Flow (`config_flow.py`)

Updated the `configure_manual_mode` step to allow selecting slots 0-9:

```python
vol.Required("time_slot", default=0): selector.NumberSelector(
    selector.NumberSelectorConfig(
        min=0,
        max=9,
        step=1,
        mode=selector.NumberSelectorMode.SLIDER,
    )
)
```

### 2. Translation Files

Updated all translation files to reflect the new slot range:

#### `strings.json`, `translations/en.json`
- Changed "Time Slot (1-4)" → "Time Slot (0-9)"
- Changed "up to 4 different schedules" → "up to 10 different schedules"

#### `translations/fr.json`
- Changed "Plage Horaire (1-4)" → "Plage Horaire (0-9)"
- Changed "jusqu'à 4 plannings différents" → "jusqu'à 10 plannings différents"

## How to Use

### Via Home Assistant UI

1. Go to **Settings** → **Devices & Services**
2. Find your **Marstek Venus E** integration
3. Click **Configure**
4. Select **Configure Manual Mode Schedule**
5. Choose a time slot from **0 to 9** using the slider
6. Set the following parameters:
   - **Start Time**: When the schedule begins (HH:MM)
   - **End Time**: When the schedule ends (HH:MM)
   - **Active Days**: Select which days of the week (multi-select)
   - **Power (W)**: 
     - **Negative** values for charging (e.g., -1000W = charge at 1000W)
     - **Positive** values for discharging (e.g., 1000W = discharge at 1000W)
   - **Enable**: Check to activate this schedule

### Via Home Assistant Services

You can also configure schedules using the `hacs_marstek_venus_e.set_manual_schedule` service:

```yaml
service: hacs_marstek_venus_e.set_manual_schedule
data:
  time_num: 5  # Slot 0-9
  start_time: "08:00"
  end_time: "16:00"
  week_set: 31  # Monday-Friday (1+2+4+8+16)
  power: -2000  # Charge at 2000W
  enable: true
```

### Week Set Bitmask

For the `week_set` parameter (in services):
- 1 = Monday
- 2 = Tuesday
- 4 = Wednesday
- 8 = Thursday
- 16 = Friday
- 32 = Saturday
- 64 = Sunday
- 127 = All days
- 31 = Weekdays (Mon-Fri)
- 96 = Weekends (Sat-Sun)

## Example Automation

Here's an example automation using Home Assistant to configure a schedule when you select Manual mode:

```yaml
automation:
  - alias: "Configure Battery Schedule on Manual Mode"
    trigger:
      - platform: state
        entity_id: select.marstek_venus_e_operating_mode
        to: "Manual"
    action:
      # Slot 0: Charge during off-peak hours (night)
      - service: hacs_marstek_venus_e.set_manual_schedule
        data:
          time_num: 0
          start_time: "01:00"
          end_time: "07:00"
          week_set: 127  # All days
          power: -3000  # Charge at 3000W
          enable: true
      
      # Slot 1: Discharge during peak hours (morning)
      - service: hacs_marstek_venus_e.set_manual_schedule
        data:
          time_num: 1
          start_time: "07:00"
          end_time: "09:00"
          week_set: 31  # Weekdays only
          power: 2000  # Discharge at 2000W
          enable: true
      
      # Slot 2: Discharge during peak hours (evening)
      - service: hacs_marstek_venus_e.set_manual_schedule
        data:
          time_num: 2
          start_time: "18:00"
          end_time: "22:00"
          week_set: 127  # All days
          power: 2500  # Discharge at 2500W
          enable: true
```

## Clearing All Schedules

You can clear all 10 schedule slots at once:

### Via UI
1. Press the **Clear all schedules** button entity

### Via Service
```yaml
service: hacs_marstek_venus_e.clear_all_schedules
```

This will disable all slots (0-9) by setting `enable: false` for each slot.

## Technical Details

- **API Method**: `ES.SetSchedule`
- **Supported Slots**: 0-9 (10 total slots)
- **Time Format**: HH:MM (24-hour format)
- **Power Range**: -10000W to +10000W
- **Week Set Range**: 1-127 (bitmask)

## Notes

- The Marstek API does **not support reading back** configured schedules
- Configure carefully and document your settings
- Only slots that are enabled will be active
- Multiple slots can be active simultaneously if their time ranges don't conflict
- The device must be in **Manual** mode for schedules to take effect

## Files Modified

1. `custom_components/hacs_marstek_venus_e/config_flow.py`
2. `custom_components/hacs_marstek_venus_e/strings.json`
3. `custom_components/hacs_marstek_venus_e/translations/en.json`
4. `custom_components/hacs_marstek_venus_e/translations/fr.json`

## Backwards Compatibility

This change is fully backwards compatible:
- Previous configurations using slots 1-4 will continue to work
- The new range (0-9) provides 6 additional slots
- Existing automations and services are unaffected
