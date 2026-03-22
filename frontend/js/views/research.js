/**
 * frontend/js/views/research.js — Research tech-tree view.
 *
 * Displays all research projects across 11 categories.  Players can:
 *   • Filter nodes by category or by status (All / Available / Completed).
 *   • Click a node to see its description, prerequisites, unlocks, and
 *     associated energy type in the right panel.
 *   • Start or cancel research via API calls.
 *
 * Design: Alpha Centauri-style information-dense list layout.
 * Cards are colour-coded: teal=available, gold=active, green=completed,
 * dim=locked.
 *
 * Data: fetched once on mount, refreshed after start/cancel actions.
 */

import { state }         from "../state.js";
import {
    getResearchTree,
    startResearch,
    cancelResearch,
} from "../api.js";
import { notify }        from "../ui/notifications.js";
import { confirm }       from "../ui/modal.js";


// ---------------------------------------------------------------------------
// Module-level state
// ---------------------------------------------------------------------------

/** Full research tree response from /api/research/tree */
let _tree = null;

/** RP/turn total and breakdown from the last tree fetch */
let _rpPerTurn  = 0;
let _rpBreakdown = {};

/** Currently selected node object */
let _selectedNode = null;

/** Active category filter ("All" or a category name string) */
let _categoryFilter = "All";

/** Active status filter: "all" | "available" | "completed" | "active" */
let _statusFilter = "all";


// ---------------------------------------------------------------------------
// Category display order (matches research.json category names)
// ---------------------------------------------------------------------------
const CATEGORY_ORDER = [
    "All",
    "Chronoscience",
    "Ecology",
    "Emergence",
    "Energetics",
    "Engineering",
    "Epistemology",
    "Governance",
    "Information",
    "Materiality",
    "Mathematics",
    "Philosophy",
    "Polemology",
    "Semiotics",
    "Theurgy",
    "Topologies",
];

/** Short display labels for each category (keeps filter tabs compact) */
const CATEGORY_SHORT = {
    "All":           "All",
    "Chronoscience": "Chrono",
    "Ecology":       "Ecology",
    "Emergence":     "Emerge",
    "Energetics":    "Energetics",
    "Engineering":   "Engineering",
    "Epistemology":  "Epistemo",
    "Governance":    "Govern",
    "Information":   "Info",
    "Materiality":   "Matter",
    "Mathematics":   "Math",
    "Philosophy":    "Philos",
    "Polemology":    "Polemo",
    "Semiotics":     "Semiotic",
    "Theurgy":       "Theurgy",
    "Topologies":    "Topo",
};

/** Category accent colours for card left-border */
const CATEGORY_COLORS = {
    "Chronoscience": "var(--accent-gold)",
    "Ecology":       "var(--accent-green)",
    "Emergence":     "var(--accent-orange)",
    "Energetics":    "var(--accent-red)",
    "Engineering":   "var(--accent-teal)",
    "Epistemology":  "var(--accent-gold)",
    "Governance":    "var(--accent-cyan)",
    "Information":   "var(--accent-teal)",
    "Materiality":   "var(--accent-orange)",
    "Mathematics":   "var(--accent-purple)",
    "Philosophy":    "var(--accent-purple)",
    "Polemology":    "var(--accent-red)",
    "Semiotics":     "var(--accent-cyan)",
    "Theurgy":       "var(--accent-purple)",
    "Topologies":    "var(--accent-orange)",
};


// ---------------------------------------------------------------------------
// Public view object
// ---------------------------------------------------------------------------

export const researchView = {

    async mount(context = {}) {
        const container = document.getElementById("view-research");
        if (!container) return;

        container.innerHTML = _buildChrome();

        // Load tree data
        await _loadTree();

        // Wire filter controls
        _attachFilterListeners();

        // If navigated here via the HUD research bar, auto-select the active project
        if (context.selectActive && _tree?.active_research) {
            _selectedNode = _tree.nodes.find(n => n.active) || null;
        }

        // Render initial list (selected card gets highlight via _buildNodeCard)
        _renderNodeList();
        _renderRightPanel();

        // Scroll the selected card into view when auto-selecting
        if (_selectedNode) {
            const card = document.querySelector(`.research-node-card[data-name="${CSS.escape(_selectedNode.name)}"]`);
            if (card) card.scrollIntoView({ block: "center", behavior: "smooth" });
        }
    },

    unmount() {
        _tree         = null;
        _selectedNode = null;
        _categoryFilter = "All";
        _statusFilter   = "all";
    },
};


// ---------------------------------------------------------------------------
// Data loading
// ---------------------------------------------------------------------------

async function _loadTree() {
    try {
        _tree       = await getResearchTree();
        _rpPerTurn  = _tree.rp_per_turn  ?? 0;
        _rpBreakdown = _tree.rp_breakdown ?? {};
    } catch (err) {
        notify("ERROR", `Could not load research tree: ${err.message}`);
        _tree = { nodes: [], active_research: null, research_progress: 0,
                  active_research_time: null, completed_count: 0 };
        _rpPerTurn  = 0;
        _rpBreakdown = {};
    }
}


// ---------------------------------------------------------------------------
// Filter logic
// ---------------------------------------------------------------------------

/** Return the subset of nodes that pass both active filters. */
function _filteredNodes() {
    if (!_tree) return [];
    return _tree.nodes.filter(node => {
        // Category filter
        if (_categoryFilter !== "All" && node.category !== _categoryFilter) return false;
        // Status filter
        if (_statusFilter === "available" && !node.available) return false;
        if (_statusFilter === "completed" && !node.completed) return false;
        if (_statusFilter === "active"    && !node.active)    return false;
        return true;
    });
}


// ---------------------------------------------------------------------------
// Rendering — left panel (filters + active research bar)
// ---------------------------------------------------------------------------

function _renderLeftPanel() {
    const panel = document.getElementById("research-left-panel");
    if (!panel) return;

    // RP/turn breakdown panel
    const rpLabelMap = {
        intellect:   "Intellect (INT)",
        background:  "Background",
        path_bonus:  "Research Path",
        colony:      "Colony Buildings",
        faction:     "Faction Bonus",
        crew:        "Crew",
    };
    const rpRows = Object.entries(_rpBreakdown)
        .filter(([, v]) => v > 0)
        .map(([k, v]) => `
            <div class="rp-row">
                <span class="rp-label">${esc(rpLabelMap[k] ?? k)}</span>
                <span class="rp-value">+${v}</span>
            </div>
        `).join("");
    const rpHtml = `
        <div class="rp-total-row">
            <span>Research Output</span>
            <span class="stat-gold">${_rpPerTurn} RP/turn</span>
        </div>
        ${rpRows ? `<div class="rp-breakdown">${rpRows}</div>` : ""}
    `;

    // Active research progress bar
    let progressHtml = "";
    if (_tree?.active_research) {
        const pct       = _tree.active_research_time
            ? Math.round(Math.min(100, _tree.research_progress / _tree.active_research_time * 100))
            : 0;
        const activeNode = _tree.nodes?.find(n => n.active);
        const turnsLeft  = activeNode?.turns_to_complete ?? "?";
        progressHtml = `
            <div class="research-active-box">
                <div class="research-active-label">Active Research</div>
                <div class="research-active-name">${esc(_tree.active_research)}</div>
                <div class="research-progress-bar">
                    <div class="research-progress-fill" style="width:${pct}%"></div>
                </div>
                <div class="research-progress-text">
                    ${_tree.research_progress} / ${_tree.active_research_time} RP
                    &nbsp;·&nbsp; <span class="stat-gold">~${turnsLeft} turns</span>
                </div>
                <button class="btn btn--danger btn--sm research-cancel-btn" id="btn-cancel-research">
                    Cancel Research
                </button>
            </div>
        `;
    } else {
        progressHtml = `<p class="muted" style="padding:var(--sp-2) 0">No active research.<br>Select a project to begin.</p>`;
    }

    // Stats
    const total     = _tree?.nodes?.length || 0;
    const completed = _tree?.completed_count || 0;
    const available = _tree?.nodes?.filter(n => n.available).length || 0;

    // Category filter tabs
    const catTabs = CATEGORY_ORDER.map(cat => {
        const active  = _categoryFilter === cat ? "research-cat-tab--active" : "";
        const label   = CATEGORY_SHORT[cat] || cat;
        const count   = cat === "All"
            ? total
            : (_tree?.nodes?.filter(n => n.category === cat).length || 0);
        return `<button class="research-cat-tab ${active}" data-cat="${esc(cat)}">${esc(label)} <span class="cat-count">${count}</span></button>`;
    }).join("");

    panel.innerHTML = `
        <div class="panel-section">
            <div class="research-stats-row">
                <div class="research-stat"><span>${completed}</span>Completed</div>
                <div class="research-stat"><span>${available}</span>Available</div>
                <div class="research-stat"><span>${total - completed}</span>Remaining</div>
            </div>
        </div>

        <div class="panel-section">
            ${rpHtml}
        </div>

        <div class="panel-section">
            ${progressHtml}
        </div>

        <div class="panel-section">
            <div class="panel-subheading">Status Filter</div>
            <div class="research-status-filters">
                ${["all","available","completed"].map(s =>
                    `<button class="btn btn--sm research-status-btn ${_statusFilter===s?"btn--primary":""}" data-status="${s}">
                        ${s.charAt(0).toUpperCase()+s.slice(1)}
                    </button>`
                ).join("")}
            </div>
        </div>

        <div class="panel-section">
            <div class="panel-subheading">Category</div>
            <div class="research-cat-tabs">${catTabs}</div>
        </div>
    `;

    // Wire cancel button
    document.getElementById("btn-cancel-research")?.addEventListener("click", _doCancel);

    // Category tabs
    panel.querySelectorAll(".research-cat-tab").forEach(btn => {
        btn.addEventListener("click", () => {
            _categoryFilter = btn.dataset.cat;
            _renderNodeList();
            _renderLeftPanel();  // refresh active class
        });
    });

    // Status filter buttons
    panel.querySelectorAll(".research-status-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            _statusFilter = btn.dataset.status;
            _renderNodeList();
            _renderLeftPanel();
        });
    });
}


// ---------------------------------------------------------------------------
// Rendering — centre (node list)
// ---------------------------------------------------------------------------

function _renderNodeList() {
    // Refresh left panel too (counts change with filters)
    _renderLeftPanel();

    const listEl = document.getElementById("research-node-list");
    if (!listEl) return;

    const nodes = _filteredNodes();

    if (!nodes.length) {
        listEl.innerHTML = `<p class="muted" style="padding:var(--sp-4)">No research projects match the current filter.</p>`;
        return;
    }

    // Group by category for display
    const groups = {};
    for (const node of nodes) {
        if (!groups[node.category]) groups[node.category] = [];
        groups[node.category].push(node);
    }

    let html = "";
    for (const [category, catNodes] of Object.entries(groups)) {
        // Only show category header when "All" filter is active
        if (_categoryFilter === "All") {
            html += `<div class="research-category-header">${esc(category)}</div>`;
        }
        for (const node of catNodes) {
            html += _buildNodeCard(node);
        }
    }

    listEl.innerHTML = html;

    // Wire click on each card
    listEl.querySelectorAll(".research-node-card").forEach(card => {
        card.addEventListener("click", () => {
            const nodeName = card.dataset.name;
            _selectedNode  = _tree.nodes.find(n => n.name === nodeName) || null;
            // Update selection highlight
            listEl.querySelectorAll(".research-node-card").forEach(c =>
                c.classList.toggle("research-node-card--selected", c === card)
            );
            _renderRightPanel();
        });
    });
}

/** Build the HTML string for a single research card. */
function _buildNodeCard(node) {
    let statusClass = "research-node--locked";
    let statusLabel = "Locked";

    if (node.active)     { statusClass = "research-node--active";    statusLabel = "Researching"; }
    else if (node.completed) { statusClass = "research-node--done";   statusLabel = "Done"; }
    else if (node.available) { statusClass = "research-node--open";   statusLabel = "Available"; }

    const catColor   = CATEGORY_COLORS[node.category] || "var(--border-color)";
    const selected   = _selectedNode?.name === node.name ? "research-node-card--selected" : "";
    const difficulty = "●".repeat(node.difficulty) + "○".repeat(Math.max(0, 10 - node.difficulty));

    const rpCost   = node.rp_cost ?? node.research_time ?? 0;
    const turnsEst = node.turns_to_complete > 0 ? `~${node.turns_to_complete}t` : (node.completed ? "✓" : "—");
    const pathBadge = node.in_research_path
        ? `<span class="research-path-badge" title="In your research path">◈</span>` : "";

    // Extended unlock category icons
    const extUnlocks = node.extended_unlocks ?? {};
    const unlockIconMap = { abilities: "⚡", ship: "⛵", crew: "◉", security: "⊛", economic: "◈", diplomacy: "⬡" };
    const unlockIcons = Object.entries(extUnlocks)
        .filter(([, v]) => v.length > 0)
        .map(([cat]) => `<span class="unlock-icon" title="${esc(cat)}">${unlockIconMap[cat] ?? "◆"}</span>`)
        .join("");

    return `
        <div class="research-node-card ${statusClass} ${selected}"
             data-name="${esc(node.name)}"
             style="border-left-color:${catColor}">
            <div class="research-node-card__header">
                <span class="research-node-card__name">${esc(node.name)}${pathBadge}</span>
                <span class="research-node-card__status">${statusLabel}</span>
            </div>
            <div class="research-node-card__meta">
                <span class="research-node-card__diff" title="Difficulty">${difficulty}</span>
                <span class="research-node-card__rp" title="RP required">${rpCost} RP</span>
                <span class="research-node-card__time">${turnsEst}</span>
            </div>
            ${unlockIcons ? `<div class="research-node-card__unlocks">${unlockIcons}</div>` : ""}
            ${node.related_energy
                ? `<div class="research-node-card__energy">⚡ ${esc(node.related_energy)}</div>`
                : ""}
        </div>
    `;
}


// ---------------------------------------------------------------------------
// Rendering — right panel (selected node detail)
// ---------------------------------------------------------------------------

function _renderRightPanel() {
    const panel = document.getElementById("research-right-panel");
    if (!panel) return;

    if (!_selectedNode) {
        panel.innerHTML = `<p class="muted" style="padding:var(--sp-4)">Select a research project to view details.</p>`;
        return;
    }

    const node    = _selectedNode;
    const catColor = CATEGORY_COLORS[node.category] || "var(--border-color)";

    // Status action button
    let actionHtml = "";
    if (node.active) {
        actionHtml = `
            <button class="btn btn--danger" id="btn-research-cancel-detail">Cancel Research</button>
        `;
    } else if (node.available && !_tree?.active_research) {
        actionHtml = `
            <button class="btn btn--primary" id="btn-research-start">
                ▶ Start Research
            </button>
        `;
    } else if (node.available && _tree?.active_research) {
        actionHtml = `<p class="muted">Cancel active research first to start this project.</p>`;
    } else if (node.completed) {
        actionHtml = `<p class="text-green">✓ Research complete.</p>`;
    } else {
        // Locked — show unmet prerequisites
        const unmet = node.prerequisites.filter(p => !game_prereq_met(p));
        actionHtml = `<p class="muted">Requires: ${unmet.map(p => esc(p)).join(", ") || "unknown"}</p>`;
    }

    // Prerequisites list
    const prereqHtml = node.prerequisites.length
        ? node.prerequisites.map(p => {
            const met = _tree.nodes.find(n => n.name === p)?.completed;
            return `<li class="${met ? "prereq-met" : "prereq-unmet"}">${met ? "✓" : "○"} ${esc(p)}</li>`;
          }).join("")
        : "<li class='muted'>None</li>";

    // Unlocks list — exclude items already shown in a categorized section below
    const _catSuffixes = /\((ability|ship|crew|security|economic|diplomacy)\)\s*$/i;
    const flatUnlocks = node.unlocks.filter(u => !_catSuffixes.test(u));
    const unlocksHtml = flatUnlocks.length
        ? flatUnlocks.map(u => `<li>◆ ${esc(u)}</li>`).join("")
        : "<li class='muted'>No listed unlocks.</li>";

    // Difficulty stars
    const diff = "●".repeat(node.difficulty) + "○".repeat(Math.max(0, 10 - node.difficulty));

    // Path bonus indicator
    const pathIndicator = node.in_research_path
        ? `<div class="research-path-indicator">◈ In your research path (+1 RP/turn)</div>` : "";

    // Extended unlocks sections
    const extCategories = {
        abilities:  "Abilities Unlocked",
        ship:       "Ship Functions Unlocked",
        crew:       "Crew Roles Unlocked",
        security:   "Security Functions Unlocked",
        economic:   "Economic Functions Unlocked",
        diplomacy:  "Diplomacy Options Unlocked",
    };
    let extHtml = "";
    for (const [cat, label] of Object.entries(extCategories)) {
        const items = (node.extended_unlocks ?? {})[cat] ?? [];
        if (!items.length) continue;
        extHtml += `
            <div class="research-detail__section">
                <div class="panel-subheading">${esc(label)}</div>
                <ul class="research-list">
                    ${items.map(id => `<li>◆ ${esc(_formatUnlockId(id))}</li>`).join("")}
                </ul>
            </div>
        `;
    }

    const rpCost  = node.rp_cost ?? node.research_time ?? 0;
    const turnsEst = node.turns_to_complete > 0 ? `~${node.turns_to_complete} turns` : (node.completed ? "Complete" : "—");

    panel.innerHTML = `
        <div class="research-detail">
            <div class="research-detail__header" style="border-left:3px solid ${catColor}">
                <h3 class="research-detail__name">${esc(node.name)}</h3>
                <div class="research-detail__category">${esc(node.category)}</div>
                ${pathIndicator}
            </div>

            <div class="research-detail__description">${esc(node.description)}</div>

            <div class="research-detail__stats">
                <div class="research-stat-row">
                    <span>RP Required</span>
                    <span class="stat-gold">${rpCost.toLocaleString()}</span>
                </div>
                <div class="research-stat-row">
                    <span>Est. Turns</span>
                    <span>${turnsEst}</span>
                </div>
                <div class="research-stat-row">
                    <span>Difficulty</span>
                    <span class="stat-diff">${diff}</span>
                </div>
                ${node.related_energy ? `
                <div class="research-stat-row">
                    <span>Energy Type</span>
                    <span class="stat-energy">⚡ ${esc(node.related_energy)}</span>
                </div>` : ""}
            </div>

            <div class="research-detail__section">
                <div class="panel-subheading">Prerequisites</div>
                <ul class="research-list">${prereqHtml}</ul>
            </div>

            <div class="research-detail__section">
                <div class="panel-subheading">Unlocks</div>
                <ul class="research-list">${unlocksHtml}</ul>
            </div>

            ${extHtml}

            <div class="research-detail__action">
                ${actionHtml}
            </div>
        </div>
    `;

    // Wire action buttons
    document.getElementById("btn-research-start")
        ?.addEventListener("click", () => _doStart(node));
    document.getElementById("btn-research-cancel-detail")
        ?.addEventListener("click", _doCancel);
}


// ---------------------------------------------------------------------------
// Prerequisite helper
// ---------------------------------------------------------------------------

/** Convert a snake_case unlock ID to a human-readable Title Case string. */
function _formatUnlockId(id) {
    return id.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
}

/** Return true if a prerequisite name appears in the completed list. */
function game_prereq_met(prereqName) {
    if (!_tree?.nodes) return false;
    return _tree.nodes.find(n => n.name === prereqName)?.completed ?? false;
}


// ---------------------------------------------------------------------------
// API actions
// ---------------------------------------------------------------------------

async function _doStart(node) {
    try {
        await startResearch(node.name);
        notify("RD", `Research started: ${node.name} (~${node.turns_to_complete ?? "?"} turns)`);
        // Re-fetch tree so progress info and status flags are fresh
        await _loadTree();
        _selectedNode = _tree.nodes.find(n => n.name === node.name) || null;
        _renderNodeList();
        _renderRightPanel();
    } catch (err) {
        notify("ERROR", err.message || "Could not start research.");
    }
}

async function _doCancel() {
    const ok = await confirm(
        "Cancel Research",
        `Cancel research on "${_tree?.active_research}"? Accumulated RP progress will be lost.`
    );
    if (!ok) return;

    try {
        const result = await cancelResearch();
        notify("RD", result.message);
        await _loadTree();
        _selectedNode = null;
        _renderNodeList();
        _renderRightPanel();
    } catch (err) {
        notify("ERROR", err.message || "Could not cancel research.");
    }
}


// ---------------------------------------------------------------------------
// Filter event listeners
// ---------------------------------------------------------------------------

function _attachFilterListeners() {
    // Initial render is triggered by _renderNodeList() in mount()
    // All event listeners are re-attached on each _renderLeftPanel() call
    // so nothing extra needed here.
}


// ---------------------------------------------------------------------------
// Static chrome
// ---------------------------------------------------------------------------

/**
 * Build the three-column layout HTML for the research view.
 * Left: filters + active research progress
 * Centre: scrollable node list
 * Right: selected node detail + action buttons
 */
function _buildChrome() {
    return `
        <div class="view-inner research-view-inner">

            <!-- Left panel: filters and active research -->
            <aside class="panel panel--left" id="research-left-panel">
                <div class="panel-section">
                    <h2 class="panel-title">Research</h2>
                </div>
            </aside>

            <!-- Centre: scrollable node list -->
            <main class="research-centre">
                <div id="research-node-list" class="research-node-list">
                    <p class="muted" style="padding:var(--sp-4)">Loading research tree…</p>
                </div>
            </main>

            <!-- Right panel: selected node detail -->
            <aside class="panel panel--right" id="research-right-panel">
                <p class="muted" style="padding:var(--sp-4)">Select a project to view details.</p>
            </aside>

        </div>
    `;
}


// ---------------------------------------------------------------------------
// HTML escape helper
// ---------------------------------------------------------------------------

function esc(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}
