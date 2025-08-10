"""Define constants used throughout the Gryf Smart integration."""

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass
from homeassistant.const import Platform

DOMAIN = "gryfsmart"

CONF_MODULE_COUNT = "module_count"
CONF_PORT = "port"
CONF_TYPE = "type"
CONF_ID = "id"
CONF_PIN = "pin"
CONF_NAME = "name"
CONF_EXTRA = "extra parameters"
CONF_DEVICES = "devices"
CONF_RECONFIGURE = "reconfigure"
CONF_COMMUNICATION = "communication"
CONF_API = "api"
CONF_DEVICE_DATA = "device_data"
CONF_INPUTS = "input"
CONF_DEVICE_CLASS = "device_class"
CONF_GRYF_EXPERT = "gryf_expert"
CONF_TEMP = "temp"
CONF_OUT = "out"
CONF_TIME = "time"
CONF_NEGATION = "negation"
CONF_TEMP_ID = "Sensor ID"
CONF_OUT_ID = "Output ID"
CONF_HYSTERESIS_LOOP = "hysteresis loop"

class Platforms():
    PWM = "pwm"
    TEMPERATURE = "temperature"
    INPUT = "input"
    LIGHT = "light"
    BINARY_SENSOR = "binary_sensor"
    SWITCH = "output"
    CLIMATE = "climate"
    LOCK = "lock"
    COVER = "cover"
    GATE = "gate"

    PUBLIC_NAMES = {
        LIGHT: "Light",
        SWITCH: "Output",
        COVER: "Shutter",
        BINARY_SENSOR: "Binary input",
        LOCK: "Lock",
        CLIMATE: "Thermostat",
        PWM: "PWM",
        TEMPERATURE: "Termometr",
        INPUT: "Input",
        GATE: "Gate",
        "device_menu": "exit",
    }

HOMEASSISTANT_PLATFORMS: list[Platform] = [
    Platform.LIGHT,
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.CLIMATE,
    Platform.COVER,
    Platform.SWITCH,
    Platform.LOCK
]

DEFAULT_PORT = "/dev/ttyUSB0"
GRYF_IN_NAME = "Gryf IN"
GRYF_OUT_NAME = "Gryf OUT"

NORMAL_HEATING_MODE = "away"
SLOWEST_HEATING_MODE = "eco"
THE_SLOWEST_HEATING_MODE = "sleep"

SLOWEST_HEATING_MODE_DIFFERENTIAL = 1
THE_SLOWEST_HEATING_MODE_DIFFERENTIAL = 1

CONFIG_FLOW_MENU_OPTIONS = {
    "add_device": "Add Device",
    "edit_device": "Edit Device",
    "communication": "Setup Communication",
    "finish": "Finish",
}


CONF_LINE_SENSOR_ICONS = {
    GRYF_IN_NAME: ["mdi:message-arrow-right-outline", "mdi:message-arrow-right"],
    GRYF_OUT_NAME: ["mdi:message-arrow-left-outline", "mdi:message-arrow-left"],
}

BINARY_SENSOR_DEVICE_CLASS = {
    "door": BinarySensorDeviceClass.DOOR,
    "garage door": BinarySensorDeviceClass.GARAGE_DOOR,
    "heat": BinarySensorDeviceClass.HEAT,
    "light": BinarySensorDeviceClass.LIGHT,
    "motion": BinarySensorDeviceClass.MOTION,
    "window": BinarySensorDeviceClass.WINDOW,
    "smoke": BinarySensorDeviceClass.SMOKE,
    "sound": BinarySensorDeviceClass.SOUND,
    "power": BinarySensorDeviceClass.POWER,
    "battery": BinarySensorDeviceClass.BATTERY,
    "batery charging": BinarySensorDeviceClass.BATTERY_CHARGING,
    "co": BinarySensorDeviceClass.CO,
    "cold": BinarySensorDeviceClass.COLD,
    "connectivity": BinarySensorDeviceClass.CONNECTIVITY,
    "gas": BinarySensorDeviceClass.GAS,
    "lock": BinarySensorDeviceClass.LOCK,
    "moisture": BinarySensorDeviceClass.MOISTURE,
}

SWITCH_DEVICE_CLASS = {
    "switch": SwitchDeviceClass.SWITCH,
    "outlet": SwitchDeviceClass.OUTLET,
}
