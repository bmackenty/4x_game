/**
 * views/ship.js — Ship stats and component management view.
 *
 * Shows:
 *   • Top bar: ship name, class, and key derived stats (fuel, jump range, cargo).
 *   • Category filter bar: click a category to show only those attributes.
 *   • Attribute list: each attribute rendered as a labeled progress bar (0–100).
 *   • Components panel: installed components and available upgrades per slot.
 *
 * All data comes from /api/ship/attributes and /api/ship/components.
 * No game logic lives here — display only.
 */

import { getShipAttributes, getShipComponents } from "../api.js";
import { notify } from "../ui/notifications.js";


// ---------------------------------------------------------------------------
// Module state
// ---------------------------------------------------------------------------

let _attrs   = null;   // Response from /api/ship/attributes
let _comps   = null;   // Response from /api/ship/components
let _catFilter = "all"; // Active category id, or "all"
let _tab = "stats";    // "stats" | "components" | "cargo"


// ---------------------------------------------------------------------------
// Public view object
// ---------------------------------------------------------------------------

export const shipView = { mount, unmount };


async function mount() {
  const container = document.getElementById("ship-container");
  if (!container) return;

  container.innerHTML = '<p class="ship__loading">Loading ship data…</p>';

  try {
    [_attrs, _comps] = await Promise.all([getShipAttributes(), getShipComponents()]);
  } catch (err) {
    container.innerHTML = `<p class="ship__error">Could not load ship data: ${err.message}</p>`;
    return;
  }

  _catFilter = "all";
  _tab = "stats";
  render(container);
}

function unmount() {
  _attrs = null;
  _comps = null;
}


// ---------------------------------------------------------------------------
// Rendering
// ---------------------------------------------------------------------------

function render(container) {
  container.innerHTML = buildHtml();
  wireEvents(container);
}

function buildHtml() {
  if (!_attrs) return "";

  const {
    ship_name, ship_class, fuel, max_fuel, jump_range, scan_range, fuel_efficiency, max_cargo,
    hull_damage, hull_integrity_base, hull_integrity_effective,
  } = _attrs;

  // Display efficiency as a signed percentage relative to baseline (1.0 = ±0%)
  const effPct     = fuel_efficiency != null ? Math.round((1.0 - fuel_efficiency) * 100) : null;
  const effLabel   = effPct == null  ? "—"
                   : effPct  >  0    ? `−${effPct}%`   // better than baseline: cheaper jumps
                   : effPct  <  0    ? `+${-effPct}%`  // worse than baseline: costlier jumps
                   :                   "±0%";           // exactly at baseline
  const fuelPct = max_fuel > 0 ? Math.round((fuel / max_fuel) * 100) : 0;

  // Hull integrity bar: effective / base, colour shifts from green → amber → red as damage grows
  const hullBase  = hull_integrity_base      ?? 30;
  const hullEff   = hull_integrity_effective ?? hullBase;
  const hullPct   = hullBase > 0 ? Math.round((hullEff / hullBase) * 100) : 100;
  const hullLabel = `${hullEff}/${hullBase}`;
  // bar colour modifier: high (green) → warn (amber) → crit (red)
  const hullMod   = hullPct >= 80 ? "" : hullPct >= 50 ? " ship-stat__bar--warn" : " ship-stat__bar--crit";

  return `
    <div class="ship-view">

      <!-- ── Header ─────────────────────────────────────── -->
      <header class="ship-view__header">
        <div class="ship-view__identity">
          <h2 class="ship-view__name">${ship_name}</h2>
          <span class="ship-view__class">${ship_class}</span>
        </div>
        <div class="ship-view__quick-stats">
          <div class="ship-stat">
            <span class="ship-stat__label">FUEL</span>
            <div class="ship-stat__bar-wrap">
              <div class="ship-stat__bar" style="width:${fuelPct}%"></div>
            </div>
            <span class="ship-stat__value">${fuel}/${max_fuel}</span>
          </div>
          <div class="ship-stat" title="Hull integrity: current / base. Degrades from jump stress and hazards; auto-repairs each turn or fully at any station.">
            <span class="ship-stat__label">HULL</span>
            <div class="ship-stat__bar-wrap">
              <div class="ship-stat__bar${hullMod}" style="width:${hullPct}%"></div>
            </div>
            <span class="ship-stat__value">${hullLabel}</span>
          </div>
          <div class="ship-stat">
            <span class="ship-stat__label">JUMP</span>
            <span class="ship-stat__value ship-stat__value--solo">${jump_range} u</span>
          </div>
          <div class="ship-stat">
            <span class="ship-stat__label">SENSORS</span>
            <span class="ship-stat__value ship-stat__value--solo">${scan_range ?? "—"} u</span>
          </div>
          <div class="ship-stat" title="Fuel cost per jump relative to baseline. Negative = cheaper.">
            <span class="ship-stat__label">EFFICIENCY</span>
            <span class="ship-stat__value ship-stat__value--solo">${effLabel}</span>
          </div>
          <div class="ship-stat">
            <span class="ship-stat__label">CARGO</span>
            <span class="ship-stat__value ship-stat__value--solo">${max_cargo} t</span>
          </div>
        </div>
      </header>

      <!-- ── Tab switcher ────────────────────────────────── -->
      <div class="ship-view__tabs">
        <button class="ship-tab-btn ${_tab === "stats" ? "ship-tab-btn--active" : ""}"
                data-tab="stats">ATTRIBUTES</button>
        <button class="ship-tab-btn ${_tab === "components" ? "ship-tab-btn--active" : ""}"
                data-tab="components">COMPONENTS</button>
        <button class="ship-tab-btn ${_tab === "cargo" ? "ship-tab-btn--active" : ""}"
                data-tab="cargo">CARGO</button>
      </div>

      <!-- ── Tab content ─────────────────────────────────── -->
      <div class="ship-view__body">
        ${_tab === "stats" ? buildStatsTab() : _tab === "components" ? buildComponentsTab() : buildCargoTab()}
      </div>

    </div>
  `;
}

// ── Stats tab ──────────────────────────────────────────────────────────────

function buildStatsTab() {
  const categories = _attrs.categories || [];

  const filterBtns = [
    `<button class="ship-cat-btn ${_catFilter === "all" ? "ship-cat-btn--active" : ""}"
             data-cat="all">All</button>`,
    ...categories.map(cat =>
      `<button class="ship-cat-btn ${_catFilter === cat.id ? "ship-cat-btn--active" : ""}"
               data-cat="${cat.id}">${cat.name}</button>`
    ),
  ].join("");

  const visibleCats = _catFilter === "all"
    ? categories
    : categories.filter(c => c.id === _catFilter);

  const catSections = visibleCats.map(cat => `
    <section class="ship-cat-section">
      <h3 class="ship-cat-section__title">${cat.name}</h3>
      <div class="ship-attr-list">
        ${cat.attributes.map(attr => buildAttrRow(attr)).join("")}
      </div>
    </section>
  `).join("");

  return `
    <div class="ship-cat-filter">${filterBtns}</div>
    <div class="ship-attr-body">${catSections}</div>
  `;
}

function buildAttrRow(attr) {
  const pct = Math.min(100, Math.max(0, attr.value));
  const colorClass = pct >= 60 ? "attr-bar--high"
                   : pct >= 35 ? "attr-bar--mid"
                   : "attr-bar--low";
  return `
    <div class="attr-row" title="${attr.description}">
      <span class="attr-row__name">${attr.name}</span>
      <div class="attr-row__bar-wrap">
        <div class="attr-row__bar ${colorClass}" style="width:${pct}%"></div>
      </div>
      <span class="attr-row__value">${attr.value}</span>
    </div>
  `;
}

// ── Components tab ─────────────────────────────────────────────────────────

function buildComponentsTab() {
  if (!_comps) return "<p>No component data.</p>";

  const installed = _comps.installed || {};

  return `
    <div class="ship-components">
      <section class="ship-comp-section">
        <h3 class="ship-comp-section__title">SHIP SCHEMATIC</h3>
        <div class="ship-schematic-canvas-wrap">${buildShipSchematic(installed)}</div>
      </section>
      <section class="ship-comp-section">
        <h3 class="ship-comp-section__title">INSTALLED COMPONENTS</h3>
        ${buildInstalledSection(installed)}
      </section>
      <p class="ship-comp-note">Component upgrades available at a <strong>Shipyard</strong>.</p>
    </div>
  `;
}


// ── Cargo tab ───────────────────────────────────────────────────────────────

const CARGO_ICONS = {
  minerals:        "⬡",
  food:            "❋",
  water:           "◉",
  alloys:          "◈",
  energy_cells:    "⚡",
  dark_matter:     "◆",
  crystals:        "✦",
  data_cores:      "◎",
  artifacts:       "◎",
  organics:        "❋",
  hydrogen:        "◉",
  exotic_particles:"✦",
};

function buildCargoTab() {
  const cargo   = _attrs.cargo   || {};
  const credits = _attrs.credits ?? 0;
  const maxCargo = _attrs.max_cargo ?? 0;

  const entries = Object.entries(cargo).filter(([, v]) => v > 0);
  const used    = entries.reduce((sum, [, v]) => sum + v, 0);
  const usedPct = maxCargo > 0 ? Math.min(100, Math.round((used / maxCargo) * 100)) : 0;
  const barMod  = usedPct >= 90 ? " cargo-bar--crit" : usedPct >= 70 ? " cargo-bar--warn" : "";

  const emptyMsg = entries.length === 0
    ? `<div class="cargo-empty">Cargo hold is empty.</div>`
    : "";

  const rows = entries.map(([key, qty]) => {
    const label = key.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
    const icon  = CARGO_ICONS[key] || "·";
    return `
      <div class="cargo-row">
        <span class="cargo-row__icon">${icon}</span>
        <span class="cargo-row__name">${label}</span>
        <span class="cargo-row__qty">${qty}</span>
      </div>
    `;
  }).join("");

  return `
    <div class="ship-cargo">
      <div class="cargo-header">
        <div class="cargo-header__label">HOLD CAPACITY</div>
        <div class="cargo-header__bar-wrap">
          <div class="cargo-header__bar${barMod}" style="width:${usedPct}%"></div>
        </div>
        <div class="cargo-header__value">${used} / ${maxCargo} t</div>
      </div>
      <div class="cargo-credits">
        <span class="cargo-credits__icon">◈</span>
        <span class="cargo-credits__label">Credits</span>
        <span class="cargo-credits__value">${credits.toLocaleString()}</span>
      </div>
      <div class="cargo-list">
        ${emptyMsg}
        ${rows}
      </div>
    </div>
  `;
}


// ── 8-bit pixel art ship schematic ──────────────────────────────────────────

/**
 * Pixel-art colour palette.
 * Each character maps to an RGBA/hex colour (null = transparent/skip).
 */
const _PIX_PAL = {
  '.': null,        // transparent — draw nothing (shows canvas bg)
  's': '#08111c',   // deep shadow
  'd': '#17354f',   // dark hull
  'm': '#1f4d6e',   // mid hull
  'b': '#2f6a90',   // body
  'h': '#4a90b8',   // hull highlight
  'l': '#6db0d4',   // bright hull edge
  'T': '#00d4aa',   // teal core / cockpit
  't': '#007a62',   // teal shadow
  'E': '#ff8c00',   // engine warm glow
  'e': '#ff4400',   // engine hot core
  'W': '#c8eeff',   // bright specular
  'R': '#cc3333',   // red weapon port
};

/**
 * Three ship sprites — 20 columns × 18 rows each (top-down, nose points up).
 *
 * SCOUT  : narrow dart — for scouts/explorers/ghosts/drifters
 * HEAVY  : wide body   — for freighters/transports/traders
 * COMBAT : flanged hull — for corsairs/interceptors/pursuit/runners
 *
 * Each row MUST be exactly 20 characters.  Rows shorter than 20 are
 * right-padded with '.' at render time.
 */
const _SPRITES = {

  // ── SCOUT ──────────────────────────────────────────────────────────────────
  // Sleek dart with teal cockpit bubble and twin engines
  scout: [
    '........lll.........',   // nose tip
    '.......lhThl........',   // cockpit front
    '......lhTWThl.......',   // cockpit (W = bright specular)
    '.....lhTTWTThl......',
    '....mhhTTTTThhm.....',
    '...mmbbhTTTThbbmm...',
    '..dmmbbhTtTthbbmmd..',   // teal shadow transitions
    '.ddmmbbhhTThhbbmmdd.',   // wing roots widen
    'dddmmbbbhTThbbbmmdd.',   // widest — main wing span
    'dddmmbbhTTTThbbmmdd.',   // mirror
    '.ddmmbbhhTThhbbmmdd.',
    '..dmmmbbbhhbbbmmmdd.',
    '...dddmmmbbbbmmmddd.',   // tail narrows
    '....dddmmttttmmddd..',
    '.....ddddEEEEdddd...',   // engine shroud
    '......dddEEEEddd....',
    '.......ddEEEEdd.....',   // nozzle flare
    '........eEEEe.......',
  ],

  // ── HEAVY FREIGHTER ────────────────────────────────────────────────────────
  // Wide boxy body with central cargo bay (teal) and quad engines
  heavy: [
    '.......bhhb.........',   // blunt nose
    '......bbhThbb.......',
    '.....mbbhTWhbbm.....',
    '....mmbbhTTThbbmm...',
    '...dmmbbhTTTThbbmmd.',
    '..ddmmbhhTTTThhbbmdd',   // widest nose-block
    '.dddmmbbhTtTthbbmmdd',
    'ddddmmbbbhTThbbbmmdd',   // max wing span (cargo pod width)
    'ddddmmbbbhTThbbbmmdd',   // hold — same width for boxy feel
    'ddddmmbbbhTThbbbmmdd',
    '.dddmmbbhTTTThbbmmdd',
    '..ddmmbhhTTTThhbbmdd',
    '...dmmmbbbhThbbbmmmd',
    '....ddmmmbbbbbmmmdd.',
    '.....dddmmtttmmddd..',
    '....dddEEddddEEdd...',   // quad engine ports
    '....dEEEEddddEEEEd..',
    '.....eEEe....eEEe...',
  ],

  // ── COMBAT ─────────────────────────────────────────────────────────────────
  // Aggressive swept wings, red weapon ports at tips, narrow cockpit
  combat: [
    '.........Tl.........',   // sharp nose
    '........TThl........',
    '.......TTThhl.......',
    '......mTTThhbm......',
    '.....mmhTThhbbm.....',
    '....dmmhhTThbbmmd...',
    '...dmmbbhTThbbmmdd..',   // wing sweep starts
    '..RdmmbhhTThhibmddR.',   // R = weapon ports at wing tips
    '.RddmmbbhTThbbmmddR.',   // widest — swept wings
    '..RdmmbbhTThbbmmdR..',
    '...ddmmbhTTThbmmddd.',
    '....dddmhTTThmddd...',
    '.....ddmmhTThmmdd...',   // fuselage narrows
    '......ddmhTThmddd...',
    '.......dmmttmmd.....',
    '......ddEEttEEdd....',   // twin engines angled out
    '......dEEEttEEEd....',
    '.......eEe..eEe.....',
  ],
};

/**
 * Pick which sprite variant to use based on the ship class name string.
 * Keywords are matched case-insensitively.
 */
function _pickSprite(shipClass) {
  const s = (shipClass || '').toLowerCase();
  if (/corsair|intercept|pursuit|shadow|combat|phantom|fighter/.test(s)) return 'combat';
  if (/freighter|transport|trader|hauler|heavy|cargo|genesis|aurora/.test(s)) return 'heavy';
  return 'scout';   // explorer, scout, wanderer, drifter, voyager, ghost, etc.
}

/**
 * Return the HTML for the ship pixel-art section.
 * The canvas is drawn after mount via drawShipPixelArt().
 */
function buildShipSchematic(installed) {
  // Canvas: 20 px-cells × 7 px/cell = 140, plus 20 px padding each side → 180
  // Height: 18 rows × 7 + 40 = 166
  return `<canvas id="ship-pixel-canvas" width="180" height="166"
    style="display:block;margin:0 auto;image-rendering:pixelated"></canvas>`;
}

/**
 * Render the pixel-art ship sprite onto #ship-pixel-canvas.
 * Called after the DOM is ready (wireEvents).
 *
 * @param {string} shipClass  — ship_class string from the attributes response
 */
function drawShipPixelArt(shipClass) {
  const canvas = document.getElementById('ship-pixel-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  const PX   = 7;    // pixels per sprite cell
  const COLS = 20;   // sprite columns
  const ROWS = 18;   // sprite rows
  const OX   = 10;   // x offset (centres the 140px sprite in the 180px canvas)
  const OY   = 13;   // y offset

  // ── Background: deep space with tiny stars ──────────────────────────────
  ctx.fillStyle = '#05080f';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Deterministic star field — same hash every call so it doesn't flicker
  const stars = [
    [12,8],[40,5],[155,10],[170,3],[8,80],[175,60],[20,150],[160,140],
    [90,4],[100,160],[5,120],[178,100],[50,162],[130,8],[65,155],
  ];
  ctx.fillStyle = 'rgba(200,230,255,0.5)';
  stars.forEach(([x, y]) => ctx.fillRect(x, y, 1, 1));

  // ── Engine glow (drawn behind the sprite) ───────────────────────────────
  // Radial gradient centred on where the engine nozzles sit
  const glowX = OX + COLS * PX / 2;
  const glowY = OY + ROWS * PX + 6;
  const grd = ctx.createRadialGradient(glowX, glowY, 2, glowX, glowY, 28);
  grd.addColorStop(0,   'rgba(255,140,0,0.55)');
  grd.addColorStop(0.5, 'rgba(255,80,0,0.18)');
  grd.addColorStop(1,   'rgba(255,80,0,0)');
  ctx.fillStyle = grd;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // ── Sprite ──────────────────────────────────────────────────────────────
  const sprite = _SPRITES[_pickSprite(shipClass)] || _SPRITES.scout;

  sprite.forEach((row, ry) => {
    // Pad row to COLS chars in case it's shorter
    const padded = row.padEnd(COLS, '.');
    for (let cx = 0; cx < COLS; cx++) {
      const ch  = padded[cx];
      const col = _PIX_PAL[ch];
      if (!col) continue;   // transparent — skip
      ctx.fillStyle = col;
      ctx.fillRect(OX + cx * PX, OY + ry * PX, PX, PX);
    }
  });

  // ── Teal cockpit glow overlay ────────────────────────────────────────────
  // Soft glow centred around rows 1-4 where the cockpit T pixels are
  const ckX = OX + COLS * PX / 2;
  const ckY = OY + 3 * PX;
  const ckG = ctx.createRadialGradient(ckX, ckY, 0, ckX, ckY, 30);
  ckG.addColorStop(0,   'rgba(0,212,170,0.18)');
  ckG.addColorStop(1,   'rgba(0,212,170,0)');
  ctx.fillStyle = ckG;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // ── Ship name label ──────────────────────────────────────────────────────
  const name = _attrs?.ship_name || '';
  ctx.font      = '9px monospace';
  ctx.fillStyle = 'rgba(0,212,170,0.55)';
  ctx.textAlign = 'center';
  ctx.fillText(name.toUpperCase(), canvas.width / 2, canvas.height - 3);
}

function buildInstalledSection(installed) {
  if (!installed || Object.keys(installed).length === 0) {
    return "<p class=\"ship__empty\">No components installed.</p>";
  }
  const rows = Object.entries(installed).map(([slot, value]) => {
    const names = Array.isArray(value) ? value : [value];
    return names.map(n => `
      <div class="comp-row comp-row--installed">
        <span class="comp-row__slot">${slot.toUpperCase()}</span>
        <span class="comp-row__name">${n}</span>
      </div>
    `).join("");
  }).join("");
  return `<div class="comp-list">${rows}</div>`;
}

function buildSlotSection(slotKey, slotData, installed) {
  const available = slotData.available || [];
  if (available.length === 0) return "";

  const rows = available.map(comp => {
    const isInstalled = isComponentInstalled(comp.name, installed);

    // Faction lock badge
    const lockLabel = comp.faction_lock
      ? `<span class="comp-lock">[${Array.isArray(comp.faction_lock)
          ? comp.faction_lock.join(", ") : comp.faction_lock}]</span>`
      : "";

    // Stat pills — each key_stat shown as a coloured chip with sign and value
    const statPills = (comp.key_stats || []).map(s => {
      const positive = s.value >= 0;
      const sign     = positive ? "+" : "";
      return `<span class="comp-stat-pill ${positive ? "comp-stat-pill--pos" : "comp-stat-pill--neg"}">
                ${s.name} <strong>${sign}${s.value}</strong>
              </span>`;
    }).join("");

    // Lore / flavor text
    const loreHtml = comp.lore
      ? `<p class="comp-lore">${comp.lore}</p>`
      : "";

    return `
      <div class="comp-card ${isInstalled ? "comp-card--active" : ""}">

        <!-- Header row: name + meta badges -->
        <div class="comp-card__header">
          <span class="comp-card__name">${comp.name}</span>
          ${lockLabel}
          <span class="comp-card__cost">${comp.cost.toLocaleString()} ◈</span>
          <span class="comp-card__risk" title="Probability of component failure per jump">
            ${comp.failure_chance}% risk
          </span>
          ${isInstalled ? `<span class="comp-card__installed-badge">INSTALLED</span>` : ""}
        </div>

        <!-- Flavor text -->
        ${loreHtml}

        <!-- Key stat pills -->
        ${statPills ? `<div class="comp-stat-pills">${statPills}</div>` : ""}

        <!-- Install requires shipyard -->
        ${!isInstalled ? `<span class="comp-shipyard-notice">⚓ Requires Shipyard</span>` : ""}

      </div>
    `;
  }).join("");

  return `
    <div class="ship-slot-section">
      <h4 class="ship-slot-section__label">${slotData.label}</h4>
      <div class="comp-list">${rows}</div>
    </div>
  `;
}

function isComponentInstalled(name, installed) {
  for (const value of Object.values(installed)) {
    if (Array.isArray(value)) { if (value.includes(name)) return true; }
    else if (value === name) return true;
  }
  return false;
}


// ---------------------------------------------------------------------------
// Event wiring
// ---------------------------------------------------------------------------

function wireEvents(container) {
  // Draw pixel-art ship sprite if the components tab (which hosts the canvas) is active
  if (_tab === "components") {
    drawShipPixelArt(_attrs?.ship_class || '');
  }

  // Tab buttons
  container.querySelectorAll(".ship-tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      _tab = btn.dataset.tab;
      render(container);
    });
  });

  // Category filter buttons
  container.querySelectorAll(".ship-cat-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      _catFilter = btn.dataset.cat;
      render(container);
    });
  });

}

