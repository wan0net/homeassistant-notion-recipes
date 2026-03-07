"""Notion recipe select entity — for choosing the active recipe."""
from __future__ import annotations

from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import RecipeCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: RecipeCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NotionRecipeSelect(coordinator, entry)])


class NotionRecipeSelect(CoordinatorEntity[RecipeCoordinator], SelectEntity):
    """Select entity for choosing the active recipe.

    When a recipe is selected, its full details are exposed as attributes.
    Useful for ESPHome displays (Guition) and automations.
    """

    _attr_icon = "mdi:book-open-page-variant"

    def __init__(
        self, coordinator: RecipeCoordinator, entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_recipe_select"
        self._attr_name = f"{entry.title} Selected"
        self._selected: str | None = None

    @property
    def options(self) -> list[str]:
        if not self.coordinator.data:
            return []
        return [r["name"] for r in self.coordinator.data.get("recipes", [])]

    @property
    def current_option(self) -> str | None:
        if self._selected and self._selected in self.options:
            return self._selected
        return None

    async def async_select_option(self, option: str) -> None:
        self._selected = option
        self.async_write_ha_state()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if not self._selected or not self.coordinator.data:
            return {}
        for recipe in self.coordinator.data.get("recipes", []):
            if recipe["name"] == self._selected:
                return {
                    "recipe_id": recipe["id"],
                    "ingredients": recipe["ingredients"],
                    "method": recipe["method"],
                    "link": recipe["link"],
                    "tags": [t["name"] for t in recipe.get("tags", [])],
                    "cover": recipe.get("cover"),
                    "url": recipe.get("url"),
                }
        return {}
