"""
Services Database for 4X Galactic Empire Management Game

All services data is stored in lore/services.json.
This module loads that file and exposes the same public API as before,
so all existing callers are unaffected.
"""

import json
import pathlib

# ── Load raw data from lore/services.json ─────────────────────────────────────
_LORE_PATH = pathlib.Path(__file__).parent / "lore" / "services.json"

with _LORE_PATH.open(encoding="utf-8") as _f:
    services: dict = json.load(_f)
