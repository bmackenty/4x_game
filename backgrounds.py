"""
Backgrounds for 7019 - Character Creation

All background data is stored in lore/backgrounds.json.
This module loads that file and exposes the same public API as before,
so all existing callers (characters.py, nethack_interface.py, etc.) are unaffected.
"""

import json
import pathlib

# ---------------------------------------------------------------------------
# Load raw data from lore/backgrounds.json
# ---------------------------------------------------------------------------

_LORE_PATH = pathlib.Path(__file__).parent / "lore" / "backgrounds.json"

with _LORE_PATH.open(encoding="utf-8") as _f:
    backgrounds: dict = json.load(_f)

# ---------------------------------------------------------------------------
# Helper functions — pure logic, no data
# ---------------------------------------------------------------------------

def get_background_list() -> list:
    """Return a list of all background names."""
    return list(backgrounds.keys())


def get_background(name: str) -> dict:
    """Return background data by name."""
    return backgrounds.get(name)


def apply_background_bonuses(base_stats: dict, background_name: str) -> dict:
    """Return a copy of base_stats with the named background's stat bonuses applied."""
    if background_name not in backgrounds:
        return base_stats.copy()

    background = backgrounds[background_name]
    bonuses = background.get("stat_bonuses", {})

    # Apply bonuses to a copy so the original is not mutated
    modified_stats = base_stats.copy()
    for stat, bonus in bonuses.items():
        if stat in modified_stats:
            modified_stats[stat] += bonus

    return modified_stats
