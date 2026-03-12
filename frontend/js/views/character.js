/**
 * views/character.js — Character sheet view.
 *
 * Displays base stats, derived metrics, class info, background traits,
 * and equipment/cybernetic/etheric slots.
 *
 * All data comes from GET /api/character/sheet.
 */

import { getCharacterSheet } from "../api.js";
import { notify }            from "../ui/notifications.js";


// ---------------------------------------------------------------------------
// Public view object
// ---------------------------------------------------------------------------

export const characterView = { mount, unmount };


async function mount() {
  const container = document.getElementById("character-container");
  if (!container) return;

  container.innerHTML = '<p class="char__loading">Loading character data…</p>';

  let sheet;
  try {
    sheet = await getCharacterSheet();
  } catch (err) {
    container.innerHTML = `<p class="char__error">Could not load character sheet: ${err.message}</p>`;
    return;
  }

  container.innerHTML = _buildSheet(sheet);
}

function unmount() { /* nothing to clean up */ }


// ---------------------------------------------------------------------------
// Rendering
// ---------------------------------------------------------------------------

function _buildSheet(s) {
  return `
    <div class="char-sheet">

      ${_buildHeader(s)}

      <div class="char-sheet__body">

        <div class="char-sheet__col char-sheet__col--left">
          ${_buildStatsSection(s.stats)}
          ${_buildDerivedSection(s.derived)}
        </div>

        <div class="char-sheet__col char-sheet__col--right">
          ${_buildClassSection(s)}
          ${_buildProfessionSection(s)}
          ${_buildBackgroundSection(s)}
          ${_buildFactionSection(s)}
          ${_buildGearSection("EQUIPMENT",            s.equipment,            "No equipment installed.")}
          ${_buildGearSection("CYBERNETICS",          s.cybernetics,          "No cybernetic augmentations.")}
          ${_buildGearSection("ETHERIC ENHANCEMENTS", s.etheric_enhancements, "No etheric enhancements.")}
        </div>

      </div>
    </div>
  `;
}


function _buildHeader(s) {
  const xpPct = Math.min(100, Math.round((s.xp / Math.max(1, s.level * 100)) * 100));
  return `
    <div class="char-sheet__header">
      <div class="char-sheet__avatar" aria-label="Character portrait placeholder">
        <span class="char-sheet__avatar-glyph">◉</span>
      </div>
      <div class="char-sheet__identity">
        <h1 class="char-sheet__name">${esc(s.name)}</h1>
        <div class="char-sheet__meta">
          <span class="char-sheet__tag">${esc(s.character_class)}</span>
          <span class="char-sheet__sep">·</span>
          <span class="char-sheet__tag char-sheet__tag--dim">${esc(s.species)}</span>
          <span class="char-sheet__sep">·</span>
          <span class="char-sheet__tag char-sheet__tag--dim">${esc(s.background)}</span>
          ${s.faction ? `<span class="char-sheet__sep">·</span>
          <span class="char-sheet__tag char-sheet__tag--faction">${esc(s.faction)}</span>` : ""}
          ${s.profession ? `<span class="char-sheet__sep">·</span>
          <span class="char-sheet__tag char-sheet__tag--profession">${esc(s.profession)}</span>` : ""}
        </div>
        <div class="char-sheet__xp-row">
          <span class="char-sheet__xp-label">LVL ${s.level}</span>
          <div class="char-sheet__xp-bar">
            <div class="char-sheet__xp-fill" style="width:${xpPct}%"></div>
          </div>
          <span class="char-sheet__xp-val">${s.xp} XP</span>
        </div>
      </div>
    </div>
  `;
}


function _buildStatsSection(stats) {
  const rows = stats.map(st => {
    const pct = Math.round((st.value / 100) * 100);
    const tierClass = st.value >= 70 ? "char-stat__bar-fill--high"
                    : st.value >= 50 ? "char-stat__bar-fill--mid"
                    : "";
    return `
      <div class="char-stat" title="${esc(st.description)}">
        <span class="char-stat__abbr">${esc(st.abbr)}</span>
        <span class="char-stat__name">${esc(st.name)}</span>
        <div class="char-stat__bar">
          <div class="char-stat__bar-fill ${tierClass}" style="width:${pct}%"></div>
        </div>
        <span class="char-stat__val">${st.value}</span>
      </div>
    `;
  }).join("");

  return `
    <section class="char-section">
      <div class="char-section__title">CORE STATS</div>
      <div class="char-stats-list">${rows}</div>
    </section>
  `;
}


function _buildDerivedSection(derived) {
  const rows = derived.map(d => `
    <div class="char-derived" title="${esc(d.formula)} — ${esc(d.description)}">
      <span class="char-derived__name">${esc(d.name)}</span>
      <span class="char-derived__val">${d.value}</span>
      <span class="char-derived__formula">${esc(d.formula)}</span>
    </div>
  `).join("");

  return `
    <section class="char-section">
      <div class="char-section__title">DERIVED ATTRIBUTES</div>
      <div class="char-derived-list">${rows}</div>
    </section>
  `;
}


function _buildClassSection(s) {
  const bonusChips = Object.entries(s.bonuses).map(([k, v]) =>
    `<div class="char-chip"><span class="char-chip__key">${esc(k)}</span><span class="char-chip__val">${esc(v)}</span></div>`
  ).join("");

  const skillChips = s.skills.map(sk =>
    `<span class="char-skill">${esc(sk)}</span>`
  ).join("");

  return `
    <section class="char-section">
      <div class="char-section__title">CLASS — ${esc(s.character_class)}</div>
      <p class="char-section__desc">${esc(s.class_description)}</p>
      ${skillChips ? `<div class="char-skills">${skillChips}</div>` : ""}
      ${bonusChips ? `<div class="char-chips">${bonusChips}</div>` : ""}
    </section>
  `;
}


/**
 * Render the PROFESSION section.
 *
 * Shows: category tag, description, 5 core skills, and all four benefit tiers.
 * Benefits at tiers the player hasn't reached yet are rendered dimmed with a
 * lock indicator so they remain visible as goals.
 *
 * Tier unlock thresholds (matching ProfessionSystem):
 *   Base          — always unlocked (level ≥ 1)
 *   Intermediate  — level ≥ 3
 *   Advanced      — level ≥ 6
 *   Master        — level ≥ 9
 */
function _buildProfessionSection(s) {
  if (!s.profession) {
    return `
      <section class="char-section">
        <div class="char-section__title">PROFESSION</div>
        <p class="char-section__empty">No profession selected.</p>
      </section>
    `;
  }

  const level = s.profession_level || 1;

  // Five core skill chips
  const skillChips = (s.profession_skills || []).map(sk =>
    `<span class="char-skill char-skill--prof">${esc(sk)}</span>`
  ).join("");

  // XP bar for this profession
  const xpPct   = Math.min(100, Math.round(((s.profession_xp % 100) / 100) * 100));
  const xpBar   = `
    <div class="char-prof__xp-row">
      <span class="char-prof__xp-label">LEVEL ${level}</span>
      <div class="char-sheet__xp-bar">
        <div class="char-sheet__xp-fill" style="width:${xpPct}%"></div>
      </div>
      <span class="char-prof__xp-val">${s.profession_xp} XP</span>
    </div>
  `;

  // Benefit tier definitions with unlock level thresholds
  const tiers = [
    { key: "base",         label: "TIER I — BASE",         unlockAt: 1 },
    { key: "intermediate", label: "TIER II — DEVELOPING",  unlockAt: 3 },
    { key: "advanced",     label: "TIER III — EXPERT",     unlockAt: 6 },
    { key: "master",       label: "TIER IV — MASTER",      unlockAt: 9 },
  ];

  const tierHtml = tiers.map(tier => {
    const benefits  = (s.profession_tiers || {})[tier.key] || [];
    const unlocked  = level >= tier.unlockAt;
    const lockLabel = unlocked ? "" : `<span class="char-prof__lock">Unlocks at level ${tier.unlockAt}</span>`;

    const items = benefits.map(b => `
      <div class="char-prof__benefit${unlocked ? "" : " char-prof__benefit--locked"}">
        <span class="char-prof__benefit-dot">${unlocked ? "◈" : "○"}</span>
        <span class="char-prof__benefit-text">${esc(b)}</span>
      </div>
    `).join("");

    return `
      <div class="char-prof__tier${unlocked ? "" : " char-prof__tier--locked"}">
        <div class="char-prof__tier-label">${esc(tier.label)} ${lockLabel}</div>
        <div class="char-prof__tier-items">${items || "<span style='color:var(--text-dim);font-size:var(--font-size-xs)'>—</span>"}</div>
      </div>
    `;
  }).join("");

  return `
    <section class="char-section">
      <div class="char-section__title">PROFESSION — ${esc(s.profession)}</div>
      <div class="char-prof__category-tag">${esc(s.profession_category)}</div>
      <p class="char-section__desc">${esc(s.profession_description)}</p>
      ${xpBar}
      ${skillChips ? `<div class="char-skills char-skills--prof">${skillChips}</div>` : ""}
      <div class="char-prof__tiers">${tierHtml}</div>
    </section>
  `;
}


function _buildBackgroundSection(s) {
  const traitChips = s.traits.map(t =>
    `<span class="char-trait">${esc(t)}</span>`
  ).join("");

  return `
    <section class="char-section">
      <div class="char-section__title">BACKGROUND — ${esc(s.background)}</div>
      <p class="char-section__desc">${esc(s.background_description)}</p>
      ${traitChips ? `<div class="char-traits">${traitChips}</div>` : ""}
    </section>
  `;
}


function _buildFactionSection(s) {
  if (!s.faction) return "";
  const chips = [
    s.faction_philosophy ? `<span class="char-trait char-trait--faction">⬡ ${esc(s.faction_philosophy)}</span>` : "",
    s.faction_focus      ? `<span class="char-trait char-trait--faction">◈ ${esc(s.faction_focus)}</span>`      : "",
  ].filter(Boolean).join("");

  return `
    <section class="char-section">
      <div class="char-section__title">FACTION — ${esc(s.faction)}</div>
      ${s.faction_description ? `<p class="char-section__desc">${esc(s.faction_description)}</p>` : ""}
      ${chips ? `<div class="char-traits">${chips}</div>` : ""}
    </section>
  `;
}


function _buildGearSection(title, items, emptyMsg) {
  if (!items || items.length === 0) {
    return `
      <section class="char-section">
        <div class="char-section__title">${esc(title)}</div>
        <p class="char-section__empty">${esc(emptyMsg)}</p>
      </section>
    `;
  }
  const rows = items.map(item => `
    <div class="char-gear-item">
      <span class="char-gear-item__name">${esc(item.name || "Unknown")}</span>
      <span class="char-gear-item__slot">${esc(item.slot || "")}</span>
      <span class="char-gear-item__rarity char-gear-item__rarity--${esc(item.rarity || "common")}">${esc(item.rarity || "")}</span>
    </div>
  `).join("");
  return `
    <section class="char-section">
      <div class="char-section__title">${esc(title)}</div>
      <div class="char-gear-list">${rows}</div>
    </section>
  `;
}


function esc(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
