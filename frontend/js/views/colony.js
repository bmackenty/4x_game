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
    getColonySystems,
    setColonySystem,
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

/**
 * Which tab is active in the left panel.
 * "hex"     — the default hex-grid + tile-info view
 * "systems" — the social/economic/political systems panel
 */
let _activeTab = "hex";

/** Cached response from GET /api/colony/{planet}/systems */
let _systemsData = null;


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

            // Wire the HEX / SYSTEMS tab buttons in the left panel
            document.getElementById("colony-tab-hex")
                ?.addEventListener("click", () => _switchTab("hex"));
            document.getElementById("colony-tab-systems")
                ?.addEventListener("click", () => _switchTab("systems"));
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
        _activeTab    = "hex";
        _systemsData  = null;
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
            <div class="colony-stat">Population: <span>${(_colony.population || 0).toLocaleString()} <small style="color:#00d4aa">(+${(_colony.pop_growth_est || 0).toLocaleString()}/turn, ${(_colony.pop_growth_rate || 0).toFixed(1)}%)</small></span></div>
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
 * Shows a wide two-column panel: category sidebar on the left, scrollable
 * card grid on the right.  A search box and Available/All toggle let the
 * player quickly find what they want among 200+ buildings.
 *
 * @param {object} tile - The tile the player wants to build on.
 */
function _showBuildMenu(tile) {
    if (!_catalogue.length) {
        notify("ERROR", "Improvement catalogue not loaded.");
        return;
    }

    // ── Collect all unique categories in display order ──────────────────────
    // "Baseline" always first; the rest are sorted alphabetically.
    const allCats = [...new Set(_catalogue.map(i => i.category || "Unknown"))];
    allCats.sort((a, b) => {
        if (a === "Baseline") return -1;
        if (b === "Baseline") return 1;
        return a.localeCompare(b);
    });

    // ── Initial filter state ─────────────────────────────────────────────────
    let _activeCat   = "All";
    let _showAll     = false;   // false = Available only (unlocked + compatible terrain)
    let _searchQuery = "";

    // ── Helper: is an improvement buildable on this tile? ───────────────────
    const isRestricted = (imp) =>
        imp.terrain_restriction.length > 0 &&
        !imp.terrain_restriction.includes(tile.terrain);

    // ── Render one building card ─────────────────────────────────────────────
    const makeCard = (imp) => {
        const locked      = !imp.unlocked;
        const restricted  = isRestricted(imp);
        const disabled    = locked || restricted;

        // Terrain bonus badge for this tile's terrain
        const bonus = imp.terrain_bonus[tile.terrain];
        const bonusBadge = bonus !== undefined
            ? `<span class="bcard__terrain-badge bcard__terrain-badge--${bonus >= 1.3 ? "high" : "low"}">
                   ${bonus > 1 ? "+" : ""}${Math.round((bonus - 1) * 100)}% ${tile.terrain}
               </span>`
            : "";

        // Production summary
        const prodPills = Object.entries(imp.base_production)
            .map(([k, v]) => `<span class="bcard__prod-pill bcard__prod-pill--${k}">+${v} ${k}</span>`)
            .join("");

        // Terrain restriction notice
        const restrictNote = imp.terrain_restriction.length
            ? `<div class="bcard__restrict">${imp.terrain_restriction.join(" / ")} only</div>`
            : "";

        // Lock / cost line
        const statusLine = locked
            ? `<div class="bcard__lock">🔒 ${imp.unlock_required}</div>`
            : restricted
                ? `<div class="bcard__lock bcard__lock--terrain">Wrong terrain</div>`
                : `<div class="bcard__cost">${imp.cost.toLocaleString()} cr</div>`;

        // Category pill
        const catPill = `<span class="bcard__cat">${imp.category || ""}</span>`;

        const cardClass = [
            "bcard",
            locked      ? "bcard--locked"      : "",
            restricted  ? "bcard--restricted"  : "",
        ].filter(Boolean).join(" ");

        return `
            <div class="${cardClass}"
                 data-improvement="${imp.name}"
                 data-disabled="${disabled}"
                 title="${imp.description}">
                <div class="bcard__head">
                    <span class="bcard__name">${imp.name}</span>
                    ${bonusBadge}
                </div>
                <div class="bcard__prod">${prodPills}</div>
                ${restrictNote}
                <div class="bcard__foot">
                    ${catPill}
                    ${statusLine}
                </div>
                <div class="bcard__desc">${imp.description}</div>
            </div>
        `;
    };

    // ── Render category sidebar tabs ─────────────────────────────────────────
    const makeSidebar = (activeCat) => {
        const countFor = (cat) => {
            const items = cat === "All" ? _catalogue : _catalogue.filter(i => i.category === cat);
            return _showAll ? items.length : items.filter(i => i.unlocked && !isRestricted(i)).length;
        };
        const tabs = ["All", ...allCats].map(cat => {
            const n = countFor(cat);
            return `<button class="bpanel__tab${cat === activeCat ? " bpanel__tab--active" : ""}"
                            data-cat="${cat}">
                        ${cat} <span class="bpanel__tab-count">${n}</span>
                    </button>`;
        });
        return tabs.join("");
    };

    // ── Render the card grid based on current filter state ───────────────────
    const renderCards = () => {
        let items = _activeCat === "All"
            ? _catalogue
            : _catalogue.filter(i => i.category === _activeCat);

        if (!_showAll) {
            items = items.filter(i => i.unlocked && !isRestricted(i));
        }

        if (_searchQuery) {
            const q = _searchQuery.toLowerCase();
            items = items.filter(i =>
                i.name.toLowerCase().includes(q) ||
                (i.description || "").toLowerCase().includes(q) ||
                Object.keys(i.base_production).some(k => k.includes(q))
            );
        }

        const grid = document.getElementById("bpanel-grid");
        if (!grid) return;

        if (!items.length) {
            grid.innerHTML = `<div class="bpanel__empty">No buildings match the current filter.</div>`;
            return;
        }
        grid.innerHTML = items.map(makeCard).join("");

        // Wire click on buildable cards
        grid.querySelectorAll(".bcard[data-disabled='false']").forEach(card => {
            card.addEventListener("click", () => {
                const impName = card.dataset.improvement;
                closeModal();
                _doBuild(tile, impName);
            });
        });
    };

    // ── Full panel re-render (sidebar + grid) ────────────────────────────────
    const rerenderSidebar = () => {
        const sidebar = document.getElementById("bpanel-sidebar");
        if (!sidebar) return;
        sidebar.innerHTML = makeSidebar(_activeCat);
        sidebar.querySelectorAll(".bpanel__tab").forEach(btn => {
            btn.addEventListener("click", () => {
                _activeCat = btn.dataset.cat;
                rerenderSidebar();
                renderCards();
            });
        });
    };

    // ── Initial HTML ─────────────────────────────────────────────────────────
    const bodyHtml = `
        <div class="bpanel">
            <div class="bpanel__toolbar">
                <input  id="bpanel-search"
                        class="bpanel__search"
                        type="text"
                        placeholder="Search buildings…"
                        value="" />
                <label class="bpanel__toggle">
                    <input id="bpanel-showall" type="checkbox" ${_showAll ? "checked" : ""} />
                    Show locked &amp; incompatible
                </label>
                <span class="bpanel__context">
                    Tile: <strong>${tile.terrain}</strong> (${tile.q}, ${tile.r})
                </span>
            </div>
            <div class="bpanel__body">
                <nav id="bpanel-sidebar" class="bpanel__sidebar">
                    ${makeSidebar(_activeCat)}
                </nav>
                <div id="bpanel-grid" class="bpanel__grid"></div>
            </div>
        </div>
    `;

    showModal("Build Improvement", bodyHtml, [
        { label: "Cancel", className: "btn--secondary", onClick: () => closeModal() },
    ], { wide: true });

    // ── Wire toolbar after modal is in the DOM ───────────────────────────────
    rerenderSidebar();
    renderCards();

    document.getElementById("bpanel-search").addEventListener("input", (e) => {
        _searchQuery = e.target.value.trim();
        renderCards();
    });

    document.getElementById("bpanel-showall").addEventListener("change", (e) => {
        _showAll = e.target.checked;
        rerenderSidebar();
        renderCards();
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

        // Invalidate the galaxy map cache so territory borders update when
        // the player returns to the galaxy view.
        state.galaxyMap = [];

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
    const { planetName = "Unknown", planetType } = _context;

    // Show the prompt inside the right panel, hide/dim the canvas
    const rightPanel = document.getElementById("colony-right-panel");
    if (rightPanel) {
        rightPanel.innerHTML = `
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
// Tab system — HEX MAP ↔ SYSTEMS
// ---------------------------------------------------------------------------

/**
 * Switch between the "hex" (default) and "systems" tabs.
 * Toggling the SYSTEMS tab fetches fresh data from the API and renders the
 * Systems panel.  Switching back to HEX restores the normal right-panel
 * content and makes the canvas interactive again.
 *
 * @param {"hex"|"systems"} tab
 */
async function _switchTab(tab) {
    _activeTab = tab;

    // Update tab button styles
    const tabHex = document.getElementById("colony-tab-hex");
    const tabSys = document.getElementById("colony-tab-systems");
    if (tabHex) tabHex.classList.toggle("colony-tab--active", tab === "hex");
    if (tabSys) tabSys.classList.toggle("colony-tab--active", tab === "systems");

    // Show/hide the canvas area
    const canvasContainer = document.querySelector(".colony-canvas-container");
    if (canvasContainer) canvasContainer.style.display = (tab === "hex") ? "" : "none";

    if (tab === "systems") {
        const panel = document.getElementById("colony-right-panel");
        if (panel) panel.innerHTML = `<p class="muted">Loading systems…</p>`;
        try {
            const { planetName } = _context;
            _systemsData = await getColonySystems(planetName);
            _renderSystemsPanel();
        } catch (err) {
            const panel = document.getElementById("colony-right-panel");
            if (panel) panel.innerHTML = `<p class="muted">Could not load systems: ${err.message}</p>`;
        }
    } else {
        // Restore hex view
        _renderInfoPanel();
        // Re-show selected tile panel if one was selected
        if (_selectedTile) _renderTilePanel(_selectedTile);
    }
}


// ---------------------------------------------------------------------------
// Systems panel — social / economic / political
// ---------------------------------------------------------------------------

/**
 * Render the full Systems panel in the right panel column.
 * Reads from the cached _systemsData and _colony objects.
 */
function _renderSystemsPanel() {
    const panel = document.getElementById("colony-right-panel");
    if (!panel || !_systemsData) return;

    const {
        coherence_score   = 0,
        coherence_label   = "Stable",
        coherence_multiplier = 1.0,
        cooldown          = {},
        affinity_table    = {},
        current_systems   = {},
    } = _systemsData;

    // Coherence bar colour
    const cohColour = coherence_score >= 4 ? "#00d4aa"
                    : coherence_score >= 1 ? "#8888ff"
                    : coherence_score >= -1 ? "#cccccc"
                    : coherence_score >= -3 ? "#ff8844"
                    :                         "#ff4444";
    const cohPct = Math.round(((coherence_score + 6) / 12) * 100);

    // Build three system sections
    const sections = [
        { key: "social",    label: "SOCIAL SYSTEM" },
        { key: "economic",  label: "ECONOMIC SYSTEM" },
        { key: "political", label: "POLITICAL SYSTEM" },
    ];

    const sectionsHtml = sections.map(({ key, label }) => {
        const sysDef = _colony?.systems?.[key] || {};
        const cooldownTurns = cooldown[key] || 0;
        const onCooldown = cooldownTurns > 0;

        // Format modifiers as chips
        const mods = sysDef.modifiers || {};
        const modChips = Object.entries(mods).map(([k, v]) => {
            const isFlat = k === "stability";
            const sign   = v >= 0 ? "+" : "";
            const val    = isFlat ? `${sign}${v}` : `${sign}${Math.round(v * 100)}%`;
            const colour = v >= 0 ? "#00d4aa" : "#ff6666";
            return `<span class="system-modifier-chip" style="color:${colour}">${_modLabel(k)} ${val}</span>`;
        }).join(" ");

        // Unique commodity (economic only)
        const commodityHtml = key === "economic" && sysDef.unique_commodity
            ? `<div class="colony-stat" style="margin-top:4px">
                Produces: <span style="color:#f0c040">
                    ${sysDef.unique_commodity} ×${sysDef.commodity_amount}/turn
                </span>
               </div>`
            : "";

        // Cooldown badge
        const cooldownBadge = onCooldown
            ? `<span class="system-cooldown-badge" title="Cooldown active">
                ⏳ ${cooldownTurns} turn${cooldownTurns !== 1 ? "s" : ""}
               </span>`
            : "";

        const changeBtnDisabled = onCooldown ? "disabled" : "";
        const changeBtnTitle    = onCooldown
            ? `Cooldown: ${cooldownTurns} turn(s) remaining`
            : `Change ${key} system`;

        return `
        <div class="colony-system-section">
            <div class="panel-subheading">${label}</div>
            <div class="colony-system-active">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <strong>${sysDef.name || current_systems[key] || "—"}</strong>
                    ${cooldownBadge}
                    <button class="btn btn--sm btn--primary colony-sys-change-btn"
                            data-category="${key}"
                            ${changeBtnDisabled}
                            title="${changeBtnTitle}">
                        CHANGE
                    </button>
                </div>
                <p class="muted" style="font-size:0.75rem;margin:4px 0">
                    ${sysDef.description || ""}
                </p>
                <div class="system-modifier-chips">${modChips}</div>
                ${commodityHtml}
            </div>
        </div>`;
    }).join("");

    // Faction affinity table — sorted by absolute value descending
    const affinityEntries = Object.entries(affinity_table)
        .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]));

    const affinityRows = affinityEntries.map(([name, score]) => {
        const sign   = score > 0 ? "+" : "";
        const colour = score > 0 ? "#00d4aa" : score < 0 ? "#ff6666" : "#888";
        const arrow  = score > 0 ? "▲" : score < 0 ? "▼" : "—";
        return `<div class="system-affinity-row">
            <span class="system-affinity-name">${name}</span>
            <span style="color:${colour}">${arrow} ${sign}${score}</span>
        </div>`;
    }).join("");

    panel.innerHTML = `
        <div class="colony-systems-panel">

            <!-- Header -->
            <div class="panel-section">
                <div class="panel-heading">Colony Systems</div>
                <p class="muted" style="font-size:0.75rem">
                    Configure the social, economic and political systems that
                    govern ${_colony?.planet_name || "this colony"}.
                    Aligned systems unlock coherence bonuses; misaligned systems
                    create friction penalties on all production.
                </p>
            </div>

            <!-- Coherence score -->
            <div class="panel-section">
                <div class="panel-subheading">SYSTEM COHERENCE</div>
                <div style="display:flex;justify-content:space-between;margin-bottom:4px">
                    <span style="color:${cohColour}">${coherence_label}</span>
                    <span class="muted">${coherence_multiplier >= 1 ? "+" : ""}${Math.round((coherence_multiplier - 1) * 100)}% production</span>
                </div>
                <div class="coherence-bar">
                    <div class="coherence-bar__fill" style="width:${cohPct}%;background:${cohColour}"></div>
                </div>
            </div>

            <!-- Three system sections -->
            ${sectionsHtml}

            <!-- Faction affinity table -->
            ${affinityEntries.length > 0 ? `
            <div class="panel-section">
                <div class="panel-subheading">FACTION AFFINITY</div>
                <p class="muted" style="font-size:0.75rem;margin-bottom:6px">
                    How compatible your systems are with each faction's worldview.
                </p>
                <div class="system-affinity-list">${affinityRows}</div>
            </div>` : ""}

        </div>
    `;

    // Wire CHANGE buttons
    panel.querySelectorAll(".colony-sys-change-btn").forEach(btn => {
        btn.addEventListener("click", () => _showSystemSelector(btn.dataset.category));
    });
}


/**
 * Return a human-readable label for a modifier key.
 * @param {string} key - e.g. "fleet_points", "pop_growth"
 * @returns {string}
 */
function _modLabel(key) {
    const MAP = {
        minerals:         "Minerals",
        credits:          "Credits",
        research:         "Research",
        food:             "Food",
        fleet_points:     "Fleet",
        pop_growth:       "Pop Growth",
        trade_volume:     "Trade Vol.",
        all_production:   "All Output",
        faction_rep_gain: "Rep Gain",
        all_diplomacy:    "Diplomacy",
        stability:        "Stability",
    };
    return MAP[key] || key;
}


/**
 * Open the system selector modal for a given category.
 * Shows all 6 options for that category, marking the current one and any
 * locked (research-gated) options.
 *
 * @param {"social"|"economic"|"political"} category
 */
function _showSystemSelector(category) {
    if (!_systemsData) return;
    const { planetName } = _context;
    const options   = _systemsData.options?.[category] || [];
    const current   = _systemsData.current_systems?.[category];

    const label = { social: "Social", economic: "Economic", political: "Political" }[category];

    const cardsHtml = options.map(opt => {
        const isCurrent = opt.id === current;
        const isLocked  = opt.locked;

        const modChips = Object.entries(opt.modifiers || {}).map(([k, v]) => {
            const isFlat = k === "stability";
            const sign   = v >= 0 ? "+" : "";
            const val    = isFlat ? `${sign}${v}` : `${sign}${Math.round(v * 100)}%`;
            const colour = v >= 0 ? "#00d4aa" : "#ff6666";
            return `<span class="system-modifier-chip" style="color:${colour}">${_modLabel(k)} ${val}</span>`;
        }).join(" ");

        const commodityHtml = category === "economic" && opt.unique_commodity
            ? `<div style="font-size:0.75rem;color:#f0c040;margin-top:4px">
                Produces: ${opt.unique_commodity} ×${opt.commodity_amount}/turn
               </div>`
            : "";

        const lockHtml = isLocked
            ? `<div style="font-size:0.72rem;color:#ff8844;margin-top:4px">
                🔒 ${opt.lock_reason}
               </div>`
            : "";

        const cardClasses = [
            "system-card",
            isCurrent ? "system-card--current" : "",
            isLocked  ? "system-card--locked"  : "",
        ].filter(Boolean).join(" ");

        return `
        <div class="${cardClasses}"
             data-id="${opt.id}"
             style="${isLocked ? "opacity:0.55;cursor:not-allowed" : "cursor:pointer"}">
            <div style="display:flex;justify-content:space-between;align-items:center">
                <strong>${opt.name}</strong>
                ${isCurrent ? `<span style="color:#00d4aa;font-size:0.75rem">● ACTIVE</span>` : ""}
            </div>
            <p class="muted" style="font-size:0.75rem;margin:4px 0">${opt.description}</p>
            <div class="system-modifier-chips" style="margin-bottom:4px">${modChips}</div>
            ${commodityHtml}
            ${lockHtml}
        </div>`;
    }).join("");

    showModal(`Change ${label} System`, cardsHtml, [
        { label: "Cancel", className: "btn btn--secondary", action: closeModal },
    ]);

    // Wire clicks on unlocked, non-current cards
    document.querySelectorAll(".system-card:not(.system-card--locked):not(.system-card--current)")
        .forEach(card => {
            card.addEventListener("click", async () => {
                closeModal();
                await _doSetSystem(planetName, category, card.dataset.id);
            });
        });
}


/**
 * Call the API to change a colony system, then refresh the systems panel.
 *
 * @param {string} planetName
 * @param {string} category   - "social" | "economic" | "political"
 * @param {string} systemId   - New system ID
 */
async function _doSetSystem(planetName, category, systemId) {
    try {
        const result = await setColonySystem(planetName, category, systemId);
        notify("ECON", result.message);

        // Update cached colony and systems data
        _colony      = result.colony;
        _systemsData = await getColonySystems(planetName);
        _renderSystemsPanel();
    } catch (err) {
        notify("ERROR", err.message || "Failed to change system.");
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

                <!-- Tab row: HEX MAP | SYSTEMS -->
                <div class="panel-section colony-tab-row">
                    <button id="colony-tab-hex"
                            class="btn btn--sm colony-tab colony-tab--active"
                            title="Hex tile map and improvements">
                        HEX MAP
                    </button>
                    <button id="colony-tab-systems"
                            class="btn btn--sm colony-tab"
                            title="Social, economic and political systems">
                        SYSTEMS
                    </button>
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
