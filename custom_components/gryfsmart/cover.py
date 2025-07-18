"""Handle the Gryf Smart Cover platform funtionality."""

import asyncio
from typing import Any

from pygryfsmart.device import _GryfDevice, GryfCover, GryfOutput

from homeassistant.components.cover import CoverEntity, CoverDeviceClass, CoverEntityFeature
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE, CONF_TYPE, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import CONF_API, CONF_DEVICES, CONF_ID, CONF_EXTRA, CONF_NAME, DOMAIN, PLATFORM_COVER, CONF_TIME, PLATFORM_GATE
from .entity import GryfConfigFlowEntity, GryfYamlEntity

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None,
) -> None:
    """Set up the Cover Platform."""

    covers = []

    for conf in hass.data[DOMAIN].get(PLATFORM_COVER, {}):
        device = GryfCover(
            conf.get(CONF_NAME),
            conf.get(CONF_ID) // 10,
            conf.get(CONF_ID) % 10,
            conf.get(CONF_TIME),
            hass.data[DOMAIN][CONF_API],
        )
        covers.append(GryfYamlCover(device))

    async_add_entities(covers)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:

    covers = []
    for conf in config_entry.data[CONF_DEVICES]:
        if conf.get(CONF_TYPE) == PLATFORM_COVER:
            device = GryfCover(
                conf.get(CONF_NAME),
                conf.get(CONF_ID) // 10,
                conf.get(CONF_ID) % 10,
                conf.get(CONF_EXTRA),
                config_entry.runtime_data[CONF_API],
            )
            covers.append(GryfConfigFlowCover(device, config_entry))
        if conf.get(CONF_TYPE) == PLATFORM_GATE:
            pass

    async_add_entities(covers)

    device = GryfOutput(
        "test",
        1,
        1,
        hass.data[DOMAIN][CONF_API]
    )
    async_add_entities([GryfNoFeedBackGateConfigFlow(device, config_entry)])


class GryfCoverBase(CoverEntity):
    """Gryf Cover entity base."""

    _device: GryfCover
    _attr_is_closed = False
    _attr_is_opening = False
    _attr_is_closing = False
    _attr_device_class = CoverDeviceClass.SHUTTER
    _attr_supported_features = CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.OPEN_TILT

    async def async_open_cover(self, **kwargs):
        await self._device.turn_on()

    async def async_close_cover(self, **kwargs):
        await self._device.turn_off()

    async def async_open_cover_tilt(self, **kwargs):
        await self._device.toggle()

    async def async_update(self, state):
        if state == 1:
            self._attr_is_opening = True
            self._attr_is_closing = False
        elif state == 2:
            self._attr_is_opening = False
            self._attr_is_closing = True
        else:
            if self._attr_is_opening:
                self._attr_is_closed = False
            else:
                self._attr_is_closed = True

            self._attr_is_opening = False
            self._attr_is_closing = False
            
            self.async_write_ha_state()

class GryfYamlCover(GryfYamlEntity, GryfCoverBase):

    def __init__(self, device: GryfCover):

        super().__init__(device)
        device.subscribe(self.async_update)

class GryfNoFeedBackGateBase(ButtonEntity):

    _device: GryfOutput

    async def async_press(self) -> None:
        await self._device.turn_on()

        await asyncio.sleep(1000)

        await self._device.turn_off()

    async def async_update(self, state):
        if state:
            self._attr_icon = "mdi:boom-gate-up"
        else:
            self._attr_icon = "mdi:boom-gate"

        self.async_write_ha_state()

class GryfNoFeedBackGateConfigFlow(GryfNoFeedBackGateBase):

    def __init__(
        self,
        device: _GryfDevice,
        config_entry: ConfigEntry,
    ) -> None:

        self._config_entry = config_entry
        super().__init__(config_entry, device)
        self._device.subscribe(self.async_update)
