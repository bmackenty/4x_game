/**
 * api.js — All HTTP calls to the FastAPI backend.
 *
 * DESIGN RULE: This is the ONLY file in the frontend that calls fetch().
 * Every view/UI module imports from here.  This keeps the server contract
 * in one place and makes it easy to add error-handling or caching later.
 *
 * Every function is async and either:
 *   - Returns the parsed JSON response body on success, OR
 *   - Throws an Error with a human-readable message on failure.
 *
 * The base URL is relative (no host), so the game always talks to the
 * same server that served the HTML — works on any port without config.
 */

const BASE = "";  // Relative to current origin (localhost:8765)


/**
 * Low-level fetch wrapper.
 * @param {string} path    - URL path, e.g. "/api/game/state"
 * @param {object} options - fetch() options (method, body, headers, etc.)
 * @returns {Promise<any>} Parsed JSON body
 */
async function request(path, options = {}) {
  const defaultHeaders = { "Content-Type": "application/json" };
  const response = await fetch(BASE + path, {
    headers: { ...defaultHeaders, ...(options.headers || {}) },
    ...options,
  });

  // Try to parse JSON even on error responses so we can show the detail field
  let body;
  try {
    body = await response.json();
  } catch {
    body = null;
  }

  if (!response.ok) {
    let detail = body?.detail || `HTTP ${response.status}`;
    if (Array.isArray(detail)) {
      detail = detail.map(e => e.msg || JSON.stringify(e)).join("; ");
    }
    const apiErr = new Error(detail);
    apiErr.status = response.status;
    throw apiErr;
  }

  return body;
}

// Convenience wrappers
const get  = (path)         => request(path, { method: "GET" });
const post = (path, data)   => request(path, { method: "POST", body: JSON.stringify(data ?? {}) });
const del  = (path, data)   => request(path, { method: "DELETE", body: JSON.stringify(data ?? {}) });


// ===========================================================================
// Game lifecycle
// ===========================================================================

/**
 * Start a new game with the given character data.
 * @param {{ name, character_class, background, species, faction, stats }} characterData
 */
export function newGame(characterData) {
  return post("/api/game/new", characterData);
}

/**
 * Fetch the current game state (credits, turn, ship, research, etc.).
 * Called by the polling loop every second.
 */
export function getGameState() {
  return get("/api/game/state");
}

/**
 * End the current turn and run the per-turn subsystem tick.
 * Returns { success, new_turn, events, game_ended, state }.
 */
export function endTurn() {
  return post("/api/game/turn/end");
}

/**
 * Save the current game to a named slot.
 * @param {string} slotName
 */
export function saveGame(slotName = "autosave") {
  return post("/api/game/save", { slot_name: slotName });
}

/**
 * List all available save files.
 * Returns { saves: [ { name, timestamp, player_name, turn, ... } ] }.
 */
export function listSaves() {
  return get("/api/game/saves");
}

/**
 * Load a previously saved game from a file path.
 * @param {string} savePath
 */
export function loadGame(savePath) {
  return post("/api/game/load", { save_path: savePath });
}

/**
 * Fetch all character-creation options (classes, backgrounds, species, factions, stat meta).
 * Called once when the setup view mounts.
 */
export function getGameOptions() {
  return get("/api/game/options");
}

/**
 * Fetch the full character sheet: stats, derived metrics, class info,
 * background traits, and equipment slots.
 */
export function getCharacterSheet() {
  return get("/api/character/sheet");
}


// ===========================================================================
// Galaxy / Navigation  (Phase 2)
// ===========================================================================

/**
 * Fetch all star systems projected onto the 2D hex grid.
 * Returns { systems: [ { name, hex_q, hex_r, x, y, z, type, ... } ] }.
 */
export function getGalaxyMap() {
  return get("/api/galaxy/map");
}

/**
 * Fetch detailed info for one star system by name.
 * @param {string} systemName
 */
export function getSystem(systemName) {
  return get(`/api/system/${encodeURIComponent(systemName)}`);
}

/**
 * Fetch NPC presence at a system: stations, docked NPC ships, settled planets.
 * @param {string} systemName
 */
export function getSystemPresence(systemName) {
  return get(`/api/system/${encodeURIComponent(systemName)}/presence`);
}

/**
 * Fetch the deterministic hex-map interior layout for a star system.
 * Returns { system_name, system_type, grid_radius, player_ship_here, objects[] }.
 * Objects include the star, planets, stations, and any NPC ships present.
 * @param {string} systemName
 */
export function getSystemInterior(systemName) {
  return get(`/api/system/${encodeURIComponent(systemName)}/interior`);
}

/**
 * Jump the player's ship to a set of galaxy coordinates.
 * @param {number} x
 * @param {number} y
 * @param {number} z
 */
export function jumpToCoords(x, y, z) {
  return post("/api/ship/jump", { target_x: x, target_y: y, target_z: z });
}

/**
 * Fetch the current ship's status (fuel, cargo, position, etc.).
 */
export function getShipStatus() {
  return get("/api/ship/status");
}

/**
 * Fetch the full attribute profile grouped by category, plus installed components.
 */
export function getShipAttributes() {
  return get("/api/ship/attributes");
}

/**
 * Fetch installed components and all available components per slot.
 */
export function getShipComponents() {
  return get("/api/ship/components");
}

/**
 * Install a component on the player's ship.
 * @param {string} category      - Slot category key (e.g. "hulls", "engines")
 * @param {string} componentName - Exact component name from the registry
 */
export function installShipComponent(category, componentName) {
  return post("/api/ship/components/install", {
    category,
    component_name: componentName,
  });
}


// ===========================================================================
// Colony management  (Phase 3)
// ===========================================================================

/**
 * List all player-founded colonies with their production summaries.
 */
export function getAllColonies() {
  return get("/api/colony/all");
}

/**
 * Full empire-wide colony overview (enriched data + totals).
 */
export function getColonyOverview() {
  return get("/api/colony/overview");
}

/**
 * Fetch the full hex grid for one planet (tiles, terrain, improvements).
 * @param {string} planetName
 */
export function getColony(planetName) {
  return get(`/api/colony/${encodeURIComponent(planetName)}`);
}

/**
 * Found a new colony on a habitable planet.
 * @param {string} planetName
 * @param {string} systemName
 * @param {string} planetType
 */
export function foundColony(planetName, systemName, planetType) {
  return post(`/api/colony/${encodeURIComponent(planetName)}/found`, {
    planet_name: planetName,
    system_name: systemName,
    planet_type: planetType,
  });
}

/**
 * Build an improvement on a specific hex tile.
 * @param {string} planetName
 * @param {number} q  Axial hex coordinate
 * @param {number} r  Axial hex coordinate
 * @param {string} improvementType
 */
export function buildImprovement(planetName, q, r, improvementType) {
  return post(`/api/colony/${encodeURIComponent(planetName)}/build`, {
    q,
    r,
    improvement_type: improvementType,
  });
}

/**
 * Demolish an improvement on a hex tile (50% credit refund).
 * @param {string} planetName
 * @param {number} q
 * @param {number} r
 */
export function demolishImprovement(planetName, q, r) {
  return del(`/api/colony/${encodeURIComponent(planetName)}/build`, { q, r });
}

/**
 * Upgrade the improvement on a colony tile to the next production tier.
 * @param {string} planetName
 * @param {number} q
 * @param {number} r
 */
export function upgradeImprovement(planetName, q, r) {
  return post(`/api/colony/${encodeURIComponent(planetName)}/upgrade`, { q, r });
}

/**
 * Fetch the improvement catalogue with unlock status for the player's
 * current research.  Used to populate the build menu in the colony view.
 */
export function getImprovementsCatalogue() {
  return get("/api/colony/improvements");
}

/**
 * Fetch the current social / economic / political systems for a colony,
 * together with all available options (including lock state) and the
 * faction affinity table for the current configuration.
 * @param {string} planetName
 */
export function getColonySystems(planetName) {
  return get(`/api/colony/${encodeURIComponent(planetName)}/systems`);
}

/**
 * Change one governing system for a colony.
 * @param {string} planetName  - Colony planet name
 * @param {string} category    - "social" | "economic" | "political"
 * @param {string} systemId    - System ID key (e.g. "memory_economy")
 */
export function setColonySystem(planetName, category, systemId) {
  return post(`/api/colony/${encodeURIComponent(planetName)}/systems`, {
    category,
    system_id: systemId,
  });
}


// ===========================================================================
// Research  (Phase 4)
// ===========================================================================

/**
 * Fetch the full tech tree with each node's completion status.
 * Returns { categories, nodes: [...], active }.
 */
export function getResearchTree() {
  return get("/api/research/tree");
}

/**
 * Begin researching a technology.
 * @param {string} researchName
 */
export function startResearch(researchName) {
  return post("/api/research/start", { research_name: researchName });
}

/**
 * Cancel the currently active research (no refund).
 */
export function cancelResearch() {
  return post("/api/research/cancel");
}

/**
 * Fetch the current research progress (name, progress, total_time, percent).
 */
export function getResearchStatus() {
  return get("/api/research/status");
}


// ===========================================================================
// Factions / Diplomacy  (Phase 4)
// ===========================================================================

/**
 * Fetch all factions with current reputation values.
 */
export function getFactions() {
  return get("/api/factions");
}

/**
 * Fetch detailed info for one faction.
 * @param {string} factionName
 */
export function getFaction(factionName) {
  return get(`/api/faction/${encodeURIComponent(factionName)}`);
}

/**
 * Perform a diplomatic action toward a faction.
 * @param {string} factionName
 * @param {"gift"|"mission_complete"|"provoke"} action
 * @param {number|null} amount  Credit amount for gifts
 */
export function factionAction(factionName, action, amount = null) {
  return post(`/api/faction/${encodeURIComponent(factionName)}/action`, {
    action,
    amount,
  });
}


// ===========================================================================
// Trade  (Phase 5)
// ===========================================================================

/**
 * Fetch market prices and stock for a star system.
 * @param {string} systemName
 */
export function getMarket(systemName) {
  return get(`/api/market/${encodeURIComponent(systemName)}`);
}

/**
 * Buy a commodity at a system.
 * @param {string} systemName
 * @param {string} commodity
 * @param {number} quantity
 */
export function buyGoods(systemName, commodity, quantity) {
  return post("/api/trade/buy", { system_name: systemName, commodity, quantity });
}

/**
 * Sell a commodity at a system.
 * @param {string} systemName
 * @param {string} commodity
 * @param {number} quantity
 */
export function sellGoods(systemName, commodity, quantity) {
  return post("/api/trade/sell", { system_name: systemName, commodity, quantity });
}


// ===========================================================================
// Space Stations
// ===========================================================================

/** Fetch full details for a named station. */
export function getStation(name) {
  return get(`/api/station/${encodeURIComponent(name)}`);
}

/** Fetch available ship upgrades at a station. */
export function getStationUpgrades(name) {
  return get(`/api/station/${encodeURIComponent(name)}/upgrades`);
}

/**
 * Purchase and install a ship upgrade at a station.
 * @param {string} stationName
 * @param {string} category     - Upgrade category (e.g. "Engine Upgrades")
 * @param {string} upgradeName  - Upgrade name (e.g. "Quantum Booster")
 */
export function buyStationUpgrade(stationName, category, upgradeName) {
  return post(`/api/station/${encodeURIComponent(stationName)}/upgrade`, {
    category,
    upgrade_name: upgradeName,
  });
}

/** Repair the player's ship hull at a station (costs 500 cr per integrity point). */
export function repairShipAtStation(stationName) {
  return post(`/api/station/${encodeURIComponent(stationName)}/repair`, {});
}


// ===========================================================================
// Lore  (Phase 4)
// ===========================================================================

/**
 * Fetch the introductory lore text from lore/intro.json.
 * Returns { title, subtitle, sections: [{ heading, text }] }.
 */
export function getLoreIntro() {
  return get("/api/lore/intro");
}

/**
 * Fetch all energy type descriptions.
 * Returns an array of energy objects { name, category, description, ... }.
 */
export function getLoreEnergies() {
  return get("/api/lore/energies");
}

/**
 * Fetch all species lore.
 */
export function getLoreSpecies() {
  return get("/api/lore/species");
}

/**
 * Fetch current NPC ship positions for the galaxy map canvas.
 * Returns { ships: [{ name, bot_type, coordinates: [x,y,z] }, ...] }
 */
export function getNpcShips() {
  return get("/api/npc_ships");
}

// ===========================================================================
// Deep space actions
// ===========================================================================

/**
 * Harvest the resource node or salvage the derelict at the ship's current position.
 * Returns { success, credits_gained, cargo_added, credits, cargo }.
 */
export function harvestDeepSpace() {
  return post("/api/deep_space/harvest");
}

/**
 * Trigger a random encounter with the derelict at the ship's current position.
 * Returns { success, opening, outcome_type, outcome_title, outcome_narrative,
 *           credits_gained, cargo_added, hull_damage, credits, cargo, subtype }.
 */
export function encounterDerelict() {
  return post("/api/deep_space/encounter");
}

/**
 * Attempt to found an outpost at the ship's current position (stub — future feature).
 * Returns { success, message }.
 */
export function foundDeepSpaceOutpost() {
  return post("/api/deep_space/found_outpost");
}

// ===========================================================================
// Lore Editor
// ===========================================================================

export function editorListFiles() {
  return get("/api/editor/files");
}

export function editorGetFile(filename) {
  return get(`/api/editor/file/${encodeURIComponent(filename)}`);
}

export function editorSaveFile(filename, content) {
  return post(`/api/editor/file/${encodeURIComponent(filename)}`, { content });
}

export function editorValidate() {
  return get("/api/editor/validate");
}
