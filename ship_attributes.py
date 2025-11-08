"""
Canonical starship attribute schema.

The schema captures every quantitative dimension a ship, component, or crew
modifier can express.  Each attribute is normalized to a 0–100 scale so that
different sources can be merged or compared without additional bookkeeping.

The definitions are split into two pieces:

* ``SHIP_ATTRIBUTE_DEFINITIONS`` holds metadata for each attribute id.
* ``SHIP_ATTRIBUTE_CATEGORIES`` lists logical groupings that reference those ids.

Components, hulls, ship classes, and crew assignments should reference the
``id`` field to avoid ad-hoc naming and to ensure the entire game speaks the
same language when it comes to ship capabilities.
"""

from __future__ import annotations

from typing import Dict, List, Mapping, Sequence

# ---------------------------------------------------------------------------
# Attribute definitions (id -> metadata)
# ---------------------------------------------------------------------------

SHIP_ATTRIBUTE_DEFINITIONS: Dict[str, Dict[str, str]] = {
    # 1. Structural & Physical Systems
    "hull_integrity": {
        "name": "Hull Integrity",
        "description": "Physical resilience and tolerance to damage.",
    },
    "armor_strength": {
        "name": "Armor Strength",
        "description": "Effectiveness at absorbing kinetic and energy impacts.",
    },
    "structural_redundancy": {
        "name": "Structural Redundancy",
        "description": "Degree of compartmentalization and failover design.",
    },
    "maintenance_complexity": {
        "name": "Maintenance Complexity",
        "description": "Ease or difficulty of performing repairs and upkeep.",
    },
    "mass_efficiency": {
        "name": "Mass Efficiency",
        "description": "Optimization of strength relative to vessel mass.",
    },
    "material_consciousness_resonance": {
        "name": "Material Consciousness Resonance",
        "description": "How deeply the hull harmonizes with AI or etheric fields.",
    },
    # 2. Propulsion & Mobility
    "engine_output": {
        "name": "Engine Output",
        "description": "Total thrust and acceleration potential.",
    },
    "engine_efficiency": {
        "name": "Engine Efficiency",
        "description": "Energy conversion efficiency per unit of thrust.",
    },
    "maneuverability": {
        "name": "Maneuverability",
        "description": "Agility and responsiveness to pilot or AI input.",
    },
    "top_velocity": {
        "name": "Top Velocity",
        "description": "Maximum sustainable sub-light speed.",
    },
    "ftl_jump_capacity": {
        "name": "FTL / Jump Capacity",
        "description": "Reach and reliability of faster-than-light transitions.",
    },
    "chrono_adaptability": {
        "name": "Chrono-Adaptability",
        "description": "Tolerance for temporal distortions and time dilation.",
    },
    "gravitic_stability": {
        "name": "Gravitic Stability",
        "description": "Ability to sustain internal gravity fields under stress.",
    },
    # 3. Power & Energy Systems
    "reactor_output": {
        "name": "Reactor Output",
        "description": "Overall energy generation capability.",
    },
    "energy_storage": {
        "name": "Energy Storage",
        "description": "Reserve capacity within capacitors or etheric wells.",
    },
    "power_distribution_efficiency": {
        "name": "Power Distribution Efficiency",
        "description": "Loss rate when reallocating energy among systems.",
    },
    "thermal_regulation": {
        "name": "Thermal Regulation",
        "description": "Efficiency in dissipating and transferring heat.",
    },
    "flux_stability": {
        "name": "Flux Stability",
        "description": "Control of energy turbulence during extreme operations.",
    },
    "etheric_channel_conductivity": {
        "name": "Etheric Channel Conductivity",
        "description": "Quality of etheric energy transmission across systems.",
    },
    "quantum_power_conversion": {
        "name": "Quantum Power Conversion",
        "description": "Efficiency converting power across quantum states.",
    },
    # 4. Defensive Systems
    "shield_capacity": {
        "name": "Shield Capacity",
        "description": "Total strength of energy barriers.",
    },
    "shield_regeneration": {
        "name": "Shield Regeneration",
        "description": "Recovery speed while under fire.",
    },
    "shield_modulation": {
        "name": "Shield Modulation",
        "description": "Adaptability to different weapon signatures.",
    },
    "ecm_strength": {
        "name": "Electronic Countermeasure Strength",
        "description": "Effectiveness at spoofing or disrupting hostile targeting.",
    },
    "point_defense_accuracy": {
        "name": "Point Defense Accuracy",
        "description": "Probability of intercepting incoming projectiles.",
    },
    "damage_control_automation": {
        "name": "Damage Control Automation",
        "description": "Autonomous fire suppression, sealing, and repair capacity.",
    },
    "harmonic_shield_resonance": {
        "name": "Harmonic Shield Resonance",
        "description": "Synchrony between shields and etheric frequencies.",
    },
    # 5. Offensive Systems
    "weapon_power": {
        "name": "Weapon Power",
        "description": "Aggregate destructive output across all armaments.",
    },
    "weapon_accuracy": {
        "name": "Weapon Accuracy",
        "description": "Hit probability and targeting precision.",
    },
    "weapon_range": {
        "name": "Weapon Range",
        "description": "Effective engagement distance.",
    },
    "targeting_speed": {
        "name": "Targeting Speed",
        "description": "Time required to lock onto a target.",
    },
    "fire_control_intelligence": {
        "name": "Fire Control Intelligence",
        "description": "Predictive quality of firing solutions.",
    },
    "ammo_energy_sustainment": {
        "name": "Ammunition / Energy Sustainment",
        "description": "Duration of continuous weapon operation.",
    },
    "etheric_weapon_integration": {
        "name": "Etheric Weapon Integration",
        "description": "Efficiency of harmonizing weapons with etheric flows.",
    },
    # 6. Sensors & Scanning
    "detection_range": {
        "name": "Detection Range",
        "description": "Maximum distance at which objects can be detected.",
    },
    "scan_resolution": {
        "name": "Scan Resolution",
        "description": "Detail and fidelity of sensor imagery.",
    },
    "scan_refresh_rate": {
        "name": "Scan Refresh Rate",
        "description": "Temporal resolution of sensor updates.",
    },
    "target_tracking_stability": {
        "name": "Target Tracking Stability",
        "description": "Reliability of maintaining target locks.",
    },
    "noise_floor": {
        "name": "Noise Floor",
        "description": "Baseline interference within the sensor suite.",
    },
    "sensor_discipline": {
        "name": "Sensor Discipline",
        "description": "Ability to operate covertly without revealing position.",
    },
    "ecm_resistance": {
        "name": "ECM Resistance",
        "description": "Resilience against jamming or spoofing attempts.",
    },
    "signature_analysis": {
        "name": "Signature Analysis",
        "description": "Capacity to interpret multi-spectrum emissions.",
    },
    "etheric_sensitivity": {
        "name": "Etheric Sensitivity",
        "description": "Precision detecting etheric disturbances.",
    },
    "scanner_noise_spectrum": {
        "name": "Scanner Noise Spectrum",
        "description": "Internal signal pollution from the sensors themselves.",
    },
    # 7. Stealth & Signature
    "thermal_signature": {
        "name": "Thermal Signature",
        "description": "Visibility to infrared and heat-based sensors.",
    },
    "electromagnetic_signature": {
        "name": "Electromagnetic Signature",
        "description": "Detectability via EM-spectrum surveillance.",
    },
    "radar_lidar_cross_section": {
        "name": "Radar / Lidar Cross Section",
        "description": "Reflectivity and susceptibility to ranging systems.",
    },
    "etheric_signature": {
        "name": "Etheric Signature",
        "description": "Resonant footprint within etheric space.",
    },
    "signature_dampening": {
        "name": "Signature Dampening",
        "description": "Effectiveness of passive and active stealth systems.",
    },
    "spectral_noise_emission": {
        "name": "Spectral Noise Emission",
        "description": "Cross-band interference generated during operation.",
    },
    "temporal_signature": {
        "name": "Temporal Signature",
        "description": "Detectability through chronometric scanning.",
    },
    # 8. AI, Cognition & Sentience
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
    # 9. Etheric & Coherence Systems
    "ether_machine_harmony": {
        "name": "Ether/Machine Harmony",
        "description": "Synchronization of mechanical, AI, and etheric fields.",
    },
    "resonance_stability": {
        "name": "Resonance Stability",
        "description": "Consistency of harmonic output across etheric bands.",
    },
    "ai_ether_integration": {
        "name": "AI/Ether Integration",
        "description": "Synergy between AI cognition and etheric dynamics.",
    },
    "space_ship_coherence": {
        "name": "Space/Ship Coherence",
        "description": "Alignment of the vessel's local reality bubble with spacetime.",
    },
    "flux_tolerance": {
        "name": "Flux Tolerance",
        "description": "Resilience during etheric turbulence.",
    },
    "etheric_signature_complexity": {
        "name": "Etheric Signature Complexity",
        "description": "Richness of resonance; affects stealth versus control.",
    },
    "chrono_symphony": {
        "name": "Chrono-Symphony",
        "description": "Harmony between the ship's time flow and universal constants.",
    },
    "coherence_entropy": {
        "name": "Coherence Entropy",
        "description": "Disorder within ship-space boundaries (lower is better).",
    },
    "harmonic_feedback_control": {
        "name": "Harmonic Feedback Control",
        "description": "Suppression of runaway etheric oscillations.",
    },
    # 10. Computing & Data Systems
    "computational_core_integrity": {
        "name": "Computational Core Integrity",
        "description": "Stability and health of central data systems.",
    },
    "processing_density": {
        "name": "Processing Density",
        "description": "Compute throughput per unit volume.",
    },
    "quantum_compute_efficiency": {
        "name": "Quantum Compute Efficiency",
        "description": "Stability and utilization of entangled processors.",
    },
    "neural_resonant_architecture": {
        "name": "Neural-Resonant Architecture",
        "description": "Overlap between neural nets and etheric substrates.",
    },
    "etheric_logic_alignment": {
        "name": "Etheric Logic Alignment",
        "description": "Exploitation of etheric harmonics for computation.",
    },
    "data_throughput": {
        "name": "Data Throughput",
        "description": "Total bandwidth across ship systems.",
    },
    "latency_optimization": {
        "name": "Latency Optimization",
        "description": "Management of internal communication delays.",
    },
    "parallel_synchrony": {
        "name": "Parallel Synchrony",
        "description": "Coordination among distributed computing cores.",
    },
    "cognitive_resonance": {
        "name": "Cognitive Resonance",
        "description": "Alignment of AI cycles with etheric oscillations.",
    },
    "entropy_management": {
        "name": "Entropy Management",
        "description": "Ability to dissipate computational noise and decoherence.",
    },
    "etheric_channeling_index": {
        "name": "Etheric Channeling Index",
        "description": "Efficiency of powering computation with etheric energy.",
    },
    "predictive_modeling_depth": {
        "name": "Predictive Modeling Depth",
        "description": "Scale of foresight and probabilistic simulation.",
    },
    "causal_mapping_precision": {
        "name": "Causal Mapping Precision",
        "description": "Accuracy when simulating causal chains.",
    },
    "information_integrity": {
        "name": "Information Integrity",
        "description": "Defense against corruption, interference, or paradox.",
    },
    "self_optimization_capacity": {
        "name": "Self-Optimization Capacity",
        "description": "Ability for the ship to rewrite and tune itself.",
    },
    # 11. Communication & Networking
    "transmission_bandwidth": {
        "name": "Transmission Bandwidth",
        "description": "Throughput across all communication channels.",
    },
    "latency_control": {
        "name": "Latency Control",
        "description": "Precision timing over long-distance links.",
    },
    "quantum_link_stability": {
        "name": "Quantum Link Stability",
        "description": "Reliability of entangled or etheric comm relays.",
    },
    "fleet_synchronization": {
        "name": "Fleet Synchronization",
        "description": "Precision sharing of tactical data across allies.",
    },
    "protocol_interoperability": {
        "name": "Protocol Interoperability",
        "description": "Compatibility with foreign or legacy systems.",
    },
    "etheric_signal_clarity": {
        "name": "Etheric Signal Clarity",
        "description": "Purity of transmissions through etheric mediums.",
    },
    "information_security": {
        "name": "Information Security",
        "description": "Resistance to interception or corruption.",
    },
    # 12. Crew & Operational
    "crew_efficiency": {
        "name": "Crew Efficiency",
        "description": "Overall performance of coordinated crew actions.",
    },
    "crew_morale": {
        "name": "Crew Morale",
        "description": "Emotional and psychological condition of personnel.",
    },
    "automation_level": {
        "name": "Automation Level",
        "description": "Ratio of autonomous to manual system control.",
    },
    "life_support_robustness": {
        "name": "Life Support Robustness",
        "description": "Duration and redundancy of vital life systems.",
    },
    "maintenance_autonomy": {
        "name": "Maintenance Autonomy",
        "description": "Self-diagnosis and repair capabilities.",
    },
    "command_feedback_clarity": {
        "name": "Command Feedback Clarity",
        "description": "Transparency of command chains between human and AI.",
    },
    "psycho_etheric_resonance": {
        "name": "Psycho-Etheric Resonance",
        "description": "Harmony between crew emotions and etheric fields.",
    },
    # 13. Exploration & Adaptation
    "environmental_resilience": {
        "name": "Environmental Resilience",
        "description": "Performance within extreme cosmic conditions.",
    },
    "scientific_instrumentation": {
        "name": "Scientific Instrumentation",
        "description": "Capability for data gathering and experimentation.",
    },
    "adaptation_index": {
        "name": "Adaptation Index",
        "description": "Rate at which systems learn and evolve.",
    },
    "cognitive_growth_potential": {
        "name": "Cognitive Growth Potential",
        "description": "Capacity for emergent behavior and self-development.",
    },
    "reality_anchoring_strength": {
        "name": "Reality Anchoring Strength",
        "description": "Ability to maintain coherence near exotic phenomena.",
    },
    "mythic_resonance": {
        "name": "Mythic Resonance",
        "description": "Symbolic or memetic impact that influences morale or etheric responses.",
    },
}

# Chrono-Adaptability is shared between propulsion and exploration—the same id
# appears in multiple category listings below.

# ---------------------------------------------------------------------------
# Categories (id -> attribute id list)
# ---------------------------------------------------------------------------

SHIP_ATTRIBUTE_CATEGORIES: List[Dict[str, object]] = [
    {
        "id": "structural",
        "name": "Structural & Physical Systems",
        "attributes": [
            "hull_integrity",
            "armor_strength",
            "structural_redundancy",
            "maintenance_complexity",
            "mass_efficiency",
            "material_consciousness_resonance",
        ],
    },
    {
        "id": "propulsion",
        "name": "Propulsion & Mobility",
        "attributes": [
            "engine_output",
            "engine_efficiency",
            "maneuverability",
            "top_velocity",
            "ftl_jump_capacity",
            "chrono_adaptability",
            "gravitic_stability",
        ],
    },
    {
        "id": "power",
        "name": "Power & Energy Systems",
        "attributes": [
            "reactor_output",
            "energy_storage",
            "power_distribution_efficiency",
            "thermal_regulation",
            "flux_stability",
            "etheric_channel_conductivity",
            "quantum_power_conversion",
        ],
    },
    {
        "id": "defensive",
        "name": "Defensive Systems",
        "attributes": [
            "shield_capacity",
            "shield_regeneration",
            "shield_modulation",
            "ecm_strength",
            "point_defense_accuracy",
            "damage_control_automation",
            "harmonic_shield_resonance",
        ],
    },
    {
        "id": "offensive",
        "name": "Offensive Systems",
        "attributes": [
            "weapon_power",
            "weapon_accuracy",
            "weapon_range",
            "targeting_speed",
            "fire_control_intelligence",
            "ammo_energy_sustainment",
            "etheric_weapon_integration",
        ],
    },
    {
        "id": "sensors",
        "name": "Sensors & Scanning",
        "attributes": [
            "detection_range",
            "scan_resolution",
            "scan_refresh_rate",
            "target_tracking_stability",
            "noise_floor",
            "sensor_discipline",
            "ecm_resistance",
            "signature_analysis",
            "etheric_sensitivity",
            "scanner_noise_spectrum",
        ],
    },
    {
        "id": "stealth",
        "name": "Stealth & Signature",
        "attributes": [
            "thermal_signature",
            "electromagnetic_signature",
            "radar_lidar_cross_section",
            "etheric_signature",
            "signature_dampening",
            "spectral_noise_emission",
            "temporal_signature",
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
    {
        "id": "etheric_coherence",
        "name": "Etheric & Coherence Systems",
        "attributes": [
            "ether_machine_harmony",
            "resonance_stability",
            "ai_ether_integration",
            "space_ship_coherence",
            "flux_tolerance",
            "etheric_signature_complexity",
            "chrono_symphony",
            "coherence_entropy",
            "harmonic_feedback_control",
        ],
    },
    {
        "id": "computing",
        "name": "Computing & Data Systems",
        "attributes": [
            "computational_core_integrity",
            "processing_density",
            "quantum_compute_efficiency",
            "neural_resonant_architecture",
            "etheric_logic_alignment",
            "data_throughput",
            "latency_optimization",
            "parallel_synchrony",
            "cognitive_resonance",
            "entropy_management",
            "etheric_channeling_index",
            "predictive_modeling_depth",
            "causal_mapping_precision",
            "information_integrity",
            "self_optimization_capacity",
        ],
    },
    {
        "id": "communications",
        "name": "Communication & Networking",
        "attributes": [
            "transmission_bandwidth",
            "latency_control",
            "quantum_link_stability",
            "fleet_synchronization",
            "protocol_interoperability",
            "etheric_signal_clarity",
            "information_security",
        ],
    },
    {
        "id": "crew_operational",
        "name": "Crew & Operational",
        "attributes": [
            "crew_efficiency",
            "crew_morale",
            "automation_level",
            "life_support_robustness",
            "maintenance_autonomy",
            "command_feedback_clarity",
            "psycho_etheric_resonance",
        ],
    },
    {
        "id": "exploration",
        "name": "Exploration & Adaptation",
        "attributes": [
            "environmental_resilience",
            "scientific_instrumentation",
            "adaptation_index",
            "cognitive_growth_potential",
            "chrono_adaptability",
            "reality_anchoring_strength",
            "mythic_resonance",
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

