#!/usr/bin/env python3
"""
Test script for NPC ship system
"""

from navigation import NavigationSystem, NPCShip
from game import Game

def test_npc_ships():
    print("=" * 70)
    print(" " * 20 + "NPC SHIP SYSTEM TEST")
    print("=" * 70)
    
    # Create a game instance
    game = Game()
    
    # Navigation system should auto-spawn NPCs
    nav = game.navigation
    
    print(f"\nGalaxy created with {len(nav.galaxy.systems)} systems")
    print(f"NPC ships spawned: {len(nav.npc_ships)}")
    
    if nav.npc_ships:
        print("\n" + "─" * 70)
        print("NPC SHIP ROSTER:")
        print("─" * 70)
        
        for i, npc in enumerate(nav.npc_ships, 1):
            x, y, z = npc.coordinates
            print(f"\n{i}. {npc.name}")
            print(f"   Ship Class: {npc.ship_class}")
            print(f"   Personality: {npc.personality}")
            print(f"   Position: ({x}, {y}, {z})")
            print(f"   Credits: {npc.credits:,}")
            print(f"   Trade Goods: {', '.join(list(npc.trade_goods.keys())[:3])}...")
            print(f"   Greeting: \"{npc.get_greeting()}\"")
    
    # Test NPC movement
    print("\n" + "=" * 70)
    print("TESTING NPC MOVEMENT (10 steps)")
    print("=" * 70)
    
    if nav.npc_ships:
        test_npc = nav.npc_ships[0]
        print(f"\nTracking: {test_npc.name}")
        print(f"Starting position: {test_npc.coordinates}")
        
        for step in range(10):
            old_pos = test_npc.coordinates
            test_npc.move()
            new_pos = test_npc.coordinates
            
            if old_pos != new_pos:
                print(f"  Step {step+1}: {old_pos} → {new_pos}")
            else:
                print(f"  Step {step+1}: (no movement)")
        
        print(f"Final position: {test_npc.coordinates}")
    
    # Test rumor generation
    print("\n" + "=" * 70)
    print("TESTING RUMOR GENERATION")
    print("=" * 70)
    
    if nav.npc_ships:
        test_npc = nav.npc_ships[0]
        print(f"\n{test_npc.name} shares rumors:\n")
        
        for i in range(5):
            rumor = test_npc.generate_rumor()
            print(f"{i+1}. {rumor}")
    
    # Test encounter detection
    print("\n" + "=" * 70)
    print("TESTING ENCOUNTER DETECTION")
    print("=" * 70)
    
    if nav.npc_ships:
        # Place player ship near an NPC
        test_npc = nav.npc_ships[0]
        test_coords = test_npc.coordinates
        
        print(f"\nNPC at: {test_coords}")
        print(f"Testing detection at various distances:")
        
        # Test exact position
        npc = nav.get_npc_at_location(test_coords)
        print(f"  Same position: {'DETECTED' if npc else 'Not detected'}")
        
        # Test 1 unit away
        x, y, z = test_coords
        npc = nav.get_npc_at_location((x+1, y, z))
        print(f"  1 unit away: {'DETECTED' if npc else 'Not detected'}")
        
        # Test 2 units away
        npc = nav.get_npc_at_location((x+2, y, z))
        print(f"  2 units away: {'DETECTED' if npc else 'Not detected'}")
        
        # Test 5 units away
        npc = nav.get_npc_at_location((x+5, y, z))
        print(f"  5 units away: {'DETECTED' if npc else 'Not detected'}")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print("\nNPC ships will appear as '&' on the galaxy map.")
    print("Move into them to trigger encounters and trade!")

if __name__ == "__main__":
    test_npc_ships()
