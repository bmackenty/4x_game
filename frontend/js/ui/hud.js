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
  setText("hud-turn",    `Turn ${t.current_turn}${t.max_turns > 0 ? " / " + t.max_turns : ""}`);
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
    description: "Measures overall military and strategic capability. Starts near zero and grows " +
                 "only through real in-game progress: fleet production, colony defenses, completed " +
                 "research, and alignment with military-adjacent factions (Industry / Technology).",
    components: {
      "Fleet Strength (pool)":   "Fleet Pool  (grows via Shipyards each turn)",
      "Defense Grid":            "Colony Defense/turn × 25  +  Colonies × 20",
      "Combat Doctrine":         "Research Completed × 4  +  KIN ÷ 20",
      "Intelligence Capability": "INT ÷ 20  +  COH ÷ 20",
      "Faction Bonus":           "Allied faction (Industry/Technology): rep>10 → +4,  rep>50 → +12,  rep>75 → +25",
    },
  },
  rei: {
    label:       "Resource Extraction Index",
    color:       "var(--accent-gold, #d4a800)",
    description: "Measures the empire’s capacity to extract, harvest, and distribute raw " +
                 "resources across explored space. Driven by colony production chains, " +
                 "etheric energy output, exploration reach, character stats (KIN/SYN/COH/AEF), " +
                 "and profession — 20 extraction and logistics professions apply direct " +
                 "multipliers to sub-components, scaled by profession level (10% at level 1 → " +
                 "100% at level 10). Industry and Exploration-aligned factions provide " +
                 "rep-gated network bonuses.",
    components: {
      "Raw Material Access":   "Colony Minerals/turn × 8  +  Refined Ore/turn × 6  +  Systems Visited × 2",
      "Energy Production":     "Colony Ether/turn × 10  +  AEF ÷ 5",
      "Logistics Capacity":    "Ships × 12  +  Systems Visited × 3",
      "Extraction Aptitude":   "KIN ÷ 8  +  SYN ÷ 10  +  COH ÷ 12  (physical precision + tech integration + sustained ops)",
      "Prospecting Advantage": "AEF ÷ 6  +  Systems Visited  (etheric deposit sensing + exploration breadth)",
      "Profession Bonus":      "Per-component multipliers × profession level ÷ 10  (extraction/logistics professions only)",
      "Faction Bonus":         "Industry / Exploration faction: rep>10 → +5,  rep>50 → +15,  rep>75 → +30",
    },
  },
  kii: {
    label:       "Knowledge & Innovation Index",
    color:       "var(--accent-teal, #00d4aa)",
    description: "Measures scientific advancement and the rate of technological discovery. " +
                 "Driven by colony research output, completed technologies, AI and etheric " +
                 "cognition, and character stats (INT/SYN/COH/AEF). Two new components " +
                 "compound over time: Cognitive Aptitude (raw intellectual capacity) and " +
                 "Knowledge Network (breadth of research + exploration reinforcing new " +
                 "discovery). 25 research, education, and AI professions apply direct " +
                 "multipliers to sub-components, scaled by profession level (10% → 100%). " +
                 "Technology and Science factions provide rep-gated archive bonuses.",
    components: {
      "Research Output":    "Colony Research/turn × 8  +  INT ÷ 4",
      "Education Level":    "Research Completed × 6  +  INT ÷ 3",
      "AI Capability":      "SYN ÷ 3  +  AEF ÷ 6",
      "Innovation Rate":    "SYN ÷ 5  +  COH ÷ 8",
      "Cognitive Aptitude": "INT ÷ 6  +  COH ÷ 8  +  AEF ÷ 8  (raw intellectual + etheric pattern recognition)",
      "Knowledge Network":  "Research Completed × 3  +  Systems Visited ÷ 2  (breadth compounds discovery)",
      "Profession Bonus":   "Per-component multipliers × profession level ÷ 10  (research/education/AI professions only)",
      "Faction Bonus":      "Technology / Science faction: rep>10 → +5,  rep>50 → +15,  rep>75 → +30",
    },
  },
  eci: {
    label:       "Economic Capability Index",
    color:       "#4caf80",
    description: "Measures the economic strength of the empire. Combines colony industrial " +
                 "output, trade income, energy conversion, and financial reserves with two " +
                 "compounding drivers: Commercial Acumen (INT/SYN/COH stat-driven capacity " +
                 "for negotiation and market integration) and Infrastructure Depth (colonies, " +
                 "ships, and refined ore signalling upstream industrial maturity). 20 trade, " +
                 "industrial, and logistics professions apply direct multipliers, scaled by " +
                 "profession level (10% → 100%). Trade, Commerce, and Industry factions " +
                 "provide rep-gated lane and tariff bonuses.",
    components: {
      "Industrial Output":    "Colony Minerals/turn × 4  +  Colony Food/turn × 3",
      "Trade Volume":         "Colony Credits/turn × 10  +  Credits ÷ 5000",
      "Energy Output":        "Colony Ether/turn × 6  +  AEF ÷ 5",
      "Financial Liquidity":  "min(500,  Credits ÷ 2000)",
      "Commercial Acumen":    "INT ÷ 8  +  SYN ÷ 10  +  COH ÷ 12  (pricing, market integration, relationship stability)",
      "Infrastructure Depth": "Colonies × 4  +  Ships × 3  +  Refined Ore/turn × 2  (upstream industrial maturity)",
      "Profession Bonus":     "Per-component multipliers × profession level ÷ 10  (trade/industrial/logistics professions only)",
      "Faction Bonus":        "Trade / Commerce / Industry faction: rep>10 → +5,  rep>50 → +15,  rep>75 → +30",
    },
  },
};

const INDEX_INPUTS = {
  spi: ["Fleet pool", "Colony defense/turn", "Colonies founded", "Research completed",
        "KIN stat", "INT stat", "COH stat",
        "Allied faction", "Faction focus", "Faction reputation"],
  rei: [
    "Colony minerals/turn", "Colony refined ore/turn", "Colony ether/turn",
    "Ships owned", "Systems visited",
    "KIN stat", "SYN stat", "COH stat", "AEF stat",
    "REI Profession", "REI Profession level", "REI Profession scale",
    "Allied faction", "Faction focus", "Faction reputation",
  ],
  kii: [
    "Colony research/turn", "Research completed", "Systems visited",
    "INT stat", "SYN stat", "COH stat", "AEF stat",
    "KII Profession", "KII Profession level", "KII Profession scale",
    "Allied faction", "Faction focus", "Faction reputation",
  ],
  eci: [
    "Colony minerals/turn", "Colony food/turn", "Colony credits/turn", "Colony ether/turn",
    "Colony refined ore/turn", "Colonies founded", "Ships owned", "Credits",
    "INT stat", "SYN stat", "COH stat", "AEF stat",
    "ECI Profession", "ECI Profession level", "ECI Profession scale",
    "Allied faction", "Faction focus", "Faction reputation",
  ],
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

