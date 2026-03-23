/**
 * views/setup.js — Character creation screen.
 *
 * Tabbed layout: category tabs on the left, content panel on the right.
 * On submit it calls /api/game/new and, on success, hands off to main.js.
 */

import { state }                    from "../state.js";
import { newGame }                  from "../api.js";
import { notify }                   from "../ui/notifications.js";
import { showModal, closeModal }    from "../ui/modal.js";
// onGameStarted is imported lazily to avoid circular dep with main.js
let _onGameStarted = null;

// ---------------------------------------------------------------------------
// Setup form state — populated as the player makes selections
// ---------------------------------------------------------------------------
const form = {
  name:             "",
  background:       "",
  species:          "",
  faction:          "",
  profession:       "",
  stats: {
    VIT: 30, KIN: 30, INT: 30, AEF: 30, COH: 30, INF: 30, SYN: 30,
  },
};

const BASE_STAT    = 30;
const TOTAL_POINTS = 30;
const MAX_STAT     = 100;

function pointsAllocated() {
  return Object.values(form.stats).reduce((sum, v) => sum + (v - BASE_STAT), 0);
}
function pointsRemaining() {
  return TOTAL_POINTS - pointsAllocated();
}


// ---------------------------------------------------------------------------
// Tab definitions
// ---------------------------------------------------------------------------

const SETUP_TABS = [
  { id: "designation",    label: "Commander Designation",       stepNum: 1 },
  { id: "species",        label: "Species Origin",              stepNum: 2 },
  { id: "background",     label: "Early Life",                  stepNum: 3 },
  { id: "specialization", label: "Professional Specialization", stepNum: 4 },
  { id: "faction",        label: "Faction Allegiance",          stepNum: 5, optional: true },
  { id: "attributes",     label: "Attribute Allocation",        stepNum: 6 },
  { id: "equipment",      label: "Equipment",                   reserved: true },
  { id: "cybernetics",    label: "Cybernetics",                 reserved: true },
];


// ---------------------------------------------------------------------------
// mount / unmount
// ---------------------------------------------------------------------------

export const setupView = {

  async mount() {
    const container = document.getElementById("view-setup");
    if (!container) return;

    if (!_onGameStarted) {
      const mainModule = await import("../main.js");
      _onGameStarted = mainModule.onGameStarted;
    }

    if (!state.options) {
      container.innerHTML = `<div class="flex-center" style="height:100%;color:var(--text-dim)">
        Loading game options…</div>`;
      return;
    }

    container.innerHTML = buildSetupHtml(state.options);
    attachEventListeners(container);
  },

  unmount() {},
};


// ---------------------------------------------------------------------------
// HTML builder
// ---------------------------------------------------------------------------

function buildSetupHtml(opts) {
  // ── Left nav ──────────────────────────────────────────────────────────────
  const navHtml = SETUP_TABS.map((t, i) => {
    const cls = ["setup-tab"];
    if (i === 0)    cls.push("setup-tab--active");
    if (t.reserved) cls.push("setup-tab--reserved");
    const selSpan = t.stepNum
      ? `<span class="setup-tab__sel" id="step-${t.stepNum}-selection"></span>`
      : "";
    const optionalTag = t.optional
      ? `<span class="setup-tab__optional">optional</span>`
      : "";
    return `
      <div class="${cls.join(" ")}" data-tab="${t.id}">
        <span class="setup-tab__label">${t.label}</span>
        ${optionalTag}${selSpan}
      </div>
    `;
  }).join("");

  // ── Right panels ──────────────────────────────────────────────────────────
  const panelDefs = [
    {
      id: "designation",
      html: `
        <div class="setup-panel__title">COMMANDER DESIGNATION</div>
        <p class="setup-panel__desc">Your name in the galactic record.</p>
        <div class="form-group">
          <label class="label" for="input-name">Commander name</label>
          <input
            class="input"
            id="input-name"
            type="text"
            placeholder="e.g. Commander Vael Orishan"
            maxlength="48"
            autocomplete="off"
          />
        </div>
      `,
    },
    {
      id: "species",
      html: `
        <div class="setup-panel__title">SPECIES ORIGIN</div>
        <p class="setup-panel__desc">Choose your species. Each brings distinct traits and cultural background.</p>
        ${buildCardGrid(opts.species, "species", s => ({
          name:     s.name,
          category: s.category,
          desc:     s.description,
          extra:    s.special_traits.slice(0, 3).map(t =>
            `<span class="trait-tag">${t}</span>`).join(""),
        }))}
      `,
    },
    {
      id: "background",
      html: `
        <div class="setup-panel__title">EARLY LIFE</div>
        <p class="setup-panel__desc">The developmental pathway that shaped your mind before you took command. Each pathway reflects a distinct relationship to knowledge, systems, and time — and grants stat bonuses, traits, and a unique talent.</p>
        ${buildCardGrid(opts.backgrounds, "background", b => {
          // Build stat bonus summary string (e.g. "SYN +1  COH +1")
          const statLine = Object.entries(b.stat_bonuses || {})
            .map(([k, v]) => `${k} +${v}`).join("  ·  ");
          // Category shows credits if non-zero, otherwise the stat line
          const category = b.credit_bonus !== 0
            ? `⬡ ${b.credit_bonus > 0 ? "+" : ""}${b.credit_bonus.toLocaleString()} credits${statLine ? "  ·  " + statLine : ""}`
            : statLine || "";
          const traitTags = (b.traits || []).map(t =>
            `<span class="trait-tag">${t}</span>`).join("");
          const talentLine = b.talent
            ? `<div style="margin-top:var(--sp-2);font-size:var(--font-size-xs);color:var(--text-dim);font-style:italic">${escapeHtml(b.talent)}</div>`
            : "";
          return { name: b.name, category, desc: b.description, extra: traitTags + talentLine };
        })}
      `,
    },
    {
      id: "specialization",
      html: `
        <div class="setup-panel__title">PROFESSIONAL SPECIALIZATION</div>
        ${buildProfessionSection(opts.professions, opts.profession_categories)}
      `,
    },
    {
      id: "faction",
      html: `
        <div class="setup-panel__title">FACTION ALLEGIANCE <span style="color:var(--text-dim);font-size:var(--font-size-xs);letter-spacing:0.05em">— OPTIONAL</span></div>
        <p class="setup-panel__desc">
          Starting with an allegiance grants +25 reputation with that faction.
          Leave blank for a neutral start — useful for diplomatic playstyles.
        </p>
        ${buildCardGrid(
          [{ name: "(None — Neutral Start)", philosophy: "", primary_focus: "", description: "Begin with no faction ties. Suitable for traders and explorers who want to remain impartial." }, ...opts.factions],
          "faction",
          f => ({
            name:     f.name,
            category: f.philosophy || "Independent",
            desc:     f.description,
            extra:    f.primary_focus
              ? `<span class="trait-tag">${f.primary_focus}</span>`
              : "",
          })
        )}
      `,
    },
    {
      id: "attributes",
      html: `
        <div class="setup-panel__title">ATTRIBUTE ALLOCATION</div>
        ${buildStatSection(opts.stats)}
      `,
    },
    {
      id: "equipment",
      html: `
        <div class="setup-panel__title">EQUIPMENT</div>
        <p class="setup-panel__desc" style="color:var(--text-dim)">Equipment slots — reserved for a future update.</p>
      `,
    },
    {
      id: "cybernetics",
      html: `
        <div class="setup-panel__title">CYBERNETICS</div>
        <p class="setup-panel__desc" style="color:var(--text-dim)">Cybernetic augmentation — reserved for a future update.</p>
      `,
    },
  ];

  const panelsHtml = panelDefs.map((p, i) =>
    `<div class="setup-panel${i === 0 ? " setup-panel--active" : ""}" data-panel="${p.id}">${p.html}</div>`
  ).join("");

  return `
    <div class="setup-screen">

      <div class="setup-banner">
        <h1 class="setup-banner__title">CHRONICLES OF THE ETHER</h1>
        <p class="setup-banner__subtitle">Year 7019 — The galaxy remembers, and the Ether endures</p>
      </div>

      <div class="setup-main">
        <nav class="setup-nav">${navHtml}</nav>
        <div class="setup-content">${panelsHtml}</div>
      </div>

      <!-- ERROR BANNER — hidden until validation fails -->
      <div id="setup-error" class="setup-error hidden">
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

    </div>
  `;
}


/**
 * Build a responsive card grid for a list of choices.
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
 * Build the profession selection section with category filter tabs.
 */
function buildProfessionSection(professions, categories) {
  if (!professions || professions.length === 0) {
    return "<p style='color:var(--text-dim)'>No professions available.</p>";
  }

  const cats = categories || [...new Set(professions.map(p => p.category))];

  const tabs = cats.map((cat, i) => `
    <button
      class="prof-tab${i === 0 ? " prof-tab--active" : ""}"
      data-cat="${escapeAttr(cat)}"
      type="button"
    >${escapeHtml(cat)}</button>
  `).join("");

  const grids = cats.map((cat, i) => {
    const subset = professions.filter(p => p.category === cat);
    const cards  = subset.map(p => {
      const skillTags = (p.skills || []).slice(0, 3)
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
  // ── Tab switching ──────────────────────────────────────────────────────────
  const setupNav = container.querySelector(".setup-nav");
  if (setupNav) {
    setupNav.addEventListener("click", e => {
      const tab = e.target.closest(".setup-tab");
      if (!tab || tab.classList.contains("setup-tab--reserved")) return;
      const id = tab.dataset.tab;

      setupNav.querySelectorAll(".setup-tab").forEach(t => t.classList.remove("setup-tab--active"));
      tab.classList.add("setup-tab--active");

      container.querySelectorAll(".setup-panel").forEach(p => p.classList.remove("setup-panel--active"));
      const panel = container.querySelector(`[data-panel="${id}"]`);
      if (panel) panel.classList.add("setup-panel--active");
    });
  }

  // ── Card selection ─────────────────────────────────────────────────────────
  container.addEventListener("click", e => {
    const card = e.target.closest(".choice-card");
    if (!card) return;

    const type  = card.dataset.type;
    const value = card.dataset.value;

    container.querySelectorAll(`.choice-card[data-type="${type}"]`)
      .forEach(c => c.classList.remove("choice-card--selected"));
    card.classList.add("choice-card--selected");

    if (type === "species")     { form.species           = value; updateStepLabel(2, value); clearPanelError(container, "species"); }
    if (type === "background")  { form.background        = value; updateStepLabel(3, value); clearPanelError(container, "background"); }
    if (type === "profession")  { form.profession        = value; updateStepLabel(4, value); }
    if (type === "faction") {
      form.faction = value === "(None — Neutral Start)" ? "" : value;
      updateStepLabel(5, value === "(None — Neutral Start)" ? "None" : value);
    }
  });

  // ── Name input ─────────────────────────────────────────────────────────────
  const nameInput = container.querySelector("#input-name");
  if (nameInput) {
    nameInput.addEventListener("input", e => {
      form.name = e.target.value.trim();
      updateStepLabel(1, form.name);
      if (form.name) {
        nameInput.classList.remove("input--error");
        clearPanelError(container, "designation");
      }
    });
  }

  // ── Stat +/− buttons ───────────────────────────────────────────────────────
  container.addEventListener("click", e => {
    const btn = e.target.closest(".stat-row-input__btn");
    if (!btn) return;
    adjustStat(btn.dataset.stat, parseInt(btn.dataset.delta, 10), container);
  });

  // ── Reset ──────────────────────────────────────────────────────────────────
  const resetBtn = container.querySelector("#btn-setup-reset");
  if (resetBtn) {
    resetBtn.addEventListener("click", () => resetForm(container));
  }

  // ── Profession category tabs ───────────────────────────────────────────────
  const profTabsEl = container.querySelector("#prof-tabs");
  if (profTabsEl) {
    profTabsEl.addEventListener("click", e => {
      const tab = e.target.closest(".prof-tab");
      if (!tab) return;
      const cat = tab.dataset.cat;
      profTabsEl.querySelectorAll(".prof-tab")
        .forEach(t => t.classList.toggle("prof-tab--active", t === tab));
      container.querySelectorAll("[data-cat-grid]").forEach(grid => {
        grid.style.display = grid.dataset.catGrid === cat ? "" : "none";
      });
    });
  }

  // ── Begin ──────────────────────────────────────────────────────────────────
  const beginBtn = container.querySelector("#btn-setup-begin");
  if (beginBtn) {
    beginBtn.addEventListener("click", () => handleSubmit(container));
  }
}


function updateStepLabel(stepNum, value) {
  const el = document.getElementById(`step-${stepNum}-selection`);
  if (el) el.textContent = value ? `[ ${value} ]` : "";
}


function adjustStat(statKey, delta, container) {
  const current  = form.stats[statKey];
  const proposed = current + delta;
  if (proposed < BASE_STAT) return;
  if (proposed > MAX_STAT)  return;
  if (delta > 0 && pointsRemaining() <= 0) return;
  form.stats[statKey] = proposed;
  const valEl = container.querySelector(`#stat-val-${statKey}`);
  if (valEl) valEl.textContent = proposed;
  refreshPointsDisplay(container);
}


function refreshPointsDisplay(container) {
  const remaining = pointsRemaining();
  const countEl   = container.querySelector("#points-count");
  const displayEl = container.querySelector("#points-display");
  if (countEl)   countEl.textContent = remaining;
  if (displayEl) {
    displayEl.classList.toggle("points-remaining--warning", remaining <= 5 && remaining > 0);
  }
}


function resetForm(container) {
  form.name            = "";
  form.background      = "";
  form.species         = "";
  form.faction         = "";
  form.profession      = "";
  Object.keys(form.stats).forEach(k => { form.stats[k] = BASE_STAT; });

  container.querySelectorAll(".choice-card--selected")
    .forEach(c => c.classList.remove("choice-card--selected"));

  const nameInput = container.querySelector("#input-name");
  if (nameInput) nameInput.value = "";

  Object.keys(form.stats).forEach(k => {
    const valEl = container.querySelector(`#stat-val-${k}`);
    if (valEl) valEl.textContent = BASE_STAT;
  });

  [1, 2, 3, 4, 5, 6].forEach(n => updateStepLabel(n, ""));
  refreshPointsDisplay(container);
  hideError(container);
}


// ---------------------------------------------------------------------------
// Inline validation helpers
// ---------------------------------------------------------------------------

function switchToTab(container, tabId) {
  const nav = container.querySelector(".setup-nav");
  if (!nav) return;
  nav.querySelectorAll(".setup-tab").forEach(t => t.classList.remove("setup-tab--active"));
  const tab = nav.querySelector(`[data-tab="${tabId}"]`);
  if (tab) tab.classList.add("setup-tab--active");

  container.querySelectorAll(".setup-panel").forEach(p => p.classList.remove("setup-panel--active"));
  const panel = container.querySelector(`[data-panel="${tabId}"]`);
  if (panel) panel.classList.add("setup-panel--active");
}

function flashPanelError(container, tabId, message) {
  const panel = container.querySelector(`[data-panel="${tabId}"]`);
  if (!panel) return;

  // Remove any existing inline error in this panel
  const existing = panel.querySelector(".setup-panel__inline-err");
  if (existing) existing.remove();

  // For the name field: also add a red border to the input
  if (tabId === "designation") {
    const input = panel.querySelector("#input-name");
    if (input) input.classList.add("input--error");
  }

  const errEl = document.createElement("div");
  errEl.className = "setup-panel__inline-err";
  errEl.textContent = message;

  // Insert after the title/desc block, before the interactive content
  const desc = panel.querySelector(".setup-panel__desc");
  const anchor = desc || panel.querySelector(".setup-panel__title");
  if (anchor && anchor.nextSibling) {
    panel.insertBefore(errEl, anchor.nextSibling);
  } else {
    panel.appendChild(errEl);
  }

  // Scroll error into view
  errEl.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function clearPanelError(container, tabId) {
  const panel = container.querySelector(`[data-panel="${tabId}"]`);
  if (!panel) return;
  const err = panel.querySelector(".setup-panel__inline-err");
  if (err) err.remove();
}


// ---------------------------------------------------------------------------
// Form submission
// ---------------------------------------------------------------------------

async function handleSubmit(container) {
  hideError(container);

  // Check required fields in order — navigate to the first incomplete one
  const required = [
    { test: !form.name,       tab: "designation", msg: "Commander name is required." },
    { test: !form.species,    tab: "species",     msg: "A species selection is required." },
    { test: !form.background, tab: "background",  msg: "A background selection is required." },
  ];

  for (const r of required) {
    if (r.test) {
      switchToTab(container, r.tab);
      flashPanelError(container, r.tab, r.msg);
      return;
    }
  }

  if (pointsAllocated() > TOTAL_POINTS) {
    switchToTab(container, "attributes");
    flashPanelError(container, "attributes", `Too many stat points allocated. Remove ${pointsAllocated() - TOTAL_POINTS} point(s).`);
    return;
  }

  const btn = container.querySelector("#btn-setup-begin");
  if (btn) {
    btn.disabled    = true;
    btn.textContent = "INITIALISING...";
  }

  try {
    const result = await newGame({
      name:             form.name,
      background:       form.background,
      species:          form.species,
      faction:          form.faction,
      profession:       form.profession,
      stats:            { ...form.stats },
      research_paths:   [],
    });

    // Store the backstory on global state so the character sheet can display it
    // without a separate API call.
    state.characterBackstory = result.backstory || "";

    // Show the Commander Dossier modal before routing to the galaxy.
    // The player clicks "BEGIN JOURNEY" to dismiss it and start the game.
    if (result.backstory && _onGameStarted) {
      showModal(
        "COMMANDER DOSSIER",
        `<div class="backstory-modal">
           <p class="backstory-modal__lede">${escapeHtml(result.backstory)}</p>
         </div>`,
        [
          {
            label:     "BEGIN JOURNEY",
            className: "btn--primary",
            onClick:   () => {
              closeModal();
              _onGameStarted(result.state);
            },
          },
        ]
      );
    } else if (_onGameStarted) {
      _onGameStarted(result.state);
    }

  } catch (err) {
    showError(container, `Failed to start game: ${err.message}`);
    if (btn) {
      btn.disabled    = false;
      btn.textContent = "BEGIN JOURNEY";
    }
  }
}


function showError(container, message) {
  const errDiv = container.querySelector("#setup-error");
  const errMsg = container.querySelector("#setup-error-msg");
  if (errDiv) errDiv.classList.remove("hidden");
  if (errMsg) errMsg.textContent = message;
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
