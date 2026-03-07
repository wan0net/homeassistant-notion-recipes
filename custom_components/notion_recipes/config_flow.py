"""Config flow for Notion Recipes integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import CONF_API_KEY, CONF_SCAN_INTERVAL
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import CONF_DATABASE_ID, DEFAULT_SCAN_INTERVAL, DOMAIN
from .notion_client import NotionClient, parse_database_id

_LOGGER = logging.getLogger(__name__)


class NotionRecipesConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Notion Recipes."""

    VERSION = 1

    def __init__(self) -> None:
        self._api_key: str = ""
        self._database_id: str = ""
        self._db_meta: dict = {}
        self._client: NotionClient | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> dict:
        errors: dict[str, str] = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY]
            session = async_get_clientsession(self.hass)
            client = NotionClient(session, api_key)

            try:
                valid = await client.validate_api_key()
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            else:
                if not valid:
                    errors[CONF_API_KEY] = "invalid_auth"
                else:
                    self._api_key = api_key
                    self._client = client
                    return await self.async_step_database()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_API_KEY): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.PASSWORD)
                ),
            }),
            errors=errors,
        )

    async def async_step_database(
        self, user_input: dict[str, Any] | None = None
    ) -> dict:
        errors: dict[str, str] = {}

        if user_input is not None:
            db_id = parse_database_id(user_input[CONF_DATABASE_ID])
            try:
                db = await self._client.get_database(db_id)
            except aiohttp.ClientResponseError as err:
                if err.status == 404:
                    errors[CONF_DATABASE_ID] = "database_not_found"
                elif err.status == 401:
                    errors[CONF_DATABASE_ID] = "database_not_shared"
                else:
                    errors["base"] = "cannot_connect"
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            else:
                self._database_id = db_id
                self._db_meta = db
                db_title = self._get_db_title()
                await self.async_set_unique_id(self._database_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=db_title,
                    data={
                        CONF_API_KEY: self._api_key,
                        CONF_DATABASE_ID: self._database_id,
                    },
                )

        return self.async_show_form(
            step_id="database",
            data_schema=vol.Schema({
                vol.Required(CONF_DATABASE_ID): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.URL)
                ),
            }),
            errors=errors,
        )

    def _get_db_title(self) -> str:
        parts = self._db_meta.get("title", [])
        return "".join(p.get("plain_text", "") for p in parts) or "Recipes"

    @staticmethod
    @callback
    def async_get_options_flow(entry: ConfigEntry) -> OptionsFlow:
        return NotionRecipesOptionsFlow(entry)


class NotionRecipesOptionsFlow(OptionsFlow):
    """Handle options (scan interval)."""

    def __init__(self, entry: ConfigEntry) -> None:
        self._entry = entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> dict:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=self._entry.options.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): NumberSelector(
                        NumberSelectorConfig(min=60, max=3600, step=60, unit_of_measurement="s")
                    ),
                }
            ),
        )
