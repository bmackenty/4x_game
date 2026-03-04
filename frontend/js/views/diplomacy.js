/**
 * frontend/js/views/diplomacy.js — Faction diplomacy view.
 *
 * Displays all factions with the player's current reputation, organised
 * by reputation tier (Allied → Enemy).  Players can:
 *   • Browse the faction list to see reputation and status.
 *   • Select a faction to view full detail: philosophy, government type,
 *     current activity, territory, origin story, and available benefits.
 *   • Send a diplomatic gift (spend 500 credits per reputation point).
 *
 * Design: Alpha Centauri-style information-dense two-column layout.
 * Status badges are colour-coded to match the reputation tier.
 */

import { state }  from "../state.js";
import {
    getFactions,
    getFaction,
    factionAction,
} from "../api.js";
import { notify } from "../ui/notifications.js";
import { showModal, closeModal } from "../ui/modal.js";


// ---------------------------------------------------------------------------
// Module-level state
// ---------------------------------------------------------------------------

/** Summary list from /api/factions */
let _factions = [];

/** Full detail of the selected faction */
let _selectedFaction = null;


// ---------------------------------------------------------------------------
// Reputation tier metadata (colour, label)
// ---------------------------------------------------------------------------
const STATUS_META = {
    "Allied":      { color: "var(--accent-green)",  label: "Allied" },
    "Friendly":    { color: "var(--accent-teal)",   label: "Friendly" },
    "Cordial":     { color: "var(--accent-cyan)",   label: "Cordial" },
    "Neutral":     { color: "var(--text-dim)",      label: "Neutral" },
    "Unfriendly":  { color: "var(--accent-orange)", label: "Unfriendly" },
    "Hostile":     { color: "var(--accent-red)",    label: "Hostile" },
    "Enemy":       { color: "var(--text-red)",      label: "Enemy" },
};


// ---------------------------------------------------------------------------
// Public view object
// ---------------------------------------------------------------------------

export const diplomacyView = {

    async mount() {
        const container = document.getElementById("view-diplomacy");
        if (!container) return;

        container.innerHTML = _buildChrome();

        await _loadFactions();
        _renderFactionList();
    },

    unmount() {
        _factions         = [];
        _selectedFaction  = null;
    },
};


// ---------------------------------------------------------------------------
// Data loading
// ---------------------------------------------------------------------------

async function _loadFactions() {
    try {
        const result = await getFactions();
        _factions = result.factions || [];
    } catch (err) {
        notify("ERROR", `Could not load faction data: ${err.message}`);
        _factions = [];
    }
}

async function _loadFactionDetail(factionName) {
    try {
        _selectedFaction = await getFaction(factionName);
    } catch (err) {
        notify("ERROR", `Could not load faction details: ${err.message}`);
        _selectedFaction = null;
    }
}


// ---------------------------------------------------------------------------
// Faction list (left panel)
// ---------------------------------------------------------------------------

function _renderFactionList() {
    const listEl = document.getElementById("diplomacy-faction-list");
    if (!listEl) return;

    if (!_factions.length) {
        listEl.innerHTML = `<p class="muted" style="padding:var(--sp-3)">No faction data available.</p>`;
        return;
    }

    // Group by status tier for visual clarity
    const tierOrder = ["Allied","Friendly","Cordial","Neutral","Unfriendly","Hostile","Enemy"];
    const grouped   = {};
    for (const tier of tierOrder) grouped[tier] = [];
    for (const f of _factions) {
        if (grouped[f.status]) grouped[f.status].push(f);
        else grouped["Neutral"].push(f);
    }

    let html = "";
    for (const tier of tierOrder) {
        if (!grouped[tier].length) continue;
        const meta = STATUS_META[tier] || {};
        html += `<div class="diplo-tier-header" style="color:${meta.color}">${tier}</div>`;
        for (const f of grouped[tier]) {
            const selected = _selectedFaction?.name === f.name ? "diplo-faction-row--selected" : "";
            const repBar   = _repBar(f.reputation);
            html += `
                <div class="diplo-faction-row ${selected}" data-name="${esc(f.name)}">
                    <div class="diplo-faction-row__name">${esc(f.name)}</div>
                    <div class="diplo-faction-row__focus muted">${esc(f.primary_focus)}</div>
                    <div class="diplo-faction-row__repbar">${repBar}</div>
                    <div class="diplo-faction-row__rep" style="color:${meta.color}">
                        ${f.reputation > 0 ? "+" : ""}${f.reputation}
                    </div>
                </div>
            `;
        }
    }

    listEl.innerHTML = html;

    // Wire click — fetch full detail then re-render right panel
    listEl.querySelectorAll(".diplo-faction-row").forEach(row => {
        row.addEventListener("click", async () => {
            const name = row.dataset.name;
            await _loadFactionDetail(name);
            // Update selection highlight
            listEl.querySelectorAll(".diplo-faction-row").forEach(r =>
                r.classList.toggle("diplo-faction-row--selected", r === row)
            );
            _renderDetailPanel();
        });
    });
}

/**
 * Build a small horizontal reputation bar using CSS clip.
 * Range -100 to +100, mapped to 0–100% width.
 * @param {number} rep
 * @returns {string} HTML
 */
function _repBar(rep) {
    const pct    = Math.round((rep + 100) / 2);   // -100→0%, 0→50%, +100→100%
    const color  = rep >= 50  ? "var(--accent-green)"
                 : rep >= 0   ? "var(--accent-teal)"
                 : rep >= -50 ? "var(--accent-orange)"
                 : "var(--accent-red)";
    return `
        <div class="rep-bar-track">
            <div class="rep-bar-fill" style="width:${pct}%;background:${color}"></div>
            <div class="rep-bar-midline"></div>
        </div>
    `;
}


// ---------------------------------------------------------------------------
// Detail panel (right)
// ---------------------------------------------------------------------------

function _renderDetailPanel() {
    const panel = document.getElementById("diplomacy-detail-panel");
    if (!panel) return;

    if (!_selectedFaction) {
        panel.innerHTML = `<p class="muted" style="padding:var(--sp-4)">Select a faction to view details.</p>`;
        return;
    }

    const f      = _selectedFaction;
    const meta   = STATUS_META[f.status] || { color: "var(--text-dim)" };
    const repPct = Math.round((f.reputation + 100) / 2);
    const repColor = meta.color;

    // Benefits grouped by tier
    const benefitsHtml = f.benefits?.length
        ? f.benefits.map(b => `<li class="diplo-benefit">◆ ${esc(b)}</li>`).join("")
        : `<li class="muted">No benefits at current reputation.</li>`;

    // Locked benefits preview
    const lockedBenefits = [];
    if (f.reputation < 75) lockedBenefits.push(...(f.high_rep_benefits || []));
    if (f.reputation < 50) lockedBenefits.push(...(f.mid_rep_benefits  || []));
    if (f.reputation < 25) lockedBenefits.push(...(f.low_rep_benefits  || []));
    const lockedHtml = lockedBenefits.length
        ? lockedBenefits.slice(0, 6).map(b => `<li class="diplo-benefit diplo-benefit--locked">○ ${esc(b)}</li>`).join("")
        : "";

    panel.innerHTML = `
        <div class="diplo-detail">

            <!-- Header -->
            <div class="diplo-detail__header">
                <h3 class="diplo-detail__name">${esc(f.name)}</h3>
                <span class="diplo-detail__status" style="color:${repColor}">${esc(f.status)}</span>
            </div>

            <div class="diplo-detail__tagline">${esc(f.philosophy)}</div>

            <!-- Reputation bar -->
            <div class="diplo-rep-section">
                <div class="diplo-rep-label">Reputation: <strong style="color:${repColor}">${f.reputation > 0 ? "+" : ""}${f.reputation}</strong></div>
                <div class="rep-bar-track rep-bar-track--lg">
                    <div class="rep-bar-fill" style="width:${repPct}%;background:${repColor}"></div>
                    <div class="rep-bar-midline"></div>
                </div>
                <div class="diplo-rep-tiers">
                    <span style="color:var(--text-dim)">−100</span>
                    <span style="color:var(--accent-orange)">Unfriendly</span>
                    <span style="color:var(--text-dim)">0</span>
                    <span style="color:var(--accent-teal)">Cordial</span>
                    <span style="color:var(--accent-green)">Allied</span>
                    <span style="color:var(--text-dim)">+100</span>
                </div>
            </div>

            <!-- Key stats -->
            <div class="diplo-stats">
                <div class="research-stat-row"><span>Focus</span><span>${esc(f.primary_focus)}</span></div>
                <div class="research-stat-row"><span>Government</span><span>${esc(f.government_type)}</span></div>
                <div class="research-stat-row"><span>Founded</span><span>${f.founding_year ? f.founding_year + " (" + esc(f.founding_epoch) + ")" : "Unknown"}</span></div>
                <div class="research-stat-row"><span>Current Activity</span><span class="muted">${esc(f.current_activity)}</span></div>
                <div class="research-stat-row"><span>Systems Controlled</span><span>${f.territory_count}</span></div>
            </div>

            <!-- Description -->
            ${f.description ? `
            <div class="diplo-description">${esc(f.description)}</div>` : ""}

            <!-- Origin story -->
            ${f.origin_story ? `
            <div class="diplo-origin">
                <div class="panel-subheading">Origin</div>
                <p class="diplo-lore-text">${esc(f.origin_story)}</p>
            </div>` : ""}

            <!-- Active benefits -->
            <div class="diplo-benefits-section">
                <div class="panel-subheading">Current Benefits</div>
                <ul class="diplo-benefit-list">${benefitsHtml}</ul>
                ${lockedHtml ? `<ul class="diplo-benefit-list">${lockedHtml}</ul>` : ""}
            </div>

            <!-- Preferred trades -->
            ${f.preferred_trades?.length ? `
            <div class="diplo-trades-section">
                <div class="panel-subheading">Preferred Trades</div>
                <div class="diplo-trades">${f.preferred_trades.map(t => `<span class="trade-tag">${esc(t)}</span>`).join(" ")}</div>
            </div>` : ""}

            <!-- Diplomatic action -->
            <div class="diplo-action-section">
                <div class="panel-subheading">Diplomacy</div>
                <div class="diplo-gift-row">
                    <input type="number" id="diplo-gift-amount" class="diplo-gift-input"
                           value="5" min="1" max="20" title="Reputation points (1–20)">
                    <span class="muted">pts × 500 cr</span>
                    <button class="btn btn--primary btn--sm" id="btn-diplo-gift">
                        Send Gift
                    </button>
                </div>
                <p class="muted" style="font-size:11px">Spend credits to improve standing. Capped at 20 pts per action.</p>
            </div>

        </div>
    `;

    // Wire gift button
    document.getElementById("btn-diplo-gift")?.addEventListener("click", () => {
        const amount = parseInt(document.getElementById("diplo-gift-amount")?.value || "5", 10);
        _doGift(f.name, amount);
    });
}


// ---------------------------------------------------------------------------
// Diplomatic gift action
// ---------------------------------------------------------------------------

async function _doGift(factionName, amount) {
    if (!amount || amount < 1) {
        notify("ERROR", "Enter a gift amount between 1 and 20.");
        return;
    }

    try {
        const result = await factionAction(factionName, "gift", amount);
        notify("TURN", result.message);

        // Update local summary list and selected faction with fresh rep
        const idx = _factions.findIndex(f => f.name === factionName);
        if (idx >= 0) {
            _factions[idx].reputation = result.reputation;
            _factions[idx].status     = result.status;
        }

        // Update the selected faction object too
        if (_selectedFaction?.name === factionName) {
            _selectedFaction.reputation = result.reputation;
            _selectedFaction.status     = result.status;
        }

        // Credits changed — update state so HUD reflects it
        if (state.gameState?.player) {
            state.gameState.player.credits = result.credits_remaining;
        }

        // Re-render both panels to show new reputation
        _renderFactionList();
        _renderDetailPanel();

    } catch (err) {
        notify("ERROR", err.message || "Gift failed.");
    }
}


// ---------------------------------------------------------------------------
// Static chrome
// ---------------------------------------------------------------------------

function _buildChrome() {
    return `
        <div class="view-inner diplomacy-view-inner">

            <!-- Left: faction list -->
            <aside class="panel panel--left diplomacy-left" id="diplomacy-left-panel">
                <div class="panel-section">
                    <h2 class="panel-title">Factions</h2>
                    <p class="muted" style="font-size:11px">Click a faction to view details and diplomatic options.</p>
                </div>
                <div id="diplomacy-faction-list" class="diplomacy-faction-list">
                    <p class="muted" style="padding:var(--sp-3)">Loading…</p>
                </div>
            </aside>

            <!-- Right: selected faction detail -->
            <main class="panel diplomacy-detail-area" id="diplomacy-detail-panel">
                <p class="muted" style="padding:var(--sp-4)">Select a faction to view details.</p>
            </main>

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
