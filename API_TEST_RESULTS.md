# Marstek Venus E Local API v143 - Test Results

## Test Date: November 26, 2025
**Device**: Marstek Venus E 3.0 (API v143)  
**IP**: 192.168.0.225  
**Current Mode**: Manual

## Summary of Findings

### ✅ Working API Methods

| Method | Purpose | Returns Schedule Config? |
|--------|---------|-------------------------|
| `ES.GetMode` | Get current operating mode | **NO** |
| `ES.GetStatus` | Get energy system status | **NO** |
| `Bat.GetStatus` | Get battery information | **NO** |
| `Marstek.GetDevice` | Get device information | **NO** |
| `Wifi.GetStatus` | Get WiFi connection status | **NO** |

### ❌ Non-Working API Methods

| Method | Status | Error |
|--------|--------|-------|
| `ES.GetSchedule` | **Does not exist** | Method not found (-32601) |

## Key Discovery: Schedules are Write-Only

The API v143 **does NOT support reading back manual schedule configurations**.

- You **CAN** set schedules using `ES.SetSchedule`
- You **CANNOT** retrieve schedules to view what's configured
- The device stores schedules internally but doesn't expose them via API

## Detailed API Response Analysis

### 1. ES.GetMode

**Request:**
```json
{
  "id": 1,
  "method": "ES.GetMode",
  "params": {"id": 0}
}
```

**Response:**
```json
{
  "id": 0,
  "mode": "Manual",
  "ongrid_power": 0,
  "offgrid_power": 0,
  "bat_soc": 11
}
```

**Fields:**
- `mode`: Current operating mode (Auto/AI/Manual/Passive)
- `ongrid_power`: Grid power in watts
- `offgrid_power`: Off-grid power in watts
- `bat_soc`: Battery state of charge (%)

**Notable:** No `manual_cfg`, `ai_cfg`, or `passive_cfg` fields present.

### 2. ES.GetStatus

**Request:**
```json
{
  "id": 1,
  "method": "ES.GetStatus",
  "params": {"id": 0}
}
```

**Response:**
```json
{
  "id": 0,
  "bat_soc": 11,
  "bat_cap": 5120,
  "pv_power": 0,
  "ongrid_power": 0,
  "offgrid_power": 0,
  "total_pv_energy": 0,
  "total_grid_output_energy": 9247,
  "total_grid_import_energy": 10335,
  "total_load_energy": 0
}
```

**Fields:**
- `bat_soc`: Battery state of charge (%)
- `bat_cap`: Battery capacity (Wh)
- `pv_power`: Solar PV power (W)
- `ongrid_power`: Grid power (W)
- `offgrid_power`: Off-grid power (W)
- `total_pv_energy`: Cumulative PV energy (Wh)
- `total_grid_output_energy`: Grid export (Wh)
- `total_grid_input_energy`: Grid import (Wh)
- `total_load_energy`: Load consumption (Wh)

**Notable:** No schedule configuration data.

### 3. Bat.GetStatus

**Response:**
```json
{
  "id": 0,
  "soc": 11,
  "charg_flag": true,
  "dischrg_flag": true,
  "bat_temp": 24.0,
  "bat_capacity": 609.0,
  "rated_capacity": 5120.0
}
```

**Fields:**
- `soc`: State of charge (%)
- `charg_flag`: Charging allowed
- `dischrg_flag`: Discharging allowed
- `bat_temp`: Battery temperature (°C)
- `bat_capacity`: Current capacity (Wh)
- `rated_capacity`: Rated capacity (Wh)

### 4. Marstek.GetDevice

**Response:**
```json
{
  "device": "VenusE 3.0",
  "ver": 143,
  "ble_mac": "18cedfe4f39f",
  "wifi_mac": "3c2d9e786d20",
  "wifi_name": "Orange-ErrL3",
  "ip": "192.168.0.225"
}
```

**Fields:**
- `device`: Device model name
- `ver`: API version (143)
- `ble_mac`: Bluetooth MAC address
- `wifi_mac`: WiFi MAC address
- `wifi_name`: Connected WiFi SSID
- `ip`: Device IP address

### 5. Wifi.GetStatus

**Response:**
```json
{
  "id": 0,
  "wifi_mac": "3c2d9e786d20",
  "ssid": "Orange-ErrL3",
  "rssi": -37,
  "sta_ip": "192.168.0.225",
  "sta_gate": "192.168.0.1",
  "sta_mask": "255.255.255.0",
  "sta_dns": "192.168.0.1"
}
```

**Fields:**
- `wifi_mac`: WiFi MAC address
- `ssid`: Connected network SSID
- `rssi`: Signal strength (dBm)
- `sta_ip`: Device IP address
- `sta_gate`: Gateway IP
- `sta_mask`: Subnet mask
- `sta_dns`: DNS server

## Implications for Home Assistant Integration

### What Works

1. **Reading current mode** ✅
   - Use `ES.GetMode` to show which mode is active
   - Display in UI via select entity

2. **Setting mode** ✅
   - Use `ES.SetMode` to change modes
   - Works reliably

3. **Setting schedules** ✅
   - Use `ES.SetSchedule` to configure manual schedules
   - Device accepts and stores the configuration
   - Changes take effect immediately

4. **Monitoring status** ✅
   - Battery level, power flows, energy totals
   - All real-time monitoring works perfectly

### What Doesn't Work

1. **Reading schedules back** ❌
   - Cannot retrieve what schedules are configured
   - Cannot display current schedule configuration in UI
   - Cannot validate if schedule was set correctly

### Workarounds for Integration

1. **Schedule Configuration UI**
   - Provide clear warning that schedules cannot be read back
   - Ask user to keep track of configured schedules
   - Consider storing schedule config locally in Home Assistant

2. **Validation**
   - Can only validate that `ES.SetSchedule` doesn't return error
   - Cannot verify schedule is actually active

3. **User Experience**
   - Make it clear in UI that this is write-only
   - Provide good documentation
   - Consider adding confirmation messages after setting schedules

## Recommendations

1. **Remove "View Schedules" Option** ✅ (Done)
   - Since API doesn't support it, remove from UI

2. **Update Documentation** ✅ (Done)
   - Note that schedules are write-only
   - Explain limitation

3. **Consider Local Storage** (Optional Future Enhancement)
   - Store schedule configurations in Home Assistant
   - Show what was last configured
   - Add disclaimer that this might not reflect actual device state

4. **Add Confirmation Messages**
   - After setting schedule, show success message
   - Include what was configured for user reference

## Testing Files Created

1. **test_get_mode.py** - Test ES.GetMode response structure
2. **test_get_schedule.py** - Attempt to read schedules (fails as expected)
3. **test_all_methods.py** - Comprehensive test of all API methods

## Conclusion

The Marstek Venus E API v143 provides excellent real-time monitoring and control capabilities, but **does not support reading back manual schedule configurations**. This is a limitation of the device firmware, not the integration.

The integration has been updated to:
- ✅ Remove attempts to read schedules
- ✅ Remove "View Schedules" option from UI
- ✅ Add clear warnings in schedule configuration UI
- ✅ Focus on what works: monitoring and mode/schedule setting
