"""
backend/main.py — FastAPI application for the 4X game.

Wraps the existing Python game engine in a REST API so that a browser-based
JavaScript frontend can drive gameplay.  The game logic lives entirely in the
project-root Python modules (game.py, navigation.py, etc.); this file is a
thin translation layer — it never duplicates game logic, only exposes it.

Design rules:
  * One singleton Game instance lives for the lifetime of the server process.
  * All game-mutating endpoints consume an action point via game.consume_action()
    (unless the action IS turn management itself).
  * Return shapes are plain dicts; Pydantic BaseModels are only used for request
    bodies where type validation is helpful.
  * Static files (the JS/CSS frontend) are mounted LAST so that all /api/*
    routes always win over the file-server.
"""

import os
import sys
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Path setup — add the project root so all existing game modules are importable
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Game-engine imports (all live in the project root)
from game import Game                                          # core engine
import save_game as save_game_module                           # save/load helpers
from characters import (
    character_classes,
    character_backgrounds,
    STAT_NAMES,
    BASE_STAT_VALUE,
    POINT_BUY_POINTS,
)
from species import get_playable_species
from factions import factions                                  # module-level dict
from research import all_research                              # full research tree
from energies import all_energies                              # 50 energy types
from backend.hex_utils import resolve_hex_collisions, galaxy_coords_to_hex
from backend.colony import ColonyManager                       # colony system
from backend.gnn import generate_gnn_summary                   # end-of-turn broadcast

# ---------------------------------------------------------------------------
# Singleton instances — one pair per server process, replaced on new game
# ---------------------------------------------------------------------------
game: Optional[Game] = None
colony_manager: Optional[ColonyManager] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan hook.
    Creates the initial (empty) Game instance at startup so the /api/game/state
    endpoint can safely report "not initialized" before the player starts a game.
    """
    global game, colony_manager
    game = Game()
    colony_manager = ColonyManager(game)
    print("[4X] Game engine ready.")
    yield
    print("[4X] Shutting down.")


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------
app = FastAPI(
    title="4X Game API",
    description="REST bridge between the browser frontend and the Python game engine.",
    lifespan=lifespan,
)

# CORS — allow the browser to call the API from any origin (localhost dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===========================================================================
# Request body models
# ===========================================================================

class NewGameRequest(BaseModel):
    """Character-creation payload sent when the player starts a new game."""
    name: str
    character_class: str
    background: str
    species: str
    faction: str = ""
    research_paths: list[str] = []
    # 7 stats: VIT, KIN, INT, AEF, COH, INF, SYN — each 30–100
    stats: dict[str, int] = {}


class SaveRequest(BaseModel):
    """Optional custom name for a save slot."""
    slot_name: str = "autosave"


class LoadRequest(BaseModel):
    """Path to the save file to load."""
    save_path: str


# ===========================================================================
# Helper — four composite power indices derived from live game state
# ===========================================================================

def _compute_indices() -> dict:
    """
    Compute the four strategic composite indices from live game data.

    Each index is the integer sum of its named sub-components so the
    frontend can display both the total and a per-component tooltip.

    SPI  Strategic Power Index
         Fleet_Strength + Defense_Grid + Strategic_Weapons + Intelligence_Capability
    REI  Resource Extraction Index
         Raw_Material_Access + Energy_Production + Logistics_Capacity
    KII  Knowledge & Innovation Index
         Research_Output + Education_Level + AI_Capability + Innovation_Rate
    ECI  Economic Capability Index
         Industrial_Output + Trade_Volume + Energy_Output + Financial_Liquidity
    """
    if not game or not game.character_created:
        return {}

    stats     = game.character_stats or {}
    completed = game.completed_research or []
    ships     = len(game.owned_ships or [])
    credits   = max(0, game.credits)

    # Character stat shortcuts (base 30; range 30-100)
    kin = stats.get("KIN", 30)
    int_ = stats.get("INT", 30)
    aef  = stats.get("AEF", 30)
    syn  = stats.get("SYN", 30)
    coh  = stats.get("COH", 30)
    n_completed = len(completed)

    # Colony production totals (zero when no colonies exist)
    prod = {}
    if colony_manager and colony_manager.colonies:
        prod = colony_manager.calculate_all_production()

    minerals     = int(prod.get("minerals",  0))
    food         = int(prod.get("food",      0))
    ether        = int(prod.get("ether",     0))
    research_pts = int(prod.get("research",  0))
    credits_prod = int(prod.get("credits",   0))
    defense_pts  = int(prod.get("defense",   0))
    refined_ore  = int(prod.get("refined_ore", 0))

    # Systems the player has visited — used as a proxy for scouting / logistics
    try:
        visited = sum(
            1 for s in game.navigation.galaxy.systems.values()
            if s.get("visited")
        )
    except Exception:
        visited = 0

    # Fleet pool — the canonical, production-chain-backed military strength.
    # Grows each turn via Shipyards (amplified by Ore Processors).
    fleet_pool  = max(0, getattr(game, "fleet_pool", 0))

    # Number of colonized systems — contributes to defense depth.
    empire_size = len(colony_manager.colonies) if colony_manager else 0

    # ── SPI ──────────────────────────────────────────────────────────────────
    fleet_strength          = fleet_pool                          # from production chain
    defense_grid            = defense_pts * 20 + empire_size * 15 + kin // 5
    strategic_weapons       = kin // 3 + n_completed * 2
    intelligence_capability = int_ // 4 + coh // 6

    spi = fleet_strength + defense_grid + strategic_weapons + intelligence_capability

    # ── REI ──────────────────────────────────────────────────────────────────
    # refined_ore is included in raw material access — it represents processed
    # industrial capacity sitting upstream of the military chain.
    raw_material_access = minerals * 8 + refined_ore * 6 + visited * 2
    energy_production   = ether * 10 + aef // 5
    logistics_capacity  = ships * 12 + visited * 3

    rei = raw_material_access + energy_production + logistics_capacity

    # ── KII ──────────────────────────────────────────────────────────────────
    research_output = research_pts * 8 + int_ // 4
    education_level = n_completed * 6 + int_ // 3
    ai_capability   = syn // 3 + aef // 6
    innovation_rate = syn // 5 + coh // 8

    kii = research_output + education_level + ai_capability + innovation_rate

    # ── ECI ──────────────────────────────────────────────────────────────────
    industrial_output   = minerals * 4 + food * 3
    trade_volume        = credits_prod * 10 + credits // 5000
    energy_output       = ether * 6 + aef // 5
    financial_liquidity = min(500, credits // 2000)

    eci = industrial_output + trade_volume + energy_output + financial_liquidity

    return {
        "spi": spi,
        "rei": rei,
        "kii": kii,
        "eci": eci,
        "fleet_pool": fleet_pool,   # also exposed at top level for HUD/GNN use
        "details": {
            "spi": {
                "Fleet Strength (pool)":   fleet_strength,
                "Defense Grid":            defense_grid,
                "Strategic Weapons":       strategic_weapons,
                "Intelligence Capability": intelligence_capability,
            },
            "rei": {
                "Raw Material Access": raw_material_access,
                "Energy Production":   energy_production,
                "Logistics Capacity":  logistics_capacity,
            },
            "kii": {
                "Research Output": research_output,
                "Education Level": education_level,
                "AI Capability":   ai_capability,
                "Innovation Rate": innovation_rate,
            },
            "eci": {
                "Industrial Output":   industrial_output,
                "Trade Volume":        trade_volume,
                "Energy Output":       energy_output,
                "Financial Liquidity": financial_liquidity,
            },
        },
        "inputs": {
            "Ships owned":              ships,
            "KIN stat":                 kin,
            "INT stat":                 int_,
            "AEF stat":                 aef,
            "SYN stat":                 syn,
            "COH stat":                 coh,
            "Research completed":       n_completed,
            "Colony minerals/turn":     minerals,
            "Colony food/turn":         food,
            "Colony ether/turn":        ether,
            "Colony research/turn":     research_pts,
            "Colony credits/turn":      credits_prod,
            "Colony defense/turn":      defense_pts,
            "Colony refined ore/turn":  refined_ore,
            "Systems visited":          visited,
            "Credits":                  credits,
            "Fleet pool":               fleet_pool,
        },
    }


# ===========================================================================
# Helper — player proximity checks
# ===========================================================================

def _ship_coords():
    """Return the current ship's (x, y, z) coordinates, or None."""
    try:
        return game.navigation.current_ship.coordinates
    except Exception:
        return None


def _current_system_name() -> str | None:
    """Return the name of the system the ship is currently in, or None."""
    try:
        info = game.get_active_ship_info()
        return info.get("current_system") if info else None
    except Exception:
        return None


def _player_is_in_system(system_name: str) -> bool:
    """True if the player's ship is currently at the named system."""
    return _current_system_name() == system_name


# Improvements that open a commodity market on a player colony.
# A colony system without at least one of these shows no market and
# blocks all trade transactions — the player must build infrastructure
# before tapping into interstellar commerce.
_TRADE_BUILDINGS = {"Trade Nexus", "Spaceport Hub"}


def _colony_has_trade_building(system_name: str) -> bool:
    """
    Return True if at least one player colony in system_name has a
    Trade Nexus or Spaceport Hub built on any tile.
    """
    for colony in colony_manager.colonies.values():
        if colony.system_name == system_name:
            for tile in colony.tiles.values():
                if tile.improvement in _TRADE_BUILDINGS:
                    return True
    return False


def _player_is_at_market(market_name: str) -> bool:
    """
    True if the player is at the location that hosts this market.

    Accepts both system names and station names as market_name:
      - System market:         ship must be in that system (resolved by name).
      - In-system station:     ship must be in the station's parent system.
      - Deep-space station:    ship must be within 8 units of the station's
                               3-D coordinates (one hex-unit tolerance).
    """
    import math as _math
    current_name = _current_system_name()

    # System market
    if current_name == market_name:
        # If this system only has a player colony (no pre-existing NPC market),
        # require a Trade Nexus or Spaceport Hub before trading.
        # NPC/predefined system markets are always accessible.
        npc_market_exists = (
            hasattr(game, "economy") and game.economy
            and market_name in game.economy.markets
        )
        if not npc_market_exists:
            # Pure player-colony system — must build trade infrastructure first
            if not _colony_has_trade_building(market_name):
                return False
        return True

    # Check stations
    coords = _ship_coords()
    if not coords:
        return False
    if game.station_manager:
        st = game.station_manager.get_station_by_name(market_name)
        if st:
            parent_system = st.get("system_name")
            if parent_system:
                # In-system station: being in the parent system is sufficient
                return current_name == parent_system
            else:
                # Deep-space station: proximity check
                st_coords = st.get("coordinates")
                if st_coords:
                    dist = _math.sqrt(sum((a - b) ** 2 for a, b in zip(coords, st_coords)))
                    return dist < 8.0

    return False

# Helper — snapshot of current game state (reused in multiple endpoints)
# ===========================================================================

def _build_state_snapshot() -> dict:
    """
    Return a JSON-serialisable dict that represents the full current game state.
    Called by /api/game/state and /api/game/load so they return identical shapes.
    """
    if not game or not game.character_created:
        return {"initialized": False}

    turn_info = game.get_turn_info()

    # Ship info — gracefully absent before the player has a ship
    ship_info = None
    try:
        ship_info = game.get_active_ship_info()
    except Exception:
        pass

    return {
        "initialized": True,
        "player": {
            "name": game.player_name,
            "character_class": game.character_class,
            "background": game.character_background,
            "species": game.character_species,
            "faction": game.character_faction,
            "credits": game.credits,
            "fleet_pool": getattr(game, "fleet_pool", 0),
        },
        "turn": turn_info,
        "research": {
            "active":     game.active_research,
            "progress":   game.research_progress,
            "completed":  game.completed_research,
            # total_time lets the HUD compute a % without a separate API call
            "total_time": (
                all_research[game.active_research].get("research_time", 1)
                if game.active_research and game.active_research in all_research
                else None
            ),
        },
        "ship":    ship_info,
        "indices": _compute_indices(),
    }


# ===========================================================================
# Helper — bot manager initialisation
# Called from both /api/game/new and /api/game/load.  BotManager state is not
# serialised in save files, so it must be rebuilt on every session start.
# ===========================================================================

def _init_bot_manager(g) -> None:
    """
    (Re-)create the BotManager on *g*, placing each NPC bot at a random
    starting system spread across the galaxy.
    """
    try:
        from ai_bots import BotManager
        g.bot_manager = BotManager(g)
    except Exception as _e:
        print(f"[4X] Warning: bot_manager init failed: {_e}")
        g.bot_manager = None


# ===========================================================================
# Helper — station manager + economy market registration
# Called from both /api/game/new and /api/game/load so stations always have
# tradeable markets regardless of how the session was started.
# ===========================================================================

def _init_station_manager(g) -> None:
    """
    (Re-)create the SpaceStationManager on *g* and register every station as a
    market in the economy engine.

    economy.generate_market_profile() requires the 'resources' key to be one of
    five richness levels ('Poor' … 'Abundant').  Previously the station *type*
    string (e.g. "Trading Post") was passed instead, causing a KeyError that
    silently swallowed every station market on startup.
    """
    import random as _rnd
    _RICHNESS = ["Poor", "Moderate", "Moderate", "Rich", "Abundant"]

    try:
        from station_manager import SpaceStationManager
        g.station_manager = SpaceStationManager(g.navigation.galaxy)
    except Exception as _e:
        print(f"[4X] Warning: station_manager init failed: {_e}")
        g.station_manager = None
        return

    if not (hasattr(g, "economy") and g.economy):
        return

    for _st in g.station_manager.stations.values():
        try:
            _econ_type = g.station_manager.get_economy_type(_st["type"])
            g.economy.create_market({
                "name":       _st["name"],
                "type":       _econ_type,
                "population": _rnd.randint(500, 5000),
                "resources":  _rnd.choice(_RICHNESS),   # must be a richness level
            })
        except Exception as _me:
            print(f"[4X] Warning: station market init failed for {_st['name']}: {_me}")


# ===========================================================================
# Game lifecycle endpoints
# ===========================================================================

@app.post("/api/game/new")
async def new_game(request: NewGameRequest):
    """
    Start a fresh game.

    Creates a brand-new Game instance (discarding any previous session) and
    calls initialize_new_game() with the player's character choices.
    """
    global game, colony_manager
    # Always start with a clean slate
    game = Game()
    colony_manager = ColonyManager(game)

    character_data = {
        "name": request.name,
        "character_class": request.character_class,
        "background": request.background,
        "species": request.species,
        "faction": request.faction,
        "research_paths": request.research_paths,
        "stats": request.stats,
    }

    success = game.initialize_new_game(character_data)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to initialise game character.")

    # Assign the class's starting ship(s) to the player's fleet, then activate the first one.
    # initialize_new_game() doesn't do this — the old UIs each handled ship assignment
    # separately.  We replicate that pattern here without modifying game.py.
    cls_data = character_classes.get(request.character_class, {})
    starting_ships = cls_data.get("starting_ships", ["Basic Transport"])
    for ship_name in starting_ships:
        if ship_name not in game.owned_ships:
            game.owned_ships.append(ship_name)

    if game.owned_ships and not game.navigation.current_ship:
        from navigation import Ship as _NavShip
        first_ship = game.owned_ships[0]
        game.navigation.current_ship = _NavShip(first_ship, first_ship)
        # Place the ship at the starting system (Proxima b — closest predefined
        # system to the default (50,50,25) origin).  Without this the player
        # starts in deep space and every proximity check fails until they jump.
        galaxy = game.navigation.galaxy
        start_sys = next(
            (data for coords, data in galaxy.systems.items()
             if data.get("name") == "Proxima b"),
            None,
        )
        if start_sys:
            game.navigation.current_ship.coordinates = start_sys["coordinates"]
            start_sys["visited"] = True

    # Initialise NPC infrastructure — bots and stations are generated fresh each game.
    _init_bot_manager(game)
    _init_station_manager(game)

    return {
        "success": True,
        "message": f"Welcome, {game.player_name}. The galaxy awaits.",
        "state": _build_state_snapshot(),
    }


@app.get("/api/game/state")
async def get_game_state():
    """
    Return the current game state.

    The frontend polls this endpoint roughly once per second to keep the HUD
    up to date (credits, turn, active research bar, etc.).
    """
    return _build_state_snapshot()


@app.get("/api/debug/nav")
async def debug_nav():
    """
    Debug endpoint: returns raw ship coordinates and which system (if any)
    the ship is currently at, along with all galaxy system coordinates.
    Useful for diagnosing proximity-check failures.
    """
    if not game or not game.character_created:
        return {"error": "No game in progress"}
    coords = _ship_coords()
    current = None
    nearby = []
    if coords:
        for sys_coords, sys_data in game.navigation.galaxy.systems.items():
            import math as _math
            dist = _math.sqrt(sum((a - b) ** 2 for a, b in zip(coords, sys_coords)))
            entry = {"name": sys_data.get("name"), "coords": list(sys_coords), "distance": round(dist, 2)}
            if dist < 1.0:
                current = entry
            if dist < 20:
                nearby.append(entry)
    nearby.sort(key=lambda e: e["distance"])
    return {
        "ship_coords": list(coords) if coords else None,
        "current_system": current,
        "nearby_systems": nearby[:10],
    }


@app.post("/api/game/turn/end")
async def end_turn():
    """
    End the current turn and advance to the next.

    Calls game.end_turn() (which resets action points and increments the turn
    counter) then game.advance_turn() (which runs per-turn subsystem updates
    and returns a structured event log for the notification toast queue).
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    success, end_message = game.end_turn()
    # advance_turn also increments current_turn internally; end_turn already did
    # that too — the game is intentionally designed so end_turn is the canonical
    # "pass the turn" action and advance_turn runs the subsystem tick.
    events = game.advance_turn()

    # Snapshot credits BEFORE colony income so the ledger can show the delta.
    credits_before = game.credits

    # Apply colony production + population tax to the player's resources.
    # Returns a financial_summary dict used by the GNN broadcast.
    financial_summary = colony_manager.advance_turn(events)

    credits_after = game.credits

    # Tick all NPC bots so they move toward their goals each turn.
    bot_mgr = getattr(game, "bot_manager", None)
    if bot_mgr:
        try:
            bot_mgr.update_all_bots()
        except Exception as _e:
            print(f"[4X] Warning: bot update failed: {_e}")

    # Generate the Galactic News Network end-of-turn summary.
    gnn = generate_gnn_summary(
        game, colony_manager, events,
        financial_summary, credits_before, credits_after,
    )

    return {
        "success":     success,
        "message":     end_message,
        "new_turn":    game.current_turn,
        "events":      events,          # list of {"channel": str, "message": str}
        "game_ended":  game.game_ended,
        "gnn_summary": gnn,             # Galactic News Network broadcast
        "state":       _build_state_snapshot(),
    }


@app.post("/api/game/save")
async def save_game(request: SaveRequest):
    """
    Persist the current game to a JSON file in the saves/ directory.

    Colony state (Phase 3) will be injected here once the ColonyManager
    is wired in.  For now the save covers all core game state.
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    # Inject colony state so save_game.py persists it transparently via game.colony_state.
    game.colony_state = colony_manager.serialize()

    ok = save_game_module.save_game(game, request.slot_name)
    return {"success": ok, "slot_name": request.slot_name}


@app.get("/api/game/saves")
async def list_saves():
    """Return metadata for all available save files."""
    saves = save_game_module.get_save_files()
    return {"saves": saves}


@app.post("/api/game/load")
async def load_game(request: LoadRequest):
    """
    Load a previously saved game.

    The global game instance is mutated in-place by save_game_module.load_game().
    After loading, colony state (Phase 3) will be restored from game.colony_state.
    """
    if not game:
        raise HTTPException(status_code=500, detail="Game engine not ready.")

    ok, message = save_game_module.load_game(game, request.save_path)
    if not ok:
        raise HTTPException(status_code=400, detail=message)

    # Restore colony manager state from the loaded save (or empty if none saved yet).
    colony_manager.deserialize(getattr(game, "colony_state", {}))

    # Recreate NPC infrastructure — bots and station managers are not serialised
    # in save files, so they must be rebuilt every time a game is loaded.
    _init_bot_manager(game)
    _init_station_manager(game)

    return {
        "success": True,
        "message": message,
        "state": _build_state_snapshot(),
    }


# ===========================================================================
# Character-creation options endpoint
# ===========================================================================

@app.get("/api/game/options")
async def get_game_options():
    """
    Return all choices needed to populate the character-creation screen:
    classes, backgrounds, playable species, and factions.

    Called once when the setup view mounts; results can be cached by the
    frontend for the entire session.
    """
    playable_species = get_playable_species()

    classes_list = [
        {
            "name": name,
            "description": data["description"],
            "starting_credits": data.get("starting_credits", 10000),
            "skills": data.get("skills", []),
            # Flatten bonuses keys for display
            "bonuses": list(data.get("bonuses", {}).keys()),
        }
        for name, data in character_classes.items()
    ]

    backgrounds_list = [
        {
            "name": name,
            "description": data["description"],
            "credit_bonus": data.get("credit_bonus", 0),
            "traits": data.get("traits", []),
        }
        for name, data in character_backgrounds.items()
    ]

    species_list = [
        {
            "name": name,
            "description": data["description"],
            "category": data.get("category", "Unknown"),
            "special_traits": data.get("special_traits", []),
            "biology": data.get("biology", ""),
        }
        for name, data in playable_species.items()
    ]

    factions_list = [
        {
            "name": name,
            "philosophy": data.get("philosophy", ""),
            "primary_focus": data.get("primary_focus", ""),
            "description": data.get("description", ""),
        }
        for name, data in factions.items()
    ]

    # Stat metadata for the point-buy UI
    stat_meta = [
        {"key": key, "name": STAT_NAMES[key]}
        for key in STAT_NAMES
    ]

    return {
        "classes": classes_list,
        "backgrounds": backgrounds_list,
        "species": species_list,
        "factions": factions_list,
        "stats": {
            "names": stat_meta,
            "base_value": BASE_STAT_VALUE,
            "point_buy_points": POINT_BUY_POINTS,
            "max_value": 100,
        },
    }


# ===========================================================================
# Galaxy / Navigation endpoints  (Phase 2)
# ===========================================================================

@app.get("/api/galaxy/map")
async def get_galaxy_map():
    """
    Return all star systems projected onto a 2D axial hex grid.

    The galaxy stores systems with 3D (x, y, z) coordinates.  This endpoint
    projects them to (hex_q, hex_r) using hex_utils.resolve_hex_collisions(),
    resolving any two systems that would land on the same hex by nudging the
    later one to the nearest free neighbour.

    Response shape:
      { systems: [ { name, hex_q, hex_r, x, y, z, type, population,
                     threat_level, controlling_faction, visited, planet_count } ] }
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    galaxy = game.navigation.galaxy
    raw_systems = []

    for coords, data in galaxy.systems.items():
        x, y, z = coords
        raw_systems.append({
            "name":                data.get("name", "Unknown"),
            "x": x, "y": y, "z": z,
            "type":                data.get("type", "Unknown"),
            "population":          data.get("population", 0),
            "threat_level":        data.get("threat_level", 0),
            "resources":           data.get("resources", "Unknown"),
            "description":         data.get("description", ""),
            "controlling_faction": data.get("controlling_faction"),
            "visited":             data.get("visited", False),
            # Count only planet/habitable bodies
            "planet_count": len([
                b for b in data.get("celestial_bodies", [])
                if b.get("object_type") == "Planet"
            ]),
        })

    # Project 3D→2D and resolve hex collisions
    projected = resolve_hex_collisions(raw_systems)

    # Mark systems that have at least one player colony so the renderer can
    # draw territory overlays without a separate API call.
    colonized_systems = {
        c["system_name"] for c in colony_manager.list_colonies()
    }
    for sys in projected:
        sys["has_player_colony"] = sys["name"] in colonized_systems

    # Include deep-space stations (system_name == None) for map rendering
    deep_space_stations = []
    station_mgr = getattr(game, "station_manager", None)
    if station_mgr:
        for st in station_mgr.get_deep_space_stations():
            deep_space_stations.append({
                "name":        st["name"],
                "type":        st["type"],
                "hex_q":       st["hex_q"],
                "hex_r":       st["hex_r"],
                "coordinates": list(st["coordinates"]),
                "services":    st.get("services", []),
                "description": st.get("description", ""),
            })

    return {"systems": projected, "stations": deep_space_stations}


@app.get("/api/system/{system_name}")
async def get_system(system_name: str):
    """
    Fetch detailed info for one star system, including its planet list
    (used to populate the "found colony" button in the right panel).
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    galaxy = game.navigation.galaxy

    # Find the system by name across all coordinate keys
    system_data = None
    system_coords = None
    for coords, data in galaxy.systems.items():
        if data.get("name", "").lower() == system_name.lower():
            system_data = data
            system_coords = coords
            break

    if not system_data:
        raise HTTPException(status_code=404, detail=f"System '{system_name}' not found.")

    # Mark as visited
    system_data["visited"] = True

    # Build planet list
    planets = []
    for body in system_data.get("celestial_bodies", []):
        if body.get("object_type") == "Planet":
            planet_name = body.get("name", "Unknown Planet")
            planets.append({
                "name":                planet_name,
                "subtype":             body.get("subtype", "Unknown"),
                "habitable":           body.get("habitable", False),
                "has_atmosphere":      body.get("has_atmosphere", False),
                "population":          body.get("population", 0),
                "resources":           body.get("resources", []),
                "controlling_faction": body.get("controlling_faction"),
                "has_shipyard":        body.get("shipyard", False),
                "has_colony":          planet_name in colony_manager.colonies,
            })

    # Market info — gated by trade infrastructure.
    # Player colonies only get market access if a Trade Nexus or Spaceport Hub
    # has been built; NPC systems always expose their market data.
    market_info = None
    try:
        if hasattr(game, "economy") and game.economy:
            mkt = game.economy.get_market_info(system_name)
            if mkt:
                colony_here = any(
                    c.system_name == system_name
                    for c in colony_manager.colonies.values()
                )
                if not colony_here or _colony_has_trade_building(system_name):
                    market_info = mkt
    except Exception:
        pass

    x, y, z = system_coords
    hex_coord = galaxy_coords_to_hex(x, y)

    return {
        "name":                system_data.get("name"),
        "type":                system_data.get("type"),
        "coordinates":         [x, y, z],
        "hex_q":               hex_coord.q,
        "hex_r":               hex_coord.r,
        "population":          system_data.get("population", 0),
        "threat_level":        system_data.get("threat_level", 0),
        "resources":           system_data.get("resources", ""),
        "description":         system_data.get("description", ""),
        "controlling_faction": system_data.get("controlling_faction"),
        "visited":             True,
        "planets":             planets,
        "market":              market_info,
    }


@app.get("/api/system/{system_name}/presence")
async def get_system_presence(system_name: str):
    """
    Return the NPC presence at a star system: stations, docked NPC ships,
    and settled (NPC-colonised) planets.  Used by the galaxy panel to display
    stations and NPCs the player can see on arrival.
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    galaxy = game.navigation.galaxy

    # Find the system by name
    system_data = next(
        (s for s in galaxy.systems.values() if s.get("name") == system_name),
        None,
    )
    if not system_data:
        raise HTTPException(status_code=404, detail=f"System '{system_name}' not found.")

    coords = system_data.get("coordinates")
    faction = system_data.get("controlling_faction") or ""

    # NPC-colonised planets (any planet with a population)
    npc_colonies = []
    for planet in system_data.get("planets", []):
        pop = planet.get("population", 0)
        if pop and pop > 0:
            npc_colonies.append({
                "name":       planet.get("name", "Unknown"),
                "type":       planet.get("type") or planet.get("subtype", "Planet"),
                "population": pop,
                "faction":    faction,
            })

    # Stations at this system
    stations = []
    station_mgr = getattr(game, "station_manager", None)
    if station_mgr:
        for station in station_mgr.stations.values():
            if station.get("system_name") == system_name:
                stations.append({
                    "name":        station["name"],
                    "type":        station["type"],
                    "services":    station.get("services", []),
                    "description": station.get("description", ""),
                })

    # NPC ships docked at this system
    npc_ships = []
    bot_mgr = getattr(game, "bot_manager", None)
    if bot_mgr and coords:
        for bot in bot_mgr.bots:
            bot_ship = getattr(bot, "ship", None)
            if bot_ship and getattr(bot_ship, "coordinates", None) == tuple(coords):
                npc_ships.append({
                    "name":      bot.name,
                    "ship_type": bot.bot_type,
                    "vessel":    getattr(bot_ship, "name", "Unknown Vessel"),
                })

    # Whether a tradeable market exists here — same trade-building gate as the
    # system detail endpoint.  Player colonies need a Trade Nexus / Spaceport Hub.
    has_market = False
    if hasattr(game, "economy") and game.economy:
        try:
            if game.economy.get_market_info(system_name):
                colony_here = any(
                    c.system_name == system_name
                    for c in colony_manager.colonies.values()
                )
                has_market = (not colony_here) or _colony_has_trade_building(system_name)
        except Exception:
            pass

    return {
        "system_name":   system_name,
        "npc_colonies":  npc_colonies,
        "stations":      stations,
        "npc_ships":     npc_ships,
        "has_market":    has_market,
    }


# ===========================================================================
# Space Station endpoints
# ===========================================================================

@app.get("/api/station/{station_name}")
async def get_station(station_name: str):
    """
    Return full details for a named space station: type, location, services,
    owner status, and whether a market is available here.
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    station_mgr = getattr(game, "station_manager", None)
    if not station_mgr:
        raise HTTPException(status_code=503, detail="Station manager unavailable.")

    station = station_mgr.get_station_by_name(station_name)
    if not station:
        raise HTTPException(status_code=404, detail=f"Station '{station_name}' not found.")

    has_market = any(s in station.get("services", [])
                     for s in ("Market", "Ore Processing", "Luxury Goods"))
    has_upgrades = "Ship Upgrades" in station.get("services", [])

    return {
        "name":        station["name"],
        "type":        station["type"],
        "description": station.get("description", ""),
        "services":    station.get("services", []),
        "coordinates": list(station["coordinates"]),
        "system_name": station.get("system_name"),      # None = deep space
        "owner":       station.get("owner"),
        "upgrade_level": station.get("upgrade_level", 1),
        "has_market":  has_market,
        "has_upgrades": has_upgrades,
    }


@app.get("/api/station/{station_name}/upgrades")
async def get_station_upgrades(station_name: str):
    """
    Return available ship upgrades at this station.
    Only stations with 'Ship Upgrades' in their services offer this.
    Excludes upgrades the player's ship already has installed.
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    station_mgr = getattr(game, "station_manager", None)
    if not station_mgr:
        raise HTTPException(status_code=503, detail="Station manager unavailable.")

    station = station_mgr.get_station_by_name(station_name)
    if not station:
        raise HTTPException(status_code=404, detail=f"Station '{station_name}' not found.")

    if "Ship Upgrades" not in station.get("services", []):
        raise HTTPException(status_code=400, detail="This station does not offer ship upgrades.")

    from station_manager import ShipUpgradeSystem
    upgrade_sys = ShipUpgradeSystem()
    ship = game.navigation.current_ship
    if not ship:
        raise HTTPException(status_code=400, detail="No active ship.")

    available = upgrade_sys.get_available_upgrades(ship)

    # Flatten for the frontend: list of {category, name, cost, description, effects}
    items = []
    for category, upgrades in available.items():
        for name, data in upgrades.items():
            effects = {k: v for k, v in data.items() if k not in ("cost", "description")}
            items.append({
                "category":    category,
                "name":        name,
                "cost":        data.get("cost", 0),
                "description": data.get("description", ""),
                "effects":     effects,
            })

    return {
        "station_name":    station_name,
        "player_credits":  game.credits,
        "upgrades":        items,
        "installed":       list(getattr(game.navigation.current_ship, "upgrades", {}).keys()),
    }


class StationUpgradeRequest(BaseModel):
    category:     str
    upgrade_name: str


@app.post("/api/station/{station_name}/upgrade")
async def buy_station_upgrade(station_name: str, request: StationUpgradeRequest):
    """
    Purchase and install a ship upgrade from this station.
    Deducts credits and applies stat effects to the player's ship immediately.
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    station_mgr = getattr(game, "station_manager", None)
    if not station_mgr:
        raise HTTPException(status_code=503, detail="Station manager unavailable.")

    station = station_mgr.get_station_by_name(station_name)
    if not station:
        raise HTTPException(status_code=404, detail=f"Station '{station_name}' not found.")

    if "Ship Upgrades" not in station.get("services", []):
        raise HTTPException(status_code=400, detail="This station does not offer ship upgrades.")

    from station_manager import ShipUpgradeSystem
    upgrade_sys = ShipUpgradeSystem()

    # Validate category + upgrade name
    cat_upgrades = upgrade_sys.upgrade_categories.get(request.category)
    if not cat_upgrades:
        raise HTTPException(status_code=404, detail=f"Unknown upgrade category '{request.category}'.")
    upgrade_data = cat_upgrades.get(request.upgrade_name)
    if not upgrade_data:
        raise HTTPException(status_code=404, detail=f"Unknown upgrade '{request.upgrade_name}'.")

    # Credits check
    cost = upgrade_data.get("cost", 0)
    if game.credits < cost:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient credits. Need {cost:,}, have {game.credits:,}."
        )

    ship = game.navigation.current_ship
    if not ship:
        raise HTTPException(status_code=400, detail="No active ship.")

    ok, message = upgrade_sys.install_upgrade(ship, request.upgrade_name, upgrade_data)
    if not ok:
        raise HTTPException(status_code=400, detail=message)

    game.credits -= cost

    return {
        "success":           True,
        "message":           message,
        "credits_remaining": game.credits,
        "fuel":              ship.fuel,
        "max_fuel":          ship.max_fuel,
        "jump_range":        ship.jump_range,
        "max_cargo":         ship.max_cargo,
        "installed_upgrades": list(getattr(ship, "upgrades", {}).keys()),
    }


class JumpRequest(BaseModel):
    """Request body for jumping the player's ship."""
    target_x: float
    target_y: float
    target_z: float


@app.post("/api/ship/jump")
async def ship_jump(request: JumpRequest):
    """
    Jump the player's ship to the target galaxy coordinates.

    Consumes one action point.  The jump validates fuel, jump range, and
    ether energy friction using the existing Ship.jump_to() method.
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    nav = game.navigation
    ship = nav.current_ship
    if not ship:
        raise HTTPException(status_code=400, detail="No active ship.")

    # Check action points first
    can_act, reason = game.consume_action("navigation")
    if not can_act:
        raise HTTPException(status_code=400, detail=reason)

    target = (request.target_x, request.target_y, request.target_z)
    success, message = ship.jump_to(target, nav.galaxy, game)

    # Determine if there is a system at the destination
    dest_system = nav.galaxy.get_system_at(*target)

    return {
        "success":     success,
        "message":     message,
        "new_coords":  list(ship.coordinates),
        "fuel_remaining": ship.fuel,
        "system_at_destination": dest_system,
    }


@app.get("/api/ship/status")
async def get_ship_status():
    """Return the current ship's full status."""
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    ship = game.navigation.current_ship
    if not ship:
        return {"ship": None}

    return {
        "name":        ship.name,
        "ship_class":  ship.ship_class,
        "coordinates": list(ship.coordinates),
        "fuel":        ship.fuel,
        "max_fuel":    ship.max_fuel,
        "jump_range":  ship.jump_range,
        "cargo_used":  sum(ship.cargo.values()) if ship.cargo else 0,
        "max_cargo":   ship.max_cargo,
        "cargo":       dict(ship.cargo) if ship.cargo else {},
    }


@app.get("/api/ship/attributes")
async def get_ship_attributes():
    """
    Return the ship's full attribute profile (0–100 per attribute) grouped by
    category, plus derived legacy stats and the current component loadout.
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    ship = game.navigation.current_ship
    if not ship:
        raise HTTPException(status_code=400, detail="No active ship.")

    from ship_builder import compute_ship_profile
    from ship_attributes import SHIP_ATTRIBUTE_CATEGORIES, SHIP_ATTRIBUTE_DEFINITIONS
    from crew import calculate_crew_bonuses

    # Compute base profile from installed components
    profile = compute_ship_profile(getattr(ship, "components", {}) or {})

    # Layer crew bonuses on top
    if getattr(ship, "crew", None):
        try:
            for stat, bonus in calculate_crew_bonuses(ship.crew).items():
                if stat in profile:
                    profile[stat] = min(100.0, profile[stat] + bonus)
        except Exception:
            pass

    # Group by category for the frontend
    categories = []
    for cat in SHIP_ATTRIBUTE_CATEGORIES:
        attrs = []
        for attr_id in cat["attributes"]:
            meta = SHIP_ATTRIBUTE_DEFINITIONS.get(attr_id, {})
            attrs.append({
                "id":          attr_id,
                "name":        meta.get("name", attr_id),
                "description": meta.get("description", ""),
                "value":       round(profile.get(attr_id, 30.0), 1),
            })
        categories.append({"id": cat["id"], "name": cat["name"], "attributes": attrs})

    return {
        "ship_name":   ship.name,
        "ship_class":  ship.ship_class,
        "fuel":        ship.fuel,
        "max_fuel":    ship.max_fuel,
        "jump_range":  ship.jump_range,
        "max_cargo":   ship.max_cargo,
        "components":  getattr(ship, "components", {}),
        "categories":  categories,
    }


@app.get("/api/ship/components")
async def get_ship_components():
    """
    Return the ship's current component loadout plus every component available
    for each slot (filtered by player faction where relevant).
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    ship = game.navigation.current_ship
    if not ship:
        raise HTTPException(status_code=400, detail="No active ship.")

    from ship_builder import get_available_components, ship_components, COMPONENT_CATEGORY_LABELS

    player_faction = getattr(game, "player_faction", None)
    if not player_faction and hasattr(game, "character") and game.character:
        player_faction = game.character.get("faction")

    slots = {}
    for slot_key in ("hulls", "engines", "weapons", "shields", "sensors", "support",
                     "computing", "communications", "crew_modules"):
        available = get_available_components(slot_key, ship, player_faction)
        slots[slot_key] = {
            "label": COMPONENT_CATEGORY_LABELS.get(slot_key, slot_key.title()),
            "available": [
                {
                    "name":         name,
                    "cost":         int(data.get("cost", 0)),
                    "faction_lock": data.get("faction_lock"),
                    "failure_chance": round(float(data.get("failure_chance", 0)) * 100, 1),
                    "lore":         data.get("lore", ""),
                }
                for name, data in available.items()
            ],
        }

    return {
        "installed":  getattr(ship, "components", {}),
        "slots":      slots,
    }


class InstallComponentRequest(BaseModel):
    """Request body for installing a component on the player's ship."""
    category: str
    component_name: str


@app.post("/api/ship/components/install")
async def install_ship_component(request: InstallComponentRequest):
    """
    Replace or add a component on the player's ship.  Recalculates all derived
    stats after installation.  Does not cost an action point (must be done at a
    shipyard in the future).
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    ship = game.navigation.current_ship
    if not ship:
        raise HTTPException(status_code=400, detail="No active ship.")

    from ship_builder import install_component, ship_components, COMPONENT_CATEGORY_ALIASES

    player_faction = None
    if hasattr(game, "character") and game.character:
        player_faction = game.character.get("faction")

    # Resolve category alias and look up component cost before installing
    resolved_cat = COMPONENT_CATEGORY_ALIASES.get(request.category, request.category)
    comp_data = (
        ship_components.get(request.category, {}).get(request.component_name)
        or ship_components.get(resolved_cat, {}).get(request.component_name)
    )
    cost = int((comp_data or {}).get("cost", 0))

    if cost > 0 and game.credits < cost:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient credits. Need {cost:,} cr, have {game.credits:,} cr."
        )

    success, message = install_component(
        ship, request.category, request.component_name, player_faction
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)

    # Deduct credits on success
    if cost > 0:
        game.credits -= cost

    # Recompute all derived stats
    ship.calculate_stats_from_components()

    return {
        "success":           True,
        "message":           message,
        "credits_remaining": game.credits,
        "components":        getattr(ship, "components", {}),
        "fuel":              ship.fuel,
        "max_fuel":          ship.max_fuel,
        "jump_range":        ship.jump_range,
        "max_cargo":         ship.max_cargo,
    }


# ===========================================================================
# Colony endpoints  (Phase 3)
# ===========================================================================

class FoundColonyRequest(BaseModel):
    """Request body for founding a new colony on a planet."""
    system_name: str
    planet_type: str


class BuildImprovementRequest(BaseModel):
    """Request body for placing an improvement on a colony tile."""
    q: int
    r: int
    improvement_type: str


class DemolishRequest(BaseModel):
    """Request body for demolishing an improvement (identifies the tile)."""
    q: int
    r: int


@app.get("/api/colony/all")
async def get_all_colonies():
    """
    Return a summary list of all player-owned colonies.
    Used by the left-panel colony list and the HUD.
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")
    return {"colonies": colony_manager.list_colonies()}




@app.get("/api/colony/overview")
async def get_colony_overview():
    """
    Return rich per-colony data plus empire-wide totals for the colony
    management screen.  Includes improvement breakdown and income split.
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    from backend.colony import POPULATION_INCOME_PER_10K

    colonies_out = []
    for planet_name, colony in colony_manager.colonies.items():
        prod = colony_manager.calculate_colony_production(planet_name)

        # Count each improvement type across all tiles
        improvements: dict[str, int] = {}
        for tile in colony.tiles.values():
            if tile.improvement:
                improvements[tile.improvement] = improvements.get(tile.improvement, 0) + 1

        pop_income     = int(colony.population / 10_000 * POPULATION_INCOME_PER_10K)
        bldg_income    = int(prod.get("credits", 0))
        total_income   = pop_income + bldg_income

        colonies_out.append({
            "planet_name":      planet_name,
            "system_name":      colony.system_name,
            "planet_type":      colony.planet_type,
            "population":       colony.population,
            "founded_turn":     colony.founded_turn,
            "tile_count":       len(colony.tiles),
            "improvement_count": sum(1 for t in colony.tiles.values() if t.improvement),
            "improvements":     improvements,
            "production":       prod,
            "income":           total_income,
            "pop_income":       pop_income,
            "bldg_income":      bldg_income,
        })

    all_prod    = colony_manager.calculate_all_production()
    total_pop   = sum(c["population"]   for c in colonies_out)
    total_income = sum(c["income"]       for c in colonies_out)

    return {
        "colonies": colonies_out,
        "totals": {
            "colony_count": len(colonies_out),
            "population":   total_pop,
            "income":       total_income,
            "production":   all_prod,
        },
    }

@app.get("/api/colony/improvements")
async def get_improvements_catalogue():
    """
    Return the full improvement catalogue annotated with the current player's
    unlock status (based on completed research).

    The build menu uses this to show locked improvements greyed-out with
    their research requirement displayed as a tooltip.
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")
    catalogue = ColonyManager.get_improvements_catalogue(game.completed_research)
    return {"improvements": catalogue}


@app.get("/api/colony/{planet_name}")
async def get_colony(planet_name: str):
    """
    Return the full tile grid and per-turn production summary for one colony.
    Called when the player clicks an owned planet to open the colony view.
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    colony_dict = colony_manager.get_colony_dict(planet_name)
    if colony_dict is None:
        raise HTTPException(status_code=404, detail=f"No colony on '{planet_name}'.")
    return colony_dict


@app.post("/api/colony/{planet_name}/found")
async def found_colony(planet_name: str, request: FoundColonyRequest):
    """
    Found a new colony on a habitable planet.

    Generates a hex tile grid seeded from the planet name (so the same planet
    always gets the same terrain layout, even across game saves).
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    if not _player_is_in_system(request.system_name):
        raise HTTPException(
            status_code=403,
            detail=f"You must be in the {request.system_name} system to found a colony there."
        )

    success, message, _colony = colony_manager.found_colony(
        planet_name, request.system_name, request.planet_type
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {
        "success": True,
        "message": message,
        "colony": colony_manager.get_colony_dict(planet_name),
    }


@app.post("/api/colony/{planet_name}/build")
async def build_improvement(planet_name: str, request: BuildImprovementRequest):
    """
    Build an improvement on a specific tile of a colony.

    Validates:
      * Research prerequisite met.
      * Terrain restriction satisfied.
      * Sufficient credits.
      * Action point available.
    Deducts credits and consumes one action on success.
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    success, message = colony_manager.build_improvement(
        planet_name, request.q, request.r, request.improvement_type
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)

    # If this is the first trade building on the colony, register the system
    # as a market in the economy engine so buy/sell transactions work.
    if request.improvement_type in _TRADE_BUILDINGS:
        colony = colony_manager.colonies.get(planet_name)
        if colony and hasattr(game, "economy") and game.economy:
            sys_name = colony.system_name
            if not game.economy.get_market_info(sys_name):
                import random as _rnd
                _RICHNESS = ["Poor", "Moderate", "Moderate", "Rich", "Abundant"]
                try:
                    game.economy.create_market({
                        "name":       sys_name,
                        "type":       "colony",
                        "population": colony.population,
                        "resources":  _rnd.choice(_RICHNESS),
                    })
                    message += f" Interstellar market opened at {sys_name}."
                except Exception as _me:
                    print(f"[4X] Warning: colony market init failed for {sys_name}: {_me}")

    return {
        "success": True,
        "message": message,
        "colony": colony_manager.get_colony_dict(planet_name),
        "credits_remaining": game.credits,
    }


@app.delete("/api/colony/{planet_name}/build")
async def demolish_improvement(planet_name: str, request: DemolishRequest):
    """
    Demolish the improvement on a specific tile.
    Refunds 50% of the improvement's original cost.
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    success, message, refund = colony_manager.demolish_improvement(
        planet_name, request.q, request.r
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {
        "success": True,
        "message": message,
        "refund": refund,
        "colony": colony_manager.get_colony_dict(planet_name),
        "credits_remaining": game.credits,
    }


class UpgradeRequest(BaseModel):
    """Request body for upgrading an improvement on a colony tile."""
    q: int
    r: int


@app.post("/api/colony/{planet_name}/upgrade")
async def upgrade_improvement(planet_name: str, request: UpgradeRequest):
    """
    Upgrade the improvement on a tile to the next production tier.

    Each tier costs a fraction of the original build cost and multiplies
    output: Tier 2 = 1.5×, Tier 3 = 2.2× base production.
    Max upgrade level is 2 (Tier 3).
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    success, message = colony_manager.upgrade_improvement(
        planet_name, request.q, request.r
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {
        "success": True,
        "message": message,
        "colony": colony_manager.get_colony_dict(planet_name),
        "credits_remaining": game.credits,
    }


# ===========================================================================
# Research endpoints  (Phase 4)
# ===========================================================================

class StartResearchRequest(BaseModel):
    """Request body for beginning a new research project."""
    research_name: str


@app.get("/api/research/tree")
async def get_research_tree():
    """
    Return the full research tree with each node's status for the current player.

    Status flags per node:
      completed — already finished
      active    — currently being researched
      available — prerequisites met and not yet started (can be started)

    The frontend uses these flags to render the tech tree with correct colouring
    and to show the Start Research button only on available nodes.
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    # get_available_research_projects() returns a dict of researchable (not yet
    # completed, prerequisites met) projects.
    available_dict = game.get_available_research_projects()
    available_names = set(available_dict.keys()) if available_dict else set()

    # Determine progress percentage for the active research node
    active_time = None
    if game.active_research and game.active_research in all_research:
        active_time = all_research[game.active_research].get("research_time", 1)

    nodes = []
    for name, data in all_research.items():
        completed  = name in game.completed_research
        active     = (name == game.active_research)
        available  = (name in available_names) and not completed

        nodes.append({
            "name":           name,
            "category":       data.get("category", ""),
            "description":    data.get("description", ""),
            "difficulty":     data.get("difficulty", 5),
            "research_cost":  data.get("research_cost", 0),
            "research_time":  data.get("research_time", 0),
            "prerequisites":  data.get("prerequisites", []),
            "unlocks":        data.get("unlocks", []),
            "related_energy": data.get("related_energy", ""),
            "completed":      completed,
            "active":         active,
            "available":      available,
        })

    return {
        "nodes":           nodes,
        "active_research": game.active_research,
        "research_progress": game.research_progress,
        "active_research_time": active_time,
        "completed_count": len(game.completed_research),
    }


@app.get("/api/research/status")
async def get_research_status():
    """
    Return a brief snapshot of the current research progress.
    Polled by the HUD to update the research progress bar without re-fetching
    the entire tree.
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    if not game.active_research:
        return {"active": None, "progress": 0, "total_time": 0, "percent": 0.0}

    total = all_research.get(game.active_research, {}).get("research_time", 1)
    percent = round(min(100.0, game.research_progress / max(total, 1) * 100), 1)

    return {
        "active":       game.active_research,
        "progress":     game.research_progress,
        "total_time":   total,
        "percent":      percent,
    }


@app.post("/api/research/start")
async def start_research(request: StartResearchRequest):
    """
    Begin a new research project.

    Delegates to game.start_research_project() which checks:
      * No research is currently active.
      * The research exists.
      * All prerequisites are completed.
      * The player has sufficient credits.
    Credits are deducted immediately on start.
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    success, message = game.start_research_project(request.research_name)
    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {
        "success":         True,
        "message":         message,
        "active_research": game.active_research,
        "credits_remaining": game.credits,
    }


@app.post("/api/research/cancel")
async def cancel_research():
    """
    Cancel the active research project.
    No credits are refunded.
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    success, message = game.cancel_research()
    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {"success": True, "message": message}


# ===========================================================================
# Faction / Diplomacy endpoints  (Phase 4)
# ===========================================================================

class FactionActionRequest(BaseModel):
    """Request body for performing a diplomatic action with a faction."""
    action: str          # e.g. "gift"
    amount: int = 10     # reputation points to gain (gift costs 500 cr / point)


@app.get("/api/factions")
async def get_all_factions():
    """
    Return a summary list of every faction with the player's current reputation.
    Sorted descending by reputation so Allied factions appear first.
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    fs = game.faction_system
    result = []
    for faction_name, reputation in fs.player_relations.items():
        faction_data = factions.get(faction_name, {})
        result.append({
            "name":          faction_name,
            "philosophy":    faction_data.get("philosophy", ""),
            "primary_focus": faction_data.get("primary_focus", ""),
            "reputation":    reputation,
            "status":        fs.get_reputation_status(faction_name),
        })

    # Sorted Allied → Enemy
    result.sort(key=lambda f: -f["reputation"])
    return {"factions": result}


@app.get("/api/faction/{faction_name}")
async def get_faction(faction_name: str):
    """
    Return full detail for one faction, including available benefits,
    current activity, and territory count.
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    fs  = game.faction_system
    info = fs.get_faction_info(faction_name)
    if info is None:
        raise HTTPException(status_code=404, detail=f"Faction '{faction_name}' not found.")

    benefits = fs.get_faction_benefits(faction_name)
    rep      = fs.player_relations.get(faction_name, 0)
    status   = fs.get_reputation_status(faction_name)

    return {
        "name":              faction_name,
        "philosophy":        info.get("philosophy", ""),
        "primary_focus":     info.get("primary_focus", ""),
        "description":       info.get("description", ""),
        "government_type":   info.get("government_type", ""),
        "origin_story":      info.get("origin_story", ""),
        "founding_year":     info.get("founding_year"),
        "founding_epoch":    info.get("founding_epoch", ""),
        "current_activity":  info.get("current_activity", ""),
        "territory_count":   info.get("territory_count", 0),
        "preferred_trades":  info.get("preferred_trades", []),
        "low_rep_benefits":  info.get("low_rep_benefits", []),
        "mid_rep_benefits":  info.get("mid_rep_benefits", []),
        "high_rep_benefits": info.get("high_rep_benefits", []),
        "benefits":          benefits,
        "reputation":        rep,
        "status":            status,
    }


@app.post("/api/faction/{faction_name}/action")
async def faction_action(faction_name: str, request: FactionActionRequest):
    """
    Perform a diplomatic action with a faction.

    Currently supported actions:
      "gift" — spend 500 credits per reputation point to improve standing.
                amount is capped at 20 points per action.
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    fs = game.faction_system
    if faction_name not in fs.player_relations:
        raise HTTPException(status_code=404, detail=f"Faction '{faction_name}' not found.")

    if request.action == "gift":
        points = max(1, min(20, request.amount))   # clamp 1–20 points
        cost   = points * 500                       # 500 credits per point
        if game.credits < cost:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient credits. Gift costs {cost:,} cr ({points} pt × 500 cr)."
            )
        game.credits -= cost
        message = fs.modify_reputation(faction_name, points, "diplomatic gift")
        return {
            "success":           True,
            "message":           message,
            "reputation":        fs.player_relations[faction_name],
            "status":            fs.get_reputation_status(faction_name),
            "credits_remaining": game.credits,
        }

    raise HTTPException(status_code=400, detail=f"Unknown action: '{request.action}'.")


# ===========================================================================
# Trade / Market endpoints  (Phase 5)
# ===========================================================================

class TradeRequest(BaseModel):
    """Request body for a buy or sell transaction."""
    system_name: str
    commodity:   str
    quantity:    int


@app.get("/api/market/{system_name}")
async def get_market(system_name: str):
    """
    Return commodity prices, supply, and demand for a star system's market.

    Also includes best_buys (high supply, low price) and best_sells
    (high demand, high price) computed by the economy engine, and the
    player's current inventory so the frontend can show what can be sold.
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    if not hasattr(game, "economy") or not game.economy:
        raise HTTPException(status_code=503, detail="Economy system unavailable.")

    info = game.economy.get_market_info(system_name)
    if not info:
        raise HTTPException(status_code=404, detail=f"No market at '{system_name}'.")

    market = info["market"]

    # Build a flat commodity list for the frontend — one entry per good.
    commodities = []
    for commodity, price in market.get("prices", {}).items():
        supply = market.get("supply", {}).get(commodity, 0)
        demand = market.get("demand", {}).get(commodity, 0)
        in_inventory = game.inventory.get(commodity, 0)
        commodities.append({
            "name":         commodity,
            "price":        round(price, 2),
            "supply":       int(supply),
            "demand":       int(demand),
            "in_inventory": int(in_inventory),
        })

    # Sort alphabetically for a stable display order
    commodities.sort(key=lambda c: c["name"])

    return {
        "system_name":  system_name,
        "commodities":  commodities,
        "best_buys":    [{"name": b[0], "price": b[1], "supply": b[2]} for b in info.get("best_buys",  [])],
        "best_sells":   [{"name": s[0], "price": s[1], "demand": s[2]} for s in info.get("best_sells", [])],
        "player_credits": game.credits,
        "cargo_used":   sum(game.inventory.values()) if game.inventory else 0,
    }


@app.post("/api/trade/buy")
async def trade_buy(request: TradeRequest):
    """
    Buy a commodity at the current system's market.

    Delegates to game.perform_trade_buy() which:
      * Checks cargo capacity on the active ship.
      * Deducts credits.
      * Adds the goods to game.inventory and ship.cargo.
    Consumes one action point.
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    # Action point check — trading costs one action
    ok, reason = game.consume_action("trade")
    if not ok:
        raise HTTPException(status_code=400, detail=reason)

    if not _player_is_at_market(request.system_name):
        game.turn_actions_remaining = min(game.turn_actions_remaining + 1, game.max_actions_per_turn)
        raise HTTPException(
            status_code=403,
            detail=f"You must be at {request.system_name} to trade there."
        )

    success, message = game.perform_trade_buy(
        request.system_name, request.commodity, request.quantity
    )
    if not success:
        # Refund the action point since the trade failed
        game.turn_actions_remaining = min(game.turn_actions_remaining + 1, game.max_actions_per_turn)
        raise HTTPException(status_code=400, detail=message)

    # Return fresh market + player data so the frontend can update immediately
    info = game.economy.get_market_info(request.system_name)
    return {
        "success":        True,
        "message":        message,
        "credits_remaining": game.credits,
        "inventory":      dict(game.inventory),
        "market_prices":  info["market"]["prices"] if info else {},
    }


@app.post("/api/trade/sell")
async def trade_sell(request: TradeRequest):
    """
    Sell a commodity at the current system's market.

    Delegates to game.perform_trade_sell() which:
      * Validates inventory.
      * Adds credits earned.
      * Removes goods from game.inventory and ship.cargo.
    Consumes one action point.
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    ok, reason = game.consume_action("trade")
    if not ok:
        raise HTTPException(status_code=400, detail=reason)

    if not _player_is_at_market(request.system_name):
        game.turn_actions_remaining = min(game.turn_actions_remaining + 1, game.max_actions_per_turn)
        raise HTTPException(
            status_code=403,
            detail=f"You must be at {request.system_name} to trade there."
        )

    success, message = game.perform_trade_sell(
        request.system_name, request.commodity, request.quantity
    )
    if not success:
        game.turn_actions_remaining = min(game.turn_actions_remaining + 1, game.max_actions_per_turn)
        raise HTTPException(status_code=400, detail=message)

    info = game.economy.get_market_info(request.system_name)
    return {
        "success":        True,
        "message":        message,
        "credits_remaining": game.credits,
        "inventory":      dict(game.inventory),
        "market_prices":  info["market"]["prices"] if info else {},
    }


# ===========================================================================
# Lore endpoints  (Phase 4)
# ===========================================================================

@app.get("/api/lore/energies")
async def get_lore_energies():
    """
    Return the full catalogue of 50 energy types from energies.py.

    Each entry includes category, description, efficiency, stability,
    safety_level, applications, and optional faction/warning fields.
    The frontend uses this for research tree tooltips and galaxy ether overlays.
    """
    return {"energies": all_energies}


@app.get("/api/character/sheet")
async def get_character_sheet():
    """
    Full character sheet — base stats, derived metrics, class info,
    background traits, and equipment slots (placeholders until the
    inventory system is wired to the player).
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    from characters import (
        character_classes, character_backgrounds,
        STAT_NAMES, STAT_DESCRIPTIONS, DERIVED_METRIC_INFO,
        calculate_derived_attributes,
    )

    raw_stats = game.character_stats or {}
    derived   = calculate_derived_attributes(raw_stats) if raw_stats else {}

    class_data = character_classes.get(game.character_class, {})
    bg_data    = character_backgrounds.get(game.character_background, {})

    # Format bonuses as human-readable strings (e.g. "trade_discount" → "Trade Discount: +10%")
    formatted_bonuses = {}
    for key, val in class_data.get("bonuses", {}).items():
        label = key.replace("_", " ").title()
        if isinstance(val, float) and val < 2:
            formatted_bonuses[label] = f"+{int(val * 100)}%"
        else:
            formatted_bonuses[label] = str(val)

    return {
        "name":             game.player_name,
        "character_class":  game.character_class,
        "class_description": class_data.get("description", ""),
        "background":       game.character_background,
        "background_description": bg_data.get("description", ""),
        "species":          game.character_species,
        "faction":          game.character_faction,
        "xp":               getattr(game, "xp", 0),
        "level":            getattr(game, "level", 1),
        "stats": [
            {
                "abbr":        abbr,
                "name":        STAT_NAMES[abbr],
                "description": STAT_DESCRIPTIONS[abbr],
                "value":       raw_stats.get(abbr, 30),
            }
            for abbr in STAT_NAMES
        ],
        "derived": [
            {
                "name":        name,
                "value":       derived.get(name, 0),
                "formula":     DERIVED_METRIC_INFO[name]["formula"],
                "description": DERIVED_METRIC_INFO[name]["description"],
            }
            for name in DERIVED_METRIC_INFO
        ],
        "skills":    class_data.get("skills", []),
        "bonuses":   formatted_bonuses,
        "traits":    bg_data.get("traits", []),
        # Inventory slots — placeholders until the equipment system is active
        "equipment":             [],
        "cybernetics":           [],
        "etheric_enhancements":  [],
    }


@app.get("/api/lore/factions")
async def get_lore_factions():
    """
    Return static faction lore (descriptions, philosophies, origin stories)
    without the dynamic reputation data.  Used for flavour-text modals.
    """
    lore = []
    for name, data in factions.items():
        lore.append({
            "name":           name,
            "philosophy":     data.get("philosophy", ""),
            "primary_focus":  data.get("primary_focus", ""),
            "description":    data.get("description", ""),
            "government_type":data.get("government_type", ""),
            "founding_epoch": data.get("founding_epoch", ""),
            "founding_year":  data.get("founding_year"),
            "origin_story":   data.get("origin_story", ""),
        })
    return {"factions": lore}


# ===========================================================================
# Static files — mounted LAST so /api/* routes always win
# ===========================================================================

FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")

# html=True makes StaticFiles serve index.html for any path that doesn't
# match a real file — the standard pattern for single-page apps.
app.mount(
    "/",
    StaticFiles(directory=FRONTEND_DIR, html=True),
    name="static",
)
