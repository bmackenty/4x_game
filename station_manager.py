"""
Ship Upgrade and Space Station Management System
"""

import random

class ShipUpgradeSystem:
    def __init__(self):
        self.upgrade_categories = {
            "Engine Upgrades": {
                "Ion Drive Mk2": {
                    "cost": 25000,
                    "fuel_efficiency": 1.2,
                    "speed": 1.1,
                    "description": "Improved ion drive with better fuel efficiency"
                },
                "Fusion Engine Mk2": {
                    "cost": 45000,
                    "fuel_efficiency": 1.0,
                    "speed": 1.4,
                    "description": "Enhanced fusion engine with higher thrust"
                },
                "Quantum Booster": {
                    "cost": 75000,
                    "fuel_efficiency": 0.9,
                    "speed": 1.8,
                    "jump_range": 1.3,
                    "description": "Experimental quantum field manipulation drive"
                }
            },
            "Fuel Systems": {
                "Extended Fuel Tanks": {
                    "cost": 15000,
                    "max_fuel": 1.5,
                    "description": "Increases maximum fuel capacity by 50%"
                },
                "Fuel Recycler": {
                    "cost": 30000,
                    "fuel_efficiency": 1.3,
                    "description": "Recycles waste energy to improve fuel efficiency"
                },
                "Emergency Reserves": {
                    "cost": 20000,
                    "emergency_fuel": 50,
                    "description": "Emergency fuel reserves for crisis situations"
                }
            },
            "Cargo Systems": {
                "Cargo Bay Expansion": {
                    "cost": 20000,
                    "max_cargo": 1.4,
                    "description": "Increases cargo capacity by 40%"
                },
                "Smart Storage": {
                    "cost": 35000,
                    "max_cargo": 1.6,
                    "cargo_efficiency": 1.2,
                    "description": "AI-managed storage with compression technology"
                },
                "Modular Containers": {
                    "cost": 25000,
                    "max_cargo": 1.3,
                    "loading_speed": 2.0,
                    "description": "Quick-swap container system for faster loading"
                }
            },
            "Navigation Systems": {
                "Advanced Scanner": {
                    "cost": 40000,
                    "scan_range": 2.0,
                    "description": "Extended range sensors and navigation computer"
                },
                "Jump Computer": {
                    "cost": 60000,
                    "jump_accuracy": 1.5,
                    "fuel_efficiency": 1.1,
                    "description": "Precision jump calculations reduce fuel waste"
                },
                "Stellar Cartographer": {
                    "cost": 50000,
                    "exploration_bonus": 1.3,
                    "description": "Automated system mapping and analysis tools"
                }
            },
            "Defensive Systems": {
                "Reinforced Hull": {
                    "cost": 30000,
                    "hull_strength": 1.4,
                    "description": "Additional armor plating and structural reinforcement"
                },
                "Shield Booster": {
                    "cost": 45000,
                    "shield_strength": 1.6,
                    "shield_recharge": 1.3,
                    "description": "Enhanced shield generators and capacitors"
                },
                "Point Defense": {
                    "cost": 55000,
                    "missile_defense": 0.7,
                    "description": "Automated defense against missiles and debris"
                }
            },
            "Life Support": {
                "Extended Life Support": {
                    "cost": 25000,
                    "crew_capacity": 1.3,
                    "description": "Support for larger crew and longer missions"
                },
                "Medical Bay": {
                    "cost": 40000,
                    "crew_health": 1.5,
                    "description": "Advanced medical facilities for crew health"
                },
                "Luxury Quarters": {
                    "cost": 60000,
                    "crew_morale": 1.4,
                    "passenger_capacity": 2.0,
                    "description": "Comfortable accommodations for crew and passengers"
                }
            }
        }
    
    def get_available_upgrades(self, ship):
        """Get upgrades available for a specific ship"""
        available = {}
        
        # Check which upgrades the ship doesn't already have
        for category, upgrades in self.upgrade_categories.items():
            available[category] = {}
            for name, upgrade in upgrades.items():
                if not hasattr(ship, 'upgrades') or name not in ship.upgrades:
                    available[category][name] = upgrade
        
        return available
    
    def install_upgrade(self, ship, upgrade_name, upgrade_data):
        """Install an upgrade on a ship"""
        if not hasattr(ship, 'upgrades'):
            ship.upgrades = {}
        
        if upgrade_name in ship.upgrades:
            return False, "Upgrade already installed"
        
        # Apply upgrade effects
        if 'max_fuel' in upgrade_data:
            ship.max_fuel = int(ship.max_fuel * upgrade_data['max_fuel'])
            ship.fuel = min(ship.fuel, ship.max_fuel)
        
        if 'max_cargo' in upgrade_data:
            ship.max_cargo = int(ship.max_cargo * upgrade_data['max_cargo'])
        
        if 'jump_range' in upgrade_data:
            ship.jump_range = int(ship.jump_range * upgrade_data['jump_range'])
        
        # Store upgrade for future reference
        ship.upgrades[upgrade_name] = upgrade_data
        
        return True, f"Successfully installed {upgrade_name}"

class SpaceStationManager:
    def __init__(self, galaxy):
        self.galaxy = galaxy
        self.stations = {}
        self.station_types = {
            "Trading Post": {
                "cost": 500000,
                "services": ["Market", "Refuel", "Repairs"],
                "description": "Commercial hub with expanded trading facilities",
                "income_base": 5000
            },
            "Mining Station": {
                "cost": 750000,
                "services": ["Ore Processing", "Refuel", "Mining Equipment"],
                "description": "Asteroid mining and ore processing facility",
                "income_base": 8000
            },
            "Research Lab": {
                "cost": 1000000,
                "services": ["Technology Research", "Ship Upgrades", "Data Analysis"],
                "description": "Advanced research and development facility",
                "income_base": 12000
            },
            "Military Base": {
                "cost": 1200000,
                "services": ["Ship Upgrades", "Weapons", "Defense Systems"],
                "description": "Fortified military installation with defensive capabilities",
                "income_base": 15000
            },
            "Shipyard": {
                "cost": 2000000,
                "services": ["Ship Construction", "Major Repairs", "Ship Upgrades"],
                "description": "Full ship construction and modification facility",
                "income_base": 25000
            },
            "Luxury Resort": {
                "cost": 800000,
                "services": ["Entertainment", "Luxury Goods", "Passenger Transport"],
                "description": "High-end recreational facility for wealthy travelers",
                "income_base": 10000
            }
        }
        
        self.place_stations_in_galaxy()
    
    def place_stations_in_galaxy(self):
        """Place existing stations throughout the galaxy"""
        # Place 15-20 stations in various systems
        systems = list(self.galaxy.systems.values())
        num_stations = random.randint(15, 20)
        
        selected_systems = random.sample(systems, num_stations)
        
        station_names = [
            "Nexus Prime", "Starforge Alpha", "Deep Space Nine", "Babylon Station",
            "Aurora Terminal", "Vega Outpost", "Centauri Hub", "Phoenix Base",
            "Titan Complex", "Nova Station", "Eclipse Platform", "Meridian Post",
            "Frontier Depot", "Stellar Gateway", "Crimson Outpost", "Azure Station",
            "Quantum Labs", "Helix Research", "Omega Base", "Apex Terminal"
        ]
        
        for i, system in enumerate(selected_systems):
            if i < len(station_names):
                station_name = station_names[i]
            else:
                station_name = f"Station {i+1}"
            
            station_type = random.choice(list(self.station_types.keys()))
            coords = system['coordinates']
            
            station = {
                'name': station_name,
                'type': station_type,
                'coordinates': coords,
                'system_name': system['name'],
                'owner': None,  # Can be purchased by player
                'services': self.station_types[station_type]['services'],
                'description': self.station_types[station_type]['description'],
                'income': self.station_types[station_type]['income_base'],
                'upgrade_level': 1,
                'last_income_collected': 0
            }
            
            self.stations[coords] = station
    
    def get_station_at_location(self, coordinates):
        """Get station at specific coordinates"""
        return self.stations.get(coordinates)
    
    def purchase_station(self, coordinates, player_credits):
        """Purchase a station"""
        station = self.stations.get(coordinates)
        if not station:
            return False, "No station at this location", 0
        
        if station['owner'] is not None:
            return False, "Station already owned", 0
        
        station_type = station['type']
        cost = self.station_types[station_type]['cost']
        
        if player_credits < cost:
            return False, f"Insufficient credits. Need {cost:,}, have {player_credits:,}", 0
        
        station['owner'] = "Player"
        return True, f"Successfully purchased {station['name']}", cost
    
    def get_player_stations(self):
        """Get all player-owned stations"""
        return [station for station in self.stations.values() if station['owner'] == "Player"]
    
    def collect_station_income(self, station):
        """Collect income from a station"""
        income = station['income'] * station['upgrade_level']
        station['last_income_collected'] += 1
        return income
    
    def upgrade_station(self, coordinates, player_credits):
        """Upgrade a station to increase income"""
        station = self.stations.get(coordinates)
        if not station or station['owner'] != "Player":
            return False, "You don't own this station", 0
        
        current_level = station['upgrade_level']
        if current_level >= 5:
            return False, "Station already at maximum upgrade level", 0
        
        upgrade_cost = station['income'] * current_level * 10  # 10x income per level
        
        if player_credits < upgrade_cost:
            return False, f"Insufficient credits. Need {upgrade_cost:,}, have {player_credits:,}", 0
        
        station['upgrade_level'] += 1
        station['income'] = int(station['income'] * 1.2)  # 20% income increase per level
        
        return True, f"Upgraded {station['name']} to level {station['upgrade_level']}", upgrade_cost
    
    def get_all_stations_info(self):
        """Get information about all stations in galaxy"""
        stations_by_system = {}
        
        for station in self.stations.values():
            system_name = station['system_name']
            if system_name not in stations_by_system:
                stations_by_system[system_name] = []
            stations_by_system[system_name].append(station)
        
        return stations_by_system