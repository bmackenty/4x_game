/**
 * views/ship.js — Ship stats and component management view.
 *
 * Shows:
 *   • Top bar: ship name, class, and key derived stats (fuel, jump range, cargo).
 *   • Category filter bar: click a category to show only those attributes.
 *   • Attribute list: each attribute rendered as a labeled progress bar (0–100).
 *   • Components panel: installed components and available upgrades per slot.
 *
 * All data comes from /api/ship/attributes and /api/ship/components.
 * No game logic lives here — display only.
 */

import { getShipAttributes, getShipComponents, installShipComponent } from "../api.js";
import { notify } from "../ui/notifications.js";


// ---------------------------------------------------------------------------
// Module state
// ---------------------------------------------------------------------------

let _attrs   = null;   // Response from /api/ship/attributes
let _comps   = null;   // Response from /api/ship/components
let _catFilter = "all"; // Active category id, or "all"
let _tab = "stats";    // "stats" | "components"


// ---------------------------------------------------------------------------
// Public view object
// ---------------------------------------------------------------------------

export const shipView = { mount, unmount };


async function mount() {
  const container = document.getElementById("ship-container");
  if (!container) return;

  container.innerHTML = '<p class="ship__loading">Loading ship data…</p>';

  try {
    [_attrs, _comps] = await Promise.all([getShipAttributes(), getShipComponents()]);
  } catch (err) {
    container.innerHTML = `<p class="ship__error">Could not load ship data: ${err.message}</p>`;
    return;
  }

  _catFilter = "all";
  _tab = "stats";
  render(container);
}

function unmount() {
  _attrs = null;
  _comps = null;
}


// ---------------------------------------------------------------------------
// Rendering
// ---------------------------------------------------------------------------

function render(container) {
  container.innerHTML = buildHtml();
  wireEvents(container);
}

function buildHtml() {
  if (!_attrs) return "";

  const { ship_name, ship_class, fuel, max_fuel, jump_range, max_cargo } = _attrs;
  const fuelPct = max_fuel > 0 ? Math.round((fuel / max_fuel) * 100) : 0;

  return `
    <div class="ship-view">

      <!-- ── Header ─────────────────────────────────────── -->
      <header class="ship-view__header">
        <div class="ship-view__identity">
          <h2 class="ship-view__name">${ship_name}</h2>
          <span class="ship-view__class">${ship_class}</span>
        </div>
        <div class="ship-view__quick-stats">
          <div class="ship-stat">
            <span class="ship-stat__label">FUEL</span>
            <div class="ship-stat__bar-wrap">
              <div class="ship-stat__bar" style="width:${fuelPct}%"></div>
            </div>
            <span class="ship-stat__value">${fuel}/${max_fuel}</span>
          </div>
          <div class="ship-stat">
            <span class="ship-stat__label">JUMP</span>
            <span class="ship-stat__value ship-stat__value--solo">${jump_range} u</span>
          </div>
          <div class="ship-stat">
            <span class="ship-stat__label">CARGO</span>
            <span class="ship-stat__value ship-stat__value--solo">${max_cargo} t</span>
          </div>
        </div>
      </header>

      <!-- ── Tab switcher ────────────────────────────────── -->
      <div class="ship-view__tabs">
        <button class="ship-tab-btn ${_tab === "stats" ? "ship-tab-btn--active" : ""}"
                data-tab="stats">ATTRIBUTES</button>
        <button class="ship-tab-btn ${_tab === "components" ? "ship-tab-btn--active" : ""}"
                data-tab="components">COMPONENTS</button>
      </div>

      <!-- ── Tab content ─────────────────────────────────── -->
      <div class="ship-view__body">
        ${_tab === "stats" ? buildStatsTab() : buildComponentsTab()}
      </div>

    </div>
  `;
}

// ── Stats tab ──────────────────────────────────────────────────────────────

function buildStatsTab() {
  const categories = _attrs.categories || [];

  const filterBtns = [
    `<button class="ship-cat-btn ${_catFilter === "all" ? "ship-cat-btn--active" : ""}"
             data-cat="all">All</button>`,
    ...categories.map(cat =>
      `<button class="ship-cat-btn ${_catFilter === cat.id ? "ship-cat-btn--active" : ""}"
               data-cat="${cat.id}">${cat.name}</button>`
    ),
  ].join("");

  const visibleCats = _catFilter === "all"
    ? categories
    : categories.filter(c => c.id === _catFilter);

  const catSections = visibleCats.map(cat => `
    <section class="ship-cat-section">
      <h3 class="ship-cat-section__title">${cat.name}</h3>
      <div class="ship-attr-list">
        ${cat.attributes.map(attr => buildAttrRow(attr)).join("")}
      </div>
    </section>
  `).join("");

  return `
    <div class="ship-cat-filter">${filterBtns}</div>
    <div class="ship-attr-body">${catSections}</div>
  `;
}

function buildAttrRow(attr) {
  const pct = Math.min(100, Math.max(0, attr.value));
  const colorClass = pct >= 60 ? "attr-bar--high"
                   : pct >= 35 ? "attr-bar--mid"
                   : "attr-bar--low";
  return `
    <div class="attr-row" title="${attr.description}">
      <span class="attr-row__name">${attr.name}</span>
      <div class="attr-row__bar-wrap">
        <div class="attr-row__bar ${colorClass}" style="width:${pct}%"></div>
      </div>
      <span class="attr-row__value">${attr.value}</span>
    </div>
  `;
}

// ── Components tab ─────────────────────────────────────────────────────────

function buildComponentsTab() {
  if (!_comps) return "<p>No component data.</p>";

  const installed = _comps.installed || {};
  const slots     = _comps.slots || {};

  const installedHtml = buildInstalledSection(installed);
  const upgradeHtml   = Object.entries(slots).map(([slotKey, slotData]) =>
    buildSlotSection(slotKey, slotData, installed)
  ).join("");

  return `
    <div class="ship-components">
      <section class="ship-comp-section">
        <h3 class="ship-comp-section__title">INSTALLED COMPONENTS</h3>
        ${installedHtml}
      </section>
      <section class="ship-comp-section">
        <h3 class="ship-comp-section__title">AVAILABLE UPGRADES</h3>
        ${upgradeHtml}
      </section>
    </div>
  `;
}

function buildInstalledSection(installed) {
  if (!installed || Object.keys(installed).length === 0) {
    return "<p class=\"ship__empty\">No components installed.</p>";
  }
  const rows = Object.entries(installed).map(([slot, value]) => {
    const names = Array.isArray(value) ? value : [value];
    return names.map(n => `
      <div class="comp-row comp-row--installed">
        <span class="comp-row__slot">${slot.toUpperCase()}</span>
        <span class="comp-row__name">${n}</span>
      </div>
    `).join("");
  }).join("");
  return `<div class="comp-list">${rows}</div>`;
}

function buildSlotSection(slotKey, slotData, installed) {
  const available = slotData.available || [];
  if (available.length === 0) return "";

  const rows = available.map(comp => {
    const isInstalled = isComponentInstalled(comp.name, installed);
    const lockLabel = comp.faction_lock
      ? `<span class="comp-lock">[${Array.isArray(comp.faction_lock)
          ? comp.faction_lock.join(", ") : comp.faction_lock}]</span>`
      : "";
    return `
      <div class="comp-row ${isInstalled ? "comp-row--active" : ""}">
        <div class="comp-row__info">
          <span class="comp-row__name">${comp.name}</span>
          ${lockLabel}
          <span class="comp-row__cost">${comp.cost.toLocaleString()} cr</span>
          <span class="comp-row__risk" title="Failure risk">${comp.failure_chance}% risk</span>
        </div>
        ${!isInstalled ? `
          <button class="btn btn--sm btn-install"
                  data-category="${slotKey}"
                  data-name="${comp.name}">INSTALL</button>` : ""}
      </div>
    `;
  }).join("");

  return `
    <div class="ship-slot-section">
      <h4 class="ship-slot-section__label">${slotData.label}</h4>
      <div class="comp-list">${rows}</div>
    </div>
  `;
}

function isComponentInstalled(name, installed) {
  for (const value of Object.values(installed)) {
    if (Array.isArray(value)) { if (value.includes(name)) return true; }
    else if (value === name) return true;
  }
  return false;
}


// ---------------------------------------------------------------------------
// Event wiring
// ---------------------------------------------------------------------------

function wireEvents(container) {
  // Tab buttons
  container.querySelectorAll(".ship-tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      _tab = btn.dataset.tab;
      render(container);
    });
  });

  // Category filter buttons
  container.querySelectorAll(".ship-cat-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      _catFilter = btn.dataset.cat;
      render(container);
    });
  });

  // Install buttons
  container.querySelectorAll(".btn-install").forEach(btn => {
    btn.addEventListener("click", () => handleInstall(btn, container));
  });
}

async function handleInstall(btn, container) {
  const category = btn.dataset.category;
  const name     = btn.dataset.name;
  btn.disabled   = true;
  btn.textContent = "…";

  try {
    const result = await installShipComponent(category, name);
    notify("SHIP", `Installed: ${name}`);
    // Refresh both data sets
    [_attrs, _comps] = await Promise.all([getShipAttributes(), getShipComponents()]);
    render(container);
  } catch (err) {
    notify("ERROR", `Install failed: ${err.message}`);
    btn.disabled    = false;
    btn.textContent = "INSTALL";
  }
}
