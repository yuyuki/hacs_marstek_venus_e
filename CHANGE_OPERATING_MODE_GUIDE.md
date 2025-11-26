# Quick Guide: Using the Change Operating Mode Service

## Overview

The `change_operating_mode` service allows you to change your Marstek Venus E operating mode and configure all 10 manual schedule slots in a single action. This is perfect for automations.

## Basic Usage

### Change to Auto Mode
```yaml
service: hacs_marstek_venus_e.change_operating_mode
data:
  mode: Auto
```

### Change to AI Mode
```yaml
service: hacs_marstek_venus_e.change_operating_mode
data:
  mode: AI
```

### Change to Passive Mode
```yaml
service: hacs_marstek_venus_e.change_operating_mode
data:
  mode: Passive
```

## Manual Mode with Schedules

### Example 1: Night Charging Only
Charge from grid during cheap nighttime hours:

```yaml
service: hacs_marstek_venus_e.change_operating_mode
data:
  mode: Manual
  slot_0_enable: true
  slot_0_start_time: "23:00"
  slot_0_end_time: "07:00"
  slot_0_power: 800
  slot_0_mode: Charging
  slot_0_days: 127  # Every day
```

### Example 2: Peak Shaving
Discharge during evening peak hours on weekdays:

```yaml
service: hacs_marstek_venus_e.change_operating_mode
data:
  mode: Manual
  slot_0_enable: true
  slot_0_start_time: "17:00"
  slot_0_end_time: "21:00"
  slot_0_power: 500
  slot_0_mode: Discharging
  slot_0_days: 31  # Monday-Friday (1+2+4+8+16)
```

### Example 3: Multiple Schedules
Charge at night, discharge during peak hours:

```yaml
service: hacs_marstek_venus_e.change_operating_mode
data:
  mode: Manual
  # Night charging
  slot_0_enable: true
  slot_0_start_time: "00:00"
  slot_0_end_time: "06:00"
  slot_0_power: 800
  slot_0_mode: Charging
  slot_0_days: 127  # Every day
  
  # Morning peak discharge
  slot_1_enable: true
  slot_1_start_time: "07:00"
  slot_1_end_time: "09:00"
  slot_1_power: 400
  slot_1_mode: Discharging
  slot_1_days: 31  # Weekdays
  
  # Evening peak discharge
  slot_2_enable: true
  slot_2_start_time: "17:00"
  slot_2_end_time: "22:00"
  slot_2_power: 600
  slot_2_mode: Discharging
  slot_2_days: 31  # Weekdays
```

### Example 4: Different Schedules for Weekdays vs Weekends
```yaml
service: hacs_marstek_venus_e.change_operating_mode
data:
  mode: Manual
  # Weekday schedule
  slot_0_enable: true
  slot_0_start_time: "23:00"
  slot_0_end_time: "06:00"
  slot_0_power: 800
  slot_0_mode: Charging
  slot_0_days: 31  # Mon-Fri
  
  # Weekend schedule (longer charging)
  slot_1_enable: true
  slot_1_start_time: "22:00"
  slot_1_end_time: "08:00"
  slot_1_power: 500
  slot_1_mode: Charging
  slot_1_days: 96  # Sat-Sun (32+64)
```

## Day Bitmask Quick Reference

Use these values for the `slot_X_days` field:

| Days | Value | Calculation |
|------|-------|-------------|
| Monday | 1 | - |
| Tuesday | 2 | - |
| Wednesday | 4 | - |
| Thursday | 8 | - |
| Friday | 16 | - |
| Saturday | 32 | - |
| Sunday | 64 | - |
| **Common Combinations** | | |
| All days | 127 | 1+2+4+8+16+32+64 |
| Weekdays (Mon-Fri) | 31 | 1+2+4+8+16 |
| Weekend (Sat-Sun) | 96 | 32+64 |
| Mon + Wed + Fri | 21 | 1+4+16 |
| Tue + Thu | 10 | 2+8 |

## Automation Examples

### Time-Based Automation
Switch to Manual mode at 10 PM:

```yaml
automation:
  - alias: "Switch to Manual Mode at Night"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: hacs_marstek_venus_e.change_operating_mode
        data:
          mode: Manual
          slot_0_enable: true
          slot_0_start_time: "22:00"
          slot_0_end_time: "07:00"
          slot_0_power: 800
          slot_0_mode: Charging
          slot_0_days: 127
```

### Price-Based Automation
Switch modes based on electricity price:

```yaml
automation:
  - alias: "Cheap Electricity - Charge"
    trigger:
      - platform: numeric_state
        entity_id: sensor.electricity_price
        below: 0.10
    action:
      - service: hacs_marstek_venus_e.change_operating_mode
        data:
          mode: Manual
          slot_0_enable: true
          slot_0_start_time: "{{ now().strftime('%H:%M') }}"
          slot_0_end_time: "{{ (now() + timedelta(hours=2)).strftime('%H:%M') }}"
          slot_0_power: 800
          slot_0_mode: Charging
          slot_0_days: 127

  - alias: "Expensive Electricity - Discharge"
    trigger:
      - platform: numeric_state
        entity_id: sensor.electricity_price
        above: 0.30
    action:
      - service: hacs_marstek_venus_e.change_operating_mode
        data:
          mode: Manual
          slot_0_enable: true
          slot_0_start_time: "{{ now().strftime('%H:%M') }}"
          slot_0_end_time: "{{ (now() + timedelta(hours=2)).strftime('%H:%M') }}"
          slot_0_power: 600
          slot_0_mode: Discharging
          slot_0_days: 127
```

### Solar Forecast Automation
Adjust based on tomorrow's solar forecast:

```yaml
automation:
  - alias: "Adjust Manual Mode Based on Solar Forecast"
    trigger:
      - platform: time
        at: "20:00:00"
    action:
      - choose:
          # Good solar forecast - minimal charging
          - conditions:
              - condition: numeric_state
                entity_id: sensor.solar_forecast_tomorrow
                above: 20  # kWh
            sequence:
              - service: hacs_marstek_venus_e.change_operating_mode
                data:
                  mode: Auto
          
          # Poor solar forecast - charge at night
          - conditions:
              - condition: numeric_state
                entity_id: sensor.solar_forecast_tomorrow
                below: 5  # kWh
            sequence:
              - service: hacs_marstek_venus_e.change_operating_mode
                data:
                  mode: Manual
                  slot_0_enable: true
                  slot_0_start_time: "23:00"
                  slot_0_end_time: "07:00"
                  slot_0_power: 800
                  slot_0_mode: Charging
                  slot_0_days: 127
        default:
          - service: hacs_marstek_venus_e.change_operating_mode
            data:
              mode: AI
```

## Tips

1. **Test First**: Test your schedules manually before adding to automations
2. **Non-Overlapping Times**: Avoid overlapping time slots for predictable behavior
3. **Power Limits**: Stay within 100-800W range
4. **Days Calculation**: Use the bitmask calculator above or sum individual day values
5. **Disable Unused Slots**: Set `slot_X_enable: false` or omit them (defaults to false)
6. **Time Format**: Always use 24-hour format "HH:MM" (e.g., "23:00" not "11:00 PM")

## Troubleshooting

**Schedule not activating:**
- Verify the device is in Manual mode
- Check start_time < end_time
- Confirm days bitmask is correct
- Ensure slot is enabled (`slot_X_enable: true`)

**Can't see all slots in UI:**
- All 10 slots are available, scroll down in the service dialog
- In automation YAML, you can configure any/all slots directly

**Mode changes but schedules don't:**
- Schedules only apply in Manual mode
- Check integration logs for errors
- Verify power is within 100-800W range
