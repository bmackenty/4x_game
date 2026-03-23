/**
 * frontend/js/views/system.js — Star system interior view.
 *
 * Renders a hex map of a single star system showing:
 *   • The star at hex (0, 0)
 *   • Planets on expanding orbital rings (ring 2, 3, 4 …)
 *   • Stations adjacent to their host planet
 *   • NPC ships on the outermost ring
 *
 * Clicking an object opens a right-panel detail card with relevant info
 * and action buttons (Enter Colony, Establish Colony).
 *
 * This view sits between the galaxy map and the colony surface in the
 * navigation hierarchy:
 *   Galaxy Map → System Interior → Colony Surface
 *
 * Context passed to mount():
 *   { systemName: string }
 *
 * Rendering pipeline: renderSystemMap() + attachHexInput() — identical
 * infrastructure to the galaxy and colony views.
 */

import { getSystemInterior }            from "../api.js";
import { renderSystemMap, SYSTEM_HEX_SIZE } from "../hex/hex-render.js";
import { attachHexInput }               from "../hex/hex-input.js";
import { notify }                       from "../ui/notifications.js";


// ---------------------------------------------------------------------------
// Module-level view state
// (reset to null in unmount() so stale data never bleeds into a new session)
// ---------------------------------------------------------------------------

/** Full response from GET /api/system/{name}/interior */
let _systemData = null;

/** Context passed to mount(): { systemName } */
let _context = {};

/** Canvas element */
let _canvas = null;

/** hex-input handle returned by attachHexInput() */
let _hexInput = null;

/** requestAnimationFrame ID for the render loop */
let _rafId = null;

/** Whether the canvas needs a repaint */
let _dirty = true;

/** The object dict from _systemData.objects that the player clicked */
let _selectedObj = null;


// ---------------------------------------------------------------------------
// XSS-safe HTML escaping (same helper used throughout the galaxy view)
// ---------------------------------------------------------------------------

/**
 * Escape a string for safe injection into innerHTML.
 * @param {string} s
 */
function esc(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}


// ---------------------------------------------------------------------------
// Public view object
// ---------------------------------------------------------------------------

export const systemView = {

  /**
   * Mount the system interior view.
   * @param {object} context - { systemName: string }
   */
  async mount(context = {}) {
    _context = context;
    const { systemName = "Unknown System" } = context;

    const container = document.getElementById("view-system");
    if (!container) return;

    // Inject chrome: header bar + canvas
    container.innerHTML = _buildChrome(systemName);
    _canvas = document.getElementById("system-canvas");

    // Wire "Back to Galaxy" button (lazy import avoids circular dep)
    document.getElementById("system-back-btn")
      ?.addEventListener("click", async () => {
        const { switchView } = await import("../main.js");
        switchView("galaxy");
      });

    // Show a loading state in the right panel
    _renderDefaultPanel("Loading system data…");

    // Fetch the hex layout from the backend
    try {
      _systemData = await getSystemInterior(systemName);
    } catch (err) {
      notify("ERROR", `Could not load system interior: ${err.message}`);
      _renderDefaultPanel("Failed to load system data.");
      return;
    }

    // Start the hex canvas
    _setupCanvas();

    // Show default prompt now that data is loaded
    _renderDefaultPanel();
  },

  unmount() {
    // Stop animation and remove event listeners
    if (_rafId) {
      cancelAnimationFrame(_rafId);
      _rafId = null;
    }
    if (_hexInput) {
      _hexInput.detach();
      _hexInput = null;
    }
    // Hide the shared right panel so it doesn't bleed into the next view
    _closePanel();
    _systemData  = null;
    _context     = {};
    _canvas      = null;
    _selectedObj = null;
    _dirty       = true;
  },
};


// ---------------------------------------------------------------------------
// Chrome (static HTML shell)
// ---------------------------------------------------------------------------

/**
 * Build the static HTML chrome for the system view.
 * The canvas is injected here; the right panel is populated dynamically.
 *
 * @param {string} systemName
 * @returns {string} innerHTML
 */
function _buildChrome(systemName) {
  return `
    <div class="system-view-header">
      <span class="system-view-breadcrumb">SYSTEM INTERIOR</span>
      <span class="system-view-title">${esc(systemName)}</span>
      <button class="btn btn--ghost btn--sm" id="system-back-btn">&#8592; GALAXY MAP</button>
    </div>
    <canvas id="system-canvas" class="hex-canvas system-canvas" aria-label="System interior canvas"></canvas>
  `;
}


// ---------------------------------------------------------------------------
// Canvas + render loop
// ---------------------------------------------------------------------------

/**
 * Attach hex input to the canvas and start the RAF render loop.
 */
function _setupCanvas() {
  if (!_canvas || !_systemData) return;

  // Match canvas pixel size to its CSS layout size
  _canvas.width  = _canvas.clientWidth  || 700;
  _canvas.height = _canvas.clientHeight || 600;

  // Attach pan/zoom/click input — same system as galaxy and colony views
  _hexInput = attachHexInput(_canvas, {
    hexSize:       SYSTEM_HEX_SIZE,
    onHexClick:    _onHexClick,
    onViewChanged: () => { _dirty = true; },
  });

  // Render loop — only redraws when _dirty is set
  function loop() {
    if (_dirty) {
      _dirty = false;
      renderSystemMap(
        _canvas,
        _systemData.objects,
        _systemData.grid_radius,
        {
          ..._hexInput.viewState,
          selectedQ:  _selectedObj?.q ?? null,
          selectedR:  _selectedObj?.r ?? null,
          playerHere: _systemData.player_ship_here,
        }
      );
    }
    _rafId = requestAnimationFrame(loop);
  }
  _rafId = requestAnimationFrame(loop);
}


// ---------------------------------------------------------------------------
// Hex click handler
// ---------------------------------------------------------------------------

/**
 * Called when the player clicks a hex on the system canvas.
 * @param {{ q: number, r: number }} coord
 */
function _onHexClick({ q, r }) {
  // Find the object at this hex (linear search — N is always small)
  const obj = (_systemData?.objects || []).find(o => o.q === q && o.r === r) || null;
  _selectedObj = obj;
  _dirty = true;

  if (obj) {
    _renderObjectPanel(obj);
  } else {
    _renderDefaultPanel();
  }
}


// ---------------------------------------------------------------------------
// Right panel rendering
// ---------------------------------------------------------------------------

/**
 * Show the main layout's right panel (reused from the galaxy view).
 */
function _openPanel() {
  const panel = document.getElementById("panel-right");
  if (panel) panel.classList.remove("panel--hidden");
}

/**
 * Hide the right panel and clear its content (called on unmount).
 */
function _closePanel() {
  const panel = document.getElementById("panel-right");
  if (panel) panel.classList.add("panel--hidden");
  const content = document.getElementById("panel-right-content");
  if (content) content.innerHTML = "";
}

/**
 * Show the default "click to inspect" hint in the right panel.
 * @param {string} [msg] - optional override message
 */
function _renderDefaultPanel(msg) {
  _openPanel();
  const content = document.getElementById("panel-right-content");
  if (!content) return;

  const systemName = _context.systemName || "System";
  const sysType    = _systemData?.system_type || "";

  content.innerHTML = `
    <div style="padding:var(--sp-3)">
      <h3 style="color:var(--accent-teal);letter-spacing:0.12em;
                 font-size:var(--font-size-md);margin-bottom:var(--sp-1)">
        ${esc(systemName)}
      </h3>
      ${sysType ? `<div style="font-size:var(--font-size-xs);color:var(--text-dim);
                               margin-bottom:var(--sp-4)">${esc(sysType)}</div>` : ""}
      <p style="color:var(--text-dim);font-size:var(--font-size-xs);line-height:1.6">
        ${esc(msg || "Click an object to inspect it.")}
      </p>
    </div>
  `;
}

/**
 * Populate the right panel with details about a clicked system object.
 * @param {object} obj - one entry from _systemData.objects
 */
function _renderObjectPanel(obj) {
  _openPanel();
  const content = document.getElementById("panel-right-content");
  if (!content) return;

  let html = "";

  if (obj.kind === "star") {
    html = _starPanel(obj);
  } else if (obj.kind === "planet") {
    html = _planetPanel(obj);
  } else if (obj.kind === "station") {
    html = _stationPanel(obj);
  } else if (obj.kind === "npc_ship") {
    html = _npcShipPanel(obj);
  } else {
    html = `<div style="padding:var(--sp-3);color:var(--text-dim);font-size:var(--font-size-xs)">
              Unknown object type: ${esc(obj.kind)}
            </div>`;
  }

  content.innerHTML = html;

  // Wire buttons that need JS event listeners (after innerHTML set)
  _wirePanelButtons(obj);
}

/**
 * HTML for the star detail card.
 */
function _starPanel(obj) {
  return `
    <div style="padding:var(--sp-3)">
      <div style="margin-bottom:var(--sp-3);padding-bottom:var(--sp-3);
                  border-bottom:1px solid var(--border-accent)">
        <h3 style="color:#f0d060;letter-spacing:0.12em;font-size:var(--font-size-md)">
          &#9733; ${esc(obj.label)}
        </h3>
        <div style="font-size:var(--font-size-xs);color:var(--text-dim);margin-top:var(--sp-1)">
          ${esc(obj.system_type || "Star System")}
        </div>
      </div>
      ${obj.description ? `
      <div style="font-size:var(--font-size-xs);color:var(--text-dim);line-height:1.6;
                  padding:var(--sp-2);background:var(--bg-secondary);
                  border-left:2px solid var(--border-accent)">
        ${esc(obj.description)}
      </div>` : ""}
    </div>
  `;
}

/**
 * HTML for the planet detail card.
 */
function _planetPanel(obj) {
  const habitableChip = obj.habitable
    ? `<span style="color:var(--accent-green);font-size:var(--font-size-xs);
                    border:1px solid var(--accent-green);padding:1px 6px;border-radius:2px">
         HABITABLE</span>`
    : `<span style="color:var(--text-dim);font-size:var(--font-size-xs);
                    border:1px solid var(--border-color);padding:1px 6px;border-radius:2px">
         BARREN</span>`;

  const resourceList = (obj.resources || []).slice(0, 6).map(r =>
    `<span style="display:inline-block;margin:2px;padding:1px 5px;background:var(--bg-secondary);
                  border:1px solid var(--border-color);font-size:var(--font-size-xs);
                  color:var(--text-dim)">${esc(r)}</span>`
  ).join("") || `<span style="font-size:var(--font-size-xs);color:var(--text-dim)">None detected</span>`;

  // Colony / establish button — wired after innerHTML is set (see _wirePanelButtons)
  let actionBtn = "";
  if (obj.habitable) {
    if (obj.has_colony) {
      actionBtn = `
        <button class="btn btn--secondary btn--sm btn-enter-colony"
                style="width:100%;margin-top:var(--sp-3)"
                data-planet="${esc(obj.label)}" data-type="${esc(obj.subtype)}">
          &#9689; ENTER COLONY
        </button>`;
    } else {
      actionBtn = `
        <button class="btn btn--primary btn--sm btn-establish-colony"
                style="width:100%;margin-top:var(--sp-3)"
                data-planet="${esc(obj.label)}" data-type="${esc(obj.subtype)}">
          &#8853; ESTABLISH COLONY
        </button>`;
    }
  }

  return `
    <div style="padding:var(--sp-3)">
      <div style="margin-bottom:var(--sp-3);padding-bottom:var(--sp-3);
                  border-bottom:1px solid var(--border-accent)">
        <h3 style="color:var(--text-bright);letter-spacing:0.1em;font-size:var(--font-size-md)">
          ${esc(obj.label)}
        </h3>
        <div style="display:flex;align-items:center;gap:var(--sp-2);margin-top:var(--sp-2)">
          <span style="font-size:var(--font-size-xs);color:var(--text-dim)">${esc(obj.subtype)}</span>
          ${habitableChip}
        </div>
      </div>

      ${obj.population > 0 ? `
      <div class="stat-row" style="margin-bottom:var(--sp-2)">
        <span class="stat-row__label">Population</span>
        <span class="stat-row__value">${obj.population.toLocaleString()}</span>
      </div>` : ""}

      ${obj.controlling_faction ? `
      <div class="stat-row" style="margin-bottom:var(--sp-2)">
        <span class="stat-row__label">Controlled by</span>
        <span class="stat-row__value" style="color:var(--accent-orange)">${esc(obj.controlling_faction)}</span>
      </div>` : ""}

      ${obj.has_colony ? `
      <div class="stat-row" style="margin-bottom:var(--sp-3)">
        <span class="stat-row__label">Colony</span>
        <span class="stat-row__value" style="color:var(--accent-teal)">&#8962; YOUR COLONY</span>
      </div>` : ""}

      <div style="margin-bottom:var(--sp-2)">
        <div class="section-header" style="margin-bottom:var(--sp-2)">Resources</div>
        <div>${resourceList}</div>
      </div>

      ${actionBtn}
    </div>
  `;
}

/**
 * HTML for the station detail card.
 */
function _stationPanel(obj) {
  const serviceChips = (obj.services || []).map(s =>
    `<span style="display:inline-block;margin:2px;padding:1px 5px;background:var(--bg-secondary);
                  border:1px solid #c08820;font-size:var(--font-size-xs);
                  color:#d0a040">${esc(s)}</span>`
  ).join("") || `<span style="font-size:var(--font-size-xs);color:var(--text-dim)">No services listed</span>`;

  return `
    <div style="padding:var(--sp-3)">
      <div style="margin-bottom:var(--sp-3);padding-bottom:var(--sp-3);
                  border-bottom:1px solid var(--border-accent)">
        <h3 style="color:#d0a040;letter-spacing:0.1em;font-size:var(--font-size-md)">
          &#8853; ${esc(obj.label)}
        </h3>
        <div style="font-size:var(--font-size-xs);color:var(--text-dim);margin-top:var(--sp-1)">
          ${esc(obj.station_type || "Station")}
        </div>
      </div>

      <div style="margin-bottom:var(--sp-3)">
        <div class="section-header" style="margin-bottom:var(--sp-2)">Services</div>
        <div>${serviceChips}</div>
      </div>

      ${obj.description ? `
      <div style="font-size:var(--font-size-xs);color:var(--text-dim);line-height:1.6;
                  padding:var(--sp-2);background:var(--bg-secondary);
                  border-left:2px solid #c08820">
        ${esc(obj.description)}
      </div>` : ""}
    </div>
  `;
}

/**
 * HTML for the NPC ship detail card.
 */
function _npcShipPanel(obj) {
  return `
    <div style="padding:var(--sp-3)">
      <div style="margin-bottom:var(--sp-3);padding-bottom:var(--sp-3);
                  border-bottom:1px solid var(--border-accent)">
        <h3 style="color:var(--accent-orange);letter-spacing:0.1em;font-size:var(--font-size-md)">
          &#9650; ${esc(obj.label)}
        </h3>
        <div style="font-size:var(--font-size-xs);color:var(--text-dim);margin-top:var(--sp-1)">
          ${esc(obj.ship_type || "Vessel")}
        </div>
      </div>
      ${obj.faction ? `
      <div class="stat-row">
        <span class="stat-row__label">Faction</span>
        <span class="stat-row__value" style="color:var(--accent-orange)">${esc(obj.faction)}</span>
      </div>` : ""}
    </div>
  `;
}

/**
 * Wire any action buttons injected by _renderObjectPanel after innerHTML is set.
 * @param {object} obj - the clicked system object
 */
function _wirePanelButtons(obj) {
  const content = document.getElementById("panel-right-content");
  if (!content) return;

  // "Enter Colony" — navigate to the colony surface view
  content.querySelector(".btn-enter-colony")
    ?.addEventListener("click", async () => {
      const { switchView } = await import("../main.js");
      switchView("colony", {
        planetName:  obj.label,
        systemName:  _context.systemName,
        planetType:  obj.subtype,
      });
    });

  // "Establish Colony" — navigate to colony view which handles the found-colony prompt
  content.querySelector(".btn-establish-colony")
    ?.addEventListener("click", async () => {
      const { switchView } = await import("../main.js");
      switchView("colony", {
        planetName:  obj.label,
        systemName:  _context.systemName,
        planetType:  obj.subtype,
      });
    });
}
