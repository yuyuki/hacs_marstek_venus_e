# Quick Schedule Reference Card

## 10 Time Slots (0-9) Configuration

Each slot can be independently configured with these parameters:

| Parameter | Description | Values |
|-----------|-------------|--------|
| **time_num** | Slot number | 0-9 |
| **start_time** | Start time | "HH:MM" (24-hour) |
| **end_time** | End time | "HH:MM" (24-hour, MUST be > start_time) |
| **week_set** | Active days | 1-127 (byte-based bitmask) |
| **mode** | Operation mode | "Charging" or "Discharging" |
| **power** | Power magnitude | 100 to 800 W (always positive) |
| **enable** | Active slot | true/false |

## Mode & Power Values

**MODE: Determines charging vs discharging**
```
"Charging"    → Power becomes negative (battery charges)
"Discharging" → Power stays positive (battery discharges)
```

**POWER: Always positive 100-800W magnitude**

```
Power Settings (100-800W range)
├── 800W = Maximum power
├── 700W = High power
├── 600W = Medium-high power
├── 500W = Medium power
├── 400W = Medium-low power
├── 300W = Low power
├── 200W = Very low power
└── 100W = Minimum power

⚠️ Values outside 100-800W will be rejected by device
⚠️ Power is ALWAYS positive - mode determines the sign
```

## Day Bitmask Quick Reference

```
╔═══════════╦═══════╦════════════════╗
║ Day       ║ Value ║ Binary         ║
╠═══════════╬═══════╬════════════════╣
║ Monday    ║   1   ║ 0000001        ║
║ Tuesday   ║   2   ║ 0000010        ║
║ Wednesday ║   4   ║ 0000100        ║
║ Thursday  ║   8   ║ 0001000        ║
║ Friday    ║  16   ║ 0010000        ║
║ Saturday  ║  32   ║ 0100000        ║
║ Sunday    ║  64   ║ 1000000        ║
╚═══════════╩═══════╩════════════════╝

Common Combinations:
├── 127 = All days (1+2+4+8+16+32+64)
├── 31  = Weekdays (1+2+4+8+16)
├── 96  = Weekends (32+64)
├── 62  = Tue-Sat (2+4+8+16+32)
└── 65  = Mon+Sun (1+64)
```

## Calculator

To calculate your custom bitmask, add the values:

**Example 1: Monday, Wednesday, Friday**
```
Monday (1) + Wednesday (4) + Friday (16) = 21
```

**Example 2: Weekend + Friday**
```
Friday (16) + Saturday (32) + Sunday (64) = 112
```

## Service Call Template

```yaml
service: hacs_marstek_venus_e.set_manual_schedule
data:
  time_num: 0              # Slot 0-9
  start_time: "00:00"      # HH:MM
  end_time: "23:59"        # HH:MM (MUST be > start_time)
  week_set: 127            # Byte-based bitmask
  mode: "Charging"         # "Charging" or "Discharging"
  power: 500               # 100-800 Watts (always positive)
  enable: true             # true/false
```

**Critical Constraints:**
- `end_time` MUST be greater than `start_time`
- `mode` MUST be "Charging" or "Discharging"
- `power` MUST be between 100 and 800 (inclusive, always positive)
- `week_set` uses byte-based bitmask (not boolean array)

## Common Use Cases

### 🌙 Night Charging (Off-Peak)
```yaml
time_num: 0
start_time: "01:00"
end_time: "06:00"
week_set: 127       # All days
mode: "Charging"
power: 800          # Charge at 800W
enable: true
```

### ☀️ Midday Solar Charging
```yaml
time_num: 1
start_time: "11:00"
end_time: "15:00"
week_set: 127       # All days
mode: "Charging"
power: 400          # Charge at 400W
enable: true
```

### ⚡ Evening Peak Discharge
```yaml
time_num: 2
start_time: "18:00"
end_time: "22:00"
week_set: 127       # All days
mode: "Discharging"
power: 700          # Discharge at 700W
enable: true
```

### 💼 Weekday Morning Discharge
```yaml
time_num: 3
start_time: "07:00"
end_time: "09:00"
week_set: 31        # Mon-Fri only
mode: "Discharging"
power: 600          # Discharge at 600W
enable: true
```

### 🏖️ Weekend Light Discharge
```yaml
time_num: 4
start_time: "10:00"
end_time: "14:00"
week_set: 96        # Sat-Sun only
mode: "Discharging"
power: 300          # Discharge at 300W
enable: true
```

### 🚫 Disabled Slot (Reserved)
```yaml
time_num: 5
start_time: "00:00"
end_time: "01:00"   # Must be > start_time
week_set: 127
mode: "Charging"
power: 100          # Minimum power
enable: false       # Disabled
```

## Visual Schedule Planner

```
Hour │ 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23
─────┼────────────────────────────────────────────────────────────────────────
Slot0│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                                              
Slot1│                   ░░░░░░░░░░░░                                          
Slot2│                                    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░        
Slot3│                                                            ▓▓▓▓▓▓▓▓▓▓▓▓
Slot4│ (unused)
...  │ (configure as needed)

Legend:
▓▓▓▓ = Charging (negative power)
░░░░ = Discharging (positive power)
     = Inactive/disabled
```

## Automation Trigger Template

```yaml
automation:
  - alias: "Configure Manual Schedules"
    trigger:
      - platform: state
        entity_id: select.operating_mode
        to: "Manual"
    action:
      # Add your 10 slots here
      - service: hacs_marstek_venus_e.set_manual_schedule
        data:
          time_num: 0
          # ... rest of configuration
```

## Clear All Schedules

To disable all 10 slots at once:

```yaml
service: hacs_marstek_venus_e.clear_all_schedules
```

This sets `enable: false` for all slots (0-9).

## Tips & Best Practices

✅ **DO:**
- Ensure end_time > start_time (device requirement)
- Keep power between 100-800W (device enforced)
- Use byte-based bitmask for week_set
- Use all 10 slots for fine-grained control
- Set `enable: false` for unused slots
- Align with your electricity tariff periods
- Test schedules on weekends first
- Document each slot's purpose

❌ **DON'T:**
- Set end_time <= start_time (will fail)
- Use power values outside 100-800W range
- Overlap conflicting power settings
- Forget to switch to Manual mode!

## Verification

Since the API doesn't support reading schedules back:

1. **Monitor** battery power sensor during scheduled times
2. **Document** your slots in automation descriptions
3. **Create logs** in Home Assistant when schedules are set
4. **Use notifications** to confirm configuration

---

**📖 For complete examples and advanced patterns, see:**
- [Manual Mode Automation Guide](MANUAL_MODE_AUTOMATION_GUIDE.md)
- [Example Automation YAML](example_automation.yaml)
- [Integration Guide](INTEGRATION_GUIDE.md)
