#!/usr/bin/env python3
"""
Test script for faction zones in the expanded galaxy
"""

from navigation import Galaxy
from factions import FactionSystem, factions

def test_faction_zones():
    """Test the faction zone system"""
    print("=" * 80)
    print("FACTION ZONE TEST - EXPANDED GALAXY")
    print("=" * 80)
    print()
    
    # Create galaxy
    print("Generating galaxy...")
    galaxy = Galaxy()
    
    print(f"✓ Galaxy size: {galaxy.size_x} x {galaxy.size_y} x {galaxy.size_z}")
    print(f"✓ Total systems: {len(galaxy.systems)}")
    print()
    
    # Display faction zones
    print("=" * 80)
    print("FACTION ZONES")
    print("=" * 80)
    print()
    
    for faction_name, zone_data in galaxy.faction_zones.items():
        center = zone_data['center']
        radius = zone_data['radius']
        systems_count = len(zone_data['systems'])
        
        print(f"📍 {faction_name}")
        print(f"   Center: ({center[0]}, {center[1]}, {center[2]})")
        print(f"   Radius: {radius}")
        print(f"   Systems: {systems_count}")
        
        # Show faction focus
        faction_data = factions.get(faction_name, {})
        focus = faction_data.get('primary_focus', 'Unknown')
        philosophy = faction_data.get('philosophy', 'Unknown')
        print(f"   Focus: {focus} | Philosophy: {philosophy}")
        print()
    
    # Analyze system distribution
    print("=" * 80)
    print("SYSTEM DISTRIBUTION BY FACTION")
    print("=" * 80)
    print()
    
    faction_system_counts = {}
    neutral_count = 0
    
    for system in galaxy.systems.values():
        faction = system.get('controlling_faction')
        if faction:
            faction_system_counts[faction] = faction_system_counts.get(faction, 0) + 1
        else:
            neutral_count += 1
    
    print(f"Neutral/Unclaimed Space: {neutral_count} systems")
    print()
    
    for faction_name, count in sorted(faction_system_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(galaxy.systems)) * 100
        bar = "█" * int(percentage)
        print(f"{faction_name:30s}: {count:3d} systems ({percentage:5.1f}%) {bar}")
    
    print()
    
    # Show sample faction-controlled systems
    print("=" * 80)
    print("SAMPLE FACTION-CONTROLLED SYSTEMS")
    print("=" * 80)
    print()
    
    shown = 0
    for system in galaxy.systems.values():
        faction = system.get('controlling_faction')
        if faction and shown < 5:
            print(f"🌟 {system['name']}")
            print(f"   Type: {system['type']}")
            print(f"   Faction: {faction}")
            print(f"   Stations: {len(system['stations'])}")
            
            # Show station factions
            for station in system['stations']:
                station_faction = station.get('controlling_faction', 'None')
                print(f"      • {station['name']} (Faction: {station_faction})")
            
            # Show habitable planets with faction control
            for body in system['celestial_bodies']:
                if body.get('object_type') == 'Planet' and body.get('habitable'):
                    planet_faction = body.get('controlling_faction', 'None')
                    print(f"      🌍 {body['name']} - Habitable (Faction: {planet_faction})")
            
            print()
            shown += 1
    
    # Test faction benefits
    print("=" * 80)
    print("FACTION BENEFIT EXAMPLES")
    print("=" * 80)
    print()
    
    faction_system = FactionSystem()
    
    # Test with different reputation levels
    test_faction = list(galaxy.faction_zones.keys())[0] if galaxy.faction_zones else None
    
    if test_faction:
        print(f"Testing benefits for: {test_faction}")
        print()
        
        # Set different reputation levels
        for rep_level, rep_name in [(0, "Neutral"), (30, "Cordial"), (60, "Friendly"), (80, "Allied")]:
            faction_system.player_relations[test_faction] = rep_level
            benefits = faction_system.get_faction_zone_benefits(test_faction, 'station')
            
            print(f"--- {rep_name} (Reputation: {rep_level}) ---")
            print(f"Trade Discount: {benefits['trade_discount']}%")
            print(f"Repair Discount: {benefits['repair_discount']}%")
            print(f"Refuel Discount: {benefits['refuel_discount']}%")
            print(f"Shipyard Discount: {benefits['shipyard_discount']}%")
            print(f"Research Bonus: {benefits['research_bonus']}%")
            print("Benefits:")
            for desc in benefits['description']:
                print(f"  • {desc}")
            print()
    
    # Distance analysis
    print("=" * 80)
    print("GALAXY SIZE ANALYSIS")
    print("=" * 80)
    print()
    
    # Find max distance between any two systems
    max_distance = 0
    max_pair = (None, None)
    
    systems_list = list(galaxy.systems.values())
    for i, sys1 in enumerate(systems_list[:50]):  # Sample for speed
        for sys2 in systems_list[i+1:i+51]:
            x1, y1, z1 = sys1['coordinates']
            x2, y2, z2 = sys2['coordinates']
            distance = ((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2) ** 0.5
            
            if distance > max_distance:
                max_distance = distance
                max_pair = (sys1['name'], sys2['name'])
    
    print(f"Maximum sampled distance: {max_distance:.1f} units")
    print(f"Between: {max_pair[0]} and {max_pair[1]}")
    print()
    print(f"Galaxy volume: {galaxy.size_x * galaxy.size_y * galaxy.size_z:,} cubic units")
    print(f"System density: {len(galaxy.systems) / (galaxy.size_x * galaxy.size_y * galaxy.size_z):.8f} systems/unit³")
    
    print()
    print("=" * 80)
    print("FACTION ZONE TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_faction_zones()
