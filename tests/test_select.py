"""Tests for the Notion recipe select entity."""
from __future__ import annotations

from unittest.mock import MagicMock, AsyncMock

import pytest

from custom_components.notion_recipes.select import NotionRecipeSelect


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


def make_select(data=None):
    coordinator = MagicMock()
    coordinator.data = data or {"recipes": RECIPES, "tags": []}

    entry = MagicMock()
    entry.entry_id = "test-entry-id"
    entry.title = "Recipes"

    select = NotionRecipeSelect(coordinator, entry)
    # Mock HA state writing since we're not in a real HA context
    select.async_write_ha_state = MagicMock()
    return select


def test_options_lists_recipe_names():
    select = make_select()
    assert select.options == ["Baked Potato", "Chocolate Cake"]


def test_options_empty_when_no_data():
    select = make_select()
    select.coordinator.data = None
    assert select.options == []


def test_current_option_none_by_default():
    select = make_select()
    assert select.current_option is None


@pytest.mark.asyncio
async def test_select_option_sets_current():
    select = make_select()
    await select.async_select_option("Baked Potato")
    assert select.current_option == "Baked Potato"


@pytest.mark.asyncio
async def test_select_option_writes_state():
    select = make_select()
    await select.async_select_option("Baked Potato")
    select.async_write_ha_state.assert_called_once()


def test_current_option_clears_if_removed():
    select = make_select()
    select._selected = "Deleted Recipe"
    assert select.current_option is None


def test_attributes_empty_when_nothing_selected():
    select = make_select()
    assert select.extra_state_attributes == {}


@pytest.mark.asyncio
async def test_attributes_expose_selected_recipe():
    select = make_select()
    await select.async_select_option("Chocolate Cake")
    attrs = select.extra_state_attributes
    assert attrs["recipe_id"] == "p2"
    assert attrs["ingredients"] == "200g chocolate\n4 eggs"
    assert attrs["method"] == "Melt. Mix. Bake."
    assert attrs["link"] == "https://example.com/cake"
    assert attrs["tags"] == ["Dessert"]
    assert attrs["cover"] == "https://example.com/cake.jpg"
    assert attrs["url"] == "https://notion.so/p2"


@pytest.mark.asyncio
async def test_attributes_empty_for_unknown_recipe():
    select = make_select()
    select._selected = "Nonexistent"
    assert select.extra_state_attributes == {}


def test_unique_id():
    select = make_select()
    assert select.unique_id == "test-entry-id_recipe_select"


def test_icon():
    select = make_select()
    assert select.icon == "mdi:book-open-page-variant"
