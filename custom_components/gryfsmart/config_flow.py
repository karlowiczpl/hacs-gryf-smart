"""Handle the configuration flow for the Gryf Smart integration."""

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.config_entries import OptionsFlow

from .const import (
    BINARY_SENSOR_DEVICE_CLASS,

    CONF_COMMUNICATION,
    CONF_DEVICES,
    CONF_EXTRA,
    CONF_ID,
    CONF_MODULE_COUNT,
    CONF_NAME,
    CONF_PORT,
    CONF_TYPE,
    CONF_DEVICE_CLASS,
    CONF_TIME,
    CONF_NEGATION,
    CONF_TEMP_ID,
    CONF_OUT_ID,
    CONF_HYSTERESIS_LOOP,

    DEFAULT_PORT,
    DOMAIN,
    SWITCH_DEVICE_CLASS,

    CONFIG_FLOW_MENU_OPTIONS,
    Platforms
)

class GryfSmartConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gryf Smart ConfigFlow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH


    def __init__(self) -> None:
        """Initialize Gryf Smart ConfigFlow."""
        super().__init__()

        self._config_data: dict[str, Any] = {
            CONF_DEVICES: [],
            CONF_COMMUNICATION: {}
        }

        self._unique_id: str
        self._last_id = 11
        self._last_name = ""

        self._editing_platform_function = {
            Platforms.PWM: self.async_step_pwm,
            Platforms.TEMPERATURE: self.async_step_temperature,
            Platforms.INPUT: self.async_step_input,
            Platforms.LIGHT: self.async_step_light,
            Platforms.BINARY_SENSOR: self.async_step_binary_sensor,
            Platforms.SWITCH: self.async_step_output,
            Platforms.CLIMATE: self.async_step_climate,
            Platforms.LOCK: self.async_step_lock,
            Platforms.COVER: self.async_step_cover,
            Platforms.GATE: self.async_step_gate,
        }       

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """First config flow step, selecting communication parameters."""

        errors = {}

        if user_input:
            self._config_data[CONF_COMMUNICATION][CONF_PORT] = user_input[CONF_PORT]
            self._config_data[CONF_COMMUNICATION][CONF_MODULE_COUNT] = user_input[CONF_MODULE_COUNT]

            self._unique_id = user_input[CONF_PORT]

            await self.async_set_unique_id(self._unique_id)
            self._abort_if_unique_id_configured()

            return await self.async_step_device_menu()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): str,
                    vol.Required(CONF_MODULE_COUNT, default=1): int,
                }
            ),
            errors=errors,
        )

    async def async_step_device_menu(
        self,
        user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Show menu step."""

        return self.async_show_menu(
            step_id="device_menu",
            menu_options=CONFIG_FLOW_MENU_OPTIONS,
        )

    async def async_step_add_device(
        self,
        user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Add new device."""

        return self.async_show_menu(
            step_id="add_device",
            menu_options=Platforms.PUBLIC_NAMES,
        )

    async def async_step_light(
        self,
        user_input: dict[str, Any] | None=None,
        edited: dict[str, Any] | None=None,
    ) -> config_entries.ConfigFlowResult:
        if user_input:

            if user_input[CONF_ID] and user_input[CONF_NAME]:
                entity_data = {
                    CONF_TYPE: Platforms.LIGHT,
                    CONF_ID: user_input[CONF_ID],
                    CONF_NAME: user_input[CONF_NAME],
                }
                self._config_data[CONF_DEVICES].append(entity_data)
                self._last_id = user_input[CONF_ID]
            else:
                return await self.async_step_add_device(None)

        return self.async_show_form(
            step_id=Platforms.LIGHT,
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_NAME, default=edited[CONF_NAME] if edited else ""): str, 
                    vol.Optional(CONF_ID, default=edited[CONF_ID] if edited else self._last_id): int,
                }
            )
        )

    async def async_step_output(
        self,
        user_input: dict[str, Any] | None=None,
        edited: dict[str, Any] | None=None,
    ) -> config_entries.ConfigFlowResult:
        if user_input:

            if user_input[CONF_NAME] and user_input[CONF_ID]:
                entity_data = {
                    CONF_TYPE: Platforms.SWITCH,
                    CONF_ID: user_input[CONF_ID],
                    CONF_NAME: user_input[CONF_NAME],
                    CONF_EXTRA: user_input[CONF_DEVICE_CLASS],
                }
                self._config_data[CONF_DEVICES].append(entity_data)
                self._last_id = user_input[CONF_ID]
            else:
                return await self.async_step_add_device(None)

        return self.async_show_form(
            step_id=Platforms.SWITCH,
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_NAME, default=edited[CONF_NAME] if edited else self._last_name): str, 
                    vol.Optional(CONF_ID, default=edited[CONF_ID] if edited else self._last_id): int,
                    vol.Required(CONF_DEVICE_CLASS, default=edited[CONF_EXTRA] if edited and edited[CONF_EXTRA] else "switch"): vol.In(SWITCH_DEVICE_CLASS),
                }
            )
        )

    async def async_step_binary_sensor(
        self,
        user_input: dict[str, Any] | None=None,
        edited: dict[str, Any] | None=None,
    ) -> config_entries.ConfigFlowResult:
        if user_input:

            if user_input[CONF_ID] and user_input[CONF_NAME]:
                entity_data = {
                    CONF_TYPE: Platforms.BINARY_SENSOR,
                    CONF_ID: user_input[CONF_ID],
                    CONF_NAME: user_input[CONF_NAME],
                    CONF_EXTRA: user_input[CONF_DEVICE_CLASS],
                    CONF_NEGATION: user_input[CONF_NEGATION],
                }
                self._config_data[CONF_DEVICES].append(entity_data)
                self._last_id = user_input[CONF_ID]
            else:
                return await self.async_step_add_device(None)

        return self.async_show_form(
            step_id=Platforms.BINARY_SENSOR,
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_NAME, default=edited[CONF_NAME] if edited else self._last_name): str, 
                    vol.Optional(CONF_ID, default=edited[CONF_ID] if edited else self._last_id): int,
                    vol.Required(CONF_NEGATION, default=edited[CONF_NEGATION] if edited and edited[CONF_NEGATION] else 0): bool,
                    vol.Required(CONF_DEVICE_CLASS, default=edited[CONF_EXTRA] if edited and edited[CONF_EXTRA] else "door"): vol.In(BINARY_SENSOR_DEVICE_CLASS),
                }
            )
        )

    async def async_step_cover(
        self,
        user_input: dict[str, Any] | None=None,
        edited: dict[str, Any] | None=None,
    ) -> config_entries.ConfigFlowResult:
        if user_input:

            if user_input[CONF_ID] and user_input[CONF_NAME]:
                entity_data = {
                    CONF_TYPE: Platforms.COVER,
                    CONF_ID: user_input[CONF_ID],
                    CONF_NAME: user_input[CONF_NAME],
                    CONF_EXTRA: user_input[CONF_TIME],
                }
                self._config_data[CONF_DEVICES].append(entity_data)
                self._last_id = user_input[CONF_ID]
            else:
                return await self.async_step_add_device(None)

        return self.async_show_form(
            step_id=Platforms.COVER,
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_NAME, default=edited[CONF_NAME] if edited else self._last_name): str, 
                    vol.Optional(CONF_ID, default=edited[CONF_ID] if edited else self._last_id): int,
                    vol.Required(CONF_TIME, default=edited[CONF_EXTRA] if edited else 100): int,
                }
            )
        )

    async def async_step_lock(
        self,
        user_input: dict[str, Any] | None=None,
        edited: dict[str, Any] | None=None,
    ) -> config_entries.ConfigFlowResult:
        if user_input:

            if user_input[CONF_ID] and user_input[CONF_NAME]:
                entity_data = {
                    CONF_TYPE: Platforms.LOCK,
                    CONF_ID: user_input[CONF_ID],
                    CONF_NAME: user_input[CONF_NAME],
                }
                self._config_data[CONF_DEVICES].append(entity_data)
                self._last_id = user_input[CONF_ID]
            else:
                return await self.async_step_add_device(None)

        return self.async_show_form(
            step_id=Platforms.LOCK,
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_NAME, default=edited[CONF_NAME] if edited else self._last_name): str, 
                    vol.Optional(CONF_ID, default=edited[CONF_ID] if edited else self._last_id): int,
                }
            )
        )

    async def async_step_climate(
        self,
        user_input: dict[str, Any] | None=None,
        edited: dict[str, Any] | None=None,
    ) -> config_entries.ConfigFlowResult:
        if user_input:

            if user_input[CONF_OUT_ID] and user_input[CONF_NAME]:
                entity_data = {
                    CONF_TYPE: Platforms.CLIMATE,
                    CONF_ID: user_input[CONF_OUT_ID],
                    CONF_EXTRA: user_input[CONF_TEMP_ID],
                    CONF_HYSTERESIS_LOOP: user_input[CONF_HYSTERESIS_LOOP],
                    CONF_NAME: user_input[CONF_NAME],
                }
                self._config_data[CONF_DEVICES].append(entity_data)
                self._last_id = user_input[CONF_OUT_ID]
            else:
                return await self.async_step_add_device(None)

        return self.async_show_form(
            step_id=Platforms.CLIMATE,
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_NAME, default=edited[CONF_NAME] if edited else self._last_name): str, 
                    vol.Optional(CONF_OUT_ID, default=edited[CONF_ID] if edited else self._last_id): int,
                    vol.Optional(CONF_TEMP_ID, default=edited[CONF_EXTRA] if edited and edited[CONF_EXTRA] else 0): int,
                    vol.Optional(CONF_HYSTERESIS_LOOP, default=edited[CONF_HYSTERESIS_LOOP] if edited and edited[CONF_HYSTERESIS_LOOP] else 0): int,
                }
            )
        )

    async def async_step_pwm(
        self,
        user_input: dict[str, Any] | None=None,
        edited: dict[str, Any] | None=None,
    ) -> config_entries.ConfigFlowResult:
        if user_input:

            if user_input[CONF_ID] and user_input[CONF_NAME]:
                entity_data = {
                    CONF_TYPE: Platforms.PWM,
                    CONF_ID: user_input[CONF_ID],
                    CONF_NAME: user_input[CONF_NAME],
                }
                self._config_data[CONF_DEVICES].append(entity_data)
                self._last_id = user_input[CONF_ID]
            else:
                return await self.async_step_add_device(None)

        return self.async_show_form(
            step_id=Platforms.PWM,
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_NAME, default=edited[CONF_NAME] if edited else self._last_name): str, 
                    vol.Optional(CONF_ID, default=edited[CONF_ID] if edited else self._last_id): int,
                }
            )
        )

    async def async_step_temperature(
        self,
        user_input: dict[str, Any] | None=None,
        edited: dict[str, Any] | None=None,
    ) -> config_entries.ConfigFlowResult:
        if user_input:

            if user_input[CONF_ID] and user_input[CONF_NAME]:
                entity_data = {
                    CONF_TYPE: Platforms.TEMPERATURE,
                    CONF_ID: user_input[CONF_ID],
                    CONF_NAME: user_input[CONF_NAME],
                }
                self._config_data[CONF_DEVICES].append(entity_data)
                self._last_id = user_input[CONF_ID]
            else:
                return await self.async_step_add_device(None)

        return self.async_show_form(
            step_id=Platforms.TEMPERATURE,
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_NAME, default=edited[CONF_NAME] if edited else self._last_name): str, 
                    vol.Optional(CONF_ID, default=edited[CONF_ID] if edited else self._last_id): int,
                }
            )
        )

    async def async_step_input(
        self,
        user_input: dict[str, Any] | None=None,
        edited: dict[str, Any] | None=None,
    ) -> config_entries.ConfigFlowResult:
        if user_input:

            if user_input[CONF_ID] and user_input[CONF_NAME]:
                entity_data = {
                    CONF_TYPE: Platforms.INPUT,
                    CONF_ID: user_input[CONF_ID],
                    CONF_NAME: user_input[CONF_NAME],
                }
                self._config_data[CONF_DEVICES].append(entity_data)
                self._last_id = user_input[CONF_ID]
            else:
                return await self.async_step_add_device(None)

        return self.async_show_form(
            step_id=Platforms.INPUT,
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_NAME, default=edited[CONF_NAME] if edited else self._last_name): str, 
                    vol.Optional(CONF_ID, default=edited[CONF_ID] if edited else self._last_id): int,
                }
            )
        )

    async def async_step_gate(
        self,
        user_input: dict[str, Any] | None=None,
        edited: dict[str, Any] | None=None,
    ) -> config_entries.ConfigFlowResult:
        if user_input:

            if user_input[CONF_ID] and user_input[CONF_NAME]:
                entity_data = {
                    CONF_TYPE: Platforms.GATE,
                    CONF_ID: user_input[CONF_ID],
                    CONF_NAME: user_input[CONF_NAME],
                }
                self._config_data[CONF_DEVICES].append(entity_data)
                self._last_id = user_input[CONF_ID]
            else:
                return await self.async_step_add_device(None)

        return self.async_show_form(
            step_id=Platforms.GATE,
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_NAME, default=edited[CONF_NAME] if edited else self._last_name): str, 
                    vol.Optional(CONF_ID, default=edited[CONF_NAME] if edited else self._last_id): int,
                }
            )
        )

    async def async_step_edit_device(
        self,
        user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Select device to edit."""

        if not self._config_data[CONF_DEVICES]:
            return await self.async_step_device_menu()

        if user_input:
            edit_index = int(user_input["device_index"])
            current_device = self._config_data[CONF_DEVICES][edit_index].copy()
            device_type = self._config_data[CONF_DEVICES][edit_index][CONF_TYPE]

            del self._config_data[CONF_DEVICES][edit_index]

            return await self._editing_platform_function[device_type](None, edited=current_device)

        devices = [
            selector.SelectOptionDict(
                value=str(idx), label=f"{dev[CONF_NAME]} (ID: {dev[CONF_ID]})"
            )
            for idx, dev in enumerate(self._config_data[CONF_DEVICES])
        ]

        return self.async_show_form(
            step_id="edit_device",
            data_schema=vol.Schema(
                {
                    vol.Required("device_index"): selector.SelectSelector(
                        selector.SelectSelectorConfig(options=devices)
                    )
                }
            ),
        )

    async def async_step_finish(
        self, 
        user_input: dict[str, Any] | None=None,
    ) -> config_entries.ConfigFlowResult:
        """Finish the config flow."""

        return self.async_create_entry(
            title=f"GryfSmart: {self._config_data[CONF_COMMUNICATION][CONF_PORT]}",
            data=self._config_data,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""

        return GryfSmartOptionsFlow()

class GryfSmartOptionsFlow(OptionsFlow, GryfSmartConfigFlow):

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None=None,
    ) -> config_entries.ConfigFlowResult:

        self._config_data = dict(self.config_entry.data)
        self._config_data.update(dict(self.config_entry.options or {}))

        return await self.async_step_device_menu(None)
        
    async def async_step_communication(
        self,
        user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """First config flow step, selecting communication parameters."""

        errors = {}

        if user_input:
            self._config_data[CONF_COMMUNICATION][CONF_PORT] = user_input[CONF_PORT]
            self._config_data[CONF_COMMUNICATION][CONF_MODULE_COUNT] = user_input[CONF_MODULE_COUNT]

            return await self.async_step_device_menu()

        return self.async_show_form(
            step_id="communication",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PORT, default=self._config_data[CONF_COMMUNICATION][CONF_PORT]): str,
                    vol.Required(CONF_MODULE_COUNT, default=self._config_data[CONF_COMMUNICATION][CONF_MODULE_COUNT]): int,
                }
            ),
            errors=errors,
        )

    async def async_step_finish(
        self,
        user_input: dict[str, Any] | None=None,
    ) -> config_entries.ConfigFlowResult:

        self.hass.config_entries.async_update_entry(
            self.config_entry,
            options=self._config_data,
        )
        return self.async_create_entry(title=self._config_data[CONF_COMMUNICATION][CONF_PORT], data={})

