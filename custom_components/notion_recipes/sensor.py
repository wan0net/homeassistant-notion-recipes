"""Notion recipe sensor — exposes recipe list data for the Lovelace card."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
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
    async_add_entities([NotionRecipeSensor(coordinator, entry)])


class NotionRecipeSensor(CoordinatorEntity[RecipeCoordinator], SensorEntity):
    """Sensor that exposes Notion recipes for the recipe card.

    State is the total recipe count.
    Attributes contain the full recipe list and available tags.
    """

    _attr_icon = "mdi:silverware-fork-knife"

    def __init__(
        self, coordinator: RecipeCoordinator, entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_recipes"
        self._attr_name = f"{entry.title}"

    @property
    def native_value(self) -> int:
        if not self.coordinator.data:
            return 0
        return len(self.coordinator.data.get("recipes", []))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if not self.coordinator.data:
            return {"recipes": [], "tags": []}

        data = self.coordinator.data
        return {
            "recipes": [
                {
                    "id": r["id"],
                    "name": r["name"],
                    "ingredients": r["ingredients"],
                    "method": r["method"],
                    "link": r["link"],
                    "tags": r.get("tags", []),
                    "cover": r.get("cover"),
                    "url": r.get("url"),
                }
                for r in data["recipes"]
            ],
            "tags": data.get("tags", []),
        }
