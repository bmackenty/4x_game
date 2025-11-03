#!/usr/bin/env python3
"""
Test script for ship scanning range system
"""

from navigation import Ship, Galaxy
import math

def test_scan_range():
    """Test basic scan range functionality"""
    print("=" * 60)
    print("TESTING SHIP SCANNING SYSTEM")
    print("=" * 60)
    
    # Create a test ship
    ship = Ship("Test Scout", "Scout Ship")
    print(f"\nCreated ship: {ship.name}")
    print(f"Default scan range: {ship.scan_range}")
    
    # Create a galaxy
    galaxy = Galaxy()
    print(f"\nGalaxy created with {len(galaxy.systems)} systems")
    
    # Place ship at a specific location
    ship.coordinates = (50, 50, 25)
    print(f"Ship position: {ship.coordinates}")
    
    # Test scanning
    print("\n" + "-" * 60)
    print("SCANNING FOR NEARBY OBJECTS...")
    print("-" * 60)
    
    scan_results = ship.get_objects_in_scan_range(galaxy)
    
    if scan_results:
        print(f"\nFound {len(scan_results)} objects within scan range ({ship.scan_range} units):")
        
        # Group by object type
        by_type = {}
        for obj_type, obj_data, distance in scan_results:
            if obj_type not in by_type:
                by_type[obj_type] = []
            by_type[obj_type].append((obj_data, distance))
        
        for obj_type, objects in by_type.items():
            print(f"\n{obj_type.upper()}S ({len(objects)}):")
            for obj_data, distance in objects[:5]:  # Show first 5
                if obj_type == 'system':
                    name = obj_data.get('name', 'Unknown')
                    sys_type = obj_data.get('type', 'Unknown')
                    print(f"  - {name} ({sys_type}) - {distance:.1f} units away")
                elif obj_type == 'station':
                    name = obj_data.get('name', 'Station')
                    print(f"  - {name} - {distance:.1f} units away")
                elif obj_type == 'planet':
                    name = obj_data.get('name', 'Planet')
                    subtype = obj_data.get('subtype', 'Unknown')
                    habitable = " [HABITABLE]" if obj_data.get('habitable') else ""
                    print(f"  - {name} ({subtype}){habitable} - {distance:.1f} units away")
                else:
                    name = obj_data.get('name', obj_type)
                    print(f"  - {name} - {distance:.1f} units away")
            
            if len(objects) > 5:
                print(f"  ... and {len(objects) - 5} more")
    else:
        print("\nNo objects detected within scan range.")
        print("Ship may be in deep space away from any systems.")
    
    # Test with scanner upgrade
    print("\n" + "=" * 60)
    print("TESTING SCANNER UPGRADE")
    print("=" * 60)
    
    # Add Scanner Array component
    ship.components['special'] = ['Scanner Array']
    ship.calculate_stats_from_components()
    
    print(f"\nInstalled Scanner Array")
    print(f"New scan range: {ship.scan_range}")
    
    scan_results = ship.get_objects_in_scan_range(galaxy)
    print(f"Now detecting {len(scan_results)} objects (was {len(scan_results)} before)")
    
    # Test with advanced scanner
    print("\n" + "-" * 60)
    print("TESTING ADVANCED SCANNER")
    print("-" * 60)
    
    ship.components['special'] = ['Advanced Scanner Array']
    ship.calculate_stats_from_components()
    
    print(f"\nInstalled Advanced Scanner Array")
    print(f"New scan range: {ship.scan_range}")
    
    scan_results = ship.get_objects_in_scan_range(galaxy)
    print(f"Now detecting {len(scan_results)} objects")
    
    # Test with quantum scanner
    print("\n" + "-" * 60)
    print("TESTING QUANTUM SCANNER")
    print("-" * 60)
    
    ship.components['special'] = ['Quantum Scanner']
    ship.calculate_stats_from_components()
    
    print(f"\nInstalled Quantum Scanner")
    print(f"New scan range: {ship.scan_range}")
    
    scan_results = ship.get_objects_in_scan_range(galaxy)
    print(f"Now detecting {len(scan_results)} objects")
    
    # Show distribution of scanned objects
    if scan_results:
        by_type = {}
        for obj_type, obj_data, distance in scan_results:
            by_type[obj_type] = by_type.get(obj_type, 0) + 1
        
        print("\nScanned object distribution:")
        for obj_type, count in sorted(by_type.items()):
            print(f"  {obj_type}: {count}")
    
    print("\n" + "=" * 60)
    print("SCANNING TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_scan_range()
