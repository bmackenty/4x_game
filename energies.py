"""
Energy Systems Database for 4X Galactic Empire Management Game
Year 7019 - Celestial Alliance Era

This file contains all known energy types used to power ships, stations,
and advanced technologies across the galaxy.
"""

# Physical & Technological Energies
physical_energies = {
    "Kinetic Energy": {
        "category": "Physical",
        "description": "Generated through motion, used in weapons and propulsion systems.",
        "efficiency": 0.8,
        "stability": 0.9,
        "availability": 0.95,
        "cost_multiplier": 1.0,
        "applications": ["Weapons", "Propulsion", "Kinetic Shields"],
        "safety_level": "Safe",
        "environmental_impact": "Low"
    },
    "Thermal Energy": {
        "category": "Physical",
        "description": "Harvested from planetary cores, stars, and volcanic systems.",
        "efficiency": 0.7,
        "stability": 0.8,
        "availability": 0.85,
        "cost_multiplier": 0.8,
        "applications": ["Power Generation", "Heating Systems", "Industrial Processes"],
        "safety_level": "Safe",
        "environmental_impact": "Medium"
    },
    "Gravitational Energy": {
        "category": "Physical",
        "description": "Used for artificial gravity and planetary manipulation.",
        "efficiency": 0.6,
        "stability": 0.7,
        "availability": 0.6,
        "cost_multiplier": 1.5,
        "applications": ["Artificial Gravity", "Planetary Manipulation", "Gravity Wells"],
        "safety_level": "Caution",
        "environmental_impact": "High"
    },
    "Nuclear Energy": {
        "category": "Physical",
        "description": "Derived from fission/fusion reactions; still used in older technology.",
        "efficiency": 0.9,
        "stability": 0.6,
        "availability": 0.9,
        "cost_multiplier": 0.7,
        "applications": ["Power Reactors", "Weapons", "Propulsion"],
        "safety_level": "Dangerous",
        "environmental_impact": "High"
    },
    "Electromagnetic Energy": {
        "category": "Physical",
        "description": "Includes all EM spectrum uses: communications, sensors, and shields.",
        "efficiency": 0.85,
        "stability": 0.9,
        "availability": 0.95,
        "cost_multiplier": 1.0,
        "applications": ["Communications", "Sensors", "Shields", "Weapons"],
        "safety_level": "Safe",
        "environmental_impact": "Low"
    },
    "Plasma Energy": {
        "category": "Physical",
        "description": "High-temperature ionized gas, common in weapons and engines.",
        "efficiency": 0.8,
        "stability": 0.5,
        "availability": 0.8,
        "cost_multiplier": 1.2,
        "applications": ["Weapons", "Engines", "Shields"],
        "safety_level": "Caution",
        "environmental_impact": "Medium"
    },
    "Zero-Point Energy": {
        "category": "Physical",
        "description": "Theoretical baseline energy of the vacuum, tapped by advanced civilizations.",
        "efficiency": 0.95,
        "stability": 0.3,
        "availability": 0.2,
        "cost_multiplier": 3.0,
        "applications": ["Power Generation", "Propulsion", "Advanced Weapons"],
        "safety_level": "Extremely Dangerous",
        "environmental_impact": "Unknown"
    },
    "Quantum Flux": {
        "category": "Physical",
        "description": "Unstable but potent; used in teleportation and reality-altering tech.",
        "efficiency": 0.7,
        "stability": 0.2,
        "availability": 0.3,
        "cost_multiplier": 2.5,
        "applications": ["Teleportation", "Reality Manipulation", "Quantum Computing"],
        "safety_level": "Extremely Dangerous",
        "environmental_impact": "Unknown"
    },
    "Dark Matter Energy": {
        "category": "Physical",
        "description": "Harnessed from exotic particles; key to stealth and shadow tech.",
        "efficiency": 0.6,
        "stability": 0.4,
        "availability": 0.1,
        "cost_multiplier": 4.0,
        "applications": ["Stealth Systems", "Shadow Tech", "Cloaking"],
        "safety_level": "Dangerous",
        "environmental_impact": "Unknown"
    },
    "Antimatter": {
        "category": "Physical",
        "description": "Dangerous and volatile, used in high-yield reactors.",
        "efficiency": 1.0,
        "stability": 0.1,
        "availability": 0.4,
        "cost_multiplier": 5.0,
        "applications": ["High-Yield Reactors", "Weapons", "Propulsion"],
        "safety_level": "Extremely Dangerous",
        "environmental_impact": "Catastrophic"
    },
    "Neutrino Energy": {
        "category": "Physical",
        "description": "Clean and hard to detect, ideal for covert power systems.",
        "efficiency": 0.4,
        "stability": 0.9,
        "availability": 0.6,
        "cost_multiplier": 2.0,
        "applications": ["Covert Power", "Stealth Operations", "Clean Energy"],
        "safety_level": "Safe",
        "environmental_impact": "None"
    }
}

# Mystical & Etheric Energies
mystical_energies = {
    "Etheric Energy": {
        "category": "Mystical",
        "description": "The fundamental magical force woven into the universe.",
        "efficiency": 0.9,
        "stability": 0.8,
        "availability": 0.7,
        "cost_multiplier": 1.5,
        "applications": ["Magic Systems", "Etheric Tech", "Reality Manipulation"],
        "safety_level": "Caution",
        "environmental_impact": "Medium",
        "magical_level": "High"
    },
    "Leyline Currents": {
        "category": "Mystical",
        "description": "Flowing mystical energies connecting worlds and nodes.",
        "efficiency": 0.8,
        "stability": 0.6,
        "availability": 0.5,
        "cost_multiplier": 1.8,
        "applications": ["Long-Range Power", "Planetary Networks", "Magic Amplification"],
        "safety_level": "Caution",
        "environmental_impact": "Medium",
        "magical_level": "High"
    },
    "Soul Energy": {
        "category": "Mystical",
        "description": "Life-force power, used by some necromantic or healing practices.",
        "efficiency": 0.6,
        "stability": 0.7,
        "availability": 0.8,
        "cost_multiplier": 2.0,
        "applications": ["Healing", "Necromancy", "Life Support"],
        "safety_level": "Dangerous",
        "environmental_impact": "High",
        "magical_level": "Very High"
    },
    "Aether Flames": {
        "category": "Mystical",
        "description": "Energetic wisps used for both spiritual and combat rituals.",
        "efficiency": 0.7,
        "stability": 0.5,
        "availability": 0.6,
        "cost_multiplier": 1.7,
        "applications": ["Combat Magic", "Spiritual Rituals", "Purification"],
        "safety_level": "Caution",
        "environmental_impact": "Medium",
        "magical_level": "High"
    },
    "Astral Energy": {
        "category": "Mystical",
        "description": "Drawn from the astral plane, used in dreams and divination.",
        "efficiency": 0.5,
        "stability": 0.8,
        "availability": 0.4,
        "cost_multiplier": 2.2,
        "applications": ["Divination", "Dream Magic", "Astral Projection"],
        "safety_level": "Caution",
        "environmental_impact": "Low",
        "magical_level": "Very High"
    },
    "Mana": {
        "category": "Mystical",
        "description": "A classic reservoir of magical force, used in spellcasting.",
        "efficiency": 0.8,
        "stability": 0.9,
        "availability": 0.8,
        "cost_multiplier": 1.3,
        "applications": ["Spellcasting", "Magic Systems", "Enchantments"],
        "safety_level": "Safe",
        "environmental_impact": "Low",
        "magical_level": "Medium"
    },
    "Chrono-Energy": {
        "category": "Mystical",
        "description": "Temporal power used for time manipulation or travel.",
        "efficiency": 0.6,
        "stability": 0.3,
        "availability": 0.2,
        "cost_multiplier": 3.5,
        "applications": ["Time Manipulation", "Temporal Travel", "Chronology"],
        "safety_level": "Extremely Dangerous",
        "environmental_impact": "Unknown",
        "magical_level": "Extreme"
    },
    "Void Essence": {
        "category": "Mystical",
        "description": "Dark, nihilistic energy from the edge of reality, feared and forbidden.",
        "efficiency": 0.9,
        "stability": 0.1,
        "availability": 0.1,
        "cost_multiplier": 6.0,
        "applications": ["Forbidden Magic", "Reality Destruction", "Void Weapons"],
        "safety_level": "Forbidden",
        "environmental_impact": "Catastrophic",
        "magical_level": "Extreme"
    },
    "Divine Light": {
        "category": "Mystical",
        "description": "Sacred energy tied to gods or celestial entities.",
        "efficiency": 0.95,
        "stability": 0.9,
        "availability": 0.3,
        "cost_multiplier": 2.8,
        "applications": ["Divine Magic", "Healing", "Purification"],
        "safety_level": "Safe",
        "environmental_impact": "Positive",
        "magical_level": "Extreme"
    },
    "Shadow Flux": {
        "category": "Mystical",
        "description": "Opposing Divine Light, often used in stealth and curse magic.",
        "efficiency": 0.8,
        "stability": 0.6,
        "availability": 0.4,
        "cost_multiplier": 2.0,
        "applications": ["Stealth Magic", "Curses", "Shadow Manipulation"],
        "safety_level": "Dangerous",
        "environmental_impact": "Negative",
        "magical_level": "High"
    }
}

# Psychic & Consciousness-Based Energies
psychic_energies = {
    "Psionic Energy": {
        "category": "Psychic",
        "description": "Mental power enabling telepathy, telekinesis, or illusion.",
        "efficiency": 0.7,
        "stability": 0.6,
        "availability": 0.6,
        "cost_multiplier": 1.8,
        "applications": ["Telepathy", "Telekinesis", "Illusions", "Mind Control"],
        "safety_level": "Caution",
        "environmental_impact": "Medium",
        "psychic_level": "High"
    },
    "Empathic Resonance": {
        "category": "Psychic",
        "description": "Energy generated by strong emotional fields, used in diplomacy and healing.",
        "efficiency": 0.6,
        "stability": 0.7,
        "availability": 0.7,
        "cost_multiplier": 1.5,
        "applications": ["Diplomacy", "Healing", "Emotional Manipulation"],
        "safety_level": "Safe",
        "environmental_impact": "Low",
        "psychic_level": "Medium"
    },
    "Noospheric Energy": {
        "category": "Psychic",
        "description": "Collective consciousness field of intelligent species.",
        "efficiency": 0.8,
        "stability": 0.8,
        "availability": 0.5,
        "cost_multiplier": 2.2,
        "applications": ["Collective Intelligence", "Hive Mind", "Group Consciousness"],
        "safety_level": "Caution",
        "environmental_impact": "Medium",
        "psychic_level": "Very High"
    },
    "Dream Energy": {
        "category": "Psychic",
        "description": "Manifested in dreamscapes; fuels illusion magic or subconscious computation.",
        "efficiency": 0.5,
        "stability": 0.4,
        "availability": 0.8,
        "cost_multiplier": 1.6,
        "applications": ["Illusion Magic", "Subconscious Computing", "Dream Manipulation"],
        "safety_level": "Caution",
        "environmental_impact": "Low",
        "psychic_level": "High"
    },
    "Cognitive Pulse": {
        "category": "Psychic",
        "description": "Energy emitted during intense thought or focus; used in mental networks.",
        "efficiency": 0.6,
        "stability": 0.7,
        "availability": 0.9,
        "cost_multiplier": 1.2,
        "applications": ["Mental Networks", "AI Communication", "Focus Enhancement"],
        "safety_level": "Safe",
        "environmental_impact": "None",
        "psychic_level": "Medium"
    },
    "Neural Sync Fields": {
        "category": "Psychic",
        "description": "Required for AI-organic communication and control systems.",
        "efficiency": 0.8,
        "stability": 0.9,
        "availability": 0.7,
        "cost_multiplier": 1.4,
        "applications": ["AI-Organic Interface", "Neural Control", "Mind-Machine Link"],
        "safety_level": "Caution",
        "environmental_impact": "Low",
        "psychic_level": "High"
    }
}

# Exotic & Speculative Energies
exotic_energies = {
    "Hyperdimensional Energy": {
        "category": "Exotic",
        "description": "Accessed from other dimensions; unstable but powerful.",
        "efficiency": 0.9,
        "stability": 0.2,
        "availability": 0.1,
        "cost_multiplier": 4.5,
        "applications": ["Dimensional Travel", "Reality Manipulation", "Exotic Weapons"],
        "safety_level": "Extremely Dangerous",
        "environmental_impact": "Unknown"
    },
    "Tachyonic Currents": {
        "category": "Exotic",
        "description": "Used for FTL communication and predictive algorithms.",
        "efficiency": 0.7,
        "stability": 0.5,
        "availability": 0.3,
        "cost_multiplier": 3.0,
        "applications": ["FTL Communication", "Predictive Algorithms", "Temporal Sensors"],
        "safety_level": "Dangerous",
        "environmental_impact": "Unknown"
    },
    "Chrono-Synthetic Flux": {
        "category": "Exotic",
        "description": "Found in time-distorted regions; affects ship travel speeds.",
        "efficiency": 0.6,
        "stability": 0.3,
        "availability": 0.2,
        "cost_multiplier": 3.5,
        "applications": ["Time Distortion", "Speed Manipulation", "Temporal Fields"],
        "safety_level": "Extremely Dangerous",
        "environmental_impact": "Unknown"
    },
    "Anima Energy": {
        "category": "Exotic",
        "description": "Linked to planetary or biosphere consciousness.",
        "efficiency": 0.7,
        "stability": 0.8,
        "availability": 0.4,
        "cost_multiplier": 2.5,
        "applications": ["Planetary Consciousness", "Biosphere Control", "Gaia Systems"],
        "safety_level": "Caution",
        "environmental_impact": "High"
    },
    "Phantom Energy": {
        "category": "Exotic",
        "description": "Hypothetical energy contributing to the accelerated expansion of the universe.",
        "efficiency": 0.8,
        "stability": 0.4,
        "availability": 0.05,
        "cost_multiplier": 8.0,
        "applications": ["Universe Manipulation", "Expansion Control", "Cosmic Engineering"],
        "safety_level": "Forbidden",
        "environmental_impact": "Catastrophic"
    },
    "Entropy Reversal Fields": {
        "category": "Exotic",
        "description": "Energy required to reverse decay or maintain youth.",
        "efficiency": 0.6,
        "stability": 0.6,
        "availability": 0.3,
        "cost_multiplier": 4.0,
        "applications": ["Anti-Aging", "Decay Reversal", "Youth Maintenance"],
        "safety_level": "Dangerous",
        "environmental_impact": "Unknown"
    },
    "Echo Energy": {
        "category": "Exotic",
        "description": "Residual power from lost civilizations or ancient battles.",
        "efficiency": 0.5,
        "stability": 0.7,
        "availability": 0.6,
        "cost_multiplier": 2.0,
        "applications": ["Archaeological Power", "Ancient Tech", "Historical Resonance"],
        "safety_level": "Caution",
        "environmental_impact": "Medium"
    },
    "Mythic Resonance": {
        "category": "Exotic",
        "description": "Semi-symbolic energy that manifests based on cultural or belief strength.",
        "efficiency": 0.4,
        "stability": 0.8,
        "availability": 0.7,
        "cost_multiplier": 1.8,
        "applications": ["Cultural Magic", "Belief Systems", "Mythological Power"],
        "safety_level": "Safe",
        "environmental_impact": "Low"
    },
    "Probability Fields": {
        "category": "Exotic",
        "description": "Energy used to manipulate outcomes; rare and controversial.",
        "efficiency": 0.7,
        "stability": 0.3,
        "availability": 0.2,
        "cost_multiplier": 5.0,
        "applications": ["Outcome Manipulation", "Probability Control", "Luck Systems"],
        "safety_level": "Forbidden",
        "environmental_impact": "Unknown"
    },
    "Singularity Energy": {
        "category": "Exotic",
        "description": "Tapped from black holes or artificial singularities.",
        "efficiency": 0.95,
        "stability": 0.1,
        "availability": 0.1,
        "cost_multiplier": 6.0,
        "applications": ["Massive Power Generation", "Gravity Manipulation", "Singularity Weapons"],
        "safety_level": "Extremely Dangerous",
        "environmental_impact": "Catastrophic"
    }
}

# Utility & Industrial Energies
utility_energies = {
    "Synthetic Bio-Energy": {
        "category": "Utility",
        "description": "Engineered biological energy used in living machines.",
        "efficiency": 0.7,
        "stability": 0.8,
        "availability": 0.8,
        "cost_multiplier": 1.3,
        "applications": ["Living Machines", "Bio-Tech", "Organic Systems"],
        "safety_level": "Safe",
        "environmental_impact": "Low"
    },
    "Geo-Energy": {
        "category": "Utility",
        "description": "Planet-based renewable energy, especially from tectonic activity.",
        "efficiency": 0.6,
        "stability": 0.9,
        "availability": 0.9,
        "cost_multiplier": 0.8,
        "applications": ["Planetary Power", "Tectonic Harvesting", "Renewable Energy"],
        "safety_level": "Safe",
        "environmental_impact": "Low"
    },
    "Photonic Power": {
        "category": "Utility",
        "description": "Light-based energy; used in clean power systems.",
        "efficiency": 0.8,
        "stability": 0.9,
        "availability": 0.95,
        "cost_multiplier": 1.0,
        "applications": ["Clean Power", "Solar Systems", "Light-Based Tech"],
        "safety_level": "Safe",
        "environmental_impact": "None"
    },
    "Cryo-Energy": {
        "category": "Utility",
        "description": "Stored cold for temperature regulation or freezing tech.",
        "efficiency": 0.6,
        "stability": 0.8,
        "availability": 0.8,
        "cost_multiplier": 1.2,
        "applications": ["Temperature Control", "Cryogenic Systems", "Freezing Tech"],
        "safety_level": "Safe",
        "environmental_impact": "Low"
    },
    "Chemical Energy": {
        "category": "Utility",
        "description": "Still used in less advanced worlds and in biochemical systems.",
        "efficiency": 0.5,
        "stability": 0.9,
        "availability": 0.95,
        "cost_multiplier": 0.7,
        "applications": ["Basic Power", "Biochemical Systems", "Traditional Tech"],
        "safety_level": "Safe",
        "environmental_impact": "Medium"
    },
    "Molecular Torque": {
        "category": "Utility",
        "description": "Energy from controlled molecular friction in nanotech engines.",
        "efficiency": 0.8,
        "stability": 0.7,
        "availability": 0.7,
        "cost_multiplier": 1.5,
        "applications": ["Nanotech Engines", "Molecular Systems", "Precision Tech"],
        "safety_level": "Caution",
        "environmental_impact": "Low"
    }
}

# Faction-Specific Energies
faction_energies = {
    "Concordant Harmony": {
        "category": "Faction-Specific",
        "description": "Used by the Harmonic Resonance Collective; balances technology and life.",
        "efficiency": 0.8,
        "stability": 0.9,
        "availability": 0.4,
        "cost_multiplier": 2.0,
        "applications": ["Harmonic Systems", "Life-Tech Balance", "Resonance Tech"],
        "safety_level": "Safe",
        "environmental_impact": "Positive",
        "faction": "Harmonic Resonance Collective"
    },
    "Veritas Pulse": {
        "category": "Faction-Specific",
        "description": "Used by the Veritas Covenant, believed to align with truth and clarity.",
        "efficiency": 0.9,
        "stability": 0.8,
        "availability": 0.3,
        "cost_multiplier": 2.5,
        "applications": ["Truth Detection", "Clarity Systems", "Veritas Tech"],
        "safety_level": "Safe",
        "environmental_impact": "Positive",
        "faction": "Veritas Covenant"
    },
    "Technotheos Charge": {
        "category": "Faction-Specific",
        "description": "Sacred energy harnessed by techno-religious orders.",
        "efficiency": 0.7,
        "stability": 0.8,
        "availability": 0.5,
        "cost_multiplier": 1.8,
        "applications": ["Sacred Tech", "Religious Systems", "Divine Technology"],
        "safety_level": "Caution",
        "environmental_impact": "Medium",
        "faction": "Technotheos"
    },
    "Silvan Bloomforce": {
        "category": "Faction-Specific",
        "description": "Bio-mystical energy tied to flora and forest worlds.",
        "efficiency": 0.8,
        "stability": 0.9,
        "availability": 0.6,
        "cost_multiplier": 1.6,
        "applications": ["Bio-Mystical Tech", "Forest Systems", "Plant-Based Power"],
        "safety_level": "Safe",
        "environmental_impact": "Positive",
        "faction": "Silvan"
    },
    "Quantum Choir": {
        "category": "Faction-Specific",
        "description": "Collective energy from AI minds syncing in harmonic networks.",
        "efficiency": 0.9,
        "stability": 0.7,
        "availability": 0.4,
        "cost_multiplier": 2.2,
        "applications": ["AI Networks", "Collective Intelligence", "Harmonic AI"],
        "safety_level": "Caution",
        "environmental_impact": "Medium",
        "faction": "Synthetix"
    }
}

# Chaotic & Unstable Energies
chaotic_energies = {
    "Chaotic Potential": {
        "category": "Chaotic",
        "description": "Highly volatile energy harvested from disorder and unpredictability. Banned by the Icaron Collective.",
        "efficiency": 1.0,
        "stability": 0.05,
        "availability": 0.3,
        "cost_multiplier": 8.0,
        "applications": ["Unlimited Power", "Reality Manipulation", "Chaos Weapons"],
        "safety_level": "Forbidden",
        "environmental_impact": "Catastrophic",
        "warning": "Three moons vanished during Icaron Collective experiments",
        "banned_by": ["Icaron Collective"]
    }
}

# Combine all energy types
all_energies = {
    **physical_energies,
    **mystical_energies,
    **psychic_energies,
    **exotic_energies,
    **utility_energies,
    **faction_energies,
    **chaotic_energies
}

# Energy categories for easy access
energy_categories = {
    "Physical": physical_energies,
    "Mystical": mystical_energies,
    "Psychic": psychic_energies,
    "Exotic": exotic_energies,
    "Utility": utility_energies,
    "Faction-Specific": faction_energies,
    "Chaotic": chaotic_energies
}

def get_energy_by_category(category):
    """Get all energies in a specific category."""
    return energy_categories.get(category, {})

def get_safe_energies():
    """Get all energies with safe safety levels."""
    return {name: data for name, data in all_energies.items() 
            if data.get("safety_level") == "Safe"}

def get_dangerous_energies():
    """Get all energies with dangerous or forbidden safety levels."""
    return {name: data for name, data in all_energies.items() 
            if data.get("safety_level") in ["Dangerous", "Extremely Dangerous", "Forbidden"]}

def get_energy_efficiency(energy_name):
    """Get the efficiency rating of a specific energy type."""
    energy = all_energies.get(energy_name)
    return energy.get("efficiency", 0.5) if energy else 0.5

def get_energy_stability(energy_name):
    """Get the stability rating of a specific energy type."""
    energy = all_energies.get(energy_name)
    return energy.get("stability", 0.5) if energy else 0.5

def get_energy_cost_multiplier(energy_name):
    """Get the cost multiplier for a specific energy type."""
    energy = all_energies.get(energy_name)
    return energy.get("cost_multiplier", 1.0) if energy else 1.0

def get_energy_applications(energy_name):
    """Get the applications for a specific energy type."""
    energy = all_energies.get(energy_name)
    return energy.get("applications", []) if energy else []

def get_energy_safety_level(energy_name):
    """Get the safety level of a specific energy type."""
    energy = all_energies.get(energy_name)
    return energy.get("safety_level", "Unknown") if energy else "Unknown"

def calculate_power_output(energy_name, base_power):
    """Calculate actual power output based on energy efficiency."""
    efficiency = get_energy_efficiency(energy_name)
    return base_power * efficiency

def calculate_energy_cost(energy_name, base_cost):
    """Calculate actual energy cost based on cost multiplier."""
    multiplier = get_energy_cost_multiplier(energy_name)
    return base_cost * multiplier

def get_energy_compatibility(ship_type, energy_name):
    """Check if an energy type is compatible with a ship type."""
    energy = all_energies.get(energy_name)
    if not energy:
        return False
    
    # Basic compatibility check based on safety level
    safety_level = energy.get("safety_level", "Unknown")
    if safety_level in ["Forbidden", "Extremely Dangerous"]:
        return False
    
    return True

def get_recommended_energies(ship_type):
    """Get recommended energy types for a specific ship type."""
    recommended = []
    
    for energy_name, energy_data in all_energies.items():
        if energy_data.get("safety_level") == "Safe" and energy_data.get("efficiency", 0) >= 0.7:
            recommended.append(energy_name)
    
    return recommended[:5]  # Return top 5 recommendations
