"""Handle the gryfSmart Remote platform functionality."""

from typing import Any
import asyncio

from pygryfsmart.device import _GryfDevice, GryfOutputLine, GryfInputLine 
from pygryfsmart import GryfApi
from homeassistant.components.remote import RemoteEntity, RemoteEntityDescription, RemoteEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_TYPE
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .entity import GryfConfigFlowEntity, GryfYamlEntity
from .const import (
    CONF_API,
    CONF_DEVICE_CLASS,
    CONF_EXTRA,
    CONF_NAME,
    DOMAIN,
    PLATFORM_REMOTE,
    GRYF_IN_NAME,
    GRYF_OUT_NAME,
)

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    dicovery_info: DiscoveryInfoType,
) -> None:
    """Set up the remote platform."""

    remotes = []
    remotes.append(GryfYamlRemote(hass.data[DOMAIN][CONF_API]))

    async_add_entities(remotes)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    pass

class GryfRemoteBase(RemoteEntity):
    """Gryf remote entity base."""

    _device: GryfInputLine
    _output_device: GryfOutputLine

    _input = ""
    _output = ""

    async def async_input_update(self, state):
        self._device = state

        await self.update_current_activity()

    async def async_output_update(self, state):
        self._output = state

        await self.update_current_activity()

    async def update_current_activity(self):
        self._attr_current_activity = f"input: {self._input}\n output: {self._output}"
        self._attr_state = f"input:dsakdjka"
        
        self.async_write_ha_state()

class GryfYamlRemote(GryfYamlEntity, GryfRemoteBase):

    def __init__(
        self,
        api: GryfApi
    ) -> None:
        self._device = GryfInputLine("GRYF COMMUNICATION PORT", api)
        self._output_device = GryfOutputLine(GRYF_OUT_NAME, api)

        super().__init__(self._device)

        self._device.subscribe(self.async_input_update)
        self._output_device.subscribe(self.async_output_update)
