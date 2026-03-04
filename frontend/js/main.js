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
import { getGameState, getGameOptions, endTurn } from "./api.js";
import { setupView }    from "./views/setup.js";
import { notify }       from "./ui/notifications.js";

import { galaxyView }    from "./views/galaxy.js";
import { colonyView }    from "./views/colony.js";
import { researchView }  from "./views/research.js";
import { diplomacyView } from "./views/diplomacy.js";
import { shipView }      from "./views/ship.js";
import { tradeView }     from "./views/trade.js";

// ---------------------------------------------------------------------------
// View registry — maps view name → { mount(), unmount() }
// ---------------------------------------------------------------------------
const VIEWS = {
  setup:     setupView,
  galaxy:    galaxyView,
  colony:    colonyView,
  ship:      shipView,
  research:  researchView,
  diplomacy: diplomacyView,
  trade:     tradeView,
};

/** DOM container for each view */
const viewEls = {
  setup:     document.getElementById("view-setup"),
  galaxy:    document.getElementById("view-galaxy"),
  colony:    document.getElementById("view-colony"),
  ship:      document.getElementById("view-ship"),
  research:  document.getElementById("view-research"),
  diplomacy: document.getElementById("view-diplomacy"),
  trade:     document.getElementById("view-trade"),
};

// ---------------------------------------------------------------------------
// switchView — the one place that controls which view is active
// ---------------------------------------------------------------------------

/**
 * Show a view and hide all others.
 * @param {string} viewName - Key in VIEWS: "setup" | "galaxy" | "colony" | "research" | "diplomacy"
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
  setText("hud-turn", `Turn ${t.current_turn} / ${t.max_turns}`);

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

    // Fire a notification toast for each turn event
    if (result.events && Array.isArray(result.events)) {
      result.events.forEach(evt => {
        notify(evt.channel, evt.message);
      });
    }

    // Refresh HUD immediately without waiting for next poll
    if (result.state) {
      state.gameState = result.state;
      updateHud(result.state);
    }

    if (result.game_ended) {
      notify("TURN", "The game has ended. Final score coming in Phase 6.");
    }
  } catch (err) {
    notify("ERROR", err.message);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = "END TURN";
    }
  }
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
        if (state.selectedPlanet) switchView("colony");
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
