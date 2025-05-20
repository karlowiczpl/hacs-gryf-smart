"""Hanlde the GryfSmart Lock platform functionality."""

from typing import Any
import asyncio

from pygryfsmart.device import _GryfDevice, GryfOutput

from homeassistant.components.lock import LockEntity, LockEntityDescription, LockEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_TYPE
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .entity import GryfConfigFlowEntity, GryfYamlEntity

from .const import (
    CONF_API,
    CONF_DEVICE_CLASS,
    CONF_DEVICES,
    CONF_EXTRA,
    CONF_ID,
    CONF_NAME,
    DOMAIN,
    PLATFORM_LOCK,
)

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    dicovery_info: DiscoveryInfoType,
) -> None:
    """Set up the switch platform."""

    locks = []
    for conf in hass.data[DOMAIN].get(PLATFORM_LOCK, []):
        device = GryfOutput(
            conf.get(CONF_NAME),
            conf.get(CONF_ID) // 10,
            conf.get(CONF_ID) % 10,
            hass.data[DOMAIN][CONF_API],
        )

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Config flow for lock platform."""

    locks = []
    for conf in config_entry.data[CONF_DEVICES]:
        if conf.get(CONF_TYPE) == PLATFORM_LOCK:
            device = GryfOutput(
                conf.get(CONF_NAME),
                conf.get(CONF_ID) // 10,
                conf.get(CONF_ID) % 10,
                config_entry.runtime_data[CONF_API],
            )
            locks.append(GryfConfigFlowLock(device, config_entry))

    async_add_entities(locks)

class GryfLockBase(LockEntity):
    """Gryf Lock entity base."""

    _device: GryfOutput
    _attr_is_locked = False
    _attr_is_locking = False
    _attr_is_unlocking = False

    async def async_lock(self, **kwargs):
        await self._device.turn_on()

        self._attr_is_locking = True
        self.async_write_ha_state()

    async def async_unlock(self, **kwargs):
        await self._device.turn_off()

        self._attr_is_locking = False
        self.async_write_ha_state()

    async def async_update(self, state):
        self._attr_is_locked = state

        self._attr_is_unlocking = False
        self._attr_is_locking = False

        self.async_write_ha_state()

class GryfConfigFlowLock(GryfConfigFlowEntity, GryfLockBase):
    
    def __init__(
        self,
        device: _GryfDevice,
        config_entry: ConfigEntry,
    ) -> None:

        self._config_entry = config_entry
        super().__init__(config_entry, device)
        self._device.subscribe(self.async_update)

