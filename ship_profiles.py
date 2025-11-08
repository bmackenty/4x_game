"""
Baseline ship attribute profiles.

This module exports canonical attribute dictionaries keyed by the attribute ids
defined in :mod:`ship_attributes`.  Every value lives on the shared 0–100 scale,
making it safe to merge with component or crew modifiers before clamping.
"""

from __future__ import annotations

from typing import Dict, Mapping

from ship_attributes import ALL_ATTRIBUTE_IDS

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASELINE_ATTRIBUTE_VALUE: float = 30.0

# ---------------------------------------------------------------------------
# Profiles
# ---------------------------------------------------------------------------

BASE_SHIP_PROFILE: Mapping[str, float] = {
    attribute_id: BASELINE_ATTRIBUTE_VALUE for attribute_id in ALL_ATTRIBUTE_IDS
}


def get_base_ship_profile() -> Dict[str, float]:
    """Return a mutable copy of the canonical base ship profile."""

    return dict(BASE_SHIP_PROFILE)


__all__ = [
    "BASELINE_ATTRIBUTE_VALUE",
    "BASE_SHIP_PROFILE",
    "get_base_ship_profile",
]

