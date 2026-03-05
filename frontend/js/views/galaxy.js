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
         getStation, getStationUpgrades, buyStationUpgrade } from "../api.js";
import { notify }             from "../ui/notifications.js";
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
  return {
    q: Math.round(coords[0] / GALAXY_SCALE),
    r: Math.round(coords[1] / GALAXY_SCALE),
  };
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

// View transform
let viewState = { panX: 0, panY: 0, zoom: 1.0, selectedSystemName: null, selectedStationName: null };

/** Cached market data for the currently selected system. */
let _marketData = null;


// ---------------------------------------------------------------------------
// Exported view object
// ---------------------------------------------------------------------------

export const galaxyView = {

  async mount(context) {
    const canvas = document.getElementById("galaxy-canvas");
    if (!canvas) return;

    // Fetch galaxy map data (or use cache)
    if (state.galaxyMap.length === 0) {
      try {
        const result = await getGalaxyMap();
        state.galaxyMap = result.systems || [];
        state.stationsData = result.stations || [];
      } catch (err) {
        notify("ERROR", `Could not load galaxy map: ${err.message}`);
        return;
      }
    }
    systemsData  = state.galaxyMap;
    stationsData = state.stationsData || [];

    // If a system was pre-selected (e.g. returning from colony view), re-apply it
    if (state.selectedSystem) {
      viewState.selectedSystemName = state.selectedSystem.name;
      showSystemPanel(state.selectedSystem);
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
      const shipCoords = state.gameState?.ship?.coordinates;
      const shipHex    = shipCoordsToHex(shipCoords);

      renderGalaxyMap(
        canvas,
        systemsData,
        { ...viewState, shipHex, stations: stationsData },
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
    // Clicked empty space — deselect
    viewState.selectedSystemName  = null;
    viewState.selectedStationName = null;
    state.selectedSystem = null;
    hideRightPanel();
    isDirty = true;
    return;
  }

  // Select the system
  viewState.selectedSystemName  = sys.name;
  viewState.selectedStationName = null;
  state.selectedSystem = sys;
  isDirty = true;

  // Fetch detailed system data (planets, market, etc.)
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

  // Wire jump button
  const jumpBtn = content.querySelector(".btn-jump");
  if (jumpBtn) {
    jumpBtn.addEventListener("click", () => handleJump(system));
  }

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

  // Inject NPC presence section
  const presence = presenceResult.status === "fulfilled" ? presenceResult.value : null;
  if (presence) {
    _renderPresenceSection(content, presence);
    // Wire TRADE button if market exists
    if (presence.has_market) {
      content.querySelector(".btn-open-trade")
        ?.addEventListener("click", () => _openTradeView(system.name));
    }
  } else {
    content.querySelector(".presence-placeholder")?.remove();
  }

  // Inject market section
  if (marketResult.status === "fulfilled") {
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
  const hasMarket   = detail ? detail.has_market   : services.some(s => ["Market","Ore Processing","Luxury Goods"].includes(s));
  const hasUpgrades = detail ? detail.has_upgrades : services.includes("Ship Upgrades");

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

      <!-- Upgrade section -->
      ${upgradeSection}
    </div>
  `;
}

function _wireStationButtons(content, station, detail, upgrades) {
  // Trade button
  content.querySelector(".btn-station-trade")
    ?.addEventListener("click", () => _openTradeView(station.name));

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
function buildSystemPanelHtml(system, shipCoords) {
  const threatColor = system.threat_level >= 7 ? "var(--accent-red)"
    : system.threat_level >= 4 ? "var(--accent-orange)"
    : "var(--accent-green)";

  const planets = system.planets || [];
  const planetRows = planets.map(p => `
    <div style="padding:var(--sp-2) var(--sp-3);border:1px solid var(--border-color);
                border-radius:2px;margin-bottom:var(--sp-2);background:var(--bg-tertiary)">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <span style="color:var(--text-bright);font-size:var(--font-size-xs);
                     text-transform:uppercase;letter-spacing:0.06em">${esc(p.name)}</span>
        <span style="font-size:var(--font-size-xs);color:var(--text-dim)">${esc(p.subtype)}</span>
      </div>
      ${p.population > 0
        ? `<div style="font-size:var(--font-size-xs);color:var(--text-dim);margin-top:var(--sp-1)">
             Pop: ${p.population.toLocaleString()}</div>`
        : ""}
      ${p.resources && p.resources.length > 0
        ? `<div style="font-size:var(--font-size-xs);color:var(--text-dim);margin-top:2px">
             ${p.resources.slice(0, 3).join(", ")}</div>`
        : ""}
      ${p.habitable
        ? `<button class="btn btn--sm btn--primary btn-found-colony"
                   style="margin-top:var(--sp-2);width:100%"
                   data-planet="${esc(p.name)}" data-type="${esc(p.subtype)}">
             ⊕ FOUND COLONY
           </button>`
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
          <span class="stat-row__value" style="color:var(--accent-cyan)">${esc(system.controlling_faction)}</span>
        </div>` : ""}
      </div>

      <!-- Description -->
      ${system.description ? `
      <div style="font-size:var(--font-size-xs);color:var(--text-dim);line-height:1.5;
                  margin-bottom:var(--sp-4);padding:var(--sp-2);background:var(--bg-secondary);
                  border-left:2px solid var(--border-accent)">
        ${esc(system.description)}
      </div>` : ""}

      <!-- Jump button -->
      <button class="btn btn--primary btn-jump" style="width:100%;margin-bottom:var(--sp-4)">
        ▶ JUMP TO SYSTEM
      </button>

      <!-- Planets -->
      <div class="section-header" style="margin-bottom:var(--sp-2)">
        Planets (${planets.length})
      </div>
      ${planetRows}

      <!-- NPC Presence — injected asynchronously after getSystemPresence() resolves -->
      <div class="presence-placeholder" style="margin-top:var(--sp-4)"></div>

      <!-- Market — injected asynchronously after getMarket() resolves -->
      <div class="market-placeholder" style="margin-top:var(--sp-4)">
        <div class="section-header" style="margin-bottom:var(--sp-2)">Market</div>
        <p style="color:var(--text-dim);font-size:var(--font-size-xs)">Loading market data…</p>
      </div>
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

  const commodities = market.commodities || [];
  const credits     = market.player_credits ?? state.gameState?.player?.credits ?? 0;

  if (!commodities.length) {
    placeholder.innerHTML = `
      <div class="section-header" style="margin-bottom:var(--sp-2)">Market</div>
      <p style="color:var(--text-dim);font-size:var(--font-size-xs)">No commodities traded here.</p>
    `;
    return;
  }

  // Build the commodity rows.
  // The backend returns a single "price" per commodity.
  // Sell price is conventionally 80% of buy price (handled server-side).
  const rows = commodities.map(c => {
    const price     = c.price ?? 0;
    const sellEst   = Math.round(price * 0.8);
    const canBuy    = price > 0 && c.supply > 0;
    const canSell   = price > 0 && c.in_inventory > 0;
    return `
      <div class="market-row" data-commodity="${esc(c.name)}">
        <div class="market-row__name">${esc(c.name)}</div>
        <div class="market-row__prices">
          <span style="color:var(--accent-teal)">${canBuy ? price + " ⊕" : "—"}</span>
          <span style="color:var(--accent-gold)">${price > 0 ? sellEst + " ⊗" : "—"}</span>
        </div>
        <div class="market-row__stock muted">${c.supply ?? "—"} in stock</div>
        ${c.in_inventory > 0
          ? `<div class="market-row__held muted">Holding: ${c.in_inventory}</div>`
          : ""}
        <div class="market-row__actions">
          ${canBuy ? `
            <input type="number" class="market-qty-input" value="1" min="1"
                   data-commodity="${esc(c.name)}" data-action="buy"
                   title="Quantity to buy" style="width:44px">
            <button class="btn btn--sm btn--primary btn-trade"
                    data-system="${esc(systemName)}"
                    data-commodity="${esc(c.name)}" data-action="buy">BUY</button>
          ` : ""}
          ${canSell ? `
            <input type="number" class="market-qty-input" value="1" min="1"
                   max="${c.in_inventory}"
                   data-commodity="${esc(c.name)}" data-action="sell"
                   title="Quantity to sell" style="width:44px">
            <button class="btn btn--sm btn--secondary btn-trade"
                    data-system="${esc(systemName)}"
                    data-commodity="${esc(c.name)}" data-action="sell">SELL</button>
          ` : ""}
        </div>
      </div>
    `;
  }).join("");

  placeholder.innerHTML = `
    <div class="section-header" style="margin-bottom:var(--sp-2)">
      Market
      <span class="muted" style="font-size:10px;margin-left:var(--sp-2)">
        Credits: <strong style="color:var(--accent-gold)">${credits.toLocaleString()}</strong>
      </span>
    </div>
    <div class="market-table">${rows}</div>
  `;
  placeholder.classList.remove("market-placeholder"); // prevent double-inject

  // Wire trade buttons — each button reads its sibling qty input
  placeholder.querySelectorAll(".btn-trade").forEach(btn => {
    btn.addEventListener("click", () => {
      const action    = btn.dataset.action;
      const commodity = btn.dataset.commodity;
      const system    = btn.dataset.system;
      // Find the qty input that matches this button's commodity+action
      const qtyInput  = placeholder.querySelector(
        `.market-qty-input[data-commodity="${CSS.escape(commodity)}"][data-action="${action}"]`
      );
      const qty = parseInt(qtyInput?.value || "1", 10);
      _doTrade(system, commodity, action, qty, btn);
    });
  });
}


/**
 * Execute a buy or sell trade action, then refresh the market section.
 *
 * @param {string} systemName
 * @param {string} commodity
 * @param {"buy"|"sell"} action
 * @param {number} quantity
 * @param {HTMLElement} btn   The button that was clicked (for disabled feedback)
 */
async function _doTrade(systemName, commodity, action, quantity, btn) {
  if (!quantity || quantity < 1) {
    notify("ERROR", "Enter a quantity of at least 1.");
    return;
  }

  const origText = btn.textContent;
  btn.disabled   = true;
  btn.textContent = action === "buy" ? "BUYING…" : "SELLING…";

  try {
    const fn     = action === "buy" ? buyGoods : sellGoods;
    const result = await fn(systemName, commodity, quantity);

    notify("TRADE", result.message || `${action.toUpperCase()} complete.`);

    // Update credits in local state immediately so HUD reflects the change
    if (state.gameState?.player) {
      state.gameState.player.credits = result.credits_remaining;
    }

    // Re-fetch market and refresh the section so prices/stock are up-to-date
    _marketData = await getMarket(systemName);
    _renderMarketSection(systemName, _marketData);

  } catch (err) {
    notify("ERROR", err.message || "Trade failed.");
    btn.disabled   = false;
    btn.textContent = origText;
  }
}


// ---------------------------------------------------------------------------
// Jump action
// ---------------------------------------------------------------------------

async function handleJump(system) {
  const btn = document.querySelector(".btn-jump");
  if (btn) { btn.disabled = true; btn.textContent = "JUMPING..."; }

  try {
    const [sx, sy, sz] = system.coordinates ?? [system.x, system.y, system.z];
    const result = await jumpToCoords(sx, sy, sz);

    if (result.success) {
      notify("NAV", `Arrived at ${system.name}.  Fuel: ${result.fuel_remaining}`);

      // Update the visited flag in our local cache
      const cached = systemsData.find(s => s.name === system.name);
      if (cached) cached.visited = true;

      // Update ship coordinates in state immediately so the marker moves
      // without waiting for the 1-second polling loop to catch up.
      if (state.gameState?.ship && result.new_coords) {
        state.gameState.ship.coordinates = result.new_coords;
      }

      // Refresh state
      state.selectedSystem = { ...state.selectedSystem, visited: true };
      isDirty = true;
    } else {
      notify("ERROR", result.message || "Jump failed.");
    }
  } catch (err) {
    notify("ERROR", `Jump failed: ${err.message}`);
  } finally {
    if (btn) { btn.disabled = false; btn.textContent = "▶ JUMP TO SYSTEM"; }
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
      hideRightPanel();
      isDirty = true;
    });
  }
});
