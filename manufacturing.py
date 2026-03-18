"""
Industrial Platforms Database for 4X Galactic Empire Management Game

All manufacturing data is stored in lore/manufacturing.json.
This module loads that file and exposes the same public API as before,
so all existing callers (game.py, etc.) are unaffected.
"""

import json
import pathlib

# ── Load raw data from lore/manufacturing.json ────────────────────────────────
_LORE_PATH = pathlib.Path(__file__).parent / "lore" / "manufacturing.json"

with _LORE_PATH.open(encoding="utf-8") as _f:
    industrial_platforms: dict = json.load(_f)
