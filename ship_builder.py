"""
Ship Building and Customization System

Power System:
- Each component requires power (weapons, shields, special systems)
- Engines provide power output
- Total power_required cannot exceed engine power_output

Slot System:
- Components require specific slot types and quantities
- Hull types define available slots
- Example: Light Hull has 2 weapon hardpoints, 1 utility bay

Tech Prerequisites:
- Some components require research/tech unlocks
- Links to research.py tech tree

Size Classes:
- Components have size_class (Small, Medium, Large, XL)
- Must fit within hull size limits
"""

ship_components = {
    "Hull Types": {
        "Light Hull": {
            "cost": 10000,
            "health": 100,
            "cargo_space": 50,
            "speed_modifier": 1.2,
            "size_class": "Small",
            "slots": {
                "weapon_hardpoints": 2,
                "utility_bays": 1,
                "engine_mounts": 1,
                "shield_slots": 1
            },
            "description": "Fast and nimble, perfect for scouts and couriers"
        },
        "Standard Hull": {
            "cost": 25000,
            "health": 200,
            "cargo_space": 100,
            "speed_modifier": 1.0,
            "size_class": "Medium",
            "slots": {
                "weapon_hardpoints": 4,
                "utility_bays": 2,
                "engine_mounts": 1,
                "shield_slots": 1
            },
            "description": "Balanced design suitable for most operations"
        },
        "Heavy Hull": {
            "cost": 50000,
            "health": 400,
            "cargo_space": 150,
            "speed_modifier": 0.8,
            "size_class": "Large",
            "slots": {
                "weapon_hardpoints": 6,
                "utility_bays": 3,
                "engine_mounts": 1,
                "shield_slots": 2
            },
            "description": "Robust construction for dangerous missions"
        },
        "Mega Hull": {
            "cost": 100000,
            "health": 800,
            "cargo_space": 300,
            "speed_modifier": 0.6,
            "size_class": "XL",
            "slots": {
                "weapon_hardpoints": 8,
                "utility_bays": 4,
                "engine_mounts": 2,
                "shield_slots": 2
            },
            "description": "Massive frame for industrial operations"
        }
    },
    "Engines": {
        "Ion Drive": {
            "cost": 5000,
            "fuel_efficiency": 1.0,
            "speed": 1.0,
            "reliability": 0.9,
            "power_output": 100,
            "size_class": "Small",
            "slots_required": 1,
            "slot_type": "engine_mounts",
            "tech_required": None,
            "description": "Reliable ion propulsion system"
        },
        "Fusion Engine": {
            "cost": 15000,
            "fuel_efficiency": 0.8,
            "speed": 1.3,
            "reliability": 0.85,
            "power_output": 200,
            "size_class": "Medium",
            "slots_required": 1,
            "slot_type": "engine_mounts",
            "tech_required": "Fusion Technology",
            "description": "High-performance fusion reactor drive"
        },
        "Ether Drive": {
            "cost": 30000,
            "fuel_efficiency": 1.2,
            "speed": 1.5,
            "reliability": 0.75,
            "power_output": 300,
            "size_class": "Medium",
            "slots_required": 1,
            "slot_type": "engine_mounts",
            "tech_required": "Etheric Manipulation",
            "description": "Exotic etheric field manipulation drive"
        },
        "Quantum Jump Drive": {
            "cost": 75000,
            "fuel_efficiency": 2.0,
            "speed": 3.0,
            "reliability": 0.7,
            "power_output": 400,
            "size_class": "Large",
            "slots_required": 1,
            "slot_type": "engine_mounts",
            "tech_required": "Quantum Mechanics",
            "description": "Instantaneous quantum tunneling system"
        },
        "Graviton Flux Engine": {
            "cost": 95000,
            "fuel_efficiency": 2.2,
            "speed": 2.8,
            "reliability": 0.65,
            "power_output": 450,
            "size_class": "Large",
            "slots_required": 1,
            "slot_type": "engine_mounts",
            "tech_required": "Graviton Physics",
            "description": "Manipulates localized gravity wells to create near-instant acceleration."
        },
        "Solaris Bloom Drive": {
            "cost": 40000,
            "fuel_efficiency": 1.8,
            "speed": 1.6,
            "reliability": 0.9,
            "power_output": 250,
            "size_class": "Medium",
            "slots_required": 1,
            "slot_type": "engine_mounts",
            "tech_required": "Bio-Engineering",
            "description": "Photosynthetic nano-panels harvest stellar radiation and Etheric sunlight."
        },
        "Voidstream Engine": {
            "cost": 120000,
            "fuel_efficiency": 3.0,
            "speed": 3.5,
            "reliability": 0.6,
            "power_output": 500,
            "size_class": "XL",
            "slots_required": 2,
            "slot_type": "engine_mounts",
            "tech_required": "Subspace Navigation",
            "description": "Taps subspace void currents for silent, faster-than-sensor travel."
        },
        "Chrono-Spindle Reactor": {
            "cost": 150000,
            "fuel_efficiency": 2.8,
            "speed": 2.2,
            "reliability": 0.7,
            "power_output": 550,
            "size_class": "XL",
            "slots_required": 2,
            "slot_type": "engine_mounts",
            "tech_required": "Temporal Manipulation",
            "description": "Generates thrust by coiling and releasing micro-temporal distortions."
        }
    },
    "Weapons": {
        "Pulse Cannons": {
            "cost": 8000,
            "damage": 50,
            "range": 100,
            "accuracy": 0.8,
            "power_required": 20,
            "size_class": "Small",
            "slots_required": 1,
            "slot_type": "weapon_hardpoints",
            "tech_required": None,
            "description": "Standard energy weapon system"
        },
        "Plasma Torpedoes": {
            "cost": 15000,
            "damage": 120,
            "range": 200,
            "accuracy": 0.6,
            "power_required": 40,
            "size_class": "Medium",
            "slots_required": 2,
            "slot_type": "weapon_hardpoints",
            "tech_required": "Plasma Physics",
            "description": "Heavy explosive projectiles"
        },
        "Etheric Disruptors": {
            "cost": 25000,
            "damage": 80,
            "range": 150,
            "accuracy": 0.85,
            "power_required": 50,
            "size_class": "Medium",
            "slots_required": 1,
            "slot_type": "weapon_hardpoints",
            "tech_required": "Etheric Manipulation",
            "special": "Disables shields",
            "description": "Disrupts enemy etheric fields"
        },
        "Gravity Cannon": {
            "cost": 50000,
            "damage": 200,
            "range": 300,
            "accuracy": 0.7,
            "power_required": 80,
            "size_class": "Large",
            "slots_required": 3,
            "slot_type": "weapon_hardpoints",
            "tech_required": "Graviton Physics",
            "special": "Area damage",
            "description": "Weaponized gravitational distortion"
        },
        "Neutrino Lance": {
            "cost": 40000,
            "damage": 140,
            "range": 350,
            "accuracy": 0.85,
            "power_required": 60,
            "size_class": "Large",
            "slots_required": 2,
            "slot_type": "weapon_hardpoints",
            "tech_required": "Particle Physics",
            "special": "Bypasses most shields",
            "description": "Fires tightly focused neutrino beams that ignore conventional defenses."
        },
        "Chrono Torpedoes": {
            "cost": 65000,
            "damage": 300,
            "range": 250,
            "accuracy": 0.6,
            "power_required": 90,
            "size_class": "Large",
            "slots_required": 3,
            "slot_type": "weapon_hardpoints",
            "tech_required": "Temporal Manipulation",
            "special": "Delays detonation across time, striking seconds later.",
            "description": "Temporal-phase explosives that detonate in multiple timeframes."
        },
        "Nanite Swarm Projector": {
            "cost": 35000,
            "damage": 50,
            "range": 150,
            "accuracy": 0.9,
            "power_required": 45,
            "size_class": "Medium",
            "slots_required": 1,
            "slot_type": "weapon_hardpoints",
            "tech_required": "Nanotechnology",
            "special": "Erodes hull integrity over time",
            "description": "Releases self-replicating nanites that disassemble enemy hulls."
        },
        "Dark Matter Railgun": {
            "cost": 90000,
            "damage": 250,
            "range": 400,
            "accuracy": 0.7,
            "power_required": 100,
            "size_class": "XL",
            "slots_required": 4,
            "slot_type": "weapon_hardpoints",
            "tech_required": "Dark Matter Research",
            "special": "Pierces through multiple targets",
            "description": "Accelerates dense dark-matter slugs beyond relativistic speeds."
        },
        "Harmonic Resonator": {
            "cost": 20000,
            "damage": 100,
            "range": 180,
            "accuracy": 0.75,
            "power_required": 35,
            "size_class": "Small",
            "slots_required": 1,
            "slot_type": "weapon_hardpoints",
            "tech_required": "Etheric Manipulation",
            "special": "Destabilizes Etheric shields",
            "description": "Emits frequencies tuned to resonate with Ether fields."
        }
    },
    "Shields": {
        "Basic Deflectors": {
            "cost": 3000,
            "shield_strength": 50,
            "recharge_rate": 5,
            "power_required": 15,
            "size_class": "Small",
            "slots_required": 1,
            "slot_type": "shield_slots",
            "tech_required": None,
            "description": "Standard particle deflection system"
        },
        "Plasma Shields": {
            "cost": 10000,
            "shield_strength": 150,
            "recharge_rate": 8,
            "power_required": 30,
            "size_class": "Medium",
            "slots_required": 1,
            "slot_type": "shield_slots",
            "tech_required": "Plasma Physics",
            "description": "High-energy plasma barrier"
        },
        "Etheric Barriers": {
            "cost": 20000,
            "shield_strength": 200,
            "recharge_rate": 12,
            "power_required": 50,
            "size_class": "Large",
            "slots_required": 1,
            "slot_type": "shield_slots",
            "tech_required": "Etheric Manipulation",
            "special": "Reflects energy attacks",
            "description": "Mystical etheric protection field"
        },
        "Phase Shields": {
            "cost": 40000,
            "shield_strength": 100,
            "recharge_rate": 15,
            "power_required": 60,
            "size_class": "Large",
            "slots_required": 2,
            "slot_type": "shield_slots",
            "tech_required": "Quantum Mechanics",
            "special": "50% chance to phase through attacks",
            "description": "Quantum phase-shifting defensive matrix"
        }
    },
    "Special Systems": {
        "Cargo Expander": {
            "cost": 8000,
            "cargo_bonus": 100,
            "power_required": 10,
            "size_class": "Medium",
            "slots_required": 1,
            "slot_type": "utility_bays",
            "tech_required": None,
            "description": "Dimensional compression cargo system"
        },
        "Stealth Generator": {
            "cost": 25000,
            "stealth_rating": 0.8,
            "power_required": 40,
            "size_class": "Large",
            "slots_required": 1,
            "slot_type": "utility_bays",
            "tech_required": "Cloaking Technology",
            "description": "Advanced cloaking technology"
        },
        "Scanner Array": {
            "cost": 12000,
            "detection_range": 500,
            "scan_range": 8.0,  # Map scanning range
            "power_required": 20,
            "size_class": "Small",
            "slots_required": 1,
            "slot_type": "utility_bays",
            "tech_required": None,
            "description": "Long-range sensor system"
        },
        "Advanced Scanner Array": {
            "cost": 30000,
            "detection_range": 1000,
            "scan_range": 15.0,  # Extended map scanning range
            "power_required": 35,
            "size_class": "Medium",
            "slots_required": 1,
            "slot_type": "utility_bays",
            "tech_required": "Advanced Research",
            "description": "Extended-range deep space sensors"
        },
        "Quantum Scanner": {
            "cost": 50000,
            "detection_range": 2000,
            "scan_range": 25.0,  # Long-range scanning
            "power_required": 50,
            "size_class": "Large",
            "slots_required": 2,
            "slot_type": "utility_bays",
            "tech_required": "Quantum Mechanics",
            "description": "Quantum-entangled sensor network with extreme range"
        },
        "Mining Laser": {
            "cost": 15000,
            "mining_efficiency": 2.0,
            "power_required": 30,
            "size_class": "Medium",
            "slots_required": 1,
            "slot_type": "utility_bays",
            "tech_required": None,
            "description": "Asteroid mining equipment"
        },
        "Research Lab": {
            "cost": 30000,
            "research_bonus": 0.5,
            "power_required": 25,
            "size_class": "Large",
            "slots_required": 2,
            "slot_type": "utility_bays",
            "tech_required": "Advanced Research",
            "description": "Mobile scientific laboratory"
        },
        "Medical Bay": {
            "cost": 20000,
            "crew_health": 1.5,
            "power_required": 15,
            "size_class": "Medium",
            "slots_required": 1,
            "slot_type": "utility_bays",
            "tech_required": None,
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


def check_component_compatibility(hull_name, component_category, component_name, current_components, unlocked_tech=None):
    """
    Check if a component can be installed on the ship.
    
    Args:
        hull_name: Name of the hull type
        component_category: Category (Engines, Weapons, Shields, Special Systems)
        component_name: Name of the component to install
        current_components: Dict of currently installed components
        unlocked_tech: List of unlocked technologies (optional)
    
    Returns:
        (bool, str): (can_install, reason)
    """
    unlocked_tech = unlocked_tech or []
    
    # Get component and hull data
    component = ship_components[component_category][component_name]
    hull = ship_components["Hull Types"][hull_name]
    
    # Check tech requirements
    if component.get("tech_required") and component["tech_required"] not in unlocked_tech:
        return False, f"Requires technology: {component['tech_required']}"
    
    # Check slot availability
    slot_type = component.get("slot_type")
    slots_required = component.get("slots_required", 1)
    
    if slot_type:
        # Count currently used slots
        used_slots = 0
        
        if component_category == "Engines" and "engine" in current_components:
            current_engine = ship_components["Engines"][current_components["engine"]]
            if current_engine.get("slot_type") == slot_type:
                used_slots += current_engine.get("slots_required", 1)
        
        if component_category == "Weapons" and "weapons" in current_components:
            for weapon in current_components["weapons"]:
                weapon_data = ship_components["Weapons"][weapon]
                if weapon_data.get("slot_type") == slot_type:
                    used_slots += weapon_data.get("slots_required", 1)
        
        if component_category == "Shields" and "shields" in current_components:
            for shield in current_components.get("shields", []):
                shield_data = ship_components["Shields"][shield]
                if shield_data.get("slot_type") == slot_type:
                    used_slots += shield_data.get("slots_required", 1)
        
        if component_category == "Special Systems" and "special" in current_components:
            for system in current_components["special"]:
                system_data = ship_components["Special Systems"][system]
                if system_data.get("slot_type") == slot_type:
                    used_slots += system_data.get("slots_required", 1)
        
        # For replacement (not adding), don't count current component's slots
        available_slots = hull["slots"].get(slot_type, 0) - used_slots
        
        if slots_required > available_slots:
            return False, f"Not enough {slot_type} ({available_slots} available, {slots_required} required)"
    
    # Check size class compatibility
    hull_size = hull.get("size_class", "Medium")
    component_size = component.get("size_class", "Small")
    
    size_order = {"Small": 0, "Medium": 1, "Large": 2, "XL": 3}
    if size_order.get(component_size, 0) > size_order.get(hull_size, 1):
        return False, f"Component too large for {hull_size} hull (requires {component_size} hull or larger)"
    
    return True, "Compatible"


def calculate_power_usage(current_components):
    """Calculate total power usage and available power"""
    power_output = 0
    power_used = 0
    
    # Get engine power output
    if "engine" in current_components:
        engine = ship_components["Engines"][current_components["engine"]]
        power_output = engine.get("power_output", 0)
    
    # Calculate power consumption
    if "weapons" in current_components:
        for weapon in current_components["weapons"]:
            weapon_data = ship_components["Weapons"][weapon]
            power_used += weapon_data.get("power_required", 0)
    
    if "shields" in current_components:
        shields_list = current_components["shields"] if isinstance(current_components["shields"], list) else [current_components["shields"]]
        for shield in shields_list:
            shield_data = ship_components["Shields"][shield]
            power_used += shield_data.get("power_required", 0)
    
    if "special" in current_components:
        for system in current_components["special"]:
            system_data = ship_components["Special Systems"][system]
            power_used += system_data.get("power_required", 0)
    
    return {
        "power_output": power_output,
        "power_used": power_used,
        "power_available": power_output - power_used,
        "power_percentage": (power_used / power_output * 100) if power_output > 0 else 0
    }


def get_component_power_requirement(component_category, component_name):
    """Get power requirement for a specific component"""
    component = ship_components[component_category][component_name]
    return component.get("power_required", 0)


def can_afford_component(component_category, component_name, credits):
    """Check if player has enough credits for a component"""
    component = ship_components[component_category][component_name]
    cost = component.get("cost", 0)
    return credits >= cost, cost