# GitHub Copilot Instructions for Marstek Venus E Integration

## Target Environment

### Home Assistant Configuration
- **Installation Method**: Home Assistant OS
- **Core Version**: 2025.11.3
- **Supervisor Version**: 2025.11.5
- **Operating System**: 16.3
- **Frontend Version**: 20251105.1

### Python Environment
- **Python Version**: 3.12+ (Home Assistant 2025.11+ requirement)
- **Integration Type**: Custom Component (HACS compatible)
- **API Protocol**: UDP JSON-RPC (port 30000)

### lOCAL Api Details
The integration is based on the version 1.0 (2025-08-09)

## Project Overview

This is a Home Assistant custom integration for the **Marstek Venus E** battery energy storage system. It provides local control and monitoring via UDP communication.

### Key Features
- Automatic device discovery via UDP broadcast
- Real-time battery, solar PV, and grid monitoring
- Operating mode control (Auto, AI, Manual, Passive)
- Schedule configuration for charging/discharging
- Energy dashboard integration
- Multi-language support (English, French)

## Code Architecture

### Core Components

1. **`__init__.py`** - Integration setup and coordinator initialization
2. **`config_flow.py`** - Configuration UI and options flow
3. **`coordinator.py`** - DataUpdateCoordinator for periodic data fetching
4. **`udp_client.py`** - UDP communication with Marstek device
5. **Platform files**:
   - `sensor.py` - Sensor entities (battery, PV, grid, energy)
   - `binary_sensor.py` - Binary sensors (charging, discharging, CT status)
   - `select.py` - Mode selection entity
   - `button.py` - Action buttons
6. **`services.py`** - Service implementations
7. **`const.py`** - Constants and configuration
8. **`translations/`** - Language files for localization
9. **`tests/`** - Unit and integration tests
10. **`doc/`** - Documentation files
11. **`readme.md`** - User-facing documentation

### Important Patterns

#### Async/Await
- All I/O operations must be async
- Use `asyncio` for concurrent operations
- Never block the event loop

#### Coordinator Pattern
```python
# Entities should extend CoordinatorEntity
class MarstekSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, description):
        super().__init__(coordinator)
        self.entity_description = description
```

## Guidelines for Integration Development

### General instructions to follow

#### General purpose
As the local API of the Marstek Venus E device is not really stable. respect the following guidelines when developing or extending this integration:
- 30 secondes between each UDP request
- 30 secondes timeout for UDP requests
- Retry up to 3 times on timeout errors
- Log payload and response for debugging purposes
- Respect the protocol explained here
- Do not log error for timeouts, only debug log
- Log payload and response in case of errors

#### Protocol Handling
The integration uses UDP communication with JSON-RPC, ensure that all interactions with the device are handled asynchronously to avoid blocking the Home Assistant event loop. Use the DataUpdateCoordinator pattern to manage periodic data fetching and state updates for entities.

## Protocol description

### Marstek.GetDevice
To discover Marstek devices within the LAN, a UDP broadcast is utilized. The broadcast content 
is as follows:

Payload:
```json
{
    "id": 0,
    "method": "Marstek.GetDevice", 
    "params": {
        "ble_mac":"0" 
    }
}
```

Response (sample):
```json
{
    "id": 0,                      // = device_id : An identifier established by the Client.
    "src": "VenusC-123456789012", 
    "result": {
        "device":"VenusC", 
        "ver":111, 
        "ble_mac":"123456789012", // = ble_mac : Bluetooth MAC address of the device
        "wifi_mac":"123456789012", 
        "wifi_name":"MY_HOME", 
        "ip":"192.168.1.11"
    }
}
```

Important :
- the device_id must be reuse to ALL others calls to the device. It's its identifier. If we have several devices, each one will have its own device_id.
- the ble_mac in the request is used to filter the response. If set to "0", all devices will respond. It must be saved for later calls.

### Marstek.GetDevice 
It locates Marstek devices on the local area network and get these information: Device model, firmware version, Bluetooth MAC addresses, WiFi MAC address, WiFi name, Device IP.
```json
{
    "id": 0,                      // = 0 (need to ensure it's always 0 for this method)
    "method": "Marstek.GetDevice", 
    "params": {
        "ble_mac":"123456789012"  // = ble_mac : it must be the ble_mac retrieved during the discovery
    }
}
```

Response (sample):
```json
{
    "id": 0,
    "src": "VenusC-123456789012", 
    "result": {
        "device":"VenusC", 
        "ver":111, 
        "ble_mac":"123456789012", 
        "wifi_mac":"012123456789", 
        "wifi_name"："MY_HOME", 
        "ip":"192.168.1.11"
    }
}
```

### Wifi.GetStatus

### BLE.GetStatus

### Bat.GetStatus

### PV.GetStatus 

### ES.GetStatus 

### ES.SetMode 

### ES.GetMode

### EM.GetStatus

#### Entity Naming
- Use descriptive unique_id: `f"{device_sn}_{sensor_type}"`
- Translation keys in `strings.json` and `translations/`
- Device class and state class for proper categorization

## Coding Standards

### Home Assistant Best Practices

1. **Entity Categories**: Use appropriate device classes
   - Battery: `DEVICE_CLASS_BATTERY`, `STATE_CLASS_MEASUREMENT`
   - Energy: `DEVICE_CLASS_ENERGY`, `STATE_CLASS_TOTAL_INCREASING`
   - Power: `DEVICE_CLASS_POWER`, `STATE_CLASS_MEASUREMENT`

2. **Units**: Use Home Assistant constants
   ```python
   from homeassistant.const import (
       UnitOfPower.WATT,
       UnitOfEnergy.KILO_WATT_HOUR,
       PERCENTAGE,
   )
   ```

3. **Error Handling**:
   ```python
   try:
       result = await self.coordinator.api.some_method()
   except Exception as err:
       _LOGGER.error("Failed to execute: %s", err)
       raise HomeAssistantError(f"Operation failed: {err}")
   ```

4. **Logging**: Use module-level logger
   ```python
   _LOGGER = logging.getLogger(__name__)
   _LOGGER.debug("Debug message")
   _LOGGER.info("Info message")
   _LOGGER.error("Error message")
   ```

5. **Configuration Validation**:
   - Use `vol` (voluptuous) for schema validation
   - Validate user input in config flow
   - Provide helpful error messages

### UDP Communication

The `udp_client.py` implements JSON-RPC over UDP:

```python
# Request format
{
    "id": 0,             // device_id : An identifier established by the Client.
    "method": "string",  // Marstek.GetDevice | ES.GetStatus | ES.SetMode
    "params": {
        "id":0 
    }
}

# Response format
{
    "id": 0,            // device_id : An identifier established by the Client.
    "method": "string",
    "params": {
       
    }
}
```

**Important UDP Methods**:


### Testing

Tests are in the `tests/` directory:
- Use pytest for unit tests
- Test UDP communication independently
- Mock the coordinator for entity tests
- Include integration tests for full flows

## Common Tasks

### Adding a New Sensor

1. Define entity description in platform file:
```python
SENSOR_DESCRIPTIONS = [
    SensorEntityDescription(
        key="battery_soc",
        name="Battery State of Charge",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
]
```

2. Extract value in `_extract_value()` method:
```python
def _extract_value(self, data: dict) -> StateType:
    if self.entity_description.key == "battery_soc":
        return data.get("soc")
```

3. Add translation in `strings.json` and `translations/en.json`

### Adding a New Service

1. Define in `services.yaml`:
```yaml
set_mode:
  name: Set Operating Mode
  description: Change the operating mode
  fields:
    mode:
      description: Operating mode
      example: "Auto"
      required: true
      selector:
        select:
          options:
            - "Auto"
            - "AI"
            - "Manual"
            - "Passive"
```

2. Implement in `services.py`:
```python
async def async_set_mode(call: ServiceCall) -> None:
    mode = call.data.get("mode")
    api = hass.data[DOMAIN][entry.entry_id]["api"]
    await api.set_mode(mode)
```

3. Register in `__init__.py`:
```python
hass.services.async_register(
    DOMAIN,
    "set_mode",
    async_set_mode,
    schema=SERVICE_SET_MODE_SCHEMA,
)
```

### Updating Translations

Update all language files:
- `strings.json` (base)
- `translations/en.json` (English)
- `translations/fr.json` (French)

Maintain consistency across all translation files.

## Device-Specific Information

### Operating Modes
- **Auto (Self-Consuming)**: Optimize self-consumption
- **AI**: Intelligent mode based on patterns
- **Manual**: Time-based schedules (up to 4 slots)
- **Passive**: Fixed power target

### Schedule Configuration
- 0-10 time slots available
- Week bitmask (1=Mon, 2=Tue, 4=Wed, 8=Thu, 16=Fri, 32=Sat, 64=Sun, 127=All days)
- Power: negative = charge, positive = discharge with a range of 100-800W
- Time format: "HH:MM" with startTime < endTime
- Enable/Disable each slot individually

### API Quirks
- UDP responses may timeout - implement retry logic
- Device may not respond immediately after mode change
- Some features require specific firmware versions
- CT meter sensors only available if hardware installed

## Security Considerations

- UDP communication is unencrypted (local network only)
- No authentication required by device
- Validate all user input
- Sanitize data from device responses
- Use private network only - not exposed to internet

## Performance Guidelines

- Update interval: 5 seconds (configurable via SCAN_INTERVAL)
- Batch UDP requests when possible
- Use coordinator to prevent duplicate requests
- Implement exponential backoff on errors
- Cache device info (SN, model, firmware)

## Dependencies

From `manifest.json`:
```json
{
  "domain": "hacs_marstek_venus_e",
  "name": "Marstek Venus E",
  "version": "1.0.0",
  "documentation": "https://github.com/yuyuki/hacs_marstek_venus_e",
  "requirements": [],
  "dependencies": [],
  "codeowners": ["@yuyuki"],
  "iot_class": "local_polling"
}
```

- No external Python dependencies
- Uses built-in `asyncio`, `socket`, `json`
- Home Assistant core >= 2025.11.0

## Documentation Files

- `README.md` - User-facing documentation
- `INTEGRATION_GUIDE.md` - Detailed integration guide
- `PROJECT_SUMMARY.md` - Project overview
- `API_TEST_RESULTS.md` - API testing results
- `TEST_STATUS.md` - Current test status
- Feature-specific docs in root directory

## Debugging Tips

Enable debug logging:
```yaml
logger:
  default: info
  logs:
    custom_components.hacs_marstek_venus_e: debug
```

Common issues:
- UDP timeout: Check network connectivity and firewall
- Discovery fails: Try manual IP entry
- Entities unavailable: Check coordinator update errors
- Schedule not working: Verify device is in Manual mode

## Future Enhancements

Consider when implementing new features:
- Energy storage optimization algorithms
- Grid pricing integration
- Weather-based charging strategies
- Battery health monitoring
- Firmware update notifications
- Multi-device support
- WebSocket support (if API evolves)

## References

- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [HACS Documentation](https://hacs.xyz/)
- [Home Assistant Architecture](https://developers.home-assistant.io/docs/architecture_index)
- [Integration Quality Scale](https://developers.home-assistant.io/docs/integration_quality_scale_index)

---

**When working on this project, always prioritize:**
1. Home Assistant compatibility
2. Async/non-blocking operations
3. Proper error handling
4. User-friendly error messages
5. Complete translations
6. Test coverage
7. Documentation updates
