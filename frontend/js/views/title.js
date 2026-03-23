/**
 * views/title.js — Opening title / main-menu screen.
 *
 * Shown on every load before the player starts or resumes a game.
 * Context: { hasGame: bool } — controls whether "Continue" appears.
 */

import { state }                        from "../state.js";
import { saveGame, listSaves, loadGame, getLoreIntro } from "../api.js";
import { notify }                       from "../ui/notifications.js";

// Lazy imports to avoid circular dep with main.js
let _switchView    = null;
let _onGameStarted = null;

async function _getMain() {
  if (!_switchView) {
    const m   = await import("../main.js");
    _switchView    = m.switchView;
    _onGameStarted = m.onGameStarted;
  }
}


// ---------------------------------------------------------------------------
// ASCII art logo — "7019" in figlet Big-style, hand-aligned
// ---------------------------------------------------------------------------

const ASCII_LOGO =
` ______    ___  __    ___
|___  /   / _ \\/_ |  / _ \\
   / /   | | | | | | | (_) |
  / /    | |_| | | |  \\__, |
 /_/      \\___/  |_|    /_/ `;


// ---------------------------------------------------------------------------
// mount / unmount
// ---------------------------------------------------------------------------

export const titleView = {

  async mount(context = {}) {
    const container = document.getElementById("view-title");
    if (!container) return;
    await _getMain();

    const hasGame = !!(context.hasGame);
    container.innerHTML = _buildHtml(hasGame);
    _attach(container, hasGame);
  },

  unmount() {},
};


// ---------------------------------------------------------------------------
// HTML builder
// ---------------------------------------------------------------------------

function _buildHtml(hasGame) {
  const continueLink = hasGame
    ? `<a href="#" class="title-link title-link--primary" id="title-continue">Continue Game</a>`
    : "";

  const saveLink = hasGame
    ? `<a href="#" class="title-link" id="title-save">Save Game</a>`
    : "";

  const newGameClass = hasGame ? "title-link" : "title-link title-link--primary";

  return `
    <div class="title-screen">

      <div class="title-body">

        <pre class="title-logo" aria-label="7019 The 4X Game">${ASCII_LOGO}</pre>

        <div class="title-game-name">THE  4X  GAME</div>
        <div class="title-tagline">Chronicles of the Ether &nbsp;·&nbsp; Year 7019</div>

        <nav class="title-menu" aria-label="Main menu">
          <a href="#" class="title-link title-link--dim" id="title-intro">Introduction</a>
          ${continueLink}
          <a href="#" class="${newGameClass}" id="title-new">New Game</a>
          <a href="#" class="title-link" id="title-load">Load Game</a>
          ${saveLink}
          <a href="#" class="title-link title-link--dim" id="title-credits">Credits</a>
          <a href="#" class="title-link title-link--dim" id="title-editor">Data Editor</a>
        </nav>

      </div>

      <footer class="title-footer">
        CHRONICLES OF THE ETHER &nbsp;·&nbsp; 7019
      </footer>

    </div>
  `;
}


// ---------------------------------------------------------------------------
// Event listeners
// ---------------------------------------------------------------------------

function _attach(container, hasGame) {
  container.querySelector("#title-intro")?.addEventListener("click", e => {
    e.preventDefault();
    _showIntroModal();
  });

  container.querySelector("#title-new")?.addEventListener("click", e => {
    e.preventDefault();
    _switchView("setup");
  });

  container.querySelector("#title-load")?.addEventListener("click", e => {
    e.preventDefault();
    _showLoadModal();
  });

  container.querySelector("#title-credits")?.addEventListener("click", e => {
    e.preventDefault();
    _showCreditsModal();
  });

  container.querySelector("#title-editor")?.addEventListener("click", e => {
    e.preventDefault();
    _switchView("editor");
  });

  if (hasGame) {
    container.querySelector("#title-continue")?.addEventListener("click", e => {
      e.preventDefault();
      _onGameStarted(state.gameState);
    });

    container.querySelector("#title-save")?.addEventListener("click", async e => {
      e.preventDefault();
      try {
        await saveGame("autosave");
        notify("SAVE", "Game saved to autosave slot.");
      } catch (err) {
        notify("ERROR", `Save failed: ${err.message}`);
      }
    });
  }
}


// ---------------------------------------------------------------------------
// Introduction modal
// ---------------------------------------------------------------------------

async function _showIntroModal() {
  const { showModal, closeModal } = await import("../ui/modal.js");

  let data;
  try {
    data = await getLoreIntro();
  } catch (err) {
    showModal("ERROR", `<p>Could not load introduction: ${err.message}</p>`,
      [{ label: "CLOSE", className: "btn--secondary", onClick: closeModal }]);
    return;
  }

  const sectionsHtml = (data.sections || []).map(s => `
    <div class="intro-section">
      <h3 class="intro-section__heading">${s.heading}</h3>
      <p class="intro-section__text">${s.text.replace(/\n/g, "<br>")}</p>
    </div>
  `).join("");

  const body = `
    <div class="intro-modal">
      <p class="intro-subtitle">${data.subtitle || ""}</p>
      ${sectionsHtml}
    </div>
  `;

  showModal(data.title || "Introduction", body,
    [{ label: "CLOSE", className: "btn--secondary", onClick: () => closeModal() }],
    { wide: true });
}


// ---------------------------------------------------------------------------
// Load game modal
// ---------------------------------------------------------------------------

async function _showLoadModal() {
  const { showModal, closeModal } = await import("../ui/modal.js");

  let saves;
  try {
    const result = await listSaves();
    saves = result.saves || [];
  } catch (err) {
    showModal("LOAD GAME", `<p class="muted">Could not list saves: ${err.message}</p>`,
      [{ label: "CLOSE", className: "btn--secondary", onClick: () => closeModal() }]);
    return;
  }

  if (saves.length === 0) {
    showModal("LOAD GAME",
      `<p class="muted" style="text-align:center;padding:var(--sp-8) 0">No save files found.</p>`,
      [{ label: "CLOSE", className: "btn--secondary", onClick: () => closeModal() }]);
    return;
  }

  const rowsHtml = saves.map(s => `
    <div class="save-row" data-path="${_escAttr(s.path || s.name)}">
      <div class="save-row__name">${_escHtml(s.player_name || s.name)}</div>
      <div class="save-row__meta">
        <span class="save-row__turn">Turn ${s.turn ?? "—"}</span>
        <span class="save-row__date">${s.timestamp ? new Date(s.timestamp).toLocaleDateString() : ""}</span>
      </div>
    </div>
  `).join("");

  const body = `<div class="save-list">${rowsHtml}</div>`;

  showModal("LOAD GAME", body,
    [{ label: "CANCEL", className: "btn--ghost", onClick: () => closeModal() }]);

  // Wire row clicks after modal renders
  setTimeout(() => {
    document.querySelectorAll(".save-row").forEach(row => {
      row.addEventListener("click", async () => {
        const path = row.dataset.path;
        try {
          const result = await loadGame(path);
          closeModal();
          if (result.state) _onGameStarted(result.state);
        } catch (err) {
          notify("ERROR", `Load failed: ${err.message}`);
        }
      });
    });
  }, 50);
}


// ---------------------------------------------------------------------------
// Credits modal
// ---------------------------------------------------------------------------

function _showCreditsModal() {
  Promise.all([
    import("../ui/modal.js"),
    fetch("/lore/credits.json").then(r => r.json()),
  ]).then(([{ showModal, closeModal }, data]) => {
    const blocks = data.entries.map(e => `
        <div class="credits-block">
          <div class="credits-role">${_escHtml(e.role)}</div>
          <div class="credits-name">${_escHtml(e.name)}</div>
        </div>`).join("");
    const body = `
      <div class="credits-modal">
        ${blocks}
        <div class="credits-version">${_escHtml(data.version)}</div>
      </div>
    `;
    showModal(data.title, body,
      [{ label: "CLOSE", className: "btn--secondary", onClick: () => closeModal() }]);
  });
}


// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function _escHtml(str) {
  return String(str || "")
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function _escAttr(str) {
  return String(str || "").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}
