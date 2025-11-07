"""
Character Classes and Backgrounds for 4X Game
"""

character_classes = {
    "Merchant Captain": {
        "description": "A savvy trader with connections across the galaxy",
        "starting_credits": 15000,
        "starting_ships": ["Aurora-Class Freighter"],
        "bonuses": {
            "trade_discount": 0.1,  # 10% better prices
            "negotiation_bonus": 0.15
        },
        "skills": ["Trade Networks", "Market Analysis", "Cargo Optimization"]
    },
    "Explorer": {
        "description": "A fearless pioneer seeking new frontiers",
        "starting_credits": 8000,
        "starting_ships": ["Stellar Voyager"],
        "bonuses": {
            "exploration_bonus": 0.2,
            "fuel_efficiency": 0.15
        },
        "skills": ["Navigation", "Xenobiology", "Survey Operations"]
    },
    "Industrial Magnate": {
        "description": "A manufacturing expert focused on production",
        "starting_credits": 12000,
        "starting_ships": ["Basic Transport"],
        "starting_platforms": ["Nanoforge Spires"],
        "bonuses": {
            "production_efficiency": 0.2,
            "construction_discount": 0.15
        },
        "skills": ["Industrial Management", "Resource Optimization", "Logistics"]
    },
    "Military Commander": {
        "description": "A tactical genius with combat experience",
        "starting_credits": 10000,
        "starting_ships": ["Aurora Ascendant"],
        "bonuses": {
            "combat_effectiveness": 0.25,
            "crew_morale": 0.2
        },
        "skills": ["Fleet Tactics", "Combat Engineering", "Strategic Planning"]
    },
    "Diplomat": {
        "description": "A skilled negotiator and alliance builder",
        "starting_credits": 12000,
        "starting_ships": ["Celestium-Class Communication Ship"],
        "bonuses": {
            "diplomatic_relations": 0.3,
            "information_access": 0.2
        },
        "skills": ["Xenolinguistics", "Cultural Analysis", "Treaty Negotiation"]
    },
    "Scientist": {
        "description": "A researcher focused on technological advancement",
        "starting_credits": 9000,
        "starting_ships": ["Nebula Drifter"],
        "starting_stations": ["Archive of Echoes"],
        "bonuses": {
            "research_speed": 0.25,
            "technology_discount": 0.15
        },
        "skills": ["Quantum Physics", "Bioengineering", "Data Analysis"]
    },
    "Smuggler": {
        "description": "A cunning operator working in the galaxy's shadows",
        "starting_credits": 7500,
        "starting_ships": ["Shadow Runner"],
        "bonuses": {
            "stealth_operations": 0.3,
            "black_market_access": 0.25,
            "contraband_profits": 0.2
        },
        "skills": ["Stealth Navigation", "Black Market Contacts", "Evasive Maneuvers"]
    },
    "Archaeologist": {
        "description": "An expert in ancient civilizations and lost technologies",
        "starting_credits": 8500,
        "starting_ships": ["Deep Explorer"],
        "bonuses": {
            "artifact_discovery": 0.4,
            "ancient_tech_bonus": 0.25,
            "excavation_efficiency": 0.3
        },
        "skills": ["Xenoarchaeology", "Ancient Languages", "Artifact Analysis"]
    },
    "Corporate Spy": {
        "description": "A master of espionage and information warfare",
        "starting_credits": 11000,
        "starting_ships": ["Phantom Interceptor"],
        "bonuses": {
            "intelligence_gathering": 0.35,
            "sabotage_effectiveness": 0.25,
            "infiltration_success": 0.3
        },
        "skills": ["Corporate Espionage", "Data Infiltration", "Social Engineering"]
    },
    "Bounty Hunter": {
        "description": "A skilled tracker specializing in high-value targets",
        "starting_credits": 9500,
        "starting_ships": ["Pursuit Vessel"],
        "bonuses": {
            "tracking_ability": 0.35,
            "combat_initiative": 0.2,
            "capture_bonus": 0.25
        },
        "skills": ["Target Tracking", "Combat Tactics", "Prisoner Containment"]
    },
    "Terraformer": {
        "description": "An environmental engineer transforming worlds",
        "starting_credits": 13000,
        "starting_ships": ["Genesis Transport"],
        "starting_platforms": ["Atmospheric Processor"],
        "bonuses": {
            "terraforming_speed": 0.4,
            "environmental_efficiency": 0.25,
            "colony_development": 0.3
        },
        "skills": ["Atmospheric Engineering", "Ecosystem Design", "Planetary Geology"]
    }
}

character_backgrounds = {
    "Core Worlds Noble": {
        "description": "Born into wealth and privilege in the galactic center",
        "credit_bonus": 5000,
        "reputation_bonus": 0.2,
        "traits": ["Well Connected", "Educated", "Resource Rich"]
    },
    "Frontier Survivor": {
        "description": "Hardened by life on the galaxy's dangerous edges",
        "credit_penalty": -2000,
        "resilience_bonus": 0.25,
        "traits": ["Resourceful", "Hardy", "Independent"]
    },
    "Corporate Executive": {
        "description": "Former high-ranking member of a mega-corporation",
        "credit_bonus": 3000,
        "business_bonus": 0.15,
        "traits": ["Business Acumen", "Network Access", "Profit Focused"]
    },
    "Military Veteran": {
        "description": "Retired from galactic military service",
        "combat_bonus": 0.2,
        "discipline_bonus": 0.15,
        "traits": ["Disciplined", "Combat Ready", "Leadership"]
    },
    "Academic Researcher": {
        "description": "Former university professor and researcher",
        "knowledge_bonus": 0.25,
        "credit_penalty": -1000,
        "traits": ["Analytical", "Methodical", "Innovative"]
    },
    "Pirate Reformed": {
        "description": "Former outlaw seeking legitimate opportunities",
        "credit_penalty": -3000,
        "street_smart_bonus": 0.3,
        "traits": ["Cunning", "Adaptable", "Risk Taker"]
    }
}

# The Seven Core Characteristics of 7019
# Base-100 system: all stats start at 30, players allocate 30 points
STAT_NAMES = {
    "VIT": "Vitality",
    "KIN": "Kinetics",
    "INT": "Intellect",
    "AEF": "Aetheric Affinity",
    "COH": "Coherence",
    "INF": "Influence",
    "SYN": "Synthesis"
}

STAT_DESCRIPTIONS = {
    "VIT": "Biological endurance, physical resilience, and self-repair capacity",
    "KIN": "Speed, agility, reaction time, and precision in physical and cybernetic systems",
    "INT": "Cognitive power, analytical capacity, and data-processing speed",
    "AEF": "Resonance with Etheric Energy - ability to sense, channel, and manipulate the Ether",
    "COH": "Stability of consciousness and identity across biological, digital, and etheric layers",
    "INF": "Social resonance - charisma, authority, and emotional projection",
    "SYN": "Adaptability - ability to integrate technologies, merge disciplines, or harmonize with alien systems"
}

BASE_STAT_VALUE = 30
POINT_BUY_POINTS = 30
MAX_STAT_VALUE = 100

def create_base_character_stats():
    """Create base character stats - all stats start at 30"""
    return {
        "VIT": BASE_STAT_VALUE,
        "KIN": BASE_STAT_VALUE,
        "INT": BASE_STAT_VALUE,
        "AEF": BASE_STAT_VALUE,
        "COH": BASE_STAT_VALUE,
        "INF": BASE_STAT_VALUE,
        "SYN": BASE_STAT_VALUE
    }

def validate_stat_allocation(stats, background_name=None):
    """Validate that stat allocation is legal (30 points allocated, max 100 per stat)
    
    Args:
        stats: Dictionary of stat values
        background_name: Optional background name to account for stat bonuses
    """
    base_total = BASE_STAT_VALUE * len(STAT_NAMES)
    
    # Account for background bonuses if provided
    if background_name:
        try:
            from backgrounds import backgrounds as background_data
            bg = background_data.get(background_name, {})
            bonuses = bg.get('stat_bonuses', {})
            if bonuses:
                bg_bonus_total = sum(bonuses.values())
                base_total += bg_bonus_total
        except ImportError:
            pass  # backgrounds module not available, ignore
    
    current_total = sum(stats.values())
    allocated_points = current_total - base_total
    
    # Check total allocation (can be under, but not over)
    if allocated_points > POINT_BUY_POINTS:
        return False, f"Cannot allocate more than {POINT_BUY_POINTS} points (currently {allocated_points})"
    
    # Check max per stat
    for stat_name, value in stats.items():
        if value > MAX_STAT_VALUE:
            return False, f"{STAT_NAMES[stat_name]} cannot exceed {MAX_STAT_VALUE} (currently {value})"
        # Calculate minimum for this stat (including background bonus)
        min_value = BASE_STAT_VALUE
        if background_name:
            try:
                from backgrounds import backgrounds as background_data
                bg = background_data.get(background_name, {})
                bonuses = bg.get('stat_bonuses', {})
                if stat_name in bonuses:
                    min_value += bonuses[stat_name]
            except ImportError:
                pass
        if value < min_value:
            return False, f"{STAT_NAMES[stat_name]} cannot be below {min_value} (currently {value})"
    
    remaining_points = POINT_BUY_POINTS - allocated_points
    if remaining_points > 0:
        return True, f"Valid allocation ({remaining_points} points remaining)"
    return True, "Valid allocation"

DERIVED_METRIC_INFO = {
    "Health": {
        "formula": "VIT × 10 + COH × 5",
        "description": "Physical integrity and resistance to damage."
    },
    "Etheric Capacity": {
        "formula": "AEF × 8 + COH × 4",
        "description": "Total energy that can be safely channeled."
    },
    "Processing Speed": {
        "formula": "INT + KIN",
        "description": "Reaction speed in both physical and digital domains."
    },
    "Adaptation Index": {
        "formula": "(SYN + COH + INT) ÷ 3",
        "description": "Ability to evolve under stress or exposure to new environments."
    },
    "Resilience Index": {
        "formula": "VIT + COH",
        "description": "Combined physical and mental stability."
    },
    "Innovation Quotient": {
        "formula": "INT + SYN",
        "description": "Capacity to invent, adapt, and hybridize solutions."
    },
    "Etheric Stability": {
        "formula": "AEF + COH",
        "description": "Safety margin when channeling or resisting etheric forces."
    },
    "Social Engineering Potential": {
        "formula": "INF + SYN",
        "description": "Effectiveness at blending diplomacy with technological or cultural manipulation."
    }
}

def calculate_derived_attributes(stats):
    """Calculate derived metrics from base stats"""
    derived = {}
    derived["Health"] = stats["VIT"] * 10 + stats["COH"] * 5
    derived["Etheric Capacity"] = stats["AEF"] * 8 + stats["COH"] * 4
    derived["Processing Speed"] = stats["INT"] + stats["KIN"]
    derived["Adaptation Index"] = int((stats["SYN"] + stats["COH"] + stats["INT"]) / 3)
    derived["Resilience Index"] = stats["VIT"] + stats["COH"]
    derived["Innovation Quotient"] = stats["INT"] + stats["SYN"]
    derived["Etheric Stability"] = stats["AEF"] + stats["COH"]
    derived["Social Engineering Potential"] = stats["INF"] + stats["SYN"]
    return derived

def create_character_stats():
    """
    Create character stats with point-buy system.
    For backward compatibility, returns base stats (all 30).
    Point allocation should be done through the UI.
    """
    return create_base_character_stats()