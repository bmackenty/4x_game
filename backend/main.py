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

import math
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
from professions import PROFESSIONS, PROFESSION_CATEGORIES_ORDERED, ProfessionSystem
from species import get_playable_species
from factions import factions                                  # module-level dict
from research import all_research, RESEARCH_PATH_CATEGORIES, EXTENDED_UNLOCKS  # research data
from energies import all_energies                              # 50 energy types
from backend.hex_utils import resolve_hex_collisions, galaxy_coords_to_hex, _find_free_hex, HexCoord
from backend.colony import ColonyManager                       # colony system
from backend.colony_systems import (                            # governing system logic
    get_available_systems,
    calculate_faction_affinity,
    SYSTEM_CHANGE_COOLDOWN,
)

# Load the faction preferred-system configuration from lore/faction_systems.json.
# This maps faction names to their preferred social/economic/political systems so
# the player's colony choices can passively influence diplomatic standing.
import json as _json
_FACTION_SYSTEMS_PATH = os.path.join(PROJECT_ROOT, "lore", "faction_systems.json")
try:
    with open(_FACTION_SYSTEMS_PATH, encoding="utf-8") as _fsf:
        _raw_faction_systems = _json.load(_fsf)
    # Strip the internal comment key if present
    FACTION_SYSTEM_PREFS: dict = {k: v for k, v in _raw_faction_systems.items() if not k.startswith("_")}
except (FileNotFoundError, _json.JSONDecodeError):
    FACTION_SYSTEM_PREFS: dict = {}
from backend.deep_space import DeepSpaceManager                # deep space objects
from backend.gnn import generate_gnn_summary                   # end-of-turn broadcast

# ---------------------------------------------------------------------------
# Singleton instances — one pair per server process, replaced on new game
# ---------------------------------------------------------------------------
game: Optional[Game] = None
colony_manager: Optional[ColonyManager] = None
deep_space_manager: Optional[DeepSpaceManager] = None

# ---------------------------------------------------------------------------
# Scan / discovery tracking
# ---------------------------------------------------------------------------
# Set of system names the player has ever had in scan range.  Persists for
# the session; seeded from visited systems on first use so save-loads work.
_discovered_systems: set[str] = set()
_discovery_seeded: bool = False

# Base scan range in 3D galaxy units (galaxy is 500×500×200).
# Will scale with scanner component tech in future.
_BASE_SCAN_RANGE: float = 40.0

# Sensor component → scan range bonus (additive, in galaxy units)
_SENSOR_RANGE: dict[str, float] = {
    "Oracle Crown Array":       0.0,   # starter — base range only
    "Meridian Pulse Scanner":  10.0,
    "Helios Resonance Array":  20.0,
    "Void Lens Array":         35.0,
    "Quantum Echo Suite":      55.0,
}


def _effective_scan_range() -> float:
    """Return the ship's effective scan range in galaxy units."""
    try:
        sensors = game.navigation.current_ship.components.get("sensors", [])
        bonus = max((_SENSOR_RANGE.get(s, 0.0) for s in sensors), default=0.0)
        return _BASE_SCAN_RANGE + bonus
    except Exception:
        return _BASE_SCAN_RANGE


def _seed_discovery() -> None:
    """Pre-populate _discovered_systems from visited systems (called once after load)."""
    global _discovery_seeded
    if _discovery_seeded or not game or not game.character_created:
        return
    try:
        for data in game.navigation.galaxy.systems.values():
            if data.get("visited", False):
                _discovered_systems.add(data.get("name", ""))
        _discovery_seeded = True
    except Exception:
        pass



def _colony_research_output() -> int:
    """Extract current research RP from all colonies (backend glue — passed to game method)."""
    if not (colony_manager and colony_manager.colonies):
        return 0
    try:
        return int(colony_manager.calculate_all_production().get("research", 0))
    except Exception:
        return 0


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan hook.
    Creates the initial (empty) Game instance at startup so the /api/game/state
    endpoint can safely report "not initialized" before the player starts a game.
    """
    global game, colony_manager, deep_space_manager
    game = Game()
    colony_manager = ColonyManager(game)
    deep_space_manager = DeepSpaceManager()
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
    profession: str = ""          # optional: chosen profession from PROFESSIONS
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
         Fleet_Strength + Defense_Grid + Strategic_Weapons + Intelligence_Capability + Faction_Bonus
         Starts near zero; grows only through fleet production, colony defense, and research.
         Faction bonus applies when allied faction has Industry/Technology focus and rep > 10.
    REI  Resource Extraction Index
         Raw_Material_Access + Energy_Production + Logistics_Capacity
         + Extraction_Aptitude + Prospecting_Advantage + Profession_Bonus + Faction_Bonus
         Profession bonus: 20 extraction/logistics professions apply per-component multipliers
           scaled by profession level (level 1 = 10%, level 10 = 100% of stated multiplier).
           Add future extraction modifiers (upgrades, events, policies) to _REI_PROFESSION_BONUSES.
    KII  Knowledge & Innovation Index
         Research_Output + Education_Level + AI_Capability + Innovation_Rate
         + Cognitive_Aptitude + Knowledge_Network + Profession_Bonus + Faction_Bonus
         Profession bonus: 25 research/education/AI professions apply per-component multipliers
           scaled by profession level.  Technology/Science factions add rep-gated bonus.
         Add future KII modifiers to _KII_PROFESSION_BONUSES.
    ECI  Economic Capability Index
         Industrial_Output + Trade_Volume + Energy_Output + Financial_Liquidity
         + Commercial_Acumen + Infrastructure_Depth + Profession_Bonus + Faction_Bonus
         Profession bonus: 20 trade/industrial/logistics professions apply per-component
           multipliers scaled by profession level.
         Trade / Commerce / Industry factions add rep-gated bonus.
         Add future ECI modifiers to _ECI_PROFESSION_BONUSES.
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
    # Fleet Strength: backed entirely by the production chain (fleet_pool).
    # Starts at 0 and grows only via Shipyards — no free points from stats.
    fleet_strength = fleet_pool

    # Defense Grid: actual built infrastructure.  Zero until colonies exist.
    defense_grid = defense_pts * 25 + empire_size * 20

    # Combat Doctrine: reflects learned military techniques (completed research)
    # and the commander's kinetic aptitude (KIN).  No weapon hardware implied.
    combat_doctrine = n_completed * 4 + kin // 20

    # Intelligence Capability: passive cognitive advantage; deliberately small
    # so that raw stats never dominate the index at game start.
    intelligence_capability = int_ // 20 + coh // 20

    # Faction Bonus: allied factions with military-adjacent focus provide a
    # reputational boost to SPI.  Rep starts at +25 (from faction allegiance),
    # so Industry / Technology players get a small head-start.
    #   rep >  10 → small bonus   (+4)
    #   rep >  50 → medium bonus  (+12)
    #   rep >  75 → large bonus   (+25)
    _SPI_FACTION_FOCUSES = {"Industry", "Technology"}
    _allied_faction       = getattr(game, "character_faction", "") or ""
    _faction_focus        = factions.get(_allied_faction, {}).get("primary_focus", "")
    _faction_rep          = 0
    try:
        _faction_rep = game.faction_system.player_relations.get(_allied_faction, 0)
    except Exception:
        pass
    if _faction_focus in _SPI_FACTION_FOCUSES:
        if _faction_rep > 75:
            faction_bonus_spi = 25
        elif _faction_rep > 50:
            faction_bonus_spi = 12
        elif _faction_rep > 10:
            faction_bonus_spi = 4
        else:
            faction_bonus_spi = 0
    else:
        faction_bonus_spi = 0

    spi = fleet_strength + defense_grid + combat_doctrine + intelligence_capability + faction_bonus_spi

    # ── REI ──────────────────────────────────────────────────────────────────
    # Professions that directly boost REI sub-components.
    # Keys: sub-component names used in the formula below.
    # Values are fractional multipliers applied to each sub-component total;
    # the final bonus is further scaled by profession_level / 10 so that
    # a level-1 player gets 10% of the stated value and a level-10 master
    # gets the full 100%.  Add new professions or adjust weights here only —
    # no other code changes are needed to pick them up.
    _REI_PROFESSION_BONUSES: dict[str, dict[str, float]] = {
        # ── Directly extractive ─────────────────────────────────────────────
        "Resource Vein Prospector":              {"raw": 0.20, "energy": 0.05, "prospecting": 0.15},
        "Atmospheric Harvest Technician":        {"energy": 0.25},
        "Etheric Materials Synthesist":          {"energy": 0.15, "raw": 0.05},
        "Salvage Systems Diver":                 {"raw": 0.10},
        "Nano-Fabrication Artisan":              {"raw": 0.10},
        "Bio-Integrated Manufacturing Director": {"raw": 0.15},
        "Terraforming Ecologist":                {"raw": 0.05, "energy": 0.05},
        "Planetary Renewal Engineer":            {"raw": 0.05},
        # ── Exploration and surveying ────────────────────────────────────────
        "Void Cartographer":                     {"logistics": 0.15, "prospecting": 0.10},
        "Deep Space Reconnaissance Operative":   {"logistics": 0.10, "prospecting": 0.15},
        "Chrono-Synthetic Flux Analyst":          {"prospecting": 0.10},
        # ── Logistics and infrastructure ────────────────────────────────────
        "Ether Drive Tuner":                     {"energy": 0.10, "logistics": 0.10},
        "Gravitic Systems Engineer":             {"logistics": 0.15},
        "Wormline Infrastructure Engineer":      {"logistics": 0.20},
        "Orbital Dockmaster":                    {"logistics": 0.15},
        "Interstellar Quartermaster":            {"logistics": 0.20},
        "Habitat Systems Warden":                {"logistics": 0.10},
    }

    # Base colony-production chain
    # refined_ore represents processed industrial capacity upstream of the chain.
    raw_material_access = minerals * 8 + refined_ore * 6 + visited * 2
    energy_production   = ether * 10 + aef // 5
    logistics_capacity  = ships * 12 + visited * 3

    # Stat-driven contributions
    # KIN — physical precision in drilling, recovery, and field operations
    # SYN — ability to integrate heterogeneous extraction technologies
    # COH — sustained focus across distributed long-range mining sites
    extraction_aptitude = kin // 8 + syn // 10 + coh // 12

    # Prospecting advantage
    # AEF amplifies etheric deposit sensing; breadth of exploration multiplies discovery chance
    prospecting_advantage = aef // 6 + visited

    # Profession bonus: multiply base sub-components by stated weights, scaled by level
    _prof_name   = getattr(game, "character_profession", "") or ""
    _prof_system = getattr(game, "profession_system", None)
    _prof_level  = _prof_system.profession_levels.get(_prof_name, 1) if _prof_system else 1
    _prof_scale  = _prof_level / 10.0   # level 1 → 0.10,  level 10 → 1.0
    _prof_mults  = _REI_PROFESSION_BONUSES.get(_prof_name, {})

    profession_bonus_rei = int(
        raw_material_access   * _prof_mults.get("raw",         0) * _prof_scale
        + energy_production   * _prof_mults.get("energy",      0) * _prof_scale
        + logistics_capacity  * _prof_mults.get("logistics",   0) * _prof_scale
        + prospecting_advantage * _prof_mults.get("prospecting", 0) * _prof_scale
    )

    # Faction bonus: Industry / Exploration factions provide better extraction networks
    # (same rep-gating pattern as SPI faction bonus)
    _REI_FACTION_FOCUSES = {"Industry", "Exploration"}
    if _faction_focus in _REI_FACTION_FOCUSES:
        if _faction_rep > 75:
            faction_bonus_rei = 30
        elif _faction_rep > 50:
            faction_bonus_rei = 15
        elif _faction_rep > 10:
            faction_bonus_rei = 5
        else:
            faction_bonus_rei = 0
    else:
        faction_bonus_rei = 0

    rei = (
        raw_material_access
        + energy_production
        + logistics_capacity
        + extraction_aptitude
        + prospecting_advantage
        + profession_bonus_rei
        + faction_bonus_rei
    )

    # ── KII ──────────────────────────────────────────────────────────────────
    # Professions that directly boost KII sub-components.
    # Same scaling rule as REI: multiplier × (profession_level / 10).
    # Add new professions or adjust weights here only.
    _KII_PROFESSION_BONUSES: dict[str, dict[str, float]] = {
        # ── Research and analysis ────────────────────────────────────────────
        "Astrobiologist":                       {"research": 0.15, "innovation": 0.05},
        "Quantum Computer Scientist":           {"research": 0.20, "ai": 0.15},
        "Ancient Systems Decipherer":           {"research": 0.15, "education": 0.10},
        "Etheric Historian":                    {"education": 0.15, "research": 0.05},
        "Memory Forensics Analyst":             {"research": 0.10, "education": 0.10},
        "Chrono-Synthetic Flux Analyst":        {"research": 0.10, "innovation": 0.10},
        "Myth-Systems Scholar":                 {"education": 0.10},
        "Cultural Pattern Archivist":           {"education": 0.10},
        "Relic Recovery Specialist":            {"research": 0.10},
        # ── Consciousness, AI, and cognition ────────────────────────────────
        "Consciousness Engineer":               {"ai": 0.20, "innovation": 0.10},
        "AI-Ether Integration Specialist":      {"ai": 0.25},
        "Cognitive Archive Curator":            {"education": 0.15, "ai": 0.10},
        "Quantum Consciousness Transfer Technician": {"ai": 0.10},
        "Collective Consciousness Integrator":  {"ai": 0.15, "innovation": 0.10},
        "Consciousness Confluence Architect":   {"ai": 0.20, "research": 0.10},
        "Shared Mind Systems Steward":          {"ai": 0.10, "education": 0.10},
        # ── Education and mentorship ─────────────────────────────────────────
        "Adaptive Education Designer":          {"education": 0.20},
        "Knowledge Systems Mentor":             {"education": 0.20, "innovation": 0.05},
        "Cognitive Apprenticeship Instructor":  {"education": 0.15},
        "Inter-Species Education Facilitator":  {"education": 0.15},
        "Foundational Learning Guide":          {"education": 0.10},
        # ── Exploration feeding discovery ────────────────────────────────────
        "Quantum Navigator":                    {"innovation": 0.10, "ai": 0.05},
        "Void Cartographer":                    {"research": 0.05, "innovation": 0.05},
        "Deep Space Reconnaissance Operative":  {"research": 0.05},
    }

    # Base production-chain components (existing formulas unchanged)
    research_output = research_pts * 8 + int_ // 4
    education_level = n_completed * 6 + int_ // 3
    ai_capability   = syn // 3 + aef // 6
    innovation_rate = syn // 5 + coh // 8

    # Cognitive aptitude: raw intellectual and perceptual capacity
    # INT — analytical processing; COH — sustained mental coherence across long research arcs;
    # AEF — etheric pattern recognition that amplifies discovery in anomalous phenomena.
    # Deliberately kept smaller than per-component stat terms so it adds flavour,
    # not dominance, at game start.
    cognitive_aptitude = int_ // 6 + coh // 8 + aef // 8

    # Knowledge network: breadth of completed research and explored space reinforces itself —
    # the more you know and have seen, the faster new connections form.
    knowledge_network = n_completed * 3 + visited // 2

    # Profession bonus: apply per-component multipliers scaled by profession level
    _kii_prof_mults = _KII_PROFESSION_BONUSES.get(_prof_name, {})

    profession_bonus_kii = int(
        research_output     * _kii_prof_mults.get("research",   0) * _prof_scale
        + education_level   * _kii_prof_mults.get("education",  0) * _prof_scale
        + ai_capability     * _kii_prof_mults.get("ai",         0) * _prof_scale
        + innovation_rate   * _kii_prof_mults.get("innovation", 0) * _prof_scale
    )

    # Faction bonus: Technology / Science factions provide access to research networks,
    # knowledge archives, and collaborative discovery infrastructure.
    _KII_FACTION_FOCUSES = {"Technology", "Science"}
    if _faction_focus in _KII_FACTION_FOCUSES:
        if _faction_rep > 75:
            faction_bonus_kii = 30
        elif _faction_rep > 50:
            faction_bonus_kii = 15
        elif _faction_rep > 10:
            faction_bonus_kii = 5
        else:
            faction_bonus_kii = 0
    else:
        faction_bonus_kii = 0

    kii = (
        research_output
        + education_level
        + ai_capability
        + innovation_rate
        + cognitive_aptitude
        + knowledge_network
        + profession_bonus_kii
        + faction_bonus_kii
    )

    # ── ECI ──────────────────────────────────────────────────────────────────
    # Professions that directly boost ECI sub-components.
    # Same scaling rule as REI/KII: multiplier × (profession_level / 10).
    # Add new professions or adjust weights here only.
    _ECI_PROFESSION_BONUSES: dict[str, dict[str, float]] = {
        # ── Trade, commerce, and brokerage ──────────────────────────────────
        "Exotic Commodities Broker":            {"trade": 0.25, "liquidity": 0.10},
        "Trade Route Adjudicator":              {"trade": 0.20},
        "Interstellar Diplomatic Attaché":      {"trade": 0.10, "liquidity": 0.05},
        "Faction Liaison Officer":              {"trade": 0.10},
        "Universal Translation Mediator":       {"trade": 0.10},
        # ── Industrial production ────────────────────────────────────────────
        "Bio-Integrated Manufacturing Director":{"industrial": 0.20},
        "Nano-Fabrication Artisan":             {"industrial": 0.15},
        "Closed-Loop Sustainability Planner":   {"industrial": 0.15, "energy": 0.05},
        "Terraforming Ecologist":               {"industrial": 0.10},
        "Planetary Renewal Engineer":           {"industrial": 0.10},
        "Programmable Matter Architect":        {"industrial": 0.15, "energy": 0.05},
        "Nano-Swarm Systems Engineer":          {"industrial": 0.10},
        "Programmable Matter Fabrication Technician": {"industrial": 0.10},
        # ── Energy and resource conversion ───────────────────────────────────
        "Atmospheric Harvest Technician":       {"energy": 0.20},
        "Etheric Materials Synthesist":         {"energy": 0.15},
        "Gravitic Systems Engineer":            {"energy": 0.10},
        "Ether Drive Tuner":                    {"energy": 0.10},
        # ── Logistics, supply, and operations ───────────────────────────────
        "Interstellar Quartermaster":           {"industrial": 0.10, "trade": 0.10},
        "Orbital Dockmaster":                   {"trade": 0.15},
        "Habitat Systems Warden":               {"industrial": 0.05, "liquidity": 0.05},
        "Wormline Infrastructure Engineer":     {"trade": 0.10},
    }

    # Base colony-production chain (existing formulas unchanged)
    industrial_output   = minerals * 4 + food * 3
    trade_volume        = credits_prod * 10 + credits // 5000
    energy_output       = ether * 6 + aef // 5
    financial_liquidity = min(500, credits // 2000)

    # Commercial acumen: stat-driven capacity for negotiation, resource valuation,
    # and optimizing transactions.
    # INT — analytical pricing and contract evaluation
    # SYN — integrating diverse market systems and alien economic frameworks
    # COH — maintaining reliable long-term trade relationships
    commercial_acumen = int_ // 8 + syn // 10 + coh // 12

    # Infrastructure depth: how well-developed the empire's physical and
    # logistical foundations are — colony count amplifies per-turn output,
    # ship network enables trade reach, and refined ore signals upstream
    # industrial maturity.
    infrastructure_depth = empire_size * 4 + ships * 3 + refined_ore * 2

    # Profession bonus: apply per-component multipliers scaled by profession level
    _eci_prof_mults = _ECI_PROFESSION_BONUSES.get(_prof_name, {})

    profession_bonus_eci = int(
        industrial_output   * _eci_prof_mults.get("industrial", 0) * _prof_scale
        + trade_volume      * _eci_prof_mults.get("trade",      0) * _prof_scale
        + energy_output     * _eci_prof_mults.get("energy",     0) * _prof_scale
        + financial_liquidity * _eci_prof_mults.get("liquidity", 0) * _prof_scale
    )

    # Faction bonus: Trade / Commerce factions open access to preferred
    # shipping lanes, tariff exemptions, and market intelligence.
    _ECI_FACTION_FOCUSES = {"Trade", "Commerce", "Industry"}
    if _faction_focus in _ECI_FACTION_FOCUSES:
        if _faction_rep > 75:
            faction_bonus_eci = 30
        elif _faction_rep > 50:
            faction_bonus_eci = 15
        elif _faction_rep > 10:
            faction_bonus_eci = 5
        else:
            faction_bonus_eci = 0
    else:
        faction_bonus_eci = 0

    eci = (
        industrial_output
        + trade_volume
        + energy_output
        + financial_liquidity
        + commercial_acumen
        + infrastructure_depth
        + profession_bonus_eci
        + faction_bonus_eci
    )

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
                "Combat Doctrine":         combat_doctrine,
                "Intelligence Capability": intelligence_capability,
                "Faction Bonus":           faction_bonus_spi,
            },
            "rei": {
                "Raw Material Access":    raw_material_access,
                "Energy Production":      energy_production,
                "Logistics Capacity":     logistics_capacity,
                "Extraction Aptitude":    extraction_aptitude,
                "Prospecting Advantage":  prospecting_advantage,
                "Profession Bonus":       profession_bonus_rei,
                "Faction Bonus":          faction_bonus_rei,
            },
            "kii": {
                "Research Output":    research_output,
                "Education Level":    education_level,
                "AI Capability":      ai_capability,
                "Innovation Rate":    innovation_rate,
                "Cognitive Aptitude": cognitive_aptitude,
                "Knowledge Network":  knowledge_network,
                "Profession Bonus":   profession_bonus_kii,
                "Faction Bonus":      faction_bonus_kii,
            },
            "eci": {
                "Industrial Output":    industrial_output,
                "Trade Volume":         trade_volume,
                "Energy Output":        energy_output,
                "Financial Liquidity":  financial_liquidity,
                "Commercial Acumen":    commercial_acumen,
                "Infrastructure Depth": infrastructure_depth,
                "Profession Bonus":     profession_bonus_eci,
                "Faction Bonus":        faction_bonus_eci,
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
            "Colonies founded":         empire_size,
            "Systems visited":          visited,
            "Credits":                  credits,
            "Fleet pool":               fleet_pool,
            "Allied faction":           _allied_faction or "None",
            "Faction focus":            _faction_focus  or "None",
            "Faction reputation":       _faction_rep,
            # Profession inputs (same values, displayed under whichever index is clicked)
            "REI Profession":           _prof_name or "None",
            "REI Profession level":     _prof_level,
            "REI Profession scale":     f"{int(_prof_scale * 100)}%",
            "KII Profession":           _prof_name or "None",
            "KII Profession level":     _prof_level,
            "KII Profession scale":     f"{int(_prof_scale * 100)}%",
            "ECI Profession":           _prof_name or "None",
            "ECI Profession level":     _prof_level,
            "ECI Profession scale":     f"{int(_prof_scale * 100)}%",
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
            "profession": getattr(game, "character_profession", ""),
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
# Helper — deep space object initialisation
# Called from both /api/game/new and /api/game/load.
# ===========================================================================

def _init_deep_space(g) -> None:
    """
    (Re-)generate deep space objects for the current galaxy.

    Uses the galaxy object count as a seed offset so the DSO layout is
    deterministic for a given galaxy while being independent of the default seed.
    Objects are placed only on empty hexes (no star system).
    """
    global deep_space_manager

    try:
        galaxy = g.navigation.galaxy
        # Build the set of hexes that already have star systems
        system_hex_set = set()
        for _sys in galaxy.systems.values():
            hq = _sys.get("hex_q")
            hr = _sys.get("hex_r")
            if hq is not None and hr is not None:
                system_hex_set.add((hq, hr))
            else:
                # Fall back to projection if hex coords not yet assigned
                from backend.hex_utils import galaxy_coords_to_hex
                coords = _sys.get("coordinates", (0, 0, 0))
                h = galaxy_coords_to_hex(coords[0], coords[1])
                system_hex_set.add((h.q, h.r))

        # Use len(galaxy.systems) as a stable, per-galaxy seed offset
        seed = 1000 + len(galaxy.systems)
        deep_space_manager = DeepSpaceManager(galaxy_seed=seed)
        deep_space_manager.generate(system_hex_set)
    except Exception as _e:
        print(f"[4X] Warning: deep_space_manager init failed: {_e}")
        deep_space_manager = DeepSpaceManager()


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
    global game, colony_manager, deep_space_manager, _discovered_systems, _discovery_seeded
    # Always start with a clean slate
    game = Game()
    colony_manager = ColonyManager(game)
    _discovered_systems = set()
    _discovery_seeded = False

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

    # Give the starter ship a generous fuel load so new players can explore freely.
    ship = game.navigation.current_ship
    if ship:
        ship.max_fuel = max(ship.max_fuel, 500)
        ship.fuel     = ship.max_fuel

    # Initialise NPC infrastructure — bots and stations are generated fresh each game.
    _init_bot_manager(game)
    _init_station_manager(game)
    _init_deep_space(game)

    # If the player chose a faction, start them at Allied standing with that faction.
    # All other factions are initialised to neutral by FactionSystem.initialize_factions().
    # Future quest / trade / mission hooks should call faction_system.modify_reputation()
    # to nudge this value rather than setting it directly.
    if request.faction and request.faction in game.faction_system.player_relations:
        game.faction_system.set_player_home_faction(request.faction, reputation=80)

    # Initialise profession system and assign the chosen profession (if any).
    # game.profession_system is used by ProfessionSystem throughout the session.
    game.profession_system = ProfessionSystem()
    if request.profession and request.profession in PROFESSIONS:
        game.profession_system.assign_profession(request.profession)
        game.character_profession = request.profession
    else:
        game.character_profession = ""

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

    success, end_message = game.end_turn()   # increments current_turn, resets actions
    events = game.advance_turn()             # runs subsystem tick; does NOT increment turn

    # Inject extra research progress so total increment equals RP/turn.
    # The engine already added +1 inside advance_turn(); we add (rp - 1) more.
    if game.active_research:
        _rp = game.calculate_rp_per_turn(colony_rp=_colony_research_output())["total"]
        game.research_progress += max(0, _rp - 1)
        _rt = all_research.get(game.active_research, {}).get("research_time", 1)
        if game.research_progress >= _rt:
            game.complete_research()

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

    # Inject colony and deep-space state so save_game.py persists them via game.*_state.
    game.colony_state = colony_manager.serialize()
    game.deep_space_state = deep_space_manager.serialize() if deep_space_manager else {}

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

    # Restore deep space state, or regenerate fresh if missing from old saves.
    _ds_saved = getattr(game, "deep_space_state", {})
    if _ds_saved:
        deep_space_manager.deserialize(_ds_saved)
    else:
        _init_deep_space(game)

    # Re-apply the full bonus stack (research/faction/character) on top of the
    # component profile that save_game restores via calculate_stats_from_components().
    _loaded_ship = getattr(game.navigation, "current_ship", None) if game.navigation else None
    if _loaded_ship:
        apply_all_bonuses_to_ship(_loaded_ship, game)

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

    # Build profession list grouped by category for the UI.
    # Each entry carries enough data for the selection card.
    professions_list = [
        {
            "name":                  name,
            "category":              data["category"],
            "description":           data["description"],
            "skills":                data.get("skills", []),
            "base_benefits":         data.get("base_benefits", []),
            "intermediate_benefits": data.get("intermediate_benefits", []),
            "advanced_benefits":     data.get("advanced_benefits", []),
            "master_benefits":       data.get("master_benefits", []),
        }
        for name, data in PROFESSIONS.items()
    ]

    return {
        "classes": classes_list,
        "backgrounds": backgrounds_list,
        "species": species_list,
        "factions": factions_list,
        "professions": professions_list,
        "profession_categories": PROFESSION_CATEGORIES_ORDERED,
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

    # Seed discovery set from visited systems on first call after a load
    _seed_discovery()

    galaxy      = game.navigation.galaxy
    ship_coords = _ship_coords()   # (sx, sy, sz) or None
    scan_range  = _effective_scan_range()
    raw_systems = []

    for coords, data in galaxy.systems.items():
        x, y, z = coords
        name = data.get("name", "Unknown")

        # Compute distance from player's ship to this system
        if ship_coords:
            sx, sy, sz = ship_coords
            dist = math.sqrt((x - sx) ** 2 + (y - sy) ** 2 + (z - sz) ** 2)
        else:
            dist = float("inf")

        in_range = dist <= scan_range

        if in_range:
            # Currently in scanner range — full data, mark as discovered
            _discovered_systems.add(name)
            raw_systems.append({
                "name":                name,
                "x": x, "y": y, "z": z,
                "type":                data.get("type", "Unknown"),
                "population":          data.get("population", 0),
                "threat_level":        data.get("threat_level", 0),
                "resources":           data.get("resources", "Unknown"),
                "description":         data.get("description", ""),
                "controlling_faction": data.get("controlling_faction"),
                "visited":             data.get("visited", False),
                "in_scan_range":       True,
                "planet_count": len([
                    b for b in data.get("celestial_bodies", [])
                    if b.get("object_type") == "Planet"
                ]),
            })
        elif name in _discovered_systems:
            # Previously scanned — partial data only (no live intel)
            raw_systems.append({
                "name":                name,
                "x": x, "y": y, "z": z,
                "type":                data.get("type", "Unknown"),
                "population":          None,
                "threat_level":        None,
                "resources":           None,
                "description":         None,
                "controlling_faction": None,
                "visited":             data.get("visited", False),
                "in_scan_range":       False,
                "planet_count":        None,
            })
        # else: never scanned — omit entirely (true fog of war)

    # Project 3D→2D and resolve hex collisions
    projected = resolve_hex_collisions(raw_systems)

    # Mark systems that have at least one player colony so the renderer can
    # draw territory overlays without a separate API call.
    colonized_systems = {
        c["system_name"] for c in colony_manager.list_colonies()
    }
    for sys in projected:
        sys["has_player_colony"] = sys["name"] in colonized_systems

    # Include deep-space stations within scan range only
    deep_space_stations = []
    station_mgr = getattr(game, "station_manager", None)
    if station_mgr:
        for st in station_mgr.get_deep_space_stations():
            sc = st.get("coordinates")
            if sc and ship_coords:
                sx, sy, sz = ship_coords
                dist = math.sqrt((sc[0]-sx)**2 + (sc[1]-sy)**2 + (sc[2]-sz)**2)
                if dist > scan_range:
                    continue
            deep_space_stations.append({
                "name":        st["name"],
                "type":        st["type"],
                "hex_q":       st["hex_q"],
                "hex_r":       st["hex_r"],
                "coordinates": list(sc),
                "services":    st.get("services", []),
                "description": st.get("description", ""),
            })

    # Include deep space objects using the same scan-range fog-of-war as systems:
    #   - within current scan range → auto-discover and include
    #   - previously discovered      → include
    #   - never seen                 → omit entirely
    dso_list = []
    if deep_space_manager:
        for dso in deep_space_manager.list_all():
            if ship_coords:
                sx, sy, sz = ship_coords
                dso_dist = math.sqrt((dso.x - sx) ** 2 + (dso.y - sy) ** 2 + (dso.z - sz) ** 2)
                if dso_dist <= scan_range and not dso.discovered:
                    deep_space_manager.discover(dso.hex_q, dso.hex_r)
            if dso.discovered:
                dso_list.append(dso.to_dict())

    return {"systems": projected, "stations": deep_space_stations, "deep_space_objects": dso_list}


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


# ===========================================================================
# Ship bonus helper — applies research/faction/character bonuses to the ship
# ===========================================================================

def _get_player_faction(g) -> Optional[str]:
    """Return the player's faction name from whichever attribute is populated."""
    faction = getattr(g, "player_faction", None)
    if not faction and getattr(g, "character", None):
        faction = g.character.get("faction")
    return faction


def _colony_system_affinity_for_faction(faction_name: str) -> int:
    """
    Compute the average system affinity score for a faction across all player
    colonies.  Returns an integer in [-15, +15].

    If the player has no colonies yet, returns 0 (neutral).
    If the faction has no entry in FACTION_SYSTEM_PREFS, returns 0.
    """
    if not colony_manager or not colony_manager.colonies:
        return 0
    prefs = FACTION_SYSTEM_PREFS.get(faction_name)
    if not prefs:
        return 0

    scores = [
        calculate_faction_affinity(
            colony.social_system,
            colony.economic_system,
            colony.political_system,
            prefs,
        )
        for colony in colony_manager.colonies.values()
    ]
    return round(sum(scores) / len(scores))


def apply_all_bonuses_to_ship(ship, g) -> None:
    """
    Layer research, faction, and character-stat bonuses on top of the
    component-derived attribute profile already stored in
    ``ship.attribute_profile``, then re-derive the legacy engine properties
    (max_cargo, max_fuel, jump_range, scan_range) so real gameplay reflects
    the full bonus stack.

    Call this immediately after any ``ship.calculate_stats_from_components()``
    invocation so the two steps always stay in sync.
    """
    profile = dict(getattr(ship, "attribute_profile", None) or {})
    if not profile:
        # No component profile yet — nothing to augment.
        return

    from ship_bonus_rules import (
        calculate_research_bonuses,
        calculate_faction_bonuses,
        calculate_character_stat_bonuses,
    )

    completed_research: list = getattr(g, "completed_research", None) or []
    faction_name: Optional[str] = _get_player_faction(g)
    char_stats: dict = getattr(g, "character_stats", None) or {}

    for bonus_dict in (
        calculate_research_bonuses(completed_research),
        calculate_faction_bonuses(faction_name),
        calculate_character_stat_bonuses(char_stats),
    ):
        for attr_id, bonus in bonus_dict.items():
            if attr_id in profile:
                profile[attr_id] = max(0.0, min(100.0, profile[attr_id] + bonus))

    ship.attribute_profile = profile

    # Re-derive legacy engine properties using the same formulas as
    # navigation.Ship.calculate_stats_from_components() so the engine's
    # actual gameplay values stay in sync with the full bonus stack.
    hull_integrity     = profile.get("hull_integrity",              30.0)
    mass_efficiency    = profile.get("mass_efficiency",             30.0)
    energy_storage     = profile.get("energy_storage",              30.0)
    engine_efficiency  = profile.get("engine_efficiency",           30.0)
    engine_output      = profile.get("engine_output",               30.0)
    ftl_capacity       = profile.get("ftl_jump_capacity",           30.0)
    detection_range    = profile.get("detection_range",             30.0)
    etheric_sensitivity = profile.get("etheric_sensitivity",        20.0)

    ship.health    = max(100, int(hull_integrity * 10))
    ship.max_cargo = max(30,  int(mass_efficiency * 3 + hull_integrity))

    fuel_capacity  = max(80,  int(energy_storage * 3 + engine_efficiency * 2.5))
    ship.max_fuel  = fuel_capacity
    ship.fuel      = min(ship.fuel, ship.max_fuel)

    ship.jump_range = max(5,   int(ftl_capacity / 2 + engine_output / 6))
    ship.scan_range = max(5.0, detection_range / 3.0 + etheric_sensitivity / 6.0)


class JumpRequest(BaseModel):
    """Request body for jumping the player's ship."""
    target_x: float
    target_y: float
    target_z: float


@app.post("/api/ship/jump")
async def ship_jump(request: JumpRequest):
    """
    Jump the player's ship to the target galaxy coordinates.

    Costs one action point per jump in addition to fuel.  If the engine
    rejects the jump (out of range, insufficient fuel, etc.) the action
    point is refunded so the player is not penalised for invalid moves.
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    nav = game.navigation
    ship = nav.current_ship
    if not ship:
        raise HTTPException(status_code=400, detail="No active ship.")

    # Consume one action point before attempting the jump
    ok, reason = game.consume_action("move")
    if not ok:
        return {
            "success":               False,
            "message":               reason,
            "new_coords":            list(ship.coordinates),
            "fuel_remaining":        ship.fuel,
            "system_at_destination": None,
            "deep_space_object":     None,
        }

    target = (request.target_x, request.target_y, request.target_z)
    success, message = ship.jump_to(target, nav.galaxy, game)

    if not success:
        # Refund the action — the move never happened
        game.turn_actions_remaining = min(
            game.turn_actions_remaining + 1, game.max_actions_per_turn
        )
        return {
            "success":              False,
            "message":              message,
            "new_coords":           list(ship.coordinates),
            "fuel_remaining":       ship.fuel,
            "system_at_destination": None,
            "deep_space_object":    None,
        }

    # Determine if there is a star system at the destination
    dest_system = nav.galaxy.get_system_at(*target)

    # Check for a deep space object at the destination hex
    dest_hex = galaxy_coords_to_hex(request.target_x, request.target_y)
    dso = None
    if deep_space_manager:
        dso_obj = deep_space_manager.get_at_hex(dest_hex.q, dest_hex.r)
        if dso_obj:
            if not dso_obj.discovered:
                deep_space_manager.discover(dest_hex.q, dest_hex.r)
            dso = dso_obj.to_dict()

    return {
        "success":               True,
        "message":               message,
        "new_coords":            list(ship.coordinates),
        "fuel_remaining":        ship.fuel,
        "system_at_destination": dest_system,
        "deep_space_object":     dso,
    }


# ===========================================================================
# Deep space action endpoints
# ===========================================================================

@app.post("/api/deep_space/harvest")
async def deep_space_harvest():
    """
    Harvest the resource node or salvage the derelict at the ship's current hex.

    Adds loot to ship cargo and marks the object as depleted.
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")
    ship = game.navigation.current_ship
    if not ship:
        raise HTTPException(status_code=400, detail="No active ship.")
    if not deep_space_manager:
        raise HTTPException(status_code=503, detail="Deep space system not ready.")

    coords = ship.coordinates
    dest_hex = galaxy_coords_to_hex(coords[0], coords[1])
    try:
        loot = deep_space_manager.harvest(dest_hex.q, dest_hex.r)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Add loot to cargo
    credits_gained = loot.pop("credits", 0)
    game.credits = getattr(game, "credits", 0) + credits_gained
    cargo_added = {}
    for resource, amount in loot.items():
        current = ship.cargo.get(resource, 0)
        ship.cargo[resource] = current + amount
        cargo_added[resource] = amount

    return {
        "success":        True,
        "credits_gained": credits_gained,
        "cargo_added":    cargo_added,
        "credits":        game.credits,
        "cargo":          dict(ship.cargo),
    }


@app.post("/api/deep_space/found_outpost")
async def deep_space_found_outpost():
    """
    Stub endpoint for founding an outpost at the ship's current hex.
    Returns a placeholder response; full outpost building is a future feature.
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")
    ship = game.navigation.current_ship
    if not ship:
        raise HTTPException(status_code=400, detail="No active ship.")
    if not deep_space_manager:
        raise HTTPException(status_code=503, detail="Deep space system not ready.")

    coords = ship.coordinates
    dest_hex = galaxy_coords_to_hex(coords[0], coords[1])
    dso = deep_space_manager.get_at_hex(dest_hex.q, dest_hex.r)
    if not dso or dso.type != "outpost_site":
        raise HTTPException(status_code=400, detail="No outpost site at current location.")

    return {
        "success": False,
        "message": "Outpost construction is not yet available. Survey complete — location logged for future development.",
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
    from ship_bonus_rules import (
        calculate_research_bonuses,
        calculate_faction_bonuses,
        calculate_character_stat_bonuses,
    )

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

    # Layer research, faction, and character-stat bonuses
    completed_research: list = getattr(game, "completed_research", None) or []
    faction_name: Optional[str] = _get_player_faction(game)
    char_stats: dict = getattr(game, "character_stats", None) or {}

    for bonus_dict in (
        calculate_research_bonuses(completed_research),
        calculate_faction_bonuses(faction_name),
        calculate_character_stat_bonuses(char_stats),
    ):
        for attr_id, bonus in bonus_dict.items():
            if attr_id in profile:
                profile[attr_id] = max(0.0, min(100.0, profile[attr_id] + bonus))

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
    from ship_attributes import SHIP_ATTRIBUTE_DEFINITIONS

    # Build a quick id→display-name lookup from the attribute definitions
    _attr_names: dict[str, str] = {
        attr_id: defn.get("name", attr_id.replace("_", " ").title())
        for attr_id, defn in SHIP_ATTRIBUTE_DEFINITIONS.items()
    }

    def _key_stats(attributes: dict, top_n: int = 6) -> list[dict]:
        """
        Return the top_n non-zero attributes sorted by absolute value
        (descending).  Each entry is {"name": display_name, "value": float}.
        Skips zero values so the card only shows meaningful stats.
        """
        nonzero = [
            (k, v) for k, v in attributes.items() if v != 0.0
        ]
        nonzero.sort(key=lambda kv: abs(kv[1]), reverse=True)
        return [
            {"name": _attr_names.get(k, k.replace("_", " ").title()), "value": round(v, 1)}
            for k, v in nonzero[:top_n]
        ]

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
                    "name":           name,
                    "cost":           int(data.get("cost", 0)),
                    "faction_lock":   data.get("faction_lock"),
                    "failure_chance": round(float(data.get("failure_chance", 0)) * 100, 1),
                    "lore":           data.get("lore", ""),
                    # Top attributes by magnitude so the UI can show stat pills
                    "key_stats":      _key_stats(dict(data.get("attributes", {}))),
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

    # Recompute all derived stats then layer in bonus stack
    ship.calculate_stats_from_components()
    apply_all_bonuses_to_ship(ship, game)

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
    management screen.  Includes improvement breakdown, income split, and
    the full governing systems block (social / economic / political) with
    active modifiers, coherence score, and unique commodity output.
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    from backend.colony import POPULATION_INCOME_PER_10K
    from backend.colony_systems import (
        SOCIAL_SYSTEMS, ECONOMIC_SYSTEMS, POLITICAL_SYSTEMS,
        get_production_modifiers, calculate_coherence,
    )

    current_turn = getattr(game, "current_turn", 1)

    colonies_out = []
    for planet_name, colony in colony_manager.colonies.items():
        prod = colony_manager.calculate_colony_production(planet_name)

        # Count each improvement type across all tiles
        improvements: dict[str, int] = {}
        for tile in colony.tiles.values():
            if tile.improvement:
                improvements[tile.improvement] = improvements.get(tile.improvement, 0) + 1

        pop_income  = int(colony.population / 10_000 * POPULATION_INCOME_PER_10K)
        bldg_income = int(prod.get("credits", 0))
        total_income = pop_income + bldg_income

        # ── Governing systems block ──────────────────────────────────────────
        # Build compact summaries for each of the three system categories so
        # the colonies overview view can display them without a separate request.
        def _sys_info(sys_id: str, catalogue: dict) -> dict:
            defn = catalogue.get(sys_id, {})
            return {
                "id":          sys_id,
                "name":        defn.get("name", sys_id),
                "modifiers":   defn.get("modifiers", {}),
                "research_required": defn.get("research_required"),
            }

        coherence_score, coherence_label, coherence_mult = calculate_coherence(
            colony.social_system,
            colony.economic_system,
            colony.political_system,
        )
        mods = get_production_modifiers(
            colony.social_system,
            colony.economic_system,
            colony.political_system,
        )
        econ_def = ECONOMIC_SYSTEMS.get(colony.economic_system, {})

        # Cooldown turns remaining per category
        def _cd(last: int) -> int:
            return max(0, SYSTEM_CHANGE_COOLDOWN - (current_turn - last))

        systems_block = {
            "social":    {
                **_sys_info(colony.social_system, SOCIAL_SYSTEMS),
                "last_changed":    colony.social_last_changed,
                "cooldown_turns":  _cd(colony.social_last_changed),
            },
            "economic":  {
                **_sys_info(colony.economic_system, ECONOMIC_SYSTEMS),
                "last_changed":      colony.economic_last_changed,
                "cooldown_turns":    _cd(colony.economic_last_changed),
                "unique_commodity":  econ_def.get("unique_commodity"),
                "commodity_amount":  econ_def.get("commodity_amount", 0),
            },
            "political": {
                **_sys_info(colony.political_system, POLITICAL_SYSTEMS),
                "last_changed":    colony.political_last_changed,
                "cooldown_turns":  _cd(colony.political_last_changed),
            },
            # Combined modifier summary — what the three systems add up to
            "combined_modifiers":   mods,
            "coherence_score":      coherence_score,
            "coherence_label":      coherence_label,
            "coherence_multiplier": round(coherence_mult, 2),
        }

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
            "systems":          systems_block,
        })

    all_prod     = colony_manager.calculate_all_production()
    total_pop    = sum(c["population"] for c in colonies_out)
    total_income = sum(c["income"]     for c in colonies_out)

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


class SetColonySystemRequest(BaseModel):
    """Request body for changing one of a colony's governing systems."""
    category:  str   # "social" | "economic" | "political"
    system_id: str   # Must match a key in colony_systems.py


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
# Colony systems endpoints — social / economic / political configuration
# ===========================================================================

@app.get("/api/colony/{planet_name}/systems")
async def get_colony_systems(planet_name: str):
    """
    Return the current governing systems for a colony together with all
    available options (including lock state based on completed research) and
    the per-faction system affinity table.

    Used by the frontend Systems panel to build the selector UI without a
    separate round-trip.
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    colony = colony_manager.colonies.get(planet_name) if colony_manager else None
    if not colony:
        raise HTTPException(status_code=404, detail=f"Colony '{planet_name}' not found.")

    completed = getattr(game, "completed_research", []) or []
    current_turn = getattr(game, "current_turn", 1)

    # Available options per category with lock state
    options = {
        "social":    get_available_systems("social",    completed),
        "economic":  get_available_systems("economic",  completed),
        "political": get_available_systems("political", completed),
    }

    # Cooldown status per category — turns remaining until change is allowed
    def _cooldown(last_changed: int) -> int:
        elapsed = current_turn - last_changed
        return max(0, SYSTEM_CHANGE_COOLDOWN - elapsed)

    cooldown = {
        "social":    _cooldown(colony.social_last_changed),
        "economic":  _cooldown(colony.economic_last_changed),
        "political": _cooldown(colony.political_last_changed),
    }

    # Per-faction affinity for the current system configuration
    affinity_table = {}
    if game.faction_system:
        for faction_name in game.faction_system.player_relations:
            prefs = FACTION_SYSTEM_PREFS.get(faction_name)
            if prefs:
                affinity_table[faction_name] = calculate_faction_affinity(
                    colony.social_system,
                    colony.economic_system,
                    colony.political_system,
                    prefs,
                )

    # Coherence summary
    colony_dict = colony_manager.get_colony_dict(planet_name) or {}
    systems_block = colony_dict.get("systems", {})

    return {
        "planet_name":    planet_name,
        "current_systems": {
            "social":    colony.social_system,
            "economic":  colony.economic_system,
            "political": colony.political_system,
        },
        "coherence_score":      systems_block.get("coherence_score", 0),
        "coherence_label":      systems_block.get("coherence_label", "Stable"),
        "coherence_multiplier": systems_block.get("coherence_multiplier", 1.0),
        "cooldown":      cooldown,
        "options":       options,
        "affinity_table": affinity_table,
    }


@app.post("/api/colony/{planet_name}/systems")
async def set_colony_system(planet_name: str, request: SetColonySystemRequest):
    """
    Change one governing system for a colony.

    Validates:
      1. The system_id exists in the requested category.
      2. Any research prerequisite has been completed.
      3. The 5-turn cooldown since the last change to this category has elapsed.

    Always tells the player WHY a change is blocked — the error message includes
    the research requirement or the number of turns remaining on the cooldown.
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    colony = colony_manager.colonies.get(planet_name) if colony_manager else None
    if not colony:
        raise HTTPException(status_code=404, detail=f"Colony '{planet_name}' not found.")

    category  = request.category.lower()
    system_id = request.system_id
    completed = getattr(game, "completed_research", []) or []
    current_turn = getattr(game, "current_turn", 1)

    if category not in ("social", "economic", "political"):
        raise HTTPException(status_code=400, detail=f"Unknown category '{category}'.")

    # Validate the system ID and retrieve its definition
    options = get_available_systems(category, completed)
    option  = next((o for o in options if o["id"] == system_id), None)
    if not option:
        raise HTTPException(status_code=400, detail=f"Unknown system '{system_id}' for category '{category}'.")

    # Research gate
    if option["locked"]:
        raise HTTPException(
            status_code=400,
            detail=option["lock_reason"] or f"Research required to unlock '{system_id}'.",
        )

    # Cooldown check
    last_changed_attr = f"{category}_last_changed"
    last_changed = getattr(colony, last_changed_attr, 0)
    elapsed = current_turn - last_changed
    if last_changed > 0 and elapsed < SYSTEM_CHANGE_COOLDOWN:
        remaining = SYSTEM_CHANGE_COOLDOWN - elapsed
        raise HTTPException(
            status_code=400,
            detail=(
                f"System change on cooldown — {remaining} turn(s) remaining.  "
                f"Systems need {SYSTEM_CHANGE_COOLDOWN} turns to stabilise after a change."
            ),
        )

    # Apply the change
    setattr(colony, f"{category}_system",   system_id)
    setattr(colony, last_changed_attr,       current_turn)

    # Build updated affinity table
    affinity_table = {}
    if game.faction_system:
        for faction_name in game.faction_system.player_relations:
            prefs = FACTION_SYSTEM_PREFS.get(faction_name)
            if prefs:
                affinity_table[faction_name] = calculate_faction_affinity(
                    colony.social_system,
                    colony.economic_system,
                    colony.political_system,
                    prefs,
                )

    return {
        "success":         True,
        "message":         f"{option['name']} is now the {category} system for {planet_name}.",
        "colony":          colony_manager.get_colony_dict(planet_name),
        "affinity_table":  affinity_table,
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

    rp_data     = game.calculate_rp_per_turn(colony_rp=_colony_research_output())
    rp_per_turn = rp_data["total"]

    paths     = getattr(game, "character_research_paths", []) or []
    path_cats = {RESEARCH_PATH_CATEGORIES.get(p, p) for p in paths}

    nodes = []
    for name, data in all_research.items():
        completed  = name in game.completed_research
        active     = (name == game.active_research)
        available  = (name in available_names) and not completed
        rp_cost    = data.get("research_time", 0)
        progress   = game.research_progress if active else 0
        remaining  = max(0, rp_cost - progress)
        turns_est  = math.ceil(remaining / max(1, rp_per_turn)) if remaining > 0 else 0
        in_path    = data.get("category", "") in path_cats

        nodes.append({
            "name":             name,
            "category":         data.get("category", ""),
            "description":      data.get("description", ""),
            "difficulty":       data.get("difficulty", 5),
            "research_cost":    data.get("research_cost", 0),   # kept for save-compat; not shown
            "research_time":    rp_cost,
            "rp_cost":          rp_cost,
            "prerequisites":    data.get("prerequisites", []),
            "unlocks":          data.get("unlocks", []),
            "extended_unlocks": EXTENDED_UNLOCKS.get(name, {}),
            "related_energy":   data.get("related_energy", ""),
            "completed":        completed,
            "active":           active,
            "available":        available,
            "turns_to_complete": turns_est,
            "in_research_path": in_path,
        })

    return {
        "nodes":                nodes,
        "active_research":      game.active_research,
        "research_progress":    game.research_progress,
        "active_research_time": active_time,
        "completed_count":      len(game.completed_research),
        "rp_per_turn":          rp_per_turn,
        "rp_breakdown":         rp_data["breakdown"],
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

    rp_data = game.calculate_rp_per_turn(colony_rp=_colony_research_output())
    if not game.active_research:
        return {"active": None, "progress": 0, "total_time": 0, "percent": 0.0,
                "rp_per_turn": rp_data["total"], "turns_to_complete": 0}

    total      = all_research.get(game.active_research, {}).get("research_time", 1)
    percent    = round(min(100.0, game.research_progress / max(total, 1) * 100), 1)
    remaining  = max(0, total - game.research_progress)
    turns_est  = math.ceil(remaining / max(1, rp_data["total"]))

    return {
        "active":            game.active_research,
        "progress":          game.research_progress,
        "total_time":        total,
        "percent":           percent,
        "rp_per_turn":       rp_data["total"],
        "turns_to_complete": turns_est,
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

    # Bypass the engine's credit gate — research is now turn-based only.
    # Temporarily lend infinite credits so start_research_project() doesn't
    # reject the request for insufficient funds, then restore the balance.
    _saved_credits = game.credits
    game.credits   = 10_000_000_000
    success, message = game.start_research_project(request.research_name)
    game.credits   = _saved_credits   # always restore regardless of outcome

    if not success:
        raise HTTPException(status_code=400, detail=message)

    rp_data   = game.calculate_rp_per_turn(colony_rp=_colony_research_output())
    rp_cost   = all_research.get(game.active_research, {}).get("research_time", 1)
    turns_est = math.ceil(rp_cost / max(1, rp_data["total"]))

    return {
        "success":           True,
        "message":           message,
        "active_research":   game.active_research,
        "rp_per_turn":       rp_data["total"],
        "turns_to_complete": turns_est,
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

    # Attach system affinity scores — shows how compatible the player's colony
    # systems are with each faction's preferred configuration.
    for entry in result:
        entry["system_affinity"] = _colony_system_affinity_for_faction(entry["name"])

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

    # System affinity — how well the player's current colony configurations
    # align with this faction's preferred social/economic/political systems.
    prefs = FACTION_SYSTEM_PREFS.get(faction_name, {})
    system_affinity  = _colony_system_affinity_for_faction(faction_name)
    faction_sys_prefs = {
        "preferred_social":    prefs.get("preferred_social"),
        "preferred_economic":  prefs.get("preferred_economic"),
        "preferred_political": prefs.get("preferred_political"),
    }

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
        "system_affinity":       system_affinity,
        "faction_system_prefs":  faction_sys_prefs,
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

# ---------------------------------------------------------------------------
# Faction-aware market flavor text
# ---------------------------------------------------------------------------

# Templates keyed by faction primary_focus.  Each entry is a list of
# sentences; we pick by a hash of the system name so the same system always
# gets the same text (deterministic without storing state).
_MARKET_FLAVOR_BY_FOCUS: dict[str, list[str]] = {
    "Trade": [
        "Freight terminals hum with activity as Guild factors negotiate contracts across a dozen species. The exchange boards flicker with real-time commodity flows from a hundred star systems — prices here respond to the galaxy's pulse.",
        "Brokers from the Stellar Nexus Guild crowd every corridor, their comm-beads chattering with cargo manifests and futures contracts. Arbitrage is the local religion.",
        "A vast clearinghouse of interstellar commerce: bulk ore shares the docking ring with luxury silks, and a Guild adjudicator settles a dispute over rare-earth pricing in the next booth.",
    ],
    "Research": [
        "The market here is quiet and orderly — academics and archivists dominate the stalls, trading in data cores, experimental reagents, and survey maps as readily as raw ore. Commerce is viewed as a necessary discipline, not a passion.",
        "Prices are posted to four decimal places; the local factor once published a monograph on optimal bid-ask spreads. You get the sense that every transaction is logged for future analysis.",
        "Scientific equipment and exotic samples move alongside mundane cargo. A faction librarian cross-references your manifest before stamping the clearance — thoroughness first, throughput second.",
    ],
    "Technology": [
        "The market floor doubles as a showcase floor: prototype components sit under glass beside bulk listings, and the collective's neural-interface terminals let registered traders query inventory with a thought.",
        "Transactions here feel less like commerce and more like data exchange — the Collective tracks supply chains across the entire network, routing goods with machine precision.",
        "Every commodity is graded to exacting tolerances. A hive-mind logistics overseer flags any irregularity in the manifest before it reaches the exchange floor.",
    ],
    "Industry": [
        "The Gearwrights have turned commerce into craft: goods are inspected, stamped, and graded before they reach the floor. Inferior merchandise doesn't make it past the dock inspector.",
        "Smelling of machine oil and hot metal, the trading floor is a working space — deals struck amid the clatter of pneumatic loaders and the hiss of pressurised cargo locks.",
        "Every lot carries a Guild mark certifying provenance and quality. The local factor will remind you, unprompted, that authenticity has a price — and that knockoffs are confiscated.",
    ],
    "Cultural": [
        "Harmonic chimes mark each completed transaction, and the vendors wrap every purchase in botanical fibre rather than plasticene. Commerce here carries an almost ceremonial weight.",
        "The Consortium's factors insist on face-to-face negotiation; the automated exchange terminals stand dark by local regulation. Relationships, they say, are the only true currency.",
        "Aromatic diffusers mist the trading hall with calming frequencies. Prices are fair and unhurried — the Consortium discourages panic-buying as energetically as it discourages panic.",
    ],
    "Mysticism": [
        "Trade here observes the tidal cycles of the local biosphere; the Enclave opens the exchange only when the ecosystem indicators are favourable. Patience is the cost of doing business.",
        "Every commodity listing includes an ecological-impact assessment. Sellers of synthetic goods pay a restoration tithe; sellers of naturally-sourced materials receive a small premium.",
        "The market is open-air, roofed only by bioluminescent canopy. The factors are unhurried, and the prices reflect that — nothing is rushed, nothing discounted in haste.",
    ],
    "Military": [
        "This is a supply depot first and a market second. Bulk contracts for fuel cells, rations, and armour plating are posted on the tactical board; everything else is secondary.",
        "The exchange operates under strict accountability protocols — every lot is bonded, every buyer credentialled. Efficiency here means zero discrepancies, not fast transactions.",
        "Armed customs officers screen every manifest at the gate. The prices are firm and non-negotiable: the military administration sets them quarterly and does not accept appeals.",
    ],
}

# Generic templates for systems with no controlling faction.
_MARKET_FLAVOR_NEUTRAL: list[str] = [
    "An independent free-port where no single authority sets the rates. Prices fluctuate with the tides of supply and captain's desperation; sharp eyes find opportunities that regulated markets never offer.",
    "The station operates on an honour-ledger system: no faction oversight, no tariffs beyond a modest docking fee. What you find here is what traders have chosen to bring.",
    "Unclaimed space breeds eclectic commerce. Crates of unknown provenance sit beside certified lots, and the factor behind the exchange terminal has clearly seen things that broadened their definition of 'legal'.",
    "A crossroads market: factions pass through but none claim it, so prices bend to the negotiation skill of whoever is at the table today.",
    "The exchange board lists commodities from six different trade networks, each denominated in a different credit system. The local converter adds two percent and pretends it's a service.",
]


def _generate_market_flavor(system_name: str) -> tuple[str, str | None]:
    """
    Return (flavor_text, controlling_faction_name) for a market located in
    system_name.  The flavor text is a deterministic paragraph that blends the
    system's controlling faction identity with market atmosphere.

    Uses a hash of system_name to pick consistently from the template lists so
    the same system always shows the same text across sessions.
    """
    # Locate the system in the galaxy to find its controlling faction
    controlling_faction: str | None = None
    system_type: str = "Star"
    if game and hasattr(game, "galaxy") and game.galaxy:
        for sdata in game.galaxy.systems.values():
            if sdata.get("name") == system_name:
                controlling_faction = sdata.get("controlling_faction") or None
                system_type = sdata.get("type", "Star")
                break

    # Deterministic index: hash of system name → stable pick per system
    idx = abs(hash(system_name))

    if controlling_faction and controlling_faction in factions:
        fdata   = factions[controlling_faction]
        focus   = fdata.get("primary_focus", "Trade")
        phil    = fdata.get("philosophy", "")
        desc    = fdata.get("description", "")
        prefs   = fdata.get("preferred_trades", [])
        templates = _MARKET_FLAVOR_BY_FOCUS.get(focus, _MARKET_FLAVOR_NEUTRAL)
        base_text = templates[idx % len(templates)]

        # Append a brief faction-specific coda so each faction feels distinct
        pref_str = ", ".join(prefs[:3]) if prefs else ""
        coda = (
            f" {controlling_faction} ({phil}) administers this exchange. "
            f"{desc}"
            + (f" Their factors show particular interest in {pref_str}." if pref_str else "")
        )
        return base_text + coda, controlling_faction

    # No faction — neutral free-port text
    neutral = _MARKET_FLAVOR_NEUTRAL[idx % len(_MARKET_FLAVOR_NEUTRAL)]
    return neutral, None


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

    # Compute cargo stats from the active ship so the frontend can calculate
    # max-buyable quantities without a separate /api/ship call.
    ship = None
    try:
        ship = game.get_active_ship()
    except Exception:
        pass
    max_cargo  = getattr(ship, "max_cargo",  0) if ship else 0
    cargo_used = sum(game.inventory.values()) if game.inventory else 0

    # Generate faction-aware flavor text for this market
    market_description, market_faction = _generate_market_flavor(system_name)

    return {
        "system_name":        system_name,
        "commodities":        commodities,
        "best_buys":          [{"name": b[0], "price": b[1], "supply": b[2]} for b in info.get("best_buys",  [])],
        "best_sells":         [{"name": s[0], "price": s[1], "demand": s[2]} for s in info.get("best_sells", [])],
        "player_credits":     game.credits,
        "cargo_used":         cargo_used,
        "max_cargo":          max_cargo,
        "market_description": market_description,
        "controlling_faction": market_faction,
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
# NPC ship positions endpoint
# ===========================================================================

@app.get("/api/npc_ships")
async def get_npc_ships():
    """
    Return every NPC bot's position pre-projected to 2D axial hex coordinates.

    NPC bots are typically docked inside star systems, so their raw 3D
    coordinates project onto the exact same hex as the host system.  This
    makes clicking that hex always open the system panel instead of the NPC
    ship detail.  To prevent that, we compute the intended hex for each bot
    and, if it collides with any star-system hex, nudge it to the nearest
    unoccupied adjacent hex so the bot marker always renders outside systems.

    Response shape:
      { ships: [{ name, bot_type, coordinates: [x, y, z],
                  hex_q: int, hex_r: int }, ...] }

    hex_q / hex_r are the collision-free axial positions the frontend must
    use; the raw coordinates are included for reference only.
    """
    if not game or not game.character_created:
        raise HTTPException(status_code=400, detail="No game in progress.")

    bot_mgr = getattr(game, "bot_manager", None)
    if not bot_mgr:
        return {"ships": []}

    # Build the set of hexes already occupied by star systems and deep-space
    # stations so NPC ships are never placed on top of either.
    #
    # IMPORTANT: we must use resolve_hex_collisions() — not the raw
    # galaxy_coords_to_hex() projection — because the galaxy-map endpoint
    # nudges colliding systems to neighbouring hexes.  The raw projection
    # would give the wrong hex for any system that was nudged, so we'd miss
    # those hexes and still land NPC ships on top of them.
    occupied: set = set()

    galaxy = getattr(game.navigation, "galaxy", None) if hasattr(game, "navigation") else None
    if galaxy and hasattr(galaxy, "systems"):
        # Re-run the same minimal projection that /api/galaxy/map uses so we get
        # the collision-resolved hex positions, not the raw projections.
        raw = [{"name": d.get("name", ""), "x": c[0], "y": c[1], "z": c[2]}
               for c, d in galaxy.systems.items()]
        for s in resolve_hex_collisions(raw):
            occupied.add(HexCoord(s["hex_q"], s["hex_r"]))

    # Deep-space station hexes (already pre-projected and stored on each dict)
    station_mgr = getattr(game, "station_manager", None)
    if station_mgr:
        for st in station_mgr.get_deep_space_stations():
            if "hex_q" in st and "hex_r" in st:
                occupied.add(HexCoord(st["hex_q"], st["hex_r"]))

    ships = []
    # Track hexes already claimed by earlier NPC ships so they don't stack.
    claimed: set = set(occupied)

    ship_coords = _ship_coords()
    scan_range  = _effective_scan_range()

    for bot in bot_mgr.bots:
        bot_ship = getattr(bot, "ship", None)
        if not bot_ship:
            continue
        coords = getattr(bot_ship, "coordinates", None)
        if coords is None:
            continue

        # Hide NPC ships that are outside the player's scanner range
        if ship_coords:
            sx, sy, sz = ship_coords
            dist = math.sqrt((coords[0]-sx)**2 + (coords[1]-sy)**2 + (coords[2]-sz)**2)
            if dist > scan_range:
                continue

        # Project the bot's 3D position to the nearest axial hex.
        raw_hex = galaxy_coords_to_hex(coords[0], coords[1])

        # If the natural hex is inside a system (or already taken by another
        # NPC ship), find the nearest free neighbouring hex instead.
        if raw_hex in claimed:
            placed = _find_free_hex(raw_hex, claimed)
        else:
            placed = raw_hex
        claimed.add(placed)

        ships.append({
            "name":        bot.name,
            "bot_type":    bot.bot_type,
            "coordinates": list(coords),  # kept for reference
            "hex_q":       placed.q,      # collision-free hex position
            "hex_r":       placed.r,
        })

    return {"ships": ships}


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

    raw_stats    = game.character_stats or {}
    derived      = calculate_derived_attributes(raw_stats) if raw_stats else {}

    class_data   = character_classes.get(game.character_class, {})
    bg_data      = character_backgrounds.get(game.character_background, {})
    species_data = get_playable_species().get(game.character_species, {})

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
        "species":             game.character_species,
        "species_description": species_data.get("description", ""),
        "species_biology":     species_data.get("biology", ""),
        "species_traits":      species_data.get("special_traits", []),
        "species_category":    species_data.get("category", ""),
        "faction":          game.character_faction,
        "faction_description": factions.get(game.character_faction, {}).get("description", ""),
        "faction_philosophy":  factions.get(game.character_faction, {}).get("philosophy", ""),
        "faction_focus":       factions.get(game.character_faction, {}).get("primary_focus", ""),
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
        # Profession — populated from the ProfessionSystem assigned at game start
        "profession":             getattr(game, "character_profession", ""),
        "profession_category":    PROFESSIONS.get(getattr(game, "character_profession", ""), {}).get("category", ""),
        "profession_description": PROFESSIONS.get(getattr(game, "character_profession", ""), {}).get("description", ""),
        "profession_skills":      PROFESSIONS.get(getattr(game, "character_profession", ""), {}).get("skills", []),
        "profession_level":       getattr(game, "profession_system", None) and
                                  game.profession_system.profession_levels.get(getattr(game, "character_profession", ""), 1) or 1,
        "profession_xp":          getattr(game, "profession_system", None) and
                                  game.profession_system.profession_experience.get(getattr(game, "character_profession", ""), 0) or 0,
        # Unlocked benefits are gated by profession level (same logic as ProfessionSystem)
        "profession_benefits":    getattr(game, "profession_system", None) and
                                  game.profession_system.get_profession_bonuses(getattr(game, "character_profession", "")) or [],
        # All four tiers always included so the UI can display locked ones dimmed
        "profession_tiers": {
            "base":         PROFESSIONS.get(getattr(game, "character_profession", ""), {}).get("base_benefits", []),
            "intermediate": PROFESSIONS.get(getattr(game, "character_profession", ""), {}).get("intermediate_benefits", []),
            "advanced":     PROFESSIONS.get(getattr(game, "character_profession", ""), {}).get("advanced_benefits", []),
            "master":       PROFESSIONS.get(getattr(game, "character_profession", ""), {}).get("master_benefits", []),
        },
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
