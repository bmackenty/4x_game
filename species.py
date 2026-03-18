"""
Species Database for 4X Galactic Empire Management Game
Year 7019 - Celestial Alliance Era

All species data is stored in lore/species.json.
This module loads that file and exposes the same public API as before,
so all existing callers (game.py, backend/main.py, etc.) are unaffected.
"""

import json
import pathlib

# ── Load raw data from lore/species.json ──────────────────────────────────────
_LORE_PATH = pathlib.Path(__file__).parent / "lore" / "species.json"

with _LORE_PATH.open(encoding="utf-8") as _f:
    species_database: dict = json.load(_f)

# ── Helper functions — pure logic, no data ────────────────────────────────────

def get_playable_species() -> dict:
    """Return only the species that can be played by the player."""
    return {name: data for name, data in species_database.items() if data.get("playable", False)}


def get_species_by_category(category: str) -> dict:
    """Return all species in a specific category."""
    return {name: data for name, data in species_database.items() if data.get("category") == category}


def get_allied_species() -> dict:
    """Return all species that are allied with the Celestial Alliance."""
    allied_statuses = {"Founding member", "Allied member", "Advanced ally", "Refugee member"}
    return {name: data for name, data in species_database.items()
            if data.get("alliance_status") in allied_statuses}


def get_species_info(species_name: str) -> dict | None:
    """Return detailed information about a specific species."""
    return species_database.get(species_name, None)


def get_species_traits(species_name: str) -> list:
    """Return the special traits of a specific species."""
    species = species_database.get(species_name)
    return species.get("special_traits", []) if species else []


def get_species_diplomacy_modifier(species_name: str) -> float:
    """Return the diplomacy modifier for a specific species."""
    species = species_database.get(species_name)
    return species.get("diplomacy_modifier", 0.0) if species else 0.0
