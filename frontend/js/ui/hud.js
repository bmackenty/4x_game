/**
 * ui/hud.js — HUD (Heads-Up Display) helper functions.
 *
 * The HUD bar is rendered in HTML (not Canvas) for accessibility and easy
 * DOM updates.  main.js drives HUD updates via the polling loop.
 * This module provides reusable helpers that other views can also call.
 */

import { state } from "../state.js";


/**
 * Force an immediate HUD refresh from the current state.gameState.
 * Called after turn end or other state-mutating actions.
 */
export function refreshHud() {
  const gs = state.gameState;
  if (!gs || !gs.initialized) return;

  const p = gs.player;
  const t = gs.turn;
  const r = gs.research;

  setText("hud-player-name", p.name);
  setText("hud-class", p.character_class);
  setText("hud-credits", `⬡ ${p.credits.toLocaleString()}`);
  setText("hud-turn",    `Turn ${t.current_turn} / ${t.max_turns}`);
  renderActionPips(t.actions_remaining, t.max_actions);

  if (r.active) {
    setText("hud-research-name", r.active);
    const pct = r.total_time
      ? Math.min(100, Math.round((r.progress / r.total_time) * 100))
      : 0;
    setStyle("hud-research-fill", "width", `${pct}%`);
  } else {
    setText("hud-research-name", "No research");
    setStyle("hud-research-fill", "width", "0%");
  }
}


// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

function setStyle(id, prop, value) {
  const el = document.getElementById(id);
  if (el) el.style[prop] = value;
}

function renderActionPips(remaining, max) {
  const container = document.getElementById("hud-actions");
  if (!container) return;
  container.innerHTML = "";
  for (let i = 0; i < max; i++) {
    const pip = document.createElement("span");
    pip.className = `action-pip ${i < remaining ? "action-pip--full" : "action-pip--empty"}`;
    container.appendChild(pip);
  }
}
