"""Constants for the Marstek Venus E integration."""
from typing import Final

DOMAIN: Final = "hacs_marstek_venus_e"

# Device Configuration
DEFAULT_PORT: Final = 30000
DEFAULT_SCAN_INTERVAL: Final = 300  # seconds (5 minutes)
DEFAULT_TIMEOUT: Final = 20.0  # seconds - UDP request timeout

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
# Sensors from ES.GetStatus (automatic updates)
SENSORS_BATTERY: Final = {
    "battery_state_of_charge": {
        "name": "Battery State of Charge",
        "unit": "%",
        "icon": "mdi:battery-percent",
        "device_class": "battery",
        "attr": "bat_soc",
        "source": "auto",  # From ES.GetStatus
    },
    "battery_capacity": {
        "name": "Battery Capacity",
        "unit": "Wh",
        "icon": "mdi:battery-heart",
        "device_class": "energy",
        "attr": "bat_cap",
        "source": "auto",  # From ES.GetStatus
    },
}

# Sensors from Bat.GetStatus (manual refresh button)
SENSORS_BATTERY_MANUAL: Final = {
    "battery_temperature": {
        "name": "Battery Temperature",
        "unit": "°C",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
        "attr": "bat_temp",
        "source": "battery",  # From Bat.GetStatus
    },
    "battery_rated_capacity": {
        "name": "Battery Rated Capacity",
        "unit": "Wh",
        "icon": "mdi:battery-heart",
        "device_class": "energy",
        "attr": "rated_capacity",
        "source": "battery",  # From Bat.GetStatus
    },
}

# Binary sensors from Bat.GetStatus (manual refresh button)
SENSORS_BATTERY_BINARY: Final = {
    "battery_charging": {
        "name": "Battery Charging",
        "icon": "mdi:battery-charging",
        "device_class": "battery_charging",
        "attr": "charg_flag",
        "source": "battery",  # From Bat.GetStatus
    },
    "battery_discharging": {
        "name": "Battery Discharging",
        "icon": "mdi:battery-minus",
        "device_class": None,
        "attr": "dischrg_flag",
        "source": "battery",  # From Bat.GetStatus
    },
}

SENSORS_PV: Final = {
    "pv_power": {
        "name": "PV Power",
        "unit": "W",
        "icon": "mdi:solar-power",
        "device_class": "power",
        "attr": "pv_power",  # Direct field from ES.GetStatus
    },
}

SENSORS_GRID: Final = {
    "grid_power": {
        "name": "Grid Power",
        "unit": "W",
        "icon": "mdi:transmission-tower",
        "device_class": "power",
        "attr": "ongrid_power",  # Direct field from ES.GetStatus
    },
    "offgrid_power": {
        "name": "Off-Grid Power",
        "unit": "W",
        "icon": "mdi:power-off",
        "device_class": "power",
        "attr": "offgrid_power",  # Direct field from ES.GetStatus
    },
}

SENSORS_ENERGY: Final = {
    "total_pv_energy": {
        "name": "Total PV Energy",
        "unit": "Wh",  # Device returns Wh, not kWh
        "icon": "mdi:solar-power-box",
        "device_class": "energy",
        "state_class": "total_increasing",
        "attr": "total_pv_energy",  # Direct field from ES.GetStatus
    },
    "total_grid_export_energy": {
        "name": "Total Grid Export Energy",
        "unit": "Wh",  # Device returns Wh, not kWh
        "icon": "mdi:transmission-tower-export",
        "device_class": "energy",
        "state_class": "total_increasing",
        "attr": "total_grid_output_energy",  # Direct field from ES.GetStatus
    },
    "total_grid_import_energy": {
        "name": "Total Grid Import Energy",
        "unit": "Wh",  # Device returns Wh, not kWh
        "icon": "mdi:transmission-tower-import",
        "device_class": "energy",
        "state_class": "total_increasing",
        "attr": "total_grid_input_energy",  # Direct field from ES.GetStatus
    },
    "total_load_energy": {
        "name": "Total Load Energy",
        "unit": "Wh",  # Device returns Wh, not kWh
        "icon": "mdi:home-lightning-bolt",
        "device_class": "energy",
        "state_class": "total_increasing",
        "attr": "total_load_energy",  # Direct field from ES.GetStatus
    },
}

# CT meter sensors from ES.GetMode (manual refresh button)
SENSORS_CT: Final = {
    "phase_a_power": {
        "name": "Phase A Power",
        "unit": "W",
        "icon": "mdi:lightning-bolt",
        "device_class": "power",
        "attr": "a_power",
        "source": "mode",  # From ES.GetMode
    },
    "phase_b_power": {
        "name": "Phase B Power",
        "unit": "W",
        "icon": "mdi:lightning-bolt",
        "device_class": "power",
        "attr": "b_power",
        "source": "mode",  # From ES.GetMode
    },
    "phase_c_power": {
        "name": "Phase C Power",
        "unit": "W",
        "icon": "mdi:lightning-bolt",
        "device_class": "power",
        "attr": "c_power",
        "source": "mode",  # From ES.GetMode
    },
    "total_ct_power": {
        "name": "Total CT Power",
        "unit": "W",
        "icon": "mdi:lightning-bolt",
        "device_class": "power",
        "attr": "total_power",
        "source": "mode",  # From ES.GetMode
    },
}

# CT meter binary sensor from ES.GetMode
SENSORS_CT_BINARY: Final = {
    "ct_meter_connected": {
        "name": "CT Meter Connected",
        "icon": "mdi:meter-electric",
        "device_class": "connectivity",
        "attr": "ct_state",
        "source": "mode",  # From ES.GetMode
    },
}

# Operating mode sensor from ES.GetMode
SENSORS_SYSTEM: Final = {
    "operating_mode": {
        "name": "Operating Mode",
        "icon": "mdi:cog",
        "device_class": None,
        "attr": "mode",
        "source": "auto",  # Mode is added to main data by coordinator
    },
}

# Combine all sensors
ALL_SENSORS: Final = {
    **SENSORS_BATTERY,
    **SENSORS_BATTERY_MANUAL,
    **SENSORS_PV,
    **SENSORS_GRID,
    **SENSORS_ENERGY,
    **SENSORS_CT,
    **SENSORS_SYSTEM,
}

# Binary Sensors
# From manual API calls (Bat.GetStatus and ES.GetMode)
BINARY_SENSORS: Final = {
    **SENSORS_BATTERY_BINARY,
    **SENSORS_CT_BINARY,
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
