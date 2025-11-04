#!/usr/bin/env python3
"""
Quick test to verify NPC encounter detection
"""

from navigation import NavigationSystem, Ship
from game import Game
import math

print("=" * 70)
print(" " * 15 + "NPC ENCOUNTER DETECTION TEST")
print("=" * 70)

# Create game and navigation
game = Game()
nav = game.navigation

print(f"\nNPCs in galaxy: {len(nav.npc_ships)}")

if nav.npc_ships:
    # Get first NPC
    npc = nav.npc_ships[0]
    print(f"\nTest NPC: {npc.name}")
    print(f"Position: {npc.coordinates}")
    
    # Test various distances
    x, y, z = npc.coordinates
    
    test_positions = [
        ((x, y, z), "Exact position"),
        ((x+1, y, z), "1 unit away"),
        ((x+2, y, z), "2 units away"),
        ((x+3, y, z), "3 units away"),
        ((x+4, y, z), "4 units away"),
        ((x+5, y, z), "5 units away"),
        ((x+6, y, z), "6 units away"),
    ]
    
    print("\nDetection tests:")
    print("-" * 70)
    
    for pos, desc in test_positions:
        detected = nav.get_npc_at_location(pos)
        distance = math.sqrt((pos[0]-x)**2 + (pos[1]-y)**2 + (pos[2]-z)**2)
        status = "✓ DETECTED" if detected else "✗ Not detected"
        print(f"{desc:20} | Distance: {distance:.1f} | {status}")
    
    print("\n" + "=" * 70)
    print("Detection range is 5.0 units")
    print("NPCs should be detected within this range")
else:
    print("\nNo NPCs spawned!")

print("=" * 70)
