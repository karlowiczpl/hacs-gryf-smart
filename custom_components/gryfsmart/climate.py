"""Handle the Gryf Smart Climate platform."""

from typing import Any

from pygryfsmart.device import _GryfDevice, GryfThermostat

from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature, UnitOfTemperature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_TYPE, ATTR_TEMPERATURE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.components.climate.const import HVACAction, HVACMode

from .entity import GryfYamlEntity, GryfConfigFlowEntity
from .const import (
    DOMAIN,
    CONF_API,
    CONF_DEVICES,
    CONF_EXTRA,
    CONF_ID,
    CONF_NAME,
    CONF_OUT,
    CONF_TEMP,
    NORMAL_HEATING_MODE,
    SLOWEST_HEATING_MODE,
    THE_SLOWEST_HEATING_MODE,
    Platforms
)
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discover_info: DiscoveryInfoType,
) -> None:
    """Set up the climate platform."""

    climates = []

    for conf in hass.data[DOMAIN].get(Platforms.CLIMATE, []):
        device = GryfThermostat(
            conf.get(CONF_NAME),
            conf.get(CONF_OUT) // 10,
            conf.get(CONF_OUT) % 10,
            conf.get(CONF_TEMP) // 10,
            conf.get(CONF_TEMP) % 10,
            0, hass.data[DOMAIN][CONF_API],)
        climates.append(GryfYamlClimate(device))
    
    async_add_entities(climates)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Config flow for Climate platform."""

    climates = []
    for conf in config_entry.data[CONF_DEVICES]:
        if conf.get(CONF_TYPE) == Platforms.CLIMATE:
            device = GryfThermostat(
                conf.get(CONF_NAME),
                conf.get(CONF_ID) // 10,
                conf.get(CONF_ID) % 10,
                int(conf.get(CONF_EXTRA)) // 10,
                int(conf.get(CONF_EXTRA)) % 10,
                0, config_entry.runtime_data[CONF_API],
            )
            climates.append(GryfConfigFlowClimate(device, config_entry))

    async_add_entities(climates)

class GryfClimteBase(ClimateEntity):
    """Gryf Climte entity base."""

    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.PRESET_MODE
    )
    _attr_hvac_modes = [
        HVACMode.HEAT,
        HVACMode.OFF
    ]
    _attr_preset_modes = [
        NORMAL_HEATING_MODE,
        SLOWEST_HEATING_MODE,
        THE_SLOWEST_HEATING_MODE
    ]
    _attr_preset_mode = "Away"
    _attr_max_temp = 50
    _attr_min_temp = -10
    _attr_precision = 0.1
    _attr_target_temperature_step = 0.5
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _current_temperature = 21.0
    _attr_hvac_action = HVACAction.OFF
    _attr_hvac_mode = HVACMode.OFF
    _attr_target_temperature = 21.0

    _device: _GryfDevice

    @property
    def current_temperature(self):
        return self._current_temperature
    
    async def async_update(self, states):
        """Update state."""

        self._current_temperature = states.get("T")
        _LOGGER.error(self.current_temperature)

        if states.get("O"):
            self._attr_hvac_action = HVACAction.HEATING
        else:
            self._attr_hvac_action = HVACAction.OFF

        await self.async_set_hvac_mode(self._attr_hvac_mode)

        self.async_write_ha_state()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        self._attr_hvac_mode = hvac_mode

        if self._attr_hvac_mode == HVACMode.OFF:
            self._device.enable(False)
        else:
            self._device.enable(True)

        self.async_write_ha_state()

    async def async_turn_on(self) -> None:
        self._device.enable(True)

        self._attr_hvac_mode = HVACMode.HEAT
        self.async_write_ha_state()

    async def async_turn_off(self) -> None:
        self._device.enable(False)

        self._attr_hvac_mode = HVACMode.OFF
        self.async_write_ha_state()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        if preset_mode == NORMAL_HEATING_MODE:
            self._device.change_differential(0)
        elif preset_mode == SLOWEST_HEATING_MODE:
            self._device.change_differential(1)
        else:
            self._device.change_differential(2)

        self._attr_preset_mode = preset_mode
        self.async_write_ha_state()

    async def async_set_temperature(self, **kwargs: Any) -> None:

        if ATTR_TEMPERATURE in kwargs:
            await self._device.set_target_temperature(kwargs[ATTR_TEMPERATURE])
            self._attr_target_temperature = kwargs[ATTR_TEMPERATURE]

            self.async_write_ha_state()

class GryfConfigFlowClimate(GryfConfigFlowEntity, GryfClimteBase):
    """Gryf smart config flow climate class."""

    def __init__(
        self,
        device: GryfThermostat,
        config_entry: ConfigEntry,
    ) -> None:
        """Init the gryf smart climate."""

        self._config_entry = config_entry
        super().__init__(config_entry, device)
        self._device.subscribe(self.async_update)

class GryfYamlClimate(GryfYamlEntity, GryfClimteBase):
    """Gryf smart yaml climate class."""

    def __init__(
            self,
            device: GryfThermostat,
        ) -> None:
            """Init the gryf climate."""
            super().__init__(device)
            device.subscribe(self.async_update)
