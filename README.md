# Notion Recipes

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![License: BSD-3-Clause](https://img.shields.io/badge/License-BSD--3--Clause-blue.svg)](LICENSE)
[![AI Generated](https://img.shields.io/badge/AI%20Generated-Claude-blueviolet)](https://claude.ai)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=wan0net&repository=homeassistant-notion-recipes&category=integration)

<p align="center"><strong>Browse and cook recipes from your Notion database, right on the Home Assistant dashboard</strong><br>Gallery card with images, prep time, servings, and one-tap ingredient lists.</p>

<p align="center">
  <a href="#why-notion-recipes">Why</a> &bull;
  <a href="#how-it-works">How It Works</a> &bull;
  <a href="#getting-started">Getting Started</a> &bull;
  <a href="#entities">Entities</a> &bull;
  <a href="#options">Options</a> &bull;
  <a href="#limitations">Limitations</a> &bull;
  <a href="#development">Development</a>
</p>

---

> **Status** — Functional and in active use. HACS custom repository. Notion API cover image URLs expire after one hour and are refreshed on each poll; no other known issues.

## Why Notion Recipes

Notion is a practical place to keep a recipe collection — rich text, cover photos, tags, and a URL back to the original source all in one row. What it lacks is any presence on the kitchen dashboard. This integration bridges that gap: it syncs your Notion recipe database into Home Assistant as sensor and select entities, and ships a Lovelace card that turns those entities into a browsable gallery. No cloud intermediary, no webhooks — just a scheduled poll from your HA instance directly to the Notion API.

The select entity is useful beyond the dashboard. Because the selected recipe and its full details (ingredients, method, source URL) are exposed as entity attributes, ESPHome displays and automations can read them without any additional scripting.

## How It Works

```
Notion API
    |
    |  HTTP (Notion Integration token)
    v
HA Integration (custom_component/notion_recipes)
    |
    |  Poll every 10 min (configurable)
    |  Disk cache for instant restart
    v
Sensor entities         Select entity
(recipe list + tags)    (active recipe + details)
    |                       |
    +----------+------------+
               |
               v
    Lovelace Gallery Card
    (notion-recipe-card)
    Gallery grid, tag filter,
    text search, detail modal
```

The integration registers `notion-recipe-card` as a Lovelace resource automatically on setup — no manual resource configuration required.

## Notion Database Schema

Your Notion database must have the following properties. Property names are case-sensitive.

| Property | Type | Notes |
|----------|------|-------|
| Name | Title | Recipe name |
| Ingredients | Text | Ingredient list |
| Method | Text | Cooking instructions |
| Link | URL | Source recipe URL (optional) |
| Tags | Multi-select | Categories such as Dinner, Dessert, Easy (optional) |

Page cover images are used as recipe thumbnails in the gallery card. Only database properties are fetched — page body blocks are not read.

## Features

- **Recipe sensor** — exposes all recipes from a Notion database (name, ingredients, method, link, tags, cover image)
- **Recipe select entity** — choose the active recipe; selected recipe details are available as entity attributes, useful for ESPHome displays and automations
- **`notion-recipe-card`** — built-in Lovelace card with gallery grid, cover images, tag filtering, text search, and click-to-expand detail view
- **Disk cache** — instant load on HA restart, graceful fallback on API errors
- Configurable poll interval (default 10 min)

## Entities

| Entity | Type | Description |
|--------|------|-------------|
| `sensor.<db>` | Sensor | State: recipe count. Attributes: full recipe list and available tags |
| `select.<db>_selected` | Select | Pick the active recipe. Attributes: selected recipe details (name, ingredients, method, link) |

## Options

| Option | Default | Description |
|--------|---------|-------------|
| Poll interval | 600 s | How often to sync from the Notion API |

## Limitations

- Notion page body content is not fetched — only database properties (Name, Ingredients, Method, Link, Tags)
- Cover image URLs from Notion expire after one hour; they are refreshed on the next poll cycle
- Notion API rate limit is 3 req/s — increase the poll interval for large databases

## Getting Started

### HACS (Recommended)

1. Open HACS → Integrations → three-dot menu → **Custom repositories**
2. Add `wan0net/homeassistant-notion-recipes` as **Integration**
3. Download and restart Home Assistant

### Manual

Copy `custom_components/notion_recipes/` into your HA `custom_components/` directory and restart Home Assistant.

### Configuration

1. Create a [Notion internal integration](https://www.notion.so/my-integrations) and copy the API key
2. Share your recipe database with the integration in Notion (database → `...` menu → Connections)
3. In HA: **Settings → Integrations → Add → Notion Recipes**
4. Paste the API key, then the database URL or ID

Once configured, add the card to any dashboard:

```yaml
type: custom:notion-recipe-card
entity: sensor.recipes
title: My Recipes                        # optional
select_entity: select.recipes_selected   # optional, syncs selection
```

## Development

```bash
pip install -r requirements-dev.txt
pytest
```

This integration was generated by [Claude](https://claude.ai) (Anthropic) and validated by the maintainer. All code, tests, and the Lovelace card were authored by AI with human review and testing.

## License

BSD-3-Clause — see [LICENSE](LICENSE).
