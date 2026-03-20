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

import json
import pathlib
import random
import math
from dataclasses import dataclass, field
from typing import Optional

# Social / economic / political system definitions and helpers.
from .colony_systems import (
    get_production_modifiers,
    calculate_coherence,
    get_system_def,
    ECONOMIC_SYSTEMS,
)


# ---------------------------------------------------------------------------
# Improvement catalogue — loaded from lore/colony_improvements.json
# ---------------------------------------------------------------------------

_IMPROVEMENTS_PATH = pathlib.Path(__file__).parent.parent / "lore" / "colony_improvements.json"
IMPROVEMENTS: dict[str, dict] = json.loads(_IMPROVEMENTS_PATH.read_text(encoding="utf-8"))["improvements"]

# ---------------------------------------------------------------------------
# Building → research category map — derived from lore/research.json
# ---------------------------------------------------------------------------
# Maps building name → research category so the catalogue endpoint can
# group improvements by domain without embedding category in each building def.

_RESEARCH_PATH = pathlib.Path(__file__).parent.parent / "lore" / "research.json"
_research_data = json.loads(_RESEARCH_PATH.read_text(encoding="utf-8"))

# Walk every research project; any unlock ending with "(colony)" is a building.
_BUILDING_CATEGORY: dict[str, str] = {}
for _proj_name, _proj in _research_data["research"].items():
    _cat = _proj.get("category", "Unknown")
    for _unlock in _proj.get("unlocks", []):
        if "(colony)" in _unlock:
            _bname = _unlock.replace(" (colony)", "").strip()
            _BUILDING_CATEGORY[_bname] = _cat


# ---------------------------------------------------------------------------
# Terrain data — loaded from lore/terrain.json
# ---------------------------------------------------------------------------

_TERRAIN_PATH = pathlib.Path(__file__).parent.parent / "lore" / "terrain.json"
_terrain_data = json.loads(_TERRAIN_PATH.read_text(encoding="utf-8"))

# Terrain types and their base resource modifiers.
TERRAIN_MODIFIERS: dict[str, dict] = _terrain_data["terrain_modifiers"]

# Weighted terrain distribution per planet type: [[terrain, weight], ...]
PLANET_TERRAIN_DISTRIBUTIONS: dict[str, list] = _terrain_data["planet_terrain_distributions"]

# Hex grid radius per planet type — smaller grids for harsh worlds.
PLANET_GRID_RADIUS: dict[str, int] = _terrain_data["planet_grid_radius"]


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


# ---------------------------------------------------------------------------
# Game balance constants — loaded from lore/game_config.json
# ---------------------------------------------------------------------------

_CONFIG_PATH = pathlib.Path(__file__).parent.parent / "lore" / "game_config.json"
_cfg = json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))

# Upgrade cost fractions and production multipliers per tier.
_UPGRADE_COST_FRACTIONS          = _cfg["upgrade_cost_fractions"]
_UPGRADE_PRODUCTION_MULTIPLIERS  = _cfg["upgrade_production_multipliers"]
MAX_IMPROVEMENT_LEVEL            = _cfg["max_improvement_level"]

# Population constants.
POPULATION_INCOME_PER_10K  = _cfg["population_income_per_10k"]
POP_BASE_GROWTH_RATE       = _cfg["pop_base_growth_rate"]
POP_FOOD_GROWTH_PER_UNIT   = _cfg["pop_food_growth_per_unit"]
POP_HUB_GROWTH_BONUS       = _cfg["pop_hub_growth_bonus"]
POP_LUXURY_GROWTH_BONUS    = _cfg["pop_luxury_growth_bonus"]
POP_BIOFARM_GROWTH_BONUS   = _cfg["pop_biofarm_growth_bonus"]
POP_MAX_GROWTH_RATE        = _cfg["pop_max_growth_rate"]

# Fleet pool production chain constants.
ORE_FLEET_BONUS_PER_UNIT   = _cfg["ore_fleet_bonus_per_unit"]
ORE_FLEET_BONUS_CAP        = _cfg["ore_fleet_bonus_cap"]
FLEET_POOL_MAX             = _cfg["fleet_pool_max"]


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

    # ── Governing systems ────────────────────────────────────────────────────
    # Each colony has one social, economic, and political system.  These are
    # set by the player via the Systems panel and apply multiplier bonuses /
    # penalties to production, diplomacy, and trade.
    # IDs must match keys in backend/colony_systems.py.
    social_system:   str = "resonance_cohesion"
    economic_system: str = "energy_state"
    political_system: str = "consensus_field"

    # Turn number when each system was last changed (for cooldown enforcement).
    social_last_changed:   int = 0
    economic_last_changed: int = 0
    political_last_changed: int = 0


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
        """
        Sum production across all improved tiles for one colony, then apply
        the colony's social / economic / political system modifiers and the
        coherence multiplier.

        The systems layer sits on top of the terrain + improvement layer so the
        two calculation paths stay independent and easy to reason about.
        """
        colony = self.colonies.get(planet_name)
        if not colony:
            return {}

        # ── Base tile production ─────────────────────────────────────────────
        totals: dict[str, float] = {}
        for tile in colony.tiles.values():
            if tile.improvement:
                for resource, amount in self.calculate_tile_production(tile).items():
                    totals[resource] = totals.get(resource, 0.0) + amount

        # ── System modifiers ─────────────────────────────────────────────────
        # get_production_modifiers returns per-resource multipliers and a flat
        # stability delta.  We apply "all_production" first, then per-resource.
        mods = get_production_modifiers(
            colony.social_system,
            colony.economic_system,
            colony.political_system,
        )

        # Coherence multiplier — synergistic systems amplify output, friction
        # systems suppress it.
        _, _label, coherence_mult = calculate_coherence(
            colony.social_system,
            colony.economic_system,
            colony.political_system,
        )

        # "all_production" modifier is additive to the 1.0 base before coherence.
        all_prod_delta = mods.get("all_production", 1.0) - 1.0  # e.g. 0.08 for +8%

        modified: dict[str, float] = {}
        for resource, base_value in totals.items():
            # Skip non-multiplicative resources (fleet_points handled separately).
            per_resource_mult = mods.get(resource, 1.0) + all_prod_delta
            modified[resource] = base_value * per_resource_mult * coherence_mult

        # Pass through stability as a flat int (not a production resource).
        if mods.get("stability", 0):
            modified["stability"] = mods["stability"]

        return {k: round(v, 1) for k, v in modified.items()}

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
            col_prod = self.calculate_colony_production(planet_name)

            # ── Population growth ─────────────────────────────────────────────
            # Growth rate = base rate
            #             + food production bonus (each food unit = +0.4%)
            #             + Population Hub count bonus (each hub = +1.5%)
            #             + Luxury Habitat Complex bonus (each = +0.8%)
            #             + Biofarm Complex bonus (each = +0.5%)
            # Clamped to [0, POP_MAX_GROWTH_RATE].
            food_pts = col_prod.get("food", 0)
            food_bonus = food_pts * POP_FOOD_GROWTH_PER_UNIT

            pop_hub_count = sum(
                1 for t in colony.tiles.values()
                if t.improvement == "Population Hub"
            )
            luxury_count = sum(
                1 for t in colony.tiles.values()
                if t.improvement == "Luxury Habitat Complex"
            )
            biofarm_count = sum(
                1 for t in colony.tiles.values()
                if t.improvement == "Biofarm Complex"
            )

            growth_rate = min(
                POP_MAX_GROWTH_RATE,
                POP_BASE_GROWTH_RATE
                + food_bonus
                + pop_hub_count  * POP_HUB_GROWTH_BONUS
                + luxury_count   * POP_LUXURY_GROWTH_BONUS
                + biofarm_count  * POP_BIOFARM_GROWTH_BONUS,
            )
            growth_rate = max(0.0, growth_rate)  # no decline from pop mechanics

            pop_gain = int(colony.population * growth_rate)
            colony.population += pop_gain

            # Emit a notable event every time population crosses a 100k boundary.
            pop_before = colony.population - pop_gain
            if pop_gain > 0 and (colony.population // 100_000) > (pop_before // 100_000):
                turn_events.append({
                    "channel": "ECON",
                    "message": (
                        f"{planet_name} population reached "
                        f"{colony.population:,} colonists!"
                    ),
                })

            # ── Population tax ────────────────────────────────────────────────
            # Collected after growth so the new residents contribute this turn.
            pop_income = int(colony.population / 10_000 * POPULATION_INCOME_PER_10K)
            total_pop_income += pop_income
            self.game.credits += pop_income

            colony_credits = int(col_prod.get("credits", 0))
            colony_details.append({
                "name":       planet_name,
                "income":     pop_income + colony_credits,
                "pop":        colony.population,
                "pop_growth": pop_gain,
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

        # ── Unique commodity production (economic system) ────────────────────
        # Each economic system type produces a unique tradeable commodity each
        # turn.  The commodity is added directly to the player's cargo inventory
        # (game.inventory) so it can be sold at any market.
        commodity_summary: list[str] = []
        for planet_name, colony in self.colonies.items():
            econ_def = ECONOMIC_SYSTEMS.get(colony.economic_system, {})
            commodity = econ_def.get("unique_commodity")
            amount    = econ_def.get("commodity_amount", 0)
            if commodity and amount:
                inv = getattr(self.game, "inventory", None)
                if inv is None:
                    self.game.inventory = {}
                    inv = self.game.inventory
                inv[commodity] = inv.get(commodity, 0) + amount
                commodity_summary.append(f"{planet_name}: +{amount} {commodity}")

        if commodity_summary:
            turn_events.append({
                "channel": "ECON",
                "message": "Economic systems produced: " + "; ".join(commodity_summary),
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
                # Governing systems
                "social_system":            colony.social_system,
                "economic_system":          colony.economic_system,
                "political_system":         colony.political_system,
                "social_last_changed":      colony.social_last_changed,
                "economic_last_changed":    colony.economic_last_changed,
                "political_last_changed":   colony.political_last_changed,
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
                # Governing systems — fall back to tier-1 defaults for old saves.
                social_system=colony_data.get("social_system",   "resonance_cohesion"),
                economic_system=colony_data.get("economic_system", "energy_state"),
                political_system=colony_data.get("political_system", "consensus_field"),
                social_last_changed=colony_data.get("social_last_changed",   0),
                economic_last_changed=colony_data.get("economic_last_changed", 0),
                political_last_changed=colony_data.get("political_last_changed", 0),
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

        # Calculate projected growth rate for display purposes.
        # Mirrors the formula in advance_turn so the UI can show "+X pop/turn".
        col_prod = self.calculate_colony_production(planet_name)
        food_pts     = col_prod.get("food", 0)
        food_bonus   = food_pts * POP_FOOD_GROWTH_PER_UNIT
        hub_count    = sum(1 for t in colony.tiles.values() if t.improvement == "Population Hub")
        lux_count    = sum(1 for t in colony.tiles.values() if t.improvement == "Luxury Habitat Complex")
        bio_count    = sum(1 for t in colony.tiles.values() if t.improvement == "Biofarm Complex")
        growth_rate  = min(
            POP_MAX_GROWTH_RATE,
            POP_BASE_GROWTH_RATE
            + food_bonus
            + hub_count * POP_HUB_GROWTH_BONUS
            + lux_count * POP_LUXURY_GROWTH_BONUS
            + bio_count * POP_BIOFARM_GROWTH_BONUS,
        )
        growth_rate  = max(0.0, growth_rate)
        pop_gain_est = int(colony.population * growth_rate)

        # ── Systems summary block for the frontend Systems panel ─────────────
        coherence_score, coherence_label, coherence_mult = calculate_coherence(
            colony.social_system,
            colony.economic_system,
            colony.political_system,
        )
        econ_def = ECONOMIC_SYSTEMS.get(colony.economic_system, {})

        def _sys_summary(sys_id: str, sys_dict: dict) -> dict:
            """Build a compact summary dict for one system."""
            defn = sys_dict.get(sys_id, {})
            return {
                "id":              sys_id,
                "name":            defn.get("name", sys_id),
                "description":     defn.get("description", ""),
                "modifiers":       defn.get("modifiers", {}),
                "research_required": defn.get("research_required"),
            }

        from .colony_systems import SOCIAL_SYSTEMS, POLITICAL_SYSTEMS  # local to avoid top-level circular risk
        systems_block = {
            "social":   {
                **_sys_summary(colony.social_system, SOCIAL_SYSTEMS),
                "last_changed": colony.social_last_changed,
            },
            "economic": {
                **_sys_summary(colony.economic_system, ECONOMIC_SYSTEMS),
                "last_changed":      colony.economic_last_changed,
                "unique_commodity":  econ_def.get("unique_commodity"),
                "commodity_amount":  econ_def.get("commodity_amount", 0),
            },
            "political": {
                **_sys_summary(colony.political_system, POLITICAL_SYSTEMS),
                "last_changed": colony.political_last_changed,
            },
            "coherence_score":      coherence_score,
            "coherence_label":      coherence_label,
            "coherence_multiplier": round(coherence_mult, 2),
        }

        return {
            "planet_name":    colony.planet_name,
            "system_name":    colony.system_name,
            "planet_type":    colony.planet_type,
            "grid_radius":    colony.grid_radius,
            "founded_turn":   colony.founded_turn,
            "population":     colony.population,
            "pop_growth_rate":  round(growth_rate * 100, 2),  # percentage, e.g. 2.4
            "pop_growth_est":   pop_gain_est,                  # colonists added next turn
            "total_production": col_prod,
            "tiles":          tiles_list,
            "tile_count":     len(tiles_list),
            "improvement_count": sum(1 for t in colony.tiles.values() if t.improvement),
            "systems":        systems_block,
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
            # Category comes from the research project that unlocks this building.
            # Free baseline buildings (unlock_required=None) get "Baseline".
            category = _BUILDING_CATEGORY.get(name, "Baseline" if required is None else "Unknown")
            catalogue.append({
                "name":         name,
                "cost":         data["cost"],
                "description":  data["description"],
                "unlock_required": required,
                "unlocked":     unlocked,
                "category":     category,
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
