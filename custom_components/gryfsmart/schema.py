"""Config schema for Gryf Smart Integration."""

import voluptuous as vol

from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_ID,
    CONF_MODULE_COUNT,
    CONF_NAME,
    CONF_PORT,
    CONF_DEVICE_CLASS,
    CONF_TIME,
    DOMAIN,
    PLATFORM_BINARY_SENSOR,
    PLATFORM_CLIMATE,
    PLATFORM_COVER,
    PLATFORM_INPUT,
    PLATFORM_LIGHT,
    PLATFORM_PWM,
    PLATFORM_SWITCH,
    CONF_TEMP,
    CONF_OUT,
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
        vol.Required(CONF_OUT): cv.positive_int,
        vol.Required(CONF_TIME): cv.positive_int,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_PORT): cv.string,
                vol.Required(CONF_MODULE_COUNT): cv.positive_int,
                vol.Optional(PLATFORM_PWM): vol.All(cv.ensure_list, [STANDARD_SCHEMA]),
                vol.Optional(PLATFORM_LIGHT): vol.All(cv.ensure_list , [STANDARD_SCHEMA]),
                vol.Optional(PLATFORM_INPUT): vol.All(cv.ensure_list , [STANDARD_SCHEMA]),
                vol.Optional(PLATFORM_BINARY_SENSOR): vol.All(cv.ensure_list , [DEVICE_CLASS_SCHEMA]),
                vol.Optional(PLATFORM_SWITCH): vol.All(cv.ensure_list , [DEVICE_CLASS_SCHEMA]),
                vol.Optional(PLATFORM_CLIMATE): vol.All(cv.ensure_list , [CLIMATE_SCHEMA]),
                vol.Optional(PLATFORM_COVER): vol.All(cv.ensure_list , [COVER_SCHEMA]),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)
