"""
Space Navigation and Galaxy Map System
"""

import random
import math

class Galaxy:
    def __init__(self):
        self.size_x = 100  # Galaxy width
        self.size_y = 100  # Galaxy height  
        self.size_z = 50   # Galaxy depth
        self.systems = {}
        self.generate_star_systems()
    
    def generate_star_systems(self):
        """Generate random star systems throughout the galaxy"""
        from space_stations import space_stations
        
        system_names = [
            "Alpha Centauri", "Vega Prime", "Rigel Station", "Betelgeuse Sector",
            "Sirius Gate", "Procyon Hub", "Altair Outpost", "Arcturus Base",
            "Capella Nexus", "Aldebaran Port", "Antares Junction", "Spica Terminal",
            "Pollux Settlement", "Regulus Colony", "Deneb Fortress", "Canopus Trade Hub",
            "Bellatrix Mining", "Mintaka Research", "Alnilam Depot", "Alnitak Refinery",
            "Proxima Relay", "Wolf 359", "Barnard's Star", "Lalande 21185",
            "Ross 154", "Epsilon Eridani", "61 Cygni", "Groombridge 1618",
            "DX Cancri", "Tau Ceti", "Gliese 667C", "Kepler-442b",
            "HD 40307g", "Gliese 581g", "Kepler-452b", "TRAPPIST-1",
            "LHS 1140b", "Proxima b", "Ross 128b", "TOI-715b"
        ]
        
        # Generate 30-40 star systems
        num_systems = random.randint(30, 40)
        
        # Available space stations
        available_stations = list(space_stations.keys())
        random.shuffle(available_stations)
        
        for i in range(num_systems):
            name = random.choice(system_names)
            system_names.remove(name)  # Avoid duplicates
            
            # Random coordinates within galaxy bounds
            x = random.randint(10, self.size_x - 10)
            y = random.randint(10, self.size_y - 10)
            z = random.randint(5, self.size_z - 5)
            
            # Determine system type first
            system_type = random.choice(["Core World", "Frontier", "Industrial", "Military", "Research", "Trading Hub", "Mining", "Agricultural"])
            
            # Assign space stations to some systems
            system_station_count = random.choices([0, 1, 2, 3], weights=[40, 35, 20, 5])[0]
            system_stations = []
            for _ in range(system_station_count):
                if available_stations:
                    station_name = available_stations.pop()
                    station_data = space_stations[station_name].copy()
                    station_data['name'] = station_name
                    system_stations.append(station_data)
            
            # Generate celestial bodies for the system
            celestial_bodies = self.generate_celestial_bodies(system_type)
            
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
                "description": self.generate_system_description()
            }
            
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
        
        # Ship stats based on class
        self.set_ship_stats()
    
    def set_ship_stats(self):
        """Set ship statistics based on class"""
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

class NavigationSystem:
    def __init__(self, game):
        self.game = game
        self.galaxy = Galaxy()
        self.current_ship = None
        self.selected_ship_index = 0
        
        # Create markets for all star systems
        self.create_all_markets()
    
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