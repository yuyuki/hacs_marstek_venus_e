# Manual Mode Automation Guide

## Overview

This guide shows how to create Home Assistant automations that automatically configure all 10 schedule slots when you switch to Manual mode on your Marstek Venus E battery system.

## Understanding Schedule Slots

The Marstek Venus E supports **10 schedule slots (0-9)** when in Manual mode. Each slot can be configured with:

- **Time Slot Number**: 0-9 (which slot to configure)
- **Start Time**: When the schedule begins (HH:MM format)
- **End Time**: When the schedule ends (HH:MM format) - **Must be greater than start time**
- **Days of Week**: Which days the schedule is active (byte-based bitmask - see below)
- **Mode**: Charging or Discharging
  - **Charging**: Battery charges from grid/solar (power becomes negative)
  - **Discharging**: Battery discharges to home (power stays positive)
- **Power**: 100 to 800 watts (magnitude only, always positive)
  - **Note**: The mode parameter determines if it's negative (charging) or positive (discharging)
  - Power range is limited to 100-800W by the device
- **Enable**: True/False to activate or deactivate the slot

## Day Selection

### Via UI (Multi-Select)
When configuring schedules via the UI, you can select multiple days with checkboxes.

### Via Services/Automations (Bitmask)
When using the service in automations, you use a bitmask:

| Value | Day | Binary |
|-------|-----|--------|
| 1 | Monday | 0000001 |
| 2 | Tuesday | 0000010 |
| 4 | Wednesday | 0000100 |
| 8 | Thursday | 0001000 |
| 16 | Friday | 0010000 |
| 32 | Saturday | 0100000 |
| 64 | Sunday | 1000000 |

**Common Combinations:**
- **127** = All days (1+2+4+8+16+32+64)
- **31** = Weekdays only (1+2+4+8+16)
- **96** = Weekends only (32+64)
- **62** = Tuesday-Saturday (2+4+8+16+32)

To calculate custom combinations, add the values for the days you want.

## Example Automations

### Basic Example: Configure Slots When Switching to Manual Mode

This automation configures 3 schedule slots when you select Manual mode:

```yaml
automation:
  - alias: "Marstek - Configure Manual Mode Schedules"
    description: "Automatically configure battery schedules when switching to Manual mode"
    
    trigger:
      - platform: state
        entity_id: select.operating_mode
        to: "Manual"
    
    action:
      # Slot 0: Night charging (off-peak)
      - service: hacs_marstek_venus_e.set_manual_schedule
        data:
          time_num: 0
          start_time: "01:00"
          end_time: "06:00"
          week_set: 127  # All days
          mode: "Charging"
          power: 500  # 500W charging
          enable: true
      
      # Slot 1: Morning peak discharge (weekdays only)
      - service: hacs_marstek_venus_e.set_manual_schedule
        data:
          time_num: 1
          start_time: "07:00"
          end_time: "09:00"
          week_set: 31  # Monday-Friday
          mode: "Discharging"
          power: 600  # 600W discharging
          enable: true
      
      # Slot 2: Evening peak discharge (all days)
      - service: hacs_marstek_venus_e.set_manual_schedule
        data:
          time_num: 2
          start_time: "18:00"
          end_time: "22:00"
          week_set: 127  # All days
          mode: "Discharging"
          power: 700  # 700W discharging
          enable: true
```

### Advanced Example: All 10 Slots Configured

This example uses all 10 available slots for detailed schedule control:

```yaml
automation:
  - alias: "Marstek - Full 10-Slot Schedule"
    description: "Configure all 10 schedule slots for complete control"
    
    trigger:
      - platform: state
        entity_id: select.operating_mode
        to: "Manual"
    
    action:
      # Slot 0: Midnight operation
      - service: hacs_marstek_venus_e.set_manual_schedule
        data:
          time_num: 0
          start_time: "00:00"
          end_time: "04:00"
          week_set: 127  # All days
          power: 800  # 800W (maximum)
          enable: true
      
      # Slot 1: Early morning operation
      - service: hacs_marstek_venus_e.set_manual_schedule
        data:
          time_num: 1
          start_time: "04:00"
          end_time: "06:00"
          week_set: 127  # All days
          power: 600  # 600W
          enable: true
      
      # Slot 2: Morning peak (weekdays)
      - service: hacs_marstek_venus_e.set_manual_schedule
        data:
          time_num: 2
          start_time: "07:00"
          end_time: "09:00"
          week_set: 31  # Weekdays only
          power: 700  # 700W
          enable: true
      
      # Slot 3: Mid-morning (let solar handle it)
      - service: hacs_marstek_venus_e.set_manual_schedule
        data:
          time_num: 3
          start_time: "09:00"
          end_time: "12:00"
          week_set: 127  # All days
          power: 0  # No charging/discharging
          enable: false  # Disabled - solar only
      
      # Slot 4: Midday operation (weekdays)
      - service: hacs_marstek_venus_e.set_manual_schedule
        data:
          time_num: 4
          start_time: "12:00"
          end_time: "14:00"
          week_set: 31  # Weekdays only
          power: 400  # 400W
          enable: true
      
      # Slot 5: Afternoon (let solar handle it)
      - service: hacs_marstek_venus_e.set_manual_schedule
        data:
          time_num: 5
          start_time: "14:00"
          end_time: "17:00"
          week_set: 127  # All days
          power: 100  # Minimum power
          enable: false  # Disabled
      
      # Slot 6: Early evening shoulder peak (all days)
      - service: hacs_marstek_venus_e.set_manual_schedule
        data:
          time_num: 6
          start_time: "17:00"
          end_time: "19:00"
          week_set: 127  # All days
          power: 500  # 500W
          enable: true
      
      # Slot 7: Evening peak (all days)
      - service: hacs_marstek_venus_e.set_manual_schedule
        data:
          time_num: 7
          start_time: "19:00"
          end_time: "22:00"
          week_set: 127  # All days
          power: 750  # 750W
          enable: true
      
      # Slot 8: Late evening (weekends - different pattern)
      - service: hacs_marstek_venus_e.set_manual_schedule
        data:
          time_num: 8
          start_time: "22:00"
          end_time: "23:30"
          week_set: 96  # Weekends only
          power: 300  # 300W
          enable: true
      
      # Slot 9: Pre-midnight operation
      - service: hacs_marstek_venus_e.set_manual_schedule
        data:
          time_num: 9
          start_time: "23:00"
          end_time: "23:59"
          week_set: 31  # Weekdays only
          power: 600  # 600W
          enable: true
```

### Seasonal Example: Winter vs Summer Schedules

You can create different schedules based on the season:

```yaml
automation:
  # Winter schedule
  - alias: "Marstek - Winter Manual Schedule"
    description: "Winter schedule with more grid charging"
    
    trigger:
      - platform: state
        entity_id: select.operating_mode
        to: "Manual"
    
    condition:
      - condition: template
        value_template: "{{ now().month in [11, 12, 1, 2] }}"  # Nov-Feb
    
    action:
      # Winter operation pattern
      - service: hacs_marstek_venus_e.set_manual_schedule
        data:
          time_num: 0
          start_time: "01:00"
          end_time: "07:00"
          week_set: 127
          power: 800  # Maximum (800W)
          enable: true
      
      - service: hacs_marstek_venus_e.set_manual_schedule
        data:
          time_num: 1
          start_time: "18:00"
          end_time: "22:00"
          week_set: 127
          power: 600  # 600W during evening peak
          enable: true

  # Summer schedule
  - alias: "Marstek - Summer Manual Schedule"
    description: "Summer schedule with more solar reliance"
    
    trigger:
      - platform: state
        entity_id: select.operating_mode
        to: "Manual"
    
    condition:
      - condition: template
        value_template: "{{ now().month in [5, 6, 7, 8] }}"  # May-Aug
    
    action:
      # Summer operation pattern
      - service: hacs_marstek_venus_e.set_manual_schedule
        data:
          time_num: 0
          start_time: "02:00"
          end_time: "05:00"
          week_set: 127
          power: 400  # Reduced (400W)
          enable: true
      
      - service: hacs_marstek_venus_e.set_manual_schedule
        data:
          time_num: 1
          start_time: "18:00"
          end_time: "21:00"
          week_set: 127
          power: 700  # 700W (solar-charged battery)
          enable: true
```

### Dynamic Schedule Based on Battery Level

Configure different schedules based on current battery state:

```yaml
automation:
  - alias: "Marstek - Dynamic Schedule (Low Battery)"
    description: "Aggressive charging when battery is low"
    
    trigger:
      - platform: state
        entity_id: select.operating_mode
        to: "Manual"
    
    condition:
      - condition: numeric_state
        entity_id: sensor.battery_state_of_charge
        below: 30  # Battery below 30%
    
    action:
      # Operation when battery low
      - service: hacs_marstek_venus_e.set_manual_schedule
        data:
          time_num: 0
          start_time: "00:00"
          end_time: "08:00"
          week_set: 127
          power: 800  # Maximum (800W)
          enable: true

  - alias: "Marstek - Dynamic Schedule (High Battery)"
    description: "Adjust operation when battery is full"
    
    trigger:
      - platform: state
        entity_id: select.operating_mode
        to: "Manual"
    
    condition:
      - condition: numeric_state
        entity_id: sensor.battery_state_of_charge
        above: 80  # Battery above 80%
    
    action:
      # Operation when battery high
      - service: hacs_marstek_venus_e.set_manual_schedule
        data:
          time_num: 0
          start_time: "07:00"
          end_time: "22:00"
          week_set: 127
          power: 700  # 700W during day
          enable: true
```

## Integration with Energy Pricing

You can integrate with dynamic pricing (e.g., Nordpool, Octopus Energy):

```yaml
automation:
  - alias: "Marstek - Price-Based Charging"
    description: "Charge when electricity is cheap"
    
    trigger:
      - platform: state
        entity_id: select.operating_mode
        to: "Manual"
    
    action:
      # This is a simplified example - adjust times based on your pricing schedule
      - service: hacs_marstek_venus_e.set_manual_schedule
        data:
          time_num: 0
          start_time: "{{ state_attr('sensor.nordpool_price', 'cheapest_start') }}"
          end_time: "{{ state_attr('sensor.nordpool_price', 'cheapest_end') }}"
          week_set: 127
          power: 800  # Maximum (800W)
          enable: true
```

## Clearing All Schedules

If you want to clear all schedules when switching away from Manual mode:

```yaml
automation:
  - alias: "Marstek - Clear Schedules on Mode Change"
    description: "Clear all schedules when leaving Manual mode"
    
    trigger:
      - platform: state
        entity_id: select.operating_mode
        from: "Manual"
    
    action:
      - service: hacs_marstek_venus_e.clear_all_schedules
```

## Tips and Best Practices

1. **Time Validation**: End time MUST be greater than start time (device requirement)
2. **Power Limits**: Power must be between 100-800W (device enforced)
3. **Non-Overlapping Times**: Avoid overlapping time slots with conflicting power settings
4. **Byte-Based Days**: Days of week use byte-based bitmask (1=Mon, 2=Tue, 4=Wed, etc.)
5. **Battery Protection**: Monitor battery levels and adjust schedules accordingly
6. **Solar Integration**: Leave gaps during peak solar hours (11:00-15:00) to maximize solar usage
7. **Testing**: Test schedules on weekends first before applying to weekdays
8. **Documentation**: Keep notes of what each slot does in your automation description
9. **Mode Requirement**: Schedules only work when the system is in Manual mode
10. **Disabled Slots**: Use `enable: false` for slots you want to keep configured but temporarily inactive

## Verifying Your Schedules

Unfortunately, the Marstek API does not support reading back configured schedules. To verify:

1. Monitor your battery power sensor during scheduled times
2. Check if charging/discharging occurs as expected
3. Create a helper entity to track when you last updated the schedule
4. Document your schedules in the automation description

## Troubleshooting

### Schedule Not Working
- Verify the system is in Manual mode
- Check that `enable: true` is set
- Ensure times are in 24-hour format (HH:MM)
- Verify power value (negative=charge, positive=discharge)
- Check that week_set includes today

### Automation Not Triggering
- Verify the entity_id in trigger matches your actual entity
- Check automation is enabled
- Look at Home Assistant logs for errors

### Wrong Days
- Double-check your week_set calculation
- Use 127 for "all days" as a test
- Remember: 1=Mon, 2=Tue, 4=Wed, 8=Thu, 16=Fri, 32=Sat, 64=Sun

## Advanced: Template-Based Schedules

Use templates for even more dynamic control:

```yaml
automation:
  - alias: "Marstek - Template-Based Schedule"
    
    trigger:
      - platform: state
        entity_id: select.operating_mode
        to: "Manual"
    
    action:
      - service: hacs_marstek_venus_e.set_manual_schedule
        data:
          time_num: 0
          start_time: "01:00"
          end_time: "06:00"
          week_set: 127
          # Adjust power based on battery level (within 100-800W range)
          power: >
            {% set soc = states('sensor.battery_state_of_charge') | int %}
            {% if soc < 30 %}
              800
            {% elif soc < 60 %}
              600
            {% else %}
              300
            {% endif %}
          enable: true
```

## Service Reference

### set_manual_schedule

**Service**: `hacs_marstek_venus_e.set_manual_schedule`

**Parameters**:
- `time_num`: 0-9 (required)
- `start_time`: "HH:MM" format (required)
- `end_time`: "HH:MM" format (required) - must be greater than start_time
- `week_set`: 1-127 byte-based bitmask (required)
- `mode`: "Charging" or "Discharging" (required)
- `power`: 100 to 800 watts - magnitude only (required)
- `enable`: true/false (optional, default: true)

**Important Constraints**:
- End time MUST be greater than start time
- Power magnitude is limited to 100-800W range
- Mode determines sign: Charging = negative, Discharging = positive
- Days use byte-based bitmask (not individual day selection)

### clear_all_schedules

**Service**: `hacs_marstek_venus_e.clear_all_schedules`

No parameters required. Disables all 10 schedule slots.

## Related Documentation

- [Manual Mode 10 Slots Guide](MANUAL_MODE_10_SLOTS.md) - Technical details about the 10-slot support
- [Integration Guide](INTEGRATION_GUIDE.md) - General integration documentation
- [Services Documentation](custom_components/hacs_marstek_venus_e/services.yaml) - Service definitions

## Questions?

If you need help with your specific use case, feel free to open an issue on GitHub with:
- Your desired schedule pattern
- Your energy pricing structure
- Your typical daily usage pattern
- Any specific requirements or constraints
