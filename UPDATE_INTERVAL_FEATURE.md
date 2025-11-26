# Update Interval Configuration Feature

## Overview
Added a new configuration option to the integration's options menu that allows users to configure the polling interval (how often the integration fetches data from the Marstek Venus E device).

## Changes Made

### 1. Configuration Flow (`config_flow.py`)
- **Modified `async_step_init()`**: Changed from directly showing the manual mode configuration to displaying a menu with two options:
  - Configure Manual Mode Schedule
  - Configure Update Interval
  
- **Added `async_step_configure_update_interval()`**: New step that allows users to set the polling interval in minutes (range: 1-60 minutes)
  - Stores the interval in the config entry options
  - Updates the coordinator's update interval dynamically
  - Converts minutes to seconds for internal use

### 2. Data Coordinator (`coordinator.py`)
- **Modified `__init__()`**: Updated initialization to read the custom scan interval from config entry options
  - Checks if a custom scan interval is set (stored in minutes)
  - Converts minutes to seconds for the coordinator
  - Falls back to `DEFAULT_SCAN_INTERVAL` if no custom interval is set

### 3. Constants (`const.py`)
- **Added `CONF_SCAN_INTERVAL`**: New constant for storing the scan interval configuration key

### 4. Translations
Updated all translation files to support the new menu and configuration step:

#### `strings.json` (default)
- Updated menu options
- Added translations for the update interval configuration step

#### `translations/en.json` (English)
- Updated menu options
- Added translations for the update interval configuration step

#### `translations/fr.json` (French)
- Updated menu options  
- Added French translations for the update interval configuration step

## User Experience

### Before
When clicking the configuration wheel, users were directly taken to the manual mode schedule configuration.

### After
When clicking the configuration wheel, users now see a menu with two options:
1. **Configure Manual Mode Schedule**: Configure charging/discharging schedules (existing functionality)
2. **Configure Update Interval**: Set how often (in minutes) the integration polls the device for data

## Technical Details

### Storage
- The scan interval is stored in `config_entry.options[CONF_SCAN_INTERVAL]`
- Value is stored in **minutes** for user-friendliness
- Internally converted to **seconds** for the coordinator

### Default Values
- Default scan interval: 5 seconds (from `DEFAULT_SCAN_INTERVAL` constant)
- User can configure: 1-60 minutes (60-3600 seconds)

### Update Behavior
- When a user changes the interval, it's immediately applied to the coordinator
- No restart required - the change takes effect for the next update cycle

## Benefits
1. **Flexibility**: Users can now balance between real-time updates and network traffic
2. **User-friendly**: Configuration in minutes is more intuitive than seconds
3. **No restart needed**: Changes apply immediately
4. **Proper separation**: Configuration is separate from schedule management

## Example Usage
1. Click on the integration's configuration wheel
2. Select "Configure Update Interval"
3. Enter desired interval (e.g., 5 minutes)
4. Click Submit
5. The integration will now poll every 5 minutes instead of the default 5 seconds

## Notes
- Lower intervals provide more real-time data but increase network traffic
- Higher intervals reduce network traffic but data updates less frequently
- The minimum interval is 1 minute to prevent excessive polling
- The maximum interval is 60 minutes to ensure regular updates
