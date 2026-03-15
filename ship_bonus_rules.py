"""
Ship attribute bonus rules.

This module defines the three bonus layers that are applied on top of the
component-derived attribute profile:

  1. Research bonuses  — completed research grants ship attribute deltas.
  2. Faction bonuses   — the player's home-faction focus adds passive bonuses.
  3. Character-stat bonuses — the player's VIT/KIN/INT/AEF/COH/INF/SYN stats
     translate into small ship attribute improvements.

None of these tables touch the engine files.  They are merged into the profile
computed by ``ship_builder.compute_ship_profile`` before the legacy engine
properties (jump_range, max_fuel, max_cargo, scan_range) are re-derived.

Bonus values use the same 0–100 attribute scale as the rest of the system.
The caller is responsible for clamping the final profile to [0, 100].
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# 1. Research → ship attribute bonuses
#    Keys match the research names returned by game.completed_research.
#    Values are partial attribute dicts (only non-zero deltas need listing).
# ---------------------------------------------------------------------------

RESEARCH_SHIP_BONUSES: Dict[str, Dict[str, float]] = {
    # ----- ship_technologies -----------------------------------------------
    "Fusion Technology": {
        "reactor_output": 4.0,
        "energy_storage": 3.0,
        "flux_stability": 2.0,
    },
    "Plasma Physics": {
        "weapon_power": 4.0,
        "engine_output": 3.0,
        "thermal_regulation": 2.0,
    },
    "Etheric Manipulation": {
        "etheric_sensitivity": 5.0,
        "ether_machine_harmony": 4.0,
        "etheric_channel_conductivity": 3.0,
    },
    "Graviton Physics": {
        "gravitic_stability": 5.0,
        "ftl_jump_capacity": 3.0,
        "space_ship_coherence": 2.0,
    },
    "Quantum Mechanics": {
        "ai_processing_power": 4.0,
        "quantum_compute_efficiency": 4.0,
        "computational_core_integrity": 2.0,
    },
    "Particle Physics": {
        "weapon_power": 3.0,
        "shield_modulation": 3.0,
        "ammo_energy_sustainment": 2.0,
    },
    "Temporal Manipulation": {
        "chrono_adaptability": 5.0,
        "ftl_jump_capacity": 4.0,
        "chrono_symphony": 3.0,
    },
    "Nanotechnology": {
        "damage_control_automation": 5.0,
        "hull_integrity": 3.0,
        "maintenance_autonomy": 4.0,
    },
    "Dark Matter Research": {
        "ftl_jump_capacity": 4.0,
        "detection_range": 3.0,
        "mass_efficiency": 3.0,
    },
    "Subspace Navigation": {
        "ftl_jump_capacity": 6.0,
        "engine_output": 3.0,
        "engine_efficiency": 3.0,
    },
    "Bio-Engineering": {
        "life_support_robustness": 5.0,
        "crew_efficiency": 4.0,
        "crew_morale": 3.0,
    },
    "Cloaking Technology": {
        "signature_dampening": 8.0,
        "thermal_signature": -6.0,
        "electromagnetic_signature": -6.0,
        "radar_lidar_cross_section": -5.0,
        "sensor_discipline": 4.0,
    },
    "Advanced Research": {
        "ai_processing_power": 5.0,
        "scan_resolution": 4.0,
        "predictive_modeling_depth": 3.0,
    },

    # ----- quantum_sciences ------------------------------------------------
    "Quantum Temporal Dynamics": {
        "chrono_adaptability": 6.0,
        "ftl_jump_capacity": 4.0,
        "chrono_symphony": 3.0,
    },
    "Multiverse Navigation": {
        "ftl_jump_capacity": 8.0,
        "gravitic_stability": 5.0,
        "engine_output": 3.0,
    },
    "Quantum Superposition Existentialism": {
        "ai_processing_power": 4.0,
        "cognitive_security": 4.0,
        "ai_convergence": 3.0,
    },
    "Causal Integrity Theory": {
        "coherence_entropy": -5.0,
        "space_ship_coherence": 5.0,
        "information_integrity": 4.0,
    },
    "Temporal Resonance Engineering": {
        "chrono_adaptability": 7.0,
        "chrono_symphony": 5.0,
        "ftl_jump_capacity": 3.0,
    },
    "Spacetime Filament Studies": {
        "ftl_jump_capacity": 6.0,
        "engine_output": 4.0,
        "gravitic_stability": 3.0,
    },
    "Null Space Exploration": {
        "ftl_jump_capacity": 5.0,
        "sensor_discipline": 4.0,
        "signature_dampening": 3.0,
    },
    "Timefold Catalysis": {
        "chrono_adaptability": 8.0,
        "ftl_jump_capacity": 5.0,
        "chrono_symphony": 4.0,
    },
    "Chrono-Synthetic Energy Engineering": {
        "chrono_adaptability": 5.0,
        "reactor_output": 4.0,
        "energy_storage": 4.0,
    },
    "Temporal Entropy Compression": {
        "chrono_symphony": 6.0,
        "flux_stability": 5.0,
        "coherence_entropy": -4.0,
    },

    # ----- etheric_sciences ------------------------------------------------
    "Advanced Etheric Weaving": {
        "etheric_sensitivity": 7.0,
        "ether_machine_harmony": 5.0,
        "ai_ether_integration": 4.0,
    },
    "Dark Energy and Negative Mass Mechanics": {
        "ftl_jump_capacity": 8.0,
        "gravitic_stability": 6.0,
        "mass_efficiency": 4.0,
    },
    "Etheric Gravitational Synthesis": {
        "gravitic_stability": 7.0,
        "ftl_jump_capacity": 5.0,
        "ether_machine_harmony": 3.0,
    },
    "Primordial Ether Research": {
        "etheric_sensitivity": 6.0,
        "resonance_stability": 5.0,
        "etheric_channel_conductivity": 3.0,
    },
    "Stellar Ethereal Symbiosis": {
        "ether_machine_harmony": 6.0,
        "resonance_stability": 5.0,
        "etheric_sensitivity": 4.0,
    },
    "Cosmic Entropy Reversal": {
        "coherence_entropy": -8.0,
        "harmonic_feedback_control": 6.0,
        "resonance_stability": 4.0,
    },
    "Hyperluminal Drift Analysis": {
        "ftl_jump_capacity": 7.0,
        "engine_efficiency": 4.0,
        "gravitic_stability": 3.0,
    },
    "Exo-Energy Biomes": {
        "energy_storage": 5.0,
        "environmental_resilience": 4.0,
        "reactor_output": 3.0,
    },
    "Dimensional Energy Confluence": {
        "reactor_output": 5.0,
        "energy_storage": 6.0,
        "etheric_channel_conductivity": 5.0,
    },
    "Void-Energy State Propagation": {
        "etheric_signature": -5.0,
        "signature_dampening": 5.0,
        "etheric_sensitivity": 5.0,
    },

    # ----- engineering_sciences --------------------------------------------
    "Sentient Architecture": {
        "ship_sentience": 6.0,
        "material_consciousness_resonance": 5.0,
        "human_ai_symbiosis": 3.0,
    },
    "Quantum Crystalized Matter Engineering": {
        "hull_integrity": 6.0,
        "armor_strength": 5.0,
        "mass_efficiency": 4.0,
    },
    "Zero-Point Energy Architecture": {
        "reactor_output": 6.0,
        "energy_storage": 5.0,
        "power_distribution_efficiency": 4.0,
    },
    "Reactive Etheric Constructs": {
        "damage_control_automation": 5.0,
        "hull_integrity": 4.0,
        "resonance_stability": 3.0,
    },
    "Microcosmic Engine Design": {
        "engine_efficiency": 6.0,
        "engine_output": 5.0,
        "mass_efficiency": 4.0,
    },
    "Quantum Tectonics": {
        "hull_integrity": 5.0,
        "structural_redundancy": 6.0,
        "armor_strength": 4.0,
    },
    "Frictionless Energy Systems": {
        "engine_efficiency": 7.0,
        "power_distribution_efficiency": 5.0,
        "thermal_regulation": 3.0,
    },
    "Antimatter Field Containment Dynamics": {
        "reactor_output": 7.0,
        "flux_stability": 6.0,
        "energy_storage": 5.0,
    },
    "Flux-Driven Systems Engineering": {
        "flux_stability": 6.0,
        "flux_tolerance": 5.0,
        "engine_output": 4.0,
    },
    "Resonant Consciousness Tuning": {
        "human_ai_symbiosis": 6.0,
        "cognitive_resonance": 5.0,
        "ship_sentience": 4.0,
    },
    "Phase-Aligned Harmonic Construction": {
        "resonance_stability": 6.0,
        "harmonic_feedback_control": 5.0,
        "ether_machine_harmony": 4.0,
    },
    "Etheric-Mechanical Integration": {
        "ether_machine_harmony": 7.0,
        "etheric_channel_conductivity": 6.0,
        "ai_ether_integration": 5.0,
    },
    "Etheric Drive Harmonics": {
        "engine_output": 6.0,
        "ftl_jump_capacity": 5.0,
        "etheric_channel_conductivity": 5.0,
    },
    "Programmable Matter Synthesis": {
        "adaptation_index": 5.0,
        "mass_efficiency": 4.0,
        "maintenance_autonomy": 4.0,
    },
    "Resonant Frequency Manufacturing": {
        "structural_redundancy": 5.0,
        "resonance_stability": 5.0,
        "hull_integrity": 3.0,
    },
    "Morphic Alloy Engineering": {
        "hull_integrity": 5.0,
        "damage_control_automation": 6.0,
        "adaptation_index": 4.0,
    },
    "Etheric Superstructure Weaving": {
        "hull_integrity": 7.0,
        "material_consciousness_resonance": 6.0,
        "ether_machine_harmony": 4.0,
    },
    "Nanostructural Etheric Weaving": {
        "structural_redundancy": 6.0,
        "maintenance_autonomy": 5.0,
        "hull_integrity": 4.0,
    },
    "Vortex Energy Capture": {
        "energy_storage": 6.0,
        "reactor_output": 4.0,
        "etheric_channel_conductivity": 4.0,
    },
    "Sympathetic Resonance Bridging": {
        "resonance_stability": 5.0,
        "ether_machine_harmony": 5.0,
        "fleet_synchronization": 4.0,
    },
    "Living Metal Cultivation": {
        "hull_integrity": 6.0,
        "damage_control_automation": 7.0,
        "adaptation_index": 5.0,
    },
    "Adaptive Quantum Infrastructure": {
        "adaptation_index": 6.0,
        "self_optimization_capacity": 5.0,
        "quantum_compute_efficiency": 4.0,
    },
    "Chrono-Tempered Materials": {
        "hull_integrity": 5.0,
        "chrono_adaptability": 4.0,
        "material_consciousness_resonance": 4.0,
    },
    "Coherent Matter Projection": {
        "space_ship_coherence": 6.0,
        "coherence_entropy": -5.0,
        "gravitic_stability": 4.0,
    },
    "Compressed Spacetime Scaffolding": {
        "mass_efficiency": 6.0,
        "ftl_jump_capacity": 5.0,
        "structural_redundancy": 4.0,
    },
    "Void Architecture": {
        "signature_dampening": 6.0,
        "etheric_signature": -5.0,
        "environmental_resilience": 5.0,
    },

    # ----- computational_sciences ------------------------------------------
    "Hyperdimensional Simulation Theory": {
        "predictive_modeling_depth": 6.0,
        "causal_mapping_precision": 5.0,
        "fire_control_intelligence": 3.0,
    },
    "Quantum Algorithmic Foreknowledge": {
        "predictive_modeling_depth": 7.0,
        "fire_control_intelligence": 5.0,
        "targeting_speed": 3.0,
    },
    "Self-Evolving Computation": {
        "self_optimization_capacity": 7.0,
        "ai_processing_power": 5.0,
        "adaptation_index": 3.0,
    },
    "Etheric Network Consciousness": {
        "etheric_channeling_index": 6.0,
        "parallel_synchrony": 5.0,
        "cognitive_resonance": 4.0,
    },
    "Universal Constants Variance Mapping": {
        "causal_mapping_precision": 6.0,
        "scan_resolution": 5.0,
        "detection_range": 3.0,
    },
    "Multiversal Probability Analysis": {
        "predictive_modeling_depth": 6.0,
        "fire_control_intelligence": 4.0,
        "causal_mapping_precision": 4.0,
    },

    # ----- consciousness_sciences ------------------------------------------
    "Collective Metaconsciousness Networks": {
        "fleet_synchronization": 6.0,
        "human_ai_symbiosis": 5.0,
        "command_feedback_clarity": 3.0,
    },
    "Quantum Soul Theory": {
        "ship_sentience": 7.0,
        "dream_state_processing": 5.0,
        "ai_convergence": 3.0,
    },
    "Dimensional Awareness Studies": {
        "detection_range": 5.0,
        "etheric_sensitivity": 5.0,
        "scan_resolution": 4.0,
    },
    "Threshold Consciousness Research": {
        "ship_sentience": 5.0,
        "cognitive_security": 5.0,
        "ethical_constraints": 3.0,
    },
    "Artificial Existence Cultivation": {
        "ai_convergence": 6.0,
        "ship_sentience": 5.0,
        "ai_processing_power": 4.0,
    },
    "Symbiotic Existential Anchors": {
        "human_ai_symbiosis": 6.0,
        "space_ship_coherence": 5.0,
        "psycho_etheric_resonance": 3.0,
    },
    "Nonlinear Identity Dynamics": {
        "cognitive_security": 5.0,
        "ai_convergence": 5.0,
        "decision_latency": -3.0,
    },
    "Noetic Energy Channeling": {
        "etheric_sensitivity": 6.0,
        "psycho_etheric_resonance": 5.0,
        "ether_machine_harmony": 3.0,
    },
    "Cognitive Thermodynamics": {
        "decision_latency": -5.0,
        "cognitive_security": 4.0,
        "ai_processing_power": 3.0,
    },
    "Memory-Energy Conversion Studies": {
        "energy_storage": 4.0,
        "ai_processing_power": 4.0,
        "dream_state_processing": 4.0,
    },

    # ----- medical_sciences ------------------------------------------------
    "Etheric Regeneration Therapy": {
        "crew_morale": 5.0,
        "life_support_robustness": 5.0,
        "psycho_etheric_resonance": 4.0,
    },
    "Immortality Stasis Protocols": {
        "life_support_robustness": 7.0,
        "crew_efficiency": 4.0,
        "automation_level": 3.0,
    },
    "Multidimensional Pathogen Research": {
        "environmental_resilience": 5.0,
        "life_support_robustness": 4.0,
        "crew_efficiency": 3.0,
    },
    "Post-Mortality Cognitive Preservation": {
        "crew_efficiency": 5.0,
        "automation_level": 4.0,
        "cognitive_security": 3.0,
    },
    "Lightform Synthesis Medicine": {
        "psycho_etheric_resonance": 6.0,
        "crew_morale": 5.0,
        "life_support_robustness": 3.0,
    },

    # ----- philosophical_sciences ------------------------------------------
    "Post-Temporal Ethics": {
        "ethical_constraints": 5.0,
        "cognitive_security": 4.0,
        "human_ai_symbiosis": 3.0,
    },
    "Multiversal Diplomacy": {
        "fleet_synchronization": 5.0,
        "protocol_interoperability": 5.0,
        "information_security": 3.0,
    },
    "Synthetic Sentience Rights": {
        "human_ai_symbiosis": 5.0,
        "ethical_constraints": 5.0,
        "ship_sentience": 3.0,
    },
    "Inter-species Moral Entanglement": {
        "protocol_interoperability": 6.0,
        "information_security": 4.0,
        "fleet_synchronization": 3.0,
    },
    "Existential Compression Studies": {
        "coherence_entropy": -4.0,
        "space_ship_coherence": 4.0,
        "flux_tolerance": 3.0,
    },
    "Energetic Consent Theory": {
        "human_ai_symbiosis": 4.0,
        "ethical_constraints": 4.0,
        "cognitive_security": 3.0,
    },
    "The Energy-Self Continuum": {
        "ether_machine_harmony": 5.0,
        "psycho_etheric_resonance": 4.0,
        "resonance_stability": 3.0,
    },

    # ----- planetary_sciences ----------------------------------------------
    "Planetary Rejuvenation Protocols": {
        "environmental_resilience": 5.0,
        "scientific_instrumentation": 5.0,
        "life_support_robustness": 3.0,
    },
    "Artificial Stellar Ignition": {
        "reactor_output": 6.0,
        "energy_storage": 5.0,
        "thermal_regulation": 3.0,
    },
    "Astro-Geological Terraforming": {
        "environmental_resilience": 5.0,
        "scientific_instrumentation": 4.0,
        "reality_anchoring_strength": 3.0,
    },
    "Black Hole Stabilization": {
        "gravitic_stability": 7.0,
        "space_ship_coherence": 5.0,
        "reality_anchoring_strength": 5.0,
    },
    "Star-Shepherding Operations": {
        "environmental_resilience": 6.0,
        "reality_anchoring_strength": 5.0,
        "gravitic_stability": 3.0,
    },
    "Interstellar Microbiome Studies": {
        "environmental_resilience": 4.0,
        "scientific_instrumentation": 4.0,
        "crew_efficiency": 2.0,
    },
    "Dark Matter Biogeochemistry": {
        "detection_range": 4.0,
        "scientific_instrumentation": 4.0,
        "mass_efficiency": 3.0,
    },

    # ----- biological_sciences ---------------------------------------------
    "Trans-Phasic Genetics": {
        "adaptation_index": 5.0,
        "environmental_resilience": 4.0,
        "crew_efficiency": 3.0,
    },
    "Bioenergetic Ascension Theory": {
        "energy_storage": 4.0,
        "psycho_etheric_resonance": 5.0,
        "crew_morale": 3.0,
    },
    "Self-Evolving Biomes": {
        "adaptation_index": 6.0,
        "environmental_resilience": 5.0,
        "life_support_robustness": 3.0,
    },
    "Bio-Digital Symbiosis": {
        "human_ai_symbiosis": 5.0,
        "automation_level": 4.0,
        "crew_efficiency": 3.0,
    },
    "Xeno-Evolutionary Mechanics": {
        "adaptation_index": 5.0,
        "environmental_resilience": 4.0,
        "scientific_instrumentation": 3.0,
    },
    "Quantum Flora and Fauna Studies": {
        "environmental_resilience": 5.0,
        "etheric_sensitivity": 4.0,
        "scientific_instrumentation": 3.0,
    },
    "Chimeric Convergence Biology": {
        "adaptation_index": 6.0,
        "crew_efficiency": 4.0,
        "life_support_robustness": 3.0,
    },
    "Organismic Flux Adaptation": {
        "adaptation_index": 5.0,
        "crew_efficiency": 4.0,
        "environmental_resilience": 3.0,
    },
    "Photosynthetic Etheric Modulation": {
        "energy_storage": 4.0,
        "etheric_channel_conductivity": 4.0,
        "reactor_output": 3.0,
    },

    # ----- theoretical_sciences --------------------------------------------
    "Existential Substrate Theory": {
        "space_ship_coherence": 5.0,
        "material_consciousness_resonance": 4.0,
        "coherence_entropy": -3.0,
    },
    "Conscious Matter Emergence": {
        "ship_sentience": 5.0,
        "material_consciousness_resonance": 5.0,
        "adaptation_index": 4.0,
    },
    "The Nexus Principle": {
        "ether_machine_harmony": 6.0,
        "resonance_stability": 5.0,
        "space_ship_coherence": 4.0,
    },
}


# ---------------------------------------------------------------------------
# 2. Faction focus → ship attribute bonuses
#    Keyed on `primary_focus` values from factions.py.
#    These are persistent passive bonuses for belonging to that faction.
# ---------------------------------------------------------------------------

FACTION_FOCUS_SHIP_BONUSES: Dict[str, Dict[str, float]] = {
    "Technology": {
        "ai_processing_power": 5.0,
        "computational_core_integrity": 4.0,
        "engine_efficiency": 3.0,
        "quantum_compute_efficiency": 3.0,
    },
    "Research": {
        "etheric_sensitivity": 5.0,
        "scan_resolution": 4.0,
        "detection_range": 4.0,
        "scientific_instrumentation": 3.0,
    },
    "Trade": {
        "mass_efficiency": 5.0,
        "energy_storage": 3.0,
        "life_support_robustness": 3.0,
        "protocol_interoperability": 3.0,
    },
    "Industry": {
        "hull_integrity": 5.0,
        "armor_strength": 4.0,
        "structural_redundancy": 4.0,
        "maintenance_autonomy": 3.0,
    },
    "Mysticism": {
        "ether_machine_harmony": 6.0,
        "resonance_stability": 5.0,
        "etheric_sensitivity": 4.0,
        "psycho_etheric_resonance": 3.0,
    },
    "Exploration": {
        "ftl_jump_capacity": 5.0,
        "detection_range": 4.0,
        "energy_storage": 3.0,
        "environmental_resilience": 4.0,
    },
    "Cultural": {
        "human_ai_symbiosis": 5.0,
        "crew_morale": 4.0,
        "cognitive_security": 3.0,
        "mythic_resonance": 4.0,
    },
    "Diplomacy": {
        "transmission_bandwidth": 5.0,
        "fleet_synchronization": 4.0,
        "protocol_interoperability": 4.0,
        "information_security": 3.0,
    },
}


# ---------------------------------------------------------------------------
# 3. Character stat → ship attribute bonuses
#    Each stat earns bonuses scaled by how far it is above the base of 30.
#    Format: stat_key -> list of (attribute_id, points_per_10_above_base)
#    At base (30) the bonus is 0.  At max (100) the bonus is 7 × rate.
# ---------------------------------------------------------------------------

CHAR_STAT_SHIP_BONUSES: Dict[str, List[Tuple[str, float]]] = {
    # Kinetics → piloting/combat precision
    "KIN": [
        ("maneuverability", 1.0),
        ("targeting_speed", 0.8),
        ("engine_output", 0.6),
        ("weapon_accuracy", 0.6),
    ],
    # Intellect → sensors/AI/fire control
    "INT": [
        ("ai_processing_power", 1.0),
        ("scan_resolution", 0.8),
        ("fire_control_intelligence", 0.8),
        ("decision_latency", -0.5),  # negative = faster (lower) latency
    ],
    # Aetheric Affinity → etheric/resonance systems
    "AEF": [
        ("etheric_sensitivity", 1.2),
        ("ether_machine_harmony", 1.0),
        ("resonance_stability", 0.8),
        ("etheric_channel_conductivity", 0.6),
    ],
    # Synthesis → engine and power integration
    "SYN": [
        ("engine_efficiency", 1.0),
        ("power_distribution_efficiency", 0.8),
        ("human_ai_symbiosis", 0.6),
        ("adaptation_index", 0.6),
    ],
    # Coherence → structural stability and coherence fields
    "COH": [
        ("flux_stability", 1.0),
        ("gravitic_stability", 0.8),
        ("space_ship_coherence", 0.8),
        ("coherence_entropy", -0.6),  # negative = less entropy (better)
    ],
    # Vitality → hull and crew robustness
    "VIT": [
        ("hull_integrity", 0.6),
        ("damage_control_automation", 0.6),
        ("life_support_robustness", 0.5),
        ("crew_morale", 0.4),
    ],
    # Influence → communications and fleet coordination
    "INF": [
        ("transmission_bandwidth", 0.8),
        ("fleet_synchronization", 0.6),
        ("information_security", 0.5),
        ("crew_efficiency", 0.4),
    ],
}


# ---------------------------------------------------------------------------
# Calculation functions (pure — no game state or I/O)
# ---------------------------------------------------------------------------


def calculate_research_bonuses(completed_research: List[str]) -> Dict[str, float]:
    """
    Sum attribute deltas for all completed research items.

    Returns a flat ``{attribute_id: total_bonus}`` dict.  Values can be
    negative (e.g. signature reductions).  Caller is responsible for
    clamping the merged profile to [0, 100].
    """
    result: Dict[str, float] = {}
    for research_id in (completed_research or []):
        for attr_id, bonus in RESEARCH_SHIP_BONUSES.get(research_id, {}).items():
            result[attr_id] = result.get(attr_id, 0.0) + bonus
    return result


def calculate_faction_bonuses(faction_name: Optional[str]) -> Dict[str, float]:
    """
    Return passive attribute bonuses for the player's home faction.

    Looks up the faction's ``primary_focus`` in ``factions.py`` and returns
    the corresponding bonus dict.  Returns an empty dict for unknown factions
    or if ``faction_name`` is None.
    """
    if not faction_name:
        return {}
    try:
        from factions import factions as _factions
        focus = _factions.get(faction_name, {}).get("primary_focus", "")
        return dict(FACTION_FOCUS_SHIP_BONUSES.get(focus, {}))
    except Exception:
        return {}


def calculate_character_stat_bonuses(char_stats: Dict[str, int]) -> Dict[str, float]:
    """
    Translate character stats into ship attribute deltas.

    For each stat, the bonus scales linearly with how far the stat exceeds
    the base of 30.  Ten points above base = one "tier".  A stat at 80 is
    five tiers above base, so a rate of 1.0 pt/tier yields +5.0.

    Returns a flat ``{attribute_id: total_bonus}`` dict.
    """
    result: Dict[str, float] = {}
    for stat_abbr, attr_list in CHAR_STAT_SHIP_BONUSES.items():
        stat_val = (char_stats or {}).get(stat_abbr, 30)
        tiers_above_base = max(0.0, (stat_val - 30) / 10.0)
        if tiers_above_base == 0.0:
            continue
        for attr_id, points_per_tier in attr_list:
            bonus = tiers_above_base * points_per_tier
            result[attr_id] = result.get(attr_id, 0.0) + bonus
    return result


__all__ = [
    "RESEARCH_SHIP_BONUSES",
    "FACTION_FOCUS_SHIP_BONUSES",
    "CHAR_STAT_SHIP_BONUSES",
    "calculate_research_bonuses",
    "calculate_faction_bonuses",
    "calculate_character_stat_bonuses",
]
