"""Handle the Gryf Smart light platform functionality."""

from typing import Any

from pygryfsmart.device import _GryfDevice, GryfOutput, GryfPwm

from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_TYPE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util.color import value_to_brightness, brightness_to_value

from .entity import GryfConfigFlowEntity, GryfYamlEntity
from .const import (
    CONF_API,
    CONF_DEVICES,
    CONF_ID,
    CONF_NAME,
    DOMAIN,
    Platforms
)

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None,
) -> None:
    """Set up the Light platform."""

    lights = []
    pwm = []

    for conf in hass.data[DOMAIN].get(Platforms.LIGHT, {}):
        device = GryfOutput(
            conf.get(CONF_NAME),
            conf.get(CONF_ID) // 10,
            conf.get(CONF_ID) % 10,
            hass.data[DOMAIN][CONF_API],
        )
        lights.append(GryfYamlLight(device))

    for conf in hass.data[DOMAIN].get(Platforms.PWM, {}):
        device = GryfPwm(
            conf.get(CONF_NAME),
            conf.get(CONF_ID) // 10,
            conf.get(CONF_ID) % 10,
            hass.data[DOMAIN][CONF_API],
        )
        pwm.append(GryfYamlPwm(device))

    async_add_entities(lights)
    async_add_entities(pwm)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Config flow for Light platform."""
    lights = []
    pwm = []

    for conf in config_entry.data[CONF_DEVICES]:
        if conf.get(CONF_TYPE) == Platforms.LIGHT:
            device = GryfOutput(
                conf.get(CONF_NAME),
                conf.get(CONF_ID) // 10,
                conf.get(CONF_ID) % 10,
                config_entry.runtime_data[CONF_API],
            )
            lights.append(GryfConfigFlowLight(device, config_entry))
        elif conf.get(CONF_TYPE) == Platforms.PWM:
            device = GryfPwm(
                conf.get(CONF_NAME),
                conf.get(CONF_ID) // 10,
                conf.get(CONF_ID) % 10,
                config_entry.runtime_data[CONF_API],
            )
            pwm.append(GryfConfigFlowPwm(device, config_entry))

    async_add_entities(lights)
    async_add_entities(pwm)


class GryfLightBase(LightEntity, RestoreEntity):
    """Gryf Light entity base."""

    _is_on = False
    _device: _GryfDevice
    _attr_color_mode = ColorMode.ONOFF
    _attr_supported_color_modes = {ColorMode.ONOFF}

    @property
    def is_on(self):
        """Return is on."""

        return self._is_on

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()

        if(last_state := await self.async_get_last_state()) is not None:
            self._attr_is_on = last_state.state == "on"

    async def async_update(self, is_on):
        """Update state."""

        self._is_on = is_on
        if is_on:
            self._attr_icon = "mdi:lightbulb"
        else:
            self._attr_icon = "mdi:lightbulb-off"

        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn light on."""

        await self._device.turn_on()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn light off."""

        await self._device.turn_off()


class GryfConfigFlowLight(GryfConfigFlowEntity, GryfLightBase):
    """Gryf Smart config flow Light class."""

    def __init__(
        self,
        device: _GryfDevice,
        config_entry: ConfigEntry,
    ) -> None:
        """Init the Gryf Light."""

        self._config_entry = config_entry
        super().__init__(config_entry, device)
        self._device.subscribe(self.async_update)


class GryfYamlLight(GryfYamlEntity, GryfLightBase):
    """Gryf Smart Yaml Light class."""

    def __init__(self, device: _GryfDevice) -> None:
        """Init the Gryf Light."""

        super().__init__(device)
        device.subscribe(self.async_update)

class GryfPwmBase(LightEntity):
    """Gryf Pwm entity base."""

    _is_on = False
    _brightness = 0
    _device: _GryfDevice
    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _last_brightness = 0

    @property
    def brightness(self) -> int | None:
        """The brightness property."""
        return self._brightness

    @property
    def is_on(self) -> bool:
        """The is_on property."""

        return self._is_on

    async def async_update(self, brightness):
        """Update state."""

        self._is_on = bool(int(brightness))
        self._brightness = value_to_brightness((0, 100), int(brightness))
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn pwm on."""
        brightness = kwargs.get("brightness")
        if brightness is not None:
            percentage_brightness = int(brightness_to_value((0, 100), brightness))
            await self._device.set_level(percentage_brightness)

            if brightness:
                self._last_brightness = brightness
        else:
            await self._device.set_level(self._last_brightness)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn pwm off."""

        await self._device.set_level(0)


class GryfConfigFlowPwm(GryfConfigFlowEntity, GryfPwmBase):
    """Gryf Smart config flow Light class."""

    def __init__(
        self,
        device: _GryfDevice,
        config_entry: ConfigEntry,
    ) -> None:
        """Init the Gryf Light."""

        self._config_entry = config_entry
        super().__init__(config_entry, device)
        self._device.subscribe(self.async_update)


class GryfYamlPwm(GryfYamlEntity, GryfPwmBase):
    """Gryf Smart Yaml Light class."""

    def __init__(self, device: _GryfDevice) -> None:
        """Init the Gryf Light."""

        super().__init__(device)
        device.subscribe(self.async_update)
