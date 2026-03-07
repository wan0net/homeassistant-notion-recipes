"""Test fixtures for Notion Recipes."""
from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

MOCK_API_KEY = "ntn_test_0123456789abcdef"
MOCK_DATABASE_ID = "12345678-1234-1234-1234-123456789012"


def make_page(
    page_id: str = "page-1",
    name: str = "Test Recipe",
    ingredients: str = "1 cup flour\n2 eggs",
    method: str = "Mix and bake.",
    link: str | None = None,
    tags: list[dict] | None = None,
    cover_url: str | None = None,
    archived: bool = False,
) -> dict:
    """Build a Notion page dict for testing."""
    page = {
        "id": page_id,
        "archived": archived,
        "url": f"https://www.notion.so/{page_id}",
        "properties": {
            "Name": {
                "type": "title",
                "title": [{"plain_text": name}],
            },
            "Ingredients": {
                "type": "rich_text",
                "rich_text": [{"plain_text": ingredients}] if ingredients else [],
            },
            "Method": {
                "type": "rich_text",
                "rich_text": [{"plain_text": method}] if method else [],
            },
            "Link": {
                "type": "url",
                "url": link,
            },
            "Tags": {
                "type": "multi_select",
                "multi_select": tags or [],
            },
        },
    }
    if cover_url:
        page["cover"] = {"type": "external", "external": {"url": cover_url}}
    return page


def make_database(title: str = "Recipes") -> dict:
    """Build a Notion database metadata dict."""
    return {
        "id": MOCK_DATABASE_ID,
        "title": [{"plain_text": title}],
        "properties": {
            "Name": {"type": "title"},
            "Ingredients": {"type": "rich_text"},
            "Method": {"type": "rich_text"},
            "Link": {"type": "url"},
            "Tags": {
                "type": "multi_select",
                "multi_select": {
                    "options": [
                        {"name": "Dinner", "color": "orange"},
                        {"name": "Dessert", "color": "purple"},
                        {"name": "Easy", "color": "yellow"},
                    ]
                },
            },
        },
    }


@pytest.fixture
def mock_client():
    client = AsyncMock()
    client.validate_api_key.return_value = True
    client.get_database.return_value = make_database()
    client.query_database.return_value = [
        make_page(
            page_id="p1",
            name="Baked Potato",
            ingredients="1 potato\nButter\nSalt",
            method="Bake at 200C for 1 hour.",
            tags=[{"name": "Dinner", "color": "orange"}, {"name": "Easy", "color": "yellow"}],
        ),
        make_page(
            page_id="p2",
            name="Chocolate Cake",
            ingredients="200g chocolate\n200g butter\n4 eggs",
            method="Melt chocolate. Mix. Bake.",
            tags=[{"name": "Dessert", "color": "purple"}],
            link="https://example.com/cake",
        ),
    ]
    return client
