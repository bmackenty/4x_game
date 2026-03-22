"""
Canonical starship attribute schema.

Attributes are normalised to a 0–100 scale so different sources (components,
research, crew) can be merged without additional bookkeeping.

Only attributes that drive live gameplay mechanics (or the AI/Cognition system
the game is building toward) are listed here.  Placeholder categories have been
removed to keep the player-facing screen readable.
"""

from __future__ import annotations

from typing import Dict, List, Mapping, Sequence

# ---------------------------------------------------------------------------
# Attribute definitions (id -> metadata)
# ---------------------------------------------------------------------------

SHIP_ATTRIBUTE_DEFINITIONS: Dict[str, Dict[str, str]] = {

    # 1. Structural & Physical
    "hull_integrity": {
        "name": "Hull Integrity",
        "description": "Physical resilience and tolerance to damage.",
    },
    "armor_strength": {
        "name": "Armor Strength",
        "description": "Effectiveness at absorbing kinetic and energy impacts.",
    },
    "mass_efficiency": {
        "name": "Mass Efficiency",
        "description": "Optimization of strength relative to vessel mass; governs cargo capacity.",
    },

    # 2. Propulsion & Mobility
    "engine_output": {
        "name": "Engine Output",
        "description": "Total thrust; contributes to jump range.",
    },
    "engine_efficiency": {
        "name": "Engine Efficiency",
        "description": "Energy conversion efficiency; reduces fuel cost per jump.",
    },
    "ftl_jump_capacity": {
        "name": "FTL Jump Capacity",
        "description": "Reach and reliability of faster-than-light transitions; primary driver of jump range.",
    },
    "maneuverability": {
        "name": "Maneuverability",
        "description": "Agility and responsiveness to pilot or AI input.",
    },

    # 3. Power & Energy
    "reactor_output": {
        "name": "Reactor Output",
        "description": "Overall energy generation capability.",
    },
    "energy_storage": {
        "name": "Energy Storage",
        "description": "Reserve capacity within capacitors or etheric wells; governs fuel tank size.",
    },

    # 4. Sensors & Scanning
    "detection_range": {
        "name": "Detection Range",
        "description": "Maximum distance at which objects can be detected on the galaxy map.",
    },
    "scan_resolution": {
        "name": "Scan Resolution",
        "description": "Detail and fidelity of sensor imagery.",
    },
    "etheric_sensitivity": {
        "name": "Etheric Sensitivity",
        "description": "Precision detecting etheric disturbances; secondary driver of sensor range.",
    },

    # 5. AI, Cognition & Sentience
    "ai_processing_power": {
        "name": "AI Processing Power",
        "description": "Computational throughput for autonomous decision-making.",
    },
    "ai_convergence": {
        "name": "AI Convergence",
        "description": "Fusion of digital logic with emergent etheric cognition.",
    },
    "decision_latency": {
        "name": "Decision Latency",
        "description": "Delay between stimulus and AI response.",
    },
    "cognitive_security": {
        "name": "Cognitive Security",
        "description": "Resistance to hacking or etheric intrusion.",
    },
    "ship_sentience": {
        "name": "Ship Sentience",
        "description": "Degree of self-awareness and independent reasoning.",
    },
    "human_ai_symbiosis": {
        "name": "Human–AI Symbiosis",
        "description": "Harmony between human intuition and machine logic.",
    },
    "ethical_constraints": {
        "name": "Ethical Constraints",
        "description": "Adherence to safety and moral protocols.",
    },
    "dream_state_processing": {
        "name": "Dream-State Processing",
        "description": "Off-cycle cognition for creativity and pattern discovery.",
    },
}

# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------

SHIP_ATTRIBUTE_CATEGORIES: List[Dict[str, object]] = [
    {
        "id": "structural",
        "name": "Structural",
        "attributes": [
            "hull_integrity",
            "armor_strength",
            "mass_efficiency",
        ],
    },
    {
        "id": "propulsion",
        "name": "Propulsion",
        "attributes": [
            "engine_output",
            "engine_efficiency",
            "ftl_jump_capacity",
            "maneuverability",
        ],
    },
    {
        "id": "power",
        "name": "Power & Energy",
        "attributes": [
            "reactor_output",
            "energy_storage",
        ],
    },
    {
        "id": "sensors",
        "name": "Sensors",
        "attributes": [
            "detection_range",
            "scan_resolution",
            "etheric_sensitivity",
        ],
    },
    {
        "id": "ai_cognition",
        "name": "AI, Cognition & Sentience",
        "attributes": [
            "ai_processing_power",
            "ai_convergence",
            "decision_latency",
            "cognitive_security",
            "ship_sentience",
            "human_ai_symbiosis",
            "ethical_constraints",
            "dream_state_processing",
        ],
    },
]

# ---------------------------------------------------------------------------
# Convenience exports
# ---------------------------------------------------------------------------

ALL_ATTRIBUTE_IDS: Sequence[str] = tuple(SHIP_ATTRIBUTE_DEFINITIONS.keys())


def get_attribute_metadata(attribute_id: str) -> Mapping[str, str]:
    """Return metadata for a given attribute id."""
    return SHIP_ATTRIBUTE_DEFINITIONS[attribute_id]


def list_attributes_by_category(category_id: str) -> Sequence[str]:
    """Return the attribute ids assigned to a category."""
    for category in SHIP_ATTRIBUTE_CATEGORIES:
        if category["id"] == category_id:
            return tuple(category["attributes"])
    raise KeyError(f"Unknown attribute category: {category_id}")


__all__ = [
    "SHIP_ATTRIBUTE_DEFINITIONS",
    "SHIP_ATTRIBUTE_CATEGORIES",
    "ALL_ATTRIBUTE_IDS",
    "get_attribute_metadata",
    "list_attributes_by_category",
]
