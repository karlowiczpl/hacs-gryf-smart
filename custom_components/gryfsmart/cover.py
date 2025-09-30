"""Handle the Gryf Smart Cover platform funtionality."""

from pygryfsmart.device import GryfCover
from pygryfsmart.const import ShutterStates

from homeassistant.components.cover import CoverEntity, CoverDeviceClass, CoverEntityFeature, CoverState
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_TYPE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .entity import GryfConfigFlowEntity, GryfYamlEntity
from .const import (
    CONF_API,
    CONF_DEVICES,
    CONF_ID,
    CONF_EXTRA,
    CONF_NAME,
    CONF_TIME,
    DOMAIN,
    Platforms,
)

import logging
_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None,
) -> None:
    """Set up the Cover Platform."""

    covers = []

    for conf in hass.data[DOMAIN].get(Platforms.COVER, {}):
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
        if conf.get(CONF_TYPE) == Platforms.COVER:
            device = GryfCover(
                conf.get(CONF_NAME),
                conf.get(CONF_ID) // 10,
                conf.get(CONF_ID) % 10,
                conf.get(CONF_EXTRA),
                config_entry.runtime_data[CONF_API],
            )
            covers.append(GryfConfigFlowCover(device, config_entry))

    async_add_entities(covers)

class GryfCoverBase(CoverEntity):
    """Gryf Cover entity base."""

    _device: GryfCover
    _wait_for_stop = False
    _trying_to_stop = False
    _attr_is_closed = False
    _attr_is_opening = False
    _attr_is_closing = False
    _attr_current_cover_tilt_position = 0
    _attr_device_class = CoverDeviceClass.SHUTTER
    _attr_current_cover_tilt_position = 0
    _attr_supported_features = CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.OPEN_TILT | CoverEntityFeature.STOP | CoverEntityFeature.CLOSE_TILT | CoverEntityFeature.SET_TILT_POSITION
    _attr_state = CoverState.CLOSED

    async def async_open_cover(self, **kwargs):
        await self._device.turn_on()

    async def async_close_cover(self, **kwargs):
        await self._device.turn_off()

    async def async_stop_cover(self, **kwargs):
        self._trying_to_stop = True

        await self._device.stop()

    async def async_set_cover_tilt_position(self, **kwargs):
        _LOGGER.debug(kwargs)

    async def async_open_cover_tilt(self, **kwargs):
        if self._attr_state in [CoverState.OPENING, CoverState.CLOSING]:
            self._trying_to_stop = True

        await self._device.toggle()

    async def async_close_cover_tilt(self, **kwargs):
        await self._device._api.set_cover(self._device._id, self._device._pin, 25, ShutterStates.OPEN)

    async def async_update(self, state):
        if state == 1:
            self._attr_is_opening = True
            self._attr_is_closing = False
            self._wait_for_stop = 1
            self._attr_current_cover_tilt_position = 100
        elif state == 2:
            self._attr_is_opening = False
            self._attr_is_closing = True
            self._wait_for_stop = 1
            self._attr_current_cover_tilt_position = 0
        else:
            if self._attr_is_opening and self._wait_for_stop:
                self._attr_is_closed = False
            elif self._wait_for_stop:
                self._attr_is_closed = True
            if self._trying_to_stop:
                self._trying_to_stop = True
                self._attr_is_closed = None
            self._attr_is_opening = False
            self._attr_is_closing = False
            
        self.async_write_ha_state()

class GryfYamlCover(GryfYamlEntity, GryfCoverBase):

    def __init__(self, device: GryfCover):

        super().__init__(device)
        device.subscribe(self.async_update)

class GryfConfigFlowCover(GryfConfigFlowEntity, GryfCoverBase):

    def __init__(self, device: GryfCover, config_entry: ConfigEntry):
        self._config_entry = config_entry
        super().__init__(config_entry, device)
        device.subscribe(self.async_update)
