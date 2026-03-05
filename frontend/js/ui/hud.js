/**
 * ui/hud.js — HUD (Heads-Up Display) helper functions.
 *
 * The HUD bar is rendered in HTML (not Canvas) for accessibility and easy
 * DOM updates.  main.js drives HUD updates via the polling loop.
 * This module provides reusable helpers that other views can also call.
 */

import { state }                    from "../state.js";
import { showModal, closeModal }    from "./modal.js";


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

  // Update the four composite power indices
  if (gs.indices) {
    renderIndices(gs.indices);
  }
}



// ---------------------------------------------------------------------------
// Index metadata — descriptions and component formulas shown in detail modal
// ---------------------------------------------------------------------------

const INDEX_META = {
  spi: {
    label:       "Strategic Power Index",
    color:       "var(--accent-red, #e05050)",
    description: "Measures overall military and strategic capability. Reflects fleet size, " +
                 "planetary defenses, weapons development, and intelligence gathering capacity.",
    components: {
      "Fleet Strength":          "Ships × 20  +  KIN ÷ 4",
      "Defense Grid":            "Colony Defense/turn × 20  +  KIN ÷ 5",
      "Strategic Weapons":       "KIN ÷ 3  +  Research Completed × 2",
      "Intelligence Capability": "INT ÷ 4  +  COH ÷ 6",
    },
  },
  rei: {
    label:       "Resource Extraction Index",
    color:       "var(--accent-gold, #d4a800)",
    description: "Measures the empire’s capacity to extract and distribute raw resources. " +
                 "Driven by mineral production, ether energy, and exploration reach.",
    components: {
      "Raw Material Access": "Colony Minerals/turn × 8  +  Systems Visited × 2",
      "Energy Production":   "Colony Ether/turn × 10  +  AEF ÷ 5",
      "Logistics Capacity":  "Ships × 12  +  Systems Visited × 3",
    },
  },
  kii: {
    label:       "Knowledge & Innovation Index",
    color:       "var(--accent-teal, #00d4aa)",
    description: "Measures scientific advancement and the rate of technological discovery. " +
                 "Reflects active research, completed technologies, and cognitive capability.",
    components: {
      "Research Output": "Colony Research/turn × 8  +  INT ÷ 4",
      "Education Level": "Research Completed × 6  +  INT ÷ 3",
      "AI Capability":   "SYN ÷ 3  +  AEF ÷ 6",
      "Innovation Rate": "SYN ÷ 5  +  COH ÷ 8",
    },
  },
  eci: {
    label:       "Economic Capability Index",
    color:       "#4caf80",
    description: "Measures the economic strength of the empire. Combines industrial output " +
                 "from colonies, trade income, energy conversion, and financial reserves.",
    components: {
      "Industrial Output":   "Colony Minerals/turn × 4  +  Colony Food/turn × 3",
      "Trade Volume":        "Colony Credits/turn × 10  +  Credits ÷ 5000",
      "Energy Output":       "Colony Ether/turn × 6  +  AEF ÷ 5",
      "Financial Liquidity": "min(500,  Credits ÷ 2000)",
    },
  },
};

const INDEX_INPUTS = {
  spi: ["Ships owned", "KIN stat", "INT stat", "COH stat", "Research completed", "Colony defense/turn"],
  rei: ["Ships owned", "Colony minerals/turn", "Colony ether/turn", "AEF stat", "Systems visited"],
  kii: ["Colony research/turn", "Research completed", "INT stat", "SYN stat", "AEF stat", "COH stat"],
  eci: ["Colony minerals/turn", "Colony food/turn", "Colony credits/turn", "Colony ether/turn", "AEF stat", "Credits"],
};

let _lastIndices = null;

/**
 * Render SPI / REI / KII / ECI values and wire click-to-detail handlers.
 * @param {object} indices - The gs.indices object from the state snapshot.
 */
export function renderIndices(indices) {
  _lastIndices = indices;
  const keys = ["spi", "rei", "kii", "eci"];

  keys.forEach(key => {
    const val = indices[key] ?? 0;
    setText(`hud-${key}-val`, val);

    const el = document.getElementById(`hud-${key}`);
    if (!el) return;

    // Wire click handler only once per element
    if (!el.dataset.indexBound) {
      el.dataset.indexBound = "1";
      el.style.cursor = "pointer";
      el.title = `${INDEX_META[key].label} — click for details`;
      el.addEventListener("click", () => _openIndexModal(key));
    }
  });
}

/**
 * Open the detail modal for one index.
 * @param {"spi"|"rei"|"kii"|"eci"} key
 */
function _openIndexModal(key) {
  const indices = _lastIndices || {};
  const meta    = INDEX_META[key];
  const details = (indices.details ?? {})[key] ?? {};
  const inputs  = indices.inputs ?? {};
  const total   = indices[key] ?? 0;

  const compValues = Object.values(details);
  const maxComp    = Math.max(...compValues, 1);

  const compRows = Object.entries(details).map(([name, val]) => {
    const pct     = Math.round((val / maxComp) * 100);
    const formula = (meta.components ?? {})[name] || "";
    return `
      <div class="idx-comp-row">
        <div class="idx-comp-header">
          <span class="idx-comp-name">${name}</span>
          <span class="idx-comp-val" style="color:${meta.color}">${val}</span>
        </div>
        ${formula ? `<div class="idx-comp-formula">${formula}</div>` : ""}
        <div class="idx-bar-track">
          <div class="idx-bar-fill" style="width:${pct}%;background:${meta.color}"></div>
        </div>
      </div>
    `;
  }).join("");

  const relevantKeys = INDEX_INPUTS[key] || [];
  const inputRows = relevantKeys
    .filter(k => k in inputs)
    .map(k => `<tr><td class="idx-input-label">${k}</td><td class="idx-input-val">${inputs[k]}</td></tr>`)
    .join("");

  const body = `
    <div class="idx-modal">
      <div class="idx-modal-score" style="color:${meta.color}">${total}</div>
      <p class="idx-modal-desc">${meta.description}</p>
      <h4 class="idx-section-title">Component Breakdown</h4>
      <div class="idx-comp-list">${compRows}</div>
      <h4 class="idx-section-title">Contributing Inputs</h4>
      <table class="idx-inputs-table"><tbody>${inputRows}</tbody></table>
    </div>
  `;

  showModal(meta.label, body, [
    { label: "Close", className: "btn--secondary", onClick: () => closeModal() },
  ], { wide: true });
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
