# Marstek Venus E - Home Assistant Integration Features

## Overview
This integration provides full control and monitoring of your Marstek Venus E battery system through Home Assistant, using the Local API 143.

## Installation Flow

### 1. Automatic Device Discovery
When you add the integration in Home Assistant:
1. Click "Add Integration" and search for "Marstek Venus E"
2. The integration automatically scans your local network for Marstek devices
3. Discovery runs for 15 seconds using UDP broadcast on port 30000
4. All discovered devices are displayed with their IP address, device name, and identifier

### 2. Device Selection
- If devices are found: Select from the list of discovered devices
- If no devices found: Automatically prompted to enter IP address manually
- Option to manually enter IP at any time by selecting "Enter IP manually"

### 3. Configuration Complete
After selection, the device appears at:
`https://homeassistant.local:8123/config/integrations/integration/marstek_venus_e`

## Features

### Battery Status Monitoring
The integration provides comprehensive battery status sensors:

#### Battery Sensors
- **Battery State of Charge** - Current battery percentage (%)
- **Battery Capacity** - Available energy in Wh
- **Battery Rated Capacity** - Maximum battery capacity in Wh
- **Battery Power** - Current charging/discharging power in Watts
- **Battery Temperature** - Battery temperature in °C
- **Battery Charging** (Binary) - Whether battery is currently charging
- **Battery Discharging** (Binary) - Whether battery is currently discharging

#### Solar (PV) Sensors
- **PV Power** - Current solar power generation in Watts
- **PV Voltage** - Solar panel voltage
- **PV Current** - Solar panel current

#### Grid Sensors
- **Grid Power** - Current grid power (import/export) in Watts
- **Off-Grid Power** - Power when off-grid

#### Energy Statistics
- **Total PV Energy** - Cumulative solar energy generated (kWh)
- **Total Grid Export Energy** - Total energy exported to grid (kWh)
- **Total Grid Import Energy** - Total energy imported from grid (kWh)
- **Total Load Energy** - Total energy consumed by loads (kWh)

#### CT Meter (if connected)
- **Phase A/B/C Power** - Individual phase power measurements
- **Total CT Power** - Total power across all phases
- **CT Meter Connected** (Binary) - Connection status

#### System Sensors
- **WiFi Signal Strength** - Device WiFi signal in dBm
- **WiFi SSID** - Connected network name
- **Operating Mode** - Current system mode

### Operating Mode Control

The integration provides a **Select** entity to change operating modes directly from the UI:

#### Available Modes:
1. **Auto (Self-Consuming)** - Optimizes for self-consumption
2. **AI Mode** - Intelligent optimization based on usage patterns
3. **Manual** - Uses configured schedules
4. **Passive** - Follows a specific power target

Simply use the "Operating Mode" select entity in Home Assistant to switch between modes.

### Manual Mode Configuration

Configure manual charging/discharging schedules through the integration options:

#### Access Options:
1. Go to Settings → Devices & Services
2. Find "Marstek Venus E" integration
3. Click "Configure" (gear icon)
4. Select "Configure Manual Mode Schedule"

#### Schedule Configuration:
- **Time Slot** (1-4): Choose which of the 4 available slots to configure
- **Start Time**: When the schedule should start (HH:MM)
- **End Time**: When the schedule should end (HH:MM)
- **Active Days**: Select which days of the week (Monday-Sunday)
- **Power**: 
  - **Negative values** = Charge battery (e.g., -1000W to charge at 1kW)
  - **Positive values** = Discharge battery (e.g., 1000W to discharge at 1kW)
- **Enable**: Toggle to activate/deactivate this schedule

#### View Current Schedules:
From the configuration menu, select "View Current Schedules" to see all configured time slots.

### Services

The integration provides three services for automation:

#### 1. `marstek_venus_e.set_mode`
Change the operating mode programmatically.
```yaml
service: marstek_venus_e.set_mode
data:
  mode: "Manual"
```

#### 2. `marstek_venus_e.set_manual_schedule`
Configure a manual schedule via automation or script.
```yaml
service: marstek_venus_e.set_manual_schedule
data:
  time_num: 1
  start_time: "08:00"
  end_time: "16:00"
  week_set: 31  # Monday-Friday (1+2+4+8+16)
  power: -1000  # Charge at 1kW
  enable: true
```

Week Set Bitmask:
- Monday = 1, Tuesday = 2, Wednesday = 4, Thursday = 8
- Friday = 16, Saturday = 32, Sunday = 64
- All days = 127, Weekdays = 31, Weekend = 96

#### 3. `marstek_venus_e.set_passive_mode`
Set passive mode with a specific power target.
```yaml
service: marstek_venus_e.set_passive_mode
data:
  power: 500  # Target 500W
  cd_time: 0  # 0 = indefinite, or seconds for countdown
```

## Technical Details

### Communication
- **Protocol**: UDP JSON-RPC over local network
- **Port**: 30000 (default)
- **Discovery**: UDP broadcast with automatic device detection
- **Update Interval**: 5 seconds (configurable)

### API Methods Used
- `Marstek.GetDevice` - Device discovery and information
- `Bat.GetStatus` - Battery status
- `ES.GetStatus` - Energy system status
- `ES.GetMode` - Current operating mode
- `ES.SetMode` - Change operating mode
- `ES.SetSchedule` - Configure manual schedules
- `ES.GetSchedule` - Retrieve current schedules
- `ES.SetPassiveMode` - Configure passive mode
- `Wifi.GetStatus` - WiFi connection status

### Platforms
- **Sensor** - All monitoring sensors
- **Binary Sensor** - On/off status indicators
- **Select** - Operating mode selector

## Example Automations

### Charge During Off-Peak Hours
```yaml
automation:
  - alias: "Charge Battery at Night"
    trigger:
      platform: time
      at: "02:00:00"
    action:
      - service: marstek_venus_e.set_mode
        data:
          mode: "Manual"
      - service: marstek_venus_e.set_manual_schedule
        data:
          time_num: 1
          start_time: "02:00"
          end_time: "07:00"
          week_set: 127  # Every day
          power: -2000  # Charge at 2kW
          enable: true
```

### Return to Auto Mode in Morning
```yaml
automation:
  - alias: "Switch to Auto Mode Morning"
    trigger:
      platform: time
      at: "07:00:00"
    action:
      - service: marstek_venus_e.set_mode
        data:
          mode: "Auto"
```

### Export Excess Solar
```yaml
automation:
  - alias: "Export Solar When Battery Full"
    trigger:
      - platform: numeric_state
        entity_id: sensor.battery_state_of_charge
        above: 95
    condition:
      - condition: numeric_state
        entity_id: sensor.pv_power
        above: 1000
    action:
      - service: marstek_venus_e.set_passive_mode
        data:
          power: 1000  # Export 1kW to grid
```

## Troubleshooting

### Device Not Discovered
1. Ensure device is on the same network
2. Check firewall isn't blocking UDP port 30000
3. Try manual IP entry
4. Verify device is powered on and connected to WiFi

### Connection Issues
- Device only responds to UDP broadcasts, not unicast
- Discovery verifies connectivity
- Check Home Assistant can send UDP broadcasts on your network

### Schedule Not Working
1. Ensure device is in "Manual" mode
2. Verify schedule is enabled
3. Check time slots don't overlap
4. Confirm power values are within device limits

## Support
For issues or questions:
- Check the integration logs in Home Assistant
- Review the API documentation (Local API 143)
- Report issues on GitHub
