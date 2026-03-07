"""DataUpdateCoordinator for Notion recipe databases."""
from __future__ import annotations

import json
import logging
from datetime import timedelta
from pathlib import Path
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN
from .notion_client import NotionClient

_LOGGER = logging.getLogger(__name__)


def _get_title(page: dict) -> str:
    """Extract plain text title from a Notion page."""
    for prop in page.get("properties", {}).values():
        if prop.get("type") == "title":
            parts = prop.get("title", [])
            return "".join(p.get("plain_text", "") for p in parts)
    return "(Untitled)"


def _get_rich_text(page: dict, property_name: str) -> str:
    """Extract plain text from a rich_text property."""
    prop = page.get("properties", {}).get(property_name, {})
    if prop.get("type") == "rich_text":
        parts = prop.get("rich_text", [])
        return "".join(p.get("plain_text", "") for p in parts)
    return ""


def _get_url(page: dict, property_name: str) -> str | None:
    """Extract URL from a url property."""
    prop = page.get("properties", {}).get(property_name, {})
    if prop.get("type") == "url":
        return prop.get("url")
    return None


def _get_multiselect_values(page: dict, property_name: str) -> list[dict]:
    """Extract name+color pairs from a multi_select property."""
    prop = page.get("properties", {}).get(property_name, {})
    if prop.get("type") == "multi_select":
        return [
            {"name": o["name"], "color": o.get("color", "default")}
            for o in prop.get("multi_select", [])
        ]
    return []


def _get_cover_url(page: dict) -> str | None:
    """Extract cover image URL from a Notion page."""
    cover = page.get("cover")
    if not cover:
        return None
    cover_type = cover.get("type")
    if cover_type == "external":
        return cover.get("external", {}).get("url")
    if cover_type == "file":
        return cover.get("file", {}).get("url")
    return None


def transform_recipe_pages(pages: list[dict]) -> dict[str, Any]:
    """Transform raw Notion pages into recipe data.

    Pure function — no HA dependencies, easy to test.
    """
    recipes = []
    all_tags: dict[str, str] = {}

    for page in pages:
        if page.get("archived"):
            continue

        tags = _get_multiselect_values(page, "Tags")
        for tag in tags:
            all_tags[tag["name"]] = tag["color"]

        recipes.append(
            {
                "id": page["id"],
                "name": _get_title(page),
                "ingredients": _get_rich_text(page, "Ingredients"),
                "method": _get_rich_text(page, "Method"),
                "link": _get_url(page, "Link"),
                "tags": tags,
                "cover": _get_cover_url(page),
                "url": page.get("url"),
            }
        )

    recipes.sort(key=lambda r: r["name"].lower())

    return {
        "recipes": recipes,
        "tags": [
            {"name": name, "color": color}
            for name, color in sorted(all_tags.items())
        ],
    }


class RecipeCoordinator(DataUpdateCoordinator):
    """Polls a Notion recipe database and exposes recipe data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: NotionClient,
        database_id: str,
        scan_interval: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        self.client = client
        self.database_id = database_id
        self._cache_path = Path(hass.config.path(
            f".notion_recipes_cache_{database_id.replace('-', '')}.json"
        ))

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    def _load_cache_sync(self) -> dict[str, Any] | None:
        try:
            return json.loads(self._cache_path.read_text())
        except Exception:
            return None

    def _save_cache_sync(self, data: dict[str, Any]) -> None:
        try:
            self._cache_path.write_text(json.dumps(data))
        except Exception as err:
            _LOGGER.warning("Could not write recipe cache: %s", err)

    async def async_config_entry_first_refresh(self) -> None:
        cached = await self.hass.async_add_executor_job(self._load_cache_sync)
        if cached:
            self.data = cached
            _LOGGER.debug("Loaded %d recipes from cache", len(cached.get("recipes", [])))
        await super().async_config_entry_first_refresh()

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            pages = await self.client.query_database(self.database_id)
        except Exception as err:
            if self.data:
                _LOGGER.warning("Recipe fetch failed, using cached data: %s", err)
                return self.data
            raise UpdateFailed(f"Error fetching recipes: {err}") from err

        data = transform_recipe_pages(pages)
        self.hass.async_add_executor_job(self._save_cache_sync, data)
        return data
