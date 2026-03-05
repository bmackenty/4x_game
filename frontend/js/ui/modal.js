/**
 * frontend/js/ui/modal.js — Reusable modal dialog system.
 *
 * Provides a single modal overlay that any view can populate with arbitrary
 * HTML content and an action button bar.  Only one modal can be open at a time.
 *
 * Public API:
 *   showModal(title, bodyHtml, buttons)
 *     title    — string shown in the modal header
 *     bodyHtml — inner HTML for the modal body area
 *     buttons  — array of { label, className, onClick } objects
 *
 *   closeModal()
 *     Dismisses the modal and removes event listeners.
 *
 *   confirm(title, message)
 *     Returns a Promise<boolean> — resolves true on Confirm, false on Cancel.
 *     Shorthand for simple yes/no decisions.
 *
 * The DOM elements (#modal-overlay, #modal-box, #modal-title, #modal-body,
 * #modal-footer, #modal-close) are expected to exist in index.html.
 */

// ---------------------------------------------------------------------------
// Internal state
// ---------------------------------------------------------------------------

/** Currently registered cleanup callbacks (keyboard handler, overlay click). */
let _cleanupFns = [];

// ---------------------------------------------------------------------------
// Core show / close
// ---------------------------------------------------------------------------

/**
 * Show the modal with custom title, body HTML, and footer buttons.
 *
 * @param {string}   title    — Text for the modal header.
 * @param {string}   bodyHtml — HTML string rendered inside the modal body.
 * @param {Array}    buttons  — [{label, className, onClick}] for the footer.
 *                              className is added to the button element.
 * @param {object}   opts     — Optional: { wide: bool } widens the modal box.
 */
export function showModal(title, bodyHtml, buttons = [], opts = {}) {
    const overlay  = document.getElementById("modal-overlay");
    const box      = document.getElementById("modal");
    const titleEl  = document.getElementById("modal-title");
    const bodyEl   = document.getElementById("modal-body");
    const footer   = document.getElementById("modal-footer");
    const closeBtn = document.getElementById("modal-close");

    if (!overlay) {
        console.error("[modal] #modal-overlay not found in DOM.");
        return;
    }

    // Apply/remove the wide modifier class on the modal box
    if (box) {
        box.classList.toggle("modal--wide", !!opts.wide);
    }

    // Populate content
    titleEl.textContent = title;
    bodyEl.innerHTML    = bodyHtml;

    // Build footer buttons
    footer.innerHTML = "";
    for (const btn of buttons) {
        const el = document.createElement("button");
        el.textContent = btn.label;
        el.className   = `btn ${btn.className || ""}`.trim();
        el.addEventListener("click", () => {
            btn.onClick();
        });
        footer.appendChild(el);
    }

    // Show overlay by removing the hidden class
    overlay.classList.remove("modal-overlay--hidden");

    // ----- Event cleanup registration -----

    // Close on X button
    const onClose = () => closeModal();
    closeBtn.addEventListener("click", onClose);

    // Close on Escape key
    const onKey = (e) => {
        if (e.key === "Escape") closeModal();
    };
    document.addEventListener("keydown", onKey);

    // Close when clicking outside the modal box
    const onOverlayClick = (e) => {
        if (e.target === overlay) closeModal();
    };
    overlay.addEventListener("click", onOverlayClick);

    // Store cleanup so closeModal() can remove them
    _cleanupFns = [
        () => closeBtn.removeEventListener("click", onClose),
        () => document.removeEventListener("keydown", onKey),
        () => overlay.removeEventListener("click", onOverlayClick),
    ];
}

/**
 * Dismiss the modal and run all registered cleanup functions.
 */
export function closeModal() {
    const overlay = document.getElementById("modal-overlay");
    if (overlay) overlay.classList.add("modal-overlay--hidden");

    // Strip the wide modifier so normal modals aren't affected afterwards
    const box = document.getElementById("modal");
    if (box) box.classList.remove("modal--wide");

    for (const fn of _cleanupFns) fn();
    _cleanupFns = [];
}

// ---------------------------------------------------------------------------
// Convenience helpers
// ---------------------------------------------------------------------------

/**
 * Show a simple yes/no confirmation dialog.
 *
 * @param   {string} title   — Modal header text.
 * @param   {string} message — Confirmation question shown in the body.
 * @returns {Promise<boolean>} Resolves true if the user clicks "Confirm".
 */
export function confirm(title, message) {
    return new Promise((resolve) => {
        showModal(
            title,
            `<p class="modal-confirm-text">${message}</p>`,
            [
                {
                    label: "Confirm",
                    className: "btn--primary",
                    onClick: () => {
                        closeModal();
                        resolve(true);
                    },
                },
                {
                    label: "Cancel",
                    className: "btn--secondary",
                    onClick: () => {
                        closeModal();
                        resolve(false);
                    },
                },
            ]
        );
    });
}

/**
 * Show a read-only information modal with a single "Close" button.
 *
 * @param {string} title    — Modal header text.
 * @param {string} bodyHtml — HTML to display in the body.
 */
export function infoModal(title, bodyHtml) {
    showModal(title, bodyHtml, [
        {
            label: "Close",
            className: "btn--secondary",
            onClick: () => closeModal(),
        },
    ]);
}
