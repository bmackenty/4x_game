"""
Research Fields Database for 4X Galactic Empire Management Game
Year 7019 - Celestial Alliance Era

All research data is stored in lore/research.json.
This module loads that file and exposes the same public API as before,
so all existing callers (game.py, backend/main.py, etc.) are unaffected.
"""

import json
import pathlib

# ---------------------------------------------------------------------------
# Load raw data from lore/research.json
# ---------------------------------------------------------------------------

_LORE_PATH = pathlib.Path(__file__).parent / "lore" / "research.json"

with _LORE_PATH.open(encoding="utf-8") as _f:
    _data = json.load(_f)

# ---------------------------------------------------------------------------
# Public data: all research entries merged into one flat dict
# ---------------------------------------------------------------------------

all_research: dict = _data["research"]

# ---------------------------------------------------------------------------
# Research path → full category name mapping
# (e.g. "Quantum" → "Quantum and Transdimensional")
# ---------------------------------------------------------------------------

RESEARCH_PATH_CATEGORIES: dict = _data["path_categories"]

# ---------------------------------------------------------------------------
# Extended gameplay unlock IDs
# Maps research name → category → list of unlock IDs.
# Used for UI display and as feature gates in future systems.
# ---------------------------------------------------------------------------

EXTENDED_UNLOCKS: dict = _data["extended_unlocks"]

# ---------------------------------------------------------------------------
# Research categories: maps full category name → dict of research entries.
# Reconstructed from all_research so the JSON stays the single source of truth.
# ---------------------------------------------------------------------------

research_categories: dict = {}
for _name, _entry in all_research.items():
    _cat = _entry.get("category", "Uncategorized")
    research_categories.setdefault(_cat, {})[_name] = _entry

# ---------------------------------------------------------------------------
# Helper functions — pure logic, no data
# ---------------------------------------------------------------------------

def get_research_by_category(category: str) -> dict:
    """Return all research entries in a given category."""
    return research_categories.get(category, {})


def get_research_by_difficulty(min_diff: int, max_diff: int) -> dict:
    """Return research entries whose difficulty falls within [min_diff, max_diff]."""
    return {
        name: data
        for name, data in all_research.items()
        if min_diff <= data.get("difficulty", 0) <= max_diff
    }


def get_affordable_research(available_credits: int) -> dict:
    """Return research entries whose cost is within available_credits."""
    return {
        name: data
        for name, data in all_research.items()
        if data.get("research_cost", 0) <= available_credits
    }


def get_research_info(research_name: str) -> dict:
    """Return the full data dict for a single research entry."""
    return all_research.get(research_name, {})


def get_research_prerequisites(research_name: str) -> list:
    """Return the prerequisites list for a research entry."""
    research = all_research.get(research_name)
    return research.get("prerequisites", []) if research else []


def get_research_unlocks(research_name: str) -> list:
    """Return the unlocks list for a research entry."""
    research = all_research.get(research_name)
    return research.get("unlocks", []) if research else []


def get_related_energy(research_name: str) -> str:
    """Return the energy type related to a research entry."""
    research = all_research.get(research_name)
    return research.get("related_energy", "Unknown") if research else "Unknown"


def calculate_research_progress(days_spent: int, total_days: int) -> float:
    """Return research progress as a percentage (0–100)."""
    return min(100, (days_spent / total_days) * 100) if total_days > 0 else 0


def get_available_research(completed_research) -> dict:
    """Return research entries whose prerequisites are all in completed_research."""
    available = {}
    for name, data in all_research.items():
        prerequisites = data.get("prerequisites", [])
        if all(prereq in completed_research for prereq in prerequisites):
            available[name] = data
    return available
