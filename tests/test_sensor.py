"""Tests for the Notion recipe sensor."""
from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.notion_recipes.sensor import NotionRecipeSensor


RECIPES = [
    {
        "id": "p1",
        "name": "Baked Potato",
        "ingredients": "1 potato\nButter",
        "method": "Bake at 200C.",
        "link": None,
        "tags": [{"name": "Dinner", "color": "orange"}],
        "cover": None,
        "url": "https://notion.so/p1",
    },
    {
        "id": "p2",
        "name": "Chocolate Cake",
        "ingredients": "200g chocolate\n4 eggs",
        "method": "Melt. Mix. Bake.",
        "link": "https://example.com/cake",
        "tags": [{"name": "Dessert", "color": "purple"}],
        "cover": "https://example.com/cake.jpg",
        "url": "https://notion.so/p2",
    },
]

TAGS = [
    {"name": "Dessert", "color": "purple"},
    {"name": "Dinner", "color": "orange"},
]

_SENTINEL = object()


def make_sensor(data=_SENTINEL):
    coordinator = MagicMock()
    coordinator.data = {"recipes": RECIPES, "tags": TAGS} if data is _SENTINEL else data

    entry = MagicMock()
    entry.entry_id = "test-entry-id"
    entry.title = "Recipes"

    return NotionRecipeSensor(coordinator, entry)


def test_native_value_counts_recipes():
    sensor = make_sensor()
    assert sensor.native_value == 2


def test_native_value_no_data():
    sensor = make_sensor(data=None)
    assert sensor.native_value == 0


def test_attributes_contains_all_recipes():
    sensor = make_sensor()
    attrs = sensor.extra_state_attributes
    names = [r["name"] for r in attrs["recipes"]]
    assert "Baked Potato" in names
    assert "Chocolate Cake" in names


def test_attributes_recipe_fields():
    sensor = make_sensor()
    attrs = sensor.extra_state_attributes
    cake = next(r for r in attrs["recipes"] if r["name"] == "Chocolate Cake")
    assert cake["ingredients"] == "200g chocolate\n4 eggs"
    assert cake["method"] == "Melt. Mix. Bake."
    assert cake["link"] == "https://example.com/cake"
    assert cake["cover"] == "https://example.com/cake.jpg"
    assert cake["url"] == "https://notion.so/p2"


def test_attributes_tags():
    sensor = make_sensor()
    attrs = sensor.extra_state_attributes
    tag_names = [t["name"] for t in attrs["tags"]]
    assert "Dinner" in tag_names
    assert "Dessert" in tag_names


def test_attributes_no_data():
    sensor = make_sensor(data=None)
    attrs = sensor.extra_state_attributes
    assert attrs == {"recipes": [], "tags": []}


def test_unique_id():
    sensor = make_sensor()
    assert sensor.unique_id == "test-entry-id_recipes"


def test_icon():
    sensor = make_sensor()
    assert sensor.icon == "mdi:silverware-fork-knife"
