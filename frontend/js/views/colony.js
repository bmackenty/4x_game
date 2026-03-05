/**
 * frontend/js/views/colony.js — Planet colony surface view.
 *
 * Renders the hex tile grid for a colonised planet (the Alpha Centauri "city"
 * view).  Players can:
 *   • Found a new colony on a habitable planet they haven't settled yet.
 *   • Click tiles to inspect terrain and current improvement.
 *   • Build improvements from a catalogue that respects research gates.
 *   • Demolish existing improvements for a 50 % credit refund.
 *
 * Context passed to mount():
 *   { planetName: string, systemName: string, planetType: string }
 *
 * The view wires into the same hex rendering pipeline as the galaxy map
 * (renderColonyMap + attachHexInput) but with a larger hex size (32 px).
 */

import { state }         from "../state.js";
import {
    getColony,
    foundColony,
    buildImprovement,
    demolishImprovement,
    upgradeImprovement,
    getImprovementsCatalogue,
} from "../api.js";
import { renderColonyMap, PLANET_HEX_SIZE } from "../hex/hex-render.js";
import { attachHexInput }                    from "../hex/hex-input.js";
import { showModal, closeModal, confirm }     from "../ui/modal.js";
import { notify }                             from "../ui/notifications.js";


// ---------------------------------------------------------------------------
// Module-level view state
// (reset to null on unmount so stale data never bleeds into a new session)
// ---------------------------------------------------------------------------

/** Full colony object returned by the API */
let _colony = null;

/** Canvas element for the colony hex grid */
let _canvas = null;

/** hex-input controls handle (returned by attachHexInput) */
let _hexInput = null;

/** requestAnimationFrame ID for the render loop */
let _rafId = null;

/** Dirty flag — set true to schedule a repaint */
let _dirty = true;

/** The tile the player has clicked (full tile object from _colony.tiles) */
let _selectedTile = null;

/** Improvement catalogue (fetched once per colony visit) */
let _catalogue = [];

/** Planet context stored so we can found a colony if needed */
let _context = {};


// ---------------------------------------------------------------------------
// Public view object
// ---------------------------------------------------------------------------

export const colonyView = {

    /**
     * Mount the colony view.
     *
     * @param {object} context - { planetName, systemName, planetType }
     */
    async mount(context = {}) {
        _context = context;
        const { planetName = "Unknown", systemName = "" } = context;

        const container = document.getElementById("view-colony");
        if (!container) return;

        // Render the static chrome (panels, canvas, back button)
        container.innerHTML = _buildChrome(planetName, systemName);

        _canvas = document.getElementById("colony-canvas");

        // Wire "Back to Galaxy" button (lazy import avoids circular dep)
        document.getElementById("colony-back-btn")
            ?.addEventListener("click", async () => {
                const { switchView } = await import("../main.js");
                switchView("galaxy");
            });

        // Fetch colony data (or null if not yet founded)
        await _loadColony();

        // Fetch improvement catalogue (needed for build menu whether or not
        // the colony exists, so "Found Colony" prompt can show costs too)
        try {
            const cat = await getImprovementsCatalogue();
            _catalogue = cat.improvements || [];
        } catch (e) {
            _catalogue = [];
            console.warn("[colony] Could not load improvements catalogue:", e);
        }

        if (_colony) {
            // Colony exists — show the hex grid
            _setupCanvas();
            _renderInfoPanel();
        } else {
            // No colony yet — show a found-colony prompt
            _renderFoundPrompt();
        }
    },

    unmount() {
        // Stop animation loop and remove input listeners
        if (_rafId) {
            cancelAnimationFrame(_rafId);
            _rafId = null;
        }
        if (_hexInput) {
            _hexInput.detach();
            _hexInput = null;
        }
        _colony       = null;
        _selectedTile = null;
        _dirty        = true;
        _catalogue    = [];
        _context      = {};
    },
};


// ---------------------------------------------------------------------------
// Data loading
// ---------------------------------------------------------------------------

/**
 * Fetch colony data from the API.
 * Sets _colony to the response dict on success, or null if not found (404).
 */
async function _loadColony() {
    const { planetName } = _context;
    if (!planetName) return;

    try {
        const data = await getColony(planetName);
        _colony = data;
    } catch (err) {
        if (err.status === 404 || err.message?.includes("404")) {
            // Planet not yet colonised — this is normal
            _colony = null;
        } else {
            notify("ERROR", `Could not load colony data: ${err.message}`);
            _colony = null;
        }
    }
}


// ---------------------------------------------------------------------------
// Canvas + render loop
// ---------------------------------------------------------------------------

/**
 * Attach hex input, start the render loop, and wire up the right panel.
 */
function _setupCanvas() {
    if (!_canvas || !_colony) return;

    // Make sure canvas pixel size matches CSS size
    _canvas.width  = _canvas.clientWidth  || 600;
    _canvas.height = _canvas.clientHeight || 500;

    // Attach pan/zoom/click input (same system used for galaxy)
    _hexInput = attachHexInput(_canvas, {
        hexSize:       PLANET_HEX_SIZE,
        onHexClick:    _onTileClick,
        onHexHover:    _onTileHover,
        onViewChanged: () => { _dirty = true; },
    });

    // Start the render loop
    function loop() {
        if (_dirty) {
            _dirty = false;
            renderColonyMap(
                _canvas,
                _colony.tiles,
                _hexInput.viewState
            );
        }
        _rafId = requestAnimationFrame(loop);
    }
    _rafId = requestAnimationFrame(loop);
}

/**
 * Force a canvas repaint on the next frame.
 */
function _requestRedraw() {
    _dirty = true;
}


// ---------------------------------------------------------------------------
// Tile interaction
// ---------------------------------------------------------------------------

/**
 * Called when the player clicks a tile.
 * Finds the tile data and updates the right panel with tile info + build menu.
 *
 * @param {{ q: number, r: number }} hex
 */
function _onTileClick({ q, r }) {
    if (!_colony) return;

    // Find the clicked tile in the colony's tile list
    const tile = _colony.tiles.find(t => t.q === q && t.r === r) || null;
    _selectedTile = tile;

    if (tile) {
        _renderTilePanel(tile);
    }
    _requestRedraw();
}

/**
 * Called when the mouse hovers over a tile.
 * Updates a lightweight tooltip in the status bar (bottom of canvas).
 *
 * @param {{ q: number, r: number }} hex
 */
function _onTileHover({ q, r }) {
    if (!_colony) return;
    const tile = _colony.tiles.find(t => t.q === q && t.r === r);
    const statusEl = document.getElementById("colony-status-bar");
    if (!statusEl) return;

    if (tile) {
        const prod = tile.production && Object.keys(tile.production).length > 0
            ? Object.entries(tile.production).map(([k, v]) => `+${v} ${k}`).join(", ")
            : "no production";
        statusEl.textContent = `${tile.terrain}${tile.improvement ? ` — ${tile.improvement}` : ""} (${prod})`;
    } else {
        statusEl.textContent = "";
    }
}


// ---------------------------------------------------------------------------
// Right panel rendering
// ---------------------------------------------------------------------------

/**
 * Render the colony summary in the right panel (population, total production).
 * Called on mount and after any build/demolish action.
 */
function _renderInfoPanel() {
    const panel = document.getElementById("colony-right-panel");
    if (!panel || !_colony) return;

    const prod = _colony.total_production || {};
    const prodRows = Object.entries(prod)
        .map(([k, v]) => `<tr><td class="prod-resource">${k}</td><td class="prod-value">+${v}/turn</td></tr>`)
        .join("");

    panel.innerHTML = `
        <div class="colony-panel-section">
            <h3 class="panel-heading">${_colony.planet_name}</h3>
            <div class="colony-stat">System: <span>${_colony.system_name}</span></div>
            <div class="colony-stat">Type: <span>${_colony.planet_type}</span></div>
            <div class="colony-stat">Founded: <span>Turn ${_colony.founded_turn}</span></div>
            <div class="colony-stat">Population: <span>${(_colony.population || 0).toLocaleString()}</span></div>
            <div class="colony-stat">Tiles: <span>${_colony.improvement_count} / ${_colony.tile_count} improved</span></div>
        </div>

        <div class="colony-panel-section">
            <h4 class="panel-subheading">Total Production / Turn</h4>
            ${prodRows
                ? `<table class="prod-table">${prodRows}</table>`
                : '<p class="muted">No improvements built yet.</p>'
            }
        </div>

        <div class="colony-panel-section" id="colony-tile-info">
            <p class="muted">Click a tile to inspect or build.</p>
        </div>
    `;
}

/**
 * Render selected-tile info + build/demolish actions into the tile-info
 * sub-section of the right panel.
 *
 * @param {object} tile - Tile object from _colony.tiles
 */
function _renderTilePanel(tile) {
    const tileInfoEl = document.getElementById("colony-tile-info");
    if (!tileInfoEl) return;

    const prod = tile.production && Object.keys(tile.production).length > 0
        ? Object.entries(tile.production).map(([k, v]) => `+${v} ${k}/turn`).join(", ")
        : "no production";

    let actionHtml = "";

    if (tile.improvement) {
        // Tile is developed — show tier, offer upgrade (if available) and demolish
        const tierLabel  = `Tier ${(tile.improvement_level ?? 0) + 1}`;
        const canUpgrade = tile.can_upgrade;
        const upgCost    = tile.upgrade_cost ?? 0;
        const upgBtn = canUpgrade
            ? `<button id="btn-upgrade-tile" class="btn btn--primary btn--sm">
                   Upgrade → Tier ${(tile.improvement_level ?? 0) + 2}
                   <span class="btn-cost">${upgCost.toLocaleString()} cr</span>
               </button>`
            : `<span class="tile-max-tier">Max Tier Reached</span>`;

        actionHtml = `
            <div class="tile-current-improvement">
                <span class="tile-improvement-name">${tile.improvement}</span>
                <span class="tile-tier-badge">${tierLabel}</span>
                <span class="tile-prod-summary">${prod}</span>
            </div>
            <div class="tile-action-row">
                ${upgBtn}
                <button id="btn-demolish-tile" class="btn btn--danger btn--sm">
                    Demolish (50% refund)
                </button>
            </div>
        `;
    } else {
        // Tile is empty — offer build menu
        actionHtml = `
            <button id="btn-build-tile" class="btn btn--primary btn--sm">
                Build Improvement…
            </button>
        `;
    }

    tileInfoEl.innerHTML = `
        <h4 class="panel-subheading">Selected Tile</h4>
        <div class="colony-stat">Terrain: <span class="terrain-tag terrain-tag--${tile.terrain}">${tile.terrain}</span></div>
        ${actionHtml}
    `;

    // Wire up buttons
    document.getElementById("btn-build-tile")
        ?.addEventListener("click", () => _showBuildMenu(tile));

    document.getElementById("btn-upgrade-tile")
        ?.addEventListener("click", () => _doUpgrade(tile));

    document.getElementById("btn-demolish-tile")
        ?.addEventListener("click", () => _doDemolish(tile));
}


// ---------------------------------------------------------------------------
// Build menu (shown as a modal)
// ---------------------------------------------------------------------------

/**
 * Open the improvement build modal for a tile.
 *
 * Displays all 15 improvements with their costs, research gates, and terrain
 * bonuses.  Locked improvements are shown greyed-out.
 *
 * @param {object} tile - The tile the player wants to build on.
 */
function _showBuildMenu(tile) {
    if (!_catalogue.length) {
        notify("ERROR", "Improvement catalogue not loaded.");
        return;
    }

    // Build improvement rows — two groups: unlocked, then locked
    const makeRow = (imp) => {
        const locked  = !imp.unlocked;
        const bonusTerrain = imp.terrain_bonus[tile.terrain];
        const hasTerrain   = bonusTerrain !== undefined;
        const bonusText    = hasTerrain
            ? `<span class="terrain-bonus">${bonusTerrain > 1 ? "+" : ""}${Math.round((bonusTerrain - 1) * 100)}% on ${tile.terrain}</span>`
            : "";

        const prodText = Object.entries(imp.base_production)
            .map(([k, v]) => `+${v} ${k}`)
            .join(", ");

        const lockMsg = locked
            ? `<span class="locked-label">Requires: ${imp.unlock_required}</span>`
            : `<span class="cost-label">${imp.cost.toLocaleString()} cr</span>`;

        const restriction = imp.terrain_restriction.length
            ? `<span class="terrain-restriction">(${imp.terrain_restriction.join(", ")} only)</span>`
            : "";

        const isRestricted = imp.terrain_restriction.length > 0
            && !imp.terrain_restriction.includes(tile.terrain);

        const rowClass = [
            "build-row",
            locked ? "build-row--locked" : "",
            isRestricted ? "build-row--restricted" : "",
        ].filter(Boolean).join(" ");

        const disabled = locked || isRestricted;

        return `
            <div class="${rowClass}" data-improvement="${imp.name}" data-disabled="${disabled}">
                <div class="build-row__header">
                    <span class="build-row__name">${imp.name}</span>
                    ${lockMsg}
                </div>
                <div class="build-row__detail">
                    <span class="build-row__prod">${prodText}</span>
                    ${bonusText}
                    ${restriction}
                </div>
                <div class="build-row__desc">${imp.description}</div>
            </div>
        `;
    };

    const unlocked = _catalogue.filter(i => i.unlocked);
    const locked   = _catalogue.filter(i => !i.unlocked);

    const bodyHtml = `
        <div class="build-menu">
            <p class="build-menu__context">
                Building on: <strong>${tile.terrain}</strong> tile at (${tile.q}, ${tile.r})
            </p>
            <div class="build-menu__list">
                ${unlocked.map(makeRow).join("")}
                ${locked.length
                    ? `<div class="build-section-divider">Locked</div>${locked.map(makeRow).join("")}`
                    : ""}
            </div>
        </div>
    `;

    showModal("Build Improvement", bodyHtml, [
        {
            label: "Cancel",
            className: "btn--secondary",
            onClick: () => closeModal(),
        },
    ]);

    // Wire click handlers on unlocked, non-restricted rows
    document.querySelectorAll(".build-row[data-disabled='false']").forEach(row => {
        row.style.cursor = "pointer";
        row.addEventListener("click", () => {
            const impName = row.dataset.improvement;
            closeModal();
            _doBuild(tile, impName);
        });
    });
}


// ---------------------------------------------------------------------------
// API actions
// ---------------------------------------------------------------------------

/**
 * POST /api/colony/{planet}/build to place an improvement on the tile.
 *
 * @param {object} tile - The target tile.
 * @param {string} improvementType - Name of the improvement to build.
 */
async function _doBuild(tile, improvementType) {
    const { planetName } = _context;
    try {
        const result = await buildImprovement(planetName, tile.q, tile.r, improvementType);
        notify("ECON", result.message);

        // Refresh colony data and re-render
        _colony = result.colony;
        _requestRedraw();
        _renderInfoPanel();

        // Update the tile panel for the still-selected tile
        const freshTile = _colony.tiles.find(t => t.q === tile.q && t.r === tile.r);
        if (freshTile) {
            _selectedTile = freshTile;
            _renderTilePanel(freshTile);
        }
    } catch (err) {
        notify("ERROR", err.message || "Build failed.");
    }
}

/**
 * POST /api/colony/{planet}/upgrade to upgrade the improvement on a tile.
 *
 * @param {object} tile - The tile whose improvement will be upgraded.
 */
async function _doUpgrade(tile) {
    const newTier = (tile.improvement_level ?? 0) + 2;
    const cost    = tile.upgrade_cost ?? 0;
    const ok = await confirm(
        "Upgrade Improvement",
        `Upgrade ${tile.improvement} to Tier ${newTier} for ${cost.toLocaleString()} credits? ` +
        `Production will increase to ${newTier === 2 ? "1.5×" : "2.2×"} base output.`
    );
    if (!ok) return;

    const { planetName } = _context;
    try {
        const result = await upgradeImprovement(planetName, tile.q, tile.r);
        notify("ECON", result.message);

        // Refresh colony data and re-render
        _colony = result.colony;
        _requestRedraw();
        _renderInfoPanel();

        const freshTile = _colony.tiles.find(t => t.q === tile.q && t.r === tile.r);
        if (freshTile) {
            _selectedTile = freshTile;
            _renderTilePanel(freshTile);
        }
    } catch (err) {
        notify("ERROR", err.message || "Upgrade failed.");
    }
}

/**
 * DELETE /api/colony/{planet}/build to demolish the improvement on a tile.
 *
 * @param {object} tile - The tile whose improvement will be demolished.
 */
async function _doDemolish(tile) {
    const ok = await confirm(
        "Demolish Improvement",
        `Demolish ${tile.improvement} on this tile? You will receive 50% of its cost as a refund.`
    );
    if (!ok) return;

    const { planetName } = _context;
    try {
        const result = await demolishImprovement(planetName, tile.q, tile.r);
        notify("ECON", result.message);

        // Refresh colony data and re-render
        _colony = result.colony;
        _requestRedraw();
        _renderInfoPanel();

        const freshTile = _colony.tiles.find(t => t.q === tile.q && t.r === tile.r);
        if (freshTile) {
            _selectedTile = freshTile;
            _renderTilePanel(freshTile);
        }
    } catch (err) {
        notify("ERROR", err.message || "Demolish failed.");
    }
}

/**
 * POST /api/colony/{planet}/found to establish a new colony.
 */
async function _doFoundColony() {
    const { planetName, systemName, planetType } = _context;
    if (!planetName || !systemName || !planetType) {
        notify("ERROR", "Missing planet context — cannot found colony.");
        return;
    }

    try {
        const result = await foundColony(planetName, systemName, planetType);
        notify("TURN", result.message);

        _colony = result.colony;

        // Rebuild the whole view now that we have a colony
        const container = document.getElementById("view-colony");
        if (container) {
            container.innerHTML = _buildChrome(planetName, systemName);
            _canvas = document.getElementById("colony-canvas");
            _setupCanvas();
            _renderInfoPanel();

            // Re-wire back button
            document.getElementById("colony-back-btn")
                ?.addEventListener("click", async () => {
                    const { switchView } = await import("../main.js");
                    switchView("galaxy");
                });
        }
    } catch (err) {
        notify("ERROR", err.message || "Failed to found colony.");
    }
}


// ---------------------------------------------------------------------------
// "Found Colony" prompt (shown when planet has no colony yet)
// ---------------------------------------------------------------------------

/**
 * Render a prompt to found a new colony when no colony exists on the planet.
 */
function _renderFoundPrompt() {
    const { planetName, planetType } = _context;

    // Show the prompt inside the left panel, hide/dim the canvas
    const leftPanel = document.getElementById("colony-left-panel");
    if (leftPanel) {
        leftPanel.innerHTML = `
            <div class="found-colony-prompt">
                <h3>Uninhabited World</h3>
                <p class="muted">No colony has been established on <strong>${planetName}</strong> yet.</p>
                <p class="muted">Planet type: <strong>${planetType || "Unknown"}</strong></p>
                <button id="btn-found-colony" class="btn btn--primary">
                    Found Colony
                </button>
            </div>
        `;
        document.getElementById("btn-found-colony")
            ?.addEventListener("click", _doFoundColony);
    }

    // Show a dim placeholder in the canvas area
    if (_canvas) {
        const ctx = _canvas.getContext("2d");
        _canvas.width  = _canvas.clientWidth  || 600;
        _canvas.height = _canvas.clientHeight || 500;
        ctx.fillStyle = "#050810";
        ctx.fillRect(0, 0, _canvas.width, _canvas.height);
        ctx.fillStyle = "#1a2a3a";
        ctx.font = '14px "Courier New", monospace';
        ctx.textAlign = "center";
        ctx.fillText("No colony — found one to begin.", _canvas.width / 2, _canvas.height / 2);
    }
}


// ---------------------------------------------------------------------------
// HTML template
// ---------------------------------------------------------------------------

/**
 * Build the static chrome for the colony view.
 * The layout mirrors the three-column structure used on the galaxy view:
 *   left panel | canvas | right panel
 *
 * @param {string} planetName
 * @param {string} systemName
 * @returns {string} HTML string
 */
function _buildChrome(planetName, systemName) {
    return `
        <div class="view-inner colony-view-inner">

            <!-- Left panel: colony controls -->
            <aside class="panel panel--left" id="colony-left-panel">
                <div class="panel-section">
                    <button id="colony-back-btn" class="btn btn--secondary btn--sm">
                        ← Galaxy Map
                    </button>
                </div>
                <div class="panel-section">
                    <h2 class="panel-title">${planetName}</h2>
                    <p class="panel-subtitle muted">${systemName}</p>
                </div>
                <div class="panel-section muted" id="colony-legend">
                    <p class="legend-hint">Click any tile to inspect or build.</p>
                    <p class="legend-hint">Scroll to zoom · Drag to pan.</p>
                </div>
            </aside>

            <!-- Centre: hex grid canvas -->
            <main class="canvas-container colony-canvas-container">
                <canvas id="colony-canvas"></canvas>
                <div id="colony-status-bar" class="canvas-status-bar"></div>
            </main>

            <!-- Right panel: tile info + production -->
            <aside class="panel panel--right" id="colony-right-panel">
                <p class="muted">Loading colony data…</p>
            </aside>

        </div>
    `;
}
