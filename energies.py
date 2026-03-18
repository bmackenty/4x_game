"""
Energy Types Database for 4X Galactic Empire Management Game
Year 7019 - Celestial Alliance Era

All energy data is stored in lore/energies.json.
This module loads that file and exposes the same public API as before,
so all existing callers (game.py, backend/main.py, etc.) are unaffected.
"""

import json
import pathlib

# ── Load raw data from lore/energies.json ─────────────────────────────────────
_LORE_PATH = pathlib.Path(__file__).parent / "lore" / "energies.json"

with _LORE_PATH.open(encoding="utf-8") as _f:
    _data = json.load(_f)

# ── Public data ────────────────────────────────────────────────────────────────

all_energies: dict = _data["energies"]

# Category name → dict of energy entries, reconstructed from all_energies
energy_categories: dict = {}
for _name, _entry in all_energies.items():
    _cat = _entry.get("category", "Uncategorized")
    energy_categories.setdefault(_cat, {})[_name] = _entry

# Individual category dicts — exposed for callers that import them by name
physical_energies:  dict = energy_categories.get("Physical", {})
mystical_energies:  dict = energy_categories.get("Mystical", {})
psychic_energies:   dict = energy_categories.get("Psychic", {})
exotic_energies:    dict = energy_categories.get("Exotic", {})
utility_energies:   dict = energy_categories.get("Utility", {})
faction_energies:   dict = energy_categories.get("Faction-Specific", {})
chaotic_energies:   dict = energy_categories.get("Chaotic", {})

# ── Helper functions — pure logic, no data ────────────────────────────────────

def get_energy_by_category(category: str) -> dict:
    """Return all energies in a specific category."""
    return energy_categories.get(category, {})


def get_safe_energies() -> dict:
    """Return all energies with a Safe safety level."""
    return {name: data for name, data in all_energies.items()
            if data.get("safety_level") == "Safe"}


def get_dangerous_energies() -> dict:
    """Return all energies with Dangerous, Extremely Dangerous, or Forbidden safety levels."""
    dangerous = {"Dangerous", "Extremely Dangerous", "Forbidden"}
    return {name: data for name, data in all_energies.items()
            if data.get("safety_level") in dangerous}


def get_energy_efficiency(energy_name: str) -> float:
    """Return the efficiency rating of a specific energy type."""
    energy = all_energies.get(energy_name)
    return energy.get("efficiency", 0.5) if energy else 0.5


def get_energy_stability(energy_name: str) -> float:
    """Return the stability rating of a specific energy type."""
    energy = all_energies.get(energy_name)
    return energy.get("stability", 0.5) if energy else 0.5


def get_energy_cost_multiplier(energy_name: str) -> float:
    """Return the cost multiplier for a specific energy type."""
    energy = all_energies.get(energy_name)
    return energy.get("cost_multiplier", 1.0) if energy else 1.0


def get_energy_applications(energy_name: str) -> list:
    """Return the applications for a specific energy type."""
    energy = all_energies.get(energy_name)
    return energy.get("applications", []) if energy else []


def get_energy_safety_level(energy_name: str) -> str:
    """Return the safety level of a specific energy type."""
    energy = all_energies.get(energy_name)
    return energy.get("safety_level", "Unknown") if energy else "Unknown"


def calculate_power_output(energy_name: str, base_power: float) -> float:
    """Return actual power output based on energy efficiency."""
    return base_power * get_energy_efficiency(energy_name)


def calculate_energy_cost(energy_name: str, base_cost: float) -> float:
    """Return actual energy cost based on cost multiplier."""
    return base_cost * get_energy_cost_multiplier(energy_name)


def get_energy_compatibility(ship_type: str, energy_name: str) -> bool:
    """Return whether an energy type is compatible with a ship type."""
    energy = all_energies.get(energy_name)
    if not energy:
        return False
    # Forbidden and extremely dangerous energies are never ship-compatible
    return energy.get("safety_level") not in ("Forbidden", "Extremely Dangerous")


def get_recommended_energies(ship_type: str) -> list:
    """Return up to 5 recommended energy types for a specific ship type."""
    return [
        name for name, data in all_energies.items()
        if data.get("safety_level") == "Safe" and data.get("efficiency", 0) >= 0.7
    ][:5]
