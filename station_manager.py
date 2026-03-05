"""
Ship Upgrade and Space Station Management System
"""

import random

# Must match GALAXY_SCALE in backend/hex_utils.py and frontend/js/views/galaxy.js
GALAXY_SCALE = 12.5


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
        """Get upgrades available for a specific ship (excludes already installed)."""
        installed = getattr(ship, 'upgrades', {}) or {}
        available = {}
        for category, upgrades in self.upgrade_categories.items():
            avail_in_cat = {name: data for name, data in upgrades.items()
                            if name not in installed}
            if avail_in_cat:
                available[category] = avail_in_cat
        return available

    def install_upgrade(self, ship, upgrade_name, upgrade_data):
        """Install an upgrade on a ship and apply its stat effects."""
        if not hasattr(ship, 'upgrades') or ship.upgrades is None:
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

        if 'scan_range' in upgrade_data:
            current = getattr(ship, 'scan_range', 1.0) or 1.0
            ship.scan_range = current * upgrade_data['scan_range']

        # Store upgrade for future reference
        ship.upgrades[upgrade_name] = upgrade_data

        return True, f"Successfully installed {upgrade_name}"


class SpaceStationManager:
    def __init__(self, galaxy):
        self.galaxy = galaxy
        self.station_types = {
            "Trading Post": {
                "cost": 500000,
                "services": ["Market", "Refuel", "Repairs"],
                "description": "Commercial hub with expanded trading facilities",
                "income_base": 5000,
                "economy_type": "Trading Hub",
            },
            "Mining Station": {
                "cost": 750000,
                "services": ["Market", "Ore Processing", "Refuel", "Mining Equipment"],
                "description": "Asteroid mining and ore processing facility",
                "income_base": 8000,
                "economy_type": "Mining",
            },
            "Research Lab": {
                "cost": 1000000,
                "services": ["Market", "Technology Research", "Ship Upgrades", "Data Analysis"],
                "description": "Advanced research and development facility",
                "income_base": 12000,
                "economy_type": "Research",
            },
            "Military Base": {
                "cost": 1200000,
                "services": ["Ship Upgrades", "Weapons", "Defense Systems", "Refuel"],
                "description": "Fortified military installation with defensive capabilities",
                "income_base": 15000,
                "economy_type": "Industrial",
            },
            "Shipyard": {
                "cost": 2000000,
                "services": ["Market", "Ship Construction", "Major Repairs", "Ship Upgrades"],
                "description": "Full ship construction and modification facility",
                "income_base": 25000,
                "economy_type": "Industrial",
            },
            "Luxury Resort": {
                "cost": 800000,
                "services": ["Market", "Entertainment", "Luxury Goods", "Passenger Transport"],
                "description": "High-end recreational facility for wealthy travelers",
                "income_base": 10000,
                "economy_type": "Trading Hub",
            },
        }

        # Stations keyed by name (unique string) for easy lookup
        self.stations = {}

        self.place_stations_in_galaxy()
        self._place_deep_space_stations()

    # -----------------------------------------------------------------------
    # Placement
    # -----------------------------------------------------------------------

    def place_stations_in_galaxy(self):
        """Place 15-20 NPC stations in random star systems."""
        systems = list(self.galaxy.systems.values())
        num_stations = random.randint(15, 20)

        if len(systems) < num_stations:
            num_stations = len(systems)

        selected_systems = random.sample(systems, num_stations)

        station_names = [
            "Nexus Prime", "Starforge Alpha", "Deep Space Nine", "Babylon Station",
            "Aurora Terminal", "Vega Outpost", "Centauri Hub", "Phoenix Base",
            "Titan Complex", "Nova Station", "Eclipse Platform", "Meridian Post",
            "Frontier Depot", "Stellar Gateway", "Crimson Outpost", "Azure Station",
            "Quantum Labs", "Helix Research", "Omega Base", "Apex Terminal",
        ]

        used_names = set()
        for i, system in enumerate(selected_systems):
            name = station_names[i] if i < len(station_names) else f"Station {i + 1}"
            # Ensure uniqueness (shouldn't happen, but guard it)
            while name in used_names:
                name = name + " II"
            used_names.add(name)

            station_type = random.choice(list(self.station_types.keys()))
            coords = system["coordinates"]

            self.stations[name] = {
                "name":         name,
                "type":         station_type,
                "coordinates":  coords,
                "hex_q":        self._coords_to_hex_q(coords),
                "hex_r":        self._coords_to_hex_r(coords),
                "system_name":  system["name"],   # in-system station
                "owner":        None,
                "services":     list(self.station_types[station_type]["services"]),
                "description":  self.station_types[station_type]["description"],
                "income":       self.station_types[station_type]["income_base"],
                "upgrade_level": 1,
                "last_income_collected": 0,
            }

    def _place_deep_space_stations(self):
        """Place 5-7 stations in the void between star systems."""
        systems = list(self.galaxy.systems.values())
        if len(systems) < 2:
            return

        deep_space_names = [
            "Void Citadel", "The Wandering Ark", "Liminal Platform",
            "Null Point Station", "The Drifting Spire", "Interstellar Waypoint",
            "The Abyssal Forge",
        ]
        count = random.randint(5, min(7, len(deep_space_names)))
        pairs = random.sample(
            [(systems[i], systems[j])
             for i in range(len(systems)) for j in range(i + 1, len(systems))],
            count
        )

        used_names = set(self.stations.keys())
        for pair_idx, (sys_a, sys_b) in enumerate(pairs):
            name = deep_space_names[pair_idx]
            if name in used_names:
                name = name + " II"
            used_names.add(name)

            ca = sys_a["coordinates"]
            cb = sys_b["coordinates"]
            # Midpoint of the two system positions
            coords = (
                (ca[0] + cb[0]) / 2.0,
                (ca[1] + cb[1]) / 2.0,
                (ca[2] + cb[2]) / 2.0,
            )

            station_type = random.choice(list(self.station_types.keys()))

            self.stations[name] = {
                "name":         name,
                "type":         station_type,
                "coordinates":  coords,
                "hex_q":        self._coords_to_hex_q(coords),
                "hex_r":        self._coords_to_hex_r(coords),
                "system_name":  None,             # deep-space: not in any system
                "owner":        None,
                "services":     list(self.station_types[station_type]["services"]),
                "description":  self.station_types[station_type]["description"],
                "income":       self.station_types[station_type]["income_base"],
                "upgrade_level": 1,
                "last_income_collected": 0,
            }

    # -----------------------------------------------------------------------
    # Coordinate helpers (mirrors backend/hex_utils.py)
    # -----------------------------------------------------------------------

    def _coords_to_hex_q(self, coords):
        return round(coords[0] / GALAXY_SCALE)

    def _coords_to_hex_r(self, coords):
        return round(coords[1] / GALAXY_SCALE)

    # -----------------------------------------------------------------------
    # Lookups
    # -----------------------------------------------------------------------

    def get_station_by_name(self, name: str):
        """Return the station dict for the given name, or None."""
        return self.stations.get(name)

    def get_station_at_location(self, coordinates):
        """Return the first station whose coordinates match (within rounding)."""
        target_q = round(coordinates[0] / GALAXY_SCALE)
        target_r = round(coordinates[1] / GALAXY_SCALE)
        for station in self.stations.values():
            if station["hex_q"] == target_q and station["hex_r"] == target_r:
                return station
        return None

    def get_stations_in_system(self, system_name: str):
        """Return all stations in a given star system."""
        return [s for s in self.stations.values() if s.get("system_name") == system_name]

    def get_deep_space_stations(self):
        """Return stations not associated with any star system."""
        return [s for s in self.stations.values() if s.get("system_name") is None]

    def get_player_stations(self):
        """Return all player-owned stations."""
        return [s for s in self.stations.values() if s.get("owner") == "Player"]

    # -----------------------------------------------------------------------
    # Economy type for market registration
    # -----------------------------------------------------------------------

    def get_economy_type(self, station_type: str) -> str:
        return self.station_types.get(station_type, {}).get("economy_type", "Trading Hub")

    # -----------------------------------------------------------------------
    # Ownership / upgrades
    # -----------------------------------------------------------------------

    def purchase_station(self, station_name: str, player_credits: int):
        """Purchase a station by name."""
        station = self.stations.get(station_name)
        if not station:
            return False, "No station with that name", 0

        if station["owner"] is not None:
            return False, "Station already owned", 0

        cost = self.station_types[station["type"]]["cost"]
        if player_credits < cost:
            return False, f"Insufficient credits. Need {cost:,}, have {player_credits:,}", 0

        station["owner"] = "Player"
        return True, f"Successfully purchased {station['name']}", cost

    def collect_station_income(self, station):
        income = station["income"] * station["upgrade_level"]
        station["last_income_collected"] += 1
        return income

    def upgrade_station(self, station_name: str, player_credits: int):
        station = self.stations.get(station_name)
        if not station or station.get("owner") != "Player":
            return False, "You don't own this station", 0

        level = station["upgrade_level"]
        if level >= 5:
            return False, "Station already at maximum upgrade level", 0

        upgrade_cost = station["income"] * level * 10
        if player_credits < upgrade_cost:
            return False, f"Insufficient credits. Need {upgrade_cost:,}", 0

        station["upgrade_level"] += 1
        station["income"] = int(station["income"] * 1.2)
        return True, f"Upgraded {station['name']} to level {station['upgrade_level']}", upgrade_cost

    def get_all_stations_info(self):
        """Group all stations by system (None key = deep space)."""
        by_system = {}
        for station in self.stations.values():
            key = station.get("system_name")  # None for deep-space
            by_system.setdefault(key, []).append(station)
        return by_system
