"""
colony_systems.py — Social, Economic, and Political system logic.

Data is authoritative in lore/colony_systems.json.  This module loads
that file at import time and exposes the dicts under their original names
so all callers remain unchanged.

System IDs are stable string keys used throughout save data — never rename
an existing ID without a migration.
"""

import json
import pathlib

_SYSTEMS_PATH = pathlib.Path(__file__).parent.parent / "lore" / "colony_systems.json"
_sdata = json.loads(_SYSTEMS_PATH.read_text(encoding="utf-8"))

# ---------------------------------------------------------------------------
# System catalogues — loaded from lore/colony_systems.json
# ---------------------------------------------------------------------------

ECONOMIC_SYSTEMS:  dict = _sdata["economic"]
POLITICAL_SYSTEMS: dict = _sdata["political"]
SOCIAL_SYSTEMS:    dict = _sdata["social"]

# Compatibility pairs: [[system_id_a, system_id_b, score], ...]
# Score +2 = synergy, -2 = friction.  Pairs are order-independent.
COMPATIBILITY_PAIRS: list = _sdata["compatibility_pairs"]

# Coherence score thresholds: [[min_score, label, production_multiplier], ...]
COHERENCE_LEVELS: list = _sdata["coherence_levels"]


# ---------------------------------------------------------------------------
# PUBLIC API
# ---------------------------------------------------------------------------

def _all_systems():
    """Return combined lookup dict across all three categories."""
    combined = {}
    combined.update(ECONOMIC_SYSTEMS)
    combined.update(POLITICAL_SYSTEMS)
    combined.update(SOCIAL_SYSTEMS)
    return combined


def get_system_def(system_id: str) -> dict:
    """Return the definition dict for any system ID, or {} if unknown."""
    return _all_systems().get(system_id, {})


def get_production_modifiers(social: str, economic: str, political: str) -> dict:
    """
    Combine all three systems' modifiers into a single {resource: multiplier}
    dict.  Deltas are additive before being returned as the total multiplier
    (so 1.0 = no change, 1.15 = +15 %).

    Resources returned: minerals, credits, research, food, fleet_points,
    pop_growth, trade_volume, stability, all_production,
    faction_rep_gain, all_diplomacy.
    """
    # Start with identity multipliers (1.0) for every tracked resource.
    resources = [
        "minerals", "credits", "research", "food", "fleet_points",
        "pop_growth", "trade_volume", "all_production",
        "faction_rep_gain", "all_diplomacy",
    ]
    result = {r: 1.0 for r in resources}
    # stability is an additive flat integer, not a multiplier
    result["stability"] = 0

    for system_id in (social, economic, political):
        defn = get_system_def(system_id)
        for key, delta in defn.get("modifiers", {}).items():
            if key == "stability":
                result["stability"] = result.get("stability", 0) + delta
            else:
                result[key] = result.get(key, 1.0) + delta

    return result


def calculate_coherence(social: str, economic: str, political: str) -> tuple:
    """
    Compute the coherence score and return (score: int, label: str, multiplier: float).

    The multiplier is applied to all non-stability production resources in
    calculate_colony_production().
    """
    active = {social, economic, political}
    score = 0
    for id_a, id_b, delta in COMPATIBILITY_PAIRS:
        if id_a in active and id_b in active:
            score += delta

    for threshold, label, multiplier in COHERENCE_LEVELS:
        if score >= threshold:
            return score, label, multiplier

    # Fallback (should not be reached)
    return score, "High Friction", 0.80


def calculate_faction_affinity(
    social: str,
    economic: str,
    political: str,
    faction_prefs: dict,
) -> int:
    """
    Given a faction's preferred system configuration (dict with keys
    preferred_social, preferred_economic, preferred_political), return an
    integer reputation modifier in [-15, +15] representing how compatible
    the colony's systems are with this faction's worldview.

    +5 per matching system category, +0 per mismatch.
    Bonus +0 for faction_affinities fallback handled by caller.
    """
    matches = 0
    if faction_prefs.get("preferred_social")    == social:   matches += 1
    if faction_prefs.get("preferred_economic")  == economic: matches += 1
    if faction_prefs.get("preferred_political") == political: matches += 1

    # 0 → -5,  1 → 0,  2 → +5,  3 → +15
    affinity_map = {0: -5, 1: 0, 2: 5, 3: 15}
    return affinity_map[matches]


def get_available_systems(category: str, completed_research: list) -> list:
    """
    Return a list of system option dicts for the given category
    ('economic', 'political', 'social'), each annotated with lock state.

    Returned dict shape:
        id, name, description, modifiers, unique_commodity (economic only),
        commodity_amount (economic only), locked (bool), lock_reason (str|None),
        faction_affinities (list)
    """
    catalogue = {
        "economic":  ECONOMIC_SYSTEMS,
        "political": POLITICAL_SYSTEMS,
        "social":    SOCIAL_SYSTEMS,
    }.get(category, {})

    options = []
    for sys_id, defn in catalogue.items():
        req = defn.get("research_required")
        locked = bool(req and req not in completed_research)
        entry = {
            "id":                 sys_id,
            "name":               defn["name"],
            "description":        defn["description"],
            "modifiers":          defn.get("modifiers", {}),
            "research_required":  req,
            "locked":             locked,
            "lock_reason":        f"Requires research: {req}" if locked else None,
            "faction_affinities": defn.get("faction_affinities", []),
        }
        if category == "economic":
            entry["unique_commodity"]  = defn.get("unique_commodity")
            entry["commodity_amount"]  = defn.get("commodity_amount", 1)
        options.append(entry)

    return options


# Cooldown in turns before a system can be changed again.
SYSTEM_CHANGE_COOLDOWN = 5
