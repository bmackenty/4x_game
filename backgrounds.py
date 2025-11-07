"""
Backgrounds for 7019 - Character Creation
Each background provides narrative context and mechanical bonuses.
"""

backgrounds = {
    "Orbital Foundling": {
        "description": "Raised in a decaying orbital station where survival meant improvisation and stealth.",
        "stat_bonuses": {
            "KIN": 1,
            "SYN": 1
        },
        "talent": "Microgravity Adaptation: Never suffers movement penalties in low-gravity environments."
    },
    "Deep-Core Miner": {
        "description": "Born and bred in high-pressure subterranean colonies extracting etheric ore.",
        "stat_bonuses": {
            "VIT": 2
        },
        "talent": "Pressure Hardened: Immune to environmental compression and toxic gas effects."
    },
    "AI Scribe": {
        "description": "Mentored by machine intellects that taught logic, language compression, and emotion-syntax balance.",
        "stat_bonuses": {
            "INT": 1,
            "COH": 1
        },
        "talent": "Cognitive Compression: Reduce analysis time or computation by half once per day."
    },
    "Etherborn Nomad": {
        "description": "Descendant of those who wander ether streams; can feel energetic tides like weather.",
        "stat_bonuses": {
            "AEF": 2
        },
        "talent": "Resonant Sense: Detect Etheric fluctuations or nearby energy fields instinctively."
    },
    "Reclamation Diver": {
        "description": "Salvager of drowned megacities and sunken relics of pre-expansion humanity.",
        "stat_bonuses": {
            "KIN": 1,
            "VIT": 1
        },
        "talent": "Pressure Seal: Can operate underwater or in corrosive atmospheres for extended durations."
    },
    "Neo-Monastic Archivist": {
        "description": "Scholar-monks preserving digital scripture and forgotten algorithms.",
        "stat_bonuses": {
            "COH": 2
        },
        "talent": "Memory Sanctuary: Immune to memory corruption or forced recollection once per rest."
    },
    "Bioforge Technician": {
        "description": "Grew up among vats and splicing labs designing living tools and symbiotic materials.",
        "stat_bonuses": {
            "SYN": 1,
            "INT": 1
        },
        "talent": "Bio-Interface: Gains advantage on checks involving bio-tech repair or synthesis."
    },
    "Street Synth": {
        "description": "Raised in overbuilt arcologies; part organic, part streetware. Knows how to slip through systems.",
        "stat_bonuses": {
            "KIN": 1,
            "INF": 1
        },
        "talent": "Urban Ghost: Always counts as lightly obscured in crowded or neon-dense environments."
    },
    "Voidfarer Crew": {
        "description": "Spent youth aboard deep-space haulers, navigating quantum storms and engine spirits.",
        "stat_bonuses": {
            "AEF": 1,
            "VIT": 1
        },
        "talent": "Zero Drift: Immune to spatial disorientation or motion sickness."
    },
    "Chrono-Refugee": {
        "description": "Escaped a time-distorted region; perception of cause and effect is slightly off.",
        "stat_bonuses": {
            "COH": 1,
            "AEF": 1
        },
        "talent": "Temporal Flicker: Once per day, reroll an initiative or timing-based test."
    },
    "Planetary Ranger": {
        "description": "Custodian of reclaimed wilderness and terraformed biomes.",
        "stat_bonuses": {
            "VIT": 1,
            "INF": 1
        },
        "talent": "Field Survivalist: Immune to starvation or dehydration effects."
    },
    "Quantum Savant": {
        "description": "A child exposed to superposition training—raised to think in probability clouds.",
        "stat_bonuses": {
            "INT": 2
        },
        "talent": "Quantum Insight: Once per encounter, predict an outcome with statistical accuracy (advantage on a single decision roll)."
    },
    "Drift-Station Merchant": {
        "description": "Grew up bartering with a thousand species and AIs in free-trade voids.",
        "stat_bonuses": {
            "INF": 2
        },
        "talent": "Polyglot Interface: Automatically understands intent across languages and trade codes."
    },
    "Nanite Ascetic": {
        "description": "Member of a sect that replaces bodily needs with self-sustaining nanite colonies.",
        "stat_bonuses": {
            "COH": 1,
            "VIT": 1
        },
        "talent": "Self-Repair: Regain minor health without external aid once per day."
    },
    "Warfleet Remnant": {
        "description": "Descendant of military fleets long decommissioned; disciplined, austere, relentless.",
        "stat_bonuses": {
            "KIN": 2
        },
        "talent": "Combat Instinct: Gain initiative advantage in the first round of any conflict."
    },
    "Datawalker": {
        "description": "A consciousness originally uploaded and later re-embodied—half ghost, half code.",
        "stat_bonuses": {
            "SYN": 1,
            "COH": 1
        },
        "talent": "Digital Doppel: Can project a brief data-clone to perform a simple task once per rest."
    },
    "Brewmasters' Acolyte": {
        "description": "Initiate of the Guild that binds spirit, fermentation, and Ether in sacred communion.",
        "stat_bonuses": {
            "AEF": 1,
            "INF": 1
        },
        "talent": "Liquid Resonance: Share calm or courage through crafted drink; minor morale boost in allies."
    },
    "Industrial Heir": {
        "description": "Scion of a planetary fabrication dynasty, educated in design, diplomacy, and legacy management.",
        "stat_bonuses": {
            "INT": 1,
            "INF": 1
        },
        "talent": "Corporate Protocol: Automatically understands social hierarchy and bureaucracy."
    },
    "Dust-Wanderer": {
        "description": "Born on irradiated desert worlds; survivalist and storyteller of endless storms.",
        "stat_bonuses": {
            "VIT": 1,
            "COH": 1
        },
        "talent": "Storm-Hardened: Resistant to radiation, heat, and exhaustion."
    },
    "Dreamlink Initiate": {
        "description": "Trained in the ancient art of shared lucid dreaming to explore collective consciousness.",
        "stat_bonuses": {
            "AEF": 2
        },
        "talent": "Dream Gate: Once per session, enter or influence another's dream or psychic landscape."
    }
}

def get_background_list():
    """Return a list of all background names"""
    return list(backgrounds.keys())

def get_background(name):
    """Get background data by name"""
    return backgrounds.get(name)

def apply_background_bonuses(base_stats, background_name):
    """Apply background stat bonuses to base stats"""
    if background_name not in backgrounds:
        return base_stats.copy()
    
    background = backgrounds[background_name]
    bonuses = background.get("stat_bonuses", {})
    
    # Create a copy to avoid modifying the original
    modified_stats = base_stats.copy()
    
    # Apply bonuses
    for stat, bonus in bonuses.items():
        if stat in modified_stats:
            modified_stats[stat] += bonus
    
    return modified_stats

