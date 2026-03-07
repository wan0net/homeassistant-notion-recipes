"""Tests for the recipe coordinator transform logic."""
from custom_components.notion_recipes.coordinator import transform_recipe_pages
from conftest import make_page


def test_transform_basic():
    pages = [
        make_page(page_id="p1", name="Steak", tags=[{"name": "Dinner", "color": "orange"}]),
        make_page(page_id="p2", name="Cake", tags=[{"name": "Dessert", "color": "purple"}]),
    ]
    result = transform_recipe_pages(pages)

    assert len(result["recipes"]) == 2
    # Sorted alphabetically
    assert result["recipes"][0]["name"] == "Cake"
    assert result["recipes"][1]["name"] == "Steak"

    assert len(result["tags"]) == 2
    tag_names = [t["name"] for t in result["tags"]]
    assert "Dinner" in tag_names
    assert "Dessert" in tag_names


def test_transform_skips_archived():
    pages = [
        make_page(page_id="p1", name="Active"),
        make_page(page_id="p2", name="Archived", archived=True),
    ]
    result = transform_recipe_pages(pages)
    assert len(result["recipes"]) == 1
    assert result["recipes"][0]["name"] == "Active"


def test_transform_extracts_all_fields():
    pages = [
        make_page(
            page_id="p1",
            name="Test",
            ingredients="flour, eggs",
            method="mix and bake",
            link="https://example.com",
            tags=[{"name": "Easy", "color": "yellow"}],
            cover_url="https://example.com/img.jpg",
        ),
    ]
    result = transform_recipe_pages(pages)
    recipe = result["recipes"][0]

    assert recipe["id"] == "p1"
    assert recipe["name"] == "Test"
    assert recipe["ingredients"] == "flour, eggs"
    assert recipe["method"] == "mix and bake"
    assert recipe["link"] == "https://example.com"
    assert recipe["cover"] == "https://example.com/img.jpg"
    assert len(recipe["tags"]) == 1
    assert recipe["tags"][0]["name"] == "Easy"


def test_transform_empty():
    result = transform_recipe_pages([])
    assert result["recipes"] == []
    assert result["tags"] == []


def test_transform_no_tags():
    pages = [make_page(page_id="p1", name="Plain", tags=[])]
    result = transform_recipe_pages(pages)
    assert len(result["recipes"]) == 1
    assert result["recipes"][0]["tags"] == []
    assert result["tags"] == []
