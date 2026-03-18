"""
Star Systems Module - Deterministic System Definitions

All system data is stored in lore/systems.json.
This module loads that file and exposes the same public API as before,
so all existing callers (navigation.py, etc.) are unaffected.

SystemRegistry wraps the loaded data and tracks per-session state
(visited flags, custom systems, faction indexing).
"""

import json
import pathlib
import random
from typing import Dict, List, Optional, Tuple, Any

# ── Load raw data from lore/systems.json ──────────────────────────────────────
_LORE_PATH = pathlib.Path(__file__).parent / "lore" / "systems.json"

with _LORE_PATH.open(encoding="utf-8") as _f:
    _data = json.load(_f)

# ── Public data ────────────────────────────────────────────────────────────────
# JSON stores tuples as lists; convert coordinates back to tuples so they can
# be used as dict keys (matching the original behaviour).

for _zone in _data["faction_zones"].values():
    _zone["center"] = tuple(_zone["center"])

for _sys in _data["star_systems"].values():
    _sys["coordinates"] = tuple(_sys["coordinates"])

# Faction zones: faction_name → {center, radius, description}
FACTION_ZONES: dict = _data["faction_zones"]

# Faction display colours: faction_name → hex colour string
FACTION_COLORS: dict = _data["faction_colors"]

# System type templates: type_name → {population_range, threat_level, ...}
SYSTEM_TYPES: dict = _data["system_types"]

# Planet type templates: type_name → {atmosphere, habitable, resources}
PLANET_TYPES: dict = _data["planet_types"]

# Named star system definitions: system_name → {coordinates, type, planets, ...}
STAR_SYSTEMS: dict = _data["star_systems"]


# ── SystemRegistry class ───────────────────────────────────────────────────────

class SystemRegistry:
    """Registry and management for star systems."""

    def __init__(self):
        self.systems = {}
        self.systems_by_name = {}
        self.systems_by_faction = {}
        self.initialize_systems()

    def initialize_systems(self):
        """Initialize all predefined systems."""
        for name, data in STAR_SYSTEMS.items():
            coords = data['coordinates']
            self.systems[coords] = self._build_system(name, data)
            self.systems_by_name[name] = coords

            # Index by controlling faction
            faction = data.get('controlling_faction')
            if faction:
                self.systems_by_faction.setdefault(faction, []).append(coords)

    def _build_system(self, name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Build a complete system object from a definition entry."""
        system_type = data['type']
        type_data = SYSTEM_TYPES[system_type]

        # Generate celestial bodies from planet definitions
        celestial_bodies = []
        for i, planet_def in enumerate(data.get('planets', [])):
            planet_type = planet_def['type']

            if planet_type in ("Space Installation", "Research Colony"):
                # Stations, not planets
                body = {
                    "object_type": "Station",
                    "name":        planet_def['name'],
                    "population":  planet_def.get('population', 0),
                    "notes":       planet_def.get('notes', '')
                }
            else:
                planet_info = PLANET_TYPES.get(planet_type, PLANET_TYPES["Terrestrial Planet"])
                body = {
                    "object_type":        "Planet",
                    "name":               planet_def['name'],
                    "subtype":            planet_type,
                    "position":           planet_def.get('position', i + 1),
                    "has_atmosphere":     planet_info['atmosphere'],
                    "habitable":          planet_info['habitable'],
                    "population":         planet_def.get('population', 0),
                    "resources":          planet_info['resources'],
                    "notes":              planet_def.get('notes', ''),
                    "controlling_faction":data.get('controlling_faction'),
                    "shipyard":           True  # Every planet has a shipyard
                }
                moon_count = planet_def.get('moons', 0)
                if moon_count > 0:
                    body['moons'] = moon_count

            celestial_bodies.append(body)

        total_population = sum(p.get('population', 0) for p in data.get('planets', []))

        return {
            "name":               name,
            "coordinates":        data['coordinates'],
            "type":               system_type,
            "description":        data['description'],
            "population":         total_population,
            "threat_level":       data.get('threat_level', random.randint(*type_data['threat_level'])),
            "resources":          data.get('resources', random.choice(type_data['resource_quality'])),
            "stations":           [],  # Populated from space_stations.py
            "celestial_bodies":   celestial_bodies,
            "visited":            False,
            "controlling_faction":data.get('controlling_faction'),
            "founding_year":      data.get('founding_year'),
            "history":            data.get('history', []),
            "trade_routes":       data.get('trade_routes', []),
            "special_features":   data.get('special_features', [])
        }

    def get_system(self, coordinates: Tuple[int, int, int]) -> Optional[Dict[str, Any]]:
        """Return a system by coordinates."""
        return self.systems.get(coordinates)

    def get_system_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Return a system by name."""
        coords = self.systems_by_name.get(name)
        return self.systems.get(coords) if coords else None

    def get_faction_systems(self, faction_name: str) -> List[Dict[str, Any]]:
        """Return all systems controlled by a faction."""
        coords_list = self.systems_by_faction.get(faction_name, [])
        return [self.systems[coords] for coords in coords_list if coords in self.systems]

    def get_all_systems(self) -> Dict[Tuple[int, int, int], Dict[str, Any]]:
        """Return all systems."""
        return self.systems

    def add_custom_system(self, name: str, coordinates: Tuple[int, int, int],
                          system_type: str, **kwargs) -> Dict[str, Any]:
        """Add a custom system (for procedural generation or expansion)."""
        if coordinates in self.systems:
            raise ValueError(f"System already exists at {coordinates}")

        type_data = SYSTEM_TYPES.get(system_type, SYSTEM_TYPES["Frontier"])

        system = {
            "name":               name,
            "coordinates":        coordinates,
            "type":               system_type,
            "description":        kwargs.get('description', f"A {system_type.lower()} system"),
            "population":         kwargs.get('population', random.randint(*type_data['population_range'])),
            "threat_level":       kwargs.get('threat_level', random.randint(*type_data['threat_level'])),
            "resources":          kwargs.get('resources', random.choice(type_data['resource_quality'])),
            "stations":           kwargs.get('stations', []),
            "celestial_bodies":   kwargs.get('celestial_bodies', []),
            "visited":            False,
            "controlling_faction":kwargs.get('controlling_faction'),
            "founding_year":      kwargs.get('founding_year'),
            "history":            kwargs.get('history', []),
            "trade_routes":       kwargs.get('trade_routes', []),
            "special_features":   kwargs.get('special_features', [])
        }

        self.systems[coordinates] = system
        self.systems_by_name[name] = coordinates

        faction = system.get('controlling_faction')
        if faction:
            self.systems_by_faction.setdefault(faction, []).append(coordinates)

        return system


# ── Global registry instance ───────────────────────────────────────────────────
system_registry = SystemRegistry()
