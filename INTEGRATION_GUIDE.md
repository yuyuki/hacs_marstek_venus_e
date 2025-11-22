# Marstek Venus E Home Assistant Integration Guide

## Overview

This is a Home Assistant custom integration for the Marstek Venus E battery management system. It allows you to monitor and control your Marstek Venus E device directly from Home Assistant using UDP communication over your local network.

## Device Compatibility

- **Tested Device**: Marstek Venus E 3.0 (Firmware v135+)
- **Communication**: UDP JSON-RPC over port 30000
- **Network**: Requires local network access (broadcasts to discover, does not require internet)

## Features

### Discovery
- **Automatic Device Discovery**: The integration automatically broadcasts on your local network to find connected Marstek devices
- **Manual IP Entry**: Option to manually enter device IP address if automatic discovery fails
- **Device Information**: Shows device model, WiFi SSID, MAC addresses, and firmware version

### Configuration Flow

The integration uses a 3-step setup process:

1. **Welcome Step** (`user`): User initiates the setup
2. **Discovery Step** (`discovery`): System broadcasts UDP discovery probes to find devices on the local network (15-second timeout)
3. **Device Selection** (`select_device`): User selects from discovered devices or chooses manual IP entry

### Device Communication

The integration communicates with the device using JSON-RPC formatted messages over UDP:

**Discovery Probe Format**:
```json
{
  "id": 0,
  "method": "Marstek.GetDevice",
  "params": {"ble_mac": "0"}
}
```

**Request Format** (for future sensor implementations):
```json
{
  "id": 1,
  "method": "Bat.GetStatus",
  "params": {"id": 0}
}
```

## Implementation Details

### Discovery Mechanism

The discovery process (`MarstekUDPClient.discover()`):

1. Creates a UDP socket bound to port 30000 (listening port)
2. Enables broadcasting with `SO_BROADCAST` socket option
3. Sends discovery probe every 2 seconds for 15 seconds
4. Listens for responses with 1-second receive timeout
5. Returns list of (ip, port, device_info) tuples

**Key Implementation Details**:
- Socket **must** bind to the listening port (port 30000), not ephemeral port
- Discovery probes **must** be sent repeatedly every 2 seconds (single probe doesn't work)
- Socket options `SO_REUSEADDR` and `SO_REUSEPORT` improve behavior
- Standard `socket` module works better than `asyncio.create_datagram_endpoint` for discovery

### Device Response Format

The device responds to discovery probes with:

```json
{
  "id": 0,
  "src": "VenusE 3.0-18cedfe4f39f",
  "result": {
    "device": "VenusE 3.0",
    "ver": 135,
    "ble_mac": "18cedfe4f39f",
    "wifi_mac": "3c2d9e786d20",
    "wifi_name": "Orange-ErrL3",
    "ip": "192.168.0.225"
  }
}
```

### Important Notes

1. **Broadcast-Only Communication**: Marstek devices ONLY respond to UDP broadcasts. They do NOT respond to unicast requests to their IP address. This is a hardware limitation.

2. **No Unicast Connection Validation**: Because the device doesn't respond to unicast requests, the integration cannot validate connectivity by sending a direct request. Connectivity is verified through successful discovery probe responses.

3. **Echo Responses**: Discovery may receive echo responses from the local machine (localhost). These are filtered by checking for `"result"` or `"src"` fields in the response.

## Files Modified

### Core Integration Files

- **`custom_components/hacs_marstek_venus_e/udp_client.py`**
  - `MarstekUDPClient` class for UDP JSON-RPC communication
  - Static method `discover()` for device discovery
  - Methods for future sensor implementations

- **`custom_components/hacs_marstek_venus_e/config_flow.py`**
  - Multi-step configuration flow
  - Device discovery and selection UI
  - Manual IP entry fallback

- **`custom_components/hacs_marstek_venus_e/strings.json`**
  - UI text for all configuration steps

### Test Files

- **`tests/test_discovery.py`**
  - Comprehensive test for discovery mechanism
  - Network diagnostics
  - Device information display

- **`tests/test_direct_udp.py`**
  - Direct UDP probe testing
  - Raw response inspection

## Testing

### Run Discovery Test

```bash
cd e:\Projets\hacs_marstek_venus_e
python tests/test_discovery.py
```

This will:
1. Check network configuration
2. Perform device discovery (15-second broadcast)
3. Display all discovered devices with details
4. Show connectivity status

### Expected Output

```
============================================================
MARSTEK VENUS E - DISCOVERY & CONNECTION TEST
============================================================

============================================================
NETWORK CONFIGURATION CHECK
============================================================
[OK] Hostname: your-hostname
[OK] Local IP: 192.168.0.x
[OK] UDP Broadcast socket: OK (bound to port xxxxx)
[OK] UDP Broadcast send: OK (sent to 255.255.255.255:30000)

============================================================
TEST 1: Device Discovery
============================================================
[OK] Discovery completed successfully
[OK] Found X device(s)

Real Devices:
------------------------------------------------------------

Device #1:
  IP Address: 192.168.0.225
  Port: 30000
  Device Type: VenusE 3.0
  MAC Address: 18cedfe4f39f
  WiFi SSID: Orange-ErrL3
  Firmware Ver: 135

[OK] Discovery: PASSED
[OK] Connection: PASSED
[OK] Battery Info: PASSED

All critical tests completed successfully!
```

## Troubleshooting

### Discovery Returns No Devices

**Possible Causes**:
1. Device is not powered on
2. Device is on a different subnet/network
3. Device is not configured to be discoverable
4. Firewall or network configuration blocks UDP broadcast on port 30000

**Solutions**:
- Verify device is powered on and connected to same WiFi network
- Check device WiFi settings
- Try manual IP entry if you know the device IP
- Check firewall/network settings for UDP port 30000

### Manual IP Entry Doesn't Work

**Note**: The integration cannot validate unicast connection because Marstek devices only respond to broadcasts. Manual entry will accept any IP address and report success, with actual validation happening when the integration runs.

### Network Issues

Run network diagnostics:
```bash
python tests/test_discovery.py
```

This shows detailed network configuration and UDP capabilities.

## Future Implementation

### Planned Sensor Types

Once configured, the integration can be extended to add sensors for:

- **Battery Status** (`Bat.GetStatus`)
  - Battery power (W)
  - State of charge (%)
  - Status (charging/discharging/idle)

- **WiFi Status** (`Wifi.GetStatus`)
  - SSID
  - Signal strength (RSSI)
  - IP address, gateway, DNS

- **Energy System Status** (`ES.GetStatus`)
  - Grid power
  - Load power
  - Total energy counters

- **Operating Mode** (`ES.GetMode`)
  - Current mode (Auto/Manual/Passive/AI)

### Implementation Pattern

New methods in `MarstekUDPClient` should follow this pattern:

```python
async def get_battery_status(self) -> dict[str, Any]:
    """Get battery status."""
    return await self._send_request("Bat.GetStatus", {"id": 0})
```

Note: Methods use the Marstek.* naming convention in requests, not get_* naming.

## Architecture

### Configuration Entry

The integration stores configuration with the following data:
- `CONF_IP_ADDRESS`: Device IP address
- `CONF_PORT`: UDP port (default: 30000)
- `CONF_BLE_MAC`: Device BLE MAC address (optional)
- `CONF_TIMEOUT`: Request timeout in seconds (default: 15.0)

### Data Flow

1. **User initiates setup** → `async_step_user()`
2. **System discovers devices** → `async_step_discovery()` → `MarstekUDPClient.discover()`
3. **User selects device** → `async_step_select_device()`
4. **Configuration saved** → Entry created in Home Assistant

### Coordinator Pattern

Future implementation should use Home Assistant's `DataUpdateCoordinator` for periodic data updates:

```python
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

coordinator = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name="Marstek Venus E",
    update_method=async_update_data,
    update_interval=timedelta(seconds=30),
)
```

## References

- **Marstek API Documentation**: Uses JSON-RPC 2.0 format
- **UDP Discovery Protocol**: Broadcast on port 30000 with discovery probe
- **Device Response Format**: JSON-RPC responses with result/error/src fields

## Notes for Developers

1. **Socket Binding**: Discovery socket MUST bind to `("", port)` not `("0.0.0.0", 0)`
2. **Repeated Broadcasting**: Send probes every 2 seconds, not just once
3. **Response Filtering**: Check for "result" or "src" fields to filter real responses from echoes
4. **No Unicast**: Don't attempt to send unicast requests to device IP - they won't respond
5. **Logging**: Enable DEBUG logging to see probe details: `logger: {default: info, custom_components.hacs_marstek_venus_e: debug}`

