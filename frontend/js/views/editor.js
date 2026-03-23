/**
 * views/editor.js — Lore JSON file editor.
 *
 * Lets designers view and edit any file in the lore/ directory directly
 * from the browser. Also runs attribute validation across all files.
 *
 * Accessible from the title screen; no game session required.
 */

import { editorListFiles, editorGetFile, editorSaveFile, editorValidate } from "../api.js";

// ---------------------------------------------------------------------------
// Module state
// ---------------------------------------------------------------------------

let _files       = [];          // [{filename, title, description, size_kb}]
let _active      = null;        // filename of the open file
let _content     = "";          // current textarea content
let _savedContent = "";         // last-saved content (for dirty tracking)
let _container   = null;


// ---------------------------------------------------------------------------
// Public view object
// ---------------------------------------------------------------------------

export const editorView = { mount, unmount };


async function mount(context = {}) {
  _container = document.getElementById("view-editor");
  if (!_container) return;

  _container.innerHTML = `<p class="editor-loading">Loading lore files…</p>`;

  try {
    const result = await editorListFiles();
    _files = result.files || [];
  } catch (err) {
    _container.innerHTML = `<p class="editor-error">Could not load file list: ${err.message}</p>`;
    return;
  }

  // Re-open the previously active file if we're returning to the view
  if (context.filename) {
    await _openFile(context.filename);
  } else {
    _active = null;
    _content = "";
    _savedContent = "";
  }

  _render();
}

function unmount() {
  _container = null;
}


// ---------------------------------------------------------------------------
// Rendering
// ---------------------------------------------------------------------------

function _render() {
  if (!_container) return;
  _container.innerHTML = _buildHtml();
  _wire();
}

function _buildHtml() {
  const fileItems = _files.map(f => {
    const active = f.filename === _active ? " editor-file-item--active" : "";
    return `
      <button class="editor-file-item${active}" data-filename="${f.filename}">
        <span class="editor-file-item__title">${f.title}</span>
        <span class="editor-file-item__size">${f.size_kb} KB</span>
      </button>
    `;
  }).join("");

  const mainPanel = _active ? _buildEditorPanel() : `
    <div class="editor-empty">
      <p>Select a file from the list to begin editing.</p>
    </div>
  `;

  return `
    <div class="editor-view">

      <div class="editor-sidebar">
        <div class="editor-sidebar__header">LORE FILES</div>
        <div class="editor-file-list">${fileItems}</div>
        <button class="editor-validate-btn" id="editor-validate-btn">
          CHECK ATTRIBUTES
        </button>
        <button class="editor-exit-btn" id="editor-exit-btn">
          ← MAIN MENU
        </button>
      </div>

      <div class="editor-main">
        ${mainPanel}
      </div>

    </div>
  `;
}

function _buildEditorPanel() {
  const meta  = _files.find(f => f.filename === _active) || {};
  const dirty = _content !== _savedContent;

  return `
    <div class="editor-panel">

      <div class="editor-panel__header">
        <div class="editor-panel__meta">
          <h3 class="editor-panel__title">${meta.title || _active}</h3>
          <p class="editor-panel__desc">${meta.description || ""}</p>
        </div>
        <div class="editor-panel__toolbar">
          <span class="editor-dirty-badge ${dirty ? "editor-dirty-badge--visible" : ""}"
                id="editor-dirty">UNSAVED</span>
          <button class="editor-btn" id="editor-format-btn">FORMAT</button>
          <button class="editor-btn editor-btn--save" id="editor-save-btn">SAVE</button>
        </div>
      </div>

      <div class="editor-status" id="editor-status"></div>

      <textarea
        class="editor-textarea"
        id="editor-textarea"
        spellcheck="false"
        autocomplete="off"
        autocorrect="off"
      >${_escHtml(_content)}</textarea>

    </div>
  `;
}


// ---------------------------------------------------------------------------
// Event wiring
// ---------------------------------------------------------------------------

function _wire() {
  if (!_container) return;

  // File list clicks
  _container.querySelectorAll(".editor-file-item").forEach(btn => {
    btn.addEventListener("click", () => {
      const fname = btn.dataset.filename;
      if (fname === _active) return;
      if (_content !== _savedContent) {
        if (!confirm(`Discard unsaved changes to ${_active}?`)) return;
      }
      _openFile(fname);
    });
  });

  // Validate button
  _container.querySelector("#editor-validate-btn")?.addEventListener("click", _runValidation);

  // Exit to main menu
  _container.querySelector("#editor-exit-btn")?.addEventListener("click", async () => {
    if (_content !== _savedContent) {
      if (!confirm(`Discard unsaved changes to ${_active}?`)) return;
    }
    const { switchView } = await import("../main.js");
    switchView("title");
  });

  // Textarea — track changes
  const ta = _container.querySelector("#editor-textarea");
  if (ta) {
    ta.addEventListener("input", () => {
      _content = ta.value;
      _updateDirty();
    });

    // Ctrl+S / Cmd+S to save
    ta.addEventListener("keydown", e => {
      if ((e.ctrlKey || e.metaKey) && e.key === "s") {
        e.preventDefault();
        _save();
      }
      // Tab inserts two spaces instead of focusing next element
      if (e.key === "Tab") {
        e.preventDefault();
        const start = ta.selectionStart;
        const end   = ta.selectionEnd;
        ta.value = ta.value.slice(0, start) + "  " + ta.value.slice(end);
        ta.selectionStart = ta.selectionEnd = start + 2;
        _content = ta.value;
        _updateDirty();
      }
    });
  }

  // Format button
  _container.querySelector("#editor-format-btn")?.addEventListener("click", _format);

  // Save button
  _container.querySelector("#editor-save-btn")?.addEventListener("click", _save);
}


// ---------------------------------------------------------------------------
// File operations
// ---------------------------------------------------------------------------

async function _openFile(filename) {
  _setStatus("Loading…");
  try {
    const result = await editorGetFile(filename);
    _active       = filename;
    _savedContent = result.content;
    _content      = _prettyPrint(result.content);
    _savedContent = _content;   // treat pretty-printed as the baseline
    _render();
    _setStatus("");
  } catch (err) {
    _setStatus(`Error loading file: ${err.message}`, true);
  }
}

async function _save() {
  if (!_active) return;

  // Validate JSON first
  let parsed;
  try {
    parsed = JSON.parse(_content);
  } catch (e) {
    _setStatus(`JSON error: ${e.message}`, true);
    return;
  }

  _setStatus("Saving…");
  try {
    await editorSaveFile(_active, _content);
    _savedContent = _content;
    _updateDirty();
    _setStatus("Saved.");
    setTimeout(() => _setStatus(""), 2500);
  } catch (err) {
    _setStatus(`Save failed: ${err.message}`, true);
  }
}

function _format() {
  if (!_content) return;
  try {
    const pretty = _prettyPrint(_content);
    _content = pretty;
    const ta = _container?.querySelector("#editor-textarea");
    if (ta) ta.value = pretty;
    _updateDirty();
    _setStatus("Formatted.");
    setTimeout(() => _setStatus(""), 1500);
  } catch (e) {
    _setStatus(`Cannot format — invalid JSON: ${e.message}`, true);
  }
}


// ---------------------------------------------------------------------------
// Validation
// ---------------------------------------------------------------------------

async function _runValidation() {
  const btn = _container?.querySelector("#editor-validate-btn");
  if (btn) btn.textContent = "CHECKING…";

  let result;
  try {
    result = await editorValidate();
  } catch (err) {
    _setStatus(`Validation failed: ${err.message}`, true);
    if (btn) btn.textContent = "CHECK ATTRIBUTES";
    return;
  }

  if (btn) btn.textContent = "CHECK ATTRIBUTES";
  _showValidationModal(result);
}

function _showValidationModal(result) {
  const { issues, valid } = result;

  let body;
  if (valid) {
    body = `<p class="editor-validate-ok">✓ All attribute references are valid across all lore files.</p>`;
  } else {
    const rows = issues.map(issue => {
      if (issue.type === "parse_error") {
        return `<div class="editor-issue editor-issue--error">
          <span class="editor-issue__file">${issue.file}</span>
          <span class="editor-issue__detail">JSON parse error: ${_escHtml(issue.detail)}</span>
        </div>`;
      }
      return `<div class="editor-issue">
        <span class="editor-issue__file">${issue.file}</span>
        <span class="editor-issue__comp">${_escHtml(issue.component)}</span>
        <span class="editor-issue__attr">${_escHtml(issue.attribute)}</span>
        <span class="editor-issue__detail">${_escHtml(issue.detail)}</span>
      </div>`;
    }).join("");

    body = `
      <p class="editor-validate-count">${issues.length} issue${issues.length !== 1 ? "s" : ""} found:</p>
      <div class="editor-issue-list">${rows}</div>
    `;
  }

  // Inline modal using the existing modal system if available, else a simple overlay
  import("../ui/modal.js").then(({ showModal, closeModal }) => {
    showModal(
      valid ? "ATTRIBUTE CHECK — PASS" : "ATTRIBUTE CHECK — ISSUES FOUND",
      body,
      [{ label: "CLOSE", className: "btn--secondary", onClick: () => closeModal() }],
      { wide: !valid }
    );
  });
}


// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function _prettyPrint(jsonStr) {
  return JSON.stringify(JSON.parse(jsonStr), null, 2);
}

function _updateDirty() {
  const badge = _container?.querySelector("#editor-dirty");
  if (badge) {
    badge.classList.toggle("editor-dirty-badge--visible", _content !== _savedContent);
  }
}

function _setStatus(msg, isError = false) {
  const el = _container?.querySelector("#editor-status");
  if (!el) return;
  el.textContent = msg;
  el.classList.toggle("editor-status--error", isError);
}

function _escHtml(str) {
  return String(str || "")
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
