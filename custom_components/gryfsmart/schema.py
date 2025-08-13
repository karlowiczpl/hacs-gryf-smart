"""Config schema for Gryf Smart Integration."""

import voluptuous as vol

from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    CONF_TEMP,
    CONF_OUT,
    CONF_INPUTS,
    CONF_ID,
    CONF_MODULE_COUNT,
    CONF_NAME,
    CONF_PORT,
    CONF_DEVICE_CLASS,
    CONF_TIME,
    Platforms
)

STANDARD_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_ID): cv.positive_int,
    }
)
DEVICE_CLASS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_ID): cv.positive_int,
        vol.Optional(CONF_DEVICE_CLASS): cv.string,
    }
)
CLIMATE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_OUT): cv.positive_int,
        vol.Required(CONF_TEMP): cv.positive_int,
    }
)
COVER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_ID): cv.positive_int,
        vol.Required(CONF_TIME): cv.positive_int,
    }
)
GATE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_ID): cv.positive_int,
        vol.Optional(CONF_INPUTS): cv.positive_int,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_PORT): cv.string,
                vol.Required(CONF_MODULE_COUNT): cv.positive_int,
                vol.Optional(Platforms.PWM): vol.All(cv.ensure_list, [STANDARD_SCHEMA]),
                vol.Optional(Platforms.LIGHT): vol.All(cv.ensure_list , [STANDARD_SCHEMA]),
                vol.Optional(Platforms.INPUT): vol.All(cv.ensure_list , [STANDARD_SCHEMA]),
                vol.Optional(Platforms.BINARY_SENSOR): vol.All(cv.ensure_list , [DEVICE_CLASS_SCHEMA]),
                vol.Optional(Platforms.SWITCH): vol.All(cv.ensure_list , [DEVICE_CLASS_SCHEMA]),
                vol.Optional(Platforms.CLIMATE): vol.All(cv.ensure_list , [CLIMATE_SCHEMA]),
                vol.Optional(Platforms.COVER): vol.All(cv.ensure_list , [COVER_SCHEMA]),
                vol.Optional(Platforms.GATE): vol.All(cv.ensure_list , [GATE_SCHEMA]),
                vol.Optional(Platforms.TEMPERATURE): vol.All(cv.ensure_list , [STANDARD_SCHEMA]),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)
