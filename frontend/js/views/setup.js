/**
 * views/setup.js — Character creation screen.
 *
 * Renders a multi-step form for choosing species, class, background,
 * faction, name, and stat allocation.  On submit it calls /api/game/new
 * and, on success, hands off to main.js's onGameStarted().
 *
 * The form never validates in real-time — it collects everything and
 * validates on submit, showing inline error messages.
 *
 * Follows the Alpha Centauri aesthetic: dark panels, teal accents,
 * monospace font, numbered steps.
 */

import { state }           from "../state.js";
import { newGame }         from "../api.js";
import { notify }          from "../ui/notifications.js";
// onGameStarted is imported lazily to avoid circular dep with main.js
let _onGameStarted = null;

// ---------------------------------------------------------------------------
// Setup form state — populated as the player makes selections
// ---------------------------------------------------------------------------
const form = {
  name:             "",
  character_class:  "",
  background:       "",
  species:          "",
  faction:          "",
  profession:       "",   // chosen from the PROFESSIONS catalogue
  stats: {          // Default: all stats at base value (30)
    VIT: 30, KIN: 30, INT: 30, AEF: 30, COH: 30, INF: 30, SYN: 30,
  },
};

// Points remaining in the point-buy system
const BASE_STAT = 30;
const TOTAL_POINTS = 30;
const MAX_STAT = 100;

function pointsAllocated() {
  return Object.values(form.stats).reduce((sum, v) => sum + (v - BASE_STAT), 0);
}
function pointsRemaining() {
  return TOTAL_POINTS - pointsAllocated();
}


// ---------------------------------------------------------------------------
// mount / unmount (called by switchView in main.js)
// ---------------------------------------------------------------------------

export const setupView = {

  async mount() {
    const container = document.getElementById("view-setup");
    if (!container) return;

    // Lazy-load the circular dep
    if (!_onGameStarted) {
      const mainModule = await import("../main.js");
      _onGameStarted = mainModule.onGameStarted;
    }

    // Options should already be loaded by main.js boot(), but guard anyway
    if (!state.options) {
      container.innerHTML = `<div class="flex-center" style="height:100%;color:var(--text-dim)">
        Loading game options…</div>`;
      return;
    }

    container.innerHTML = buildSetupHtml(state.options);
    attachEventListeners(container);
  },

  unmount() {
    // Nothing to clean up
  },
};


// ---------------------------------------------------------------------------
// HTML builder
// ---------------------------------------------------------------------------

function buildSetupHtml(opts) {
  return `
    <div class="setup-screen">

      <!-- ========== BANNER ========== -->
      <div class="setup-banner">
        <h1 class="setup-banner__title">CHRONICLES OF THE ETHER</h1>
        <p class="setup-banner__subtitle">Year 7019 — The galaxy remembers, and the Ether endures</p>
      </div>

      <div class="setup-steps">

        <!-- STEP 1: Commander Name -->
        ${buildStep(1, "Commander Designation", `
          <div class="form-group">
            <label class="label" for="input-name">Your name in the galactic record</label>
            <input
              class="input"
              id="input-name"
              type="text"
              placeholder="e.g. Commander Vael Orishan"
              maxlength="48"
              autocomplete="off"
            />
          </div>
        `)}

        <!-- STEP 2: Species -->
        ${buildStep(2, "Species Origin", buildCardGrid(
          opts.species, "species",
          s => ({
            name: s.name,
            category: s.category,
            desc: s.description,
            extra: s.special_traits.slice(0, 3).map(t =>
              `<span class="trait-tag">${t}</span>`).join(""),
          })
        ))}

        <!-- STEP 3: Class -->
        ${buildStep(3, "Command Path", buildCardGrid(
          opts.classes, "class",
          c => ({
            name: c.name,
            category: `Starting credits: ⬡ ${c.starting_credits.toLocaleString()}`,
            desc: c.description,
            extra: c.skills.map(sk =>
              `<span class="trait-tag">${sk}</span>`).join(""),
          })
        ))}

        <!-- STEP 4: Background -->
        ${buildStep(4, "Background History", buildCardGrid(
          opts.backgrounds, "background",
          b => ({
            name: b.name,
            category: b.credit_bonus > 0
              ? `⬡ +${b.credit_bonus.toLocaleString()} credits`
              : b.credit_bonus < 0
                ? `⬡ ${b.credit_bonus.toLocaleString()} credits`
                : "No credit bonus",
            desc: b.description,
            extra: (b.traits || []).map(t =>
              `<span class="trait-tag">${t}</span>`).join(""),
          })
        ))}

        <!-- STEP 5: Professional Specialization -->
        ${buildStep(5, "Professional Specialization", buildProfessionSection(opts.professions, opts.profession_categories))}

        <!-- STEP 6: Faction Allegiance (optional) -->
        ${buildStep(6, "Faction Allegiance — Optional", `
          <p style="font-size:var(--font-size-xs);color:var(--text-dim);margin-bottom:var(--sp-4)">
            Starting with an allegiance grants +25 reputation with that faction.
            Leave blank for a neutral start — useful for diplomatic playstyles.
          </p>
          ${buildCardGrid(
            [{ name: "(None — Neutral Start)", philosophy: "", primary_focus: "", description: "Begin with no faction ties. Suitable for traders and explorers who want to remain impartial." }, ...opts.factions],
            "faction",
            f => ({
              name: f.name,
              category: f.philosophy || "Independent",
              desc: f.description,
              extra: f.primary_focus
                ? `<span class="trait-tag">${f.primary_focus}</span>`
                : "",
            })
          )}
        `)}

        <!-- STEP 7: Stat Allocation -->
        ${buildStep(7, "Attribute Allocation", buildStatSection(opts.stats))}

      </div><!-- /.setup-steps -->

      <!-- ERROR BANNER — hidden until validation fails -->
      <div id="setup-error" class="setup-error hidden"
           style="max-width:960px;margin:0 auto var(--sp-4);padding:0 var(--sp-8)">
        <div style="padding:var(--sp-3) var(--sp-4);background:rgba(204,51,51,0.12);
                    border:1px solid var(--accent-red);color:var(--text-red);font-size:var(--font-size-sm)">
          <span id="setup-error-msg"></span>
        </div>
      </div>

      <!-- ACTION ROW -->
      <div class="setup-actions">
        <button class="btn btn--ghost" id="btn-setup-reset">Reset All</button>
        <button class="btn btn--primary" id="btn-setup-begin" style="font-size:var(--font-size-md);padding:var(--sp-3) var(--sp-8)">
          BEGIN JOURNEY
        </button>
      </div>

    </div><!-- /.setup-screen -->
  `;
}


/**
 * Wrap content in a numbered setup step container.
 * @param {number} num
 * @param {string} title
 * @param {string} bodyHtml
 */
function buildStep(num, title, bodyHtml) {
  return `
    <div class="setup-step">
      <div class="setup-step__header">
        <span class="setup-step__number">${num}</span>
        <span class="setup-step__title">${title}</span>
        <span class="setup-step__selection" id="step-${num}-selection"></span>
      </div>
      <div class="setup-step__body">
        ${bodyHtml}
      </div>
    </div>
  `;
}


/**
 * Build a responsive card grid for a list of choices.
 * @param {Array}    items      - Array of choice objects
 * @param {string}   dataKey   - data-type attribute value ("species" | "class" | etc.)
 * @param {Function} mapper    - (item) => { name, category, desc, extra }
 */
function buildCardGrid(items, dataKey, mapper) {
  if (!items || items.length === 0) return "<p style='color:var(--text-dim)'>No options available.</p>";

  const cards = items.map(item => {
    const m = mapper(item);
    return `
      <div class="choice-card" data-type="${dataKey}" data-value="${escapeAttr(item.name)}">
        <div class="choice-card__name">${escapeHtml(m.name)}</div>
        ${m.category ? `<div class="choice-card__category">${escapeHtml(m.category)}</div>` : ""}
        <div class="choice-card__desc">${escapeHtml(m.desc)}</div>
        ${m.extra ? `<div class="choice-card__traits">${m.extra}</div>` : ""}
      </div>
    `;
  }).join("");

  return `<div class="card-grid">${cards}</div>`;
}


/**
 * Build the profession selection section.
 *
 * Renders a row of category filter tabs above the card grid.
 * Only cards matching the active category are shown; clicking a tab
 * swaps the visible set without re-rendering the whole setup form.
 *
 * @param {Array}  professions  - Array of profession objects from /api/game/options
 * @param {Array}  categories   - Ordered category name list
 */
function buildProfessionSection(professions, categories) {
  if (!professions || professions.length === 0) {
    return "<p style='color:var(--text-dim)'>No professions available.</p>";
  }

  const cats = categories || [...new Set(professions.map(p => p.category))];

  // Tab buttons — one per category
  const tabs = cats.map((cat, i) => `
    <button
      class="prof-tab${i === 0 ? " prof-tab--active" : ""}"
      data-cat="${escapeAttr(cat)}"
      type="button"
    >${escapeHtml(cat)}</button>
  `).join("");

  // One hidden card grid per category
  const grids = cats.map((cat, i) => {
    const subset = professions.filter(p => p.category === cat);
    const cards  = subset.map(p => {
      // Show first two skills as trait tags; show base_benefits as tooltip-style sub-list
      const skillTags  = (p.skills || []).slice(0, 3)
        .map(s => `<span class="trait-tag">${escapeHtml(s)}</span>`).join("");
      return `
        <div class="choice-card" data-type="profession" data-value="${escapeAttr(p.name)}">
          <div class="choice-card__name">${escapeHtml(p.name)}</div>
          <div class="choice-card__category">${escapeHtml(p.category)}</div>
          <div class="choice-card__desc">${escapeHtml(p.description)}</div>
          <div class="choice-card__traits">${skillTags}</div>
        </div>
      `;
    }).join("");

    return `
      <div class="prof-grid card-grid"
           data-cat-grid="${escapeAttr(cat)}"
           style="${i === 0 ? "" : "display:none"}">
        ${cards}
      </div>
    `;
  }).join("");

  return `
    <p style="font-size:var(--font-size-xs);color:var(--text-dim);margin-bottom:var(--sp-4)">
      Your profession shaped who you were before this journey began. It grants
      skills and benefits that grow as you level up (1–10).
    </p>
    <div class="prof-tabs" id="prof-tabs">${tabs}</div>
    ${grids}
  `;
}


/**
 * Build the stat-allocation section (point-buy grid).
 * @param {{ names, base_value, point_buy_points, max_value }} statMeta
 */
function buildStatSection(statMeta) {
  const statDescriptions = {
    VIT: "Physical resilience and health capacity.",
    KIN: "Speed, agility, and physical coordination.",
    INT: "Analytical power and problem-solving.",
    AEF: "Resonance with Etheric Energy — sense and channel the Ether.",
    COH: "Stability of consciousness across biological and digital layers.",
    INF: "Social resonance — charisma, authority, emotional projection.",
    SYN: "Adaptability — integrate technologies, merge disciplines.",
  };

  const rows = statMeta.names.map(s => `
    <div style="padding:var(--sp-3);background:var(--bg-secondary);border:1px solid var(--border-color);border-radius:2px">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:var(--sp-1)">
        <span style="font-size:var(--font-size-sm);color:var(--text-bright);letter-spacing:0.06em;text-transform:uppercase">
          ${s.name}
        </span>
        <div class="stat-row-input">
          <button class="stat-row-input__btn" data-stat="${s.key}" data-delta="-1">−</button>
          <span class="stat-row-input__value" id="stat-val-${s.key}">${BASE_STAT}</span>
          <button class="stat-row-input__btn" data-stat="${s.key}" data-delta="1">+</button>
        </div>
      </div>
      <div style="font-size:var(--font-size-xs);color:var(--text-dim)">${statDescriptions[s.key] || ""}</div>
    </div>
  `).join("");

  return `
    <div class="points-remaining" id="points-display">
      <span style="color:var(--text-dim);letter-spacing:0.06em;text-transform:uppercase;font-size:var(--font-size-xs)">
        Points remaining
      </span>
      <span class="points-remaining__count" id="points-count">${TOTAL_POINTS}</span>
    </div>
    <div class="stat-grid">${rows}</div>
  `;
}


// ---------------------------------------------------------------------------
// Event listener wiring
// ---------------------------------------------------------------------------

function attachEventListeners(container) {
  // Card selection
  container.addEventListener("click", e => {
    const card = e.target.closest(".choice-card");
    if (!card) return;

    const type  = card.dataset.type;
    const value = card.dataset.value;

    // Deselect all cards of this type, then select the clicked one
    container.querySelectorAll(`.choice-card[data-type="${type}"]`)
      .forEach(c => c.classList.remove("choice-card--selected"));
    card.classList.add("choice-card--selected");

    // Map data-type → form field
    const stepMap = {
      species:    [1, "species"],
      class:      [2, "character_class"],
      background: [3, "background"],
      faction:    [4, "faction"],
    };

    // Map the step numbers in the actual HTML order (species=step2, class=step3…)
    // We use the data-type directly on form
    if (type === "species")     { form.species           = value; updateStepLabel(2, value); }
    if (type === "class")       { form.character_class   = value; updateStepLabel(3, value); }
    if (type === "background")  { form.background        = value; updateStepLabel(4, value); }
    if (type === "profession")  { form.profession        = value; updateStepLabel(5, value); }
    if (type === "faction")    {
      form.faction = value === "(None — Neutral Start)" ? "" : value;
      updateStepLabel(6, value === "(None — Neutral Start)" ? "None" : value);
    }
  });

  // Name input
  const nameInput = container.querySelector("#input-name");
  if (nameInput) {
    nameInput.addEventListener("input", e => {
      form.name = e.target.value.trim();
    });
  }

  // Stat +/− buttons
  container.addEventListener("click", e => {
    const btn = e.target.closest(".stat-row-input__btn");
    if (!btn) return;

    const stat  = btn.dataset.stat;
    const delta = parseInt(btn.dataset.delta, 10);
    adjustStat(stat, delta, container);
  });

  // Reset button
  const resetBtn = container.querySelector("#btn-setup-reset");
  if (resetBtn) {
    resetBtn.addEventListener("click", () => resetForm(container));
  }

  // Profession category tab switching
  const profTabsEl = container.querySelector("#prof-tabs");
  if (profTabsEl) {
    profTabsEl.addEventListener("click", e => {
      const tab = e.target.closest(".prof-tab");
      if (!tab) return;
      const cat = tab.dataset.cat;

      // Toggle active tab styling
      profTabsEl.querySelectorAll(".prof-tab")
        .forEach(t => t.classList.toggle("prof-tab--active", t === tab));

      // Show only the grid for the selected category
      container.querySelectorAll("[data-cat-grid]").forEach(grid => {
        grid.style.display = grid.dataset.catGrid === cat ? "" : "none";
      });
    });
  }

  // Begin button
  const beginBtn = container.querySelector("#btn-setup-begin");
  if (beginBtn) {
    beginBtn.addEventListener("click", () => handleSubmit(container));
  }
}


/**
 * Show the current selection for a step in its header.
 * @param {number} stepNum
 * @param {string} value
 */
function updateStepLabel(stepNum, value) {
  const el = document.getElementById(`step-${stepNum}-selection`);
  if (el) el.textContent = value ? `[ ${value} ]` : "";
}


/**
 * Adjust a single stat value, respecting point-buy limits.
 */
function adjustStat(statKey, delta, container) {
  const current = form.stats[statKey];
  const proposed = current + delta;

  // Floor is base value; ceiling is MAX_STAT
  if (proposed < BASE_STAT) return;
  if (proposed > MAX_STAT)  return;

  // Check we haven't spent all points
  if (delta > 0 && pointsRemaining() <= 0) return;

  form.stats[statKey] = proposed;

  // Update the displayed value
  const valEl = container.querySelector(`#stat-val-${statKey}`);
  if (valEl) valEl.textContent = proposed;

  // Update points remaining counter
  refreshPointsDisplay(container);
}


/**
 * Refresh the "Points remaining" display.
 */
function refreshPointsDisplay(container) {
  const remaining = pointsRemaining();
  const countEl   = container.querySelector("#points-count");
  const displayEl = container.querySelector("#points-display");

  if (countEl)   countEl.textContent = remaining;
  if (displayEl) {
    displayEl.classList.toggle("points-remaining--warning", remaining <= 5 && remaining > 0);
  }
}


/**
 * Reset all form selections back to defaults.
 */
function resetForm(container) {
  form.name            = "";
  form.character_class = "";
  form.background      = "";
  form.species         = "";
  form.faction         = "";
  Object.keys(form.stats).forEach(k => { form.stats[k] = BASE_STAT; });

  // Clear card selections
  container.querySelectorAll(".choice-card--selected")
    .forEach(c => c.classList.remove("choice-card--selected"));

  // Clear name input
  const nameInput = container.querySelector("#input-name");
  if (nameInput) nameInput.value = "";

  // Reset stat displays
  Object.keys(form.stats).forEach(k => {
    const valEl = container.querySelector(`#stat-val-${k}`);
    if (valEl) valEl.textContent = BASE_STAT;
  });

  // Reset step labels (steps 2–6 have selection labels; step 7 is stats)
  [2, 3, 4, 5, 6].forEach(n => updateStepLabel(n, ""));

  refreshPointsDisplay(container);
  hideError(container);
}


// ---------------------------------------------------------------------------
// Form submission
// ---------------------------------------------------------------------------

async function handleSubmit(container) {
  hideError(container);

  // ---- Validation ----
  if (!form.name)            return showError(container, "Please enter your commander's name.");
  if (!form.species)         return showError(container, "Please select a species.");
  if (!form.character_class) return showError(container, "Please select a command path (class).");
  if (!form.background)      return showError(container, "Please select a background history.");

  // Stat validation — can't have over-spent
  if (pointsAllocated() > TOTAL_POINTS) {
    return showError(container, `Too many stat points allocated. Remove ${pointsAllocated() - TOTAL_POINTS} points.`);
  }

  // ---- Submit ----
  const btn = container.querySelector("#btn-setup-begin");
  if (btn) {
    btn.disabled = true;
    btn.textContent = "INITIALISING...";
  }

  try {
    const result = await newGame({
      name:             form.name,
      character_class:  form.character_class,
      background:       form.background,
      species:          form.species,
      faction:          form.faction,
      profession:       form.profession,
      stats:            { ...form.stats },
      research_paths:   [],
    });

    // Hand off to main.js to show HUD and switch to galaxy view
    if (_onGameStarted) {
      _onGameStarted(result.state);
    }

  } catch (err) {
    showError(container, `Failed to start game: ${err.message}`);
    if (btn) {
      btn.disabled = false;
      btn.textContent = "BEGIN JOURNEY";
    }
  }
}


function showError(container, message) {
  const errDiv = container.querySelector("#setup-error");
  const errMsg = container.querySelector("#setup-error-msg");
  if (errDiv) errDiv.classList.remove("hidden");
  if (errMsg) errMsg.textContent = message;
  // Scroll the error into view
  if (errDiv) errDiv.scrollIntoView({ behavior: "smooth", block: "center" });
}

function hideError(container) {
  const errDiv = container.querySelector("#setup-error");
  if (errDiv) errDiv.classList.add("hidden");
}


// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function escapeAttr(str) {
  return String(str || "").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}
