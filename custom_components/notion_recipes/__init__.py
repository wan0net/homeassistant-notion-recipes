"""Notion Recipes integration for Home Assistant."""
from __future__ import annotations

import logging
import uuid
from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_SCAN_INTERVAL, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.storage import Store

from .const import CONF_DATABASE_ID, DEFAULT_SCAN_INTERVAL, DOMAIN
from .coordinator import RecipeCoordinator
from .notion_client import NotionClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.SELECT]

_CARD_URL = "/notion_recipes/notion-recipe-card.js"
_CARD_REGISTERED = f"{DOMAIN}_card_registered"


async def _ensure_lovelace_resource(hass: HomeAssistant, url: str) -> None:
    """Register the card as a Lovelace resource."""
    resources = hass.data.get("lovelace", {}).get("resources")
    if resources is not None:
        try:
            existing = [r for r in resources.async_items() if url in r.get("url", "")]
            if existing:
                return
            await resources.async_create_item({"url": url, "res_type": "module"})
            return
        except Exception as err:
            _LOGGER.debug("Lovelace resource collection unavailable, using storage: %s", err)

    store = Store(hass, 1, "lovelace_resources")
    data = await store.async_load() or {"items": []}
    if any(url in item.get("url", "") for item in data.get("items", [])):
        return
    data.setdefault("items", []).append(
        {"id": uuid.uuid4().hex, "url": url, "type": "module"}
    )
    await store.async_save(data)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if not hass.data.get(_CARD_REGISTERED):
        await hass.http.async_register_static_paths([
            StaticPathConfig(
                _CARD_URL,
                str(Path(__file__).parent / "notion-recipe-card.js"),
                cache_headers=False,
            )
        ])
        await _ensure_lovelace_resource(hass, _CARD_URL)
        hass.data[_CARD_REGISTERED] = True

    session = async_get_clientsession(hass)
    client = NotionClient(session, entry.data[CONF_API_KEY])

    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    coordinator = RecipeCoordinator(
        hass=hass,
        client=client,
        database_id=entry.data[CONF_DATABASE_ID],
        scan_interval=scan_interval,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
