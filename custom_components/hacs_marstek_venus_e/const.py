"""Constants for the Marstek Venus E integration."""
from typing import Final

DOMAIN: Final = "hacs_marstek_venus_e"

# Device Configuration
DEFAULT_PORT: Final = 30000
DEFAULT_SCAN_INTERVAL: Final = 5  # seconds

# Modes
MODE_AUTO: Final = "Auto"
MODE_AI: Final = "AI"
MODE_MANUAL: Final = "Manual"
MODE_PASSIVE: Final = "Passive"

VALID_MODES: Final = [MODE_AUTO, MODE_AI, MODE_MANUAL, MODE_PASSIVE]

# API Methods
API_GET_REALTIME_DATA: Final = "get_realtime_data"
API_GET_BATTERY_INFO: Final = "get_battery_info"
API_SET_MODE: Final = "set_mode"
API_SET_MANUAL_SCHEDULE: Final = "set_manual_schedule"
API_SET_PASSIVE_MODE: Final = "set_passive_mode"
API_GET_SCHEDULE: Final = "get_schedule"

# Battery Attributes
ATTR_BATTERY_SOC: Final = "battery_soc"
ATTR_BATTERY_TEMPERATURE: Final = "battery_temperature"
ATTR_BATTERY_CAPACITY: Final = "battery_capacity"
ATTR_BATTERY_RATED_CAPACITY: Final = "battery_rated_capacity"
ATTR_BATTERY_POWER: Final = "battery_power"
ATTR_BATTERY_CHARGING: Final = "battery_charging"
ATTR_BATTERY_DISCHARGING: Final = "battery_discharging"

# PV Attributes
ATTR_PV_POWER: Final = "pv_power"
ATTR_PV_VOLTAGE: Final = "pv_voltage"
ATTR_PV_CURRENT: Final = "pv_current"

# Grid Attributes
ATTR_GRID_POWER: Final = "grid_power"
ATTR_OFFGRID_POWER: Final = "offgrid_power"

# Energy Attributes
ATTR_TOTAL_PV_ENERGY: Final = "total_pv_energy"
ATTR_TOTAL_GRID_EXPORT_ENERGY: Final = "total_grid_export_energy"
ATTR_TOTAL_GRID_IMPORT_ENERGY: Final = "total_grid_import_energy"
ATTR_TOTAL_LOAD_ENERGY: Final = "total_load_energy"

# CT Meter Attributes
ATTR_PHASE_A_POWER: Final = "phase_a_power"
ATTR_PHASE_B_POWER: Final = "phase_b_power"
ATTR_PHASE_C_POWER: Final = "phase_c_power"
ATTR_TOTAL_CT_POWER: Final = "total_ct_power"
ATTR_CT_METER_CONNECTED: Final = "ct_meter_connected"

# WiFi Attributes
ATTR_WIFI_SIGNAL_STRENGTH: Final = "wifi_signal_strength"
ATTR_WIFI_SSID: Final = "wifi_ssid"

# Operating Mode
ATTR_OPERATING_MODE: Final = "operating_mode"

# Sensors Configuration
SENSORS_BATTERY: Final = {
    "battery_state_of_charge": {
        "name": "Battery State of Charge",
        "unit": "%",
        "icon": "mdi:battery-percent",
        "device_class": "battery",
        "attr": ATTR_BATTERY_SOC,
    },
    "battery_temperature": {
        "name": "Battery Temperature",
        "unit": "°C",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
        "attr": ATTR_BATTERY_TEMPERATURE,
    },
    "battery_capacity": {
        "name": "Battery Capacity",
        "unit": "Wh",
        "icon": "mdi:battery-heart",
        "device_class": "energy",
        "attr": ATTR_BATTERY_CAPACITY,
    },
    "battery_rated_capacity": {
        "name": "Battery Rated Capacity",
        "unit": "Wh",
        "icon": "mdi:battery-heart",
        "device_class": "energy",
        "attr": ATTR_BATTERY_RATED_CAPACITY,
    },
    "battery_power": {
        "name": "Battery Power",
        "unit": "W",
        "icon": "mdi:battery-charging",
        "device_class": "power",
        "attr": ATTR_BATTERY_POWER,
    },
}

SENSORS_PV: Final = {
    "pv_power": {
        "name": "PV Power",
        "unit": "W",
        "icon": "mdi:solar-power",
        "device_class": "power",
        "attr": ATTR_PV_POWER,
    },
    "pv_voltage": {
        "name": "PV Voltage",
        "unit": "V",
        "icon": "mdi:lightning-bolt",
        "device_class": "voltage",
        "attr": ATTR_PV_VOLTAGE,
    },
    "pv_current": {
        "name": "PV Current",
        "unit": "A",
        "icon": "mdi:current-ac",
        "device_class": "current",
        "attr": ATTR_PV_CURRENT,
    },
}

SENSORS_GRID: Final = {
    "grid_power": {
        "name": "Grid Power",
        "unit": "W",
        "icon": "mdi:transmission-tower",
        "device_class": "power",
        "attr": ATTR_GRID_POWER,
    },
    "offgrid_power": {
        "name": "Off-Grid Power",
        "unit": "W",
        "icon": "mdi:power-off",
        "device_class": "power",
        "attr": ATTR_OFFGRID_POWER,
    },
}

SENSORS_ENERGY: Final = {
    "total_pv_energy": {
        "name": "Total PV Energy",
        "unit": "kWh",
        "icon": "mdi:solar-power-box",
        "device_class": "energy",
        "state_class": "total_increasing",
        "attr": ATTR_TOTAL_PV_ENERGY,
    },
    "total_grid_export_energy": {
        "name": "Total Grid Export Energy",
        "unit": "kWh",
        "icon": "mdi:transmission-tower-export",
        "device_class": "energy",
        "state_class": "total_increasing",
        "attr": ATTR_TOTAL_GRID_EXPORT_ENERGY,
    },
    "total_grid_import_energy": {
        "name": "Total Grid Import Energy",
        "unit": "kWh",
        "icon": "mdi:transmission-tower-import",
        "device_class": "energy",
        "state_class": "total_increasing",
        "attr": ATTR_TOTAL_GRID_IMPORT_ENERGY,
    },
    "total_load_energy": {
        "name": "Total Load Energy",
        "unit": "kWh",
        "icon": "mdi:home-lightning-bolt",
        "device_class": "energy",
        "state_class": "total_increasing",
        "attr": ATTR_TOTAL_LOAD_ENERGY,
    },
}

SENSORS_CT: Final = {
    "phase_a_power": {
        "name": "Phase A Power",
        "unit": "W",
        "icon": "mdi:lightning-bolt",
        "device_class": "power",
        "attr": ATTR_PHASE_A_POWER,
    },
    "phase_b_power": {
        "name": "Phase B Power",
        "unit": "W",
        "icon": "mdi:lightning-bolt",
        "device_class": "power",
        "attr": ATTR_PHASE_B_POWER,
    },
    "phase_c_power": {
        "name": "Phase C Power",
        "unit": "W",
        "icon": "mdi:lightning-bolt",
        "device_class": "power",
        "attr": ATTR_PHASE_C_POWER,
    },
    "total_ct_power": {
        "name": "Total CT Power",
        "unit": "W",
        "icon": "mdi:lightning-bolt",
        "device_class": "power",
        "attr": ATTR_TOTAL_CT_POWER,
    },
}

SENSORS_SYSTEM: Final = {
    "wifi_signal_strength": {
        "name": "WiFi Signal Strength",
        "unit": "dBm",
        "icon": "mdi:wifi",
        "device_class": "signal_strength",
        "attr": ATTR_WIFI_SIGNAL_STRENGTH,
    },
    "wifi_ssid": {
        "name": "WiFi SSID",
        "unit": None,
        "icon": "mdi:wifi",
        "device_class": None,
        "attr": ATTR_WIFI_SSID,
    },
    "operating_mode": {
        "name": "Operating Mode",
        "unit": None,
        "icon": "mdi:cog",
        "device_class": None,
        "attr": ATTR_OPERATING_MODE,
    },
}

# Combine all sensors
ALL_SENSORS: Final = {
    **SENSORS_BATTERY,
    **SENSORS_PV,
    **SENSORS_GRID,
    **SENSORS_ENERGY,
    **SENSORS_CT,
    **SENSORS_SYSTEM,
}

# Binary Sensors
BINARY_SENSORS: Final = {
    "battery_charging": {
        "name": "Battery Charging",
        "icon": "mdi:battery-charging",
        "device_class": "battery_charging",
        "attr": ATTR_BATTERY_CHARGING,
    },
    "battery_discharging": {
        "name": "Battery Discharging",
        "icon": "mdi:battery-minus",
        "device_class": None,
        "attr": ATTR_BATTERY_DISCHARGING,
    },
    "ct_meter_connected": {
        "name": "CT Meter Connected",
        "icon": "mdi:meter-electric",
        "device_class": "connectivity",
        "attr": ATTR_CT_METER_CONNECTED,
    },
}

# Week Set Bitmask
WEEK_SET_MONDAY: Final = 1
WEEK_SET_TUESDAY: Final = 2
WEEK_SET_WEDNESDAY: Final = 4
WEEK_SET_THURSDAY: Final = 8
WEEK_SET_FRIDAY: Final = 16
WEEK_SET_SATURDAY: Final = 32
WEEK_SET_SUNDAY: Final = 64
WEEK_SET_ALL_DAYS: Final = 127
WEEK_SET_WEEKDAYS: Final = 31
WEEK_SET_WEEKEND: Final = 96

# Configuration Keys
CONF_IP_ADDRESS: Final = "ip_address"
CONF_PORT: Final = "port"
CONF_BLE_MAC: Final = "ble_mac"
CONF_TIMEOUT: Final = "timeout"
CONF_SCAN_INTERVAL: Final = "scan_interval"
