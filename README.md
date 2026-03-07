# Notion Recipes for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Browse and select recipes from a Notion database in Home Assistant. Includes a custom Lovelace card with gallery view, tag filtering, search, and detail modal.

## Features

- **Recipe sensor** — exposes all recipes from a Notion database (name, ingredients, method, link, tags, cover image)
- **Recipe select entity** — choose the active recipe; selected recipe details available as entity attributes (great for ESPHome displays)
- **Custom Lovelace card** — gallery grid with cover images, tag filtering, text search, and click-to-expand detail view
- **Disk cache** — instant load on HA restart, graceful fallback on API errors

## Notion Database Schema

Your Notion database should have these properties:

| Property | Type | Description |
|----------|------|-------------|
| Name | Title | Recipe name |
| Ingredients | Text | Ingredient list |
| Method | Text | Cooking instructions |
| Link | URL | Source recipe URL (optional) |
| Tags | Multi-select | Categories like Dinner, Dessert, Easy (optional) |

Page cover images are used as recipe thumbnails in the card.

## Installation

### HACS (Recommended)

1. Open HACS → Integrations → three-dot menu → **Custom repositories**
2. Add `wan0net/homeassistant-notion-recipes` as **Integration**
3. Download and restart Home Assistant

### Manual

Copy `custom_components/notion_recipes/` to your HA `custom_components/` directory and restart.

## Setup

1. Create a [Notion internal integration](https://www.notion.so/my-integrations) and copy the API key
2. Share your recipe database with the integration in Notion (database → `...` menu → Connections)
3. In HA: **Settings → Integrations → Add → Notion Recipes**
4. Paste the API key, then the database URL or ID

## Lovelace Card

The card auto-registers on setup. Add it to a dashboard:

```yaml
type: custom:notion-recipe-card
entity: sensor.recipes
title: My Recipes                        # optional
select_entity: select.recipes_selected   # optional, syncs selection
```

## Entities

| Entity | Type | Description |
|--------|------|-------------|
| `sensor.recipes` | Sensor | State: recipe count. Attributes: full recipe list and tags |
| `select.recipes_selected` | Select | Pick active recipe. Attributes: selected recipe details |

## Options

| Option | Default | Description |
|--------|---------|-------------|
| Poll interval | 600s | How often to sync from Notion |
