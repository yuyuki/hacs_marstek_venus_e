# Quick Setup Guide - Marstek Venus E Integration

## 🚀 Quick Start (5 minutes)

### Step 1: Install the Integration
1. In Home Assistant, go to **Settings** → **Devices & Services**
2. Click **"+ Add Integration"** (bottom right)
3. Search for **"Marstek Venus E"**
4. Click on it to start setup

### Step 2: Device Discovery
The integration will automatically scan your network for Marstek devices.

**If device is found:**
- Select your device from the list
- Click Submit

**If no device found:**
- Select "Enter IP manually"
- Enter your device's IP address (find it in your router)
- Port: 30000 (default)
- Click Submit

### Step 3: Done! 
Your device is now configured and appears in:
- **Settings** → **Devices & Services** → **Marstek Venus E**

## 📊 What You Get

### Automatic Sensors
Once configured, you'll immediately see:
- Battery level (%)
- Battery power (W)
- Solar production (W)
- Grid power (W)
- All energy statistics (kWh)

### Operating Mode Selector
Change modes directly from the UI:
- **Auto** - Self-consumption optimization
- **AI** - Intelligent mode
- **Manual** - Use your schedules
- **Passive** - Fixed power target

Find it in: **Entities** → Search "Operating Mode"

## ⚙️ Configure Manual Schedules (Optional)

Want to charge/discharge at specific times?

### Via UI (Recommended)
1. Go to **Settings** → **Devices & Services**
2. Find **Marstek Venus E** → Click **Configure** (gear icon)
3. Select **"Configure Manual Mode Schedule"**
4. Fill in:
   - **Time Slot**: 1-4 (you can create 4 schedules)
   - **Start/End Time**: When to run
   - **Days**: Which days to apply
   - **Power**: 
     - **-1000** = Charge at 1kW
     - **+1000** = Discharge at 1kW
   - **Enable**: Check to activate
5. Click Submit

### Example Schedules

**Night Charging (Cheap Electricity)**
- Time Slot: 1
- Start: 02:00, End: 07:00
- Days: Every day
- Power: -2000 (charge 2kW)
- Enable: ✓

**Peak Export (Expensive Electricity)**
- Time Slot: 2
- Start: 17:00, End: 20:00
- Days: Weekdays
- Power: +1500 (discharge 1.5kW)
- Enable: ✓

## 🤖 Simple Automations

### Charge Battery at Night
```yaml
alias: Night Charging
trigger:
  - platform: time
    at: "02:00:00"
action:
  - service: marstek_venus_e.set_mode
    data:
      mode: "Manual"
```

### Back to Auto in Morning
```yaml
alias: Morning Auto Mode
trigger:
  - platform: time
    at: "07:00:00"
action:
  - service: marstek_venus_e.set_mode
    data:
      mode: "Auto"
```

### Low Battery Alert
```yaml
alias: Battery Low Notification
trigger:
  - platform: numeric_state
    entity_id: sensor.battery_state_of_charge
    below: 20
action:
  - service: notify.mobile_app
    data:
      message: "Battery is low ({{ states('sensor.battery_state_of_charge') }}%)"
```

## 📱 Dashboard Card Example

Add this to your dashboard for quick monitoring:

```yaml
type: entities
title: Marstek Venus E
entities:
  - entity: sensor.battery_state_of_charge
    name: Battery Level
  - entity: sensor.battery_power
    name: Battery Power
  - entity: sensor.pv_power
    name: Solar Production
  - entity: sensor.grid_power
    name: Grid Power
  - entity: select.operating_mode
    name: Mode
  - entity: binary_sensor.battery_charging
    name: Charging Status
```

## ❓ Troubleshooting

### Can't Find Device
- Make sure device is on the same WiFi network as Home Assistant
- Check your router's DHCP client list for the device IP
- Try entering IP manually

### Integration Shows Error
- Check the device is powered on
- Verify network connectivity
- Try reloading the integration: Settings → Devices & Services → Marstek Venus E → ⋮ → Reload

### Schedules Not Working
- Make sure device is in **Manual** mode (use the Operating Mode selector)
- Verify the schedule is **enabled**
- Check power values are within your battery limits

## 🎯 Next Steps

1. **Monitor your system**: Check the sensors work correctly
2. **Test mode switching**: Try changing between Auto/Manual modes
3. **Set up schedules**: Configure charging/discharging times
4. **Create automations**: Build smart rules for your needs
5. **Add to dashboard**: Create a nice energy monitoring card

## 📚 More Information

- **Full Documentation**: See `INTEGRATION_FEATURES.md`
- **API Details**: Check `INTEGRATION_GUIDE.md`
- **Test Tools**: See `tests/` folder for testing scripts

---

**Need Help?** Check the logs:
- Settings → System → Logs → Search "marstek"
