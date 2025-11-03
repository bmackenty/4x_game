#!/usr/bin/env python3
"""
Test to verify research stations are properly distributed in the galaxy
"""

from navigation import Galaxy
from space_stations import space_stations

print("=" * 70)
print(" " * 15 + "RESEARCH STATION DISTRIBUTION TEST")
print("=" * 70)

# Check how many research stations exist in the database
research_stations = []
for name, data in space_stations.items():
    category = data.get('category', '')
    station_type = data.get('type', '')
    if 'Research' in category or 'Lab' in station_type:
        research_stations.append(name)

print(f"\nTotal space stations in database: {len(space_stations)}")
print(f"Research stations in database: {len(research_stations)}")
print("\nResearch Stations:")
for name in research_stations:
    station = space_stations[name]
    print(f"  • {name}")
    print(f"    Category: {station.get('category')}")
    print(f"    Type: {station.get('type')}")
    print(f"    Description: {station.get('description')[:70]}...")
    print()

# Create a galaxy and check distribution
print("-" * 70)
print("GALAXY GENERATION TEST")
print("-" * 70)

galaxy = Galaxy()
print(f"\nGenerated galaxy with {len(galaxy.systems)} systems")

# Count research stations in the galaxy
research_count = 0
research_systems = []

for coords, system in galaxy.systems.items():
    stations = system.get('stations', [])
    for station in stations:
        category = station.get('category', '')
        station_type = station.get('type', '')
        if 'Research' in category or 'Lab' in station_type:
            research_count += 1
            research_systems.append({
                'system': system['name'],
                'station': station.get('name'),
                'coords': coords
            })

print(f"\nResearch stations placed in galaxy: {research_count}")
print(f"Systems with research stations: {len(research_systems)}")

if research_systems:
    print("\nResearch Station Locations:")
    for entry in research_systems:
        print(f"  • {entry['station']}")
        print(f"    System: {entry['system']} at {entry['coords']}")
        print()
else:
    print("\nWARNING: No research stations found in the galaxy!")
    print("This might be due to random distribution. Try running again.")

# Calculate percentage of systems with research access
if len(galaxy.systems) > 0:
    research_coverage = (len(research_systems) / len(galaxy.systems)) * 100
    print(f"\nResearch Coverage: {research_coverage:.1f}% of systems have research stations")
    
    if research_coverage < 10:
        print("⚠️  Low coverage - players may struggle to find research facilities")
    elif research_coverage < 20:
        print("✓ Moderate coverage - reasonable research station distribution")
    else:
        print("✓ Good coverage - research stations are widely available")

print("\n" + "=" * 70)
