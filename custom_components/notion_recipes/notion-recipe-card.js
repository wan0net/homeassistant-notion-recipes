/**
 * Notion Recipe Card — custom Lovelace card for browsing Notion recipes.
 *
 * Config:
 *   type: custom:notion-recipe-card
 *   entity: sensor.recipes
 *   title: My Recipes          # optional, overrides entity name
 *   select_entity: select.recipes_selected  # optional, syncs selection
 */

const NOTION_COLORS = {
  default: "#999",
  gray: "#999",
  brown: "#8B6C5C",
  orange: "#D9730D",
  yellow: "#DFAB01",
  green: "#0F7B6C",
  blue: "#0B6E99",
  purple: "#6940A5",
  pink: "#AD1A72",
  red: "#E03E3E",
  light_gray: "#ccc",
};

const STYLES = `
  :host {
    --card-bg: var(--ha-card-background, var(--card-background-color, #fff));
    --text-primary: var(--primary-text-color, #333);
    --text-secondary: var(--secondary-text-color, #666);
    --divider: var(--divider-color, #e0e0e0);
    --accent: var(--primary-color, #03a9f4);
  }
  ha-card { overflow: hidden; }
  .header {
    padding: 16px 16px 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .header h2 {
    margin: 0; font-size: 1.1em; font-weight: 500;
    color: var(--text-primary);
  }
  .header .count {
    font-size: 0.85em; color: var(--text-secondary);
  }
  .controls {
    padding: 12px 16px;
    display: flex; flex-direction: column; gap: 8px;
  }
  .search-bar {
    display: flex; align-items: center;
    background: var(--input-fill-color, rgba(0,0,0,0.05));
    border-radius: 8px; padding: 6px 10px;
  }
  .search-bar input {
    border: none; outline: none; background: transparent;
    color: var(--text-primary); font-size: 0.9em;
    width: 100%; padding: 2px 0;
  }
  .search-bar input::placeholder { color: var(--text-secondary); }
  .search-icon { color: var(--text-secondary); margin-right: 6px; font-size: 1em; }
  .tags { display: flex; flex-wrap: wrap; gap: 6px; }
  .tag-chip {
    display: inline-flex; align-items: center;
    padding: 3px 10px; border-radius: 12px;
    font-size: 0.78em; font-weight: 500; cursor: pointer;
    border: 1.5px solid transparent;
    transition: opacity 0.15s; color: #fff;
  }
  .tag-chip.active {
    border-color: var(--text-primary);
    box-shadow: 0 0 0 1px var(--text-primary);
  }
  .tag-chip:hover { opacity: 0.85; }
  .recipe-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 12px; padding: 0 16px 16px;
    max-height: 60vh; overflow-y: auto;
  }
  .recipe-card {
    background: var(--input-fill-color, rgba(0,0,0,0.03));
    border-radius: 10px; overflow: hidden; cursor: pointer;
    transition: box-shadow 0.15s, transform 0.1s;
    border: 1px solid var(--divider);
  }
  .recipe-card:hover {
    box-shadow: 0 2px 8px rgba(0,0,0,0.12);
    transform: translateY(-1px);
  }
  .recipe-cover {
    width: 100%; height: 120px; object-fit: cover;
    display: block; background: var(--divider);
  }
  .recipe-cover-placeholder {
    width: 100%; height: 80px;
    display: flex; align-items: center; justify-content: center;
    font-size: 2.5em;
    background: linear-gradient(135deg, var(--divider), transparent);
  }
  .recipe-info { padding: 10px 12px; }
  .recipe-name {
    font-weight: 500; font-size: 0.92em;
    color: var(--text-primary); margin: 0 0 6px; line-height: 1.3;
  }
  .recipe-tags { display: flex; flex-wrap: wrap; gap: 4px; }
  .recipe-tag {
    font-size: 0.7em; padding: 1px 6px;
    border-radius: 8px; color: #fff; font-weight: 500;
  }
  .empty {
    padding: 24px 16px; text-align: center;
    color: var(--text-secondary); font-size: 0.9em;
  }
  .detail-overlay {
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.5); z-index: 999;
    display: flex; align-items: center; justify-content: center;
    padding: 16px;
  }
  .detail-panel {
    background: var(--card-bg); border-radius: 12px;
    max-width: 600px; width: 100%; max-height: 85vh;
    overflow-y: auto; box-shadow: 0 8px 32px rgba(0,0,0,0.3);
  }
  .detail-header { position: relative; }
  .detail-cover {
    width: 100%; height: 200px; object-fit: cover;
    display: block; border-radius: 12px 12px 0 0;
  }
  .detail-close {
    position: absolute; top: 10px; right: 10px;
    background: rgba(0,0,0,0.5); color: #fff;
    border: none; border-radius: 50%;
    width: 32px; height: 32px; font-size: 1.1em;
    cursor: pointer; display: flex;
    align-items: center; justify-content: center;
  }
  .detail-close:hover { background: rgba(0,0,0,0.7); }
  .detail-body { padding: 20px; }
  .detail-title {
    font-size: 1.3em; font-weight: 600;
    color: var(--text-primary); margin: 0 0 8px;
  }
  .detail-tags { display: flex; gap: 6px; margin-bottom: 16px; }
  .detail-tag {
    font-size: 0.78em; padding: 2px 10px;
    border-radius: 10px; color: #fff; font-weight: 500;
  }
  .detail-section { margin-bottom: 16px; }
  .detail-section h3 {
    font-size: 0.85em; font-weight: 600;
    color: var(--text-secondary); text-transform: uppercase;
    letter-spacing: 0.5px; margin: 0 0 8px;
  }
  .detail-section pre {
    white-space: pre-wrap; word-break: break-word;
    font-family: inherit; font-size: 0.9em; line-height: 1.5;
    color: var(--text-primary); margin: 0;
    background: var(--input-fill-color, rgba(0,0,0,0.03));
    padding: 12px; border-radius: 8px;
  }
  .detail-link {
    color: var(--accent); text-decoration: none;
    font-size: 0.85em; font-weight: 500;
  }
  .detail-link:hover { text-decoration: underline; }
  .detail-actions {
    display: flex; gap: 12px; margin-top: 12px;
    padding-top: 12px; border-top: 1px solid var(--divider);
  }
`;

function el(tag, attrs, ...children) {
  const node = document.createElement(tag);
  if (attrs) {
    for (const [k, v] of Object.entries(attrs)) {
      if (k === "className") node.className = v;
      else if (k === "textContent") node.textContent = v;
      else if (k.startsWith("on")) node.addEventListener(k.slice(2).toLowerCase(), v);
      else node.setAttribute(k, v);
    }
  }
  for (const child of children) {
    if (typeof child === "string") node.appendChild(document.createTextNode(child));
    else if (child) node.appendChild(child);
  }
  return node;
}

class NotionRecipeCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._hass = null;
    this._activeTag = null;
    this._searchQuery = "";
    this._selectedRecipeId = null;
    this._lastChanged = null;
  }

  setConfig(config) {
    if (!config.entity) throw new Error("Please define an entity");
    this._config = config;
  }

  set hass(hass) {
    this._hass = hass;
    const entity = hass.states[this._config.entity];
    if (!entity) {
      this._renderError("Entity not found: " + this._config.entity);
      return;
    }
    const changed = entity.last_changed;
    if (changed !== this._lastChanged || !this._lastChanged) {
      this._lastChanged = changed;
      this._render();
    }
  }

  _getRecipes() {
    if (!this._hass) return { recipes: [], tags: [] };
    const entity = this._hass.states[this._config.entity];
    if (!entity) return { recipes: [], tags: [] };
    return {
      recipes: entity.attributes.recipes || [],
      tags: entity.attributes.tags || [],
    };
  }

  _filterRecipes(recipes) {
    let filtered = recipes;
    if (this._activeTag) {
      filtered = filtered.filter((r) =>
        r.tags.some((t) => t.name === this._activeTag)
      );
    }
    if (this._searchQuery) {
      const q = this._searchQuery.toLowerCase();
      filtered = filtered.filter(
        (r) =>
          r.name.toLowerCase().includes(q) ||
          (r.ingredients && r.ingredients.toLowerCase().includes(q))
      );
    }
    return filtered;
  }

  _selectRecipe(recipe) {
    this._selectedRecipeId = recipe.id;
    const selectEntity = this._config.select_entity;
    if (selectEntity && this._hass) {
      this._hass.callService("select", "select_option", {
        entity_id: selectEntity,
        option: recipe.name,
      });
    }
    this._render();
  }

  _closeDetail() {
    this._selectedRecipeId = null;
    this._render();
  }

  _renderError(msg) {
    this.shadowRoot.replaceChildren(
      el("ha-card", null, el("div", { style: "padding:16px;color:var(--error-color,red)", textContent: msg }))
    );
  }

  _buildTagChip(tag, active) {
    const chip = el("span", {
      className: "tag-chip" + (active ? " active" : ""),
      style: "background:" + (NOTION_COLORS[tag.color] || NOTION_COLORS.default),
      textContent: tag.name,
    });
    chip.addEventListener("click", () => {
      this._activeTag = this._activeTag === tag.name ? null : tag.name;
      this._render();
    });
    return chip;
  }

  _buildRecipeCard(recipe) {
    const card = el("div", { className: "recipe-card" });

    if (recipe.cover) {
      card.appendChild(el("img", { className: "recipe-cover", src: recipe.cover, alt: "", loading: "lazy" }));
    } else {
      card.appendChild(el("div", { className: "recipe-cover-placeholder", textContent: "\uD83C\uDF5D" }));
    }

    const info = el("div", { className: "recipe-info" });
    info.appendChild(el("div", { className: "recipe-name", textContent: recipe.name }));

    if (recipe.tags.length) {
      const tagsDiv = el("div", { className: "recipe-tags" });
      for (const t of recipe.tags) {
        tagsDiv.appendChild(el("span", {
          className: "recipe-tag",
          style: "background:" + (NOTION_COLORS[t.color] || NOTION_COLORS.default),
          textContent: t.name,
        }));
      }
      info.appendChild(tagsDiv);
    }

    card.appendChild(info);
    card.addEventListener("click", () => this._selectRecipe(recipe));
    return card;
  }

  _buildDetail(recipe) {
    const overlay = el("div", { className: "detail-overlay" });
    const panel = el("div", { className: "detail-panel" });

    // Header with cover + close button
    const header = el("div", { className: "detail-header" });
    if (recipe.cover) {
      header.appendChild(el("img", { className: "detail-cover", src: recipe.cover, alt: "" }));
    }
    const closeBtn = el("button", { className: "detail-close", textContent: "\u00D7" });
    closeBtn.addEventListener("click", (e) => { e.stopPropagation(); this._closeDetail(); });
    header.appendChild(closeBtn);
    panel.appendChild(header);

    // Body
    const body = el("div", { className: "detail-body" });
    body.appendChild(el("div", { className: "detail-title", textContent: recipe.name }));

    if (recipe.tags.length) {
      const tagsDiv = el("div", { className: "detail-tags" });
      for (const t of recipe.tags) {
        tagsDiv.appendChild(el("span", {
          className: "detail-tag",
          style: "background:" + (NOTION_COLORS[t.color] || NOTION_COLORS.default),
          textContent: t.name,
        }));
      }
      body.appendChild(tagsDiv);
    }

    if (recipe.ingredients) {
      const section = el("div", { className: "detail-section" });
      section.appendChild(el("h3", { textContent: "Ingredients" }));
      section.appendChild(el("pre", { textContent: recipe.ingredients }));
      body.appendChild(section);
    }

    if (recipe.method) {
      const section = el("div", { className: "detail-section" });
      section.appendChild(el("h3", { textContent: "Method" }));
      section.appendChild(el("pre", { textContent: recipe.method }));
      body.appendChild(section);
    }

    const hasLinks = recipe.link || recipe.url;
    if (hasLinks) {
      const actions = el("div", { className: "detail-actions" });
      if (recipe.link) {
        actions.appendChild(el("a", {
          className: "detail-link",
          href: recipe.link,
          target: "_blank",
          rel: "noopener",
          textContent: "Source",
        }));
      }
      if (recipe.url) {
        actions.appendChild(el("a", {
          className: "detail-link",
          href: recipe.url,
          target: "_blank",
          rel: "noopener",
          textContent: "Open in Notion",
        }));
      }
      body.appendChild(actions);
    }

    panel.appendChild(body);
    overlay.appendChild(panel);

    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) this._closeDetail();
    });

    return overlay;
  }

  _render() {
    const { recipes, tags } = this._getRecipes();
    const filtered = this._filterRecipes(recipes);
    const selected = this._selectedRecipeId
      ? recipes.find((r) => r.id === this._selectedRecipeId)
      : null;
    const title = this._config.title ||
      this._hass?.states[this._config.entity]?.attributes?.friendly_name || "Recipes";

    // Build the DOM tree
    const style = document.createElement("style");
    style.textContent = STYLES;

    const card = document.createElement("ha-card");

    // Header
    const header = el("div", { className: "header" },
      el("h2", { textContent: title }),
      el("span", { className: "count", textContent: filtered.length + " recipe" + (filtered.length !== 1 ? "s" : "") }),
    );
    card.appendChild(header);

    // Controls
    const controls = el("div", { className: "controls" });
    const searchBar = el("div", { className: "search-bar" });
    searchBar.appendChild(el("span", { className: "search-icon", textContent: "\uD83D\uDD0D" }));
    const searchInput = el("input", { type: "text", placeholder: "Search recipes...", value: this._searchQuery });
    searchInput.addEventListener("input", (e) => {
      this._searchQuery = e.target.value;
      this._render();
    });
    searchBar.appendChild(searchInput);
    controls.appendChild(searchBar);

    if (tags.length) {
      const tagsDiv = el("div", { className: "tags" });
      for (const t of tags) {
        tagsDiv.appendChild(this._buildTagChip(t, this._activeTag === t.name));
      }
      controls.appendChild(tagsDiv);
    }
    card.appendChild(controls);

    // Recipe grid or empty state
    if (filtered.length === 0) {
      card.appendChild(el("div", { className: "empty", textContent: "No recipes found" }));
    } else {
      const grid = el("div", { className: "recipe-grid" });
      for (const r of filtered) {
        grid.appendChild(this._buildRecipeCard(r));
      }
      card.appendChild(grid);
    }

    // Replace shadow DOM content
    this.shadowRoot.replaceChildren(style, card);

    // Detail overlay
    if (selected) {
      this.shadowRoot.appendChild(this._buildDetail(selected));
    }
  }

  getCardSize() {
    return 4;
  }

  static getStubConfig() {
    return { entity: "" };
  }
}

customElements.define("notion-recipe-card", NotionRecipeCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "notion-recipe-card",
  name: "Notion Recipe Card",
  description: "Browse recipes from a Notion database",
  preview: true,
});
