"""
Crew system for ships - crew members provide bonuses to ship systems.
Crew can be recruited at colonies and stations.
"""

# Crew member database
CREW_TYPES = {
    "Engineer": {
        "name": "Engineer",
        "description": "Skilled technician who maintains ship systems and improves efficiency.",
        "rarity": "common",
        "bonuses": {
            "engine_efficiency": 8.0,
            "power_efficiency": 6.0,
        },
        "salary": 200,
        "recruitment_locations": ["Industrial Station", "Mining Colony", "Trading Hub"]
    },
    
    "Navigator": {
        "name": "Navigator",
        "description": "Expert in stellar cartography and jump calculations.",
        "rarity": "common",
        "bonuses": {
            "ftl_jump_capacity": 10.0,
            "detection_range": 5.0,
        },
        "salary": 250,
        "recruitment_locations": ["Trading Hub", "Research Station", "Frontier Outpost"]
    },
    
    "Sensor Specialist": {
        "name": "Sensor Specialist",
        "description": "Enhances scanning and detection capabilities.",
        "rarity": "common",
        "bonuses": {
            "detection_range": 12.0,
            "signal_processing": 8.0,
        },
        "salary": 220,
        "recruitment_locations": ["Research Station", "Military Outpost", "Trading Hub"]
    },
    
    "Weapons Officer": {
        "name": "Weapons Officer",
        "description": "Trained in combat systems and weapon optimization.",
        "rarity": "uncommon",
        "bonuses": {
            "weapon_output": 10.0,
            "targeting_accuracy": 8.0,
        },
        "salary": 300,
        "recruitment_locations": ["Military Outpost", "Frontier Outpost"]
    },
    
    "Shield Technician": {
        "name": "Shield Technician",
        "description": "Maintains and optimizes defensive systems.",
        "rarity": "uncommon",
        "bonuses": {
            "shield_strength": 10.0,
            "shield_recharge": 8.0,
        },
        "salary": 280,
        "recruitment_locations": ["Military Outpost", "Trading Hub"]
    },
    
    "Etheric Harmonizer": {
        "name": "Etheric Harmonizer",
        "description": "Specialist in etheric field manipulation and resonance.",
        "rarity": "rare",
        "bonuses": {
            "etheric_sensitivity": 15.0,
            "etheric_stability": 12.0,
        },
        "salary": 450,
        "recruitment_locations": ["Research Station", "Ancient Site"]
    },
    
    "Chief Engineer": {
        "name": "Chief Engineer",
        "description": "Master technician with exceptional skills across all systems.",
        "rarity": "rare",
        "bonuses": {
            "engine_efficiency": 15.0,
            "power_efficiency": 12.0,
            "system_reliability": 10.0,
        },
        "salary": 500,
        "recruitment_locations": ["Industrial Station", "Research Station"]
    },
    
    "Medical Officer": {
        "name": "Medical Officer",
        "description": "Keeps crew healthy and morale high.",
        "rarity": "common",
        "bonuses": {
            "crew_morale": 15.0,
            "crew_efficiency": 8.0,
        },
        "salary": 280,
        "recruitment_locations": ["Trading Hub", "Industrial Station", "Research Station"]
    },
    
    "Quartermaster": {
        "name": "Quartermaster",
        "description": "Manages supplies and cargo operations efficiently.",
        "rarity": "common",
        "bonuses": {
            "mass_efficiency": 10.0,
            "cargo_security": 8.0,
        },
        "salary": 240,
        "recruitment_locations": ["Trading Hub", "Industrial Station"]
    },
    
    "Pilot": {
        "name": "Pilot",
        "description": "Expert in ship maneuvering and navigation.",
        "rarity": "uncommon",
        "bonuses": {
            "maneuverability": 12.0,
            "engine_output": 8.0,
        },
        "salary": 320,
        "recruitment_locations": ["Military Outpost", "Frontier Outpost", "Trading Hub"]
    },
    
    "Systems Analyst": {
        "name": "Systems Analyst",
        "description": "Optimizes ship computer systems and automation.",
        "rarity": "uncommon",
        "bonuses": {
            "computing_power": 15.0,
            "system_reliability": 8.0,
        },
        "salary": 340,
        "recruitment_locations": ["Research Station", "Trading Hub"]
    },
    
    "Communications Officer": {
        "name": "Communications Officer",
        "description": "Manages all communication systems and protocols.",
        "rarity": "common",
        "bonuses": {
            "signal_strength": 10.0,
            "signal_processing": 8.0,
        },
        "salary": 230,
        "recruitment_locations": ["Trading Hub", "Frontier Outpost"]
    },
    
    "Void Mystic": {
        "name": "Void Mystic",
        "description": "Rare individual who can sense anomalies in the void.",
        "rarity": "legendary",
        "bonuses": {
            "etheric_sensitivity": 20.0,
            "anomaly_detection": 18.0,
            "crew_morale": 10.0,
        },
        "salary": 800,
        "recruitment_locations": ["Ancient Site", "Research Station"]
    },
    
    "Xeno-Biologist": {
        "name": "Xeno-Biologist",
        "description": "Expert in alien life forms and ecosystems.",
        "rarity": "rare",
        "bonuses": {
            "bioscience_capacity": 18.0,
            "crew_morale": 8.0,
        },
        "salary": 420,
        "recruitment_locations": ["Research Station", "Frontier Outpost"]
    },
}


class CrewMember:
    """Represents a crew member on a ship"""
    
    def __init__(self, crew_type, name=None, level=1):
        if crew_type not in CREW_TYPES:
            raise ValueError(f"Unknown crew type: {crew_type}")
        
        self.crew_type = crew_type
        self.data = CREW_TYPES[crew_type]
        self.name = name or self._generate_name()
        self.level = level
        self.experience = 0
        self.morale = 100
        
    def _generate_name(self):
        """Generate a random name for the crew member"""
        import random
        first_names = ["Alex", "Jordan", "Sam", "Morgan", "Casey", "Riley", "Avery", "Quinn",
                      "Zara", "Kira", "Nova", "Lyra", "Jax", "Kai", "Ryn", "Vex"]
        last_names = ["Chen", "Santos", "O'Brien", "Kowalski", "Nakamura", "Okafor", "Singh",
                     "Volkov", "Martinez", "Bergström", "al-Rashid", "Thorne", "Vega", "Frost"]
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    def get_bonuses(self):
        """Get the stat bonuses this crew member provides"""
        bonuses = {}
        base_bonuses = self.data["bonuses"]
        
        # Scale bonuses by level (1.0x at level 1, up to 1.5x at level 10)
        level_multiplier = 1.0 + (self.level - 1) * 0.055
        
        # Scale by morale (50% morale = 0.75x, 100% morale = 1.0x, 150% morale = 1.25x)
        morale_multiplier = 0.75 + (self.morale / 100) * 0.25
        
        for stat, value in base_bonuses.items():
            bonuses[stat] = value * level_multiplier * morale_multiplier
        
        return bonuses
    
    def get_salary(self):
        """Get the crew member's salary per time period"""
        # Salary scales with level
        base_salary = self.data["salary"]
        return int(base_salary * (1.0 + (self.level - 1) * 0.2))
    
    def gain_experience(self, amount):
        """Gain experience and potentially level up"""
        self.experience += amount
        # Simple leveling: 100 XP per level
        while self.experience >= self.level * 100 and self.level < 10:
            self.level += 1
            self.experience -= (self.level - 1) * 100
    
    def to_dict(self):
        """Serialize crew member for saving"""
        return {
            "crew_type": self.crew_type,
            "name": self.name,
            "level": self.level,
            "experience": self.experience,
            "morale": self.morale,
        }
    
    @classmethod
    def from_dict(cls, data):
        """Deserialize crew member from save data"""
        crew = cls(data["crew_type"], data.get("name"), data.get("level", 1))
        crew.experience = data.get("experience", 0)
        crew.morale = data.get("morale", 100)
        return crew


def get_available_crew_at_location(location_type):
    """Get list of crew types that can be recruited at this location"""
    available = []
    for crew_type, data in CREW_TYPES.items():
        if location_type in data["recruitment_locations"]:
            available.append(crew_type)
    return available


def calculate_crew_bonuses(crew_list):
    """Calculate total bonuses from all crew members"""
    total_bonuses = {}
    
    for crew_member in crew_list:
        bonuses = crew_member.get_bonuses()
        for stat, value in bonuses.items():
            total_bonuses[stat] = total_bonuses.get(stat, 0) + value
    
    return total_bonuses
