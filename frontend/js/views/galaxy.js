/**
 * views/galaxy.js — Galaxy map view.
 *
 * Renders all star systems as hexes on an HTML5 Canvas, supports pan/zoom,
 * shows a system-detail panel in the right sidebar when a system is clicked,
 * and lets the player jump to adjacent systems.
 *
 * Architecture:
 *   mount()    — fetch galaxy data, attach input handlers, start render loop
 *   unmount()  — detach input handlers, cancel render loop
 *
 * The render loop uses requestAnimationFrame for smooth pan/zoom.
 * It only redraws when the view state is "dirty" (changed since last frame).
 */

import { state }              from "../state.js";
import { getGalaxyMap, getSystem, jumpToCoords,
         getMarket, buyGoods, sellGoods,
         getSystemPresence,
         getStation, getStationUpgrades, buyStationUpgrade, repairShipAtStation,
         getNpcShips,
         harvestDeepSpace, foundDeepSpaceOutpost, encounterDerelict } from "../api.js";
import { notify }             from "../ui/notifications.js";
import { showModal, closeModal } from "../ui/modal.js";
import { renderGalaxyMap, GALAXY_HEX_SIZE } from "../hex/hex-render.js";
import { attachHexInput }     from "../hex/hex-input.js";

// ---------------------------------------------------------------------------
// Galaxy projection scale — must match GALAXY_SCALE in backend/hex_utils.py
// Converts 3D game coordinates (x, y, z) → 2D axial hex (q, r).
// ---------------------------------------------------------------------------
const GALAXY_SCALE = 12.5;  // 500 galaxy units / 40 hex columns

/**
 * Project a ship's 3D game coordinates to the 2D axial hex grid.
 * @param {number[]} coords - [x, y, z] from ship.coordinates
 * @returns {{ q: number, r: number }}
 */
function shipCoordsToHex(coords) {
  if (!coords || coords.length < 2) return null;
  const q = Math.round(coords[0] / GALAXY_SCALE);
  return { q, r: Math.round(coords[1] / GALAXY_SCALE - q / 2) };
}

/**
 * Convert an axial hex (q, r) to canvas world-space pixel position.
 * Mirrors axialToPixel in hex-math.js (flat-top hex layout).
 * @param {number} q
 * @param {number} r
 * @param {number} size - hex radius in pixels
 * @returns {{ x: number, y: number }}
 */
function hexToPixel(q, r, size) {
  return {
    x: size * 1.5 * q,
    y: size * (Math.sqrt(3) / 2 * q + Math.sqrt(3) * r),
  };
}

/**
 * Convert an axial hex (q, r) back to 3D galaxy coordinates.
 * Inverse of galaxy_coords_to_hex in backend/hex_utils.py.
 * Z defaults to the player's current target depth (set by the Z-gauge).
 * Pass an explicit z to override (e.g. for system jumps that use actual Z).
 * @param {number} q
 * @param {number} r
 * @param {number} [z] - Optional Z override; falls back to targetZ
 * @returns {{ x: number, y: number, z: number }}
 */
function hexToGalaxyCoords(q, r, z) {
  return { x: q * GALAXY_SCALE, y: (r + q / 2) * GALAXY_SCALE, z: z ?? targetZ };
}


// ---------------------------------------------------------------------------
// Faction colour map — approximate colours for major factions
// Built lazily from the faction data in state.factions
// ---------------------------------------------------------------------------
const FACTION_COLORS = new Map([
  ["The Veritas Covenant",            "rgba(0,170,255,0.3)"],
  ["Stellar Nexus Guild",             "rgba(0,212,170,0.3)"],
  ["The Icaron Collective",           "rgba(170,100,220,0.3)"],
  ["The Gaian Enclave",               "rgba(50,180,80,0.3)"],
  ["The Gearwrights Guild",           "rgba(200,140,0,0.3)"],
  ["Celestial Alliance",              "rgba(0,200,255,0.3)"],
  ["Void Syndicate",                  "rgba(80,0,120,0.3)"],
  ["The Merchant Consortium",         "rgba(200,180,0,0.3)"],
  ["Etheric Order",                   "rgba(180,100,255,0.3)"],
  ["The Remnants",                    "rgba(180,60,60,0.3)"],
  ["Harmonic Resonance Collective",   "rgba(0,230,200,0.3)"],
  ["default",                         "rgba(100,140,180,0.2)"],
]);

// ---------------------------------------------------------------------------
// Module-level mutable state for this view
// ---------------------------------------------------------------------------
let inputControls  = null;   // return value of attachHexInput()
let rafHandle      = null;   // requestAnimationFrame handle
let isDirty        = true;   // if true, redraw on next frame
let systemsData    = [];     // cached from /api/galaxy/map
let stationsData   = [];     // deep-space stations from /api/galaxy/map
let dsoData        = [];     // deep space objects from /api/galaxy/map
let npcShipsData   = [];     // NPC bot positions from /api/npc_ships (hex-projected)

// Z-elevation state
let zStats        = null;    // { mean, std, min, max } computed from systemsData z values — kept for backward compat
let activeZFilter = "all";   // "all"|"1"|"2"|"3"|"4"|"5" (layer index, or "all")

// Z-depth target — the Z plane used for empty-space jumps.
// Updated when the player clicks a layer filter button.
// Defaults to galactic midplane (105 = layer 3 center); preserved across re-mounts.
let targetZ = 105;

// Sensor ring toggle — persists while this view is mounted
let showScanRing  = false;

// View transform
let viewState = { panX: 0, panY: 0, zoom: 1.0, selectedSystemName: null, selectedStationName: null };

/** Cached market data for the currently selected system. */
let _marketData = null;


// ---------------------------------------------------------------------------
// Z-elevation helpers
// ---------------------------------------------------------------------------

/**
 * Return the Z coordinate at the center of a galactic layer.
 * Used to set targetZ when the player clicks a layer filter button.
 * Layer centers mirror GALAXY_LAYERS in navigation.py.
 * "all" preserves the current targetZ.
 * @param {string} layerKey  "all"|"1"|"2"|"3"|"4"|"5"
 * @returns {number}
 */
function _layerCenterZ(layerKey) {
  const LAYER_CENTERS = { "1": 25, "2": 65, "3": 105, "4": 145, "5": 180 };
  return layerKey in LAYER_CENTERS ? LAYER_CENTERS[layerKey] : targetZ;
}

/**
 * Compute mean and standard deviation of the z coordinates across all systems.
 * Used to classify each system into an elevation band (high/above/plane/below/deep).
 * @param {Array} systems
 * @returns {{ mean: number, std: number, min: number, max: number }|null}
 */
function _computeZStats(systems) {
  if (!systems || !systems.length) return null;
  const zs   = systems.map(s => s.z ?? 0);
  const min  = Math.min(...zs);
  const max  = Math.max(...zs);
  const mean = zs.reduce((a, b) => a + b, 0) / zs.length;
  const std  = Math.sqrt(zs.reduce((a, b) => a + (b - mean) ** 2, 0) / zs.length);
  return { mean, std, min, max };
}

/**
 * Build the HTML for the galactic layer filter bar.
 * Buttons correspond to the 5 fixed galactic strata (mirrors GALAXY_LAYERS in navigation.py).
 * The active button is marked with the z-filter-btn--active class.
 * @returns {string}
 */
function _buildZFilterBar() {
  const layers = [
    { key: "all", label: "ALL",           title: "Show systems on every galactic layer" },
    { key: "5",   label: "↑↑ HIGH ORBIT", title: "High Orbit — sparse, fast ether, faction patrols (Z 165–195)" },
    { key: "4",   label: "↑ UPPER",       title: "Upper Reaches — thinning systems, fast currents (Z 125–165)" },
    { key: "3",   label: "— PLANE",       title: "Galactic Plane — most systems, balanced risk/reward (Z 85–125)" },
    { key: "2",   label: "↓ LOWER",       title: "Lower Reaches — below the plane, mining-rich (Z 45–85)" },
    { key: "1",   label: "↓↓ DEEP VOID",  title: "Deep Void — sparse, heavy ether, ancient ruins (Z 5–45)" },
  ];
  const btns = layers.map(l => `
    <button class="z-filter-btn${activeZFilter === l.key ? " z-filter-btn--active" : ""}"
            data-zband="${l.key}" title="${l.title}">${l.label}</button>
  `).join("");
  return `
    <div class="z-filter-bar" id="z-filter-bar">
      <span class="z-filter-bar__label">LAYER</span>
      ${btns}
      <button
        class="z-filter-btn${showScanRing ? " z-filter-btn--active" : ""}"
        id="btn-scan-ring"
        title="Toggle sensor range ring"
        style="margin-left:auto">
        ◎ SENSORS
      </button>
    </div>
  `;
}


// ---------------------------------------------------------------------------
// Exported view object
// ---------------------------------------------------------------------------

export const galaxyView = {

  async mount(context) {
    const canvas = document.getElementById("galaxy-canvas");
    if (!canvas) return;

    // Always re-fetch the galaxy map so has_player_colony and visited flags
    // are up to date without requiring a browser refresh.
    try {
      const result = await getGalaxyMap();
      state.galaxyMap         = result.systems            || [];
      state.stationsData      = result.stations           || [];
      state.deepSpaceObjects  = result.deep_space_objects || [];
    } catch (err) {
      // Fall back to cached data if the fetch fails
      if (state.galaxyMap.length === 0) {
        notify("ERROR", `Could not load galaxy map: ${err.message}`);
        return;
      }
    }
    systemsData  = state.galaxyMap;
    stationsData = state.stationsData      || [];
    dsoData      = state.deepSpaceObjects  || [];

    // Compute z-elevation statistics across all systems now that data is loaded.
    zStats = _computeZStats(systemsData);

    // Initialise targetZ to the ship's current Z so empty-space jumps start
    // at the player's actual depth rather than always snapping to midplane (25).
    {
      const initShipZ = state.gameState?.ship?.coordinates?.[2];
      if (initShipZ !== undefined) targetZ = initShipZ;
    }

    // Inject the galactic-plane filter bar above the canvas.
    // Remove any stale bar from a previous mount first to avoid duplication.
    const oldBar = document.getElementById("z-filter-bar");
    if (oldBar) oldBar.remove();
    canvas.insertAdjacentHTML("beforebegin", _buildZFilterBar());
    const filterBarEl = document.getElementById("z-filter-bar");
    filterBarEl.addEventListener("click", e => {
      // Sensor ring toggle
      if (e.target.closest("#btn-scan-ring")) {
        showScanRing = !showScanRing;
        e.target.closest("#btn-scan-ring").classList.toggle("z-filter-btn--active", showScanRing);
        isDirty = true;
        return;
      }

      const btn = e.target.closest("[data-zband]");
      if (!btn) return;
      activeZFilter = btn.dataset.zband;
      // Set the target jump depth to the centre of the selected layer so that
      // clicking a layer button also moves the player's operating depth —
      // "show me these systems" and "I want to travel at this elevation" are
      // the same action.  "ALL" preserves the current targetZ.
      targetZ = _layerCenterZ(activeZFilter);
      // Update active button styling immediately
      filterBarEl.querySelectorAll(".z-filter-btn").forEach(b => {
        b.classList.toggle("z-filter-btn--active", b.dataset.zband === activeZFilter);
      });
      isDirty = true;
    });

    // Fetch NPC bot positions.  The backend pre-projects each bot to axial
    // hex coordinates and ensures they never overlap a star-system hex, so we
    // use hex_q / hex_r directly rather than re-projecting from raw coordinates.
    try {
      const npcResult = await getNpcShips();
      npcShipsData = (npcResult.ships || []).map(ship => ({
        name:     ship.name,
        bot_type: ship.bot_type,
        hex_q:    ship.hex_q,
        hex_r:    ship.hex_r,
      }));
    } catch (_) {
      npcShipsData = [];  // NPC ships are cosmetic — silently fail
    }

    // Show the right panel immediately — either the pre-selected system or the default state
    if (state.selectedSystem) {
      viewState.selectedSystemName = state.selectedSystem.name;
      showSystemPanel(state.selectedSystem);
    } else {
      showDefaultPanel();
    }

    // Attach pan/zoom/click input
    inputControls = attachHexInput(canvas, {
      hexSize:       GALAXY_HEX_SIZE,
      onHexClick:    handleHexClick,
      onHexHover:    handleHexHover,
      onViewChanged: (vs) => {
        viewState = { ...viewState, ...vs };
        isDirty = true;
      },
    });

    // Sync initial viewState from inputControls
    viewState = { ...viewState, ...inputControls.viewState };

    // Centre the initial view on the player's ship position so it's visible
    // without having to pan.  Applies only on first mount, not when returning
    // from the colony view (where the player may have already panned).
    const shipCoords = state.gameState?.ship?.coordinates;
    const shipHex    = shipCoordsToHex(shipCoords);
    if (shipHex && viewState.panX === 0 && viewState.panY === 0) {
      const { x: spx, y: spy } = hexToPixel(shipHex.q, shipHex.r, GALAXY_HEX_SIZE);
      inputControls.viewState.panX = -spx;
      inputControls.viewState.panY = -spy;
      viewState = { ...viewState, ...inputControls.viewState };
    }

    // Start render loop
    isDirty = true;
    startRenderLoop(canvas);
  },

  unmount() {
    // Stop the render loop
    if (rafHandle !== null) {
      cancelAnimationFrame(rafHandle);
      rafHandle = null;
    }
    // Remove input listeners
    if (inputControls) {
      inputControls.detach();
      inputControls = null;
    }
    // Remove the galactic plane filter bar (includes the sensor ring toggle)
    const filterBar = document.getElementById("z-filter-bar");
    if (filterBar) filterBar.remove();

    // Reset overlay toggles so re-mounting starts clean
    showScanRing = false;

    // Hide the right panel
    hideRightPanel();
  },
};


// ---------------------------------------------------------------------------
// Render loop
// ---------------------------------------------------------------------------

function startRenderLoop(canvas) {
  function frame() {
    if (isDirty) {
      isDirty = false;

      // Compute ship hex position fresh each frame so it updates after jumps.
      // state.gameState.ship.coordinates is [x, y, z] (Python tuple → JSON array).
      const shipCoords  = state.gameState?.ship?.coordinates;
      const shipHex     = shipCoordsToHex(shipCoords);

      // Jump + sensor range rings: convert game units → canvas pixel units.
      // GALAXY_SCALE = 12.5 game units per hex, GALAXY_HEX_SIZE = 22 px per hex
      const PX_PER_UNIT = GALAXY_HEX_SIZE / GALAXY_SCALE;
      const jumpRange    = state.gameState?.ship?.jump_range  ?? 0;
      const scanRange    = state.gameState?.ship?.scan_range  ?? 0;
      const jumpRangePx  = jumpRange * PX_PER_UNIT;
      const scanRangePx  = scanRange * PX_PER_UNIT;

      // Ship's actual Z coordinate for the gauge's ship-position hairline
      const shipZ = shipCoords?.[2] ?? 25;

      renderGalaxyMap(
        canvas,
        systemsData,
        { ...viewState, shipHex, jumpRangePx, scanRangePx, scanRangeUnits: scanRange,
          showScanRing, stations: stationsData, npcShips: npcShipsData,
          deepSpaceObjects: dsoData, zStats, activeZFilter, zoom: viewState.zoom,
          // Ship Z passed through for the top-right elevation readout in hex-render.js
          gaugeShipZ: shipZ },
        FACTION_COLORS
      );
    }
    rafHandle = requestAnimationFrame(frame);
  }
  rafHandle = requestAnimationFrame(frame);
}


// ---------------------------------------------------------------------------
// Hex click handler — find which system was clicked and show its detail panel
// ---------------------------------------------------------------------------

async function handleHexClick({ q, r }) {
  // Check for a deep-space station first (they're their own hex objects)
  const station = stationsData.find(s => s.hex_q === q && s.hex_r === r);
  if (station) {
    viewState.selectedStationName = station.name;
    viewState.selectedSystemName  = null;
    state.selectedSystem = null;
    isDirty = true;
    showStationPanel(station);
    return;
  }

  // Find the system at this hex coordinate
  const sys = systemsData.find(s => s.hex_q === q && s.hex_r === r);

  if (!sys) {
    // Check for a deep space object at this hex
    const dso = dsoData.find(d => d.hex_q === q && d.hex_r === r);
    if (dso) {
      viewState.selectedSystemName  = null;
      viewState.selectedStationName = null;
      state.selectedSystem = null;
      isDirty = true;
      // If not already here, move then show panel (handleDeepSpaceMove shows it on arrival)
      const dsoCoords = hexToGalaxyCoords(q, r);
      if (!_playerIsAt([dsoCoords.x, dsoCoords.y, dsoCoords.z])) {
        handleDeepSpaceMove(q, r);
      } else {
        showDsoPanel(dso, q, r);
      }
      return;
    }

    // Truly empty hex — move there immediately
    viewState.selectedSystemName  = null;
    viewState.selectedStationName = null;
    state.selectedSystem = null;
    isDirty = true;
    const emptyCoords = hexToGalaxyCoords(q, r);
    if (!_playerIsAt([emptyCoords.x, emptyCoords.y, emptyCoords.z])) {
      handleDeepSpaceMove(q, r);
    } else {
      showEmptyHexPanel(q, r);
    }
    return;
  }

  // Select the system
  viewState.selectedSystemName  = sys.name;
  viewState.selectedStationName = null;
  state.selectedSystem = sys;
  isDirty = true;

  if (sys.in_scan_range === false) {
    // Out of scanner range — show limited ghost panel without API call
    showOutOfRangePanel(sys);
    return;
  }

  // Jump immediately if not already at this system
  if (!_playerIsAt(sys.coordinates)) {
    handleJump(sys);  // fire-and-forget; panel loads in parallel
  }

  // Fetch detailed system data (planets, market, etc.) and show panel
  try {
    const detail = await getSystem(sys.name);
    // Mark as visited in our local cache too
    sys.visited = true;
    showSystemPanel(detail);
  } catch (err) {
    notify("ERROR", `Could not load system data: ${err.message}`);
  }
}


// ---------------------------------------------------------------------------
// Hover handler — used for tooltip (Phase 6 polish)
// ---------------------------------------------------------------------------

function handleHexHover({ q, r }) {
  // Hover tooltips will be added in Phase 6
  // For now, nothing to do
}


// ---------------------------------------------------------------------------
// System detail panel (right sidebar)
// ---------------------------------------------------------------------------

/**
 * Show a limited panel for a system that is known but outside scanner range.
 * No live intel — only name, type, and last-known coordinates.
 */
function showOutOfRangePanel(sys) {
  const panel = document.getElementById("panel-right");
  const content = document.getElementById("panel-right-content");
  if (!panel || !content) return;

  panel.classList.remove("panel--hidden");
  state.rightPanelOpen = true;

  const fmt = n => (Math.round((n ?? 0) * 10) / 10).toFixed(1);
  content.innerHTML = `
    <div class="panel-section">
      <div class="panel-title">${esc(sys.name)}</div>
      <div style="color:var(--text-dim);font-size:var(--font-size-xs);
                  text-transform:uppercase;letter-spacing:0.08em;margin-bottom:var(--sp-3)">
        ${esc(sys.type ?? "Unknown")}
      </div>
      <div style="padding:var(--sp-3);background:var(--bg-secondary);
                  border-left:2px solid var(--accent-orange);margin-bottom:var(--sp-3);
                  font-size:var(--font-size-xs)">
        <div style="color:var(--accent-orange);text-transform:uppercase;
                    letter-spacing:0.08em;margin-bottom:var(--sp-2)">
          ⊘ OUT OF SCANNER RANGE
        </div>
        <div style="color:var(--text-dim)">
          Signal degraded. Last known position:
          (${fmt(sys.x)},&thinsp;${fmt(sys.y)},&thinsp;${fmt(sys.z)})
        </div>
        <div style="color:var(--text-dim);margin-top:var(--sp-1)">
          Move within scanner range for full intelligence.
        </div>
      </div>
    </div>
  `;
}

async function showSystemPanel(system) {
  const panel = document.getElementById("panel-right");
  const content = document.getElementById("panel-right-content");
  if (!panel || !content) return;

  // Reveal the panel
  panel.classList.remove("panel--hidden");
  state.rightPanelOpen = true;

  // Reset market data — will be fetched below
  _marketData = null;

  // Render the panel immediately with what we have (no presence/market yet)
  content.innerHTML = buildSystemPanelHtml(system, null, null);

  // "Enter System" → open the system interior hex map view
  content.querySelector(".btn-enter-system")?.addEventListener("click", async () => {
    const { switchView } = await import("../main.js");
    switchView("system", { systemName: system.name });
  });

  // Faction name link → open diplomacy view focused on that faction
  content.querySelector(".btn-faction-link")?.addEventListener("click", async (e) => {
    const factionName = e.currentTarget.dataset.faction;
    const { switchView } = await import("../main.js");
    switchView("diplomacy", { factionName });
  });

  // Colony "found" buttons on each habitable planet
  content.querySelectorAll(".btn-found-colony").forEach(btn => {
    btn.addEventListener("click", () => {
      const planetName = btn.dataset.planet;
      const planetType = btn.dataset.type;
      handleFoundColony(system.name, planetName, planetType);
    });
  });

  // Fetch presence and market data concurrently
  const [presenceResult, marketResult] = await Promise.allSettled([
    getSystemPresence(system.name),
    getMarket(system.name),
  ]);

  // Check if the player is physically at this system
  const atThisSystem = _playerIsAt(system.coordinates);

  // Inject NPC presence section
  const presence = presenceResult.status === "fulfilled" ? presenceResult.value : null;
  if (presence) {
    _renderPresenceSection(content, presence);
    // Wire TRADE button only if player is here and market exists
    if (presence.has_market && atThisSystem) {
      content.querySelector(".btn-open-trade")
        ?.addEventListener("click", () => _openTradeView(system.name));
    } else if (presence.has_market && !atThisSystem) {
      // Remove the TRADE button — player is not here
      content.querySelector(".btn-open-trade")?.remove();
    }
  } else {
    content.querySelector(".presence-placeholder")?.remove();
  }

  // Inject market section only when player is at this system
  if (atThisSystem && marketResult.status === "fulfilled") {
    _marketData = marketResult.value;
    _renderMarketSection(system.name, _marketData);
  } else {
    content.querySelector(".market-placeholder")?.remove();
  }
}

function hideRightPanel() {
  const panel = document.getElementById("panel-right");
  if (panel) panel.classList.add("panel--hidden");
  state.rightPanelOpen = false;
}

function showDefaultPanel() {
  const panel   = document.getElementById("panel-right");
  const content = document.getElementById("panel-right-content");
  if (!panel || !content) return;

  panel.classList.remove("panel--hidden");
  state.rightPanelOpen = true;

  const location = state.gameState?.ship?.current_system || "Deep Space";

  content.innerHTML = `
    <div class="panel-section">
      <div class="panel-title">GALAXY NAVIGATION</div>
    </div>
    <div class="panel-section">
      <div style="color:var(--text-dim);font-size:var(--font-size-xs);text-transform:uppercase;
                  letter-spacing:0.08em;margin-bottom:var(--sp-2)">Current Location</div>
      <div style="color:var(--text-bright);font-family:var(--font-mono)">${esc(location)}</div>
    </div>
    <div class="panel-section">
      <p class="legend-hint">Select a system on the map to view details, jump, or access markets.</p>
    </div>
  `;
}


// ---------------------------------------------------------------------------
// Empty-hex panel — move to deep space
// ---------------------------------------------------------------------------

/**
 * Show a minimal panel when the player clicks an empty hex with no system or DSO.
 * Offers a "Move here" button to jump to empty space.
 */
function showEmptyHexPanel(q, r) {
  const panel   = document.getElementById("panel-right");
  const content = document.getElementById("panel-right-content");
  if (!panel || !content) return;

  panel.classList.remove("panel--hidden");
  state.rightPanelOpen = true;

  const coords = hexToGalaxyCoords(q, r);
  content.innerHTML = `
    <div class="panel-section">
      <div class="panel-title" style="color:var(--text-dim)">DEEP SPACE</div>
      <div style="color:var(--text-dim);font-size:var(--font-size-xs);
                  text-transform:uppercase;letter-spacing:0.08em;margin-bottom:var(--sp-3)">
        Hex (${q}, ${r})
      </div>
      <div style="padding:var(--sp-3);background:var(--bg-secondary);
                  border-left:2px solid var(--text-dim);margin-bottom:var(--sp-3);
                  font-size:var(--font-size-xs);color:var(--text-dim)">
        Empty space. No objects detected on long-range sensors.<br>
        <span style="opacity:0.6">Coords: (${coords.x.toFixed(0)}, ${coords.y.toFixed(0)}, ${coords.z.toFixed(0)})</span>
      </div>
    </div>
  `;
}


// ---------------------------------------------------------------------------
// Deep space object detail panel
// ---------------------------------------------------------------------------

/** Icons for each DSO type (normal / depleted) */
const DSO_ICONS = {
  derelict:      "⊘",
  anomaly:       "✦",
  resource_node: "◈",
  outpost_site:  "○",
};
const DSO_ICONS_EXPLORED = {
  derelict:      "✓",
  resource_node: "✓",
};

/** Accent colours for each DSO type */
const DSO_COLORS = {
  derelict:      "var(--accent-orange)",
  anomaly:       "rgba(140,80,255,0.9)",
  resource_node: "rgba(0,212,100,0.9)",
  outpost_site:  "rgba(0,170,255,0.9)",
};

/**
 * Show the detail panel for a deep space object.
 * If the ship is already here, show action buttons.
 */
function showDsoPanel(dso, q, r) {
  const panel   = document.getElementById("panel-right");
  const content = document.getElementById("panel-right-content");
  if (!panel || !content) return;

  panel.classList.remove("panel--hidden");
  state.rightPanelOpen = true;

  const icon   = (dso.depleted && DSO_ICONS_EXPLORED[dso.type]) ? DSO_ICONS_EXPLORED[dso.type] : (DSO_ICONS[dso.type] || "·");
  const color  = dso.depleted ? "var(--text-dim)" : (DSO_COLORS[dso.type] || "var(--text-dim)");
  const coords = hexToGalaxyCoords(q, r);

  const shipCoords = state.gameState?.ship?.coordinates;
  const shipHex = shipCoords
    ? { q: Math.round(shipCoords[0] / GALAXY_SCALE), r: Math.round(shipCoords[1] / GALAXY_SCALE) }
    : null;
  const shipIsHere = shipHex && shipHex.q === q && shipHex.r === r;

  const typeLabel = dso.type.replace(/_/g, " ").toUpperCase();
  const displayName = dso.name || dso.subtype || typeLabel;
  const displayDesc = dso.description || "Sensor data incomplete. Move closer to scan.";

  let actionHtml = "";
  if (shipIsHere && !dso.depleted) {
    if (dso.type === "resource_node" || dso.type === "derelict") {
      const label = dso.type === "derelict" ? "⊘ SALVAGE" : "◈ HARVEST";
      actionHtml = `<button class="btn btn-primary btn-dso-harvest"
                            style="width:100%;margin-top:var(--sp-2)">${label}</button>`;
    } else if (dso.type === "outpost_site") {
      actionHtml = `<button class="btn btn-secondary btn-dso-outpost"
                            style="width:100%;margin-top:var(--sp-2)">○ FOUND OUTPOST</button>`;
    }
  }

  if (dso.depleted) {
    const depletedLabel = dso.type === "derelict" ? "✓ EXPLORED" : "DEPLETED";
    actionHtml = `<div style="color:var(--text-dim);font-size:var(--font-size-xs);
                              margin-top:var(--sp-2);text-align:center">${depletedLabel}</div>`;
  }

  content.innerHTML = `
    <div class="panel-section">
      <div class="panel-title" style="color:${color}">${icon} ${esc(displayName)}</div>
      <div style="color:${color};font-size:var(--font-size-xs);
                  text-transform:uppercase;letter-spacing:0.08em;margin-bottom:var(--sp-3)">
        ${typeLabel} · Hex (${q}, ${r})
      </div>
      <div style="padding:var(--sp-3);background:var(--bg-secondary);
                  border-left:2px solid ${color};margin-bottom:var(--sp-3);
                  font-size:var(--font-size-xs);color:var(--text-secondary)">
        ${esc(displayDesc)}
        <div style="color:var(--text-dim);margin-top:var(--sp-2);opacity:0.6">
          Coords: (${coords.x.toFixed(0)}, ${coords.y.toFixed(0)}, ${coords.z.toFixed(0)})
        </div>
      </div>
      ${actionHtml}
    </div>
  `;

  content.querySelector(".btn-dso-harvest")
    ?.addEventListener("click", () => handleDsoHarvest(dso));
  content.querySelector(".btn-dso-outpost")
    ?.addEventListener("click", () => handleDsoOutpost());
  content.querySelector(".btn-move-deep-space")
    ?.addEventListener("click", () => handleDeepSpaceMove(q, r));
}


// ---------------------------------------------------------------------------
// Station detail panel
// ---------------------------------------------------------------------------

async function showStationPanel(station) {
  const panel   = document.getElementById("panel-right");
  const content = document.getElementById("panel-right-content");
  if (!panel || !content) return;

  panel.classList.remove("panel--hidden");
  state.rightPanelOpen = true;

  // Show loading shell immediately
  content.innerHTML = _buildStationPanelHtml(station, null, null);
  _wireStationButtons(content, station, null, null);

  // Fetch station detail first so we know which optional endpoints to call
  let detail = null;
  try { detail = await getStation(station.name); } catch (_) { /* detail stays null */ }

  // Only fetch upgrades if the station actually offers "Ship Upgrades" — avoids a
  // spurious 400 from the backend for stations that have no upgrade service.
  let upgrades = null;
  if (detail?.has_upgrades) {
    try { upgrades = await getStationUpgrades(station.name); } catch (_) { /* stays null */ }
  }

  // Re-render with full data
  content.innerHTML = _buildStationPanelHtml(station, detail, upgrades);
  _wireStationButtons(content, station, detail, upgrades);
}

function _buildStationPanelHtml(station, detail, upgrades) {
  const services = (detail?.services || station.services || []);
  const stationHasMarket = detail ? detail.has_market : services.some(s => ["Market","Ore Processing","Luxury Goods"].includes(s));
  const hasUpgrades = detail ? detail.has_upgrades : services.includes("Ship Upgrades");
  // Only show market button when player is physically at this station's system
  const playerHere  = _playerIsInSystem(station.system_name);
  const hasMarket   = stationHasMarket && playerHere;

  const serviceChips = services.map(s =>
    `<span class="station-service-chip">${esc(s)}</span>`
  ).join("");

  const locationLine = station.system_name
    ? `In system: <strong>${esc(station.system_name)}</strong>`
    : `Deep space (no host system)`;

  // Upgrade list section
  let upgradeSection = "";
  if (hasUpgrades) {
    if (!upgrades) {
      upgradeSection = `
        <div class="section-header" style="margin-top:var(--sp-4);margin-bottom:var(--sp-2)">Ship Upgrades</div>
        <p style="color:var(--text-dim);font-size:var(--font-size-xs)">Loading upgrades…</p>
      `;
    } else if (!upgrades.upgrades?.length) {
      upgradeSection = `
        <div class="section-header" style="margin-top:var(--sp-4);margin-bottom:var(--sp-2)">Ship Upgrades</div>
        <p style="color:var(--text-dim);font-size:var(--font-size-xs)">All available upgrades already installed.</p>
      `;
    } else {
      const credits = upgrades.player_credits ?? 0;
      const rows = upgrades.upgrades.map(u => {
        const canAfford = credits >= u.cost;
        return `
          <div class="station-upgrade-row" data-category="${esc(u.category)}" data-name="${esc(u.name)}">
            <div class="station-upgrade-row__header">
              <span class="station-upgrade-row__name">${esc(u.name)}</span>
              <span class="station-upgrade-row__cost ${canAfford ? "" : "station-upgrade-row__cost--broke"}">${u.cost.toLocaleString()} cr</span>
            </div>
            <div class="station-upgrade-row__cat">${esc(u.category)}</div>
            <div class="station-upgrade-row__desc">${esc(u.description)}</div>
            <button class="btn btn--sm btn--primary btn-buy-upgrade"
                    data-station="${esc(station.name)}"
                    data-category="${esc(u.category)}"
                    data-name="${esc(u.name)}"
                    ${canAfford ? "" : "disabled"}>
              ${canAfford ? "INSTALL" : "TOO EXPENSIVE"}
            </button>
          </div>
        `;
      }).join("");

      upgradeSection = `
        <div class="section-header" style="margin-top:var(--sp-4);margin-bottom:var(--sp-2)">
          Ship Upgrades
          <span class="muted" style="font-size:10px;margin-left:var(--sp-2)">
            Credits: <strong style="color:var(--accent-gold)">${credits.toLocaleString()}</strong>
          </span>
        </div>
        <div class="station-upgrades-list">${rows}</div>
      `;
    }
  }

  return `
    <div style="padding:var(--sp-3)">
      <!-- Header -->
      <div style="border-bottom:1px solid var(--border-accent);padding-bottom:var(--sp-3);margin-bottom:var(--sp-3)">
        <div style="display:flex;align-items:center;gap:var(--sp-2);margin-bottom:var(--sp-1)">
          <span style="color:var(--accent-gold);font-size:1.1em">⊕</span>
          <h3 style="color:var(--accent-gold);letter-spacing:0.12em;font-size:var(--font-size-md);margin:0">
            ${esc(station.name)}
          </h3>
        </div>
        <div style="font-size:var(--font-size-xs);color:var(--text-dim)">${esc(station.type)}</div>
      </div>

      <!-- Stats -->
      <div style="margin-bottom:var(--sp-3)">
        <div class="stat-row">
          <span class="stat-row__label">Location</span>
          <span class="stat-row__value" style="font-size:11px">${locationLine}</span>
        </div>
        ${detail?.upgrade_level ? `
        <div class="stat-row">
          <span class="stat-row__label">Station Level</span>
          <span class="stat-row__value">${detail.upgrade_level} / 5</span>
        </div>` : ""}
      </div>

      <!-- Description -->
      ${station.description ? `
      <div style="font-size:var(--font-size-xs);color:var(--text-dim);line-height:1.5;
                  margin-bottom:var(--sp-3);padding:var(--sp-2);background:var(--bg-secondary);
                  border-left:2px solid var(--accent-gold)">${esc(station.description)}</div>` : ""}

      <!-- Services -->
      <div class="section-header" style="margin-bottom:var(--sp-2)">Services</div>
      <div style="display:flex;flex-wrap:wrap;gap:var(--sp-1);margin-bottom:var(--sp-4)">${serviceChips}</div>

      <!-- Trade button -->
      ${hasMarket ? `
      <button class="btn btn--primary btn-station-trade" style="width:100%;margin-bottom:var(--sp-3)">
        ⬡ OPEN MARKET
      </button>` : ""}

      <!-- Repair hull button — always available at any station when player is here -->
      ${playerHere ? `
      <button class="btn btn--secondary btn-station-repair" style="width:100%;margin-bottom:var(--sp-3)"
              title="Fully restore hull integrity. Cost: 500 cr per damage point.">
        ▲ REPAIR HULL  <span class="muted" style="font-size:10px">(500 cr / pt)</span>
      </button>` : ""}

      <!-- Upgrade section -->
      ${upgradeSection}
    </div>
  `;
}

function _wireStationButtons(content, station, detail, upgrades) {
  // Trade button
  content.querySelector(".btn-station-trade")
    ?.addEventListener("click", async () => {
      try {
        const market = await getMarket(station.name);
        _marketData = market;
        _openMarketModal(station.name, market);
      } catch (err) {
        notify("ERROR", err.message || "Could not load market.");
      }
    });

  // Hull repair button
  content.querySelector(".btn-station-repair")
    ?.addEventListener("click", async () => {
      try {
        const result = await repairShipAtStation(station.name);
        if (result.success) {
          notify("HULL", result.message);
        } else {
          notify("WARN", result.message);
        }
      } catch (err) {
        notify("ERROR", err.message || "Repair failed.");
      }
    });

  // Upgrade buy buttons
  content.querySelectorAll(".btn-buy-upgrade").forEach(btn => {
    btn.addEventListener("click", () =>
      _handleBuyUpgrade(btn, station.name, btn.dataset.category, btn.dataset.name, content, station)
    );
  });
}

async function _handleBuyUpgrade(btn, stationName, category, upgradeName, content, station) {
  const origText = btn.textContent;
  btn.disabled = true;
  btn.textContent = "INSTALLING…";

  try {
    const result = await buyStationUpgrade(stationName, category, upgradeName);
    notify("SHIP", result.message);

    // Refresh the full panel to update credit display and remove installed upgrade
    const [detailRes, upgradesRes] = await Promise.allSettled([
      getStation(stationName),
      getStationUpgrades(stationName),
    ]);
    const newDetail   = detailRes.status   === "fulfilled" ? detailRes.value   : null;
    const newUpgrades = upgradesRes.status === "fulfilled" ? upgradesRes.value : null;
    content.innerHTML = _buildStationPanelHtml(station, newDetail, newUpgrades);
    _wireStationButtons(content, station, newDetail, newUpgrades);
  } catch (err) {
    notify("ERROR", err.message || "Upgrade failed.");
    btn.disabled = false;
    btn.textContent = origText;
  }
}


/** Build the HTML for the system detail panel */
/**
 * Build the coordinates + galactic elevation stat rows for the system panel.
 * Shows raw (x, y, z) and the elevation band derived from the current zStats.
 * @param {object} system - system data object including x, y, z fields
 * @returns {string} HTML
 */
function _coordRowHtml(system) {
  const x = system.x ?? system.coordinates?.[0];
  const y = system.y ?? system.coordinates?.[1];
  const z = system.z ?? system.coordinates?.[2];
  if (x == null || y == null || z == null) return "";

  // Derive layer label + colour from fixed layer boundaries (mirrors LAYER_BANDS in hex-render.js)
  const LAYER_BANDS = [
    { z_min: 5,   z_max: 45,  label: "↓↓ DEEP VOID",  color: "#ff7043" },
    { z_min: 45,  z_max: 85,  label: "↓ LOWER REACHES", color: "#ffb74d" },
    { z_min: 85,  z_max: 125, label: "— GALACTIC PLANE", color: "var(--text-dim)" },
    { z_min: 125, z_max: 165, label: "↑ UPPER REACHES", color: "#4fc3f7" },
    { z_min: 165, z_max: 195, label: "↑↑ HIGH ORBIT",  color: "#00e5ff" },
  ];
  const lb = LAYER_BANDS.find(b => z >= b.z_min && z < b.z_max) || LAYER_BANDS[2];

  const fmt = n => (Math.round(n * 10) / 10).toFixed(1);
  return `
    <div class="stat-row">
      <span class="stat-row__label">Coordinates</span>
      <span class="stat-row__value" style="font-family:var(--font-mono);letter-spacing:0.02em">
        (${fmt(x)},&thinsp;${fmt(y)},&thinsp;${fmt(z)})
      </span>
    </div>
    <div class="stat-row">
      <span class="stat-row__label">Galactic Layer</span>
      <span class="stat-row__value" style="color:${lb.color}">${lb.label}</span>
    </div>
  `;
}


function buildSystemPanelHtml(system, shipCoords) {
  const threatColor = system.threat_level >= 7 ? "var(--accent-red)"
    : system.threat_level >= 4 ? "var(--accent-orange)"
    : "var(--accent-green)";

  // Navigation info: distance from ship to this system
  let navInfoHtml = "";
  let atSystem = false;  // hoisted so planet cards can reference it below
  {
    const shipInfo = state.gameState?.ship;
    const sCoords  = shipInfo?.coordinates ?? shipCoords;
    if (sCoords && system.coordinates) {
      const [sx, sy, sz] = sCoords;
      const [tx, ty, tz] = system.coordinates;
      const dist      = Math.round(Math.sqrt((tx-sx)**2 + (ty-sy)**2 + (tz-sz)**2) * 10) / 10;
      atSystem        = dist < 1.0;
      const jumpRange = shipInfo?.jump_range ?? 15;
      const inRange   = dist <= jumpRange;
      const distColor = atSystem ? "var(--accent-green)" : inRange ? "var(--accent-teal)" : "var(--accent-orange)";
      const curLoc    = shipInfo?.current_system || "Deep Space";
      navInfoHtml = `
        <div style="margin-bottom:var(--sp-3);padding:var(--sp-2) var(--sp-3);background:var(--bg-secondary);
                    border-left:2px solid ${distColor};font-size:var(--font-size-xs)">
          <div style="color:var(--text-dim);text-transform:uppercase;letter-spacing:0.08em;
                      margin-bottom:var(--sp-1)">Navigation</div>
          <div style="display:flex;justify-content:space-between">
            <span style="color:var(--text-dim)">Your location</span>
            <span style="color:var(--text-bright)">${esc(curLoc)}</span>
          </div>
          <div style="display:flex;justify-content:space-between;margin-top:2px">
            <span style="color:var(--text-dim)">Distance</span>
            <span style="color:${distColor}">${atSystem ? "◉ HERE" : dist + " ly"}</span>
          </div>
          ${!atSystem ? `
          <div style="display:flex;justify-content:space-between;margin-top:2px">
            <span style="color:var(--text-dim)">Jump range</span>
            <span style="color:${inRange ? "var(--accent-teal)" : "var(--accent-orange)"}">
              ${inRange ? "✓ In range" : "✗ Out of range"} (${jumpRange} ly max)
            </span>
          </div>` : ""}
        </div>
      `;
    }
  }

  const planets = system.planets || [];
  const planetRows = planets.map(p => `
    <div style="padding:var(--sp-2) var(--sp-3);border:1px solid var(--border-color);
                border-radius:2px;margin-bottom:var(--sp-2);background:var(--bg-tertiary)">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <span style="color:var(--text-bright);font-size:var(--font-size-xs);
                     text-transform:uppercase;letter-spacing:0.06em">${esc(p.name)}</span>
        <div style="display:flex;align-items:center;gap:var(--sp-2)">
          <span style="font-size:var(--font-size-xs);color:var(--text-dim)">${esc(p.subtype)}</span>
          ${p.habitable && p.has_colony
            ? `<button class="btn btn--sm btn--secondary btn-found-colony"
                         data-planet="${esc(p.name)}" data-type="${esc(p.subtype)}">
                 ◉ VISIT COLONY
               </button>`
            : ""}
        </div>
      </div>
      ${p.population > 0
        ? `<div style="font-size:var(--font-size-xs);color:var(--text-dim);margin-top:var(--sp-1)">
             Pop: ${p.population.toLocaleString()}</div>`
        : ""}
      ${p.resources && p.resources.length > 0
        ? `<div style="font-size:var(--font-size-xs);color:var(--text-dim);margin-top:2px">
             ${p.resources.slice(0, 3).join(", ")}</div>`
        : ""}
    </div>
  `).join("") || `<p style="color:var(--text-dim);font-size:var(--font-size-xs)">
    No planets detected.</p>`;

  return `
    <div style="padding:var(--sp-3)">
      <!-- System header -->
      <div style="border-bottom:1px solid var(--border-accent);padding-bottom:var(--sp-3);
                  margin-bottom:var(--sp-3)">
        <h3 style="color:var(--accent-teal);letter-spacing:0.12em;font-size:var(--font-size-md)">
          ${esc(system.name)}
        </h3>
        <div style="font-size:var(--font-size-xs);color:var(--text-dim);margin-top:var(--sp-1)">
          ${esc(system.type || "Unknown Type")}
        </div>
      </div>

      <!-- Stats -->
      <div style="margin-bottom:var(--sp-4)">
        <div class="stat-row">
          <span class="stat-row__label">Population</span>
          <span class="stat-row__value">${(system.population || 0).toLocaleString()}</span>
        </div>
        <div class="stat-row">
          <span class="stat-row__label">Threat Level</span>
          <span class="stat-row__value" style="color:${threatColor}">${system.threat_level ?? "—"}/10</span>
        </div>
        <div class="stat-row">
          <span class="stat-row__label">Resources</span>
          <span class="stat-row__value">${esc(system.resources || "Unknown")}</span>
        </div>
        ${system.controlling_faction ? `
        <div class="stat-row">
          <span class="stat-row__label">Faction</span>
          <button class="btn-faction-link" data-faction="${esc(system.controlling_faction)}">${esc(system.controlling_faction)}</button>
        </div>` : ""}
        ${_coordRowHtml(system)}
      </div>

      <!-- Description -->
      ${system.description ? `
      <div style="font-size:var(--font-size-xs);color:var(--text-dim);line-height:1.5;
                  margin-bottom:var(--sp-4);padding:var(--sp-2);background:var(--bg-secondary);
                  border-left:2px solid var(--border-accent)">
        ${esc(system.description)}
      </div>` : ""}

      <!-- Navigation info (distance, range) -->
      ${navInfoHtml}

      <!-- Enter System button — only shown when player is physically here -->
      ${atSystem ? `
      <button class="btn btn--primary btn--sm btn-enter-system"
              style="width:100%;margin-bottom:var(--sp-4)"
              data-system="${esc(system.name)}">
        &#11042; ENTER SYSTEM
      </button>` : ""}

      <!-- Planets -->
      <div class="section-header" style="margin-bottom:var(--sp-2)">
        Planets (${planets.length})
      </div>
      ${planetRows}

      <!-- NPC Presence — injected asynchronously after getSystemPresence() resolves -->
      <div class="presence-placeholder" style="margin-top:var(--sp-4)"></div>

      <!-- Market button — injected asynchronously, only when player is here -->
      <div class="market-placeholder" style="margin-top:var(--sp-4)"></div>
    </div>
  `;
}


// ---------------------------------------------------------------------------
// NPC Presence section
// ---------------------------------------------------------------------------

/**
 * Populate the .presence-placeholder div with stations, NPC ships, and
 * a TRADE button (if a market is available at this system).
 *
 * @param {HTMLElement} content   - #panel-right-content element
 * @param {object}      presence  - response from GET /api/system/{name}/presence
 */
function _renderPresenceSection(content, presence) {
  const placeholder = content.querySelector(".presence-placeholder");
  if (!placeholder) return;

  const { stations = [], npc_ships = [], npc_colonies = [], has_market = false } = presence;

  // Nothing interesting to show
  if (!stations.length && !npc_ships.length && !npc_colonies.length && !has_market) {
    placeholder.remove();
    return;
  }

  let html = "";

  // Stations
  if (stations.length) {
    const rows = stations.map(s => `
      <div style="padding:var(--sp-2) var(--sp-3);border:1px solid var(--border-dim);
                  border-radius:2px;margin-bottom:var(--sp-1);background:var(--bg-tertiary)">
        <div style="display:flex;justify-content:space-between">
          <span style="color:var(--accent-cyan);font-size:var(--font-size-xs);
                       font-family:var(--font-mono)">${esc(s.name)}</span>
          <span style="font-size:var(--font-size-xs);color:var(--text-dim)">${esc(s.station_type || s.type || "Station")}</span>
        </div>
        ${s.services && s.services.length
          ? `<div style="font-size:11px;color:var(--text-dim);margin-top:2px">${s.services.slice(0,4).join(" · ")}</div>`
          : ""}
      </div>
    `).join("");
    html += `
      <div class="section-header" style="margin-bottom:var(--sp-2)">
        Stations (${stations.length})
      </div>
      ${rows}
    `;
  }

  // NPC colonies (faction-settled planets not owned by player)
  if (npc_colonies.length) {
    const rows = npc_colonies.map(c => `
      <div style="padding:var(--sp-1) var(--sp-3);border-bottom:1px solid var(--border-dim);
                  font-size:var(--font-size-xs)">
        <span style="color:var(--text-primary)">${esc(c.name)}</span>
        <span style="color:var(--text-dim);margin-left:var(--sp-2)">— ${esc(c.controlling_faction || "Unknown")}</span>
        ${c.population ? `<span style="color:var(--text-dim);float:right">Pop: ${c.population.toLocaleString()}</span>` : ""}
      </div>
    `).join("");
    html += `
      <div class="section-header" style="margin-top:var(--sp-3);margin-bottom:var(--sp-2)">
        NPC Colonies (${npc_colonies.length})
      </div>
      <div style="border:1px solid var(--border-dim);border-radius:2px;background:var(--bg-tertiary)">${rows}</div>
    `;
  }

  // NPC ships
  if (npc_ships.length) {
    const rows = npc_ships.map(s => `
      <div style="padding:var(--sp-1) var(--sp-3);border-bottom:1px solid var(--border-dim);
                  font-size:var(--font-size-xs)">
        <span style="color:var(--text-primary)">${esc(s.ship_name || s.name)}</span>
        <span style="color:var(--text-dim);margin-left:var(--sp-2)">— ${esc(s.ship_class || s.type || "Unknown class")}</span>
      </div>
    `).join("");
    html += `
      <div class="section-header" style="margin-top:var(--sp-3);margin-bottom:var(--sp-2)">
        NPC Ships (${npc_ships.length})
      </div>
      <div style="border:1px solid var(--border-dim);border-radius:2px;background:var(--bg-tertiary)">${rows}</div>
    `;
  }

  // Trade button
  if (has_market) {
    html += `
      <button class="btn btn--secondary btn-open-trade"
              style="width:100%;margin-top:var(--sp-3)">
        ⬡ OPEN MARKET
      </button>
    `;
  }

  placeholder.innerHTML = html;
  placeholder.classList.remove("presence-placeholder"); // prevent double-inject
}


/**
 * Switch to the trade view for the given system.
 * Uses a lazy import of main.js to avoid circular dependency.
 */
async function _openTradeView(systemName) {
  const { switchView } = await import("../main.js");
  switchView("trade", { systemName });
}


// ---------------------------------------------------------------------------
// Proximity helpers
// ---------------------------------------------------------------------------

/**
 * Returns true if the player's ship is within 1.5 game-units of targetCoords.
 * Used to gate market visibility — only show a market when the player is there.
 * @param {number[]} targetCoords - [x, y, z]
 */
function _playerIsAt(targetCoords) {
  const ship = state.gameState?.ship;
  if (!ship?.coordinates || !targetCoords) return false;
  const [sx, sy, sz] = ship.coordinates;
  const [tx, ty, tz] = targetCoords;
  return Math.sqrt((tx - sx) ** 2 + (ty - sy) ** 2 + (tz - sz) ** 2) < 1.5;
}

/**
 * Returns true if the player is currently in the named system.
 */
function _playerIsInSystem(systemName) {
  return state.gameState?.ship?.current_system === systemName;
}


// ---------------------------------------------------------------------------
// Market / Trade UI
// ---------------------------------------------------------------------------

/**
 * Replace the .market-placeholder div with a full commodity table once
 * market data has been fetched.
 *
 * @param {string} systemName
 * @param {object} market  - response from GET /api/market/{system}
 */
function _renderMarketSection(systemName, market) {
  const placeholder = document.getElementById("panel-right-content")
                               ?.querySelector(".market-placeholder");
  if (!placeholder) return;

  if (!(market.commodities || []).length) {
    placeholder.remove();
    return;
  }

  // ── Galactic Needs / Shortfall badges ─────────────────────────────────────
  // Show up to 3 shortfalls above the market button so the player can see
  // trade opportunities at a glance without opening the full market modal.
  const shortfalls = market.shortfalls || [];
  const shortfallHtml = shortfalls.length
    ? `<div class="galactic-needs">
        <div class="galactic-needs__label">⚠ GALACTIC NEEDS</div>
        ${shortfalls.map(s => `
          <div class="galactic-needs__row" data-commodity="${esc(s.commodity)}">
            <span class="galactic-needs__name">${esc(s.commodity)}</span>
            <span class="galactic-needs__pct">+${s.pct_above}%</span>
            <span class="galactic-needs__hint">above base</span>
          </div>
        `).join("")}
      </div>`
    : "";

  placeholder.innerHTML = `
    ${shortfallHtml}
    <button class="btn btn--primary" style="width:100%;margin-top:var(--sp-2)" id="btn-open-market">
      ⬡ OPEN MARKET
    </button>
  `;
  placeholder.classList.remove("market-placeholder");
  placeholder.querySelector("#btn-open-market")
    ?.addEventListener("click", () => _openMarketModal(systemName, market));
}


// ---------------------------------------------------------------------------
// Market modal — information-dense redesign
// ---------------------------------------------------------------------------

/**
 * Current sort state for the market table.
 * key: "name" | "price" | "supply" | "demand" | "held"
 * dir: "asc" | "desc"
 */
let _mktSort = { key: "name", dir: "asc" };

/**
 * Current filter for the market table.
 * "all" | "buyable" | "held"
 */
let _mktFilter = "all";


/**
 * Build a small inline percentage bar for supply/demand columns.
 * maxVal is the largest value across all commodities for that column.
 *
 * @param {number} value
 * @param {number} maxVal
 * @param {"supply"|"demand"} kind
 */
function _mktBar(value, maxVal, kind) {
  const pct = maxVal > 0 ? Math.min(100, Math.round((value / maxVal) * 100)) : 0;
  return `<div class="mkt-bar"><div class="mkt-bar__fill mkt-bar__fill--${kind}" style="width:${pct}%"></div></div>`;
}


/**
 * Build the <tbody> rows for the commodity table, respecting the current
 * filter and sort state.  Called both on initial render and after sorting /
 * filtering without re-building the entire modal.
 *
 * @param {string} systemName
 * @param {object[]} commodities  — raw commodity array from the market API
 * @param {number}   credits      — player credits
 * @param {number}   cargoFree    — remaining cargo units
 */
function _buildMarketRows(systemName, commodities, credits, cargoFree) {
  // Compute column maxima for relative bar widths
  const maxSupply = Math.max(...commodities.map(c => c.supply || 0), 1);
  const maxDemand = Math.max(...commodities.map(c => c.demand || 0), 1);

  // Apply active filter
  let visible = commodities;
  if (_mktFilter === "buyable") visible = commodities.filter(c => c.supply > 0 && c.price > 0);
  if (_mktFilter === "held")    visible = commodities.filter(c => c.in_inventory > 0);

  // Apply sort
  visible = [...visible].sort((a, b) => {
    let av, bv;
    switch (_mktSort.key) {
      case "price":  av = a.price;        bv = b.price;        break;
      case "supply": av = a.supply;       bv = b.supply;       break;
      case "demand": av = a.demand;       bv = b.demand;       break;
      case "held":   av = a.in_inventory; bv = b.in_inventory; break;
      default:       av = a.name.toLowerCase(); bv = b.name.toLowerCase();
    }
    if (av < bv) return _mktSort.dir === "asc" ? -1 :  1;
    if (av > bv) return _mktSort.dir === "asc" ?  1 : -1;
    return 0;
  });

  if (!visible.length) {
    return `<tr><td colspan="8" class="mkt-empty">No commodities match the current filter.</td></tr>`;
  }

  return visible.map(c => {
    const price     = c.price ?? 0;
    const sellPrice = Math.round(price * 0.8);
    const canBuy    = price > 0 && c.supply > 0 && cargoFree > 0;
    const canSell   = price > 0 && c.in_inventory > 0;
    // Max buyable: bounded by supply, cargo space, and affordability
    const maxBuy    = canBuy ? Math.min(c.supply, cargoFree, Math.floor(credits / price)) : 0;

    return `
      <tr class="mkt-row${c.in_inventory > 0 ? " mkt-row--held" : ""}"
          data-commodity="${esc(c.name)}">

        <td class="mkt-col__name">${esc(c.name)}</td>

        <td class="mkt-col__price mkt-price--buy">
          ${price > 0 ? price + " ◈" : `<span class="muted">—</span>`}
        </td>

        <td class="mkt-col__price mkt-price--sell">
          ${price > 0 ? sellPrice + " ◈" : `<span class="muted">—</span>`}
        </td>

        <td class="mkt-col__bar">
          <span class="mkt-val">${c.supply}</span>
          ${_mktBar(c.supply, maxSupply, "supply")}
        </td>

        <td class="mkt-col__bar">
          <span class="mkt-val">${c.demand}</span>
          ${_mktBar(c.demand, maxDemand, "demand")}
        </td>

        <td class="mkt-col__held">
          ${c.in_inventory > 0
            ? `<span class="mkt-held">${c.in_inventory}</span>`
            : `<span class="muted">—</span>`}
        </td>

        <td class="mkt-col__action">
          ${canBuy ? `
            <div class="mkt-action-group">
              <input type="number" class="market-qty-input" value="1" min="1" max="${maxBuy}"
                     data-commodity="${esc(c.name)}" data-action="buy">
              <button class="btn btn--xs btn--primary btn-trade"
                      data-system="${esc(systemName)}" data-commodity="${esc(c.name)}"
                      data-action="buy">BUY</button>
              <button class="btn btn--xs btn--ghost btn-max"
                      data-commodity="${esc(c.name)}" data-action="buy"
                      data-max="${maxBuy}" title="Fill to max affordable (${maxBuy})">MAX</button>
            </div>
          ` : `<span class="muted">—</span>`}
        </td>

        <td class="mkt-col__action">
          ${canSell ? `
            <div class="mkt-action-group">
              <input type="number" class="market-qty-input" value="1" min="1" max="${c.in_inventory}"
                     data-commodity="${esc(c.name)}" data-action="sell">
              <button class="btn btn--xs btn--secondary btn-trade"
                      data-system="${esc(systemName)}" data-commodity="${esc(c.name)}"
                      data-action="sell">SELL</button>
              <button class="btn btn--xs btn--ghost btn-max"
                      data-commodity="${esc(c.name)}" data-action="sell"
                      data-max="${c.in_inventory}" title="Sell all (${c.in_inventory})">ALL</button>
            </div>
          ` : `<span class="muted">—</span>`}
        </td>

      </tr>
    `;
  }).join("");
}


/**
 * Build the complete market modal body HTML: stats bar, market intelligence
 * panel, filter tabs, sort-able commodity table.
 *
 * @param {string} systemName
 * @param {object} market  — response from GET /api/market/{system}
 */
function _buildMarketBody(systemName, market) {
  const commodities = market.commodities || [];
  const credits     = market.player_credits ?? state.gameState?.player?.credits ?? 0;
  const cargoUsed   = market.cargo_used ?? 0;
  // Prefer the value returned by the market endpoint; fall back to game state
  const maxCargo    = market.max_cargo  ?? state.gameState?.ship?.max_cargo ?? 0;
  const cargoFree   = maxCargo > 0 ? maxCargo - cargoUsed : 0;
  const bestBuys    = market.best_buys  || [];
  const bestSells   = market.best_sells || [];

  // Net inventory value at sell prices — useful for gauging trade potential
  const invValue = commodities.reduce((sum, c) =>
    sum + (c.in_inventory * Math.round((c.price ?? 0) * 0.8)), 0);

  // Cargo bar colour: red if full, gold if tight, teal otherwise
  const cargoPct   = maxCargo > 0 ? Math.round((cargoUsed / maxCargo) * 100) : 0;
  const cargoColor = cargoPct >= 90 ? "var(--accent-red,#ff4444)"
                   : cargoPct >= 70 ? "var(--accent-gold)"
                   : "var(--accent-teal)";

  // Market intelligence: top recommended buys & sells
  const buyTips = bestBuys.slice(0, 4).map(b =>
    `<span class="mkt-tip mkt-tip--buy">
       ${esc(b.name)} <span class="mkt-tip__price">${b.price}◈</span>
     </span>`
  ).join("");
  const sellTips = bestSells.slice(0, 4).map(s =>
    `<span class="mkt-tip mkt-tip--sell">
       ${esc(s.name)} <span class="mkt-tip__price">${Math.round(s.price * 0.8)}◈</span>
     </span>`
  ).join("");

  // Sort indicator arrows for column headers
  function sortArrow(key) {
    if (_mktSort.key !== key) return `<span class="mkt-sort-arrow mkt-sort-arrow--inactive">⇅</span>`;
    return `<span class="mkt-sort-arrow">${_mktSort.dir === "asc" ? "▲" : "▼"}</span>`;
  }

  // Filter tab counts
  const nAll     = commodities.length;
  const nBuyable = commodities.filter(c => c.supply > 0 && c.price > 0).length;
  const nHeld    = commodities.filter(c => c.in_inventory > 0).length;

  // Flavor text block — shown when the backend supplies market_description
  const flavorHtml = market.market_description ? `
    <div class="mkt-flavor">
      ${market.controlling_faction
        ? `<span class="mkt-flavor__faction">${esc(market.controlling_faction)}</span>`
        : ""}
      <p class="mkt-flavor__text">${esc(market.market_description)}</p>
    </div>` : "";

  return `
    ${flavorHtml}
    <!-- ── Stats bar ──────────────────────────────────────────── -->
    <div class="mkt-stats-bar" id="mkt-stats-bar">

      <div class="mkt-stat">
        <span class="mkt-stat__label">CREDITS</span>
        <span class="mkt-stat__value" style="color:var(--accent-gold)">
          ${credits.toLocaleString()} ◈
        </span>
      </div>

      ${maxCargo > 0 ? `
      <div class="mkt-stat">
        <span class="mkt-stat__label">CARGO</span>
        <span class="mkt-stat__value" style="color:${cargoColor}">
          ${cargoUsed} / ${maxCargo}
        </span>
      </div>
      <div class="mkt-stat">
        <span class="mkt-stat__label">FREE</span>
        <span class="mkt-stat__value">${cargoFree}</span>
      </div>
      ` : ""}

      ${invValue > 0 ? `
      <div class="mkt-stat">
        <span class="mkt-stat__label">INV. VALUE</span>
        <span class="mkt-stat__value" style="color:var(--accent-gold)">
          ${invValue.toLocaleString()} ◈
        </span>
      </div>
      ` : ""}

    </div>

    <!-- ── Market intelligence ───────────────────────────────── -->
    ${(buyTips || sellTips) ? `
    <div class="mkt-intel" id="mkt-intel">
      ${buyTips  ? `<div class="mkt-intel__group">
                     <span class="mkt-intel__label">⊕ BUY</span>${buyTips}
                   </div>` : ""}
      ${sellTips ? `<div class="mkt-intel__group">
                     <span class="mkt-intel__label">⊗ SELL</span>${sellTips}
                   </div>` : ""}
    </div>
    ` : ""}

    <!-- ── Filter tabs ───────────────────────────────────────── -->
    <div class="mkt-filters" id="mkt-filters">
      <button class="mkt-filter-btn${_mktFilter === "all"     ? " active" : ""}"
              data-filter="all">ALL (${nAll})</button>
      <button class="mkt-filter-btn${_mktFilter === "buyable" ? " active" : ""}"
              data-filter="buyable">IN STOCK (${nBuyable})</button>
      <button class="mkt-filter-btn${_mktFilter === "held"    ? " active" : ""}"
              data-filter="held">HELD (${nHeld})</button>
    </div>

    <!-- ── Commodity table ───────────────────────────────────── -->
    <div class="mkt-table-wrap">
      <table class="mkt-table" id="market-modal-table">
        <thead>
          <tr>
            <th class="mkt-th--sortable mkt-th--name" data-sort="name">
              COMMODITY ${sortArrow("name")}
            </th>
            <th class="mkt-th--sortable" data-sort="price">
              BUY ◈ ${sortArrow("price")}
            </th>
            <th>SELL ◈</th>
            <th class="mkt-th--sortable" data-sort="supply">
              SUPPLY ${sortArrow("supply")}
            </th>
            <th class="mkt-th--sortable" data-sort="demand">
              DEMAND ${sortArrow("demand")}
            </th>
            <th class="mkt-th--sortable" data-sort="held">
              HELD ${sortArrow("held")}
            </th>
            <th>BUY</th>
            <th>SELL</th>
          </tr>
        </thead>
        <tbody id="mkt-tbody">
          ${_buildMarketRows(systemName, commodities, credits, cargoFree)}
        </tbody>
      </table>
    </div>
  `;
}


/** Open the market modal for a system. */
function _openMarketModal(systemName, market) {
  // Reset sort/filter to defaults whenever a new market is opened
  _mktSort   = { key: "name", dir: "asc" };
  _mktFilter = "all";

  showModal(`Market — ${systemName}`, _buildMarketBody(systemName, market), [
    { label: "Close", className: "btn--secondary", onClick: () => closeModal() },
  ], { wide: true });

  _wireMarketModal(systemName, market);
}


/**
 * Wire all interactive controls inside the open market modal:
 *   • Buy / Sell trade buttons
 *   • MAX / ALL quick-fill buttons
 *   • Filter tabs (ALL / IN STOCK / HELD)
 *   • Sortable column headers
 *
 * @param {string} systemName
 * @param {object} market — full market object (needed for re-renders on sort/filter)
 */
function _wireMarketModal(systemName, market) {
  const modal = document.getElementById("modal-body");
  if (!modal) return;

  // ── Buy / Sell trade buttons ───────────────────────────────────────────────
  modal.querySelectorAll(".btn-trade").forEach(btn => {
    btn.addEventListener("click", () => {
      const commodity = btn.dataset.commodity;
      const action    = btn.dataset.action;
      const system    = btn.dataset.system;
      const qtyInput  = modal.querySelector(
        `.market-qty-input[data-commodity="${CSS.escape(commodity)}"][data-action="${action}"]`
      );
      const qty = parseInt(qtyInput?.value || "1", 10);
      _doTrade(system, commodity, action, qty, btn, systemName);
    });
  });

  // ── MAX / ALL quick-fill buttons ───────────────────────────────────────────
  modal.querySelectorAll(".btn-max").forEach(btn => {
    btn.addEventListener("click", () => {
      const commodity = btn.dataset.commodity;
      const action    = btn.dataset.action;
      const max       = parseInt(btn.dataset.max || "1", 10);
      const qtyInput  = modal.querySelector(
        `.market-qty-input[data-commodity="${CSS.escape(commodity)}"][data-action="${action}"]`
      );
      if (qtyInput) qtyInput.value = max;
    });
  });

  // ── Filter tabs ────────────────────────────────────────────────────────────
  modal.querySelectorAll(".mkt-filter-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      _mktFilter = btn.dataset.filter;
      // Update active class
      modal.querySelectorAll(".mkt-filter-btn").forEach(b =>
        b.classList.toggle("active", b.dataset.filter === _mktFilter)
      );
      // Rebuild only the tbody
      const tbody = document.getElementById("mkt-tbody");
      const credits   = market.player_credits ?? state.gameState?.player?.credits ?? 0;
      const maxCargo  = market.max_cargo ?? state.gameState?.ship?.max_cargo ?? 0;
      const cargoUsed = market.cargo_used ?? 0;
      const cargoFree = maxCargo > 0 ? maxCargo - cargoUsed : 0;
      if (tbody) {
        tbody.innerHTML = _buildMarketRows(systemName, market.commodities || [], credits, cargoFree);
        _wireMarketModal(systemName, market);
      }
    });
  });

  // ── Sortable column headers ────────────────────────────────────────────────
  modal.querySelectorAll(".mkt-th--sortable").forEach(th => {
    th.addEventListener("click", () => {
      const key = th.dataset.sort;
      if (_mktSort.key === key) {
        // Toggle direction
        _mktSort.dir = _mktSort.dir === "asc" ? "desc" : "asc";
      } else {
        _mktSort = { key, dir: "asc" };
      }
      // Rebuild thead + tbody to update sort arrows
      const credits   = market.player_credits ?? state.gameState?.player?.credits ?? 0;
      const maxCargo  = market.max_cargo ?? state.gameState?.ship?.max_cargo ?? 0;
      const cargoUsed = market.cargo_used ?? 0;
      const cargoFree = maxCargo > 0 ? maxCargo - cargoUsed : 0;
      const tbody = document.getElementById("mkt-tbody");
      if (tbody) {
        tbody.innerHTML = _buildMarketRows(systemName, market.commodities || [], credits, cargoFree);
      }
      // Update sort arrows in all header cells
      modal.querySelectorAll(".mkt-th--sortable").forEach(h => {
        const arrow = h.querySelector(".mkt-sort-arrow");
        if (!arrow) return;
        if (h.dataset.sort === _mktSort.key) {
          arrow.textContent = _mktSort.dir === "asc" ? "▲" : "▼";
          arrow.classList.remove("mkt-sort-arrow--inactive");
        } else {
          arrow.textContent = "⇅";
          arrow.classList.add("mkt-sort-arrow--inactive");
        }
      });
      // Re-wire new rows
      _wireMarketModal(systemName, market);
    });
  });
}


/**
 * Execute a buy or sell trade action, then refresh the market modal in-place.
 *
 * @param {string}      systemName
 * @param {string}      commodity
 * @param {"buy"|"sell"} action
 * @param {number}      quantity
 * @param {HTMLElement} btn   — button that was clicked (for loading state)
 */
async function _doTrade(systemName, commodity, action, quantity, btn) {
  if (!quantity || quantity < 1) {
    notify("ERROR", "Enter a quantity of at least 1.");
    return;
  }

  const origText  = btn.textContent;
  btn.disabled    = true;
  btn.textContent = action === "buy" ? "BUYING…" : "SELLING…";

  try {
    const fn     = action === "buy" ? buyGoods : sellGoods;
    const result = await fn(systemName, commodity, quantity);

    notify("TRADE", result.message || `${action.toUpperCase()} complete.`);

    // If this sale filled a Galactic Need, surface a separate high-priority
    // notification so the player understands the bonus they earned.
    if (result.shortfall_filled && result.shortfall_bonus > 0) {
      notify(
        "NEED FILLED",
        `${result.shortfall_commodity} shortage resolved. `
        + `Bonus: +${result.shortfall_bonus} cr · Faction relations improved.`,
      );
    }

    // Sync credits into local game state immediately so the HUD updates
    if (state.gameState?.player) {
      state.gameState.player.credits = result.credits_remaining;
    }

    // Re-fetch fresh market data then rebuild the entire modal body in-place
    _marketData = await getMarket(systemName);
    const modalBody = document.getElementById("modal-body");
    if (modalBody) {
      modalBody.innerHTML = _buildMarketBody(systemName, _marketData);
      _wireMarketModal(systemName, _marketData);
    }

  } catch (err) {
    notify("ERROR", err.message || "Trade failed.");
    btn.disabled    = false;
    btn.textContent = origText;
  }
}


// ---------------------------------------------------------------------------
// Galaxy map refresh — called after any movement so newly-scanned systems,
// stations, and deep-space objects become visible immediately.
// ---------------------------------------------------------------------------

async function _refreshGalaxyMap() {
  try {
    const result = await getGalaxyMap();
    state.galaxyMap        = result.systems            || [];
    state.stationsData     = result.stations           || [];
    state.deepSpaceObjects = result.deep_space_objects || [];
    systemsData  = state.galaxyMap;
    stationsData = state.stationsData;
    dsoData      = state.deepSpaceObjects;
    isDirty = true;
  } catch (_err) {
    // Non-fatal — map stays stale until the next jump or remount
  }
}


// ---------------------------------------------------------------------------
// Auto end-turn after movement
// ---------------------------------------------------------------------------

/**
 * Called after every successful jump/move.  Triggers end-of-turn processing
 * so that each move costs one turn.  Updates HUD state and shows GNN/events
 * the same way the manual End Turn button does.
 */
async function _endTurnAfterMove() {
  try {
    const { handleEndTurn } = await import("../main.js");
    await handleEndTurn();
  } catch (_err) {
    // Non-fatal: game continues, player can end turn manually
  }
}


// ---------------------------------------------------------------------------
// Jump action
// ---------------------------------------------------------------------------

async function handleJump(system) {
  try {
    const [sx, sy, sz] = system.coordinates ?? [system.x, system.y, system.z];
    const result = await jumpToCoords(sx, sy, sz);

    if (result.success) {
      notify("NAV", `Arrived at ${system.name}.  Fuel: ${result.fuel_remaining}`);

      // Update ship coordinates in state immediately so the marker moves
      // without waiting for the 1-second polling loop to catch up.
      if (state.gameState?.ship && result.new_coords) {
        state.gameState.ship.coordinates = result.new_coords;
      }

      state.selectedSystem = { ...state.selectedSystem, visited: true };

      // Re-fetch the galaxy map so systems, stations, and DSOs that just
      // entered scan range become visible without needing to remount.
      await _refreshGalaxyMap();

      // Each jump costs one turn
      await _endTurnAfterMove();
    } else {
      notify("ERROR", result.message || "Jump failed.");
    }
  } catch (err) {
    notify("ERROR", `Jump failed: ${err.message}`);
  }
}


// ---------------------------------------------------------------------------
// Deep space move action
// ---------------------------------------------------------------------------

/**
 * Jump to an empty hex (no system, possibly a DSO).
 * After arrival, if the backend reports a deep_space_object, show its panel.
 */
async function handleDeepSpaceMove(q, r) {
  try {
    const { x, y, z } = hexToGalaxyCoords(q, r);
    const result = await jumpToCoords(x, y, z);

    if (result.success) {
      // Update ship position immediately
      if (state.gameState?.ship && result.new_coords) {
        state.gameState.ship.coordinates = result.new_coords;
      }

      const dso = result.deep_space_object;

      // Re-fetch the galaxy map so newly-scanned objects appear immediately.
      await _refreshGalaxyMap();

      if (dso) {
        notify("NAV", `Arrived at ${dso.name || dso.subtype || "deep space"}.  Fuel: ${result.fuel_remaining}`);
        if (dso.type === "derelict" && !dso.depleted) {
          await _triggerDerelictEncounter(dso, q, r);
        } else {
          showDsoPanel({ ...dso, hex_q: q, hex_r: r }, q, r);
        }
      } else {
        notify("NAV", `Entered deep space at (${q}, ${r}).  Fuel: ${result.fuel_remaining}`);
        showEmptyHexPanel(q, r);
      }

      // Each move costs one turn
      await _endTurnAfterMove();
    } else {
      notify("ERROR", result.message || "Move failed.");
    }
  } catch (err) {
    notify("ERROR", `Move failed: ${err.message}`);
  }
}


// ---------------------------------------------------------------------------
// Derelict encounter — automatic random resolution
// ---------------------------------------------------------------------------

const OUTCOME_ICONS = {
  salvage:         "⊘",
  explore:         "◎",
  combat_skirmish: "⚡",
  hazard:          "⚠",
};

async function _triggerDerelictEncounter(dso, q, r) {
  const { showModal, closeModal } = await import("../ui/modal.js");

  // Show "scanning..." immediately while we wait for the API
  showModal(
    `⊘ ${esc(dso.name || dso.subtype || "DERELICT")}`,
    `<div style="color:var(--text-dim);text-align:center;padding:var(--sp-6) 0">
       Scanning wreck…
     </div>`,
    [],
    { wide: true }
  );

  let result;
  try {
    result = await encounterDerelict();
  } catch (err) {
    closeModal();
    notify("ERROR", `Encounter failed: ${err.message}`);
    showDsoPanel({ ...dso, hex_q: q, hex_r: r }, q, r);
    return;
  }

  // Update local DSO cache to depleted
  const cached = dsoData.find(d => d.hex_q === q && d.hex_r === r);
  if (cached) cached.depleted = true;
  if (state.gameState?.player) state.gameState.player.credits = result.credits;
  isDirty = true;

  // Build loot summary
  const lootParts = [];
  if (result.credits_gained > 0) lootParts.push(`${result.credits_gained.toLocaleString()} cr`);
  for (const [k, v] of Object.entries(result.cargo_added || {})) {
    if (v > 0) lootParts.push(`${v} ${k.replace(/_/g, " ")}`);
    else if (v < 0) lootParts.push(`<span style="color:var(--accent-red)">${Math.abs(v)} ${k.replace(/_/g, " ")} lost</span>`);
  }
  const lootHtml = lootParts.length
    ? `<div class="encounter-loot">${lootParts.join("  ·  ")}</div>`
    : "";

  const researchHtml = result.research_gained > 0
    ? `<div class="encounter-research">◎ +${result.research_gained} research progress</div>`
    : "";

  const hullHtml = result.hull_damage > 0
    ? `<div class="encounter-hull-warn">Hull integrity −${result.hull_damage.toFixed(1)}</div>`
    : "";

  const outcomeIcon = OUTCOME_ICONS[result.outcome_type] || "·";
  const color = result.outcome_type === "hazard"    ? "var(--accent-red)"
              : result.outcome_type === "combat_skirmish" ? "var(--accent-orange)"
              : result.outcome_type === "explore"    ? "rgba(0,170,255,0.9)"
              : "var(--accent-green)";

  const body = `
    <div class="encounter-modal">
      <p class="encounter-opening">${esc(result.opening)}</p>
      <div class="encounter-divider"></div>
      <div class="encounter-outcome" style="border-left-color:${color}">
        <div class="encounter-outcome__title" style="color:${color}">
          ${outcomeIcon} ${esc(result.outcome_title)}
        </div>
        <p class="encounter-outcome__text">${esc(result.outcome_narrative)}</p>
        ${lootHtml}
        ${researchHtml}
        ${hullHtml}
      </div>
    </div>
  `;

  showModal(
    `⊘ ${esc(dso.name || dso.subtype || "DERELICT")}`,
    body,
    [{ label: "CLOSE", className: "btn--secondary", onClick: () => {
      closeModal();
      showDsoPanel({ ...dso, hex_q: q, hex_r: r, depleted: true }, q, r);
    }}],
    { wide: true }
  );
}


// ---------------------------------------------------------------------------
// Deep space harvest/salvage action
// ---------------------------------------------------------------------------

async function handleDsoHarvest(dso) {
  const btn = document.querySelector(".btn-dso-harvest");
  if (btn) { btn.disabled = true; btn.textContent = "HARVESTING..."; }

  try {
    const result = await harvestDeepSpace();
    if (result.success) {
      const parts = [];
      if (result.credits_gained > 0) parts.push(`${result.credits_gained} cr`);
      for (const [k, v] of Object.entries(result.cargo_added || {})) {
        parts.push(`${v} ${k}`);
      }
      notify("NAV", `Salvage complete: ${parts.join(", ") || "nothing found"}.`);

      if (state.gameState?.player) {
        state.gameState.player.credits = result.credits;
      }

      // Mark as depleted in local cache
      const dsoQ = dso.hex_q;
      const dsoR = dso.hex_r;
      const cached = dsoData.find(d => d.hex_q === dsoQ && d.hex_r === dsoR);
      if (cached) cached.depleted = true;

      isDirty = true;
      // Refresh the panel to show depleted state
      showDsoPanel({ ...dso, depleted: true }, dsoQ, dsoR);
    }
  } catch (err) {
    notify("ERROR", err.message || "Harvest failed.");
    if (btn) { btn.disabled = false; btn.textContent = dso.type === "derelict" ? "⊘ SALVAGE" : "◈ HARVEST"; }
  }
}


// ---------------------------------------------------------------------------
// Deep space outpost action (stub)
// ---------------------------------------------------------------------------

async function handleDsoOutpost() {
  try {
    const result = await foundDeepSpaceOutpost();
    notify("NAV", result.message || "Outpost system unavailable.");
  } catch (err) {
    notify("ERROR", err.message || "Outpost unavailable.");
  }
}


// ---------------------------------------------------------------------------
// Found colony — navigate to the colony surface view (Phase 3)
// ---------------------------------------------------------------------------

async function handleFoundColony(systemName, planetName, planetType) {
  // Store the selected planet so the C shortcut can return here
  state.selectedPlanet = { planetName, systemName, planetType };

  // Lazy import to avoid circular dependency (galaxy imports main, main imports galaxy)
  const { switchView } = await import("../main.js");
  switchView("colony", { planetName, systemName, planetType });
}


// ---------------------------------------------------------------------------
// Tiny HTML escape helper
// ---------------------------------------------------------------------------

function esc(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}


// ---------------------------------------------------------------------------
// Close button wire-up (called once by panels.js in Phase 2)
// ---------------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {
  const closeBtn = document.getElementById("panel-right-close");
  if (closeBtn) {
    closeBtn.addEventListener("click", () => {
      viewState.selectedSystemName = null;
      state.selectedSystem = null;
      showDefaultPanel();
      isDirty = true;
    });
  }
});
