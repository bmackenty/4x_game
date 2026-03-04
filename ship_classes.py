"""
Ship class registry.

A ship class defines the role, description, default component loadout, and
slot limits for a vessel.  All logic (profile computation, stat derivation)
lives in ship_builder.py; this file is pure data.

Component names must match the keys in ship_builder.ship_components exactly.
"""

from __future__ import annotations

from typing import Dict, List, Mapping, Optional


SHIP_CLASSES: Dict[str, Dict] = {
    "Pioneer Scout": {
        "display_name": "Pioneer Scout",
        "role": "exploration",
        "description": (
            "A nimble, lightly-armed vessel built for long-range scouting and "
            "first-contact work.  Sacrifices armour for sensor reach and engine agility."
        ),
        "starting_components": {
            "hull":    "Zephyr Skysteel Chassis",
            "engine":  "Whisperstream Coil",
            "weapons": ["Frontier Coilgun Battery"],
            "shields": ["Aurelian Bulwark"],
            "sensors": ["Oracle Crown Array"],
            "support": ["Entropy Sink Array"],
        },
        "slots": {
            "hull": 1, "engine": 1,
            "weapons": 2, "shields": 2,
            "sensors": 3, "support": 2,
        },
    },

    "Free Trader": {
        "display_name": "Free Trader",
        "role": "trade",
        "description": (
            "A dependable mid-range hauler built for profit over prestige.  "
            "Ample cargo space, solid jump range, and just enough firepower to "
            "discourage pirates."
        ),
        "starting_components": {
            "hull":    "Valkyrie Lattice Frame",
            "engine":  "Helios Lance Drive",
            "weapons": ["Frontier Coilgun Battery"],
            "shields": ["Aurelian Bulwark"],
            "sensors": ["Oracle Crown Array"],
            "support": ["Entropy Sink Array"],
        },
        "slots": {
            "hull": 1, "engine": 1,
            "weapons": 2, "shields": 2,
            "sensors": 2, "support": 3,
        },
    },

    "Void Corsair": {
        "display_name": "Void Corsair",
        "role": "combat",
        "description": (
            "A lean warship built for speed and destruction.  Heavy weapons and a "
            "powerful drive, with minimal creature comforts.  Not recommended for "
            "the faint-hearted."
        ),
        "starting_components": {
            "hull":    "Aegis Bastion Hull",
            "engine":  "Drakeheart Furnace",
            "weapons": ["Frontier Coilgun Battery", "Sunlance Array"],
            "shields": ["Aurelian Bulwark"],
            "sensors": ["Oracle Crown Array"],
            "support": ["Entropy Sink Array"],
        },
        "slots": {
            "hull": 1, "engine": 1,
            "weapons": 4, "shields": 3,
            "sensors": 2, "support": 2,
        },
    },

    "Pilgrim Wanderer": {
        "display_name": "Pilgrim Wanderer",
        "role": "hybrid",
        "description": (
            "A self-sufficient vessel of the Free Pilgrim Clans.  Resilient, "
            "adaptable, and beloved by those who call the void home.  Capable in "
            "most situations if rarely exceptional in any."
        ),
        "starting_components": {
            "hull":    "Pilgrim Nomad Superstructure",
            "engine":  "Auric Flux Sails",
            "weapons": ["Frontier Coilgun Battery"],
            "shields": ["Aurelian Bulwark"],
            "sensors": ["Oracle Crown Array"],
            "support": ["Entropy Sink Array"],
        },
        "slots": {
            "hull": 1, "engine": 1,
            "weapons": 2, "shields": 2,
            "sensors": 2, "support": 3,
        },
    },

    "Ghost Wraith": {
        "display_name": "Ghost Wraith",
        "role": "stealth",
        "description": (
            "A wraith-class vessel built to disappear.  Near-zero etheric "
            "signatures and deep-field dampening make it the preferred hull of "
            "spies, smugglers, and Chorus operatives."
        ),
        "starting_components": {
            "hull":    "Eidolon Veil Hull",
            "engine":  "Whisperstream Coil",
            "weapons": ["Frontier Coilgun Battery"],
            "shields": ["Aurelian Bulwark"],
            "sensors": ["Oracle Crown Array"],
            "support": ["Entropy Sink Array"],
        },
        "slots": {
            "hull": 1, "engine": 1,
            "weapons": 2, "shields": 2,
            "sensors": 3, "support": 2,
        },
    },
}

# Keep the old name as an alias so existing imports don't break
ship_classes: Dict[str, Mapping[str, object]] = SHIP_CLASSES  # type: ignore[assignment]


def get_ship_class(name: str) -> Optional[Dict]:
    """Return the ship class definition for *name*, or None if not found."""
    return SHIP_CLASSES.get(name)


def list_ship_classes() -> List[Dict]:
    """Return all ship class definitions as a list."""
    return list(SHIP_CLASSES.values())


def get_starting_components(class_name: str) -> Optional[Dict]:
    """Return the default component loadout for a ship class, or None."""
    cls = SHIP_CLASSES.get(class_name)
    return cls["starting_components"] if cls else None


__all__ = [
    "SHIP_CLASSES",
    "ship_classes",
    "get_ship_class",
    "list_ship_classes",
    "get_starting_components",
]
