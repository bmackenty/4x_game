"""
Commodities Database for 4X Galactic Empire Management Game

All goods data is stored in lore/goods.json.
This module loads that file and exposes the same public API as before,
so all existing callers (game.py, economy.py, navigation.py, etc.) are unaffected.
"""

import json
import pathlib

# ── Load raw data from lore/goods.json ────────────────────────────────────────
_LORE_PATH = pathlib.Path(__file__).parent / "lore" / "goods.json"

with _LORE_PATH.open(encoding="utf-8") as _f:
    commodities: dict = json.load(_f)
