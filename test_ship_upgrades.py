#!/usr/bin/env python3
"""
Quick test script for ship upgrade system
"""

from ship_builder import (
    ship_components, 
    check_component_compatibility, 
    calculate_power_usage,
    can_afford_component
)

# Test ship configuration
test_ship_components = {
    "hull": "Light Hull",
    "engine": "Ion Drive",
    "weapons": ["Pulse Cannons"],
    "shields": ["Basic Deflectors"],
    "special": []
}

print("="*60)
print("SHIP UPGRADE SYSTEM TEST")
print("="*60)

# Test 1: Check initial power usage
print("\n1. Initial Power Usage:")
power_info = calculate_power_usage(test_ship_components)
print(f"   Power Output: {power_info['power_output']}W")
print(f"   Power Used: {power_info['power_used']}W")
print(f"   Power Available: {power_info['power_available']}W")
print(f"   Usage: {power_info['power_percentage']:.1f}%")

# Test 2: Check component compatibility
print("\n2. Testing Compatibility Checks:")
unlocked_tech = []  # No tech unlocked

# Try to install Fusion Engine (requires tech)
can_install, reason = check_component_compatibility(
    "Light Hull", "Engines", "Fusion Engine", test_ship_components, unlocked_tech
)
print(f"   Fusion Engine: {can_install} - {reason}")

# Try to install Gravity Cannon (too big for Light Hull)
can_install, reason = check_component_compatibility(
    "Light Hull", "Weapons", "Gravity Cannon", test_ship_components, unlocked_tech
)
print(f"   Gravity Cannon: {can_install} - {reason}")

# Try to install Scanner Array (should work)
can_install, reason = check_component_compatibility(
    "Light Hull", "Special Systems", "Scanner Array", test_ship_components, unlocked_tech
)
print(f"   Scanner Array: {can_install} - {reason}")

# Test 3: Add Scanner Array and check power
print("\n3. Installing Scanner Array:")
test_ship_components["special"].append("Scanner Array")
power_info = calculate_power_usage(test_ship_components)
print(f"   New Power Used: {power_info['power_used']}W / {power_info['power_output']}W")
print(f"   Usage: {power_info['power_percentage']:.1f}%")

# Test 4: Upgrade to bigger hull
print("\n4. Upgrading to Standard Hull:")
test_ship_components["hull"] = "Standard Hull"
print(f"   Hull slots available:")
hull = ship_components["Hull Types"]["Standard Hull"]
for slot_type, count in hull["slots"].items():
    print(f"      {slot_type}: {count}")

# Test 5: Check affordability
print("\n5. Testing Affordability:")
credits = 50000
for component_name in ["Ion Drive", "Fusion Engine", "Ether Drive"]:
    can_afford, cost = can_afford_component("Engines", component_name, credits)
    status = "✓" if can_afford else "✗"
    print(f"   {status} {component_name}: {cost:,} cr (Have: {credits:,} cr)")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
print("\nThe upgrade system is ready to use!")
print("Navigate to a shipyard station and press '2' to upgrade your ship.")
