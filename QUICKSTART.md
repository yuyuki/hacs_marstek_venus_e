# Quick Start Guide - Marstek Venus E Home Assistant Integration

## Installation

### 1. Copy Integration to Home Assistant

```bash
# Copy the custom component to your Home Assistant installation
cp -r custom_components/hacs_marstek_venus_e ~/.homeassistant/custom_components/
```

### 2. Restart Home Assistant

After copying the integration files, restart Home Assistant:
- Settings → System → Restart

### 3. Add Integration

1. Settings → Devices & Services
2. Click "Create Automation" or scroll down to find "Marstek Venus E"
3. Click "Marstek Venus E" to add the integration

## Configuration Flow

The integration guides you through 3 steps:

### Step 1: Welcome
- Displays welcome message
- Click "Submit" to proceed

### Step 2: Auto-Discovery (15 seconds)
- System broadcasts UDP discovery probe
- Listens for Marstek devices
- Shows "Discovering devices..."

### Step 3: Device Selection
Two options appear:

**Option A: Select from discovered devices**
- Lists devices found: "Device Name (IP) - MAC: xxxxx"
- Select your device from dropdown
- Click "Submit"

**Option B: Manual IP Entry**
- Select "Enter IP manually" from dropdown
- Click "Submit"
- Enter device IP address
- Click "Submit" again

## What Happens Next

After configuration:
1. Integration creates an entry in Home Assistant
2. Device IP stored in configuration
3. Integration is ready to use

## Testing the Integration

### Run Discovery Test

Test that your device can be discovered:

```bash
cd ~/.homeassistant/custom_components/hacs_marstek_venus_e/../..
python custom_components/hacs_marstek_venus_e/../../../tests/test_discovery.py
```

Expected output:
```
[OK] Discovery completed successfully
[OK] Found 1 device(s)

Real Devices:
Device #1:
  IP Address: 192.168.0.225
  Device Type: VenusE 3.0
  Firmware Ver: 135
```

### Check Home Assistant Logs

For detailed debug information:

1. Settings → System → Logs
2. Search for "marstek"
3. Enable DEBUG logging if needed:

```yaml
# Add to configuration.yaml
logger:
  default: info
  logs:
    custom_components.hacs_marstek_venus_e: debug
    custom_components.hacs_marstek_venus_e.udp_client: debug
```

## Troubleshooting

### Integration Not Showing

**Issue**: "Marstek Venus E" not visible in add integration list

**Solutions**:
1. Verify files copied to correct location: `~/.homeassistant/custom_components/hacs_marstek_venus_e/`
2. Check file permissions (should be readable)
3. Restart Home Assistant completely
4. Check Home Assistant logs for errors

### Discovery Finds No Devices

**Issue**: Discovery runs for 15 seconds but finds no devices

**Possible Causes**:
- Device is powered off
- Device is on different network/WiFi
- Device is on different subnet
- Network firewall blocks UDP port 30000
- Device firmware too old

**Solutions**:
1. Verify device is powered on and connected to WiFi
2. Check device IP address manually
3. Use "Manual IP Entry" option if you know the IP
4. Check network router for port 30000 configuration

### Manual Entry Accepted but Device Not Found

**Note**: Manual IP entry doesn't validate connectivity (device only responds to broadcasts). The connection will be validated when Home Assistant tries to use the integration.

**To verify connectivity**:
1. Run discovery test with specific IP:
   ```bash
   python tests/test_direct_udp.py 192.168.0.225
   ```
2. Check Home Assistant logs for connection errors

### Windows PowerShell Unicode Errors

**Issue**: Unicode characters in test output cause errors

**Solution**: Already fixed in provided test files. If you see:
```
UnicodeEncodeError: 'charmap' codec can't encode character
```

Update your test files to use `[OK]` and `[FAIL]` instead of ✓ and ✗

## Device Information

The integration discovers the following device information:

- **Device Type**: Model name (e.g., "VenusE 3.0")
- **Firmware Version**: Firmware version number
- **BLE MAC**: Bluetooth Low Energy MAC address
- **WiFi MAC**: WiFi MAC address
- **WiFi SSID**: Connected WiFi network name
- **IP Address**: Current device IP address
- **Port**: Communication port (default 30000)

## Network Requirements

### Port 30000
- UDP protocol (not TCP)
- Broadcast and receive on local network
- Must not be blocked by firewall
- Default Marstek communication port

### Network Connectivity
- Device must be on same subnet as Home Assistant
- Both must support UDP broadcasts
- WiFi or Ethernet connection to device

### Broadcast Support
- Router/network must support UDP broadcast
- Some networks have broadcast disabled
- Check network settings if discovery fails

## Features & Capabilities

### Currently Implemented
✓ Device discovery via UDP broadcast
✓ Manual IP entry
✓ Device information retrieval
✓ Configuration storage

### Future Implementation (Sensor Platforms)
- Battery status (power, state of charge)
- WiFi connection info (SSID, signal strength)
- Energy system status (power, energy counters)
- Operating mode
- And more...

## Getting Help

### Enable Debug Logging

```yaml
logger:
  default: info
  logs:
    custom_components.hacs_marstek_venus_e: debug
    custom_components.hacs_marstek_venus_e.udp_client: debug
```

Then check logs for detailed messages:
- Settings → System → Logs
- Search for "marstek" or "discovery"

### Run Diagnostic Tests

```bash
# Full discovery test with network diagnostics
python tests/test_discovery.py

# Direct UDP probe test
python tests/test_direct_udp.py 192.168.0.225
```

### Verify Integration Files

```bash
# Check if all required files are present
python verify_integration.py
```

## Configuration Entry

After adding the integration, Home Assistant stores:

```python
{
    "ip_address": "192.168.0.225",
    "port": 30000,
    "ble_mac": "18cedfe4f39f",
    "timeout": 15.0
}
```

To edit:
1. Settings → Devices & Services → Marstek Venus E
2. Click the entry
3. Click the gear icon to edit

## Next Steps

Once the integration is added:

1. **Monitor Device Status**: Wait for sensor platforms to be implemented
2. **Create Automations**: Set up automations based on device status
3. **Control Device**: Use service calls to set mode, schedules, etc.

## Documentation

For more detailed information:
- **INTEGRATION_GUIDE.md** - Complete technical documentation
- **PROJECT_SUMMARY.md** - Project architecture and implementation details

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review Home Assistant logs with debug enabled
3. Run diagnostic tests (test_discovery.py)
4. Check device is properly configured and powered on

---

**Version**: 1.0.0  
**Home Assistant Version**: 2025.11.0+  
**Device**: Marstek Venus E (Firmware v135+)
