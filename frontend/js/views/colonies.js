/**
 * frontend/js/views/colonies.js - Empire-wide colony management screen.
 */

import { getColonyOverview } from "../api.js";
import { notify }            from "../ui/notifications.js";

let _data = null;

export const coloniesView = {
    async mount() {
        const container = document.getElementById("view-colonies");
        if (!container) return;
        container.innerHTML = _buildChrome();
        document.getElementById("colonies-back-btn")
            ?.addEventListener("click", async () => {
                const { switchView } = await import("../main.js");
                switchView("galaxy");
            });
        await _refresh();
    },
    unmount() { _data = null; },
};

async function _refresh() {
    try {
        _data = await getColonyOverview();
    } catch (err) {
        notify("ERROR", `Could not load colony overview: ${err.message}`);
        _data = { colonies: [], totals: { colony_count: 0, population: 0, income: 0, production: {} } };
    }
    _renderSummaryPanel();
    _renderColonyList();
}

function _renderSummaryPanel() {
    const panel = document.getElementById("colonies-summary");
    if (!panel || !_data) return;
    const t    = _data.totals;
    const prod = t.production || {};
    const ICONS = { credits: "◈", minerals: "⬡", food: "❖", research: "⚗", ether: "✦", defense: "⛨" };
    const prodRows = Object.entries(prod)
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([k, v]) => {
            const icon = ICONS[k] || "·";
            return `<div class="col-summary-stat"><span class="col-summary-icon">${icon}</span><span class="col-summary-label">${k}</span><span class="col-summary-val">+${v}/turn</span></div>`;
        }).join("");
    panel.innerHTML = `
        <h3 class="col-summary-heading">EMPIRE OVERVIEW</h3>
        <div class="col-summary-block">
            <div class="col-summary-stat col-summary-stat--highlight"><span class="col-summary-label">Colonies</span><span class="col-summary-val">${t.colony_count}</span></div>
            <div class="col-summary-stat col-summary-stat--highlight"><span class="col-summary-label">Population</span><span class="col-summary-val">${(t.population||0).toLocaleString()}</span></div>
            <div class="col-summary-stat col-summary-stat--highlight"><span class="col-summary-label">Total income</span><span class="col-summary-val col-income">+${(t.income||0).toLocaleString()} cr</span></div>
        </div>
        <h4 class="col-summary-subheading">Production / Turn</h4>
        <div class="col-summary-block">${prodRows || '<p class="muted" style="font-size:var(--font-size-xs)">No colonies yet.</p>'}</div>
    `;
}

function _renderColonyList() {
    const list = document.getElementById("colonies-list");
    if (!list || !_data) return;
    if (!_data.colonies.length) {
        list.innerHTML = `<div class="col-empty"><p>No colonies established yet.</p><p class="muted">Found a colony from the system panel on the galaxy map.</p></div>`;
        return;
    }
    const sorted = [..._data.colonies].sort((a, b) =>
        a.system_name.localeCompare(b.system_name) || a.planet_name.localeCompare(b.planet_name)
    );
    list.innerHTML = sorted.map(_buildColonyCard).join("");
    list.querySelectorAll(".col-card__open-btn").forEach(btn => {
        btn.addEventListener("click", async () => {
            const { switchView } = await import("../main.js");
            switchView("colony", { planetName: btn.dataset.planet, systemName: btn.dataset.system, planetType: btn.dataset.type });
        });
    });
}

function _buildColonyCard(col) {
    const ICONS = { credits: "◈", minerals: "⬡", food: "❖", research: "⚗", ether: "✦", defense: "⛨" };
    const prodChips = Object.entries(col.production || {})
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([k, v]) => `<span class="col-card__prod-chip">${ICONS[k]||"·"} +${v} ${k}</span>`)
        .join("");
    const impEntries = Object.entries(col.improvements || {});
    const impHtml = impEntries.length
        ? impEntries.map(([name, count]) =>
            `<span class="col-card__imp">${count > 1 ? `<span class="col-card__imp-count">x${count}</span> ` : ""}${name}</span>`
          ).join("")
        : `<span class="muted" style="font-size:var(--font-size-xs)">No improvements built</span>`;
    const incomeDetail = `<span class="col-card__income-detail">pop ${col.pop_income.toLocaleString()} + bldg ${col.bldg_income.toLocaleString()}</span>`;
    return `
        <div class="col-card">
            <div class="col-card__header">
                <div class="col-card__title-block">
                    <span class="col-card__name">${col.planet_name}</span>
                    <span class="col-card__system">${col.system_name}</span>
                    <span class="col-card__type">${col.planet_type}</span>
                </div>
                <button class="btn btn--primary btn--sm col-card__open-btn" data-planet="${col.planet_name}" data-system="${col.system_name}" data-type="${col.planet_type}">OPEN</button>
            </div>
            <div class="col-card__stats">
                <div class="col-card__stat"><span class="col-card__stat-label">Population</span><span class="col-card__stat-val">${col.population.toLocaleString()}</span></div>
                <div class="col-card__stat"><span class="col-card__stat-label">Founded turn</span><span class="col-card__stat-val">${col.founded_turn}</span></div>
                <div class="col-card__stat"><span class="col-card__stat-label">Tiles developed</span><span class="col-card__stat-val">${col.improvement_count} / ${col.tile_count}</span></div>
                <div class="col-card__stat"><span class="col-card__stat-label">Income / turn</span><span class="col-card__stat-val col-income">+${col.income.toLocaleString()} cr</span>${incomeDetail}</div>
            </div>
            ${prodChips ? `<div class="col-card__prod"><span class="col-card__prod-label">Production:</span>${prodChips}</div>` : ""}
            <div class="col-card__improvements"><span class="col-card__imp-label">Improvements:</span>${impHtml}</div>
        </div>
    `;
}

function _buildChrome() {
    return `
        <div class="view-inner colonies-view-inner">
            <aside class="panel panel--left" id="colonies-left">
                <div class="panel-section">
                    <button id="colonies-back-btn" class="btn btn--secondary btn--sm">← Galaxy Map</button>
                </div>
                <div id="colonies-summary" class="panel-section"><p class="muted">Loading...</p></div>
            </aside>
            <main class="colonies-main">
                <div class="colonies-header"><h2 class="colonies-title">Colony Management</h2></div>
                <div id="colonies-list" class="colonies-list"><p class="muted">Loading...</p></div>
            </main>
        </div>
    `;
}
