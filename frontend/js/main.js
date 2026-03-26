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
import { getGameState, getGameOptions, endTurn, saveGame, listSaves, loadGame } from "./api.js";
import { titleView }    from "./views/title.js";
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
import { editorView }    from "./views/editor.js";
import { systemView }    from "./views/system.js";

// ---------------------------------------------------------------------------
// View registry — maps view name → { mount(), unmount() }
// ---------------------------------------------------------------------------
const VIEWS = {
  title:     titleView,
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
  editor:    editorView,
  system:    systemView,
};

/** DOM container for each view */
const viewEls = {
  title:     document.getElementById("view-title"),
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
  editor:    document.getElementById("view-editor"),
  system:    document.getElementById("view-system"),
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

  // Research bar — clickable link to R&D view when a project is active
  const researchEl   = document.getElementById("hud-research");
  const researchNode = document.getElementById("hud-research-name");
  const researchFill = document.getElementById("hud-research-fill");

  if (r.active) {
    if (researchNode) researchNode.textContent = r.active;

    // Compute percentage complete
    const pct = r.total_time
      ? Math.min(100, Math.round((r.progress / r.total_time) * 100))
      : 0;
    if (researchFill) researchFill.style.width = `${pct}%`;

    // Make the research widget a clickable link to the R&D view.
    // Store the handler reference on the element so we can remove it later
    // and avoid stacking duplicate listeners across poll cycles.
    if (researchEl && !researchEl._researchClickHandler) {
      researchEl.style.cursor = "pointer";
      researchEl.title        = `${r.active} — click to open R&D`;
      researchEl._researchClickHandler = () => {
        // Pass selectActive so the R&D view auto-selects the current project
        if (state.gameInitialized) switchView("research", { selectActive: true });
      };
      researchEl.addEventListener("click", researchEl._researchClickHandler);
    } else if (researchEl) {
      // Update the title in case the active project name changed
      researchEl.title = `${r.active} — click to open R&D`;
    }
  } else {
    if (researchNode) researchNode.textContent = "No research";
    if (researchFill) researchFill.style.width = "0%";

    // Remove the click handler when no research is active
    if (researchEl && researchEl._researchClickHandler) {
      researchEl.removeEventListener("click", researchEl._researchClickHandler);
      researchEl._researchClickHandler = null;
      researchEl.style.cursor = "";
      researchEl.title        = "Active research";
    }
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



// ---------------------------------------------------------------------------
// End-turn button
// ---------------------------------------------------------------------------

export async function handleEndTurn() {
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

    // Show research completion modal first, then GNN broadcast
    if (result.newly_completed_research) {
      const showGnn = result.gnn_summary
        ? () => _showGnnModal(result.gnn_summary)
        : null;
      _showResearchCompleteModal(result.newly_completed_research, showGnn);
    } else if (result.gnn_summary) {
      _showGnnModal(result.gnn_summary);
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
 * Show a research completion modal.  Fires onContinue (if provided) when
 * the player dismisses it so the GNN modal can chain after.
 *
 * @param {object}   research    - { name, description, unlocks, category }
 * @param {Function} onContinue  - Called after the player dismisses.
 */
function _showResearchCompleteModal(research, onContinue) {
  const unlocksList = (research.unlocks || []).length
    ? `<ul class="research-complete__unlocks">
         ${research.unlocks.map(u => `<li>${u}</li>`).join("")}
       </ul>`
    : `<p class="research-complete__no-unlocks muted">No direct unlocks.</p>`;

  const body = `
    <div class="research-complete-modal">
      <div class="research-complete__category">${research.category || ""}</div>
      <p class="research-complete__desc">${research.description || ""}</p>
      <h4 class="research-complete__unlocks-heading">UNLOCKS</h4>
      ${unlocksList}
    </div>
  `;

  import("./ui/modal.js").then(({ showModal, closeModal }) => {
    showModal(
      `✦ RESEARCH COMPLETE — ${research.name}`,
      body,
      [{
        label: "CONTINUE",
        className: "btn--primary",
        onClick: () => { closeModal(); if (onContinue) onContinue(); },
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
      case "escape":                // Esc → game menu
        e.preventDefault();
        showGameMenu();
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

  const menuBtn = document.getElementById("btn-menu");
  if (menuBtn) {
    menuBtn.addEventListener("click", showGameMenu);
  }
}


// ---------------------------------------------------------------------------
// In-game menu (MENU button / Escape)
// ---------------------------------------------------------------------------

function showGameMenu() {
  import("./ui/modal.js").then(({ showModal, closeModal }) => {
    const body = `
      <div class="game-menu">
        <button class="game-menu__btn" id="gmenu-save">Save Game</button>
        <button class="game-menu__btn" id="gmenu-load">Load Game</button>
        <button class="game-menu__btn game-menu__btn--danger" id="gmenu-title">Return to Title</button>
      </div>
    `;

    showModal("GAME MENU", body,
      [{ label: "RESUME", className: "btn--secondary", onClick: () => closeModal() }]);

    setTimeout(() => {
      // Save
      document.getElementById("gmenu-save")?.addEventListener("click", async () => {
        try {
          await saveGame("autosave");
          closeModal();
          notify("SAVE", "Game saved.");
        } catch (err) {
          notify("ERROR", `Save failed: ${err.message}`);
        }
      });

      // Load — show save list
      document.getElementById("gmenu-load")?.addEventListener("click", async () => {
        closeModal();
        setTimeout(() => _showLoadFromMenu(), 50);
      });

      // Return to title
      document.getElementById("gmenu-title")?.addEventListener("click", () => {
        closeModal();
        stopPolling();
        hideHud();
        state.gameInitialized = false;
        switchView("title", { hasGame: true });
      });
    }, 50);
  });
}

async function _showLoadFromMenu() {
  const { showModal, closeModal } = await import("./ui/modal.js");

  let saves;
  try {
    const result = await listSaves();
    saves = result.saves || [];
  } catch (err) {
    showModal("LOAD GAME", `<p class="muted">Could not list saves: ${err.message}</p>`,
      [{ label: "CLOSE", className: "btn--secondary", onClick: () => closeModal() }]);
    return;
  }

  if (saves.length === 0) {
    showModal("LOAD GAME",
      `<p class="muted" style="text-align:center;padding:var(--sp-8) 0">No save files found.</p>`,
      [{ label: "CLOSE", className: "btn--secondary", onClick: () => closeModal() }]);
    return;
  }

  const rowsHtml = saves.map(s => `
    <div class="save-row" data-path="${String(s.path || s.name).replace(/"/g, "&quot;")}">
      <div class="save-row__name">${String(s.player_name || s.name).replace(/</g, "&lt;")}</div>
      <div class="save-row__meta">
        <span class="save-row__turn">Turn ${s.turn ?? "—"}</span>
        <span class="save-row__date">${s.timestamp ? new Date(s.timestamp).toLocaleDateString() : ""}</span>
      </div>
    </div>
  `).join("");

  showModal("LOAD GAME", `<div class="save-list">${rowsHtml}</div>`,
    [{ label: "CANCEL", className: "btn--ghost", onClick: () => closeModal() }]);

  setTimeout(() => {
    document.querySelectorAll(".save-row").forEach(row => {
      row.addEventListener("click", async () => {
        try {
          const result = await loadGame(row.dataset.path);
          closeModal();
          if (result.state) onGameStarted(result.state);
        } catch (err) {
          notify("ERROR", `Load failed: ${err.message}`);
        }
      });
    });
  }, 50);
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
  let hasGame = false;
  try {
    const gs = await getGameState();
    if (gs && gs.initialized) {
      state.gameState = gs;
      hasGame = true;
    }
  } catch (err) {
    // No game in progress — title will show New Game as primary action
  }

  // Always show the title screen first
  hideHud();
  await switchView("title", { hasGame });
}

// Run as soon as the DOM is ready
document.addEventListener("DOMContentLoaded", boot);
