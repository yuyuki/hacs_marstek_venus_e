# Schedule Configuration Constraints - IMPORTANT

## Critical Device Constraints

Based on the device PDF documentation, the following constraints apply to manual schedule configuration:

### 1. Time Constraint
- **End time MUST be greater than start time**
- This is enforced by the device
- Schedules that cross midnight (e.g., 23:00 to 07:00) are **NOT supported**
- Each schedule must complete within the same 24-hour period

**Valid Example:**
```yaml
start_time: "01:00"
end_time: "06:00"  # ✅ Valid: 06:00 > 01:00
```

**Invalid Example:**
```yaml
start_time: "23:00"
end_time: "07:00"  # ❌ Invalid: 07:00 < 23:00 (crosses midnight)
```

### 2. Power Range and Mode
- **Power magnitude must be between 100 and 800 watts**
- **Mode** determines if it's charging (negative) or discharging (positive)
- This is enforced by the device hardware

**Mode Parameter:**
- `Charging`: Power becomes negative (-100 to -800W)
- `Discharging`: Power stays positive (100 to 800W)

**Valid Examples:**
```yaml
mode: "Charging"
power: 500   # ✅ Results in -500W (charging at 500W)

mode: "Discharging"
power: 800   # ✅ Results in +800W (discharging at 800W)
```

**Invalid Examples:**
```yaml
power: 50     # ❌ Too low
power: 1000   # ❌ Too high
power: 0      # ❌ Below minimum
```

### 3. Days of Week (Byte-Based)
- Uses byte-based bitmask (not boolean array)
- Each day is represented by a power of 2

| Day | Value | Binary |
|-----|-------|--------|
| Monday | 1 | 0000001 |
| Tuesday | 2 | 0000010 |
| Wednesday | 4 | 0000100 |
| Thursday | 8 | 0001000 |
| Friday | 16 | 0010000 |
| Saturday | 32 | 0100000 |
| Sunday | 64 | 1000000 |

**To select multiple days, add their values:**
- Monday + Wednesday + Friday = 1 + 4 + 16 = 21
- All days = 1 + 2 + 4 + 8 + 16 + 32 + 64 = 127
- Weekdays = 1 + 2 + 4 + 8 + 16 = 31
- Weekends = 32 + 64 = 96

## Updated Integration Constraints

The integration has been updated to enforce these constraints:

### services.yaml
```yaml
power:
  selector:
    number:
      min: 100      # Device minimum
      max: 800      # Device maximum
      step: 10
```

### services.py
```python
vol.Required("power"): vol.All(vol.Coerce(int), vol.Range(min=100, max=800))
```

## Workaround for Midnight Crossing

If you need a schedule that runs overnight, you must create **two separate slots**:

**Example: Run from 23:00 to 07:00**

Create two slots:
```yaml
# Slot 0: Evening portion (23:00 to 23:59)
- service: hacs_marstek_venus_e.set_manual_schedule
  data:
    time_num: 0
    start_time: "23:00"
    end_time: "23:59"
    week_set: 127
    power: 500
    enable: true

# Slot 1: Morning portion (00:00 to 07:00)
- service: hacs_marstek_venus_e.set_manual_schedule
  data:
    time_num: 1
    start_time: "00:00"
    end_time: "07:00"
    week_set: 127
    power: 500
    enable: true
```

## Impact on Existing Documentation

All documentation files have been updated with correct constraints:

### Files Updated
1. ✅ `MANUAL_MODE_AUTOMATION_GUIDE.md` - Full automation examples
2. ✅ `example_automation.yaml` - Ready-to-use automation
3. ✅ `QUICK_SCHEDULE_REFERENCE.md` - Quick reference guide
4. ✅ `README.md` - Main documentation
5. ✅ `services.yaml` - Service definitions with validation
6. ✅ `services.py` - Python validation schema

### Changes Made
- **Power range**: Changed from -10000 to +10000W → **100 to 800W**
- **Time validation**: Added note that end_time must be > start_time
- **Day selection**: Clarified byte-based bitmask usage
- **All examples**: Updated to use valid power values (100-800W)
- **Validation**: Added range constraints in schema

## Testing Recommendations

Before deploying to production:

1. **Test time validation**:
   - Verify end_time > start_time works
   - Confirm end_time <= start_time fails

2. **Test power limits**:
   - Try power = 100 (should work)
   - Try power = 800 (should work)
   - Try power = 99 (should fail)
   - Try power = 801 (should fail)

3. **Test day selection**:
   - Test single day (e.g., week_set = 1 for Monday)
   - Test multiple days (e.g., week_set = 31 for weekdays)
   - Test all days (week_set = 127)

4. **Test midnight crossing workaround**:
   - Create two consecutive slots that span midnight
   - Verify both slots execute correctly

## Questions?

If you encounter issues with these constraints or need clarification, please:
1. Check the device PDF documentation
2. Verify your device firmware version
3. Test with simple schedules first
4. Review the integration logs for errors

---

**Last Updated**: November 26, 2025
**Integration Version**: 1.0.0
**Based on**: Marstek Venus E Official API Documentation
