"""Handle the Gryf Smart Switch platform functionality."""

from typing import Any
import asyncio

from homeassistant.components import switch
from pygryfsmart.device import _GryfDevice , GryfOutput, GryfReset

from homeassistant.components.switch import SwitchEntity , SwitchDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform , CONF_TYPE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType , DiscoveryInfoType

from .const import CONF_API, CONF_DEVICE_CLASS , CONF_DEVICES, CONF_EXTRA , CONF_ID , CONF_NAME , DOMAIN, PLATFORM_SWITCH, SWITCH_DEVICE_CLASS
from .entity import GryfYamlEntity , GryfConfigFlowEntity

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType,
) -> None:
    """Set up the Switch platform."""

    switches = []

    for conf in hass.data[DOMAIN].get(PLATFORM_SWITCH):
        device = GryfOutput(
            conf.get(CONF_NAME),
            conf.get(CONF_ID) // 10,
            conf.get(CONF_ID) % 10,
            hass.data[DOMAIN][CONF_API],
        )
        switches.append(GryfYamlSwitch(device , conf.get(CONF_DEVICE_CLASS)))

    async_add_entities(switches)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Config flow for Switch platform."""

    switches = []
    for conf in config_entry.data[CONF_DEVICES]:
        if conf.get(CONF_TYPE) == Platform.SWITCH:
            device = GryfOutput(
                conf.get(CONF_NAME),
                conf.get(CONF_ID) // 10,
                conf.get(CONF_ID) % 10,
                config_entry.runtime_data[CONF_API],
            )
            switches.append(GryfConfigFlowSwitch(device , config_entry , conf.get(CONF_EXTRA , None)))

    async_add_entities(switches)
    
class GryfSwitchBase(SwitchEntity):
    """Gryf Switch entity base."""

    _is_on = False
    _device: _GryfDevice
    _attr_device_class = SwitchDeviceClass.SWITCH

    @property
    def is_on(self):
        """Property is on."""

        return self._is_on

    async def async_update(self , is_on):
        """Update state."""

        self._is_on = is_on
        self.async_write_ha_state()

    async def async_turn_on(self , **kwargs):
        """Turn on switch."""
    
        await self._device.turn_on()

    async def async_turn_off(self , **kwargs):
        """Turn off switch."""
    
        await self._device.turn_off()

    async def async_toggle(self , **kwargs):
        """Toggle switch."""
    
        await self._device.toggle()

class GryfConfigFlowSwitch(GryfConfigFlowEntity , GryfSwitchBase):
    """Gryf Smart config flow Switch class."""

    def __init__(
        self,
        device: _GryfDevice,
        config_entry: ConfigEntry,
        device_class: str
    ) -> None:
        """Init the Gryf Switch."""

        self._config_entry = config_entry
        super().__init__(config_entry , device)
       self._device.subscribe(self.async_update)

        self._attr_device_class = SWITCH_DEVICE_CLASS[device_class]


class GryfYamlSwitch(GryfYamlEntity , GryfSwitchBase):
    """Gryf Smart yaml Switch class."""

    def __init__(
        self,
        device: _GryfDevice,
        device_class: str,
    ) -> None:
        """Init the Gryf Switch."""
        
        super().__init__(device)
        self._device.subscribe(self.async_update)

        self._attr_device_class = SWITCH_DEVICE_CLASS[device_class]

class GryfRSTBase(SwitchEntity):
    """Gryf Smart MonoStable Switch base."""

    _is_on = False
    _device: GryfReset
    _attr_device_class = SwitchDeviceClass.SWITCH

    @property
    def is_on(self):
        """Property is on."""

        return self._is_on

    async def async_turn_on(self, **kwargs):
        """Turn on switch."""

        await self._device.reset_all()
        self._is_on = True
        self.async_write_ha_state()
        await asyncio.sleep(2)

        self._is_on = False
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn off switch."""

        pass

    async def async_toggle(self, **kwargs):
        """Toggle switch"""

        await self._device.reset_all()

class GryfConfigFlowRST(GryfConfigFlowEntity, GryfRSTBase):
    """Gryf smart config flow rst."""

    _device: GryfReset

    def __init__(
            self,
            config_entry: ConfigEntry,
            device: GryfReset
    ) -> None:
        """Initailise gryfRST."""

        super().__init__(config_entry, device)

class GryfYamlRST(GryfYamlEntity, GryfRSTBase):
    """Gryf Smart yaml reset."""

    def __init__(
        self,
        device: GryfReset
    ) -> None:
        """Initialise GryfRST."""
        
        super().__init__(device)

