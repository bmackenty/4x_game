"""
backend/colony.py — Colony / planetary hex-tile building system.

This is the Alpha Centauri "city" equivalent: each colonised planet gets a
hex-tile grid.  Players build improvements on tiles to produce resources
(minerals, food, research, ether, credits) per turn.

Design principles:
  * Terrain biases what improvements are productive (mountains → mining, etc.)
  * Research unlocks better improvements — the core research→build loop.
  * All production is calculated fresh each turn; no cached totals stored.
  * The module is self-contained and serialises to/from plain dicts for
    integration with save_game.py via game.colony_state.

Hex coordinate system: AXIAL (q, r) — same as hex_utils.py and hex-math.js.
"""

import random
import math
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Improvement catalogue
# ---------------------------------------------------------------------------

# Each entry defines the improvement's properties.
# unlock_required: name must appear in game.completed_research to allow build.
# base_production: resources added per turn on a neutral (non-modified) tile.
# terrain_bonus: { terrain_name: multiplier } — how terrain modifies production.
# terrain_restriction: if non-empty, only those terrain types allow this improvement.

IMPROVEMENTS: dict[str, dict] = {
    "Mineral Extractor": {
        "cost":                 2000,
        "unlock_required":      None,           # Available from turn 1
        "description":          "Extracts raw minerals from the planetary crust.",
        "base_production":      {"minerals": 3},
        "terrain_bonus":        {"mountains": 1.5, "volcanic": 1.2, "geothermal": 1.1},
        "terrain_restriction":  [],             # Any terrain
    },
    "Biofarm Complex": {
        "cost":                 1800,
        "unlock_required":      None,
        "description":          "Cultivates engineered crops to feed the colony population.",
        "base_production":      {"food": 4, "credits": 1},
        "terrain_bonus":        {"plains": 1.4, "forest": 1.4, "coastal": 1.2},
        "terrain_restriction":  [],
    },
    "Research Node": {
        "cost":                 3500,
        "unlock_required":      "Advanced Research",
        "description":          "A distributed computation cluster that accelerates research.",
        "base_production":      {"research": 3},
        "terrain_bonus":        {"crystal": 1.2},
        "terrain_restriction":  [],
    },
    "Ether Conduit": {
        "cost":                 4000,
        "unlock_required":      "Advanced Etheric Weaving",
        "description":          "Channels ambient Etheric Energy into usable power.",
        "base_production":      {"ether": 2},
        "terrain_bonus":        {"crystal": 1.6, "void": 1.4, "geothermal": 1.1},
        "terrain_restriction":  [],
    },
    "Defense Array": {
        "cost":                 5000,
        "unlock_required":      "Cloaking Technology",
        "description":          "Planetary defense grid that reduces orbital threat level.",
        "base_production":      {"defense": 2},     # defense reduces system threat_level
        "terrain_bonus":        {"mountains": 1.3},
        "terrain_restriction":  [],
    },
    "Trade Nexus": {
        "cost":                 6000,
        "unlock_required":      None,
        "description":          "Commercial hub boosting trade income from this planet.",
        "base_production":      {"credits": 8},
        "terrain_bonus":        {"coastal": 1.25, "ocean": 0.5},  # ocean is bad for trade hubs
        "terrain_restriction":  [],
    },
    "Neural Institute": {
        "cost":                 8000,
        "unlock_required":      "Cognitive Enhancement Systems",
        "description":          "Advanced research facility interfacing biological and digital minds.",
        "base_production":      {"research": 5, "ether": 1},
        "terrain_bonus":        {},
        "terrain_restriction":  [],
    },
    "Quantum Relay": {
        "cost":                 10000,
        "unlock_required":      "Quantum Temporal Dynamics",
        "description":          "Quantum-entanglement communications node; accelerates all research.",
        "base_production":      {"research": 3},
        "terrain_bonus":        {"crystal": 1.4},
        "terrain_restriction":  [],
    },
    "Bio-Synthesis Lab": {
        "cost":                 7000,
        "unlock_required":      "Bio-Engineering",
        "description":          "Synthesises exotic bio-materials from local organisms.",
        "base_production":      {"food": 3, "research": 2},
        "terrain_bonus":        {"forest": 1.3, "plains": 1.1},
        "terrain_restriction":  [],
    },
    "Deep Core Drill": {
        "cost":                 9000,
        "unlock_required":      "Mining Automation",
        "description":          "Pierces deep into the planetary core for ultra-dense minerals.",
        "base_production":      {"minerals": 8, "food": -1},  # food penalty from ecosystem damage
        "terrain_bonus":        {"mountains": 1.0},
        "terrain_restriction":  ["mountains"],                 # Mountains only
    },
    "Etheric Purifier": {
        "cost":                 5500,
        "unlock_required":      "Advanced Etheric Weaving",
        "description":          "Purifies corrupted Etheric zones, enabling settlement and production.",
        "base_production":      {"ether": 2},
        "terrain_bonus":        {"volcanic": 1.0},
        "terrain_restriction":  ["volcanic", "geothermal"],   # Harsh terrain only
    },
    "Void Anchor": {
        "cost":                 15000,
        "unlock_required":      "Null Space Exploration",
        "description":          "A gravitational anchor that stabilises void rifts and harvests dark energy.",
        "base_production":      {"ether": 5},
        "terrain_bonus":        {},
        "terrain_restriction":  ["void"],                      # Void terrain only
    },
    "Population Hub": {
        "cost":                 4500,
        "unlock_required":      None,
        "description":          "A dense residential district that expands the colony's population cap.",
        "base_production":      {"food": 2, "credits": 3},
        "terrain_bonus":        {"plains": 1.2, "coastal": 1.2},
        "terrain_restriction":  ["plains", "coastal", "forest", "desert"],  # No harsh terrain
    },
    "Solar Harvester": {
        "cost":                 3000,
        "unlock_required":      "Plasma Energy Dynamics",
        "description":          "Orbital solar array beaming clean power to the surface.",
        "base_production":      {"minerals": 2, "credits": 1},
        "terrain_bonus":        {},                            # No terrain dependency
        "terrain_restriction":  [],
    },
    "Xenobiology Station": {
        "cost":                 12000,
        "unlock_required":      "Xenogenetics",
        "description":          "Studies alien biomes to unlock unique research and diplomacy paths.",
        "base_production":      {"research": 4},
        "terrain_bonus":        {"forest": 1.2, "plains": 1.1},
        "terrain_restriction":  [],
    },

    # ── SPI — Strategic Power Index ─────────────────────────────────────────
    # Buildings that increase defense strength, fleet capacity, or military
    # readiness.  All feed into SPI via defense/fleet_points/refined_ore.

    "Ground Forces Barracks": {
        "cost":                 6000,
        "unlock_required":      None,
        "description":          "Trains ground troops and light garrisoned units, contributing "
                                "modest fleet points and local defense to the empire pool.",
        "base_production":      {"defense": 1, "fleet_points": 2},
        "terrain_bonus":        {"plains": 1.2, "desert": 1.1},
        "terrain_restriction":  [],
    },
    "Anti-Orbital Battery": {
        "cost":                 14000,
        "unlock_required":      "Plasma Energy Dynamics",
        "description":          "A plasma-fed surface-to-orbit cannon that raises planetary "
                                "threat cost for attackers and boosts empire defense rating.",
        "base_production":      {"defense": 4},
        "terrain_bonus":        {"mountains": 1.4, "volcanic": 1.1},
        "terrain_restriction":  ["mountains", "volcanic", "tundra"],
    },
    "Munitions Factory": {
        "cost":                 10000,
        "unlock_required":      "Mining Automation",
        "description":          "Converts raw ore directly into military ordinance, adding fleet "
                                "points and a trickle of refined ore to the empire chain.",
        "base_production":      {"fleet_points": 4, "refined_ore": 2},
        "terrain_bonus":        {"plains": 1.2, "mountains": 1.1},
        "terrain_restriction":  [],
    },
    "Planetary Shield Generator": {
        "cost":                 18000,
        "unlock_required":      "Null Space Exploration",
        "description":          "Projects a graviton barrier across the upper atmosphere, "
                                "dramatically increasing the colony's defense rating.",
        "base_production":      {"defense": 5},
        "terrain_bonus":        {"mountains": 1.2, "plains": 1.1},
        "terrain_restriction":  [],
    },
    "Command Citadel": {
        "cost":                 20000,
        "unlock_required":      "Cognitive Enhancement Systems",
        "description":          "A heavily-fortified joint-operations center that synchronises "
                                "planetary defense grids with the fleet, boosting both defense "
                                "and fleet-point output.",
        "base_production":      {"defense": 3, "fleet_points": 5},
        "terrain_bonus":        {"mountains": 1.3},
        "terrain_restriction":  [],
    },

    # ── REI — Resource Extraction Index ─────────────────────────────────────
    # Buildings that improve raw-material throughput: minerals, ether, food.
    # REI is computed from empire-wide production of these resources.

    "Tidal Energy Plant": {
        "cost":                 4500,
        "unlock_required":      None,
        "description":          "Harvests kinetic energy from ocean tides and coastal currents, "
                                "providing clean ether power and supplemental trade credits.",
        "base_production":      {"ether": 2, "credits": 2},
        "terrain_bonus":        {"coastal": 1.5, "ocean": 1.3},
        "terrain_restriction":  ["coastal", "ocean"],
    },
    "Geothermal Tap": {
        "cost":                 7000,
        "unlock_required":      "Plasma Energy Dynamics",
        "description":          "Drills deep conduits into volcanic hot-spots, extracting "
                                "massive geothermal ether and raw minerals as a by-product.",
        "base_production":      {"ether": 4, "minerals": 2},
        "terrain_bonus":        {"geothermal": 1.8, "volcanic": 1.3},
        "terrain_restriction":  ["geothermal", "volcanic"],
    },
    "Crystal Resonance Array": {
        "cost":                 12000,
        "unlock_required":      "Advanced Etheric Weaving",
        "description":          "Amplifies natural crystal-lattice vibrations to harvest dense "
                                "Etheric Energy, with a secondary harmonic that speeds local "
                                "research.",
        "base_production":      {"ether": 6, "research": 2},
        "terrain_bonus":        {"crystal": 2.0, "void": 1.5},
        "terrain_restriction":  ["crystal"],
    },
    "Atmospheric Processor": {
        "cost":                 5000,
        "unlock_required":      "Bio-Engineering",
        "description":          "Seeds hostile atmospheres with engineered microbes, slowly "
                                "converting barren terrain into arable land and freeing locked "
                                "mineral deposits.",
        "base_production":      {"food": 3, "minerals": 1},
        "terrain_bonus":        {"tundra": 1.5, "desert": 1.4},
        "terrain_restriction":  ["tundra", "desert", "volcanic"],
    },
    "Jungle Harvester": {
        "cost":                 3500,
        "unlock_required":      None,
        "description":          "A semi-autonomous canopy platform that extracts edible "
                                "bio-matter and trace Etheric compounds from deep forest biomes.",
        "base_production":      {"food": 5, "ether": 1},
        "terrain_bonus":        {"forest": 1.6, "plains": 1.1},
        "terrain_restriction":  ["forest"],
    },

    # ── KII — Knowledge & Innovation Index ──────────────────────────────────
    # Buildings that drive research output, AI capability, and innovation rate.
    # KII is computed from empire-wide research production and ether yield.

    "Academy of Sciences": {
        "cost":                 5000,
        "unlock_required":      None,
        "description":          "A formal institution of higher learning that trains researchers "
                                "and contributes steady research points each turn.",
        "base_production":      {"research": 4},
        "terrain_bonus":        {"plains": 1.1, "coastal": 1.2},
        "terrain_restriction":  [],
    },
    "Deep Space Observatory": {
        "cost":                 9000,
        "unlock_required":      "Quantum Temporal Dynamics",
        "description":          "A high-altitude telescope array that peers deep into the "
                                "galaxy, accelerating astro-physics research significantly.",
        "base_production":      {"research": 6},
        "terrain_bonus":        {"mountains": 1.4, "tundra": 1.2, "desert": 1.2},
        "terrain_restriction":  ["mountains", "tundra", "desert"],
    },
    "Psych-Net Hub": {
        "cost":                 11000,
        "unlock_required":      "Cognitive Enhancement Systems",
        "description":          "Links colonists via neural mesh into a distributed psionic "
                                "computation network, generating research and Etheric bandwidth.",
        "base_production":      {"research": 4, "ether": 2},
        "terrain_bonus":        {"crystal": 1.3, "void": 1.2},
        "terrain_restriction":  [],
    },
    "Xenolinguistics Center": {
        "cost":                 7500,
        "unlock_required":      "Xenogenetics",
        "description":          "Decodes alien communication artifacts and biological signal "
                                "patterns, producing research breakthroughs and diplomatic "
                                "trade value.",
        "base_production":      {"research": 3, "credits": 3},
        "terrain_bonus":        {"plains": 1.1, "coastal": 1.1, "forest": 1.1},
        "terrain_restriction":  [],
    },
    "Synthetic Mind Core": {
        "cost":                 22000,
        "unlock_required":      "Sentient Architecture",
        "description":          "An autonomous AI research engine that operates continuously, "
                                "producing the highest research yield of any surface structure.",
        "base_production":      {"research": 10},
        "terrain_bonus":        {"crystal": 1.4, "void": 1.2},
        "terrain_restriction":  [],
    },

    # ── ECI — Economic Capability Index ─────────────────────────────────────
    # Buildings that grow credit income, trade throughput, and food surplus.
    # ECI is computed from empire credits, trade volume, and food/industrial
    # output.

    "Spaceport Hub": {
        "cost":                 8500,
        "unlock_required":      None,
        "description":          "A commercial transit hub connecting the colony to wider trade "
                                "lanes, generating substantial credit income each turn.",
        "base_production":      {"credits": 12},
        "terrain_bonus":        {"plains": 1.3, "coastal": 1.2},
        "terrain_restriction":  [],
    },
    "Industrial Fabricator": {
        "cost":                 6500,
        "unlock_required":      "Mining Automation",
        "description":          "Mass-produces consumer goods and colony equipment, turning "
                                "raw minerals into credit-generating export commodities.",
        "base_production":      {"credits": 6, "minerals": 2},
        "terrain_bonus":        {"plains": 1.2, "mountains": 1.1},
        "terrain_restriction":  [],
    },
    "Luxury Habitat Complex": {
        "cost":                 5500,
        "unlock_required":      None,
        "description":          "High-end residential towers that attract affluent settlers, "
                                "growing the population tax base and improving food consumption "
                                "efficiency.",
        "base_production":      {"food": 3, "credits": 5},
        "terrain_bonus":        {"plains": 1.3, "forest": 1.2, "coastal": 1.2},
        "terrain_restriction":  ["plains", "coastal", "forest"],
    },
    "Interstellar Bank": {
        "cost":                 16000,
        "unlock_required":      None,
        "description":          "A galactic financial clearing-house that compounds interest "
                                "on empire reserves, producing the largest passive credit "
                                "income of any building.",
        "base_production":      {"credits": 20},
        "terrain_bonus":        {"coastal": 1.3, "plains": 1.2},
        "terrain_restriction":  [],
    },
    "Agri-Industrial Complex": {
        "cost":                 9500,
        "unlock_required":      "Bio-Engineering",
        "description":          "Integrates vertical farming with automated mineral processing "
                                "lines, producing both food surplus and raw mineral stockpiles.",
        "base_production":      {"food": 6, "minerals": 3},
        "terrain_bonus":        {"plains": 1.4, "forest": 1.2, "coastal": 1.1},
        "terrain_restriction":  [],
    },

    # ── Military production chain ────────────────────────────────────────────
    # Ore Processor  →  refined_ore per turn
    # Shipyard       →  fleet_points per turn (amplified by empire refined_ore)
    # Orbital Drydock→  fleet_points per turn (high-tier, research-gated)

    "Ore Processor": {
        "cost":                 8000,
        "unlock_required":      "Mining Automation",
        "description":          "Refines raw mineral ore into processed materials for industrial "
                                "and military use.  Ore Processors boost Shipyard output "
                                "empire-wide — more processors means faster fleet growth.",
        "base_production":      {"refined_ore": 4},
        "terrain_bonus":        {"mountains": 1.5, "volcanic": 1.3, "geothermal": 1.2},
        "terrain_restriction":  [],
    },
    "Shipyard": {
        "cost":                 12000,
        "unlock_required":      None,           # Available from turn 1
        "description":          "Constructs and maintains warships, contributing fleet points "
                                "to the empire pool each turn.  Output scales with empire-wide "
                                "refined ore supply from Ore Processors.",
        "base_production":      {"fleet_points": 6},
        "terrain_bonus":        {"coastal": 1.2, "ocean": 1.1, "plains": 1.1},
        "terrain_restriction":  [],
    },
    "Orbital Drydock": {
        "cost":                 25000,
        "unlock_required":      "Sentient Architecture",
        "description":          "A vast orbital construction platform capable of assembling "
                                "capital-class warships.  Produces substantially more fleet "
                                "points than a surface Shipyard and benefits fully from the "
                                "ore supply chain.",
        "base_production":      {"fleet_points": 18},
        "terrain_bonus":        {},
        "terrain_restriction":  [],
    },
}


# ---------------------------------------------------------------------------
# Terrain definitions
# ---------------------------------------------------------------------------

# Terrain types and their base resource modifiers.
# These multiply the improvement's base_production values.
TERRAIN_MODIFIERS: dict[str, dict] = {
    "plains":     {"food": 1.2, "minerals": 0.9, "ether": 1.0},
    "forest":     {"food": 1.3, "research": 1.1, "ether": 1.1},
    "ocean":      {"food": 0.8, "minerals": 0.5, "ether": 0.9},
    "mountains":  {"minerals": 1.4, "food": 0.7, "ether": 1.0},
    "tundra":     {"minerals": 1.1, "food": 0.5, "ether": 0.8},
    "volcanic":   {"minerals": 1.3, "food": 0.0, "ether": 1.2},
    "crystal":    {"ether": 1.5, "research": 1.2, "minerals": 1.1},
    "void":       {"ether": 2.0, "food": 0.0, "minerals": 0.0},
    "desert":     {"minerals": 1.0, "food": 0.4, "ether": 0.9},
    "coastal":    {"food": 1.1, "credits": 1.2, "minerals": 0.9},
    "geothermal": {"minerals": 1.2, "ether": 1.3, "food": 0.8},
}

# Terrain distribution probabilities per planet type.
# Each list is [(terrain_name, weight), ...].
PLANET_TERRAIN_DISTRIBUTIONS: dict[str, list] = {
    "Garden World": [
        ("plains", 40), ("forest", 30), ("ocean", 20), ("mountains", 10),
    ],
    "Terrestrial Planet": [
        ("plains", 30), ("mountains", 25), ("desert", 25), ("ocean", 20),
    ],
    "Ocean World": [
        ("ocean", 60), ("coastal", 20), ("mountains", 20),
    ],
    "Crystal World": [
        ("crystal", 30), ("mountains", 30), ("void", 20), ("plains", 20),
    ],
    "Jungle World": [
        ("forest", 50), ("ocean", 20), ("mountains", 15), ("plains", 15),
    ],
    "Lava World": [
        ("volcanic", 40), ("mountains", 30), ("geothermal", 30),
    ],
    "Frozen World": [
        ("tundra", 40), ("ocean", 30), ("mountains", 20), ("geothermal", 10),
    ],
    "Desert Planet": [
        ("desert", 50), ("mountains", 30), ("plains", 20),
    ],
    "Industrial World": [
        ("plains", 35), ("mountains", 25), ("desert", 20), ("ocean", 20),
    ],
    # Fallback for unknown planet types
    "default": [
        ("plains", 40), ("mountains", 20), ("desert", 20), ("ocean", 20),
    ],
}

# Hex grid radius per planet type — smaller grids for harsh worlds.
PLANET_GRID_RADIUS: dict[str, int] = {
    "Garden World":       6,
    "Terrestrial Planet": 5,
    "Ocean World":        6,
    "Crystal World":      5,
    "Jungle World":       6,
    "Lava World":         4,
    "Frozen World":       4,
    "Desert Planet":      4,
    "Industrial World":   5,
    "default":            5,
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class HexTile:
    """One tile in a planet's hex grid."""
    q: int                              # Axial column
    r: int                              # Axial row
    terrain: str                        # One of TERRAIN_MODIFIERS keys
    improvement: Optional[str] = None  # One of IMPROVEMENTS keys, or None
    improvement_turn_built: int = 0     # Turn number when improvement was placed
    improvement_level: int = 0          # 0 = base, 1 = upgraded, 2 = max tier
    is_claimed: bool = True             # False for tiles outside colonised radius


# Upgrade cost is this fraction of the base build cost, per level.
# Level 0→1 costs 60% of base; level 1→2 costs 90% of base.
_UPGRADE_COST_FRACTIONS = [0.60, 0.90]

# Production multiplier by level: level 0 = 1.0×, level 1 = 1.5×, level 2 = 2.2×
_UPGRADE_PRODUCTION_MULTIPLIERS = [1.0, 1.5, 2.2]

# Maximum upgrade level (0-indexed, so max = 2 means three tiers total)
MAX_IMPROVEMENT_LEVEL = 2

# Credits generated per 10,000 colonists each turn — the population tax base.
POPULATION_INCOME_PER_10K = 75

# Fleet pool production chain constants.
# Each unit of refined_ore per turn adds ORE_FLEET_BONUS_PER_UNIT to the
# shipyard output multiplier (capped at ORE_FLEET_BONUS_CAP above 1.0).
# Example: 10 refined_ore → +50% fleet_points from all Shipyards.
ORE_FLEET_BONUS_PER_UNIT = 0.05   # 5% per refined_ore/turn
ORE_FLEET_BONUS_CAP      = 2.0    # max 200% bonus (3× base output)
FLEET_POOL_MAX           = 99_999  # hard cap — unlikely to be reached in play


@dataclass
class ColonyGrid:
    """A colonised planet represented as a hex tile grid."""
    planet_name: str
    system_name: str
    planet_type: str
    grid_radius: int
    tiles: dict = field(default_factory=dict)  # (q, r) -> HexTile
    founded_turn: int = 1
    population: int = 1000


# ---------------------------------------------------------------------------
# ColonyManager
# ---------------------------------------------------------------------------

class ColonyManager:
    """
    Manages all player-founded colonies across the galaxy.

    Wired into the FastAPI app as a singleton alongside the Game instance.
    Calls advance_turn() on every turn-end to add colony production to
    the player's resources.
    """

    def __init__(self, game):
        self.game = game
        # planet_name → ColonyGrid
        self.colonies: dict[str, ColonyGrid] = {}

    # -----------------------------------------------------------------------
    # Colony lifecycle
    # -----------------------------------------------------------------------

    def found_colony(self, planet_name: str, system_name: str,
                     planet_type: str) -> tuple[bool, str, Optional[ColonyGrid]]:
        """
        Found a new colony on a habitable planet.

        Generates the hex grid seeded from the planet name for
        reproducible terrain layouts.

        Returns (success, message, colony_grid).
        """
        if planet_name in self.colonies:
            return False, f"A colony on {planet_name} already exists.", None

        radius = PLANET_GRID_RADIUS.get(planet_type, PLANET_GRID_RADIUS["default"])
        tiles = self._generate_hex_grid(planet_name, planet_type, radius)

        colony = ColonyGrid(
            planet_name=planet_name,
            system_name=system_name,
            planet_type=planet_type,
            grid_radius=radius,
            tiles=tiles,
            founded_turn=self.game.current_turn,
            population=10_000,
        )
        self.colonies[planet_name] = colony
        return True, f"Colony founded on {planet_name}.", colony

    # -----------------------------------------------------------------------
    # Building improvements
    # -----------------------------------------------------------------------

    def build_improvement(self, planet_name: str, q: int, r: int,
                          improvement_type: str) -> tuple[bool, str]:
        """
        Build an improvement on a specific hex tile.

        Validates:
          * Colony exists.
          * Tile exists in the grid.
          * Improvement type is valid.
          * Research prerequisite is met (checked against game.completed_research).
          * Tile has no existing improvement.
          * Terrain restriction is satisfied.
          * Player has sufficient credits.
          * Player has an action point remaining.
        """
        if planet_name not in self.colonies:
            return False, f"No colony on {planet_name}."

        colony = self.colonies[planet_name]
        tile = colony.tiles.get((q, r))
        if tile is None:
            return False, f"Tile ({q}, {r}) does not exist on {planet_name}."

        if improvement_type not in IMPROVEMENTS:
            return False, f"Unknown improvement type: {improvement_type}."

        improvement = IMPROVEMENTS[improvement_type]

        # Research gate
        required = improvement["unlock_required"]
        if required and required not in self.game.completed_research:
            return False, f"Requires research: {required}."

        # Existing improvement
        if tile.improvement is not None:
            return False, f"Tile ({q}, {r}) already has a {tile.improvement}."

        # Terrain restriction
        restrictions = improvement["terrain_restriction"]
        if restrictions and tile.terrain not in restrictions:
            allowed = ", ".join(restrictions)
            return False, (
                f"{improvement_type} can only be built on: {allowed}. "
                f"This tile is {tile.terrain}."
            )

        # Credits
        cost = improvement["cost"]
        if self.game.credits < cost:
            return False, f"Insufficient credits. Need {cost:,}, have {self.game.credits:,}."

        # Action point
        ok, msg = self.game.consume_action("colony_build")
        if not ok:
            return False, msg

        # Commit the build
        self.game.credits -= cost
        tile.improvement = improvement_type
        tile.improvement_turn_built = self.game.current_turn

        prod = self.calculate_tile_production(tile)
        summary = ", ".join(f"+{v} {k}" for k, v in prod.items() if v > 0)
        return True, f"Built {improvement_type} on {tile.terrain} tile. Production: {summary}."

    def upgrade_improvement(self, planet_name: str, q: int, r: int) -> tuple[bool, str]:
        """
        Upgrade the improvement on a tile to the next production tier.

        Each upgrade costs a fraction of the original build cost and increases
        production by the tier multiplier (_UPGRADE_PRODUCTION_MULTIPLIERS).
        Maximum of MAX_IMPROVEMENT_LEVEL upgrades.
        """
        if planet_name not in self.colonies:
            return False, f"No colony on {planet_name}."

        colony = self.colonies[planet_name]
        tile = colony.tiles.get((q, r))
        if tile is None:
            return False, f"Tile ({q}, {r}) does not exist on {planet_name}."
        if not tile.improvement:
            return False, "No improvement on that tile to upgrade."
        if tile.improvement_level >= MAX_IMPROVEMENT_LEVEL:
            return False, f"{tile.improvement} is already at maximum tier (Tier {MAX_IMPROVEMENT_LEVEL + 1})."

        cost = self.get_upgrade_cost(tile.improvement, tile.improvement_level)
        if cost == 0:
            return False, "Cannot determine upgrade cost."
        if self.game.credits < cost:
            return False, f"Insufficient credits. Need {cost:,}, have {self.game.credits:,}."

        # Consume an action point
        ok, msg = self.game.consume_action("colony_build")
        if not ok:
            return False, msg

        # Apply the upgrade
        self.game.credits -= cost
        tile.improvement_level += 1

        new_level_name = f"Tier {tile.improvement_level + 1}"
        prod = self.calculate_tile_production(tile)
        summary = ", ".join(f"+{v} {k}" for k, v in prod.items() if v > 0)
        return True, (
            f"{tile.improvement} upgraded to {new_level_name}. "
            f"New production: {summary}."
        )

    def demolish_improvement(self, planet_name: str, q: int, r: int
                             ) -> tuple[bool, str, int]:
        """
        Remove the improvement from a tile and refund 50% of its cost.

        Returns (success, message, refund_amount).
        """
        if planet_name not in self.colonies:
            return False, f"No colony on {planet_name}.", 0

        colony = self.colonies[planet_name]
        tile = colony.tiles.get((q, r))
        if tile is None or tile.improvement is None:
            return False, "No improvement on that tile.", 0

        improvement = IMPROVEMENTS.get(tile.improvement, {})
        refund = improvement.get("cost", 0) // 2
        self.game.credits += refund
        name = tile.improvement
        tile.improvement = None
        tile.improvement_turn_built = 0
        return True, f"Demolished {name}. Refund: {refund:,} credits.", refund

    # -----------------------------------------------------------------------
    # Production calculation
    # -----------------------------------------------------------------------

    def calculate_tile_production(self, tile: HexTile) -> dict[str, float]:
        """
        Calculate what a single tile produces per turn.

        Combines:
          * improvement's base_production
          * improvement's terrain_bonus for this specific terrain
          * TERRAIN_MODIFIERS for this terrain (applied to each resource)
          * upgrade multiplier based on tile.improvement_level
        """
        if not tile.improvement:
            return {}

        improvement = IMPROVEMENTS[tile.improvement]
        base = dict(improvement["base_production"])
        terrain_mod = TERRAIN_MODIFIERS.get(tile.terrain, {})
        improvement_terrain_bonus = improvement["terrain_bonus"].get(tile.terrain, 1.0)

        # Production scales with upgrade level
        level = max(0, min(tile.improvement_level, MAX_IMPROVEMENT_LEVEL))
        upgrade_multiplier = _UPGRADE_PRODUCTION_MULTIPLIERS[level]

        production = {}
        for resource, amount in base.items():
            if amount == 0:
                continue
            # Apply the terrain bonus specific to this improvement type
            adjusted = amount * improvement_terrain_bonus
            # Apply global terrain modifier for this resource
            terrain_factor = terrain_mod.get(resource, 1.0)
            adjusted *= terrain_factor
            # Apply upgrade tier multiplier
            adjusted *= upgrade_multiplier
            production[resource] = round(adjusted, 2)

        return production

    @staticmethod
    def get_upgrade_cost(improvement_type: str, current_level: int) -> int:
        """
        Return the credit cost to upgrade an improvement from current_level to
        current_level + 1.  Returns 0 if already at max or type is unknown.
        """
        if current_level >= MAX_IMPROVEMENT_LEVEL:
            return 0
        base_cost = IMPROVEMENTS.get(improvement_type, {}).get("cost", 0)
        fraction = _UPGRADE_COST_FRACTIONS[current_level]
        return int(base_cost * fraction)

    def calculate_colony_production(self, planet_name: str) -> dict[str, float]:
        """Sum production across all improved tiles for one colony."""
        colony = self.colonies.get(planet_name)
        if not colony:
            return {}

        totals: dict[str, float] = {}
        for tile in colony.tiles.values():
            if tile.improvement:
                for resource, amount in self.calculate_tile_production(tile).items():
                    totals[resource] = totals.get(resource, 0.0) + amount

        return {k: round(v, 1) for k, v in totals.items()}

    def calculate_all_production(self) -> dict[str, float]:
        """Sum production across all colonies."""
        totals: dict[str, float] = {}
        for planet_name in self.colonies:
            for resource, amount in self.calculate_colony_production(planet_name).items():
                totals[resource] = totals.get(resource, 0.0) + amount
        return {k: round(v, 1) for k, v in totals.items()}

    # -----------------------------------------------------------------------
    # Turn advancement hook
    # -----------------------------------------------------------------------

    def advance_turn(self, turn_events: list) -> dict:
        """
        Called by the /api/game/turn/end endpoint after game.end_turn().

        Adds colony production + population tax income to the player's
        resources and appends events to the turn_events list.

        Returns a financial_summary dict used by the GNN end-of-turn report:
          {
            "colony_credits":   int,   # credits from buildings
            "population_income": int,  # credits from population tax
            "research_pts":     int,
            "colonies":         [ { "name": str, "income": int, "pop": int } ],
          }
        """
        production = self.calculate_all_production()

        # ── Per-colony income details (for the GNN report) ──────────────────
        colony_details = []
        total_pop_income = 0

        for planet_name, colony in self.colonies.items():
            # Population tax: POPULATION_INCOME_PER_10K per 10,000 colonists
            pop_income = int(colony.population / 10_000 * POPULATION_INCOME_PER_10K)
            total_pop_income += pop_income
            self.game.credits += pop_income

            col_prod = self.calculate_colony_production(planet_name)
            colony_credits = int(col_prod.get("credits", 0))
            colony_details.append({
                "name":   planet_name,
                "income": pop_income + colony_credits,
                "pop":    colony.population,
            })

        # ── Building production ──────────────────────────────────────────────
        credits_earned = int(production.get("credits", 0))
        research_pts   = int(production.get("research", 0))

        if credits_earned:
            self.game.credits += credits_earned

        if research_pts and self.game.active_research:
            self.game.research_progress += research_pts

        # ── Fleet production chain (minerals → refined ore → fleet points) ──
        # refined_ore per turn acts as a multiplier on raw fleet_points output.
        # This is the full chain: Ore Processors feed Shipyards / Orbital Drydocks.
        refined_ore_pts  = int(production.get("refined_ore",  0))
        fleet_pts_base   = int(production.get("fleet_points", 0))

        if fleet_pts_base > 0:
            # Each unit of refined_ore adds ORE_FLEET_BONUS_PER_UNIT to the
            # multiplier, capped at 1.0 + ORE_FLEET_BONUS_CAP.
            ore_bonus      = min(ORE_FLEET_BONUS_CAP, refined_ore_pts * ORE_FLEET_BONUS_PER_UNIT)
            fleet_pts_eff  = int(fleet_pts_base * (1.0 + ore_bonus))
            self.game.fleet_pool = min(
                FLEET_POOL_MAX,
                getattr(self.game, "fleet_pool", 0) + fleet_pts_eff,
            )
            turn_events.append({
                "channel": "MILITARY",
                "message": (
                    f"Fleet production: +{fleet_pts_eff} fleet points"
                    + (f" (ore bonus: +{int(ore_bonus * 100)}%)" if ore_bonus > 0 else "")
                    + f".  Pool: {self.game.fleet_pool}"
                ),
            })
        elif refined_ore_pts > 0:
            # Ore being produced but no shipyard yet — note it for the player.
            turn_events.append({
                "channel": "MILITARY",
                "message": f"Ore Processors produced {refined_ore_pts} refined ore/turn — "
                           "build a Shipyard to convert this into fleet strength.",
            })

        # ── Event log toast ──────────────────────────────────────────────────
        total_colony_credits = credits_earned + total_pop_income
        summary_parts = []
        if total_colony_credits:
            summary_parts.append(f"+{total_colony_credits:,} credits")
        for resource, amount in production.items():
            if resource not in ("credits", "refined_ore", "fleet_points") and amount > 0:
                summary_parts.append(f"+{amount} {resource}")

        if summary_parts:
            turn_events.append({
                "channel": "ECON",
                "message": f"Colony income: {', '.join(summary_parts)}",
            })

        return {
            "colony_credits":    credits_earned,
            "population_income": total_pop_income,
            "research_pts":      research_pts,
            "fleet_pts":         fleet_pts_base,
            "fleet_pts_eff":     int(fleet_pts_base * (1.0 + min(ORE_FLEET_BONUS_CAP, refined_ore_pts * ORE_FLEET_BONUS_PER_UNIT))) if fleet_pts_base > 0 else 0,
            "refined_ore_pts":   refined_ore_pts,
            "fleet_pool":        getattr(self.game, "fleet_pool", 0),
            "colonies":          colony_details,
        }

    # -----------------------------------------------------------------------
    # Serialisation (for save_game integration)
    # -----------------------------------------------------------------------

    def serialize(self) -> dict:
        """Return a JSON-serialisable dict of all colony state."""
        result = {}
        for planet_name, colony in self.colonies.items():
            tiles_data = {}
            for (q, r), tile in colony.tiles.items():
                tiles_data[f"{q},{r}"] = {
                    "q": tile.q,
                    "r": tile.r,
                    "terrain": tile.terrain,
                    "improvement": tile.improvement,
                    "improvement_turn_built": tile.improvement_turn_built,
                    "improvement_level": tile.improvement_level,
                    "is_claimed": tile.is_claimed,
                }
            result[planet_name] = {
                "planet_name":  colony.planet_name,
                "system_name":  colony.system_name,
                "planet_type":  colony.planet_type,
                "grid_radius":  colony.grid_radius,
                "founded_turn": colony.founded_turn,
                "population":   colony.population,
                "tiles":        tiles_data,
            }
        return result

    def deserialize(self, data: dict) -> None:
        """Restore colony state from a serialised dict (after load_game)."""
        self.colonies = {}
        for planet_name, colony_data in data.items():
            tiles = {}
            for key, td in colony_data.get("tiles", {}).items():
                q, r = td["q"], td["r"]
                tiles[(q, r)] = HexTile(
                    q=q, r=r,
                    terrain=td["terrain"],
                    improvement=td.get("improvement"),
                    improvement_turn_built=td.get("improvement_turn_built", 0),
                    improvement_level=td.get("improvement_level", 0),
                    is_claimed=td.get("is_claimed", True),
                )
            self.colonies[planet_name] = ColonyGrid(
                planet_name=colony_data["planet_name"],
                system_name=colony_data["system_name"],
                planet_type=colony_data["planet_type"],
                grid_radius=colony_data["grid_radius"],
                founded_turn=colony_data.get("founded_turn", 1),
                population=colony_data.get("population", 10000),
                tiles=tiles,
            )

    # -----------------------------------------------------------------------
    # JSON representation helpers
    # -----------------------------------------------------------------------

    def get_colony_dict(self, planet_name: str) -> Optional[dict]:
        """
        Return a JSON-serialisable representation of one colony for the
        /api/colony/{planet_name} endpoint.
        """
        colony = self.colonies.get(planet_name)
        if not colony:
            return None

        tiles_list = []
        for (q, r), tile in colony.tiles.items():
            tile_prod = self.calculate_tile_production(tile)
            upgrade_cost = (
                self.get_upgrade_cost(tile.improvement, tile.improvement_level)
                if tile.improvement else 0
            )
            tiles_list.append({
                "q":                q,
                "r":                r,
                "terrain":          tile.terrain,
                "improvement":      tile.improvement,
                "improvement_level": tile.improvement_level,
                "can_upgrade":      bool(tile.improvement and upgrade_cost > 0),
                "upgrade_cost":     upgrade_cost,
                "production":       tile_prod,
                "is_claimed":       tile.is_claimed,
            })

        return {
            "planet_name":    colony.planet_name,
            "system_name":    colony.system_name,
            "planet_type":    colony.planet_type,
            "grid_radius":    colony.grid_radius,
            "founded_turn":   colony.founded_turn,
            "population":     colony.population,
            "total_production": self.calculate_colony_production(planet_name),
            "tiles":          tiles_list,
            "tile_count":     len(tiles_list),
            "improvement_count": sum(1 for t in colony.tiles.values() if t.improvement),
        }

    def list_colonies(self) -> list[dict]:
        """Return a summary list of all colonies (for /api/colony/all)."""
        result = []
        for planet_name, colony in self.colonies.items():
            result.append({
                "planet_name":   planet_name,
                "system_name":   colony.system_name,
                "planet_type":   colony.planet_type,
                "tile_count":    len(colony.tiles),
                "improvement_count": sum(1 for t in colony.tiles.values() if t.improvement),
                "production":    self.calculate_colony_production(planet_name),
                "founded_turn":  colony.founded_turn,
                "population":    colony.population,
            })
        return result

    # -----------------------------------------------------------------------
    # Improvement catalogue endpoint helper
    # -----------------------------------------------------------------------

    @staticmethod
    def get_improvements_catalogue(completed_research: list[str]) -> list[dict]:
        """
        Return all improvements with their unlock status given a list of
        completed research.  Used by /api/colony/improvements.
        """
        catalogue = []
        for name, data in IMPROVEMENTS.items():
            required = data["unlock_required"]
            unlocked = (required is None) or (required in completed_research)
            catalogue.append({
                "name":         name,
                "cost":         data["cost"],
                "description":  data["description"],
                "unlock_required": required,
                "unlocked":     unlocked,
                "base_production": data["base_production"],
                "terrain_bonus":   data["terrain_bonus"],
                "terrain_restriction": data["terrain_restriction"],
            })
        # Sort: unlocked first, then by cost
        catalogue.sort(key=lambda x: (not x["unlocked"], x["cost"]))
        return catalogue

    # -----------------------------------------------------------------------
    # Private helpers
    # -----------------------------------------------------------------------

    def _generate_hex_grid(self, planet_name: str, planet_type: str,
                            radius: int) -> dict:
        """
        Generate the hex tile grid for a planet.

        Terrain is assigned pseudo-randomly but seeded from the planet name
        so the same planet always gets the same layout (even across sessions).
        """
        rng = random.Random(hash(planet_name) & 0xFFFFFFFF)

        # Get the weighted terrain distribution for this planet type
        dist = PLANET_TERRAIN_DISTRIBUTIONS.get(
            planet_type, PLANET_TERRAIN_DISTRIBUTIONS["default"]
        )
        terrain_types = [t for t, _ in dist]
        terrain_weights = [w for _, w in dist]

        tiles = {}
        # Generate all hexes within the grid radius using spiral order
        for q, r in _hex_spiral((0, 0), radius):
            terrain = rng.choices(terrain_types, weights=terrain_weights, k=1)[0]
            tiles[(q, r)] = HexTile(q=q, r=r, terrain=terrain, is_claimed=True)

        return tiles


# ---------------------------------------------------------------------------
# Minimal hex spiral (duplicated from hex_utils to keep this module self-contained)
# ---------------------------------------------------------------------------

def _hex_spiral(center: tuple, radius: int) -> list[tuple]:
    """Return all (q, r) axial coords within `radius` steps of center."""
    cq, cr = center
    results = [(cq, cr)]
    for r in range(1, radius + 1):
        results.extend(_hex_ring(center, r))
    return results


def _hex_ring(center: tuple, radius: int) -> list[tuple]:
    """Return the ring of hexes exactly `radius` steps from center."""
    cq, cr = center
    DIRECTIONS = [(1,0),(1,-1),(0,-1),(-1,0),(-1,1),(0,1)]
    if radius == 0:
        return [(cq, cr)]
    results = []
    # Start at South-West neighbour, radius steps away
    hq = cq + DIRECTIONS[4][0] * radius
    hr = cr + DIRECTIONS[4][1] * radius
    for i in range(6):
        for _ in range(radius):
            results.append((hq, hr))
            hq += DIRECTIONS[i][0]
            hr += DIRECTIONS[i][1]
    return results
