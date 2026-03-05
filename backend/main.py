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
        "ship": ship_info,
    }


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

    # Initialise NPC infrastructure — bots and stations are generated fresh each game.
    try:
        from ai_bots import BotManager
        game.bot_manager = BotManager(game)
    except Exception as _e:
        print(f"[4X] Warning: bot_manager init failed: {_e}")
        game.bot_manager = None

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

    # Apply colony production to the player's resources for this turn.
    # colony_manager.advance_turn() appends ECON-channel events to the same list.
    colony_manager.advance_turn(events)

    return {
        "success": success,
        "message": end_message,
        "new_turn": game.current_turn,
        "events": events,          # list of {"channel": str, "message": str}
        "game_ended": game.game_ended,
        "state": _build_state_snapshot(),
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

    # Recreate station manager + station markets — these are not serialised in the
    # save file, so they must be rebuilt every time a game is loaded.
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
            planets.append({
                "name":                body.get("name", "Unknown Planet"),
                "subtype":             body.get("subtype", "Unknown"),
                "habitable":           body.get("habitable", False),
                "has_atmosphere":      body.get("has_atmosphere", False),
                "population":          body.get("population", 0),
                "resources":           body.get("resources", []),
                "controlling_faction": body.get("controlling_faction"),
                "has_shipyard":        body.get("shipyard", False),
            })

    # Market info (if available)
    market_info = None
    try:
        if hasattr(game, "economy") and game.economy:
            mkt = game.economy.get_market_info(system_name)
            if mkt:
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

    # Whether a tradeable market exists here
    has_market = False
    if hasattr(game, "economy") and game.economy:
        try:
            has_market = bool(game.economy.get_market_info(system_name))
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
