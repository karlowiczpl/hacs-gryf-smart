"""Handle the Gryf Smart Switch platform functionality."""

import asyncio
from pygryfsmart import GryfApi
from pygryfsmart.device import _GryfDevice, GryfInput , GryfOutput

from homeassistant.components.switch import SwitchEntity , SwitchDeviceClass, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform , CONF_TYPE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType , DiscoveryInfoType
from homeassistant.helpers.restore_state import RestoreEntity

from .const import CONF_API, CONF_DEVICE_CLASS , CONF_DEVICES, CONF_EXTRA , CONF_ID, CONF_INPUTS , CONF_NAME , DOMAIN, PLATFORM_GATE, PLATFORM_SWITCH, SWITCH_DEVICE_CLASS, PLATFORM_SWITCH
from .entity import GryfYamlEntity , GryfConfigFlowEntity

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType,
) -> None:
    """Set up the Switch platform."""

    switches = []

    for conf in hass.data[DOMAIN].get(PLATFORM_SWITCH, []):
        device = GryfOutput(
            conf.get(CONF_NAME),
            conf.get(CONF_ID) // 10,
            conf.get(CONF_ID) % 10,
            hass.data[DOMAIN][CONF_API],
        )
        switches.append(GryfYamlSwitch(device , conf.get(CONF_DEVICE_CLASS, "switch")))

    for conf in hass.data[DOMAIN].get(PLATFORM_GATE, []):
        device = GryfOutput(
            conf.get(CONF_NAME),
            conf.get(CONF_ID) // 10,
            conf.get(CONF_ID) % 10,
            hass.data[DOMAIN][CONF_API],
        )
        switches.append(GryfGateYaml(device, conf.get(CONF_INPUTS), hass.data[DOMAIN][CONF_API]))

    async_add_entities(switches)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Config flow for Switch platform."""

    switches = []
    for conf in config_entry.data[CONF_DEVICES]:
        if conf.get(CONF_TYPE) == PLATFORM_SWITCH:
            device = GryfOutput(
                conf.get(CONF_NAME),
                conf.get(CONF_ID) // 10,
                conf.get(CONF_ID) % 10,
                config_entry.runtime_data[CONF_API],
            )
            switches.append(GryfConfigFlowSwitch(device , config_entry , conf.get(CONF_EXTRA, "switch")))
        if conf.get(CONF_TYPE) == PLATFORM_GATE:
            device = GryfOutput(
                conf.get(CONF_NAME),
                conf.get(CONF_ID) // 10,
                conf.get(CONF_ID) % 10,
                config_entry.runtime_data[CONF_API],
            )
            switches.append(GryfGateConfigFlow(device, config_entry, conf.get(CONF_EXTRA, "switch")))

    async_add_entities(switches)
    
class GryfGateBase(SwitchEntity):
    
    _attr_is_on = False
    _attr_icon = "mdi:boom-gate"

    _device: GryfOutput
    _input_device: GryfInput
    _input_negation = 0
    _output_state = 0

    async def async_update_output(self, is_on):
        self._output_state = is_on
        self._attr_is_on = is_on

        self.async_write_ha_state()

    async def async_update_input(self, is_on):
        if is_on:
            self._attr_icon = "mdi:boom-gate-up"
        else:
            self._attr_icon = "mdi:boom-gate"

        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs):

        await self._device.turn_on()

        await asyncio.sleep(1)

        await self._device.turn_off()

    async def async_toggle(self, **kwargs) -> None:

        await self._device.turn_on()

        await asyncio.sleep(1)

        await self._device.turn_off()

    async def async_turn_off(self, **kwargs) -> None:
        pass

    def extra_parm(self, extra: str, api):

        filtred_extra = ""
        if extra:
            for char in extra:
                if char == 'n' or char == "N":
                    self._input_negation = 1
                else:
                    filtred_extra += char
            
            if filtred_extra.strip().isdigit:
                id = int(filtred_extra)
                if id > 11:
                    self._input_device = GryfInput(
                        "input",
                        id // 10,
                        id % 10,
                        api
                    )

                self._input_device.subscribe(self.async_update_input)

class GryfGateConfigFlow(GryfConfigFlowEntity, GryfGateBase):
    
    def __init__(
        self,
        device: _GryfDevice,
        config_entry: ConfigEntry,
        extra_parm: str,
    ) -> None:

        super().__init__(config_entry, device)
        self._device.subscribe(self.async_update_output)
        self.extra_parm(extra_parm, config_entry.runtime_data[CONF_API])

class GryfGateYaml(GryfYamlEntity, GryfGateBase):

    def __init__(
        self,
        device: _GryfDevice,
        extra_parm: str,
        api: GryfApi,
    ) -> None:

        super().__init__(device)
        self._device.subscribe(self.async_update_output)
        self.extra_parm(extra_parm, api)

class GryfSwitchBase(SwitchEntity, RestoreEntity):
    """Gryf Switch entity base."""

    _is_on = False
    _device: _GryfDevice
    _attr_device_class = SwitchDeviceClass.SWITCH

    @property
    def is_on(self):
        """Property is on."""

        return self._is_on

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()

        if(last_state := await self.async_get_last_state()) is not None:
            self._attr_is_on = last_state.state == "on"

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
