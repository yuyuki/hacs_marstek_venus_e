# Marstek Venus E - Test Suite

This directory contains test scripts for verifying the Marstek Venus E API functions and integration functionality.

## Test Files Overview

### Individual API Function Tests (Recommended)

Each test file focuses on a specific API function for easier debugging and validation:

- **`test_marstek_get_device.py`** - Device discovery via UDP broadcast
- **`test_es_get_status.py`** - Energy system status retrieval
- **`test_es_get_mode.py`** - Operating mode retrieval

### Comprehensive Tests

- **`test_api_functions.py`** - Runs all API tests in sequence
- **`test_discovery.py`** - Legacy discovery test with network diagnostics
- **`test_discovery_simple.py`** - Simple discovery test
- **`test_direct_udp.py`** - Low-level UDP communication test

## Quick Start

### 1. Test Device Discovery

First, verify your device can be discovered on the network:

```bash
python tests/test_marstek_get_device.py
```

This will find all Marstek Venus E devices on your local network and display their details.

### 2. Test Energy Status (ES.GetStatus)

Once you have the device IP, test energy system status retrieval:

```bash
python tests/test_es_get_status.py --ip 192.168.0.225
```

Or let it discover automatically:

```bash
python tests/test_es_get_status.py
```

### 3. Test Operating Mode (ES.GetMode)

Test retrieving the current operating mode:

```bash
python tests/test_es_get_mode.py --ip 192.168.0.225
```

### 4. Run All Tests

To run all API tests in sequence:

```bash
python tests/test_api_functions.py --ip 192.168.0.225
```

## Detailed Test Documentation

### test_marstek_get_device.py

Tests the `Marstek.GetDevice` API method for device discovery.

**Usage:**
```bash
# Run with default 15-second timeout
python tests/test_marstek_get_device.py

# Run with custom timeout
python tests/test_marstek_get_device.py --timeout 20

# Show help
python tests/test_marstek_get_device.py --help
```

**What it tests:**
- UDP broadcast discovery on port 30000
- Device response parsing
- Device information extraction (IP, BLE MAC, WiFi MAC, SSID, firmware version)

**Expected output:**
- Device IP address
- Device type (e.g., "VenusE 3.0")
- Firmware version (e.g., 143 for API v1.4.3)
- Network information

---

### test_es_get_status.py

Tests the `ES.GetStatus` API method for retrieving energy system status.

**Usage:**
```bash
# Test with specific IP
python tests/test_es_get_status.py --ip 192.168.0.225

# Auto-discover and test
python tests/test_es_get_status.py

# Custom timeout
python tests/test_es_get_status.py --ip 192.168.0.225 --timeout 10

# Show help
python tests/test_es_get_status.py --help
```

**What it tests:**
- Energy system status retrieval via unicast UDP
- Battery state of charge (SOC)
- Battery capacity (Wh)
- Battery power (W)
- PV power generation (W)
- Grid power (import/export)
- Total energy metrics (kWh)

**Expected output:**
- Battery SOC percentage
- Current battery capacity
- PV power generation
- Grid power flow
- Total energy counters

---

### test_es_get_mode.py

Tests the `ES.GetMode` API method for retrieving the current operating mode.

**Usage:**
```bash
# Test with specific IP
python tests/test_es_get_mode.py --ip 192.168.0.225

# Auto-discover and test
python tests/test_es_get_mode.py

# Custom timeout
python tests/test_es_get_mode.py --ip 192.168.0.225 --timeout 10

# Show help
python tests/test_es_get_mode.py --help
```

**What it tests:**
- Operating mode retrieval (Auto, AI, Manual, Passive)
- CT meter status and power readings
- Mode-specific configuration
- Additional status metrics

**Expected output:**
- Current operating mode
- Battery SOC
- Power metrics
- CT meter status (if installed)
- Mode-specific configuration (for Manual/Passive modes)

---

## API Functions Reference

| API Method | Test File | Description | Status |
|------------|-----------|-------------|--------|
| `Marstek.GetDevice` | test_marstek_get_device.py | Device discovery via broadcast | ✓ Tested |
| `ES.GetStatus` | test_es_get_status.py | Energy system status | ✓ Tested |
| `ES.GetMode` | test_es_get_mode.py | Operating mode | ✓ Tested |
| `ES.SetMode` | - | Change operating mode | Not tested (write operation) |
| `Bat.GetStatus` | - | Battery detailed status | Available in client |
| `Wifi.GetStatus` | - | WiFi connection status | Available in client |
| `ES.SetSchedule` | - | Configure manual schedule | Available in client |
| `ES.GetSchedule` | - | Get schedule configuration | Available in client |
| `ES.SetPassiveMode` | - | Set passive mode | Available in client |

## Running Discovery & Connection Tests

A standalone test script is available to verify that the discovery and UDP communication works correctly, without requiring a full Home Assistant installation.

### Prerequisites

- Python 3.8+
- The `udp_client.py` module

### Test Script: `test_discovery.py`

This script tests:
1. **Device Discovery** - Sends a broadcast probe and listens for device responses
2. **Device Connection** - Connects to a discovered device and requests real-time data
3. **Battery Info** - Requests battery information from the device

#### Running the Tests

**Test 1: Auto-Discovery (find devices on the network)**

```bash
python tests/test_discovery.py
```

This will:
- Send a discovery probe to broadcast address `255.255.255.255:30000`
- Wait 3 seconds for device responses
- Display any found devices with their details (IP, MAC, device type, firmware version)
- Automatically test connection to the first discovered device
- Test battery information request

**Test 2: Manual IP Test (test connection to a known IP)**

If you know the device IP address but auto-discovery didn't work:

```bash
python tests/test_discovery.py --ip 192.168.0.225
```

Replace `192.168.0.225` with your actual device IP.

### Output Examples

#### Successful Discovery
```
============================================================
TEST 1: Device Discovery
============================================================
✓ Discovery completed successfully
✓ Found 1 device(s)

Device Details:
  IP Address: 192.168.0.225
  Port: 30000
  Device Type: Venus E
  MAC Address: 123456789012
  WiFi SSID: MY_HOME
  Firmware Ver: 111
```

#### Successful Connection
```
============================================================
TEST 2: Connection Test to 192.168.0.225:30000
============================================================
✓ Successfully received real-time data!

Response Data:
{
  "battery_soc": 85,
  "battery_power": 500,
  ...
}
```

#### Connection Timeout
```
✗ Request timed out after 15 seconds
  The device did not respond in time.
  Check:
  - Device IP address is correct (192.168.0.225)
  - Device is powered on and connected to network
  - Device is listening on port 30000
  - Network allows UDP traffic
```

### Troubleshooting

#### "No devices found" after running discovery

This is normal if:
- No Marstek Venus E devices are on the network
- The device is powered off
- The device is on a different network/subnet/VLAN
- Your network/firewall blocks UDP broadcast on port 30000
- The device is not responding to `Marstek.GetDevice` RPC calls

**Solutions:**
1. Verify the device is powered on and connected to WiFi
2. Check the device's IP address using the Marstek app or your router
3. Use the `--ip` flag to test a known device IP
4. Check firewall/network settings for UDP broadcast restrictions

#### Timeout when connecting to device IP

The UDP request takes too long to complete. This can happen if:
- The device is offline or unreachable
- Network latency is very high
- The device firmware doesn't respond to `get_realtime_data` RPC calls
- Firewall is blocking UDP replies

**Solutions:**
1. Ping the device to verify connectivity: `ping 192.168.0.225`
2. Check device logs/status in the Marstek app
3. Verify device firmware version supports the RPC method
4. Check network firewall rules for UDP traffic

#### Device found but connection fails

The device was discovered but doesn't respond to data requests. This may indicate:
- Device firmware doesn't support the `get_realtime_data` method
- Device is in a state where it can't respond to requests

**Next steps:**
- Check device status in the Marstek app
- Review device documentation for supported RPC methods
- Check Home Assistant logs for more detailed error information

### Using Test Results in Home Assistant

Once you've verified the test passes:

1. If auto-discovery found your device, add the integration and it should work automatically
2. If you had to use `--ip`, try the manual IP entry during integration setup
3. Enable debug logging in Home Assistant to see detailed connection logs:
   ```yaml
   logger:
     default: info
     logs:
       custom_components.marstek_venus_e: debug
   ```

### Debug Output

For detailed debugging, the test script will print:
- All discovery probes sent
- All device responses received
- UDP connection details
- Full exception tracebacks if errors occur

All of this information is also logged in Home Assistant's logs when debug mode is enabled.
