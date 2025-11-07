"""
Star Systems Module - Deterministic System Definitions
Defines star systems with predefined characteristics, planets, resources, history, and faction control.
Also defines deterministic faction zones that control regions of space.
This replaces the purely random system generation with curated, lore-rich systems.
"""

import random
from typing import Dict, List, Optional, Tuple, Any

# Deterministic Faction Zones - defines which factions control which regions of space
# Format: faction_name -> {center: (x, y, z), radius: int, description: str}
FACTION_ZONES = {
    "The Veritas Covenant": {
        "center": (50, 50, 25),
        "radius": 60,
        "description": "Core research and knowledge preservation sector around Alpha Centauri"
    },
    "Stellar Nexus Guild": {
        "center": (65, 65, 29),
        "radius": 70,
        "description": "Major trade corridor connecting Vega Prime and Sirius Gate"
    },
    "Ironclad Collective": {
        "center": (30, 80, 20),
        "radius": 55,
        "description": "Fortified border region centered on Rigel Station"
    },
    "Scholara Nexus": {
        "center": (90, 45, 35),
        "radius": 65,
        "description": "Scientific research zone around Betelgeuse Sector"
    },
    "Harmonic Vitality Consortium": {
        "center": (40, 40, 22),
        "radius": 50,
        "description": "Agricultural and bio-diversity sector centered on Tau Ceti"
    },
    "Gearwrights Guild": {
        "center": (25, 30, 15),
        "radius": 55,
        "description": "Mining and manufacturing region around Ross 128"
    },
    "Keepers of the Spire": {
        "center": (48, 52, 24),
        "radius": 60,
        "description": "Archaeological research zone protecting ancient sites near Proxima b"
    },
    "Stellar Cartographers Alliance": {
        "center": (110, 95, 45),
        "radius": 65,
        "description": "Frontier exploration sector at TRAPPIST-1"
    }
}

# Deterministic faction color assignments for visual display
# These colors are used in the faction overlay map for consistency
FACTION_COLORS = {
    "The Veritas Covenant": "bright_blue",
    "Stellar Nexus Guild": "bright_yellow",
    "Ironclad Collective": "bright_red",
    "Scholara Nexus": "bright_magenta",
    "Harmonic Vitality Consortium": "bright_green",
    "Gearwrights Guild": "cyan",
    "Keepers of the Spire": "magenta",
    "Stellar Cartographers Alliance": "bright_cyan",
    # Additional factions with consistent colors
    "The Galactic Salvage Guild": "blue",
    "Veritas Covenant": "bright_blue",  # Alias
    "Gaian Enclave": "green",
    "The Provocateurs' Guild": "yellow",
    "Quantum Artificers Guild": "bright_magenta",
    "Harmonic Resonance Collective": "bright_green",
    "Icaron Collective": "red",
    "Etheric Preservationists": "cyan",
    "Galactic Circus": "bright_yellow",
    "Technotheos": "magenta",
    "Keepers of the Keys": "blue",
    "Celestial Marauders": "red",
    "The Brewmasters' Guild": "yellow",
    "Voidbound Monks": "bright_cyan",
    "Collective of Commonality": "green",
    "The Triune Daughters": "magenta",
    "The Chemists' Concord": "cyan",
    "The Map Makers": "bright_yellow",
    "Celestial Alliance": "bright_blue",
    "The Ironclad Collective": "bright_red",  # Alias
}

# System type definitions with gameplay implications
SYSTEM_TYPES = {
    "Core World": {
        "description": "Heavily populated, center of civilization and commerce",
        "population_range": (10_000_000, 100_000_000),
        "station_count": (2, 4),
        "threat_level": (1, 3),
        "resource_quality": ["Rich", "Abundant"],
        "typical_planets": ["Garden World", "Terrestrial Planet", "Industrial World"]
    },
    "Trading Hub": {
        "description": "Commercial nexus with extensive market activity",
        "population_range": (5_000_000, 50_000_000),
        "station_count": (2, 3),
        "threat_level": (1, 4),
        "resource_quality": ["Moderate", "Rich"],
        "typical_planets": ["Space Port", "Market World", "Terrestrial Planet"]
    },
    "Industrial": {
        "description": "Manufacturing and production powerhouse",
        "population_range": (3_000_000, 30_000_000),
        "station_count": (1, 3),
        "threat_level": (2, 5),
        "resource_quality": ["Rich", "Abundant", "Moderate"],
        "typical_planets": ["Industrial World", "Mining World", "Forge World"]
    },
    "Research": {
        "description": "Scientific and technological advancement center",
        "population_range": (1_000_000, 20_000_000),
        "station_count": (1, 2),
        "threat_level": (1, 3),
        "resource_quality": ["Moderate", "Rich"],
        "typical_planets": ["Research Colony", "Laboratory World", "Garden World"]
    },
    "Military": {
        "description": "Fortified system with defensive installations",
        "population_range": (2_000_000, 25_000_000),
        "station_count": (1, 3),
        "threat_level": (3, 7),
        "resource_quality": ["Moderate", "Poor"],
        "typical_planets": ["Fortress World", "Military Base", "Barren Rock"]
    },
    "Frontier": {
        "description": "Remote system on the edge of known space",
        "population_range": (100_000, 5_000_000),
        "station_count": (0, 1),
        "threat_level": (4, 8),
        "resource_quality": ["Poor", "Moderate", "Rich"],
        "typical_planets": ["Frontier Colony", "Desert Planet", "Ice World"]
    },
    "Mining": {
        "description": "Resource extraction and mineral processing",
        "population_range": (500_000, 10_000_000),
        "station_count": (1, 2),
        "threat_level": (3, 6),
        "resource_quality": ["Rich", "Abundant"],
        "typical_planets": ["Mining World", "Asteroid Belt", "Resource Rich"]
    },
    "Agricultural": {
        "description": "Food production and biological resources",
        "population_range": (2_000_000, 20_000_000),
        "station_count": (1, 2),
        "threat_level": (2, 4),
        "resource_quality": ["Moderate", "Rich"],
        "typical_planets": ["Garden World", "Agricultural World", "Ocean World"]
    }
}

# Planet type definitions
PLANET_TYPES = {
    "Garden World": {
        "atmosphere": True,
        "habitable": True,
        "resources": ["Food", "Water", "Organics", "Bio-materials"],
        "description": "Lush world with diverse ecosystems and breathable atmosphere",
        "colonization_difficulty": "Easy",
        "population_multiplier": 1.5
    },
    "Terrestrial Planet": {
        "atmosphere": True,
        "habitable": True,
        "resources": ["Common Metals", "Rare Minerals", "Water"],
        "description": "Rocky planet with breathable atmosphere",
        "colonization_difficulty": "Easy",
        "population_multiplier": 1.0
    },
    "Industrial World": {
        "atmosphere": True,
        "habitable": True,
        "resources": ["Heavy Metals", "Industrial Materials", "Energy"],
        "description": "Heavily developed manufacturing planet",
        "colonization_difficulty": "Moderate",
        "population_multiplier": 0.8
    },
    "Ocean World": {
        "atmosphere": True,
        "habitable": True,
        "resources": ["Water", "Aquatic Bio-materials", "Hydrogen"],
        "description": "Planet covered primarily by liquid water",
        "colonization_difficulty": "Moderate",
        "population_multiplier": 0.9
    },
    "Desert Planet": {
        "atmosphere": True,
        "habitable": True,
        "resources": ["Rare Minerals", "Silicon", "Solar Energy"],
        "description": "Arid world with minimal water",
        "colonization_difficulty": "Hard",
        "population_multiplier": 0.6
    },
    "Ice World": {
        "atmosphere": True,
        "habitable": False,
        "resources": ["Water Ice", "Frozen Gases", "Rare Elements"],
        "description": "Frozen world with extreme cold",
        "colonization_difficulty": "Hard",
        "population_multiplier": 0.4
    },
    "Gas Giant": {
        "atmosphere": True,
        "habitable": False,
        "resources": ["Hydrogen", "Helium", "Exotic Gases"],
        "description": "Massive planet composed primarily of gases",
        "colonization_difficulty": "Very Hard",
        "population_multiplier": 0.1
    },
    "Mining World": {
        "atmosphere": True,
        "habitable": True,
        "resources": ["Heavy Metals", "Rare Minerals", "Radioactives", "Crystals"],
        "description": "Rich in mineral deposits and ore",
        "colonization_difficulty": "Moderate",
        "population_multiplier": 0.7
    },
    "Lava World": {
        "atmosphere": True,
        "habitable": False,
        "resources": ["Molten Metals", "Geothermal Energy", "Rare Elements"],
        "description": "Volcanic planet with molten surface",
        "colonization_difficulty": "Very Hard",
        "population_multiplier": 0.2
    },
    "Barren Rock": {
        "atmosphere": False,
        "habitable": False,
        "resources": ["Common Metals", "Trace Minerals"],
        "description": "Lifeless rocky world with no atmosphere",
        "colonization_difficulty": "Hard",
        "population_multiplier": 0.3
    },
    "Toxic Planet": {
        "atmosphere": True,
        "habitable": False,
        "resources": ["Chemical Compounds", "Toxic Materials", "Industrial Chemicals"],
        "description": "Poisonous atmosphere unsuitable for life",
        "colonization_difficulty": "Very Hard",
        "population_multiplier": 0.2
    }
}

# Predefined star systems with rich lore and history
STAR_SYSTEMS = {
    "Alpha Centauri": {
        "coordinates": (350, 50, 25),
        "type": "Core World",
        "description": "The oldest human colony outside Sol, a beacon of civilization and commerce.",
        "controlling_faction": "The Veritas Covenant",
        "founding_year": 2420,
        "history": [
            "2420: First colony established by Earth Alliance",
            "2680: Declared independence and formed local government",
            "3200: Joined The Veritas Covenant research network",
            "6150: Survived the Etheric Convergence with minimal casualties"
        ],
        "planets": [
            {
                "name": "New Terra",
                "type": "Garden World",
                "position": 1,
                "moons": 2,
                "population": 45_000_000,
                "notes": "Primary settlement world with vast continents"
            },
            {
                "name": "Centauri Beta",
                "type": "Industrial World",
                "position": 2,
                "moons": 1,
                "population": 12_000_000,
                "notes": "Manufacturing hub for the system"
            },
            {
                "name": "Proxima Minor",
                "type": "Gas Giant",
                "position": 3,
                "moons": 15,
                "population": 500_000,
                "notes": "Hydrogen fuel harvesting operations on moons"
            }
        ],
        "resources": "Abundant",
        "threat_level": 2,
        "trade_routes": ["Vega Prime", "Sirius Gate", "Rigel Station"],
        "special_features": ["Ancient Archive", "Veritas Research Complex"]
    },
    
    "Vega Prime": {
        "coordinates": (75, 60, 30),
        "type": "Trading Hub",
        "description": "The galaxy's premier trading post, where all major trade routes converge.",
        "controlling_faction": "Stellar Nexus Guild",
        "founding_year": 2850,
        "history": [
            "2850: Established as a neutral trading outpost",
            "3100: Stellar Nexus Guild headquarters relocated here",
            "4500: Major expansion of market districts",
            "6200: Became primary commodity exchange for the sector"
        ],
        "planets": [
            {
                "name": "Vega Prime I",
                "type": "Terrestrial Planet",
                "position": 1,
                "moons": 0,
                "population": 28_000_000,
                "notes": "Massive orbital markets and trade stations"
            },
            {
                "name": "Commerce Station",
                "type": "Space Installation",
                "position": 2,
                "moons": 0,
                "population": 5_000_000,
                "notes": "Dedicated trading hub with no planetary surface"
            }
        ],
        "resources": "Moderate",
        "threat_level": 3,
        "trade_routes": ["Alpha Centauri", "Procyon Hub", "Altair Outpost", "Betelgeuse Sector"],
        "special_features": ["Central Exchange", "Guild Hall", "Commodity Vaults"]
    },
    
    "Rigel Station": {
        "coordinates": (30, 80, 20),
        "type": "Military",
        "description": "Heavily fortified border system protecting against external threats.",
        "controlling_faction": "Ironclad Collective",
        "founding_year": 3200,
        "history": [
            "3200: Constructed as defensive outpost during territorial conflicts",
            "3800: Major fleet base established",
            "5100: Withstood three-month siege during border wars",
            "6420: Command center during the Great Silence crisis"
        ],
        "planets": [
            {
                "name": "Rigel Fortress",
                "type": "Barren Rock",
                "position": 1,
                "moons": 0,
                "population": 3_000_000,
                "notes": "Entire planet converted to military installation"
            },
            {
                "name": "Sentinel Prime",
                "type": "Ice World",
                "position": 2,
                "moons": 3,
                "population": 500_000,
                "notes": "Early warning system and sensor arrays"
            }
        ],
        "resources": "Poor",
        "threat_level": 7,
        "trade_routes": ["Alpha Centauri"],
        "special_features": ["Fleet Command", "Defensive Grid", "Military Academy"]
    },
    
    "Betelgeuse Sector": {
        "coordinates": (90, 45, 35),
        "type": "Research",
        "description": "Advanced scientific research complex studying stellar phenomena.",
        "controlling_faction": "Scholara Nexus",
        "founding_year": 4100,
        "history": [
            "4100: Research outpost established to study the red supergiant",
            "4800: Major breakthrough in etheric field manipulation",
            "5500: Expanded to full research complex",
            "6150: Critical role in understanding Etheric Convergence"
        ],
        "planets": [
            {
                "name": "Observatory Prime",
                "type": "Terrestrial Planet",
                "position": 1,
                "moons": 1,
                "population": 8_000_000,
                "notes": "Primary research facilities and laboratories"
            },
            {
                "name": "Stellar Lab Beta",
                "type": "Research Colony",
                "position": 2,
                "moons": 0,
                "population": 2_000_000,
                "notes": "Specialized stellar research station"
            }
        ],
        "resources": "Rich",
        "threat_level": 2,
        "trade_routes": ["Vega Prime", "Alpha Centauri"],
        "special_features": ["Stellar Observatory", "Etheric Research Lab", "Data Archive"]
    },
    
    "Sirius Gate": {
        "coordinates": (55, 70, 28),
        "type": "Trading Hub",
        "description": "Major waypoint connecting core worlds to frontier systems.",
        "controlling_faction": "Stellar Nexus Guild",
        "founding_year": 2900,
        "history": [
            "2900: Established as navigation waypoint",
            "3300: Expanded to full trading station",
            "4200: Gate network hub constructed",
            "6000: Upgraded with advanced navigation systems"
        ],
        "planets": [
            {
                "name": "Sirius Alpha",
                "type": "Terrestrial Planet",
                "position": 1,
                "moons": 2,
                "population": 15_000_000,
                "notes": "Waystation services and refueling operations"
            },
            {
                "name": "Trade Nexus",
                "type": "Space Installation",
                "position": 2,
                "moons": 0,
                "population": 3_000_000,
                "notes": "Orbital trading complex"
            }
        ],
        "resources": "Moderate",
        "threat_level": 3,
        "trade_routes": ["Alpha Centauri", "Vega Prime", "Procyon Hub", "Frontier Systems"],
        "special_features": ["Gate Network Node", "Navigation Beacon", "Customs Station"]
    },
    
    "Tau Ceti": {
        "coordinates": (40, 40, 22),
        "type": "Agricultural",
        "description": "Breadbasket system supplying food to surrounding sectors.",
        "controlling_faction": "Harmonic Vitality Consortium",
        "founding_year": 2550,
        "history": [
            "2550: Terraformed for agricultural production",
            "3000: Became major food exporter",
            "4500: Bio-diversity preserve established",
            "6300: Organic matter synthesis breakthrough"
        ],
        "planets": [
            {
                "name": "Harvest World",
                "type": "Garden World",
                "position": 1,
                "moons": 1,
                "population": 22_000_000,
                "notes": "Vast agricultural zones producing multiple crops"
            },
            {
                "name": "Aqua Prime",
                "type": "Ocean World",
                "position": 2,
                "moons": 0,
                "population": 8_000_000,
                "notes": "Aquaculture and marine biology research"
            },
            {
                "name": "Pastoral Moon",
                "type": "Terrestrial Planet",
                "position": 3,
                "moons": 0,
                "population": 3_000_000,
                "notes": "Livestock and genetic engineering facilities"
            }
        ],
        "resources": "Rich",
        "threat_level": 2,
        "trade_routes": ["Alpha Centauri", "Vega Prime", "Tau Ceti"],
        "special_features": ["Bio-Preserve", "Seed Vault", "Agri-Research Center"]
    },
    
    "Kepler-442b": {
        "coordinates": (120, 85, 40),
        "type": "Frontier",
        "description": "Remote frontier colony on the edge of explored space.",
        "controlling_faction": None,  # Independent
        "founding_year": 5800,
        "history": [
            "5800: Survey team discovered the system",
            "6100: Small independent colony established",
            "6400: Survived isolation during Great Silence",
            "6900: Growing as a frontier trading post"
        ],
        "planets": [
            {
                "name": "New Horizon",
                "type": "Terrestrial Planet",
                "position": 1,
                "moons": 1,
                "population": 1_200_000,
                "notes": "Hardy colonists seeking independence"
            },
            {
                "name": "Frontier Outpost",
                "type": "Desert Planet",
                "position": 2,
                "moons": 0,
                "population": 300_000,
                "notes": "Mining and exploration base"
            }
        ],
        "resources": "Moderate",
        "threat_level": 6,
        "trade_routes": ["Sirius Gate"],
        "special_features": ["Scout Base", "Independent Market"]
    },
    
    "Ross 128": {
        "coordinates": (25, 30, 15),
        "type": "Mining",
        "description": "Rich asteroid mining operations and mineral processing.",
        "controlling_faction": "Gearwrights Guild",
        "founding_year": 3400,
        "history": [
            "3400: Rich mineral deposits discovered",
            "3700: Major mining corporations established operations",
            "4500: Gearwrights Guild took control of mining rights",
            "6000: Advanced automated mining systems deployed"
        ],
        "planets": [
            {
                "name": "Ross Prime",
                "type": "Mining World",
                "position": 1,
                "moons": 3,
                "population": 6_000_000,
                "notes": "Surface and subsurface mining operations"
            },
            {
                "name": "Forge Station",
                "type": "Industrial World",
                "position": 2,
                "moons": 0,
                "population": 4_000_000,
                "notes": "Ore processing and refinement"
            }
        ],
        "resources": "Abundant",
        "threat_level": 4,
        "trade_routes": ["Alpha Centauri", "Vega Prime"],
        "special_features": ["Asteroid Belt", "Processing Complex", "Mining Guild Hall"]
    },
    
    "Proxima b": {
        "coordinates": (48, 52, 24),
        "type": "Research",
        "description": "Cutting-edge xeno-archaeology and ancient civilization studies.",
        "controlling_faction": "Keepers of the Spire",
        "founding_year": 4900,
        "history": [
            "4900: Ancient ruins discovered beneath surface",
            "5200: Keepers of the Spire established research base",
            "5800: Major artifact excavation revealed lost technology",
            "6500: Ongoing studies of pre-convergence civilizations"
        ],
        "planets": [
            {
                "name": "Proxima Prime",
                "type": "Terrestrial Planet",
                "position": 1,
                "moons": 0,
                "population": 5_000_000,
                "notes": "Ancient ruins cover 30% of surface"
            },
            {
                "name": "Archive World",
                "type": "Barren Rock",
                "position": 2,
                "moons": 1,
                "population": 1_000_000,
                "notes": "Artifact storage and analysis facilities"
            }
        ],
        "resources": "Rich",
        "threat_level": 3,
        "trade_routes": ["Alpha Centauri", "Betelgeuse Sector"],
        "special_features": ["Ancient Ruins", "Artifact Vault", "Archaeological Institute"]
    },
    
    "TRAPPIST-1": {
        "coordinates": (110, 95, 45),
        "type": "Frontier",
        "description": "Seven-planet system with unique planetary configurations.",
        "controlling_faction": "Stellar Cartographers Alliance",
        "founding_year": 6200,
        "history": [
            "6200: Systematic survey revealed seven potentially habitable worlds",
            "6400: Cartographers Alliance claimed system for research",
            "6600: First colonies established on three worlds",
            "6900: Growing as navigation and exploration hub"
        ],
        "planets": [
            {
                "name": "TRAPPIST-1d",
                "type": "Ocean World",
                "position": 1,
                "moons": 0,
                "population": 2_000_000,
                "notes": "Water-rich world with unique marine ecosystems"
            },
            {
                "name": "TRAPPIST-1e",
                "type": "Terrestrial Planet",
                "position": 2,
                "moons": 0,
                "population": 3_500_000,
                "notes": "Most Earth-like of the seven worlds"
            },
            {
                "name": "TRAPPIST-1f",
                "type": "Ice World",
                "position": 3,
                "moons": 0,
                "population": 800_000,
                "notes": "Research outpost studying planetary formation"
            },
            {
                "name": "TRAPPIST-1g",
                "type": "Gas Giant",
                "position": 4,
                "moons": 8,
                "population": 200_000,
                "notes": "Fuel harvesting operations"
            }
        ],
        "resources": "Rich",
        "threat_level": 5,
        "trade_routes": ["Sirius Gate"],
        "special_features": ["Seven Worlds", "Navigation Hub", "Survey Station"]
    }
}


class SystemRegistry:
    """Registry and management for star systems"""
    
    def __init__(self):
        self.systems = {}
        self.systems_by_name = {}
        self.systems_by_faction = {}
        self.initialize_systems()
    
    def initialize_systems(self):
        """Initialize all predefined systems"""
        for name, data in STAR_SYSTEMS.items():
            coords = data['coordinates']
            self.systems[coords] = self._build_system(name, data)
            self.systems_by_name[name] = coords
            
            # Index by faction
            faction = data.get('controlling_faction')
            if faction:
                if faction not in self.systems_by_faction:
                    self.systems_by_faction[faction] = []
                self.systems_by_faction[faction].append(coords)
    
    def _build_system(self, name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Build a complete system object from definition"""
        system_type = data['type']
        type_data = SYSTEM_TYPES[system_type]
        
        # Generate celestial bodies from planet definitions
        celestial_bodies = []
        for i, planet_def in enumerate(data.get('planets', [])):
            planet_type = planet_def['type']
            
            # Handle special types
            if planet_type == "Space Installation" or planet_type == "Research Colony":
                # These are stations, not planets
                body = {
                    "object_type": "Station",
                    "name": planet_def['name'],
                    "population": planet_def.get('population', 0),
                    "notes": planet_def.get('notes', '')
                }
            else:
                planet_info = PLANET_TYPES.get(planet_type, PLANET_TYPES["Terrestrial Planet"])
                body = {
                    "object_type": "Planet",
                    "name": planet_def['name'],
                    "subtype": planet_type,
                    "position": planet_def.get('position', i + 1),
                    "has_atmosphere": planet_info['atmosphere'],
                    "habitable": planet_info['habitable'],
                    "population": planet_def.get('population', 0),
                    "resources": planet_info['resources'],
                    "notes": planet_def.get('notes', ''),
                    "controlling_faction": data.get('controlling_faction')
                }
                
                # Add moons if specified
                moon_count = planet_def.get('moons', 0)
                if moon_count > 0:
                    body['moons'] = moon_count
            
            celestial_bodies.append(body)
        
        # Calculate total population
        total_population = sum(p.get('population', 0) for p in data.get('planets', []))
        
        # Build complete system
        system = {
            "name": name,
            "coordinates": data['coordinates'],
            "type": system_type,
            "description": data['description'],
            "population": total_population,
            "threat_level": data.get('threat_level', random.randint(*type_data['threat_level'])),
            "resources": data.get('resources', random.choice(type_data['resource_quality'])),
            "stations": [],  # Will be populated from space_stations.py
            "celestial_bodies": celestial_bodies,
            "visited": False,
            "controlling_faction": data.get('controlling_faction'),
            "founding_year": data.get('founding_year'),
            "history": data.get('history', []),
            "trade_routes": data.get('trade_routes', []),
            "special_features": data.get('special_features', [])
        }
        
        return system
    
    def get_system(self, coordinates: Tuple[int, int, int]) -> Optional[Dict[str, Any]]:
        """Get a system by coordinates"""
        return self.systems.get(coordinates)
    
    def get_system_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a system by name"""
        coords = self.systems_by_name.get(name)
        return self.systems.get(coords) if coords else None
    
    def get_faction_systems(self, faction_name: str) -> List[Dict[str, Any]]:
        """Get all systems controlled by a faction"""
        coords_list = self.systems_by_faction.get(faction_name, [])
        return [self.systems[coords] for coords in coords_list if coords in self.systems]
    
    def get_all_systems(self) -> Dict[Tuple[int, int, int], Dict[str, Any]]:
        """Get all systems"""
        return self.systems
    
    def add_custom_system(self, name: str, coordinates: Tuple[int, int, int], 
                          system_type: str, **kwargs) -> Dict[str, Any]:
        """Add a custom system (for procedural generation or expansion)"""
        if coordinates in self.systems:
            raise ValueError(f"System already exists at {coordinates}")
        
        type_data = SYSTEM_TYPES.get(system_type, SYSTEM_TYPES["Frontier"])
        
        system = {
            "name": name,
            "coordinates": coordinates,
            "type": system_type,
            "description": kwargs.get('description', f"A {system_type.lower()} system"),
            "population": kwargs.get('population', random.randint(*type_data['population_range'])),
            "threat_level": kwargs.get('threat_level', random.randint(*type_data['threat_level'])),
            "resources": kwargs.get('resources', random.choice(type_data['resource_quality'])),
            "stations": kwargs.get('stations', []),
            "celestial_bodies": kwargs.get('celestial_bodies', []),
            "visited": False,
            "controlling_faction": kwargs.get('controlling_faction'),
            "founding_year": kwargs.get('founding_year'),
            "history": kwargs.get('history', []),
            "trade_routes": kwargs.get('trade_routes', []),
            "special_features": kwargs.get('special_features', [])
        }
        
        self.systems[coordinates] = system
        self.systems_by_name[name] = coordinates
        
        faction = system.get('controlling_faction')
        if faction:
            if faction not in self.systems_by_faction:
                self.systems_by_faction[faction] = []
            self.systems_by_faction[faction].append(coordinates)
        
        return system


# Create global registry instance
system_registry = SystemRegistry()
