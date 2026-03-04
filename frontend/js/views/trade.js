/**
 * views/trade.js — Full-screen commodity trading view.
 *
 * Opened when the player clicks TRADE from the galaxy system panel.
 * Context: { systemName: string }
 *
 * Layout:
 *   Left column (65%): commodity table with inline buy/sell
 *   Right column (35%): best deals + player cargo status
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
}


// ---------------------------------------------------------------------------
// Rendering
// ---------------------------------------------------------------------------

function render(container) {
  if (!_market) return;
  container.innerHTML = buildHtml();
  wireEvents(container);
}

function buildHtml() {
  const { system_name, commodities = [], best_buys = [], best_sells = [],
          player_credits = 0, cargo_used = 0 } = _market;

  const ship       = state.gameState?.ship;
  const max_cargo  = ship?.max_cargo ?? "?";
  const creditsFmt = player_credits.toLocaleString();

  const rows = commodities.map(c => buildRow(c)).join("");

  const buyDeals = best_buys.slice(0, 6).map(b =>
    `<div class="deal-row">
       <span class="deal-row__name">${esc(b.name)}</span>
       <span class="deal-row__val deal-row__val--buy">${b.price} cr</span>
     </div>`
  ).join("") || `<p class="deal-empty">None identified.</p>`;

  const sellDeals = best_sells.slice(0, 6).map(s =>
    `<div class="deal-row">
       <span class="deal-row__name">${esc(s.name)}</span>
       <span class="deal-row__val deal-row__val--sell">${s.price} cr</span>
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
            <span class="trade-stat__val trade-stat__val--gold">${creditsFmt}</span>
          </span>
          <span class="trade-stat">
            <span class="trade-stat__label">CARGO</span>
            <span class="trade-stat__val">${cargo_used} / ${max_cargo}</span>
          </span>
        </div>
      </header>

      <!-- ── Body ────────────────────────────────────────── -->
      <div class="trade-view__body">

        <!-- Commodity table -->
        <div class="trade-table-wrap">
          <div class="trade-table-header">
            <span class="tc-name">Commodity</span>
            <span class="tc-price">Price</span>
            <span class="tc-supply">Supply</span>
            <span class="tc-demand">Demand</span>
            <span class="tc-held">In Cargo</span>
            <span class="tc-actions"></span>
          </div>
          <div class="trade-table">
            ${rows || '<p class="trade-empty">No commodities available at this market.</p>'}
          </div>
        </div>

        <!-- Sidebar -->
        <aside class="trade-sidebar">
          <section class="trade-deals">
            <h3 class="trade-deals__title">BEST TO BUY</h3>
            <div class="deal-list">${buyDeals}</div>
          </section>
          <section class="trade-deals">
            <h3 class="trade-deals__title">BEST TO SELL</h3>
            <div class="deal-list">${sellDeals}</div>
          </section>
        </aside>

      </div>
    </div>
  `;
}

function buildRow(c) {
  const canBuy  = c.price > 0 && c.supply > 0;
  const canSell = c.price > 0 && c.in_inventory > 0;

  const supplyColor = c.supply > 50 ? "var(--accent-green)"
                    : c.supply > 10 ? "var(--accent-teal)"
                    : "var(--accent-orange)";

  return `
    <div class="trade-row" data-commodity="${esc(c.name)}">
      <span class="tc-name trade-row__name">${esc(c.name)}</span>
      <span class="tc-price trade-row__price">${c.price} cr</span>
      <span class="tc-supply" style="color:${supplyColor}">${c.supply}</span>
      <span class="tc-demand">${c.demand}</span>
      <span class="tc-held ${c.in_inventory > 0 ? "trade-row__held--has" : ""}">${c.in_inventory || "—"}</span>
      <span class="tc-actions">
        ${canBuy ? `
          <input class="trade-qty" type="number" value="1" min="1"
                 data-commodity="${esc(c.name)}" data-action="buy">
          <button class="btn btn--sm btn--primary btn-trade-action"
                  data-commodity="${esc(c.name)}" data-action="buy">BUY</button>
        ` : ""}
        ${canSell ? `
          <input class="trade-qty" type="number" value="1" min="1"
                 max="${c.in_inventory}"
                 data-commodity="${esc(c.name)}" data-action="sell">
          <button class="btn btn--sm btn--secondary btn-trade-action"
                  data-commodity="${esc(c.name)}" data-action="sell">SELL</button>
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

  // Trade buttons
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
