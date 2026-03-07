"""Tests for the Notion API client."""
from custom_components.notion_recipes.notion_client import parse_database_id


def test_parse_database_id_raw_hex():
    raw = "6f3852d5fa57488c9072aef78502dd8a"
    assert parse_database_id(raw) == "6f3852d5-fa57-488c-9072-aef78502dd8a"


def test_parse_database_id_with_dashes():
    raw = "6f3852d5-fa57-488c-9072-aef78502dd8a"
    assert parse_database_id(raw) == "6f3852d5-fa57-488c-9072-aef78502dd8a"


def test_parse_database_id_from_url():
    url = "https://www.notion.so/myworkspace/6f3852d5fa57488c9072aef78502dd8a?v=abc"
    assert parse_database_id(url) == "6f3852d5-fa57-488c-9072-aef78502dd8a"


def test_parse_database_id_notion_url_with_title():
    url = "https://www.notion.so/Recipes-6f3852d5fa57488c9072aef78502dd8a"
    assert parse_database_id(url) == "6f3852d5-fa57-488c-9072-aef78502dd8a"
