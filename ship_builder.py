"""
Ship component registry scaffolding built around the canonical attribute
schema defined in ``ship_attributes.py``.

This module intentionally keeps the component data empty for now.  Systems
that import it can rely on the structure and helper utilities while we build
out the new ship model incrementally.
"""

from __future__ import annotations

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
# Canonical component registry (currently empty while we rebuild the system).
# -----------------------------------------------------------------------------

ship_components: Dict[str, Dict[str, Mapping[str, object]]] = {
    "hulls": {
        "Aegis Bastion Hull": {
            "cost": 62000,
            "faction_lock": ["Solar Wardens"],
            "failure_chance": 0.015,
            "lore": (
                "Layered plasteel and sanctified ether-plates forged by the Solar Wardens. "
                "Built to hold the line against siege cannons and spiritual entropy alike."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "hull_integrity": 35,
                            "armor_strength": 30,
                            "structural_redundancy": 22,
                            "maintenance_complexity": 10,
                            "mass_efficiency": -12,
                            "material_consciousness_resonance": 5,
                            "damage_control_automation": 8,
                            "flux_tolerance": 6,
                        }
                    ]
                )
            ),
        },
        "Valkyrie Lattice Frame": {
            "cost": 48000,
            "faction_lock": None,
            "failure_chance": 0.02,
            "lore": (
                "A modular honeycomb frame popular with frontier skippers. "
                "Sacrifices raw armor for agility and quick field repairs."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "hull_integrity": 18,
                            "armor_strength": 6,
                            "structural_redundancy": 14,
                            "maintenance_complexity": 18,
                            "mass_efficiency": 16,
                            "maneuverability": 12,
                            "crew_efficiency": 6,
                        }
                    ]
                )
            ),
        },
        "Eidolon Veil Hull": {
            "cost": 70500,
            "faction_lock": ["Chorus of Silence"],
            "failure_chance": 0.03,
            "lore": (
                "Woven from voidglass and psionic mesh, the veil hull folds light and thought around the ship. "
                "Unnerving to maintain, incomparable for clandestine operations."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "hull_integrity": -6,
                            "armor_strength": -10,
                            "thermal_signature": -28,
                            "electromagnetic_signature": -24,
                            "radar_lidar_cross_section": -30,
                            "etheric_signature": -22,
                            "signature_dampening": 26,
                            "spectral_noise_emission": -10,
                            "temporal_signature": -14,
                            "sensor_discipline": 10,
                            "psycho_etheric_resonance": -4,
                        }
                    ]
                )
            ),
        },
        "Pilgrim Nomad Superstructure": {
            "cost": 54000,
            "faction_lock": ["Free Pilgrim Clans"],
            "failure_chance": 0.018,
            "lore": (
                "Self-healing lattice that adapts to harsh cosmic climates. "
                "Every Nomad hull is etched with ancestral star maps and communal lore."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "environmental_resilience": 24,
                            "hull_integrity": 12,
                            "structural_redundancy": 16,
                            "maintenance_autonomy": 12,
                            "life_support_robustness": 20,
                            "adaptation_index": 14,
                            "reality_anchoring_strength": 8,
                            "crew_morale": 10,
                        }
                    ]
                )
            ),
        },
        "Zephyr Skysteel Chassis": {
            "cost": 45500,
            "faction_lock": ["Skyforge Armada"],
            "failure_chance": 0.022,
            "lore": (
                "An ultralight skysteel lattice originally designed for atmospheric skimmers. "
                "Spacefarers prize it for evasive maneuvers and graceful drift."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "mass_efficiency": 24,
                            "maneuverability": 18,
                            "structural_redundancy": 8,
                            "hull_integrity": -6,
                            "armor_strength": -4,
                            "top_velocity": 10,
                            "engine_efficiency": 6,
                        }
                    ]
                )
            ),
        },
        "Obsidian Reliquary Carapace": {
            "cost": 68500,
            "faction_lock": ["Obsidian Bastion Chapter"],
            "failure_chance": 0.03,
            "lore": (
                "A vault-hull that houses ancestral relics within obsidian nerve channels. "
                "It hums softly, soothing sentient cores and unnerving raiders."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "hull_integrity": 28,
                            "armor_strength": 22,
                            "material_consciousness_resonance": 20,
                            "structural_redundancy": 14,
                            "maintenance_complexity": -12,
                            "ship_sentience": 8,
                            "coherence_entropy": 6,
                        }
                    ]
                )
            ),
        },
        "Myriad Bioshell": {
            "cost": 57200,
            "faction_lock": ["Aetheric Nomads"],
            "failure_chance": 0.026,
            "lore": (
                "A living bioshell cultivated from symbiotic coral matrices. "
                "It adapts to crew emotions and repairs itself by budding new plates."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "maintenance_autonomy": 18,
                            "life_support_robustness": 22,
                            "psycho_etheric_resonance": 16,
                            "crew_morale": 12,
                            "environmental_resilience": 12,
                            "hull_integrity": 10,
                            "automation_level": -6,
                        }
                    ]
                )
            ),
        },
    },
    "engines": {
        "Helios Lance Drive": {
            "cost": 38500,
            "faction_lock": None,
            "failure_chance": 0.025,
            "lore": (
                "Massive solar furnaces concentrate plasma into a coherent lance of thrust. "
                "Beloved by blockade runners who live for straight-line speed."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "engine_output": 28,
                            "top_velocity": 24,
                            "engine_efficiency": 6,
                            "thermal_regulation": -6,
                            "flux_stability": -4,
                            "spectral_noise_emission": 8,
                        }
                    ]
                )
            ),
        },
        "Whisperstream Coil": {
            "cost": 51200,
            "faction_lock": ["Chorus of Silence"],
            "failure_chance": 0.035,
            "lore": (
                "Phase-shifted coils bleed thrust across adjacent realities. "
                "Produces almost no wake, but temperamental under flux storms."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "engine_output": 12,
                            "engine_efficiency": 18,
                            "maneuverability": 14,
                            "thermal_signature": -22,
                            "electromagnetic_signature": -18,
                            "flux_stability": -8,
                            "chrono_adaptability": 10,
                        }
                    ]
                )
            ),
        },
        "Graviton Cascade Thrusters": {
            "cost": 61000,
            "faction_lock": ["Atlantean Gradient"],
            "failure_chance": 0.03,
            "lore": (
                "A cascade of gravitic nodes folds local gravity wells to catapult the ship. "
                "Requires constant calibration by gravitic monks."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "engine_output": 20,
                            "maneuverability": 22,
                            "gravitic_stability": 16,
                            "ftl_jump_capacity": 8,
                            "flux_stability": -6,
                            "maintenance_complexity": -4,
                        }
                    ]
                )
            ),
        },
        "Chronobloom Fold Engine": {
            "cost": 82000,
            "faction_lock": ["Chronomantic Concord"],
            "failure_chance": 0.045,
            "lore": (
                "Fold petals unfurl through layered time, letting the ship bloom into new coordinates. "
                "Powerful, mesmerizing, and occasionally catastrophic."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "ftl_jump_capacity": 28,
                            "chrono_adaptability": 30,
                            "chrono_symphony": 12,
                            "top_velocity": 10,
                            "flux_stability": -10,
                            "quantum_power_conversion": 8,
                            "temporal_signature": 12,
                        }
                    ]
                )
            ),
        },
        "Auric Flux Sails": {
            "cost": 34800,
            "faction_lock": ["Solar Wardens"],
            "failure_chance": 0.02,
            "lore": (
                "Etheric sails woven from auric filaments catch solar winds and star-song. "
                "Pilots describe the sensation as 'surfing hymns of light'."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "engine_efficiency": 24,
                            "top_velocity": 16,
                            "thermal_signature": -14,
                            "etheric_channel_conductivity": 10,
                            "energy_storage": 6,
                            "engine_output": 6,
                            "flux_stability": -4,
                        }
                    ]
                )
            ),
        },
        "Drakeheart Furnace": {
            "cost": 57500,
            "faction_lock": ["Guildhammer Combine"],
            "failure_chance": 0.034,
            "lore": (
                "Industrial fusion cores encased in dragonbone alloys. "
                "Capable of brutal thrust—if you can tame its volcanic temperament."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "engine_output": 30,
                            "reactor_output": 20,
                            "thermal_regulation": -16,
                            "flux_stability": -8,
                            "weapon_power": 8,
                            "engine_efficiency": -6,
                            "gravitic_stability": 8,
                        }
                    ]
                )
            ),
        },
        "Whirlwind Impeller": {
            "cost": 49800,
            "faction_lock": ["Storm Halberd Legion"],
            "failure_chance": 0.028,
            "lore": (
                "Cyclonic impellers harness stormfronts in microcosm. "
                "They deliver hairpin turns and bone-jarring acceleration."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "maneuverability": 24,
                            "engine_output": 18,
                            "gravitic_stability": 10,
                            "targeting_speed": 6,
                            "spectral_noise_emission": 8,
                            "noise_floor": 4,
                            "flux_stability": -6,
                        }
                    ]
                )
            ),
        },
    },
    "weapons": {
        "Frontier Coilgun Battery": {
            "cost": 28000,
            "faction_lock": None,
            "failure_chance": 0.02,
            "lore": (
                "Reliable kinetic coilguns used by frontier militias and merchant escorts. "
                "Cheap to maintain, easy to adapt, and surprisingly punchy when overcharged."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "weapon_power": 16,
                            "weapon_accuracy": 12,
                            "weapon_range": 10,
                            "ammo_energy_sustainment": 12,
                            "point_defense_accuracy": 8,
                            "thermal_signature": 6,
                            "maintenance_autonomy": 6,
                        }
                    ]
                )
            ),
        },
        "Sunlance Array": {
            "cost": 41000,
            "faction_lock": ["Solar Wardens"],
            "failure_chance": 0.028,
            "lore": (
                "Beam emitters channel raw stellar essence into coherent lances. "
                "A righteous glow that can scar worlds if overcharged."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "weapon_power": 24,
                            "weapon_range": 18,
                            "weapon_accuracy": 12,
                            "ammo_energy_sustainment": 6,
                            "thermal_signature": 8,
                            "etheric_weapon_integration": 10,
                            "flux_stability": -6,
                        }
                    ]
                )
            ),
        },
        "Nullwave Resonator": {
            "cost": 53500,
            "faction_lock": ["Chorus of Silence"],
            "failure_chance": 0.04,
            "lore": (
                "Emitter pods project oscillating null-fields that erode defenses. "
                "Mercifully silent, lethally efficient against energy shields."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "weapon_power": 14,
                            "weapon_accuracy": 10,
                            "shield_modulation": 16,
                            "etheric_weapon_integration": 18,
                            "signature_dampening": 8,
                            "energy_storage": -6,
                            "predictive_modeling_depth": 6,
                        }
                    ]
                )
            ),
        },
        "Ragnar Lance Batteries": {
            "cost": 62000,
            "faction_lock": ["Guildhammer Combine"],
            "failure_chance": 0.033,
            "lore": (
                "Industrial-grade rail batteries firing mass-reactive spikes. "
                "Favored by guild captains who believe overwhelming force is subtle enough."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "weapon_power": 30,
                            "weapon_range": 16,
                            "ammo_energy_sustainment": 12,
                            "thermal_regulation": -8,
                            "spectral_noise_emission": 12,
                            "hull_integrity": 6,
                        }
                    ]
                )
            ),
        },
        "Aetheric Bloom Torpedoes": {
            "cost": 69000,
            "faction_lock": ["Aetheric Nomads"],
            "failure_chance": 0.05,
            "lore": (
                "Seeded torpedoes detonate into fractal bloomstorms of ether. "
                "Devastating when timed correctly, erratic when mishandled."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "weapon_power": 28,
                            "weapon_range": 20,
                            "fire_control_intelligence": 8,
                            "etheric_weapon_integration": 22,
                            "temporal_signature": 10,
                            "point_defense_accuracy": -6,
                        }
                    ]
                )
            ),
        },
        "Seraph Scatterrail": {
            "cost": 45500,
            "faction_lock": ["Seraphim Vanguard"],
            "failure_chance": 0.032,
            "lore": (
                "Triple-linked scatterrail cannons that shred strikecraft with radiant flechettes. "
                "It sings with each salvo, a choir of righteous metal."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "weapon_power": 18,
                            "weapon_accuracy": 16,
                            "targeting_speed": 14,
                            "point_defense_accuracy": 22,
                            "ammo_energy_sustainment": 10,
                            "thermal_signature": 6,
                            "maneuverability": -4,
                        }
                    ]
                )
            ),
        },
        "Void Lantern Projector": {
            "cost": 60200,
            "faction_lock": ["Chorus of Silence"],
            "failure_chance": 0.045,
            "lore": (
                "Lanterns compress voidlight into globes that devour matter and thought. "
                "Commanders deploy them sparingly; the lanterns remember everything they consume."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "weapon_power": 26,
                            "weapon_range": 18,
                            "etheric_weapon_integration": 24,
                            "fire_control_intelligence": 10,
                            "temporal_signature": 8,
                            "ship_sentience": 8,
                            "crew_morale": -8,
                        }
                    ]
                )
            ),
        },
        "Hyperion Lance Deck": {
            "cost": 74800,
            "faction_lock": ["Solar Wardens", "Atlantean Gradient"],
            "failure_chance": 0.05,
            "lore": (
                "A spinal lance channeling stellar confinement beams. "
                "Capable of piercing dreadnoughts—or destabilizing nearby stars if misaligned."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "weapon_power": 34,
                            "weapon_range": 24,
                            "weapon_accuracy": 10,
                            "etheric_weapon_integration": 12,
                            "energy_storage": -10,
                            "flux_stability": -12,
                            "predictive_modeling_depth": 8,
                        }
                    ]
                )
            ),
        },
    },
    "shields": {
        "Aurelian Bulwark": {
            "cost": 36000,
            "faction_lock": None,
            "failure_chance": 0.02,
            "lore": (
                "A golden lattice of hardlight projectors tuned for brute endurance. "
                "Slow to cycle but capable of weathering brutal barrages."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "shield_capacity": 26,
                            "shield_regeneration": 8,
                            "shield_modulation": 6,
                            "thermal_regulation": 6,
                            "flux_stability": -4,
                            "energy_storage": -2,
                        }
                    ]
                )
            ),
        },
        "Phaseglass Screen": {
            "cost": 47500,
            "faction_lock": ["Translucent Court"],
            "failure_chance": 0.032,
            "lore": (
                "Phaseglass matrices slip the ship between energetic states. "
                "Spectacular when synchronized, disastrous if the rhythm falters."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "shield_capacity": 12,
                            "shield_regeneration": 16,
                            "shield_modulation": 18,
                            "harmonic_shield_resonance": 20,
                            "temporal_signature": -8,
                            "flux_stability": -6,
                        }
                    ]
                )
            ),
        },
        "Maelstrom Mirror": {
            "cost": 54000,
            "faction_lock": ["Storm Halberd Legion"],
            "failure_chance": 0.04,
            "lore": (
                "Cyclonic fields catch enemy fire and hurl it back in twisted arcs. "
                "Pilots call it 'angry weather in a bottle'."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "shield_capacity": 18,
                            "shield_regeneration": 10,
                            "ecm_strength": 12,
                            "harmonic_shield_resonance": 16,
                            "weapon_power": 8,
                            "flux_stability": -10,
                            "spectral_noise_emission": 12,
                        }
                    ]
                )
            ),
        },
        "Starseer Veil": {
            "cost": 48800,
            "faction_lock": ["Harmonic Pavilion"],
            "failure_chance": 0.03,
            "lore": (
                "A poetic weave of starlight and psalms that bends incoming fire into auroral cascades. "
                "Crew meditations keep the veil aligned; distractions create cracks."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "shield_capacity": 14,
                            "shield_regeneration": 20,
                            "sensor_discipline": 10,
                            "harmonic_shield_resonance": 18,
                            "psycho_etheric_resonance": 10,
                            "temporal_signature": -6,
                            "flux_stability": -4,
                        }
                    ]
                )
            ),
        },
        "Bastion Prism Ward": {
            "cost": 61200,
            "faction_lock": ["Guildhammer Combine"],
            "failure_chance": 0.04,
            "lore": (
                "Prismatic plates refract energy into concentric bulwarks. "
                "It drains reactors quickly but turns siege fire into dazzling halos."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "shield_capacity": 28,
                            "shield_modulation": 12,
                            "ecm_strength": 6,
                            "energy_storage": -8,
                            "reactor_output": -6,
                            "thermal_regulation": 10,
                        }
                    ]
                )
            ),
        },
        "Luminous Echo Barrier": {
            "cost": 52500,
            "faction_lock": ["Chorus of Silence"],
            "failure_chance": 0.038,
            "lore": (
                "Constructed from echo-crystals that remember impacts. "
                "Each strike makes the barrier stronger until the echoes crescendo and shatter."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "shield_capacity": 16,
                            "shield_regeneration": 14,
                            "shield_modulation": 12,
                            "harmonic_shield_resonance": 24,
                            "coherence_entropy": -8,
                            "flux_stability": -8,
                            "weapon_power": 6,
                        }
                    ]
                )
            ),
        },
    },
    "sensors": {
        "Oracle Crown Array": {
            "cost": 28500,
            "faction_lock": None,
            "failure_chance": 0.018,
            "lore": (
                "A crown of telescoping sensor masts tied into predictive heuristics. "
                "Standard issue for survey vessels seeking new frontiers."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "detection_range": 18,
                            "scan_resolution": 16,
                            "scan_refresh_rate": 12,
                            "signature_analysis": 10,
                            "predictive_modeling_depth": 8,
                            "spectral_noise_emission": 4,
                        }
                    ]
                )
            ),
        },
        "Ghostlight Scrying Net": {
            "cost": 45200,
            "faction_lock": ["Chorus of Silence"],
            "failure_chance": 0.03,
            "lore": (
                "Interlaced psionic fibers that read the dreams of nearby space. "
                "Provides uncanny insight, at the cost of unsettling the crew."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "etheric_sensitivity": 26,
                            "signature_analysis": 18,
                            "sensor_discipline": 12,
                            "noise_floor": -10,
                            "psycho_etheric_resonance": -6,
                            "cognitive_resonance": 6,
                        }
                    ]
                )
            ),
        },
        "Atlas Deep-Scan Spine": {
            "cost": 59800,
            "faction_lock": ["Atlas Cartography Guild"],
            "failure_chance": 0.027,
            "lore": (
                "A spinal sensor array that maps gravitational harmonics and subspace reefs. "
                "Indispensable to exploration flotillas charting the unknown."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "detection_range": 24,
                            "scan_resolution": 20,
                            "target_tracking_stability": 12,
                            "environmental_resilience": 10,
                            "reality_anchoring_strength": 12,
                            "energy_storage": -4,
                        }
                    ]
                )
            ),
        },
    },
    "support": {
        "Entropy Sink Array": {
            "cost": 32000,
            "faction_lock": None,
            "failure_chance": 0.025,
            "lore": (
                "Modular heat siphons and probability dampers siphon chaos away from the ship. "
                "Keeps systems cool, but pilots report dreams of falling snow."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "thermal_regulation": 22,
                            "entropy_management": 16,
                            "flux_tolerance": 10,
                            "crew_morale": -4,
                            "spectral_noise_emission": -6,
                        }
                    ]
                )
            ),
        },
        "Harmonic Choir Node": {
            "cost": 41000,
            "faction_lock": ["Chorus of Silence"],
            "failure_chance": 0.035,
            "lore": (
                "A chorus of resonant crystals amplifies etheric harmonics. "
                "Crew sessions around the node can steer fate—or unravel it."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "ether_machine_harmony": 18,
                            "resonance_stability": 12,
                            "ai_ether_integration": 14,
                            "psycho_etheric_resonance": 16,
                            "coherence_entropy": -12,
                        }
                    ]
                )
            ),
        },
        "Autoforge Bay": {
            "cost": 36500,
            "faction_lock": ["Guildhammer Combine"],
            "failure_chance": 0.03,
            "lore": (
                "Nanoforges knit spare parts and drones on demand. "
                "A ship fitted with an Autoforge seldom limps for long."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "maintenance_autonomy": 22,
                            "maintenance_complexity": 14,
                            "crew_efficiency": 12,
                            "structural_redundancy": 10,
                            "automation_level": 8,
                            "ai_processing_power": 6,
                            "power_distribution_efficiency": -4,
                        }
                    ]
                )
            ),
        },
        "Empathic Resonance Quarters": {
            "cost": 29800,
            "faction_lock": ["Harmonic Pavilion"],
            "failure_chance": 0.02,
            "lore": (
                "Meditative alcoves that tune crew emotions to the ship's etheric pulse. "
                "Gossip spreads quickly; so does calm resolve."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "crew_morale": 22,
                            "psycho_etheric_resonance": 18,
                            "human_ai_symbiosis": 14,
                            "cognitive_security": 6,
                            "information_security": 4,
                            "automation_level": -8,
                        }
                    ]
                )
            ),
        },
        "Synapse Bloom Neural Matrix": {
            "cost": 45500,
            "faction_lock": ["Transcendent Synod"],
            "failure_chance": 0.04,
            "lore": (
                "Bioluminescent neural pods extend the ship's conscious reach. "
                "They whisper in polyphonic dreams, seeking new solutions."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "ai_processing_power": 18,
                            "cognitive_resonance": 20,
                            "predictive_modeling_depth": 14,
                            "self_optimization_capacity": 12,
                            "dream_state_processing": 18,
                            "information_integrity": 6,
                            "psycho_etheric_resonance": -6,
                        }
                    ]
                )
            ),
        },
        "Navigator's Alembic": {
            "cost": 33200,
            "faction_lock": ["Chronomantic Concord"],
            "failure_chance": 0.03,
            "lore": (
                "An alchemical engine that distills probability gradients into navigational insight. "
                "Captains swear by its star-charts and curse its habit of rearranging furniture."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "predictive_modeling_depth": 16,
                            "causal_mapping_precision": 14,
                            "chrono_adaptability": 10,
                            "chrono_symphony": 8,
                            "latency_control": 6,
                        }
                    ]
                )
            ),
        },
        "Panacea Flow Medbay": {
            "cost": 40200,
            "faction_lock": ["Harmonic Pavilion"],
            "failure_chance": 0.02,
            "lore": (
                "Biostabilizing medpods circulate tuning harmonics through crew physiology. "
                "Reduces downtime and keeps morale high—at the price of dreamy reveries."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "life_support_robustness": 24,
                            "crew_efficiency": 16,
                            "crew_morale": 18,
                            "psycho_etheric_resonance": 12,
                            "automation_level": -4,
                            "entropy_management": 6,
                        }
                    ]
                )
            ),
        },
    },
    "computing": {
        "Quantum Loom Core": {
            "cost": 54200,
            "faction_lock": ["Transcendent Synod"],
            "failure_chance": 0.035,
            "lore": (
                "Entangled threads weave future possibilities into actionable insight. "
                "Requires constant pruning lest the loom spin paradoxical tapestries."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "quantum_compute_efficiency": 24,
                            "processing_density": 18,
                            "predictive_modeling_depth": 18,
                            "parallel_synchrony": 16,
                            "entropy_management": 12,
                            "decision_latency": -10,
                            "self_optimization_capacity": 10,
                        }
                    ]
                )
            ),
        },
        "Aurora Conscience Matrix": {
            "cost": 60800,
            "faction_lock": ["Solar Wardens"],
            "failure_chance": 0.028,
            "lore": (
                "A luminous core housing ethic-coded AI mentors. "
                "Elevates decision making and enforces graceful conduct in battle."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "ai_processing_power": 16,
                            "ethical_constraints": 20,
                            "human_ai_symbiosis": 14,
                            "cognitive_security": 12,
                            "information_integrity": 12,
                            "ship_sentience": 10,
                            "dream_state_processing": 8,
                        }
                    ]
                )
            ),
        },
        "Fractal Muse Engine": {
            "cost": 49700,
            "faction_lock": ["Aetheric Nomads"],
            "failure_chance": 0.04,
            "lore": (
                "A creative computing array that generates fractal inspirations. "
                "Boosts scientific output and occasionally composes haunting lullabies."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "cognitive_growth_potential": 20,
                            "scientific_instrumentation": 16,
                            "self_optimization_capacity": 12,
                            "dream_state_processing": 14,
                            "parallel_synchrony": 10,
                            "entropy_management": -6,
                        }
                    ]
                )
            ),
        },
    },
    "communications": {
        "Stellar Chorus Beacon": {
            "cost": 29800,
            "faction_lock": ["Chorus of Silence"],
            "failure_chance": 0.022,
            "lore": (
                "A harmonic broadcast array that threads encrypted psalms across subspace. "
                "Its signals calm allies and confuse eavesdroppers."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "transmission_bandwidth": 16,
                            "etheric_signal_clarity": 18,
                            "information_security": 14,
                            "fleet_synchronization": 10,
                            "latency_control": 8,
                            "psycho_etheric_resonance": 8,
                        }
                    ]
                )
            ),
        },
        "Gravitic Pulse Array": {
            "cost": 35500,
            "faction_lock": ["Atlantean Gradient"],
            "failure_chance": 0.03,
            "lore": (
                "Gravitic pulses encode messages in spacetime ripples. "
                "Hard to jam, harder still to decode without the right lens."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "transmission_bandwidth": 18,
                            "quantum_link_stability": 16,
                            "protocol_interoperability": 12,
                            "latency_control": 12,
                            "reality_anchoring_strength": 8,
                            "spectral_noise_emission": 6,
                        }
                    ]
                )
            ),
        },
        "Echo Lantern Relay": {
            "cost": 26800,
            "faction_lock": None,
            "failure_chance": 0.024,
            "lore": (
                "Portable relays carried by traders to maintain contact across treacherous lanes. "
                "They whisper rumors, news, and the occasional ghost story."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "transmission_bandwidth": 12,
                            "protocol_interoperability": 14,
                            "information_security": 10,
                            "fleet_synchronization": 8,
                            "crew_morale": 6,
                            "etheric_signature": 4,
                        }
                    ]
                )
            ),
        },
    },
    "crew_modules": {
        "Command Resonance Theater": {
            "cost": 38200,
            "faction_lock": ["Harmonic Pavilion"],
            "failure_chance": 0.025,
            "lore": (
                "An amphitheater of holo-choral interfaces that project battle plans as symphonies. "
                "Officers direct fleets like conductors wielding cosmic scores."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "command_feedback_clarity": 22,
                            "crew_efficiency": 16,
                            "fleet_synchronization": 14,
                            "human_ai_symbiosis": 10,
                            "weapon_accuracy": 8,
                            "psycho_etheric_resonance": 8,
                        }
                    ]
                )
            ),
        },
        "Wardens' Bulwark Barracks": {
            "cost": 31500,
            "faction_lock": ["Solar Wardens"],
            "failure_chance": 0.02,
            "lore": (
                "Fortified barracks drilled in paladin discipline. "
                "Crew share vows beneath stained glass, emerging fierce and unbreakable."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "crew_morale": 18,
                            "crew_efficiency": 16,
                            "psycho_etheric_resonance": 10,
                            "damage_control_automation": 8,
                            "armor_strength": 8,
                            "ethical_constraints": 6,
                        }
                    ]
                )
            ),
        },
        "Nomad Dream Commons": {
            "cost": 27400,
            "faction_lock": ["Free Pilgrim Clans"],
            "failure_chance": 0.018,
            "lore": (
                "Communal dream-chambers where pilgrims share visions of distant stars. "
                "Boosts adaptability and keeps spirits kindled during long drifts."
            ),
            "attributes": clamp_attribute_profile(
                merge_attribute_profiles(
                    [
                        {
                            "adaptation_index": 18,
                            "crew_morale": 16,
                            "cognitive_growth_potential": 12,
                            "dream_state_processing": 12,
                            "psycho_etheric_resonance": 14,
                            "automation_level": -4,
                        }
                    ]
                )
            ),
        },
    },
}

ship_templates: Dict[str, Mapping[str, object]] = {}

COMPONENT_CATEGORY_ALIASES: Dict[str, str] = {
    "hull": "hulls",
    "hulls": "hulls",
    "engine": "engines",
    "engines": "engines",
    "weapons": "weapons",
    "weapon": "weapons",
    "shields": "shields",
    "shield": "shields",
    "sensors": "sensors",
    "sensor": "sensors",
    "support": "support",
    "special": "support",
    "computing": "computing",
    "communications": "communications",
    "crew_modules": "crew_modules",
    "crew": "crew_modules",
}

COMPONENT_CATEGORY_LABELS: Dict[str, str] = {
    "hulls": "Hull",
    "engines": "Engine",
    "weapons": "Weapon",
    "shields": "Shield",
    "sensors": "Sensor Suite",
    "support": "Support Module",
    "computing": "Computing Core",
    "communications": "Communications Array",
    "crew_modules": "Crew Module",
}


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
                "name": name,
                "label": COMPONENT_CATEGORY_LABELS.get(category, category.title()),
                "data": data,
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
        "total_cost": total_cost,
        "combined_failure_chance": combined_failure,
        "faction_locks": sorted(faction_locks),
        "entries": entries,
    }


# -----------------------------------------------------------------------------
# Power usage scaffolding (placeholder implementation).
# -----------------------------------------------------------------------------


def calculate_power_usage(_components: Mapping[str, object]) -> Dict[str, float]:
    """
    Placeholder power usage calculation that keeps the previous public API.

    Returns zeroed values so downstream code can continue working until the new
    component data is authored.
    """

    return {
        "power_output": 0.0,
        "power_used": 0.0,
        "power_available": 0.0,
        "power_percentage": 0.0,
    }


def calculate_ship_stats(components: Mapping[str, object]) -> Dict[str, object]:
    """
    Backwards-compatible helper retained for callers in :mod:`game`.

    Returns a dictionary containing legacy aggregate numbers alongside the full
    attribute profile and metadata.
    """

    profile = compute_ship_profile(components)
    metadata = aggregate_component_metadata(components)

    health = max(100, int(profile.get("hull_integrity", 30.0) * 10))
    cargo_space = max(30, int(profile.get("mass_efficiency", 30.0) * 3 + profile.get("hull_integrity", 30.0)))
    speed = max(1.0, profile.get("engine_output", 30.0) / 10.0 + profile.get("maneuverability", 30.0) / 12.0)

    return {
        "profile": profile,
        "metadata": metadata,
        "health": health,
        "cargo_space": cargo_space,
        "speed": speed,
        "total_cost": metadata.get("total_cost", 0.0),
    }


__all__ = [
    "ship_components",
    "ship_templates",
    "COMPONENT_CATEGORY_ALIASES",
    "COMPONENT_CATEGORY_LABELS",
    "empty_attribute_profile",
    "clamp_attribute_profile",
    "merge_attribute_profiles",
    "collect_component_entries",
    "compute_ship_profile",
    "aggregate_component_metadata",
    "calculate_power_usage",
    "calculate_ship_stats",
]