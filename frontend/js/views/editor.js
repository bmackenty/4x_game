/**
 * views/editor.js — WYSIWYG Lore JSON editor.
 *
 * Detects file structure and renders form-based editing:
 *   categorized → tabs + item cards  (e.g. ship_components.json)
 *   list        → searchable cards   (e.g. species.json)
 *   config      → flat key/value     (e.g. game_config.json)
 *   mixed       → expandable sections
 * Raw JSON fallback always available via toggle.
 */

import { editorListFiles, editorGetFile, editorSaveFile, editorValidate } from "../api.js";

// Ship attribute IDs — mirrors ship_attributes.py ALL_ATTRIBUTE_IDS
const SHIP_ATTR_IDS = [
  "hull_integrity","armor_strength","mass_efficiency",
  "engine_output","engine_efficiency","ftl_jump_capacity","maneuverability",
  "reactor_output","energy_storage",
  "detection_range","scan_resolution","etheric_sensitivity",
  "ai_processing_power","ai_convergence","decision_latency",
  "cognitive_security","ship_sentience","human_ai_symbiosis",
  "ethical_constraints","dream_state_processing",
];

// Keys whose string values should use a textarea
const TEXTAREA_KEYS = new Set([
  "lore","description","text","origin_story","founding_lore",
  "philosophy","summary","detail","bio","flavor",
]);

// Keys to hide from the form
const SKIP_KEYS = new Set(["_comment","_note","_version"]);


// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

let _files          = [];
let _active         = null;
let _data           = null;
let _savedJson      = "";
let _rawMode        = false;
let _rawContent     = "";
let _activeCategory = null;
let _expandedPath   = null;
let _searchQuery    = "";
let _container      = null;


// ---------------------------------------------------------------------------
// Public
// ---------------------------------------------------------------------------

export const editorView = { mount, unmount };

async function mount(context = {}) {
  _container = document.getElementById("view-editor");
  if (!_container) return;
  _container.innerHTML = `<p class="editor-loading">Loading lore files…</p>`;
  try {
    const r = await editorListFiles();
    _files = r.files || [];
  } catch (err) {
    _container.innerHTML = `<p class="editor-error">Could not load file list: ${err.message}</p>`;
    return;
  }
  if (context.filename) await _openFile(context.filename);
  else { _active = null; _data = null; }
  _render();
}

function unmount() { _container = null; }


// ---------------------------------------------------------------------------
// Path helpers
// ---------------------------------------------------------------------------

function _segs(path) {
  const out = [];
  for (const m of String(path).matchAll(/(\w+)|\[(\d+)\]/g))
    out.push(m[1] !== undefined ? m[1] : parseInt(m[2]));
  return out;
}

function _getByPath(path) {
  return _segs(path).reduce((o, k) => o?.[k], _data);
}

function _setByPath(path, val) {
  const s = _segs(path);
  let o = _data;
  for (let i = 0; i < s.length - 1; i++) o = o[s[i]];
  o[s[s.length - 1]] = val;
}

function _deleteByPath(path) {
  const s = _segs(path);
  let o = _data;
  for (let i = 0; i < s.length - 1; i++) o = o[s[i]];
  const k = s[s.length - 1];
  Array.isArray(o) ? o.splice(k, 1) : delete o[k];
}


// ---------------------------------------------------------------------------
// Layout detection
// ---------------------------------------------------------------------------

function _detectLayout(data) {
  if (Array.isArray(data)) return "list";
  if (typeof data !== "object" || !data) return "raw";
  const keys = Object.keys(data).filter(k => !k.startsWith("_"));
  if (!keys.length) return "raw";
  const vals = keys.map(k => data[k]);
  if (vals.every(v => Array.isArray(v)))                                   return "categorized";
  if (vals.every(v => typeof v !== "object" || v === null))                return "config";
  return "mixed";
}


// ---------------------------------------------------------------------------
// Render
// ---------------------------------------------------------------------------

function _render() {
  if (!_container) return;
  _container.innerHTML = _buildHtml();
  _wire();
}

function _buildHtml() {
  return `
    <div class="editor-view">
      ${_buildSidebar()}
      <div class="editor-main">
        ${_active && _data
          ? _buildMain()
          : `<div class="editor-empty"><p>Select a file from the list to begin editing.</p></div>`}
      </div>
    </div>`;
}

function _buildSidebar() {
  const items = _files.map(f => {
    const a = f.filename === _active ? " editor-file-item--active" : "";
    return `<button class="editor-file-item${a}" data-filename="${f.filename}" title="${_esc(f.description)}">
      <span class="editor-file-item__title">${_esc(f.title)}</span>
      <span class="editor-file-item__size">${f.size_kb} KB</span>
    </button>`;
  }).join("");
  return `
    <div class="editor-sidebar">
      <div class="editor-sidebar__header">LORE FILES</div>
      <div class="editor-file-list">${items}</div>
      <button class="editor-validate-btn" id="editor-validate-btn">CHECK ATTRIBUTES</button>
      <button class="editor-exit-btn"     id="editor-exit-btn">← MAIN MENU</button>
    </div>`;
}

function _buildMain() {
  const meta  = _files.find(f => f.filename === _active) || {};
  const dirty = _isDirty();
  const layout = _rawMode ? "raw" : _detectLayout(_data);
  return `
    <div class="editor-panel">
      <div class="editor-panel__header">
        <div class="editor-panel__meta">
          <h3 class="editor-panel__title">${_esc(meta.title || _active)}</h3>
          <p class="editor-panel__desc">${_esc(meta.description || "")}</p>
        </div>
        <div class="editor-panel__toolbar">
          <span class="editor-dirty-badge ${dirty ? "editor-dirty-badge--visible" : ""}" id="editor-dirty">UNSAVED</span>
          <button class="editor-btn ${_rawMode ? "editor-btn--active" : ""}" id="editor-toggle-raw">${_rawMode ? "◈ WYSIWYG" : "{} RAW"}</button>
          <button class="editor-btn editor-btn--save" id="editor-save-btn">SAVE</button>
        </div>
      </div>
      <div class="editor-body">
        ${layout === "raw" ? _buildRaw() : _buildWysiwyg(layout)}
      </div>
    </div>`;
}

// ── Raw ──────────────────────────────────────────────────────────────────────

function _buildRaw() {
  return `<textarea class="editor-textarea" id="editor-textarea"
    spellcheck="false" autocomplete="off">${_esc(_rawContent)}</textarea>`;
}

// ── WYSIWYG dispatcher ───────────────────────────────────────────────────────

function _buildWysiwyg(layout) {
  switch (layout) {
    case "categorized": return _buildCategorized();
    case "list":        return _buildListWrap(_data, "");
    case "config":      return _buildConfig();
    default:            return _buildMixed();
  }
}

// ── Categorized: {cat: [items]} ──────────────────────────────────────────────

function _buildCategorized() {
  const cats = Object.keys(_data).filter(k => !k.startsWith("_") && Array.isArray(_data[k]));
  if (!_activeCategory || !cats.includes(_activeCategory)) _activeCategory = cats[0];
  const tabs = cats.map(c => {
    const a = c === _activeCategory ? " editor-tab--active" : "";
    return `<button class="editor-tab${a}" data-cat="${c}">
      ${_esc(c)} <span class="editor-tab__count">${(_data[c]||[]).length}</span>
    </button>`;
  }).join("");
  return `
    <div class="editor-tabs">${tabs}</div>
    ${_buildListWrap(_data[_activeCategory] || [], _activeCategory)}`;
}

// ── List view ─────────────────────────────────────────────────────────────────

function _buildListWrap(items, base) {
  const q = _searchQuery.toLowerCase();
  const searchBar = items.length > 8
    ? `<div class="editor-search-bar">
         <input class="editor-search-input" id="editor-search" type="text"
           placeholder="Filter items…" value="${_esc(_searchQuery)}">
       </div>` : "";
  const filtered = q ? items.filter(i => JSON.stringify(i).toLowerCase().includes(q)) : items;
  const cards = filtered.map(item => {
    const realIdx = items.indexOf(item);
    const path = base ? `${base}[${realIdx}]` : `[${realIdx}]`;
    return _buildItemCard(item, path);
  }).join("");
  return `
    <div class="editor-list-wrap">
      ${searchBar}
      <div class="editor-item-list">${cards}</div>
      <button class="editor-add-btn editor-add-btn--full" data-add-to="${base}">+ Add item</button>
    </div>`;
}

// ── Item card ────────────────────────────────────────────────────────────────

function _buildItemCard(item, path) {
  const exp   = _expandedPath === path;
  const title = item?.name || item?.title || item?.id || path;
  return `
    <div class="editor-item ${exp ? "editor-item--expanded" : ""}" data-path="${path}">
      <div class="editor-item__header" data-toggle="${path}">
        <span class="editor-item__name">${_esc(String(title))}</span>
        <span class="editor-item__preview">${exp ? "" : _buildPreview(item)}</span>
        <span class="editor-item__chevron">${exp ? "▴" : "▾"}</span>
      </div>
      ${exp ? `
        <div class="editor-item__form">
          ${_buildObjForm(item, path)}
          <div class="editor-item__actions">
            <button class="editor-delete-btn" data-delete-path="${path}">⊗ Delete item</button>
          </div>
        </div>` : ""}
    </div>`;
}

// ── Config: flat key → scalar ────────────────────────────────────────────────

function _buildConfig() {
  const keys = Object.keys(_data).filter(k => !k.startsWith("_"));
  const rows = keys.map(k => {
    const v = _data[k];
    return `
      <div class="editor-field-row">
        <label class="editor-field-label">${_esc(k.replace(/_/g, " "))}</label>
        <div class="editor-field-value">${_buildFieldEditor(k, v, k)}</div>
      </div>`;
  }).join("");
  return `<div class="editor-config-form">${rows}</div>`;
}

// ── Mixed: object with heterogeneous values ───────────────────────────────────

function _buildMixed() {
  const keys = Object.keys(_data).filter(k => !k.startsWith("_"));
  const cards = keys.map(k => {
    const path = k;
    const exp  = _expandedPath === path;
    const val  = _data[k];
    const preview = typeof val === "object" && val
      ? _buildPreview(val)
      : `<span class="editor-preview-pill">${_esc(String(val)).slice(0,40)}</span>`;
    return `
      <div class="editor-item ${exp ? "editor-item--expanded" : ""}" data-path="${path}">
        <div class="editor-item__header" data-toggle="${path}">
          <span class="editor-item__name">${_esc(k)}</span>
          <span class="editor-item__preview">${exp ? "" : preview}</span>
          <span class="editor-item__chevron">${exp ? "▴" : "▾"}</span>
        </div>
        ${exp ? `<div class="editor-item__form">
          ${typeof val === "object" && val && !Array.isArray(val)
            ? _buildObjForm(val, path)
            : _buildFieldEditor(k, val, path)}
        </div>` : ""}
      </div>`;
  }).join("");
  return `<div class="editor-list-wrap"><div class="editor-item-list">${cards}</div></div>`;
}

// ── Object form ───────────────────────────────────────────────────────────────

function _buildObjForm(obj, path) {
  if (!obj || typeof obj !== "object" || Array.isArray(obj)) return "";
  return Object.keys(obj).filter(k => !SKIP_KEYS.has(k)).map(k => `
    <div class="editor-field-row">
      <label class="editor-field-label">${_esc(k.replace(/_/g, " "))}</label>
      <div class="editor-field-value">${_buildFieldEditor(k, obj[k], `${path}.${k}`)}</div>
    </div>`).join("");
}

// ── Field editor ──────────────────────────────────────────────────────────────

function _buildFieldEditor(key, value, path) {
  // Special: ship modifiers
  if (key === "modifiers" && value && typeof value === "object" && !Array.isArray(value))
    return _buildModifiersEditor(value, path);

  if (value === null)
    return `<input type="text" class="editor-input editor-input--nullable" data-path="${path}" data-type="null" value="" placeholder="(none)">`;

  if (typeof value === "boolean")
    return `<label class="editor-checkbox-label">
      <input type="checkbox" class="editor-checkbox" data-path="${path}" ${value ? "checked" : ""}>${value ? " Yes" : " No"}
    </label>`;

  if (typeof value === "number")
    return `<input type="number" class="editor-input editor-input--number" data-path="${path}" value="${value}" step="any">`;

  if (typeof value === "string") {
    if (TEXTAREA_KEYS.has(key) || value.length > 100)
      return `<textarea class="editor-input editor-input--textarea" data-path="${path}" rows="3">${_esc(value)}</textarea>`;
    return `<input type="text" class="editor-input" data-path="${path}" value="${_escAttr(value)}">`;
  }

  if (Array.isArray(value)) {
    if (!value.length || value.every(v => typeof v !== "object" || v === null))
      return _buildTagEditor(value, path);
    return `<textarea class="editor-input editor-input--textarea editor-input--json"
      data-path="${path}" data-json="true" rows="4">${_esc(JSON.stringify(value, null, 2))}</textarea>`;
  }

  if (typeof value === "object")
    return `<textarea class="editor-input editor-input--textarea editor-input--json"
      data-path="${path}" data-json="true" rows="4">${_esc(JSON.stringify(value, null, 2))}</textarea>`;

  return `<input type="text" class="editor-input" data-path="${path}" value="${_escAttr(String(value))}">`;
}

// ── Modifiers editor ──────────────────────────────────────────────────────────

function _buildModifiersEditor(mods, path) {
  const used = new Set(Object.keys(mods));
  const rows = Object.entries(mods).map(([attr, val]) => `
    <div class="editor-modifier-row">
      <select class="editor-modifier-attr" data-mod-path="${path}" data-mod-oldkey="${attr}">
        ${SHIP_ATTR_IDS.map(id =>
          `<option value="${id}" ${id === attr ? "selected" : ""}>${id.replace(/_/g, " ")}</option>`
        ).join("")}
      </select>
      <input type="number" class="editor-modifier-val" data-mod-path="${path}" data-mod-key="${attr}" value="${val}" step="1">
      <button class="editor-modifier-del" data-mod-path="${path}" data-mod-key="${attr}" title="Remove">×</button>
    </div>`).join("");

  const firstUnused = SHIP_ATTR_IDS.find(id => !used.has(id)) || SHIP_ATTR_IDS[0];
  return `
    <div class="editor-modifiers" data-path="${path}">
      ${rows}
      <button class="editor-modifier-add" data-mod-path="${path}" data-mod-newkey="${firstUnused}">+ Add modifier</button>
    </div>`;
}

// ── Tag editor ────────────────────────────────────────────────────────────────

function _buildTagEditor(values, path) {
  const pills = values.map((v, i) => `
    <span class="editor-tag">
      ${_esc(v === null ? "null" : String(v))}
      <button class="editor-tag-del" data-path="${path}" data-index="${i}">×</button>
    </span>`).join("");
  return `
    <div class="editor-tags" data-path="${path}">
      ${pills}
      <input type="text" class="editor-tag-input" data-path="${path}" placeholder="Add…" size="10">
    </div>`;
}

// ── Preview pills ─────────────────────────────────────────────────────────────

function _buildPreview(item) {
  if (!item || typeof item !== "object") return "";
  const bits = [];
  if (item.cost != null)           bits.push(`◈ ${Number(item.cost).toLocaleString()}`);
  if (item.failure_chance != null) bits.push(`${(item.failure_chance * 100).toFixed(1)}% risk`);
  if (item.category != null)       bits.push(item.category);
  if (item.time != null)           bits.push(`${item.time}t`);
  if (item.rp_cost != null)        bits.push(`${item.rp_cost} RP`);
  if (item.faction_lock) {
    const fl = Array.isArray(item.faction_lock) ? item.faction_lock.join(", ") : item.faction_lock;
    if (fl) bits.push(fl);
  }
  if (item.modifiers) bits.push(`${Object.keys(item.modifiers).length} mods`);
  return bits.map(b => `<span class="editor-preview-pill">${_esc(b)}</span>`).join("");
}


// ---------------------------------------------------------------------------
// Event wiring
// ---------------------------------------------------------------------------

function _wire() {
  if (!_container) return;

  // File list
  _container.querySelectorAll(".editor-file-item").forEach(btn =>
    btn.addEventListener("click", async () => {
      const fn = btn.dataset.filename;
      if (fn === _active) return;
      if (_active && _isDirty() && !confirm(`Discard unsaved changes to ${_active}?`)) return;
      await _openFile(fn);
    })
  );

  // Sidebar actions
  _container.querySelector("#editor-validate-btn")?.addEventListener("click", _runValidation);
  _container.querySelector("#editor-exit-btn")?.addEventListener("click", async () => {
    if (_active && _isDirty() && !confirm(`Discard unsaved changes to ${_active}?`)) return;
    const { switchView } = await import("../main.js");
    switchView("title");
  });

  // Toolbar
  _container.querySelector("#editor-save-btn")?.addEventListener("click", _save);
  _container.querySelector("#editor-toggle-raw")?.addEventListener("click", _toggleRaw);

  // Category tabs
  _container.querySelectorAll(".editor-tab").forEach(btn =>
    btn.addEventListener("click", () => {
      _activeCategory = btn.dataset.cat;
      _expandedPath = null;
      _searchQuery = "";
      _render();
    })
  );

  // Search
  _container.querySelector("#editor-search")?.addEventListener("input", e => {
    _searchQuery = e.target.value;
    _render();
  });

  // Item expand/collapse
  _container.querySelectorAll("[data-toggle]").forEach(el =>
    el.addEventListener("click", () => {
      const p = el.dataset.toggle;
      _expandedPath = _expandedPath === p ? null : p;
      _render();
    })
  );

  // Delete item
  _container.querySelectorAll("[data-delete-path]").forEach(btn =>
    btn.addEventListener("click", e => {
      e.stopPropagation();
      if (!confirm("Delete this item?")) return;
      _deleteByPath(btn.dataset.deletePath);
      _expandedPath = null;
      _markDirty();
      _render();
    })
  );

  // Add item
  _container.querySelectorAll("[data-add-to]").forEach(btn =>
    btn.addEventListener("click", e => {
      e.stopPropagation();
      const base = btn.dataset.addTo;
      const arr  = base ? _getByPath(base) : _data;
      if (!Array.isArray(arr)) return;
      const tmpl = arr.length ? _blankLike(arr[0]) : { name: "New Item" };
      arr.push(tmpl);
      const newIdx = arr.length - 1;
      _expandedPath = base ? `${base}[${newIdx}]` : `[${newIdx}]`;
      _markDirty();
      _render();
    })
  );

  // Generic inputs — text, number, textarea
  _container.querySelectorAll("[data-path]").forEach(el => {
    const path = el.dataset.path;
    if (el.classList.contains("editor-tag-input"))   return;
    if (el.classList.contains("editor-modifier-val") || el.classList.contains("editor-modifier-attr")) return;

    if (el.dataset.json === "true") {
      el.addEventListener("change", () => {
        try {
          _setByPath(path, JSON.parse(el.value));
          el.classList.remove("editor-input--error");
          _markDirty();
        } catch { el.classList.add("editor-input--error"); }
      });
      return;
    }

    if (el.type === "checkbox") {
      el.addEventListener("change", () => { _setByPath(path, el.checked); _markDirty(); });
      return;
    }

    el.addEventListener(el.tagName === "SELECT" ? "change" : "input", () => {
      let val;
      if (el.type === "number")                       val = el.value === "" ? null : parseFloat(el.value);
      else if (el.dataset.type === "null" && !el.value) val = null;
      else                                            val = el.value;
      _setByPath(path, val);
      _markDirty();
    });
  });

  // Tag pills
  _container.querySelectorAll(".editor-tag-del").forEach(btn =>
    btn.addEventListener("click", e => {
      e.stopPropagation();
      const arr = _getByPath(btn.dataset.path);
      if (Array.isArray(arr)) { arr.splice(parseInt(btn.dataset.index), 1); _markDirty(); _render(); }
    })
  );
  _container.querySelectorAll(".editor-tag-input").forEach(inp =>
    inp.addEventListener("keydown", e => {
      if (e.key !== "Enter" && e.key !== ",") return;
      e.preventDefault();
      const v = inp.value.trim();
      if (!v) return;
      const arr = _getByPath(inp.dataset.path);
      if (Array.isArray(arr)) { arr.push(v === "null" ? null : v); _markDirty(); _render(); }
    })
  );

  // Modifier value
  _container.querySelectorAll(".editor-modifier-val").forEach(inp =>
    inp.addEventListener("input", () => {
      const mods = _getByPath(inp.dataset.modPath);
      if (mods) { mods[inp.dataset.modKey] = parseFloat(inp.value) || 0; _markDirty(); }
    })
  );

  // Modifier key rename
  _container.querySelectorAll(".editor-modifier-attr").forEach(sel =>
    sel.addEventListener("change", () => {
      const mods = _getByPath(sel.dataset.modPath);
      if (!mods) return;
      const oldKey = sel.dataset.modOldkey;
      const newKey = sel.value;
      if (oldKey === newKey) return;
      const rebuilt = {};
      for (const [k, v] of Object.entries(mods)) rebuilt[k === oldKey ? newKey : k] = v;
      _setByPath(sel.dataset.modPath, rebuilt);
      _markDirty();
      _render();
    })
  );

  // Modifier delete
  _container.querySelectorAll(".editor-modifier-del").forEach(btn =>
    btn.addEventListener("click", e => {
      e.stopPropagation();
      const mods = _getByPath(btn.dataset.modPath);
      if (mods) { delete mods[btn.dataset.modKey]; _markDirty(); _render(); }
    })
  );

  // Modifier add
  _container.querySelectorAll(".editor-modifier-add").forEach(btn =>
    btn.addEventListener("click", e => {
      e.stopPropagation();
      const mods = _getByPath(btn.dataset.modPath);
      if (mods) { mods[btn.dataset.modNewkey] = 0; _markDirty(); _render(); }
    })
  );

  // Raw textarea
  const ta = _container.querySelector("#editor-textarea");
  if (ta) {
    ta.addEventListener("input", () => { _rawContent = ta.value; _markDirty(); });
    ta.addEventListener("keydown", e => {
      if ((e.ctrlKey || e.metaKey) && e.key === "s") { e.preventDefault(); _save(); }
      if (e.key === "Tab") {
        e.preventDefault();
        const s = ta.selectionStart;
        ta.value = ta.value.slice(0, s) + "  " + ta.value.slice(ta.selectionEnd);
        ta.selectionStart = ta.selectionEnd = s + 2;
        _rawContent = ta.value;
      }
    });
  }
}


// ---------------------------------------------------------------------------
// File operations
// ---------------------------------------------------------------------------

async function _openFile(filename) {
  try {
    const r   = await editorGetFile(filename);
    _active   = filename;
    _data     = JSON.parse(r.content);
    _savedJson = JSON.stringify(_data, null, 2);
    _rawContent = _savedJson;
    _rawMode  = false;
    _activeCategory = null;
    _expandedPath   = null;
    _searchQuery    = "";
    _render();
  } catch (err) { alert(`Could not load ${filename}: ${err.message}`); }
}

async function _save() {
  if (!_active) return;
  let content;
  if (_rawMode) {
    try { JSON.parse(_rawContent); } catch (e) { alert(`JSON error: ${e.message}`); return; }
    content = _rawContent;
  } else {
    content = JSON.stringify(_data, null, 2);
  }
  try {
    await editorSaveFile(_active, content);
    _savedJson  = content;
    _rawContent = content;
    _markDirty();
    _render();
  } catch (err) { alert(`Save failed: ${err.message}`); }
}

function _toggleRaw() {
  if (_rawMode) {
    try { _data = JSON.parse(_rawContent); _rawMode = false; }
    catch (e) { alert(`Cannot switch — JSON is invalid: ${e.message}`); return; }
  } else {
    _rawContent = JSON.stringify(_data, null, 2);
    _rawMode = true;
  }
  _render();
}


// ---------------------------------------------------------------------------
// Dirty tracking
// ---------------------------------------------------------------------------

function _isDirty() {
  if (_rawMode) return _rawContent !== _savedJson;
  try { return JSON.stringify(_data, null, 2) !== _savedJson; } catch { return true; }
}

function _markDirty() {
  const b = _container?.querySelector("#editor-dirty");
  if (b) b.classList.toggle("editor-dirty-badge--visible", _isDirty());
}


// ---------------------------------------------------------------------------
// Validation
// ---------------------------------------------------------------------------

async function _runValidation() {
  const btn = _container?.querySelector("#editor-validate-btn");
  if (btn) btn.textContent = "CHECKING…";
  let result;
  try { result = await editorValidate(); }
  catch (err) { alert(`Validation error: ${err.message}`); if (btn) btn.textContent = "CHECK ATTRIBUTES"; return; }
  if (btn) btn.textContent = "CHECK ATTRIBUTES";

  const { issues, valid } = result;
  let body;
  if (valid) {
    body = `<p class="editor-validate-ok">✓ All attribute references are valid.</p>`;
  } else {
    const rows = issues.map(i => i.type === "parse_error"
      ? `<div class="editor-issue editor-issue--error">
           <span class="editor-issue__file">${i.file}</span>
           <span class="editor-issue__detail">Parse error: ${_esc(i.detail)}</span>
         </div>`
      : `<div class="editor-issue">
           <span class="editor-issue__file">${i.file}</span>
           <span class="editor-issue__comp">${_esc(i.component)}</span>
           <span class="editor-issue__attr">${_esc(i.attribute)}</span>
           <span class="editor-issue__detail">${_esc(i.detail)}</span>
         </div>`
    ).join("");
    body = `<p class="editor-validate-count">${issues.length} issue${issues.length !== 1 ? "s" : ""}:</p>
            <div class="editor-issue-list">${rows}</div>`;
  }
  import("../ui/modal.js").then(({ showModal, closeModal }) =>
    showModal(
      valid ? "ATTRIBUTE CHECK — PASS" : "ATTRIBUTE CHECK — ISSUES FOUND",
      body,
      [{ label: "CLOSE", className: "btn--secondary", onClick: () => closeModal() }],
      { wide: !valid }
    )
  );
}


// ---------------------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------------------

function _blankLike(sample) {
  const b = {};
  for (const [k, v] of Object.entries(sample)) {
    if (typeof v === "string")      b[k] = "";
    else if (typeof v === "number") b[k] = 0;
    else if (typeof v === "boolean") b[k] = false;
    else if (v === null)            b[k] = null;
    else if (Array.isArray(v))      b[k] = [];
    else if (typeof v === "object") b[k] = {};
  }
  return b;
}

function _esc(s) {
  return String(s ?? "")
    .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}
function _escAttr(s) {
  return String(s ?? "").replace(/"/g,"&quot;").replace(/'/g,"&#39;");
}
