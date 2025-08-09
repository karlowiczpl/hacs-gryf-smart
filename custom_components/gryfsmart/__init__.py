"""The Gryf Smart integration."""

from __future__ import annotations

import logging

from pygryfsmart.api import GryfApi, GryfExpert

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.typing import ConfigType

from .const import CONF_API, CONF_COMMUNICATION, CONF_DEVICE_DATA, CONF_PORT, DOMAIN, CONF_GRYF_EXPERT, CONF_MODULE_COUNT
from .schema import CONFIG_SCHEMA as SCHEMA

CONFIG_SCHEMA = SCHEMA

_PLATFORMS: list[Platform] = [
    Platform.LIGHT,
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.CLIMATE,
    Platform.COVER,
    Platform.SWITCH,
    Platform.LOCK
]

_LOGGER = logging.getLogger(__name__)

async def async_setup(
    hass: HomeAssistant,
    config: ConfigType,
) -> bool:
    """Set up the Gryf Smart Integration."""

    if config.get(DOMAIN) is None:
        return True

    try:
        api = GryfApi(config[DOMAIN][CONF_PORT])
        await api.start_connection()
        api.start_update_interval(1)
    except ConnectionError:
        _LOGGER.error("Unable to connect: %s", ConnectionError)
        return False

    hass.data[DOMAIN] = config.get(DOMAIN)
    hass.data[DOMAIN][CONF_API] = api

    async def handle_reset(call: ServiceCall):
        await api.reset(0, True)

    async def handle_gryf_expert(call: ServiceCall):
        action = call.data["action"]

        if action == "turn_on":
            if not hass.data.get(CONF_GRYF_EXPERT, None):
                hass.data[CONF_GRYF_EXPERT] = GryfExpert(api)

            await hass.data[CONF_GRYF_EXPERT].start_server()
        else:
            if not hass.data.get(CONF_GRYF_EXPERT, None):
                return
            
            await hass.data[CONF_GRYF_EXPERT].stop_server()

    async def handle_search_modules(call: ServiceCall):
        await api.search_modules(config[DOMAIN][CONF_MODULE_COUNT])

    hass.services.async_register(DOMAIN, "reset", handle_reset)
    hass.services.async_register(DOMAIN, "gryf_expert", handle_gryf_expert)
    hass.services.async_register(DOMAIN, "search_modules", handle_search_modules)

    for PLATFORM in _PLATFORMS:
        await async_load_platform(hass , PLATFORM , DOMAIN , None , config)

    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Config flow for Gryf Smart Integration."""

    if DOMAIN in hass.data and hass.data[DOMAIN][CONF_API] and hass.data[DOMAIN][CONF_API].port == entry.data[CONF_COMMUNICATION][CONF_PORT]:
        api = hass.data[DOMAIN][CONF_API]
        entry.runtime_data = {}
        entry.runtime_data[CONF_API] = api

    else:
        try:
            api = GryfApi(entry.data[CONF_COMMUNICATION][CONF_PORT])
            await api.start_connection()

            api.set_module_count(entry.data[CONF_COMMUNICATION][CONF_MODULE_COUNT])
            api.start_update_interval(api._module_count)

        except ConnectionError:
            raise ConfigEntryNotReady("Unable to connect with device") from ConnectionError

    entry.runtime_data = {}
    entry.runtime_data[CONF_API] = api
    entry.runtime_data[CONF_DEVICE_DATA] = {
        "identifiers": {(DOMAIN, "Gryf Smart", entry.unique_id)},
        "name": f"Gryf Smart {entry.unique_id}",
        "manufacturer": "Gryf Smart",
        "model": "serial",
        "sw_version": "1.0.0",
        "hw_version": "1.0.0",
    }

    async def handle_reset(call: ServiceCall):
        entry_id = call.data["entry_id"]

        entry = hass.config_entries.async_get_entry(entry_id)
        if entry is None:
            _LOGGER.error(f"Config entry: {entry_id} not found")
            return

        api = entry.runtime_data[CONF_API]
        await api.reset(0, True)
        

    async def handle_gryf_expert(call: ServiceCall):
        entry_id = call.data["entry_id"]
        action = call.data["action"]

        entry = hass.config_entries.async_get_entry(entry_id)
        if entry is None:
            _LOGGER.error(f"Config entry: {entry_id} not found")
            return

        api = entry.runtime_data[CONF_API]
        
        if action == "turn_on":
            if not entry.runtime_data.get(CONF_GRYF_EXPERT, None):
                entry.runtime_data[CONF_GRYF_EXPERT] = GryfExpert(api)

            await entry.runtime_data[CONF_GRYF_EXPERT].start_server()
        else:
            if not entry.runtime_data.get(CONF_GRYF_EXPERT, None):
                return
            
            await entry.runtime_data[CONF_GRYF_EXPERT].stop_server()

    async def handle_search_modules(call: ServiceCall):
        entry_id = call.data["entry_id"]

        entry = hass.config_entries.async_get_entry(entry_id)
        if entry is None:
            _LOGGER.error(f"Config entry: {entry_id} not found")
            return

        api = entry.runtime_data[CONF_API]
        await api.search_modules(entry.data.get(CONF_MODULE_COUNT, None))

    hass.services.async_register(DOMAIN, "reset", handle_reset)
    hass.services.async_register(DOMAIN, "gryf_expert", handle_gryf_expert)
    hass.services.async_register(DOMAIN, "search_modules", handle_search_modules)

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    await api.async_update_states()

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
