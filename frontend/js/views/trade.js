/**
 * views/trade.js — Full-screen commodity trading view.
 *
 * Opened when the player clicks TRADE from the galaxy system panel.
 * Context: { systemName: string }
 *
 * Layout:
 *   Left column (65%): sortable, filterable commodity table with inline buy/sell
 *   Right column (35%): market intelligence (best deals) + cargo status
 *
 * Data comes from /api/market/{systemName} (already in api.js).
 * Buy/sell via /api/trade/buy and /api/trade/sell.
 *
 * Logic-free: no game rules live here — only display and API calls.
 */

import { getMarket, buyGoods, sellGoods } from "../api.js";
import { state }  from "../state.js";
import { notify } from "../ui/notifications.js";


// ---------------------------------------------------------------------------
// Module state
// ---------------------------------------------------------------------------

let _systemName = "";
let _market     = null;   // Last fetched market response
let _sortKey    = "name"; // Active sort column: "name" | "price" | "supply" | "demand" | "held"
let _sortDir    = "asc";  // "asc" | "desc"
let _filter     = "all";  // "all" | "buyable" | "held"


// ---------------------------------------------------------------------------
// Public view object
// ---------------------------------------------------------------------------

export const tradeView = { mount, unmount };


async function mount(context = {}) {
  _systemName = context.systemName || "";

  const container = document.getElementById("trade-container");
  if (!container) return;

  container.innerHTML = `<p class="trade-loading">Loading market for ${_systemName}…</p>`;

  try {
    _market = await getMarket(_systemName);
  } catch (err) {
    container.innerHTML = `<p class="trade-error">No market at ${_systemName}: ${err.message}</p>`;
    return;
  }

  render(container);
}

function unmount() {
  _market     = null;
  _systemName = "";
  _sortKey    = "name";
  _sortDir    = "asc";
  _filter     = "all";
}


// ---------------------------------------------------------------------------
// Rendering
// ---------------------------------------------------------------------------

function render(container) {
  if (!_market) return;
  container.innerHTML = buildHtml();
  wireEvents(container);
}

/** Return a sort indicator glyph for the given column header. */
function _sortGlyph(key) {
  if (_sortKey !== key) return '<span class="tc-sort-indicator">⇅</span>';
  return `<span class="tc-sort-indicator tc-sort-indicator--active">${_sortDir === "asc" ? "▲" : "▼"}</span>`;
}

/** Return commodities filtered then sorted by the current _filter / _sortKey / _sortDir. */
function _applyFilterSort(commodities) {
  let list = commodities;
  if (_filter === "buyable") list = list.filter(c => c.supply > 0 && c.price > 0);
  if (_filter === "held")    list = list.filter(c => c.in_inventory > 0);

  const dir = _sortDir === "asc" ? 1 : -1;
  return [...list].sort((a, b) => {
    if (_sortKey === "name")   return dir * a.name.localeCompare(b.name);
    if (_sortKey === "held")   return dir * ((a.in_inventory ?? 0) - (b.in_inventory ?? 0));
    return dir * ((a[_sortKey] ?? 0) - (b[_sortKey] ?? 0));
  });
}

/** Build an inline mini bar for supply/demand columns. */
function _bar(value, maxVal, kind) {
  const pct = maxVal > 0 ? Math.min(100, Math.round((value / maxVal) * 100)) : 0;
  return `<div class="mkt-bar"><div class="mkt-bar__fill mkt-bar__fill--${kind}" style="width:${pct}%"></div></div>`;
}

function buildHtml() {
  const { system_name, commodities = [], best_buys = [], best_sells = [],
          player_credits = 0, cargo_used = 0, max_cargo: mktMaxCargo } = _market;

  const ship       = state.gameState?.ship;
  const maxCargo   = mktMaxCargo ?? ship?.max_cargo ?? 0;
  const cargoFree  = maxCargo > 0 ? maxCargo - cargo_used : 0;
  const creditsFmt = player_credits.toLocaleString();

  // Cargo bar colour
  const cargoPct   = maxCargo > 0 ? Math.round((cargo_used / maxCargo) * 100) : 0;
  const cargoColor = cargoPct >= 90 ? "var(--accent-red,#ff4444)"
                   : cargoPct >= 70 ? "var(--accent-gold)"
                   : "var(--accent-teal)";

  // Net inventory value at sell prices
  const invValue = commodities.reduce(
    (sum, c) => sum + (c.in_inventory * Math.round((c.price ?? 0) * 0.8)), 0);

  // Column maxima for relative bar widths
  const maxSupply = Math.max(...commodities.map(c => c.supply || 0), 1);
  const maxDemand = Math.max(...commodities.map(c => c.demand || 0), 1);

  // Filter counts for tabs
  const nAll     = commodities.length;
  const nBuyable = commodities.filter(c => c.supply > 0 && c.price > 0).length;
  const nHeld    = commodities.filter(c => c.in_inventory > 0).length;

  // Build commodity rows
  const visible = _applyFilterSort(commodities);
  const rows = visible.map(c => buildRow(c, player_credits, cargoFree, maxSupply, maxDemand)).join("");

  // Sidebar: best buys and sells
  const buyDeals = best_buys.slice(0, 8).map(b =>
    `<div class="deal-row">
       <span class="deal-row__name">${esc(b.name)}</span>
       <span class="deal-row__val deal-row__val--buy">${b.price} ◈</span>
       <span class="deal-row__supply muted">${b.supply} in stock</span>
     </div>`
  ).join("") || `<p class="deal-empty">None identified.</p>`;

  const sellDeals = best_sells.slice(0, 8).map(s =>
    `<div class="deal-row">
       <span class="deal-row__name">${esc(s.name)}</span>
       <span class="deal-row__val deal-row__val--sell">${Math.round(s.price * 0.8)} ◈</span>
       <span class="deal-row__supply muted">demand ${s.demand}</span>
     </div>`
  ).join("") || `<p class="deal-empty">None identified.</p>`;

  return `
    <div class="trade-view">

      <!-- ── Header ──────────────────────────────────────── -->
      <header class="trade-view__header">
        <div class="trade-view__title-block">
          <button class="btn btn--secondary trade-back-btn">← BACK</button>
          <h2 class="trade-view__title">MARKET — ${esc(system_name)}</h2>
        </div>
        <div class="trade-view__stats">
          <span class="trade-stat">
            <span class="trade-stat__label">CREDITS</span>
            <span class="trade-stat__val trade-stat__val--gold">${creditsFmt} ◈</span>
          </span>
          ${maxCargo > 0 ? `
          <span class="trade-stat">
            <span class="trade-stat__label">CARGO</span>
            <span class="trade-stat__val" style="color:${cargoColor}">${cargo_used} / ${maxCargo}</span>
          </span>
          <span class="trade-stat">
            <span class="trade-stat__label">FREE</span>
            <span class="trade-stat__val">${cargoFree}</span>
          </span>
          ` : ""}
          ${invValue > 0 ? `
          <span class="trade-stat">
            <span class="trade-stat__label">INV. VALUE</span>
            <span class="trade-stat__val trade-stat__val--gold">${invValue.toLocaleString()} ◈</span>
          </span>
          ` : ""}
        </div>
      </header>

      <!-- ── Body ────────────────────────────────────────── -->
      <div class="trade-view__body">

        <!-- Left: filterable, sortable commodity table -->
        <div class="trade-table-wrap">

          <!-- Filter tabs -->
          <div class="mkt-filters trade-filters" id="trade-filters">
            <button class="mkt-filter-btn${_filter === "all"     ? " active" : ""}"
                    data-filter="all">ALL (${nAll})</button>
            <button class="mkt-filter-btn${_filter === "buyable" ? " active" : ""}"
                    data-filter="buyable">IN STOCK (${nBuyable})</button>
            <button class="mkt-filter-btn${_filter === "held"    ? " active" : ""}"
                    data-filter="held">HELD (${nHeld})</button>
          </div>

          <!-- Sortable column headers -->
          <div class="trade-table-header">
            <button class="tc-name  tc-sort-btn ${_sortKey==='name'   ? 'tc-sort-btn--active':''}"
                    data-sort="name">COMMODITY ${_sortGlyph('name')}</button>
            <button class="tc-price tc-sort-btn ${_sortKey==='price'  ? 'tc-sort-btn--active':''}"
                    data-sort="price">BUY ◈ ${_sortGlyph('price')}</button>
            <span class="tc-price tc-sell-head">SELL ◈</span>
            <button class="tc-supply tc-sort-btn ${_sortKey==='supply' ? 'tc-sort-btn--active':''}"
                    data-sort="supply">SUPPLY ${_sortGlyph('supply')}</button>
            <button class="tc-demand tc-sort-btn ${_sortKey==='demand' ? 'tc-sort-btn--active':''}"
                    data-sort="demand">DEMAND ${_sortGlyph('demand')}</button>
            <button class="tc-held  tc-sort-btn ${_sortKey==='held'   ? 'tc-sort-btn--active':''}"
                    data-sort="held">HELD ${_sortGlyph('held')}</button>
            <span class="tc-actions"></span>
          </div>

          <div class="trade-table" id="trade-table-body">
            ${rows || '<p class="trade-empty">No commodities match the current filter.</p>'}
          </div>
        </div>

        <!-- Right: market intel sidebar -->
        <aside class="trade-sidebar">
          <section class="trade-deals">
            <h3 class="trade-deals__title">⊕ BUY OPPORTUNITIES</h3>
            <div class="deal-list">${buyDeals}</div>
          </section>
          <section class="trade-deals">
            <h3 class="trade-deals__title">⊗ SELL OPPORTUNITIES</h3>
            <div class="deal-list">${sellDeals}</div>
          </section>
        </aside>

      </div>
    </div>
  `;
}


/** Build one commodity row for the trade table. */
function buildRow(c, credits, cargoFree, maxSupply, maxDemand) {
  const canBuy   = c.price > 0 && c.supply > 0 && cargoFree > 0;
  const canSell  = c.price > 0 && c.in_inventory > 0;
  const sellPrice = Math.round((c.price ?? 0) * 0.8);
  // Max buyable bounded by supply, free cargo, and affordability
  const maxBuy   = canBuy ? Math.min(c.supply, cargoFree, Math.floor(credits / c.price)) : 0;

  const supplyBar = `<div class="mkt-bar"><div class="mkt-bar__fill mkt-bar__fill--supply"
    style="width:${maxSupply > 0 ? Math.min(100, Math.round((c.supply / maxSupply) * 100)) : 0}%"></div></div>`;
  const demandBar = `<div class="mkt-bar"><div class="mkt-bar__fill mkt-bar__fill--demand"
    style="width:${maxDemand > 0 ? Math.min(100, Math.round((c.demand / maxDemand) * 100)) : 0}%"></div></div>`;

  return `
    <div class="trade-row${c.in_inventory > 0 ? " trade-row--held" : ""}"
         data-commodity="${esc(c.name)}">

      <span class="tc-name trade-row__name">${esc(c.name)}</span>

      <span class="tc-price trade-row__price" style="color:var(--accent-teal)">
        ${c.price > 0 ? c.price + " ◈" : "—"}
      </span>

      <span class="tc-price trade-row__sell-price" style="color:var(--accent-gold)">
        ${c.price > 0 ? sellPrice + " ◈" : "—"}
      </span>

      <span class="tc-supply">
        <span class="trade-stat-val">${c.supply}</span>
        ${supplyBar}
      </span>

      <span class="tc-demand">
        <span class="trade-stat-val">${c.demand}</span>
        ${demandBar}
      </span>

      <span class="tc-held ${c.in_inventory > 0 ? "trade-row__held--has" : ""}">
        ${c.in_inventory || "—"}
      </span>

      <span class="tc-actions">
        ${canBuy ? `
          <div class="mkt-action-group">
            <input class="trade-qty market-qty-input" type="number" value="1" min="1" max="${maxBuy}"
                   data-commodity="${esc(c.name)}" data-action="buy">
            <button class="btn btn--xs btn--primary btn-trade-action"
                    data-commodity="${esc(c.name)}" data-action="buy">BUY</button>
            <button class="btn btn--xs btn--ghost btn-max-trade"
                    data-commodity="${esc(c.name)}" data-action="buy" data-max="${maxBuy}"
                    title="Fill to max affordable (${maxBuy})">MAX</button>
          </div>
        ` : ""}
        ${canSell ? `
          <div class="mkt-action-group">
            <input class="trade-qty market-qty-input" type="number" value="1" min="1"
                   max="${c.in_inventory}"
                   data-commodity="${esc(c.name)}" data-action="sell">
            <button class="btn btn--xs btn--secondary btn-trade-action"
                    data-commodity="${esc(c.name)}" data-action="sell">SELL</button>
            <button class="btn btn--xs btn--ghost btn-max-trade"
                    data-commodity="${esc(c.name)}" data-action="sell"
                    data-max="${c.in_inventory}" title="Sell all (${c.in_inventory})">ALL</button>
          </div>
        ` : ""}
      </span>
    </div>
  `;
}


// ---------------------------------------------------------------------------
// Events
// ---------------------------------------------------------------------------

function wireEvents(container) {
  // Back button → return to galaxy via HUD nav button
  container.querySelector(".trade-back-btn")
    ?.addEventListener("click", () => {
      document.querySelector('.hud__nav-btn[data-view="galaxy"]')?.click();
    });

  // Filter tabs
  container.querySelectorAll(".mkt-filter-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      _filter = btn.dataset.filter;
      render(container);
    });
  });

  // Sortable column headers
  container.querySelectorAll(".tc-sort-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const key = btn.dataset.sort;
      if (_sortKey === key) {
        _sortDir = _sortDir === "asc" ? "desc" : "asc";
      } else {
        _sortKey = key;
        _sortDir = "asc";
      }
      render(container);
    });
  });

  // MAX / ALL quick-fill buttons
  container.querySelectorAll(".btn-max-trade").forEach(btn => {
    btn.addEventListener("click", () => {
      const commodity = btn.dataset.commodity;
      const action    = btn.dataset.action;
      const max       = parseInt(btn.dataset.max || "1", 10);
      const input     = container.querySelector(
        `.trade-qty[data-commodity="${CSS.escape(commodity)}"][data-action="${action}"]`
      );
      if (input) input.value = max;
    });
  });

  // Buy / Sell trade buttons
  container.querySelectorAll(".btn-trade-action").forEach(btn => {
    btn.addEventListener("click", () => {
      const commodity = btn.dataset.commodity;
      const action    = btn.dataset.action;
      const qtyInput  = container.querySelector(
        `.trade-qty[data-commodity="${CSS.escape(commodity)}"][data-action="${action}"]`
      );
      const qty = Math.max(1, parseInt(qtyInput?.value || "1", 10));
      doTrade(commodity, action, qty, btn, container);
    });
  });
}

async function doTrade(commodity, action, quantity, btn, container) {
  const origText  = btn.textContent;
  btn.disabled    = true;
  btn.textContent = action === "buy" ? "BUYING…" : "SELLING…";

  try {
    const fn     = action === "buy" ? buyGoods : sellGoods;
    const result = await fn(_systemName, commodity, quantity);

    notify("TRADE", result.message || `${action.toUpperCase()} complete.`);

    // Reflect new credits in game state immediately
    if (state.gameState?.player) {
      state.gameState.player.credits = result.credits_remaining;
    }

    // Refresh market and re-render
    _market = await getMarket(_systemName);
    render(container);

  } catch (err) {
    notify("ERROR", err.message || "Trade failed.");
    btn.disabled    = false;
    btn.textContent = origText;
  }
}


// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function esc(str) {
  return String(str ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
