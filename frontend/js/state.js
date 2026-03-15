/**
 * state.js — Single global client-side game state.
 *
 * This is a plain JavaScript object — no framework, no proxy magic.
 * Views read from it when mounting and update specific keys after API calls.
 * The polling loop in main.js refreshes the "live" fields (credits, turn,
 * research progress) every second, then calls hud.refresh() to re-render.
 *
 * DESIGN RULE: state is the only mutable singleton in the frontend.
 * All other modules receive state as a parameter or import it directly.
 */

export const state = {
  // -----------------------------------------------------------------
  // Session flags
  // -----------------------------------------------------------------

  /** True once /api/game/new has returned successfully. */
  gameInitialized: false,

  /** The currently visible view name: "setup" | "galaxy" | "colony" | "research" | "diplomacy" */
  currentView: "setup",

  // -----------------------------------------------------------------
  // Data refreshed every second by the polling loop (main.js)
  // -----------------------------------------------------------------

  /** Full response from GET /api/game/state */
  gameState: null,

  // -----------------------------------------------------------------
  // Galaxy map state
  // -----------------------------------------------------------------

  /** Array of system objects returned by GET /api/galaxy/map
   *  Each entry: { name, hex_q, hex_r, x, y, z, type, population,
   *                threat_level, controlling_faction, visited, planet_count } */
  galaxyMap: [],

  /** Array of deep space objects from GET /api/galaxy/map
   *  Each entry: { type, hex_q, hex_r, x, y, z, subtype, name, description,
   *                discovered, depleted } */
  deepSpaceObjects: [],

  /** The currently selected (clicked) star system object, or null */
  selectedSystem: null,

  // -----------------------------------------------------------------
  // Colony state
  // -----------------------------------------------------------------

  /** The planet the player is currently viewing in the colony view */
  selectedPlanet: null,

  /** Map of planet_name → colony data (tiles, production, etc.) */
  coloniesCache: {},

  // -----------------------------------------------------------------
  // Research state
  // -----------------------------------------------------------------

  /** Full tech tree returned by GET /api/research/tree */
  researchTree: null,

  // -----------------------------------------------------------------
  // Faction state
  // -----------------------------------------------------------------

  /** Array of faction objects from GET /api/factions */
  factions: [],

  // -----------------------------------------------------------------
  // UI state
  // -----------------------------------------------------------------

  /** Whether the right panel is currently shown */
  rightPanelOpen: false,

  /** Whether the left panel is currently shown */
  leftPanelOpen: false,

  /** Notification queue — notifications.js drains this */
  notificationQueue: [],

  // -----------------------------------------------------------------
  // Options loaded once at startup (character creation choices)
  // -----------------------------------------------------------------

  /** Full response from GET /api/game/options */
  options: null,
};
