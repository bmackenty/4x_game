"""
Space Navigation and Galaxy Map System

SYSTEM GENERATION:
- Loads 10 predefined star systems from systems.py with rich lore, history, and faction control
- Generates additional procedural systems to fill galaxy to 80-120 total systems
- Predefined systems include: Alpha Centauri, Vega Prime, Rigel Station, Betelgeuse Sector,
  Sirius Gate, Tau Ceti, Kepler-442b, Ross 128, Proxima b, and TRAPPIST-1
- Each predefined system has detailed planets, resources, history, trade routes, and special features
- Faction zones are built around predefined systems, then expanded with additional zones
"""

import random
import math
from systems import system_registry, SYSTEM_TYPES

class NPCShip:
    """NPC ship that moves around the galaxy"""
    def __init__(self, name, ship_class, start_coords, galaxy):
        self.name = name
        self.ship_class = ship_class
        self.coordinates = start_coords
        self.destination = None
        self.galaxy = galaxy
        self.personality = random.choice(["Friendly", "Cautious", "Greedy", "Chatty", "Mysterious", "Suspicious"])
        self.trade_goods = self._generate_trade_goods()
        self.credits = random.randint(5000, 50000)
        self.rumors = []
        
    def _generate_trade_goods(self):
        """Generate random trade goods for this NPC"""
        from goods import commodities
        goods = {}
        
        # Flatten commodities dict to list
        all_items = []
        for category, items in commodities.items():
            all_items.extend(items)
        
        if not all_items:
            return goods
        
        # NPC has 2-5 different commodity types
        num_types = random.randint(2, 5)
        available = random.sample(all_items, min(num_types, len(all_items)))
        for commodity in available:
            quantity = random.randint(5, 30)
            goods[commodity['name']] = quantity
        return goods
    
    def move(self):
        """Move NPC ship towards destination or pick new one"""
        if not self.destination:
            # Pick a random system as destination
            systems = list(self.galaxy.systems.values())
            if systems:
                target_system = random.choice(systems)
                self.destination = target_system['coordinates']
        
        if self.destination:
            # Move towards destination
            x, y, z = self.coordinates
            tx, ty, tz = self.destination
            
            # Simple movement - move 1-3 units per step in each direction
            step_size = random.randint(1, 3)
            dx = max(-step_size, min(step_size, tx - x))
            dy = max(-step_size, min(step_size, ty - y))
            dz = max(-step_size, min(step_size, tz - z))
            
            self.coordinates = (x + dx, y + dy, z + dz)
            
            # Check if reached destination
            if self.coordinates == self.destination:
                self.destination = None  # Pick new destination next move
    
    def get_greeting(self):
        """Get a greeting based on personality"""
        greetings = {
            "Friendly": [
                "Greetings, fellow traveler! Safe journeys to you!",
                "Hello there! Beautiful day for space travel, isn't it?",
                "Welcome! Always happy to meet another captain out here!"
            ],
            "Cautious": [
                "...Identify yourself. State your intentions.",
                "Keep your distance. What do you want?",
                "I'm monitoring you. Don't try anything."
            ],
            "Greedy": [
                "Credits first, questions later. What are you buying?",
                "Time is money, friend. Make it quick.",
                "I smell profit. What have you got for me?"
            ],
            "Chatty": [
                "Oh! A visitor! I have SO much to tell you!",
                "Finally, someone to talk to! You won't believe what I've seen!",
                "Wonderful! I've been out here for weeks with no one to chat with!"
            ],
            "Mysterious": [
                "...The void whispers secrets, traveler.",
                "Some encounters are destined. This may be one of them.",
                "Curious. I sensed your approach before you arrived."
            ],
            "Suspicious": [
                "What's your angle? Nobody just 'runs into' someone out here.",
                "Convenient timing. Too convenient. What do you really want?",
                "I don't trust coincidences. Why are you here?"
            ]
        }
        
        return random.choice(greetings.get(self.personality, ["Greetings."]))
    
    def generate_rumor(self):
        """Generate a random rumor or news"""
        rumor_types = [
            # Location rumors
            "I heard there's a mineral-rich asteroid field near {} - might be worth checking out.",
            "Word is {} has the best ship upgrades in this sector.",
            "They say {} is controlled by hostile forces these days. Stay alert.",
            "Someone mentioned a derelict station drifting near {}. Could be salvage.",
            
            # Economic rumors  
            "Prices for {} are through the roof in the core systems right now.",
            "I'm hearing {} is in high demand. Could fetch a good price.",
            "Market crash on {}! Buy low while you can.",
            
            # General rumors
            "I saw something strange in deep space... lights where no ships should be.",
            "Pirates have been hitting trade routes near the frontier lately.",
            "There's talk of a new research breakthrough at one of the science stations.",
            "Some trader was going on about 'temporal anomalies' - probably drunk.",
            "I heard the Stellar Consortium is recruiting new members.",
            "Word from the core worlds: tensions are rising between the major factions.",
        ]
        
        from goods import commodities
        
        rumor_template = random.choice(rumor_types)
        
        # Fill in placeholders
        if '{}' in rumor_template:
            # Needs a system name or commodity
            if 'asteroid' in rumor_template or 'upgrades' in rumor_template or 'hostile' in rumor_template or 'derelict' in rumor_template:
                # System name
                systems = list(self.galaxy.systems.values())
                if systems:
                    system = random.choice(systems)
                    rumor = rumor_template.format(system['name'])
                else:
                    rumor = rumor_template.replace(' near {}', '')
            else:
                # Commodity name - flatten commodities dict
                all_items = []
                for category, items in commodities.items():
                    all_items.extend(items)
                
                if all_items:
                    commodity = random.choice(all_items)
                    rumor = rumor_template.format(commodity['name'])
                else:
                    rumor = rumor_template.replace(' {}', ' rare goods')
        else:
            rumor = rumor_template
        
        return rumor


class Galaxy:
    def __init__(self):
        self.size_x = 500  # Galaxy width - substantially increased
        self.size_y = 500  # Galaxy height - substantially increased
        self.size_z = 200  # Galaxy depth - substantially increased
        self.systems = {}
        self.faction_zones = {}  # {faction_name: [(center_x, center_y, center_z), radius]}
        
        # Load predefined systems from systems.py
        self.load_predefined_systems()
        
        # Generate faction zones based on predefined systems
        self.generate_faction_zones()
        
        # Generate additional procedural systems to fill the galaxy
        self.generate_procedural_systems()
    
    def load_predefined_systems(self):
        """Load all predefined systems from systems.py"""
        predefined = system_registry.get_all_systems()
        self.systems.update(predefined)
        print(f"Loaded {len(predefined)} predefined star systems")
    
    def generate_faction_zones(self):
        """Generate faction-controlled zones based on predefined systems and additional coverage"""
        from factions import factions
        
        # First, create zones around predefined faction systems
        for coords, system in self.systems.items():
            faction = system.get('controlling_faction')
            if faction:
                if faction not in self.faction_zones:
                    self.faction_zones[faction] = {
                        'center': coords,
                        'radius': random.randint(50, 80),
                        'systems': [coords]
                    }
                else:
                    # Add to existing faction systems list
                    self.faction_zones[faction]['systems'].append(coords)
        
        # Add additional faction zones in unclaimed space
        faction_names = list(factions.keys())
        factions_without_zones = [f for f in faction_names if f not in self.faction_zones]
        
        # Create zones for remaining factions to leave some neutral space
        num_additional_zones = min(len(factions_without_zones), 8)
        selected_factions = random.sample(factions_without_zones, num_additional_zones) if factions_without_zones else []
        
        for faction_name in selected_factions:
            # Random center point for faction zone
            center_x = random.randint(100, self.size_x - 100)
            center_y = random.randint(100, self.size_y - 100)
            center_z = random.randint(50, self.size_z - 50)
            
            # Zone radius based on faction influence
            radius = random.randint(40, 70)
            
            self.faction_zones[faction_name] = {
                'center': (center_x, center_y, center_z),
                'radius': radius,
                'systems': []
            }
    
    def get_faction_for_location(self, x, y, z):
        """Get the controlling faction for a given location, if any"""
        for faction_name, zone_data in self.faction_zones.items():
            center = zone_data['center']
            radius = zone_data['radius']
            
            # Calculate distance from zone center
            distance = ((x - center[0])**2 + (y - center[1])**2 + (z - center[2])**2) ** 0.5
            
            if distance <= radius:
                return faction_name
        
        return None  # Neutral/unclaimed space
    
    def generate_procedural_systems(self):
        """Generate additional procedural systems to fill the galaxy (supplements predefined systems)"""
        from space_stations import space_stations
        
        # Calculate how many systems we already have
        existing_count = len(self.systems)
        # Only generate 5 additional systems to supplement the predefined ones
        num_to_generate = 5
        
        print(f"Generating {num_to_generate} additional procedural systems...")
        
        system_names = [
            "Procyon Hub", "Altair Outpost", "Arcturus Base",
            "Capella Nexus", "Aldebaran Port", "Antares Junction", "Spica Terminal",
            "Pollux Settlement", "Regulus Colony", "Deneb Fortress", "Canopus Trade Hub",
            "Bellatrix Mining", "Mintaka Research", "Alnilam Depot", "Alnitak Refinery",
            "Proxima Relay", "Wolf 359", "Barnard's Star", "Lalande 21185",
            "Ross 154", "Epsilon Eridani", "61 Cygni", "Groombridge 1618",
            "DX Cancri", "Gliese 667C", 
            "HD 40307g", "Gliese 581g", "Kepler-452b",
            "LHS 1140b", "Ross 128b", "TOI-715b",
            "Zeta Reticuli", "Beta Pictoris", "Fomalhaut", "Epsilon Indi",
            "Delta Pavonis", "Sigma Draconis", "Mu Arae", "Upsilon Andromedae",
            "47 Ursae Majoris", "55 Cancri", "Gamma Cephei", "HD 209458",
            "Gliese 876", "Gliese 436", "Gliese 832", "Gliese 163",
            "Kapteyn's Star", "Luyten's Star", "YZ Ceti", "Lacaille 9352",
            "GJ 1061", "GJ 15 A", "GJ 273", "GJ 433", "GJ 674", "GJ 832",
            "HD 85512", "HD 40307", "HD 69830", "HD 10180"
        ]
        
        # Remove names already used by predefined systems
        for system in self.systems.values():
            if system['name'] in system_names:
                system_names.remove(system['name'])
        
        # Available space stations
        available_stations = list(space_stations.keys())
        random.shuffle(available_stations)
        
        for i in range(num_to_generate):
            # Generate unique name
            if system_names:
                name = random.choice(system_names)
                system_names.remove(name)  # Avoid duplicates
            else:
                name = f"System-{existing_count + i + 1}"  # Fallback if we run out of names
            
            # Random coordinates within galaxy bounds, avoiding predefined system locations
            max_attempts = 50
            for attempt in range(max_attempts):
                x = random.randint(10, self.size_x - 10)
                y = random.randint(10, self.size_y - 10)
                z = random.randint(5, self.size_z - 5)
                
                # Check if too close to existing systems (minimum 15 units apart)
                too_close = False
                for existing_coords in self.systems.keys():
                    distance = ((x - existing_coords[0])**2 + 
                               (y - existing_coords[1])**2 + 
                               (z - existing_coords[2])**2) ** 0.5
                    if distance < 15:
                        too_close = True
                        break
                
                if not too_close:
                    break
            else:
                # If we couldn't find a good spot, just use the last attempt
                pass
            
            # Determine which faction controls this location
            controlling_faction = self.get_faction_for_location(x, y, z)
            
            # Determine system type first
            system_type = random.choice(["Core World", "Frontier", "Industrial", "Military", "Research", "Trading Hub", "Mining", "Agricultural"])
            
            # If in faction space, bias system type and stations based on faction focus
            if controlling_faction:
                from factions import factions
                faction_data = factions.get(controlling_faction, {})
                faction_focus = faction_data.get('primary_focus', '')
                
                # Bias system type based on faction focus
                if faction_focus == 'Trade':
                    system_type = random.choice(["Trading Hub", "Core World", "Industrial"])
                elif faction_focus == 'Research':
                    system_type = random.choice(["Research", "Core World", "Frontier"])
                elif faction_focus == 'Technology':
                    system_type = random.choice(["Industrial", "Research", "Core World"])
                elif faction_focus == 'Industry':
                    system_type = random.choice(["Industrial", "Mining", "Core World"])
                elif faction_focus == 'Exploration':
                    system_type = random.choice(["Frontier", "Research", "Trading Hub"])
                elif faction_focus == 'Mysticism':
                    system_type = random.choice(["Research", "Frontier", "Core World"])
                elif faction_focus == 'Cultural':
                    system_type = random.choice(["Core World", "Trading Hub", "Agricultural"])
            
            # Assign space stations to some systems
            # Increase station count in faction space
            if controlling_faction:
                system_station_count = random.choices([1, 2, 3, 4], weights=[30, 35, 25, 10])[0]
            else:
                system_station_count = random.choices([0, 1, 2, 3], weights=[40, 35, 20, 5])[0]
            
            system_stations = []
            for _ in range(system_station_count):
                if available_stations:
                    station_name = available_stations.pop()
                    station_data = space_stations[station_name].copy()
                    station_data['name'] = station_name
                    # Mark station as faction-controlled
                    if controlling_faction:
                        station_data['controlling_faction'] = controlling_faction
                    system_stations.append(station_data)
            
            # Generate celestial bodies for the system
            celestial_bodies = self.generate_celestial_bodies(system_type)
            
            # Mark habitable planets as faction-controlled
            if controlling_faction:
                for body in celestial_bodies:
                    if body.get('object_type') == 'Planet' and body.get('habitable'):
                        body['controlling_faction'] = controlling_faction
            
            # Generate system properties
            system = {
                "name": name,
                "coordinates": (x, y, z),
                "type": system_type,
                "population": random.randint(100000, 50000000),
                "threat_level": random.randint(1, 10),
                "resources": random.choice(["Rich", "Moderate", "Poor", "Abundant", "Depleted"]),
                "stations": system_stations,  # Now holds actual station data
                "celestial_bodies": celestial_bodies,  # Planets, moons, asteroids, etc.
                "visited": False,
                "description": self.generate_system_description(),
                "controlling_faction": controlling_faction  # NEW: Track faction control
            }
            
            # Add system to faction zone's system list
            if controlling_faction and controlling_faction in self.faction_zones:
                self.faction_zones[controlling_faction]['systems'].append((x, y, z))
            
            self.systems[(x, y, z)] = system
    
    def generate_celestial_bodies(self, system_type):
        """Generate planets, moons, asteroid belts, and other celestial bodies"""
        bodies = []
        
        # Number of major bodies (planets)
        num_planets = random.randint(1, 8)
        
        planet_types = [
            "Terrestrial Planet", "Gas Giant", "Ice Giant", "Lava World",
            "Ocean World", "Desert Planet", "Jungle World", "Frozen World",
            "Toxic Planet", "Crystal World", "Garden World", "Barren Rock"
        ]
        
        for i in range(num_planets):
            planet_type = random.choice(planet_types)
            planet = {
                "object_type": "Planet",
                "name": f"Planet {i+1}",
                "subtype": planet_type,
                "has_atmosphere": random.choice([True, False]),
                "habitable": planet_type in ["Garden World", "Terrestrial Planet", "Ocean World", "Jungle World"]
            }
            bodies.append(planet)
            
            # Some planets have moons
            if random.random() < 0.5:
                num_moons = random.randint(1, 4)
                for j in range(num_moons):
                    moon = {
                        "object_type": "Moon",
                        "name": f"Moon {chr(65+j)}",  # Moon A, B, C, etc.
                        "orbits": f"Planet {i+1}",
                        "has_resources": random.choice([True, False])
                    }
                    bodies.append(moon)
        
        # Asteroid belts
        if random.random() < 0.6:
            asteroid_belt = {
                "object_type": "Asteroid Belt",
                "name": "Asteroid Belt",
                "mineral_rich": random.choice([True, False]),
                "density": random.choice(["Sparse", "Moderate", "Dense"])
            }
            bodies.append(asteroid_belt)
        
        # Nebula clouds (rare)
        if random.random() < 0.2:
            nebula = {
                "object_type": "Nebula",
                "name": random.choice(["Stellar Nursery", "Emission Nebula", "Dark Nebula"]),
                "hazardous": random.choice([True, False])
            }
            bodies.append(nebula)
        
        # Comets (very rare)
        if random.random() < 0.1:
            comet = {
                "object_type": "Comet",
                "name": "Rogue Comet",
                "active": random.choice([True, False])
            }
            bodies.append(comet)
        
        return bodies
    
    def generate_system_description(self):
        """Generate random description for star systems"""
        descriptions = [
            "A bustling hub of interstellar commerce and trade.",
            "Ancient ruins dot the surfaces of several planets here.",
            "Rich asteroid fields provide abundant mining opportunities.", 
            "Home to advanced research facilities and universities.",
            "A heavily fortified military stronghold guards this sector.",
            "Lush agricultural worlds supply food across the galaxy.",
            "Mysterious energy readings emanate from this system.",
            "Pirates and smugglers are known to frequent this area.",
            "A peaceful system with beautiful nebula formations.",
            "Industrial megafactories operate around the clock here."
        ]
        return random.choice(descriptions)
    
    def get_system_at(self, x, y, z):
        """Get star system at specific coordinates"""
        return self.systems.get((x, y, z))
    
    def get_nearby_systems(self, x, y, z, range_limit=10):
        """Get all star systems within range"""
        nearby = []
        for coords, system in self.systems.items():
            distance = self.calculate_distance((x, y, z), coords)
            if distance <= range_limit and distance > 0:
                nearby.append((system, distance))
        
        # Sort by distance
        nearby.sort(key=lambda x: x[1])
        return nearby
    
    def calculate_distance(self, pos1, pos2):
        """Calculate 3D distance between two points"""
        x1, y1, z1 = pos1
        x2, y2, z2 = pos2
        return math.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)

class Ship:
    def __init__(self, name, ship_class="Basic Transport"):
        self.name = name
        self.ship_class = ship_class
        self.coordinates = (50, 50, 25)  # Start at galaxy center
        self.fuel = 100
        self.max_fuel = 100
        self.jump_range = 15  # Maximum jump distance
        self.cargo = {}
        self.max_cargo = 100
        self.scan_range = 5.0  # Default scanning range in map units
        
        # Component tracking for upgrade system
        self.components = {
            "hull": "Light Hull",  # Default starter hull
            "engine": "Ion Drive",  # Default starter engine
            "weapons": ["Pulse Cannons"],  # List of installed weapons
            "shields": ["Basic Deflectors"],  # List of installed shields
            "special": []  # List of special systems
        }
        
        # Ship stats based on class
        self.set_ship_stats()
    
    def set_ship_stats(self):
        """Set ship statistics based on class or components"""
        # If using component system, calculate from components
        if hasattr(self, 'components') and self.components:
            self.calculate_stats_from_components()
        else:
            # Legacy system for backwards compatibility
            ship_stats = {
                "Basic Transport": {"fuel": 100, "range": 15, "cargo": 100},
                "Starter Vessel": {"fuel": 100, "range": 15, "cargo": 100},
                "Aurora-Class Freighter": {"fuel": 150, "range": 20, "cargo": 200},
                "Stellar Voyager": {"fuel": 200, "range": 25, "cargo": 75},
                "Aurora Ascendant": {"fuel": 120, "range": 18, "cargo": 80},
                "Nebula Drifter": {"fuel": 180, "range": 22, "cargo": 90},
                "Celestium-Class Communication Ship": {"fuel": 130, "range": 20, "cargo": 60}
            }
            
            stats = ship_stats.get(self.ship_class, ship_stats["Basic Transport"])
            self.max_fuel = stats["fuel"]
            self.fuel = self.max_fuel
            self.jump_range = stats["range"]
            self.max_cargo = stats["cargo"]
    
    def calculate_stats_from_components(self):
        """Calculate ship stats from installed components"""
        try:
            from ship_builder import ship_components
            
            # Reset stats
            health = 0
            cargo_space = 0
            speed_mod = 1.0
            fuel_efficiency = 1.0
            scan_range = 5.0  # Base scan range
            
            # Hull stats
            if self.components.get("hull"):
                hull = ship_components["Hull Types"][self.components["hull"]]
                health = hull.get("health", 100)
                cargo_space = hull.get("cargo_space", 100)
                speed_mod = hull.get("speed_modifier", 1.0)
            
            # Engine stats
            if self.components.get("engine"):
                engine = ship_components["Engines"][self.components["engine"]]
                fuel_efficiency = engine.get("fuel_efficiency", 1.0)
                speed_mod *= engine.get("speed", 1.0)
            
            # Special system bonuses
            if self.components.get("special"):
                for system_name in self.components["special"]:
                    system = ship_components["Special Systems"][system_name]
                    if "cargo_bonus" in system:
                        cargo_space += system["cargo_bonus"]
                    if "scan_range" in system:
                        scan_range = system["scan_range"]
            
            # Apply calculated stats
            self.max_cargo = int(cargo_space)
            self.max_fuel = int(100 * fuel_efficiency)  # Base 100 fuel scaled by efficiency
            self.fuel = min(self.fuel, self.max_fuel)  # Don't exceed new max
            self.jump_range = int(15 * speed_mod)  # Base 15 range scaled by speed
            self.health = health
            self.scan_range = scan_range
            
        except ImportError:
            # Fallback if ship_builder not available
            pass
    
    def can_jump_to(self, target_coords, galaxy):
        """Check if ship can jump to target coordinates"""
        distance = galaxy.calculate_distance(self.coordinates, target_coords)
        fuel_needed = int(distance * 2)  # 2 fuel per unit distance
        
        return distance <= self.jump_range and fuel_needed <= self.fuel
    
    def jump_to(self, target_coords, galaxy, game=None):
        """Jump to target coordinates"""
        if self.can_jump_to(target_coords, galaxy):
            distance = galaxy.calculate_distance(self.coordinates, target_coords)
            fuel_needed = int(distance * 2)
            
            # Check for dangerous regions
            danger_warning = ""
            if game and hasattr(game, 'event_system'):
                if game.event_system.is_location_dangerous(target_coords):
                    danger_warning = " WARNING: Entering dangerous region!"
                    # Increase fuel cost in dangerous regions
                    fuel_needed = int(fuel_needed * 1.5)
            
            self.coordinates = target_coords
            self.fuel -= fuel_needed
            
            # Mark system as visited if there's one here
            system = galaxy.get_system_at(*target_coords)
            if system:
                system["visited"] = True
                # Update market when visiting (if game reference provided)
                if game and hasattr(game, 'economy') and system["name"] in game.economy.markets:
                    game.economy.update_market(system["name"])
            
            return True, f"Jumped to {target_coords}. Used {fuel_needed} fuel.{danger_warning}"
        else:
            return False, "Cannot reach target coordinates."
    
    def refuel(self):
        """Refuel ship to maximum capacity"""
        fuel_needed = self.max_fuel - self.fuel
        self.fuel = self.max_fuel
        return fuel_needed
    
    def get_objects_in_scan_range(self, galaxy):
        """Get all celestial bodies and systems within scan range.
        Returns a list of tuples: (object_type, object_data, distance)
        where object_type is 'system', 'planet', 'station', etc.
        """
        results = []
        ship_x, ship_y, ship_z = self.coordinates
        
        for coords, system in galaxy.systems.items():
            sys_x, sys_y, sys_z = coords
            # Calculate 2D distance (ignoring Z for now, since map is 2D)
            distance = math.sqrt((sys_x - ship_x)**2 + (sys_y - ship_y)**2)
            
            if distance <= self.scan_range and distance > 0:
                # System is in scan range
                results.append(('system', system, distance))
                
                # Check for stations in this system
                if system.get('stations'):
                    for station in system['stations']:
                        results.append(('station', station, distance))
                
                # Check for celestial bodies
                if system.get('celestial_bodies'):
                    for body in system['celestial_bodies']:
                        results.append((body['object_type'].lower(), body, distance))
        
        # Sort by distance
        results.sort(key=lambda x: x[2])
        return results

class NavigationSystem:
    def __init__(self, game):
        self.game = game
        self.galaxy = Galaxy()
        self.current_ship = None
        self.selected_ship_index = 0
        self.npc_ships = []  # List of NPC ships in the galaxy
        
        # Create markets for all star systems
        self.create_all_markets()
        
        # Spawn NPC ships
        self.spawn_npc_ships()
    
    def spawn_npc_ships(self):
        """Spawn a small number of NPC ships in the galaxy"""
        npc_names = [
            "Wandering Merchant", "Star Drifter", "Nomad Trader",
            "Deep Space Explorer", "Fortune Seeker", "Cosmic Voyager",
            "Stellar Nomad", "Void Runner", "Frontier Trader",
            "Nebula Wanderer", "Etheric Traveler", "Quantum Drifter"
        ]
        
        npc_ship_classes = [
            "Aurora-Class Freighter", "Stellar Voyager", "Nebula Drifter",
            "Celestium-Class Communication Ship", "Basic Transport"
        ]
        
        # Spawn 3-6 NPC ships
        num_npcs = random.randint(3, 6)
        
        systems = list(self.galaxy.systems.values())
        if not systems:
            return
        
        for i in range(min(num_npcs, len(npc_names))):
            name = npc_names[i]
            ship_class = random.choice(npc_ship_classes)
            # Start at random system
            start_system = random.choice(systems)
            start_coords = start_system['coordinates']
            
            npc = NPCShip(name, ship_class, start_coords, self.galaxy)
            self.npc_ships.append(npc)
    
    def update_npc_ships(self):
        """Move all NPC ships"""
        for npc in self.npc_ships:
            npc.move()
    
    def get_npc_at_location(self, coords):
        """Check if there's an NPC ship at the given coordinates"""
        x, y, z = coords
        for npc in self.npc_ships:
            nx, ny, nz = npc.coordinates
            # Check if within range (use larger range to account for movement steps)
            distance = math.sqrt((x-nx)**2 + (y-ny)**2 + (z-nz)**2)
            if distance <= 5.0:  # Larger range to catch encounters during map movement
                return npc
        return None
    
    def display_ship_status(self):
        """Display current ship status"""
        if not self.current_ship:
            print("No ship selected!")
            return
        
        ship = self.current_ship
        x, y, z = ship.coordinates
        
        print("\n" + "="*60)
        print("           SHIP STATUS")
        print("="*60)
        print(f"Ship: {ship.name} ({ship.ship_class})")
        print(f"Location: ({x}, {y}, {z})")
        print(f"Fuel: {ship.fuel}/{ship.max_fuel}")
        print(f"Jump Range: {ship.jump_range} units")
        print(f"Cargo: {sum(ship.cargo.values()) if ship.cargo else 0}/{ship.max_cargo}")
        
        # Check if at a star system
        system = self.galaxy.get_system_at(x, y, z)
        if system:
            print(f"\nCurrent System: {system['name']}")
            print(f"Type: {system['type']}")
            print(f"Population: {system['population']:,}")
            print(f"Resources: {system['resources']}")
            print(f"Threat Level: {system['threat_level']}/10")
            print(f"Description: {system['description']}")
            
            # Check for faction control
            if hasattr(self.game, 'faction_system'):
                controlling_faction = self.game.faction_system.get_system_faction((x, y, z))
                if controlling_faction:
                    rep_status = self.game.faction_system.get_reputation_status(controlling_faction)
                    print(f"\nControlled by: {controlling_faction}")
                    print(f"Your Standing: {rep_status}")
            
            # Check for space stations
            if hasattr(self.game, 'station_manager') and self.game.station_manager:
                station = self.game.station_manager.get_station_at_location((x, y, z))
                if station:
                    owner_status = "YOUR STATION" if station['owner'] == "Player" else "Available for Purchase"
                    print(f"\nSpace Station: {station['name']} ({station['type']})")
                    print(f"Status: {owner_status}")
                    print(f"Services: {', '.join(station['services'])}")
                    if station['owner'] == "Player":
                        print(f"Income: {station['income']:,} credits/cycle (Level {station['upgrade_level']})")
            
            # Check for bots at current location
            if hasattr(self.game, 'bot_manager') and self.game.bot_manager:
                bot = self.game.bot_manager.get_bot_at_location((x, y, z))
                if bot:
                    print(f"\nAI Bot Present: {bot.name} ({bot.bot_type})")
                    print(f"Bot Activity: {bot.current_goal}")
                    print(f"Bot Attitude: {bot.personality['type']}")
            
            # Check for archaeological sites at current location
            if hasattr(self.game, 'galactic_history'):
                sites = self.game.galactic_history.get_archaeological_sites_near(x, y, z, radius=1)
                if sites:
                    print(f"\n🏛️ Archaeological Sites Detected: {len(sites)}")
                    for site in sites:
                        coords = site['coordinates']
                        if coords == (x, y, z):  # Exact location
                            status = "EXCAVATED" if site.get('excavated', False) else "Unexplored"
                            print(f"  • {site['name']} ({site['civilization']}) - {status}")
                        else:
                            distance = ((x - coords[0])**2 + (y - coords[1])**2 + (z - coords[2])**2)**0.5
                            print(f"  • {site['name']} - {distance:.1f} units away")
        else:
            print("\nCurrent Location: Deep Space")
    
    def display_local_map(self):
        """Display nearby systems and navigation options"""
        if not self.current_ship:
            return
        
        x, y, z = self.current_ship.coordinates
        
        print("\n" + "="*60)
        print("           LOCAL SPACE MAP")
        print("="*60)
        
        nearby_systems = self.galaxy.get_nearby_systems(x, y, z, self.current_ship.jump_range)
        
        if nearby_systems:
            print("Systems within jump range:")
            for i, (system, distance) in enumerate(nearby_systems[:10], 1):
                fuel_cost = int(distance * 2)
                status = "✓" if system["visited"] else "?"
                reachable = "✓" if fuel_cost <= self.current_ship.fuel else "✗"
                
                # Check for bots and stations at this location
                coords = system['coordinates']
                extra_info = []
                
                # Check for stations
                if hasattr(self.game, 'station_manager') and self.game.station_manager:
                    station = self.game.station_manager.get_station_at_location(coords)
                    if station:
                        extra_info.append("🏗️")
                
                # Check for bots
                if hasattr(self.game, 'bot_manager') and self.game.bot_manager:
                    bot = self.game.bot_manager.get_bot_at_location(coords)
                    if bot:
                        extra_info.append("🤖")
                
                # Check for faction control
                if hasattr(self.game, 'faction_system'):
                    faction = self.game.faction_system.get_system_faction(coords)
                    if faction:
                        extra_info.append("⚑")
                
                # Check for archaeological sites
                if hasattr(self.game, 'galactic_history'):
                    sites = self.game.galactic_history.get_archaeological_sites_near(coords[0], coords[1], coords[2], radius=1)
                    if sites:
                        extra_info.append("🏛️")
                
                # Check for dangerous regions
                if hasattr(self.game, 'event_system'):
                    if self.game.event_system.is_location_dangerous(coords):
                        extra_info.append("⚠️")
                
                extra_str = " ".join(extra_info)
                if extra_str:
                    extra_str = f" | {extra_str}"
                
                print(f"{i:2d}. {system['name']:<20} [{system['coordinates']}]")
                print(f"     Distance: {distance:.1f} | Fuel: {fuel_cost} | {status} | {reachable}{extra_str}")
        else:
            print("No systems within jump range. You may need to refuel or get a better ship.")
        
        # Show all systems (for reference)
        print(f"\nTotal systems in galaxy: {len(self.galaxy.systems)}")
        visited_count = sum(1 for s in self.galaxy.systems.values() if s["visited"])
        print(f"Systems visited: {visited_count}/{len(self.galaxy.systems)}")
    
    def navigate_to_coordinates(self):
        """Manual navigation to specific coordinates"""
        if not self.current_ship:
            print("No ship selected!")
            return
        
        try:
            print("\nEnter target coordinates:")
            x = int(input("X coordinate (0-100): "))
            y = int(input("Y coordinate (0-100): "))
            z = int(input("Z coordinate (0-50): "))
            
            if not (0 <= x <= 100 and 0 <= y <= 100 and 0 <= z <= 50):
                print("Coordinates out of bounds!")
                return
            
            target = (x, y, z)
            distance = self.galaxy.calculate_distance(self.current_ship.coordinates, target)
            fuel_needed = int(distance * 2)
            
            print(f"\nTarget: ({x}, {y}, {z})")
            print(f"Distance: {distance:.1f} units")
            print(f"Fuel required: {fuel_needed}")
            
            if distance > self.current_ship.jump_range:
                print("Target is beyond ship's jump range!")
                return
            
            if fuel_needed > self.current_ship.fuel:
                print("Insufficient fuel for jump!")
                return
            
            confirm = input("\nProceed with jump? (y/n): ")
            if confirm.lower() == 'y':
                success, message = self.current_ship.jump_to(target, self.galaxy, self.game)
                print(f"\n{message}")
                
                # Check what's at the destination
                system = self.galaxy.get_system_at(*target)
                if system:
                    print(f"\nArrived at {system['name']}!")
                    print(f"{system['description']}")
                else:
                    print("\nArrived in empty space.")
        
        except ValueError:
            print("Invalid coordinates!")
    
    def navigate_to_system(self):
        """Navigate to a nearby star system"""
        if not self.current_ship:
            print("No ship selected!")
            return
        
        x, y, z = self.current_ship.coordinates
        nearby_systems = self.galaxy.get_nearby_systems(x, y, z, self.current_ship.jump_range)
        
        if not nearby_systems:
            print("No systems within range!")
            return
        
        print("\nAvailable destinations:")
        for i, (system, distance) in enumerate(nearby_systems[:10], 1):
            fuel_cost = int(distance * 2)
            can_reach = "✓" if fuel_cost <= self.current_ship.fuel else "✗"
            print(f"{i}. {system['name']} - Distance: {distance:.1f} - Fuel: {fuel_cost} {can_reach}")
        
        try:
            choice = int(input("\nSelect destination (number): ")) - 1
            if 0 <= choice < len(nearby_systems):
                system, distance = nearby_systems[choice]
                fuel_cost = int(distance * 2)
                
                if fuel_cost > self.current_ship.fuel:
                    print("Insufficient fuel!")
                    return
                
                success, message = self.current_ship.jump_to(system["coordinates"], self.galaxy, self.game)
                print(f"\n{message}")
                
                if success:
                    print(f"\nArrived at {system['name']}!")
                    print(f"{system['description']}")
            else:
                print("Invalid selection!")
        
        except ValueError:
            print("Invalid input!")
    
    def refuel_ship(self):
        """Refuel current ship"""
        if not self.current_ship:
            print("No ship selected!")
            return
        
        x, y, z = self.current_ship.coordinates
        system = self.galaxy.get_system_at(x, y, z)
        
        if not system:
            print("Cannot refuel in deep space! You need to be at a star system.")
            return
        
        fuel_needed = self.current_ship.max_fuel - self.current_ship.fuel
        if fuel_needed == 0:
            print("Ship is already fully fueled!")
            return
        
        fuel_cost = fuel_needed * 10  # 10 credits per fuel unit
        
        if fuel_cost > self.game.credits:
            print(f"Insufficient credits! Need {fuel_cost}, have {self.game.credits}")
            return
        
        print(f"Refuel cost: {fuel_cost} credits ({fuel_needed} fuel units)")
        confirm = input("Proceed with refuel? (y/n): ")
        
        if confirm.lower() == 'y':
            self.game.credits -= fuel_cost
            self.current_ship.refuel()
            print(f"\nShip refueled! Spent {fuel_cost} credits.")
    
    def select_ship(self):
        """Select which ship to pilot"""
        all_ships = self.game.owned_ships + [ship['name'] for ship in self.game.custom_ships]
        
        if not all_ships:
            print("No ships available!")
            return
        
        print("\nAvailable ships:")
        for i, ship_name in enumerate(all_ships, 1):
            current = " (CURRENT)" if self.current_ship and self.current_ship.name == ship_name else ""
            print(f"{i}. {ship_name}{current}")
        
        try:
            choice = int(input("\nSelect ship to pilot: ")) - 1
            if 0 <= choice < len(all_ships):
                ship_name = all_ships[choice]
                
                # Determine ship class
                if ship_name in self.game.owned_ships:
                    # Standard ship
                    ship_class = ship_name
                else:
                    # Custom ship - find its class
                    for custom_ship in self.game.custom_ships:
                        if custom_ship['name'] == ship_name:
                            ship_class = "Custom Ship"
                            break
                
                self.current_ship = Ship(ship_name, ship_class)
                print(f"\nNow piloting: {ship_name}")
            else:
                print("Invalid selection!")
        
        except ValueError:
            print("Invalid input!")
    
    def create_all_markets(self):
        """Create markets for all star systems"""
        for system in self.galaxy.systems.values():
            if hasattr(self.game, 'economy'):
                self.game.economy.create_market(system)
        
        # Initialize station manager after galaxy is created
        if hasattr(self.game, 'station_manager') and self.game.station_manager is None:
            from station_manager import SpaceStationManager
            self.game.station_manager = SpaceStationManager(self.galaxy)
        
        # Initialize bot manager after galaxy is created
        if hasattr(self.game, 'bot_manager') and self.game.bot_manager is None:
            from ai_bots import BotManager
            self.game.bot_manager = BotManager(self.game)
            self.game.start_bot_update_thread()
        
        # Initialize faction territories
        if hasattr(self.game, 'faction_system'):
            self.game.faction_system.assign_faction_territories(self.galaxy)
        
        # Initialize archaeological sites
        if hasattr(self.game, 'galactic_history'):
            sites_placed = self.game.galactic_history.place_archaeological_sites(self.galaxy)
            print(f"Galactic history initialized: {sites_placed} archaeological sites placed")