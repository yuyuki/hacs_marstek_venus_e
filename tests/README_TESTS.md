# Marstek Venus E - Test Suite

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
