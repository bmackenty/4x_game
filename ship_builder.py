"""
Ship component registry.

Component data lives in ``lore/components.json`` — that file is the single
source of truth for all components, their costs, faction locks, and attribute
modifiers.  This module loads the JSON at import time and exposes the same
internal ``ship_components`` dict that the rest of the codebase expects.
"""

from __future__ import annotations

import json
import os
from math import prod
from typing import Dict, Iterable, Mapping, Optional, Sequence, Tuple

from ship_profiles import get_base_ship_profile
from ship_attributes import ALL_ATTRIBUTE_IDS


# -----------------------------------------------------------------------------
# Attribute helpers
# -----------------------------------------------------------------------------


def empty_attribute_profile(default_value: float = 0.0) -> Dict[str, float]:
    """Return a dict containing every canonical attribute set to ``default_value``."""
    return {attr_id: float(default_value) for attr_id in ALL_ATTRIBUTE_IDS}


def clamp_attribute_profile(profile: Mapping[str, float]) -> Dict[str, float]:
    """Clamp each attribute to the 0–100 range and fill in missing attributes."""
    clamped = empty_attribute_profile()
    for attr_id, value in profile.items():
        if attr_id not in clamped:
            continue
        clamped[attr_id] = max(0.0, min(100.0, float(value)))
    return clamped


def merge_attribute_profiles(profiles: Iterable[Mapping[str, float]]) -> Dict[str, float]:
    """Combine multiple attribute dicts, summing values and clamping to 0–100."""
    merged = empty_attribute_profile()
    for profile in profiles:
        for attr_id, value in profile.items():
            if attr_id not in merged:
                continue
            merged[attr_id] = max(0.0, min(100.0, merged[attr_id] + float(value)))
    return merged


# -----------------------------------------------------------------------------
# Load component registry from lore/components.json
# -----------------------------------------------------------------------------


def _load_components() -> Dict[str, Dict[str, Mapping[str, object]]]:
    """
    Load components from lore/components.json and convert to the internal format:
        {category: {component_name: component_data}}

    The JSON ``modifiers`` field is exposed as ``attributes`` so existing
    helpers (compute_ship_profile, etc.) work without changes.
    Unknown modifier keys (attributes not in ship_attributes.py) are silently
    ignored by the merge helpers.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "lore", "components.json")
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    result: Dict[str, Dict[str, Mapping[str, object]]] = {}
    for category, entries in raw.items():
        if category.startswith("_"):   # skip comment keys
            continue
        if not isinstance(entries, list):
            continue
        catalog: Dict[str, Mapping[str, object]] = {}
        for entry in entries:
            name = entry.get("name")
            if not name:
                continue
            catalog[name] = {
                "cost":           entry.get("cost", 0),
                "faction_lock":   entry.get("faction_lock"),
                "failure_chance": entry.get("failure_chance", 0.0),
                "lore":           entry.get("lore", ""),
                # expose modifiers as attributes so merge helpers work
                "attributes":     {k: float(v) for k, v in entry.get("modifiers", {}).items()},
            }
        result[category] = catalog
    return result


ship_components: Dict[str, Dict[str, Mapping[str, object]]] = _load_components()

ship_templates: Dict[str, Mapping[str, object]] = {}

COMPONENT_CATEGORY_ALIASES: Dict[str, str] = {
    "hull":        "hulls",
    "hulls":       "hulls",
    "engine":      "engines",
    "engines":     "engines",
    "power":       "power_cores",
    "power_cores": "power_cores",
    "sensor":      "sensors",
    "sensors":     "sensors",
    "ai":          "ai_cores",
    "ai_cores":    "ai_cores",
    # Legacy aliases kept so old save data doesn't crash
    "weapons":         "weapons",
    "weapon":          "weapons",
    "shields":         "shields",
    "shield":          "shields",
    "support":         "support",
    "computing":       "computing",
    "communications":  "communications",
    "crew_modules":    "crew_modules",
    "crew":            "crew_modules",
}

COMPONENT_CATEGORY_LABELS: Dict[str, str] = {
    "hulls":       "Hull",
    "engines":     "Engine",
    "power_cores": "Power Core",
    "sensors":     "Sensor Suite",
    "ai_cores":    "AI Core",
}

# Active categories (used to populate the ship screen)
ACTIVE_CATEGORIES = ("hulls", "engines", "power_cores", "sensors", "ai_cores")


# -----------------------------------------------------------------------------
# Internal helpers
# -----------------------------------------------------------------------------


def _normalize_component_names(component_config: Mapping[str, object]) -> Sequence[Tuple[str, str]]:
    normalized: list[Tuple[str, str]] = []
    for key, value in component_config.items():
        category = COMPONENT_CATEGORY_ALIASES.get(key)
        if not category:
            continue
        catalog = ship_components.get(category)
        if not catalog:
            continue

        if isinstance(value, str):
            names = [value]
        elif isinstance(value, Iterable):
            names = [item for item in value if isinstance(item, str)]
        else:
            continue

        for name in names:
            if name in catalog:
                normalized.append((category, name))
    return normalized


def collect_component_entries(component_config: Mapping[str, object]) -> Sequence[Mapping[str, object]]:
    entries = []
    for category, name in _normalize_component_names(component_config):
        catalog = ship_components.get(category, {})
        data = catalog.get(name)
        if not data:
            continue
        entries.append(
            {
                "category": category,
                "name":     name,
                "label":    COMPONENT_CATEGORY_LABELS.get(category, category.title()),
                "data":     data,
            }
        )
    return entries


def compute_ship_profile(component_config: Mapping[str, object]) -> Dict[str, float]:
    profiles = [get_base_ship_profile()]
    for entry in collect_component_entries(component_config):
        attributes = entry["data"].get("attributes", {})
        if attributes:
            profiles.append(attributes)
    return clamp_attribute_profile(merge_attribute_profiles(profiles))


def aggregate_component_metadata(component_config: Mapping[str, object]) -> Mapping[str, object]:
    entries = collect_component_entries(component_config)
    total_cost = 0.0
    failure_terms: list[float] = []
    faction_locks: set[str] = set()

    for entry in entries:
        data = entry["data"]
        total_cost += float(data.get("cost", 0.0) or 0.0)
        chance = data.get("failure_chance")
        if isinstance(chance, (int, float)):
            failure_terms.append(1.0 - max(0.0, min(1.0, float(chance))))
        lock = data.get("faction_lock")
        if lock:
            if isinstance(lock, str):
                faction_locks.add(lock)
            elif isinstance(lock, Iterable):
                for faction in lock:
                    if isinstance(faction, str):
                        faction_locks.add(faction)

    combined_failure = 1.0 - prod(failure_terms) if failure_terms else 0.0

    return {
        "total_cost":              total_cost,
        "combined_failure_chance": combined_failure,
        "faction_locks":           sorted(faction_locks),
        "entries":                 entries,
    }


# -----------------------------------------------------------------------------
# Power usage scaffolding (placeholder).
# -----------------------------------------------------------------------------


def calculate_power_usage(_components: Mapping[str, object]) -> Dict[str, float]:
    return {
        "power_output":     0.0,
        "power_used":       0.0,
        "power_available":  0.0,
        "power_percentage": 0.0,
    }


def calculate_ship_stats(components: Mapping[str, object]) -> Dict[str, object]:
    """Backwards-compatible helper retained for callers in game."""
    profile  = compute_ship_profile(components)
    metadata = aggregate_component_metadata(components)

    health      = max(100, int(profile.get("hull_integrity", 30.0) * 10))
    cargo_space = max(30,  int(profile.get("mass_efficiency", 30.0) * 3 + profile.get("hull_integrity", 30.0)))
    speed       = max(1.0, profile.get("engine_output", 30.0) / 10.0 + profile.get("maneuverability", 30.0) / 12.0)

    return {
        "profile":     profile,
        "metadata":    metadata,
        "health":      health,
        "cargo_space": cargo_space,
        "speed":       speed,
        "total_cost":  metadata.get("total_cost", 0.0),
    }


# -----------------------------------------------------------------------------
# Shipyard functions — querying available components
# -----------------------------------------------------------------------------


def get_available_components(category: str, ship=None, player_faction: Optional[str] = None) -> Dict[str, Mapping[str, object]]:
    """
    Return components for ``category``, optionally filtered by faction locks.
    Only components in ACTIVE_CATEGORIES are returned; legacy categories return
    an empty dict.
    """
    resolved = COMPONENT_CATEGORY_ALIASES.get(category, category)
    if resolved not in ACTIVE_CATEGORIES:
        return {}
    catalog = ship_components.get(resolved, {})
    if not catalog:
        return {}

    if not player_faction:
        return catalog

    available = {}
    for name, data in catalog.items():
        lock = data.get("faction_lock")
        if lock is None:
            available[name] = data
        elif isinstance(lock, str) and lock == player_faction:
            available[name] = data
        elif isinstance(lock, list) and player_faction in lock:
            available[name] = data
    return available


def can_install_component(ship, category: str, component_name: str, player_faction: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """Check whether a component can be installed (faction check only; shipyard check is at API level)."""
    resolved = COMPONENT_CATEGORY_ALIASES.get(category, category)
    catalog = ship_components.get(resolved, {})
    if component_name not in catalog:
        return False, f"Component '{component_name}' not found in category '{category}'"

    lock = catalog[component_name].get("faction_lock")
    if lock and player_faction:
        if isinstance(lock, str) and lock != player_faction:
            return False, f"Component requires faction: {lock}"
        if isinstance(lock, list) and player_faction not in lock:
            return False, f"Component requires one of factions: {', '.join(lock)}"

    return True, None


def install_component(ship, category: str, component_name: str, player_faction: Optional[str] = None) -> Tuple[bool, str]:
    """Install a component on a ship (called only from a shipyard context)."""
    can, error = can_install_component(ship, category, component_name, player_faction)
    if not can:
        return False, error or "Cannot install component"

    if not hasattr(ship, "components"):
        ship.components = {}

    category_key = COMPONENT_CATEGORY_ALIASES.get(category, category)
    ship.components[category_key] = component_name

    if hasattr(ship, "calculate_stats_from_components"):
        ship.calculate_stats_from_components()

    return True, f"Installed {component_name}"


def remove_component(ship, category: str, component_name: str) -> Tuple[bool, str]:
    """Remove a component from a ship."""
    if not hasattr(ship, "components"):
        return False, "Ship has no components"

    category_key = COMPONENT_CATEGORY_ALIASES.get(category, category)
    if ship.components.get(category_key) == component_name:
        ship.components[category_key] = None
        if hasattr(ship, "calculate_stats_from_components"):
            ship.calculate_stats_from_components()
        return True, f"Removed {component_name}"

    return False, f"Component {component_name} not installed"


def calculate_upgrade_cost(ship, new_components: Mapping[str, object], player_faction: Optional[str] = None) -> Tuple[float, Dict[str, float]]:
    """Calculate the credit cost to swap in new components."""
    current = getattr(ship, "components", {}).copy() if hasattr(ship, "components") else {}
    total_cost = 0.0
    breakdown: Dict[str, float] = {}

    for cat in ACTIVE_CATEGORIES:
        new_val     = new_components.get(cat)
        current_val = current.get(cat)
        if new_val == current_val or not new_val:
            continue
        data = ship_components.get(cat, {}).get(new_val)
        if data:
            cost = float(data.get("cost", 0.0) or 0.0)
            breakdown[cat] = cost
            total_cost += cost

    return total_cost, breakdown


__all__ = [
    "ship_components",
    "ship_templates",
    "COMPONENT_CATEGORY_ALIASES",
    "COMPONENT_CATEGORY_LABELS",
    "ACTIVE_CATEGORIES",
    "empty_attribute_profile",
    "clamp_attribute_profile",
    "merge_attribute_profiles",
    "collect_component_entries",
    "compute_ship_profile",
    "aggregate_component_metadata",
    "calculate_power_usage",
    "calculate_ship_stats",
    "get_available_components",
    "can_install_component",
    "install_component",
    "remove_component",
    "calculate_upgrade_cost",
]
