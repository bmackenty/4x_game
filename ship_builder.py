"""
Ship Building and Customization System
"""

ship_components = {
    "Hull Types": {
        "Light Hull": {
            "cost": 10000,
            "health": 100,
            "cargo_space": 50,
            "speed_modifier": 1.2,
            "description": "Fast and nimble, perfect for scouts and couriers"
        },
        "Standard Hull": {
            "cost": 25000,
            "health": 200,
            "cargo_space": 100,
            "speed_modifier": 1.0,
            "description": "Balanced design suitable for most operations"
        },
        "Heavy Hull": {
            "cost": 50000,
            "health": 400,
            "cargo_space": 150,
            "speed_modifier": 0.8,
            "description": "Robust construction for dangerous missions"
        },
        "Mega Hull": {
            "cost": 100000,
            "health": 800,
            "cargo_space": 300,
            "speed_modifier": 0.6,
            "description": "Massive frame for industrial operations"
        }
    },
    "Engines": {
        "Ion Drive": {
            "cost": 5000,
            "fuel_efficiency": 1.0,
            "speed": 1.0,
            "reliability": 0.9,
            "description": "Reliable ion propulsion system"
        },
        "Fusion Engine": {
            "cost": 15000,
            "fuel_efficiency": 0.8,
            "speed": 1.3,
            "reliability": 0.85,
            "description": "High-performance fusion reactor drive"
        },
        "Ether Drive": {
            "cost": 30000,
            "fuel_efficiency": 1.2,
            "speed": 1.5,
            "reliability": 0.75,
            "description": "Exotic etheric field manipulation drive"
        },
        "Quantum Jump Drive": {
            "cost": 75000,
            "fuel_efficiency": 2.0,
            "speed": 3.0,
            "reliability": 0.7,
            "description": "Instantaneous quantum tunneling system"
        }
    },
    "Weapons": {
        "Pulse Cannons": {
            "cost": 8000,
            "damage": 50,
            "range": 100,
            "accuracy": 0.8,
            "description": "Standard energy weapon system"
        },
        "Plasma Torpedoes": {
            "cost": 15000,
            "damage": 120,
            "range": 200,
            "accuracy": 0.6,
            "description": "Heavy explosive projectiles"
        },
        "Etheric Disruptors": {
            "cost": 25000,
            "damage": 80,
            "range": 150,
            "accuracy": 0.85,
            "special": "Disables shields",
            "description": "Disrupts enemy etheric fields"
        },
        "Gravity Cannon": {
            "cost": 50000,
            "damage": 200,
            "range": 300,
            "accuracy": 0.7,
            "special": "Area damage",
            "description": "Weaponized gravitational distortion"
        }
    },
    "Shields": {
        "Basic Deflectors": {
            "cost": 3000,
            "shield_strength": 50,
            "recharge_rate": 5,
            "description": "Standard particle deflection system"
        },
        "Plasma Shields": {
            "cost": 10000,
            "shield_strength": 150,
            "recharge_rate": 8,
            "description": "High-energy plasma barrier"
        },
        "Etheric Barriers": {
            "cost": 20000,
            "shield_strength": 200,
            "recharge_rate": 12,
            "special": "Reflects energy attacks",
            "description": "Mystical etheric protection field"
        },
        "Phase Shields": {
            "cost": 40000,
            "shield_strength": 100,
            "recharge_rate": 15,
            "special": "50% chance to phase through attacks",
            "description": "Quantum phase-shifting defensive matrix"
        }
    },
    "Special Systems": {
        "Cargo Expander": {
            "cost": 8000,
            "cargo_bonus": 100,
            "description": "Dimensional compression cargo system"
        },
        "Stealth Generator": {
            "cost": 25000,
            "stealth_rating": 0.8,
            "description": "Advanced cloaking technology"
        },
        "Scanner Array": {
            "cost": 12000,
            "detection_range": 500,
            "description": "Long-range sensor system"
        },
        "Mining Laser": {
            "cost": 15000,
            "mining_efficiency": 2.0,
            "description": "Asteroid mining equipment"
        },
        "Research Lab": {
            "cost": 30000,
            "research_bonus": 0.5,
            "description": "Mobile scientific laboratory"
        },
        "Medical Bay": {
            "cost": 20000,
            "crew_health": 1.5,
            "description": "Advanced medical facilities"
        }
    }
}

ship_templates = {
    "Scout Ship": {
        "hull": "Light Hull",
        "engine": "Ion Drive", 
        "weapons": ["Pulse Cannons"],
        "shields": "Basic Deflectors",
        "special": ["Scanner Array"],
        "total_cost": 38000,
        "role": "Fast reconnaissance and exploration"
    },
    "Merchant Vessel": {
        "hull": "Standard Hull",
        "engine": "Fusion Engine",
        "weapons": ["Pulse Cannons"],
        "shields": "Plasma Shields",
        "special": ["Cargo Expander"],
        "total_cost": 58000,
        "role": "Commercial trading and transport"
    },
    "Warship": {
        "hull": "Heavy Hull",
        "engine": "Ether Drive",
        "weapons": ["Plasma Torpedoes", "Etheric Disruptors"],
        "shields": "Etheric Barriers",
        "special": ["Medical Bay"],
        "total_cost": 160000,
        "role": "Military operations and fleet defense"
    },
    "Explorer": {
        "hull": "Standard Hull",
        "engine": "Quantum Jump Drive",
        "weapons": ["Pulse Cannons"],
        "shields": "Phase Shields", 
        "special": ["Scanner Array", "Research Lab"],
        "total_cost": 182000,
        "role": "Deep space exploration and research"
    },
    "Miner": {
        "hull": "Heavy Hull",
        "engine": "Ion Drive",
        "weapons": ["Pulse Cannons"],
        "shields": "Basic Deflectors",
        "special": ["Mining Laser", "Cargo Expander"],
        "total_cost": 81000,
        "role": "Resource extraction and processing"
    }
}

def calculate_ship_stats(components):
    """Calculate final ship statistics based on components"""
    stats = {
        "health": 0,
        "cargo_space": 0,
        "speed": 0,
        "total_cost": 0
    }
    
    # Add hull stats
    if "hull" in components:
        hull_data = ship_components["Hull Types"][components["hull"]]
        stats["health"] = hull_data["health"]
        stats["cargo_space"] = hull_data["cargo_space"]
        stats["speed"] = hull_data["speed_modifier"]
        stats["total_cost"] += hull_data["cost"]
    
    # Add engine stats
    if "engine" in components:
        engine_data = ship_components["Engines"][components["engine"]]
        stats["speed"] *= engine_data["speed"]
        stats["total_cost"] += engine_data["cost"]
    
    # Add weapon costs
    if "weapons" in components:
        for weapon in components["weapons"]:
            stats["total_cost"] += ship_components["Weapons"][weapon]["cost"]
    
    # Add shield stats
    if "shields" in components:
        stats["total_cost"] += ship_components["Shields"][components["shields"]]["cost"]
    
    # Add special system costs and bonuses
    if "special" in components:
        for system in components["special"]:
            system_data = ship_components["Special Systems"][system]
            stats["total_cost"] += system_data["cost"]
            if "cargo_bonus" in system_data:
                stats["cargo_space"] += system_data["cargo_bonus"]
    
    return stats