/**
 * ui/notifications.js — Toast notification system.
 *
 * Toasts are brief, auto-dismissing messages that appear in the bottom-right
 * corner.  They communicate turn events (economy changes, news, navigation
 * updates, research progress) without interrupting gameplay.
 *
 * Usage:
 *   import { notify } from "./ui/notifications.js";
 *   notify("ECON", "Spice prices surge in Tau Ceti.");
 *   notify("NEWS", "Veritas Covenant signs ceasefire.", 6000);
 *   notify("ERROR", "Insufficient fuel for jump.");
 */

const CONTAINER = () => document.getElementById("toast-container");

/** How long (ms) a toast is visible before auto-dismissing */
const DEFAULT_DURATION = 4000;

/** Maximum number of toasts visible at once */
const MAX_TOASTS = 6;


/**
 * Show a toast notification.
 *
 * @param {string} channel   - Event source label: "TURN" | "ECON" | "NEWS" | "NAV" | "R&D" | "ERROR"
 * @param {string} message   - Human-readable message text
 * @param {number} [duration] - Milliseconds before auto-dismiss (default 4000)
 */
export function notify(channel, message, duration = DEFAULT_DURATION) {
  const container = CONTAINER();
  if (!container) return;

  // Prune oldest toasts if we're at the limit
  const existing = container.querySelectorAll(".toast");
  if (existing.length >= MAX_TOASTS) {
    dismissToast(existing[existing.length - 1]);
  }

  // Normalise channel key for CSS class (R&D → RD)
  const cssChannel = channel.replace(/[^A-Z0-9]/g, "");

  // Build the toast element
  const toast = document.createElement("div");
  toast.className = `toast toast--${cssChannel}`;
  toast.innerHTML = `
    <span class="toast__channel">${channel}</span>
    <span class="toast__message">${escapeHtml(message)}</span>
  `;

  // Dismiss on click
  toast.addEventListener("click", () => dismissToast(toast));

  container.prepend(toast);

  // Auto-dismiss after `duration` ms
  if (duration > 0) {
    setTimeout(() => dismissToast(toast), duration);
  }
}


/**
 * Dismiss a single toast with a fade-out animation.
 * @param {HTMLElement} toast
 */
function dismissToast(toast) {
  if (!toast || toast.classList.contains("toast--dismissing")) return;
  toast.classList.add("toast--dismissing");
  toast.addEventListener("animationend", () => toast.remove(), { once: true });
  // Fallback removal in case animationend doesn't fire
  setTimeout(() => toast.remove(), 500);
}


/**
 * Dismiss all visible toasts immediately (e.g. when changing views).
 */
export function clearAllToasts() {
  const container = CONTAINER();
  if (!container) return;
  container.querySelectorAll(".toast").forEach(t => t.remove());
}


/**
 * Escape HTML special characters to prevent XSS in toast messages.
 * (Game messages come from the Python backend, but it's good practice.)
 * @param {string} str
 * @returns {string}
 */
function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
