/**
 * main.js — Application entry point.
 *
 * Responsibilities:
 *   1. Wait for DOM to be ready.
 *   2. Load character-creation options from the API.
 *   3. Check if a game is already in progress; route to the correct view.
 *   4. Expose a global switchView() function used by all view modules.
 *   5. Start a 1-second polling loop that refreshes HUD data.
 *   6. Wire up global keyboard shortcuts and the end-turn button.
 */

import { state }        from "./state.js";
import { renderIndices } from "./ui/hud.js";
import { getGameState, getGameOptions, endTurn } from "./api.js";
import { setupView }    from "./views/setup.js";
import { notify }       from "./ui/notifications.js";

import { galaxyView }    from "./views/galaxy.js";
import { colonyView }    from "./views/colony.js";
import { coloniesView }   from "./views/colonies.js";
import { researchView }  from "./views/research.js";
import { diplomacyView } from "./views/diplomacy.js";
import { shipView }      from "./views/ship.js";
import { tradeView }     from "./views/trade.js";
import { characterView } from "./views/character.js";
import { galaxy3dView }  from "./views/galaxy3d.js";

// ---------------------------------------------------------------------------
// View registry — maps view name → { mount(), unmount() }
// ---------------------------------------------------------------------------
const VIEWS = {
  setup:     setupView,
  galaxy:    galaxyView,
  colony:    colonyView,
  colonies:  coloniesView,
  ship:      shipView,
  research:  researchView,
  diplomacy: diplomacyView,
  trade:     tradeView,
  character: characterView,
  galaxy3d:  galaxy3dView,
};

/** DOM container for each view */
const viewEls = {
  setup:     document.getElementById("view-setup"),
  galaxy:    document.getElementById("view-galaxy"),
  colony:    document.getElementById("view-colony"),
  colonies:  document.getElementById("view-colonies"),
  ship:      document.getElementById("view-ship"),
  research:  document.getElementById("view-research"),
  diplomacy: document.getElementById("view-diplomacy"),
  trade:     document.getElementById("view-trade"),
  character: document.getElementById("view-character"),
  galaxy3d:  document.getElementById("view-galaxy3d"),
};

// ---------------------------------------------------------------------------
// switchView — the one place that controls which view is active
// ---------------------------------------------------------------------------

/**
 * Show a view and hide all others.
 * @param {string} viewName - Key in VIEWS: "setup" | "galaxy" | "colony" | "colonies" | "research" | "diplomacy"
 * @param {object} [context] - Optional data passed to the view's mount() function
 */
export async function switchView(viewName, context = {}) {
  if (!VIEWS[viewName]) {
    console.warn(`[main] Unknown view: ${viewName}`);
    return;
  }

  // Unmount the previous view (if it has an unmount hook)
  const prev = VIEWS[state.currentView];
  if (prev && typeof prev.unmount === "function") {
    prev.unmount();
  }

  // Hide all view containers
  Object.values(viewEls).forEach(el => {
    if (el) el.classList.remove("view--active");
  });

  // Show the target view container
  const targetEl = viewEls[viewName];
  if (targetEl) targetEl.classList.add("view--active");

  // Update state
  state.currentView = viewName;
  state.viewContext  = context;

  // Mount the new view
  await VIEWS[viewName].mount(context);

  // Update active nav button highlight in HUD
  document.querySelectorAll(".hud__nav-btn").forEach(btn => {
    btn.classList.toggle("hud__nav-btn--active", btn.dataset.view === viewName);
  });
}


// ---------------------------------------------------------------------------
// Polling loop — refreshes live game state every second
// ---------------------------------------------------------------------------

let pollingInterval = null;

function startPolling() {
  if (pollingInterval) return;  // Already running
  pollingInterval = setInterval(async () => {
    try {
      const fresh = await getGameState();
      state.gameState = fresh;

      if (fresh.initialized) {
        updateHud(fresh);
      }
    } catch (err) {
      // Silently ignore poll failures — the server might briefly be busy
      console.warn("[poll]", err.message);
    }
  }, 1000);
}

function stopPolling() {
  clearInterval(pollingInterval);
  pollingInterval = null;
}


// ---------------------------------------------------------------------------
// HUD helpers
// ---------------------------------------------------------------------------

/** Show the HUD bar and mark the body as game-active */
function showHud() {
  document.getElementById("hud").classList.remove("hud--hidden");
  document.body.classList.add("game-active");
}

/** Hide the HUD (during character creation) */
function hideHud() {
  document.getElementById("hud").classList.add("hud--hidden");
  document.body.classList.remove("game-active");
}

/**
 * Push fresh game state into the HUD elements.
 * @param {object} gs - Full game state object from /api/game/state
 */
function updateHud(gs) {
  if (!gs || !gs.initialized) return;

  const p = gs.player;
  const t = gs.turn;
  const r = gs.research;

  // Player identity
  setText("hud-player-name", p.name);
  setText("hud-class",       p.character_class);

  // Credits (formatted with comma separators)
  setText("hud-credits", `⬡ ${p.credits.toLocaleString()}`);

  // Turn counter
  setText("hud-turn", `Turn ${t.current_turn}${t.max_turns > 0 ? " / " + t.max_turns : ""}`);

  // Action pips
  renderActionPips(t.actions_remaining, t.max_actions);

  // Research bar
  if (r.active) {
    const researchNode = document.getElementById("hud-research-name");
    const researchFill = document.getElementById("hud-research-fill");
    if (researchNode) researchNode.textContent = r.active;

    // Compute percentage from active research data (Phase 4 will add total_time)
    // For now show indeterminate progress using turn count
    const pct = r.total_time
      ? Math.min(100, Math.round((r.progress / r.total_time) * 100))
      : 0;
    if (researchFill) researchFill.style.width = `${pct}%`;
  } else {
    setText("hud-research-name", "No research");
    const researchFill = document.getElementById("hud-research-fill");
    if (researchFill) researchFill.style.width = "0%";
  }

  // Composite power indices (SPI / REI / KII / ECI) — delegated to hud.js
  // which also wires the click-to-detail-modal handlers
  if (gs.indices) {
    renderIndices(gs.indices);
  }

  // Navigation status overlay (galaxy view bottom-left panel)
  updateNavStatus(gs.ship);
}

/**
 * Update the nav-status overlay with current ship data.
 * @param {object|null} ship - gs.ship from the state snapshot
 */
function updateNavStatus(ship) {
  if (!ship) return;

  const location  = ship.current_system || "Deep Space";
  const fuel      = ship.fuel      ?? 0;
  const maxFuel   = ship.max_fuel  ?? 1;
  const jumpRange = ship.jump_range ?? 15;
  const cargoUsed = ship.cargo_used ?? 0;
  const cargoMax  = ship.cargo_max  ?? 0;

  setText("nav-location",   location);
  setText("nav-fuel-text",  `${Math.round(fuel)} / ${Math.round(maxFuel)}`);
  setText("nav-jump-range", `${jumpRange} ly`);
  setText("nav-cargo",      `${cargoUsed} / ${cargoMax}`);

  // Show raw 3D coordinates for navigation debugging
  if (ship.coordinates) {
    const [cx, cy, cz] = ship.coordinates;
    setText("nav-coords", `(${Math.round(cx)}, ${Math.round(cy)}, ${Math.round(cz)})`);
  }

  const fillEl = document.getElementById("nav-fuel-fill");
  if (fillEl) {
    const pct = maxFuel > 0 ? Math.round((fuel / maxFuel) * 100) : 0;
    fillEl.style.width = `${pct}%`;
    fillEl.classList.toggle("nav-status__fuel-fill--warn", pct < 40 && pct >= 20);
    fillEl.classList.toggle("nav-status__fuel-fill--crit", pct < 20);
  }
}

function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

function renderActionPips(remaining, max) {
  const container = document.getElementById("hud-actions");
  if (!container) return;
  container.innerHTML = "";
  for (let i = 0; i < max; i++) {
    const pip = document.createElement("span");
    pip.className = "action-pip " + (i < remaining ? "action-pip--full" : "action-pip--empty");
    container.appendChild(pip);
  }
}


// ---------------------------------------------------------------------------
// End-turn button
// ---------------------------------------------------------------------------

async function handleEndTurn() {
  const btn = document.getElementById("btn-end-turn");
  if (btn) {
    btn.disabled = true;
    btn.textContent = "PROCESSING...";
  }

  try {
    const result = await endTurn();

    // Refresh HUD immediately without waiting for next poll
    if (result.state) {
      state.gameState = result.state;
      updateHud(result.state);
    }

    if (result.game_ended) {
      notify("TURN", "The game has ended. Final score coming in Phase 6.");
    }

    // Show scripted events modal first, then GNN on dismiss
    const showGnn = () => {
      if (result.gnn_summary) _showGnnModal(result.gnn_summary);
    };
    _showEventsModal(result.events ?? [], showGnn);
  } catch (err) {
    notify("ERROR", err.message);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = "END TURN";
    }
  }
}


/**
 * Show the end-of-turn events modal.  When the player dismisses it, calls
 * onContinue so the GNN modal can follow.
 *
 * @param {Array}    events     - List of event strings from the end-turn response.
 * @param {Function} onContinue - Called after the player clicks "Continue".
 */
function _showEventsModal(events, onContinue) {
  import("./ui/modal.js").then(({ showModal, closeModal }) => {
    const bodyHtml = events.length
      ? `<ul class="events-list">${events.map(e => `<li>${e}</li>`).join("")}</ul>`
      : `<p class="events-empty">No notable events this turn.</p>`;

    showModal(
      "END OF TURN — EVENTS",
      bodyHtml,
      [{
        label: "CONTINUE",
        className: "btn--primary",
        onClick: () => { closeModal(); onContinue(); },
      }],
    );
  });
}

/**
 * Build and display the Galactic News Network modal for the end-of-turn
 * summary.  Shows a comedic news broadcast plus the income/expense ledger.
 *
 * @param {object} gnn - The gnn_summary object from the end-turn API response.
 */
function _showGnnModal(gnn) {
  // ── Income / expense ledger ─────────────────────────────────────────────
  const ledger = gnn.ledger ?? {};

  const incomeRows = (ledger.income_lines ?? []).map(l =>
    `<tr><td>${l.label}</td><td class="gnn-ledger-val gnn-green">+${l.value.toLocaleString()} cr</td></tr>`
  ).join("");

  const colonyRows = (ledger.colony_lines ?? []).map(c =>
    `<tr>
       <td class="gnn-colony-name">${c.name}</td>
       <td class="gnn-colony-pop">${c.pop.toLocaleString()} pop</td>
       <td class="gnn-ledger-val gnn-green">+${c.income.toLocaleString()} cr</td>
     </tr>`
  ).join("");

  const researchLine = ledger.research_pts
    ? `<p class="gnn-research-line">Research output: <strong>+${ledger.research_pts} pts</strong> applied to active project.</p>`
    : "";

  const ledgerHtml = (incomeRows || colonyRows) ? `
    <section class="gnn-section gnn-ledger">
      <h3 class="gnn-section-title">FINANCIAL REPORT — TURN ${gnn.turn}</h3>
      <table class="gnn-table">
        <tbody>
          ${incomeRows}
        </tbody>
        <tfoot>
          <tr class="gnn-ledger-total">
            <td>Total colony income</td>
            <td class="gnn-ledger-val gnn-green">+${(ledger.total_income ?? 0).toLocaleString()} cr</td>
          </tr>
          <tr class="gnn-ledger-total">
            <td>Treasury balance</td>
            <td class="gnn-ledger-val gnn-gold">${(ledger.credits_after ?? 0).toLocaleString()} cr</td>
          </tr>
        </tfoot>
      </table>
      ${colonyRows ? `
        <details class="gnn-colony-detail">
          <summary>Colony breakdown</summary>
          <table class="gnn-table"><tbody>${colonyRows}</tbody></table>
        </details>` : ""}
      ${researchLine}
    </section>
  ` : "";

  // ── News items ────────────────────────────────────────────────────────────
  const newsHtml = (gnn.news_items ?? []).map(item =>
    `<p class="gnn-news-item">&#x25B6; ${item}</p>`
  ).join("");

  // ── Full modal body ───────────────────────────────────────────────────────
  const body = `
    <div class="gnn-modal">
      <div class="gnn-header">
        <span class="gnn-logo">GNN</span>
        <span class="gnn-tagline">GALACTIC NEWS NETWORK</span>
        <span class="gnn-turn">TURN ${gnn.turn} EDITION</span>
      </div>

      <div class="gnn-headline">
        <span class="gnn-breaking">BREAKING:</span>
        ${gnn.headline}
      </div>

      <div class="gnn-weather">
        <span class="gnn-weather-label">SPACE WEATHER:</span> ${gnn.weather}
      </div>

      ${ledgerHtml}

      <section class="gnn-section">
        <h3 class="gnn-section-title">TODAY'S STORIES</h3>
        <div class="gnn-news-feed">${newsHtml}</div>
      </section>

      <p class="gnn-closing">${gnn.closing}</p>
    </div>
  `;

  // Use the already-imported modal module via a dynamic import
  import("./ui/modal.js").then(({ showModal, closeModal }) => {
    showModal(
      `GNN — Turn ${gnn.turn} Broadcast`,
      body,
      [{ label: "DISMISS BROADCAST", className: "btn--secondary", onClick: () => closeModal() }],
      { wide: true },
    );
  });
}


// ---------------------------------------------------------------------------
// Keyboard shortcuts
// ---------------------------------------------------------------------------

function setupKeyboardShortcuts() {
  document.addEventListener("keydown", e => {
    // Don't fire shortcuts while typing in an input
    if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;
    if (!state.gameInitialized) return;

    switch (e.key.toLowerCase()) {
      case " ":                     // Space → end turn
        e.preventDefault();
        handleEndTurn();
        break;
      case "g":                     // G → galaxy map
        if (state.currentView !== "galaxy") switchView("galaxy");
        break;
      case "r":                     // R → research
        if (state.currentView !== "research") switchView("research");
        break;
      case "d":                     // D → diplomacy
        if (state.currentView !== "diplomacy") switchView("diplomacy");
        break;
      case "s":                     // S → ship stats
        if (state.currentView !== "ship") switchView("ship");
        break;
      case "c":                     // C → colony (only if a planet is selected)
        if (state.selectedPlanet) switchView("colony", state.selectedPlanet);
        break;
      case "l":                     // L → colonies management
        switchView("colonies");
        break;
      case "p":                     // P → character sheet (profile)
        if (state.currentView !== "character") switchView("character");
        break;
      case "3":                     // 3 → 3D galaxy view
        if (state.currentView !== "galaxy3d") switchView("galaxy3d");
        break;
    }
  });
}


// ---------------------------------------------------------------------------
// HUD nav buttons
// ---------------------------------------------------------------------------

function setupHudNav() {
  document.querySelectorAll(".hud__nav-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const target = btn.dataset.view;
      if (target && state.gameInitialized) {
        switchView(target);
      }
    });
  });

  const endTurnBtn = document.getElementById("btn-end-turn");
  if (endTurnBtn) {
    endTurnBtn.addEventListener("click", handleEndTurn);
  }
}


// ---------------------------------------------------------------------------
// Application bootstrap
// ---------------------------------------------------------------------------

/**
 * Called by the setup view when the player clicks "Begin" and the new-game
 * API call succeeds.  Exported so setup.js can call it.
 */
export function onGameStarted(gameState) {
  state.gameInitialized = true;
  state.gameState = gameState;

  showHud();
  updateHud(gameState);
  startPolling();
  switchView("galaxy");
}


async function boot() {
  console.log("[4X] Booting frontend...");

  // Wire up global event listeners
  setupKeyboardShortcuts();
  setupHudNav();

  // Load character-creation options (species, classes, backgrounds, factions)
  try {
    state.options = await getGameOptions();
  } catch (err) {
    console.error("[4X] Failed to load game options:", err);
    notify("ERROR", "Could not reach the game server. Is run.py running?");
  }

  // Check if there's already an active game (e.g. server restart with state)
  try {
    const gs = await getGameState();
    if (gs && gs.initialized) {
      // Resume existing game
      state.gameInitialized = true;
      state.gameState = gs;
      showHud();
      updateHud(gs);
      startPolling();
      await switchView("galaxy");
      return;
    }
  } catch (err) {
    // No game in progress — fall through to setup
  }

  // First visit: show character creation
  hideHud();
  await switchView("setup");
}

// Run as soon as the DOM is ready
document.addEventListener("DOMContentLoaded", boot);
