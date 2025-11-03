#!/usr/bin/env python3
"""
Helper script to show research station locations in current galaxy
"""

from navigation import Galaxy
from space_stations import space_stations

def show_research_locations():
    print("=" * 80)
    print(" " * 25 + "RESEARCH STATION LOCATOR")
    print("=" * 80)
    
    galaxy = Galaxy()
    
    # Find all research stations
    research_locations = []
    
    for coords, system in galaxy.systems.items():
        stations = system.get('stations', [])
        for station in stations:
            category = station.get('category', '')
            station_type = station.get('type', '')
            if 'Research' in category or 'Lab' in station_type:
                research_locations.append({
                    'station_name': station.get('name'),
                    'station_type': station.get('type'),
                    'system_name': system['name'],
                    'coordinates': coords,
                    'system_type': system['type'],
                    'description': station.get('description', '')
                })
    
    if not research_locations:
        print("\n⚠️  WARNING: No research stations found in this galaxy!")
        print("This is very rare. Try restarting the game to generate a new galaxy.")
        print("=" * 80)
        return
    
    print(f"\n✓ Found {len(research_locations)} research station(s) in the galaxy")
    print(f"  ({len(galaxy.systems)} total systems)")
    print()
    
    # Sort by coordinates for easier navigation
    research_locations.sort(key=lambda x: x['coordinates'])
    
    print("RESEARCH STATION DIRECTORY:")
    print("─" * 80)
    
    for i, loc in enumerate(research_locations, 1):
        x, y, z = loc['coordinates']
        print(f"\n{i}. {loc['station_name']}")
        print(f"   Type: {loc['station_type']}")
        print(f"   System: {loc['system_name']} ({loc['system_type']})")
        print(f"   Coordinates: ({x}, {y}, {z})")
        print(f"   Description: {loc['description'][:65]}...")
    
    print("\n" + "─" * 80)
    print("\nHOW TO FIND RESEARCH STATIONS:")
    print("  1. Open the galaxy map (press 'm' in game)")
    print("  2. Navigate to the coordinates listed above")
    print("  3. Look for station symbols: ◈ (visited) or ◆ (unvisited)")
    print("  4. If you have a scanner, you'll see 'S' below nearby stations")
    print("  5. Enter the system and select the research station")
    print("\nTIP: Install a Scanner Array (8.0 range) or better to detect")
    print("     research stations from farther away!")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    show_research_locations()
