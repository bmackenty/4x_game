/**
 * views/galaxy.js — Galaxy map view.
 *
 * Renders all star systems as hexes on an HTML5 Canvas, supports pan/zoom,
 * shows a system-detail panel in the right sidebar when a system is clicked,
 * and lets the player jump to adjacent systems.
 *
 * Architecture:
 *   mount()    — fetch galaxy data, attach input handlers, start render loop
 *   unmount()  — detach input handlers, cancel render loop
 *
 * The render loop uses requestAnimationFrame for smooth pan/zoom.
 * It only redraws when the view state is "dirty" (changed since last frame).
 */

import { state }              from "../state.js";
import { getGalaxyMap, getSystem, jumpToCoords,
         getMarket, buyGoods, sellGoods }        from "../api.js";
import { notify }             from "../ui/notifications.js";
import { renderGalaxyMap, GALAXY_HEX_SIZE } from "../hex/hex-render.js";
import { attachHexInput }     from "../hex/hex-input.js";

// ---------------------------------------------------------------------------
// Galaxy projection scale — must match GALAXY_SCALE in backend/hex_utils.py
// Converts 3D game coordinates (x, y, z) → 2D axial hex (q, r).
// ---------------------------------------------------------------------------
const GALAXY_SCALE = 12.5;  // 500 galaxy units / 40 hex columns

/**
 * Project a ship's 3D game coordinates to the 2D axial hex grid.
 * @param {number[]} coords - [x, y, z] from ship.coordinates
 * @returns {{ q: number, r: number }}
 */
function shipCoordsToHex(coords) {
  if (!coords || coords.length < 2) return null;
  return {
    q: Math.round(coords[0] / GALAXY_SCALE),
    r: Math.round(coords[1] / GALAXY_SCALE),
  };
}

/**
 * Convert an axial hex (q, r) to canvas world-space pixel position.
 * Mirrors axialToPixel in hex-math.js (flat-top hex layout).
 * @param {number} q
 * @param {number} r
 * @param {number} size - hex radius in pixels
 * @returns {{ x: number, y: number }}
 */
function hexToPixel(q, r, size) {
  return {
    x: size * 1.5 * q,
    y: size * (Math.sqrt(3) / 2 * q + Math.sqrt(3) * r),
  };
}


// ---------------------------------------------------------------------------
// Faction colour map — approximate colours for major factions
// Built lazily from the faction data in state.factions
// ---------------------------------------------------------------------------
const FACTION_COLORS = new Map([
  ["The Veritas Covenant",            "rgba(0,170,255,0.3)"],
  ["Stellar Nexus Guild",             "rgba(0,212,170,0.3)"],
  ["The Icaron Collective",           "rgba(170,100,220,0.3)"],
  ["The Gaian Enclave",               "rgba(50,180,80,0.3)"],
  ["The Gearwrights Guild",           "rgba(200,140,0,0.3)"],
  ["Celestial Alliance",              "rgba(0,200,255,0.3)"],
  ["Void Syndicate",                  "rgba(80,0,120,0.3)"],
  ["The Merchant Consortium",         "rgba(200,180,0,0.3)"],
  ["Etheric Order",                   "rgba(180,100,255,0.3)"],
  ["The Remnants",                    "rgba(180,60,60,0.3)"],
  ["Harmonic Resonance Collective",   "rgba(0,230,200,0.3)"],
  ["default",                         "rgba(100,140,180,0.2)"],
]);

// ---------------------------------------------------------------------------
// Module-level mutable state for this view
// ---------------------------------------------------------------------------
let inputControls  = null;   // return value of attachHexInput()
let rafHandle      = null;   // requestAnimationFrame handle
let isDirty        = true;   // if true, redraw on next frame
let systemsData    = [];     // cached from /api/galaxy/map

// View transform
let viewState = { panX: 0, panY: 0, zoom: 1.0, selectedSystemName: null };

/** Cached market data for the currently selected system. */
let _marketData = null;


// ---------------------------------------------------------------------------
// Exported view object
// ---------------------------------------------------------------------------

export const galaxyView = {

  async mount(context) {
    const canvas = document.getElementById("galaxy-canvas");
    if (!canvas) return;

    // Fetch galaxy map data (or use cache)
    if (state.galaxyMap.length === 0) {
      try {
        const result = await getGalaxyMap();
        state.galaxyMap = result.systems || [];
      } catch (err) {
        notify("ERROR", `Could not load galaxy map: ${err.message}`);
        return;
      }
    }
    systemsData = state.galaxyMap;

    // If a system was pre-selected (e.g. returning from colony view), re-apply it
    if (state.selectedSystem) {
      viewState.selectedSystemName = state.selectedSystem.name;
      showSystemPanel(state.selectedSystem);
    }

    // Attach pan/zoom/click input
    inputControls = attachHexInput(canvas, {
      hexSize:       GALAXY_HEX_SIZE,
      onHexClick:    handleHexClick,
      onHexHover:    handleHexHover,
      onViewChanged: (vs) => {
        viewState = { ...viewState, ...vs };
        isDirty = true;
      },
    });

    // Sync initial viewState from inputControls
    viewState = { ...viewState, ...inputControls.viewState };

    // Centre the initial view on the player's ship position so it's visible
    // without having to pan.  Applies only on first mount, not when returning
    // from the colony view (where the player may have already panned).
    const shipCoords = state.gameState?.ship?.coordinates;
    const shipHex    = shipCoordsToHex(shipCoords);
    if (shipHex && viewState.panX === 0 && viewState.panY === 0) {
      const { x: spx, y: spy } = hexToPixel(shipHex.q, shipHex.r, GALAXY_HEX_SIZE);
      inputControls.viewState.panX = -spx;
      inputControls.viewState.panY = -spy;
      viewState = { ...viewState, ...inputControls.viewState };
    }

    // Start render loop
    isDirty = true;
    startRenderLoop(canvas);
  },

  unmount() {
    // Stop the render loop
    if (rafHandle !== null) {
      cancelAnimationFrame(rafHandle);
      rafHandle = null;
    }
    // Remove input listeners
    if (inputControls) {
      inputControls.detach();
      inputControls = null;
    }
    // Hide the right panel
    hideRightPanel();
  },
};


// ---------------------------------------------------------------------------
// Render loop
// ---------------------------------------------------------------------------

function startRenderLoop(canvas) {
  function frame() {
    if (isDirty) {
      isDirty = false;

      // Compute ship hex position fresh each frame so it updates after jumps.
      // state.gameState.ship.coordinates is [x, y, z] (Python tuple → JSON array).
      const shipCoords = state.gameState?.ship?.coordinates;
      const shipHex    = shipCoordsToHex(shipCoords);

      renderGalaxyMap(
        canvas,
        systemsData,
        { ...viewState, shipHex },
        FACTION_COLORS
      );
    }
    rafHandle = requestAnimationFrame(frame);
  }
  rafHandle = requestAnimationFrame(frame);
}


// ---------------------------------------------------------------------------
// Hex click handler — find which system was clicked and show its detail panel
// ---------------------------------------------------------------------------

async function handleHexClick({ q, r }) {
  // Find the system at this hex coordinate
  const sys = systemsData.find(s => s.hex_q === q && s.hex_r === r);

  if (!sys) {
    // Clicked empty space — deselect
    viewState.selectedSystemName = null;
    state.selectedSystem = null;
    hideRightPanel();
    isDirty = true;
    return;
  }

  // Select the system
  viewState.selectedSystemName = sys.name;
  state.selectedSystem = sys;
  isDirty = true;

  // Fetch detailed system data (planets, market, etc.)
  try {
    const detail = await getSystem(sys.name);
    // Mark as visited in our local cache too
    sys.visited = true;
    showSystemPanel(detail);
  } catch (err) {
    notify("ERROR", `Could not load system data: ${err.message}`);
  }
}


// ---------------------------------------------------------------------------
// Hover handler — used for tooltip (Phase 6 polish)
// ---------------------------------------------------------------------------

function handleHexHover({ q, r }) {
  // Hover tooltips will be added in Phase 6
  // For now, nothing to do
}


// ---------------------------------------------------------------------------
// System detail panel (right sidebar)
// ---------------------------------------------------------------------------

async function showSystemPanel(system) {
  const panel = document.getElementById("panel-right");
  const content = document.getElementById("panel-right-content");
  if (!panel || !content) return;

  // Reveal the panel
  panel.classList.remove("panel--hidden");
  state.rightPanelOpen = true;

  // Reset market data — will be fetched below
  _marketData = null;

  // Render the panel immediately with what we have (no market section yet)
  content.innerHTML = buildSystemPanelHtml(system, null);

  // Wire jump button
  const jumpBtn = content.querySelector(".btn-jump");
  if (jumpBtn) {
    jumpBtn.addEventListener("click", () => handleJump(system));
  }

  // Colony "found" buttons on each habitable planet
  content.querySelectorAll(".btn-found-colony").forEach(btn => {
    btn.addEventListener("click", () => {
      const planetName = btn.dataset.planet;
      const planetType = btn.dataset.type;
      handleFoundColony(system.name, planetName, planetType);
    });
  });

  // Fetch market data in the background and inject the trade section when ready
  try {
    _marketData = await getMarket(system.name);
    _renderMarketSection(system.name, _marketData);
  } catch (_err) {
    // No market at this system — hide the placeholder
    const placeholder = content.querySelector(".market-placeholder");
    if (placeholder) placeholder.remove();
  }
}

function hideRightPanel() {
  const panel = document.getElementById("panel-right");
  if (panel) panel.classList.add("panel--hidden");
  state.rightPanelOpen = false;
}

/** Build the HTML for the system detail panel */
function buildSystemPanelHtml(system, shipCoords) {
  const threatColor = system.threat_level >= 7 ? "var(--accent-red)"
    : system.threat_level >= 4 ? "var(--accent-orange)"
    : "var(--accent-green)";

  const planets = system.planets || [];
  const planetRows = planets.map(p => `
    <div style="padding:var(--sp-2) var(--sp-3);border:1px solid var(--border-color);
                border-radius:2px;margin-bottom:var(--sp-2);background:var(--bg-tertiary)">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <span style="color:var(--text-bright);font-size:var(--font-size-xs);
                     text-transform:uppercase;letter-spacing:0.06em">${esc(p.name)}</span>
        <span style="font-size:var(--font-size-xs);color:var(--text-dim)">${esc(p.subtype)}</span>
      </div>
      ${p.population > 0
        ? `<div style="font-size:var(--font-size-xs);color:var(--text-dim);margin-top:var(--sp-1)">
             Pop: ${p.population.toLocaleString()}</div>`
        : ""}
      ${p.resources && p.resources.length > 0
        ? `<div style="font-size:var(--font-size-xs);color:var(--text-dim);margin-top:2px">
             ${p.resources.slice(0, 3).join(", ")}</div>`
        : ""}
      ${p.habitable
        ? `<button class="btn btn--sm btn--primary btn-found-colony"
                   style="margin-top:var(--sp-2);width:100%"
                   data-planet="${esc(p.name)}" data-type="${esc(p.subtype)}">
             ⊕ FOUND COLONY
           </button>`
        : ""}
    </div>
  `).join("") || `<p style="color:var(--text-dim);font-size:var(--font-size-xs)">
    No planets detected.</p>`;

  return `
    <div style="padding:var(--sp-3)">
      <!-- System header -->
      <div style="border-bottom:1px solid var(--border-accent);padding-bottom:var(--sp-3);
                  margin-bottom:var(--sp-3)">
        <h3 style="color:var(--accent-teal);letter-spacing:0.12em;font-size:var(--font-size-md)">
          ${esc(system.name)}
        </h3>
        <div style="font-size:var(--font-size-xs);color:var(--text-dim);margin-top:var(--sp-1)">
          ${esc(system.type || "Unknown Type")}
        </div>
      </div>

      <!-- Stats -->
      <div style="margin-bottom:var(--sp-4)">
        <div class="stat-row">
          <span class="stat-row__label">Population</span>
          <span class="stat-row__value">${(system.population || 0).toLocaleString()}</span>
        </div>
        <div class="stat-row">
          <span class="stat-row__label">Threat Level</span>
          <span class="stat-row__value" style="color:${threatColor}">${system.threat_level ?? "—"}/10</span>
        </div>
        <div class="stat-row">
          <span class="stat-row__label">Resources</span>
          <span class="stat-row__value">${esc(system.resources || "Unknown")}</span>
        </div>
        ${system.controlling_faction ? `
        <div class="stat-row">
          <span class="stat-row__label">Faction</span>
          <span class="stat-row__value" style="color:var(--accent-cyan)">${esc(system.controlling_faction)}</span>
        </div>` : ""}
      </div>

      <!-- Description -->
      ${system.description ? `
      <div style="font-size:var(--font-size-xs);color:var(--text-dim);line-height:1.5;
                  margin-bottom:var(--sp-4);padding:var(--sp-2);background:var(--bg-secondary);
                  border-left:2px solid var(--border-accent)">
        ${esc(system.description)}
      </div>` : ""}

      <!-- Jump button -->
      <button class="btn btn--primary btn-jump" style="width:100%;margin-bottom:var(--sp-4)">
        ▶ JUMP TO SYSTEM
      </button>

      <!-- Planets -->
      <div class="section-header" style="margin-bottom:var(--sp-2)">
        Planets (${planets.length})
      </div>
      ${planetRows}

      <!-- Market — injected asynchronously after getMarket() resolves -->
      <div class="market-placeholder" style="margin-top:var(--sp-4)">
        <div class="section-header" style="margin-bottom:var(--sp-2)">Market</div>
        <p style="color:var(--text-dim);font-size:var(--font-size-xs)">Loading market data…</p>
      </div>
    </div>
  `;
}


// ---------------------------------------------------------------------------
// Market / Trade UI
// ---------------------------------------------------------------------------

/**
 * Replace the .market-placeholder div with a full commodity table once
 * market data has been fetched.
 *
 * @param {string} systemName
 * @param {object} market  - response from GET /api/market/{system}
 */
function _renderMarketSection(systemName, market) {
  const placeholder = document.getElementById("panel-right-content")
                               ?.querySelector(".market-placeholder");
  if (!placeholder) return;

  const commodities = market.commodities || [];
  const credits     = market.player_credits ?? state.gameState?.player?.credits ?? 0;

  if (!commodities.length) {
    placeholder.innerHTML = `
      <div class="section-header" style="margin-bottom:var(--sp-2)">Market</div>
      <p style="color:var(--text-dim);font-size:var(--font-size-xs)">No commodities traded here.</p>
    `;
    return;
  }

  // Build the commodity rows.
  // The backend returns a single "price" per commodity.
  // Sell price is conventionally 80% of buy price (handled server-side).
  const rows = commodities.map(c => {
    const price     = c.price ?? 0;
    const sellEst   = Math.round(price * 0.8);
    const canBuy    = price > 0 && c.supply > 0;
    const canSell   = price > 0 && c.in_inventory > 0;
    return `
      <div class="market-row" data-commodity="${esc(c.name)}">
        <div class="market-row__name">${esc(c.name)}</div>
        <div class="market-row__prices">
          <span style="color:var(--accent-teal)">${canBuy ? price + " ⊕" : "—"}</span>
          <span style="color:var(--accent-gold)">${price > 0 ? sellEst + " ⊗" : "—"}</span>
        </div>
        <div class="market-row__stock muted">${c.supply ?? "—"} in stock</div>
        ${c.in_inventory > 0
          ? `<div class="market-row__held muted">Holding: ${c.in_inventory}</div>`
          : ""}
        <div class="market-row__actions">
          ${canBuy ? `
            <input type="number" class="market-qty-input" value="1" min="1"
                   data-commodity="${esc(c.name)}" data-action="buy"
                   title="Quantity to buy" style="width:44px">
            <button class="btn btn--sm btn--primary btn-trade"
                    data-system="${esc(systemName)}"
                    data-commodity="${esc(c.name)}" data-action="buy">BUY</button>
          ` : ""}
          ${canSell ? `
            <input type="number" class="market-qty-input" value="1" min="1"
                   max="${c.in_inventory}"
                   data-commodity="${esc(c.name)}" data-action="sell"
                   title="Quantity to sell" style="width:44px">
            <button class="btn btn--sm btn--secondary btn-trade"
                    data-system="${esc(systemName)}"
                    data-commodity="${esc(c.name)}" data-action="sell">SELL</button>
          ` : ""}
        </div>
      </div>
    `;
  }).join("");

  placeholder.innerHTML = `
    <div class="section-header" style="margin-bottom:var(--sp-2)">
      Market
      <span class="muted" style="font-size:10px;margin-left:var(--sp-2)">
        Credits: <strong style="color:var(--accent-gold)">${credits.toLocaleString()}</strong>
      </span>
    </div>
    <div class="market-table">${rows}</div>
  `;
  placeholder.classList.remove("market-placeholder"); // prevent double-inject

  // Wire trade buttons — each button reads its sibling qty input
  placeholder.querySelectorAll(".btn-trade").forEach(btn => {
    btn.addEventListener("click", () => {
      const action    = btn.dataset.action;
      const commodity = btn.dataset.commodity;
      const system    = btn.dataset.system;
      // Find the qty input that matches this button's commodity+action
      const qtyInput  = placeholder.querySelector(
        `.market-qty-input[data-commodity="${CSS.escape(commodity)}"][data-action="${action}"]`
      );
      const qty = parseInt(qtyInput?.value || "1", 10);
      _doTrade(system, commodity, action, qty, btn);
    });
  });
}


/**
 * Execute a buy or sell trade action, then refresh the market section.
 *
 * @param {string} systemName
 * @param {string} commodity
 * @param {"buy"|"sell"} action
 * @param {number} quantity
 * @param {HTMLElement} btn   The button that was clicked (for disabled feedback)
 */
async function _doTrade(systemName, commodity, action, quantity, btn) {
  if (!quantity || quantity < 1) {
    notify("ERROR", "Enter a quantity of at least 1.");
    return;
  }

  const origText = btn.textContent;
  btn.disabled   = true;
  btn.textContent = action === "buy" ? "BUYING…" : "SELLING…";

  try {
    const fn     = action === "buy" ? buyGoods : sellGoods;
    const result = await fn(systemName, commodity, quantity);

    notify("TRADE", result.message || `${action.toUpperCase()} complete.`);

    // Update credits in local state immediately so HUD reflects the change
    if (state.gameState?.player) {
      state.gameState.player.credits = result.credits_remaining;
    }

    // Re-fetch market and refresh the section so prices/stock are up-to-date
    _marketData = await getMarket(systemName);
    _renderMarketSection(systemName, _marketData);

  } catch (err) {
    notify("ERROR", err.message || "Trade failed.");
    btn.disabled   = false;
    btn.textContent = origText;
  }
}


// ---------------------------------------------------------------------------
// Jump action
// ---------------------------------------------------------------------------

async function handleJump(system) {
  const btn = document.querySelector(".btn-jump");
  if (btn) { btn.disabled = true; btn.textContent = "JUMPING..."; }

  try {
    const result = await jumpToCoords(system.x, system.y, system.z);

    if (result.success) {
      notify("NAV", `Arrived at ${system.name}.  Fuel: ${result.fuel_remaining}`);

      // Update the visited flag in our local cache
      const cached = systemsData.find(s => s.name === system.name);
      if (cached) cached.visited = true;

      // Update ship coordinates in state immediately so the marker moves
      // without waiting for the 1-second polling loop to catch up.
      if (state.gameState?.ship && result.new_coords) {
        state.gameState.ship.coordinates = result.new_coords;
      }

      // Refresh state
      state.selectedSystem = { ...state.selectedSystem, visited: true };
      isDirty = true;
    } else {
      notify("ERROR", result.message || "Jump failed.");
    }
  } catch (err) {
    notify("ERROR", `Jump failed: ${err.message}`);
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = "▶ JUMP TO SYSTEM"; }
  }
}


// ---------------------------------------------------------------------------
// Found colony — navigate to the colony surface view (Phase 3)
// ---------------------------------------------------------------------------

async function handleFoundColony(systemName, planetName, planetType) {
  // Store the selected planet so the C shortcut can return here
  state.selectedPlanet = { planetName, systemName, planetType };

  // Lazy import to avoid circular dependency (galaxy imports main, main imports galaxy)
  const { switchView } = await import("../main.js");
  switchView("colony", { planetName, systemName, planetType });
}


// ---------------------------------------------------------------------------
// Tiny HTML escape helper
// ---------------------------------------------------------------------------

function esc(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}


// ---------------------------------------------------------------------------
// Close button wire-up (called once by panels.js in Phase 2)
// ---------------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {
  const closeBtn = document.getElementById("panel-right-close");
  if (closeBtn) {
    closeBtn.addEventListener("click", () => {
      viewState.selectedSystemName = null;
      state.selectedSystem = null;
      hideRightPanel();
      isDirty = true;
    });
  }
});
