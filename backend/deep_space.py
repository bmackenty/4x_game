"""
backend/deep_space.py — Deep space object registry.

Manages content that exists in empty hex cells between star systems:
  * Derelict ships  — salvageable wrecks with loot
  * Anomalies       — phenomena that trigger events (hazards, research bonuses)
  * Resource nodes  — harvestable asteroid fields, gas clouds, dark matter pockets
  * Outpost sites   — pre-marked buildable locations (always visible as exploration hooks)

Architecture mirrors ColonyManager:
  - Deterministic seeded generation (same seed → same universe)
  - Serialize/deserialize for save_game integration via game.deep_space_state
  - No engine file dependencies
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Deep space object types and subtypes
# ---------------------------------------------------------------------------

DERELICT_SUBTYPES = [
    "Freighter Wreck",
    "Mining Barge Hull",
    "Exploration Vessel",
    "Military Cruiser Fragment",
    "Ancient Generation Ship",
    "Research Station Debris",
]

ANOMALY_SUBTYPES = [
    "Gravity Well",
    "Quantum Rift",
    "Etheric Resonance Bloom",
    "Dark Matter Vortex",
    "Chrono-Temporal Eddy",
    "Void Crystallisation",
    "Subspace Echo",
    "Magnetar Pulse Zone",
]

RESOURCE_NODE_SUBTYPES = [
    "Asteroid Field",
    "Gas Cloud",
    "Dark Matter Pocket",
    "Crystalline Nebula",
    "Metallic Debris Ring",
    "Exotic Particle Stream",
]

OUTPOST_SITE_SUBTYPES = [
    "Stable Lagrange Point",
    "Ancient Platform Ruins",
    "Naturally Shielded Pocket",
    "Ether-Rich Void",
    "Deep Space Crossroads",
]

# Resources each node type can yield on harvest
RESOURCE_NODE_YIELDS: Dict[str, Dict[str, int]] = {
    "Asteroid Field":        {"minerals": 15, "credits": 500},
    "Gas Cloud":             {"energy_cells": 12, "credits": 400},
    "Dark Matter Pocket":    {"dark_matter": 5,   "credits": 1500},
    "Crystalline Nebula":    {"crystals": 8,      "credits": 800},
    "Metallic Debris Ring":  {"minerals": 10,     "credits": 300},
    "Exotic Particle Stream": {"exotic_particles": 3, "credits": 2000},
}

# Anomaly effects when entered
ANOMALY_EFFECTS: Dict[str, Dict] = {
    "Gravity Well": {
        "description": "Intense gravitational shear — fuel consumption +50% for 2 turns.",
        "fuel_penalty": 0.5,
    },
    "Quantum Rift": {
        "description": "Quantum fluctuations distort instruments. Scanner range −3 for 1 turn.",
        "scan_penalty": 3,
    },
    "Etheric Resonance Bloom": {
        "description": "The ether sings. Etheric systems gain a +10 attribute boost for 1 turn.",
        "research_bonus": "Etheric",
    },
    "Dark Matter Vortex": {
        "description": "Dark matter currents pull at the hull. Jump range −5 until next turn end.",
        "jump_penalty": 5,
    },
    "Chrono-Temporal Eddy": {
        "description": "Time dilates briefly. An extra action point is recovered.",
        "action_bonus": 1,
    },
    "Void Crystallisation": {
        "description": "Crystalline void-matter adheres to the hull. Cargo hold gains +20 temporarily.",
        "cargo_bonus": 20,
    },
    "Subspace Echo": {
        "description": "A ghost transmission — partial star chart of nearby undiscovered systems revealed.",
        "reveal_nearby": True,
    },
    "Magnetar Pulse Zone": {
        "description": "Magnetic pulse disrupts electronics. Shield systems offline for 1 turn.",
        "shield_penalty": True,
    },
}

# Salvage loot tables for derelicts
DERELICT_LOOT: Dict[str, Dict] = {
    "Freighter Wreck":           {"cargo": {"minerals": 8, "food": 5},    "credits": 800},
    "Mining Barge Hull":         {"cargo": {"minerals": 20},              "credits": 400},
    "Exploration Vessel":        {"cargo": {"data_cores": 3},             "credits": 1200},
    "Military Cruiser Fragment": {"cargo": {"alloys": 6},                 "credits": 600},
    "Ancient Generation Ship":   {"cargo": {"artifacts": 2, "data_cores": 5}, "credits": 3000},
    "Research Station Debris":   {"cargo": {"data_cores": 4},             "credits": 1500},
}


# ---------------------------------------------------------------------------
# Data class
# ---------------------------------------------------------------------------

@dataclass
class DeepSpaceObject:
    type: str          # "derelict" | "anomaly" | "resource_node" | "outpost_site"
    hex_q: int
    hex_r: int
    x: float           # 3D game coords (back-projected from hex centre)
    y: float
    z: float
    name: str
    description: str
    subtype: str
    discovered: bool = False
    depleted: bool = False     # resource nodes and derelicts become depleted after use
    data: dict = field(default_factory=dict)   # type-specific payload (loot, effects, etc.)

    def to_dict(self, include_undiscovered_details: bool = False) -> dict:
        """
        Serialise to a frontend-safe dict.

        Undiscovered objects only expose type/position/subtype so the frontend
        can show a generic icon. Discovered objects get the full name/description.
        Outpost sites are always fully exposed to encourage exploration.
        """
        always_visible = self.type == "outpost_site"
        reveal = self.discovered or include_undiscovered_details or always_visible
        return {
            "type":        self.type,
            "hex_q":       self.hex_q,
            "hex_r":       self.hex_r,
            "x":           self.x,
            "y":           self.y,
            "z":           self.z,
            "subtype":     self.subtype,
            "name":        self.name  if reveal else None,
            "description": self.description if reveal else None,
            "discovered":  self.discovered,
            "depleted":    self.depleted,
        }


# ---------------------------------------------------------------------------
# Manager
# ---------------------------------------------------------------------------

class DeepSpaceManager:
    """
    Manages all deep space objects for a game session.

    Generation is seeded from the galaxy seed so the same galaxy always
    produces the same DSO layout, making exploration deterministic and
    shareable between players.
    """

    # Target density: roughly 1 DSO per N empty hexes
    TARGET_DENSITY = 10

    def __init__(self, galaxy_seed: int = 42):
        self._seed = galaxy_seed
        self._objects: Dict[Tuple[int, int], DeepSpaceObject] = {}
        self._generated = False

    # -----------------------------------------------------------------------
    # Generation
    # -----------------------------------------------------------------------

    def generate(self, system_hex_set: set,
                 exclusion_zone: set | None = None) -> None:
        """
        Scatter deep space objects across the hex grid.

        ``system_hex_set``  — (q, r) tuples that have star systems.
        ``exclusion_zone``  — additional (q, r) tuples where DSOs must not
                              be placed (e.g. hexes near the player start).

        Galaxy scale: 500×500 units, GALAXY_SCALE = 12.5 → grid ≈ 40×40 hexes.
        We scan q ∈ [-4, 44], r ∈ [-4, 44] for a small margin around the
        galaxy edge.
        """
        if self._generated:
            return

        rng = random.Random(self._seed + 1)   # offset from base seed
        forbidden = (system_hex_set | (exclusion_zone or set()))

        # The hex bounding box that covers the 500×500 galaxy with margins
        Q_MIN, Q_MAX = -4, 44
        R_MIN, R_MAX = -4, 44

        # Count empty hexes to calibrate how many objects to place
        total_cells = (Q_MAX - Q_MIN + 1) * (R_MAX - R_MIN + 1)
        empty_cells = total_cells - len(system_hex_set)
        target_count = max(80, empty_cells // self.TARGET_DENSITY)

        # Type distribution weights
        type_weights = [
            ("derelict",     0.25),
            ("anomaly",      0.30),
            ("resource_node",0.30),
            ("outpost_site", 0.15),
        ]
        types        = [t for t, _ in type_weights]
        weights      = [w for _, w in type_weights]

        placed = 0
        attempts = 0
        max_attempts = target_count * 20

        while placed < target_count and attempts < max_attempts:
            attempts += 1
            q = rng.randint(Q_MIN, Q_MAX)
            r = rng.randint(R_MIN, R_MAX)
            key = (q, r)

            # Skip if system exists here, in exclusion zone, or DSO already placed
            if key in forbidden or key in self._objects:
                continue

            obj_type = rng.choices(types, weights=weights, k=1)[0]
            obj = self._make_object(rng, obj_type, q, r)
            self._objects[key] = obj
            placed += 1

        self._generated = True

    def _make_object(self, rng: random.Random, obj_type: str, q: int, r: int) -> DeepSpaceObject:
        """Build a single DSO. z is fixed at the galactic midplane (25).

        Coordinate inverse of galaxy_coords_to_hex():
            q = round(x / SCALE)
            r = round(y / SCALE - q / 2)
        →   x = q * SCALE
        →   y = (r + q / 2) * SCALE
        """
        GALAXY_SCALE = 12.5
        x = float(q * GALAXY_SCALE)
        y = float((r + q / 2) * GALAXY_SCALE)
        z = 25.0   # galactic midplane — same default as the frontend hexToGalaxyCoords

        if obj_type == "derelict":
            subtype = rng.choice(DERELICT_SUBTYPES)
            loot = dict(DERELICT_LOOT.get(subtype, {"credits": 500}))
            return DeepSpaceObject(
                type="derelict", hex_q=q, hex_r=r, x=x, y=y, z=z,
                name=f"Derelict {subtype}",
                description=f"A drifting {subtype.lower()} with salvageable materials aboard.",
                subtype=subtype,
                data={"loot": loot},
            )

        if obj_type == "anomaly":
            subtype = rng.choice(ANOMALY_SUBTYPES)
            effect = ANOMALY_EFFECTS.get(subtype, {})
            return DeepSpaceObject(
                type="anomaly", hex_q=q, hex_r=r, x=x, y=y, z=z,
                name=subtype,
                description=effect.get("description", "An unknown spatial phenomenon."),
                subtype=subtype,
                data={"effect": effect},
            )

        if obj_type == "resource_node":
            subtype = rng.choice(RESOURCE_NODE_SUBTYPES)
            yield_data = dict(RESOURCE_NODE_YIELDS.get(subtype, {"credits": 200}))
            return DeepSpaceObject(
                type="resource_node", hex_q=q, hex_r=r, x=x, y=y, z=z,
                name=subtype,
                description=f"A harvestable {subtype.lower()} rich in extractable materials.",
                subtype=subtype,
                data={"yield": yield_data},
            )

        # outpost_site
        subtype = rng.choice(OUTPOST_SITE_SUBTYPES)
        return DeepSpaceObject(
            type="outpost_site", hex_q=q, hex_r=r, x=x, y=y, z=z,
            name=f"Site: {subtype}",
            description=(
                f"A {subtype.lower()} suitable for establishing a deep space outpost. "
                "Survey complete — awaiting construction orders."
            ),
            subtype=subtype,
            data={},
        )

    # -----------------------------------------------------------------------
    # Lookup and mutation
    # -----------------------------------------------------------------------

    def get_at_hex(self, q: int, r: int) -> Optional[DeepSpaceObject]:
        return self._objects.get((q, r))

    def discover(self, q: int, r: int) -> None:
        obj = self._objects.get((q, r))
        if obj:
            obj.discovered = True

    def harvest(self, q: int, r: int) -> Dict:
        """
        Harvest a resource node or salvage a derelict at (q, r).

        Returns the loot dict, marks the object as depleted.
        Raises ValueError if nothing is there or it's already depleted.
        """
        obj = self._objects.get((q, r))
        if not obj:
            raise ValueError("No deep space object at this location.")
        if obj.depleted:
            raise ValueError(f"This {obj.type.replace('_', ' ')} has already been depleted.")
        if obj.type not in ("resource_node", "derelict"):
            raise ValueError(f"Cannot harvest a {obj.type.replace('_', ' ')}.")

        loot_key = "yield" if obj.type == "resource_node" else "loot"
        loot = dict(obj.data.get(loot_key, {}))
        obj.depleted = True
        return loot

    def list_all(self) -> List[DeepSpaceObject]:
        return list(self._objects.values())

    def list_discovered(self) -> List[DeepSpaceObject]:
        return [o for o in self._objects.values() if o.discovered or o.type == "outpost_site"]

    # -----------------------------------------------------------------------
    # Serialisation (save/load)
    # -----------------------------------------------------------------------

    def serialize(self) -> dict:
        """Return a JSON-serialisable dict of all DSO state."""
        return {
            "seed":      self._seed,
            "generated": self._generated,
            "objects": {
                f"{q},{r}": {
                    "type":       o.type,
                    "hex_q":      o.hex_q,
                    "hex_r":      o.hex_r,
                    "x":          o.x,
                    "y":          o.y,
                    "z":          o.z,
                    "name":       o.name,
                    "description":o.description,
                    "subtype":    o.subtype,
                    "discovered": o.discovered,
                    "depleted":   o.depleted,
                    "data":       o.data,
                }
                for (q, r), o in self._objects.items()
            },
        }

    def deserialize(self, data: dict) -> None:
        """Restore DSO state from a serialised dict (after load_game)."""
        if not data:
            return
        self._seed      = data.get("seed", self._seed)
        self._generated = data.get("generated", False)
        self._objects   = {}
        for key, od in data.get("objects", {}).items():
            q, r = map(int, key.split(","))
            self._objects[(q, r)] = DeepSpaceObject(
                type=od["type"],
                hex_q=od["hex_q"],
                hex_r=od["hex_r"],
                x=od["x"],
                y=od["y"],
                z=od["z"],
                name=od["name"],
                description=od["description"],
                subtype=od["subtype"],
                discovered=od.get("discovered", False),
                depleted=od.get("depleted", False),
                data=od.get("data", {}),
            )
