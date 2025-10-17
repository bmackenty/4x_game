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

def create_character_stats():
    """Generate random character statistics"""
    import random
    
    stats = {
        # Core Command Attributes
        "leadership": random.randint(1, 10),
        "charisma": random.randint(1, 10),
        "strategy": random.randint(1, 10),
        
        # Combat & Military
        "combat": random.randint(1, 10),
        "tactics": random.randint(1, 10),
        "piloting": random.randint(1, 10),
        
        # Technical & Science
        "engineering": random.randint(1, 10),
        "research": random.randint(1, 10),
        "hacking": random.randint(1, 10),
        
        # Social & Economic
        "diplomacy": random.randint(1, 10),
        "trading": random.randint(1, 10),
        "espionage": random.randint(1, 10),
        
        # Exploration & Survival
        "navigation": random.randint(1, 10),
        "survival": random.randint(1, 10),
        "archaeology": random.randint(1, 10)
    }
    
    return stats