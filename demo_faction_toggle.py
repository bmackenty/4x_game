#!/usr/bin/env python3
"""
Demo script showing the faction zone toggle feature
"""

from navigation import Galaxy

def demo_faction_toggle():
    """Demonstrate the faction zone visualization toggle feature"""
    print("=" * 80)
    print("FACTION ZONE TOGGLE FEATURE DEMO")
    print("=" * 80)
    print()
    
    print("📍 NEW FEATURE: Press 'f' on the galaxy map to toggle faction zone visualization")
    print()
    
    # Create a galaxy to show faction zones
    print("Generating galaxy with faction zones...")
    galaxy = Galaxy()
    
    print(f"✓ Galaxy created: {galaxy.size_x} x {galaxy.size_y} x {galaxy.size_z}")
    print(f"✓ Total systems: {len(galaxy.systems)}")
    print(f"✓ Faction zones: {len(galaxy.faction_zones)}")
    print()
    
    print("=" * 80)
    print("HOW IT WORKS")
    print("=" * 80)
    print()
    
    print("When you press 'f' on the map screen:")
    print()
    print("FACTION MODE OFF (Default View):")
    print("  • Normal colored systems (* = visited, + = unvisited)")
    print("  • Stations shown as ◈ (visited) or ◆ (unvisited)")
    print("  • Clean, minimal display")
    print()
    
    print("FACTION MODE ON (Toggle with 'f'):")
    print("  • ░ characters show faction-controlled space")
    print("  • Each faction zone has a unique color background")
    print("  • Systems in faction space shown with faction color backgrounds")
    print("  • Current zone name displayed in HUD")
    print("  • Header changes to 'GALAXY MAP - FACTION ZONES'")
    print()
    
    print("=" * 80)
    print("VISUAL FEATURES")
    print("=" * 80)
    print()
    
    print("Color-coded faction zones:")
    for idx, (faction_name, zone_data) in enumerate(list(galaxy.faction_zones.items())[:5]):
        colors = ["blue", "red", "green", "magenta", "cyan", 
                 "yellow", "bright_blue", "bright_red", "bright_green",
                 "bright_magenta", "bright_cyan"]
        color = colors[idx % len(colors)]
        center = zone_data['center']
        radius = zone_data['radius']
        systems_count = len(zone_data['systems'])
        
        print(f"  [{color.upper():15s}] {faction_name}")
        print(f"    • Center: ({center[0]}, {center[1]}, {center[2]})")
        print(f"    • Radius: {radius} units")
        print(f"    • Systems: {systems_count}")
    
    if len(galaxy.faction_zones) > 5:
        print(f"  ... and {len(galaxy.faction_zones) - 5} more faction zones")
    
    print()
    print("=" * 80)
    print("GAMEPLAY BENEFITS")
    print("=" * 80)
    print()
    
    print("✓ Easily identify faction-controlled territory")
    print("✓ Plan routes through friendly faction space for benefits")
    print("✓ Avoid hostile faction zones")
    print("✓ Locate faction research stations and trade hubs quickly")
    print("✓ See your current faction zone in the HUD")
    print("✓ Visual representation of faction influence across the galaxy")
    print()
    
    print("=" * 80)
    print("CONTROLS")
    print("=" * 80)
    print()
    
    print("Map Screen Keybindings:")
    print("  f        - Toggle faction zone visualization ON/OFF")
    print("  n        - Open galactic news feed")
    print("  q/ESC    - Return to main screen")
    print("  hjkl     - Move ship (vim-style)")
    print("  arrows   - Move ship (arrow keys)")
    print()
    
    print("=" * 80)
    print("IMPLEMENTATION DETAILS")
    print("=" * 80)
    print()
    
    print("Backend Changes:")
    print("  • MapScreen.show_faction_zones toggle flag")
    print("  • MapScreen.action_toggle_factions() method")
    print("  • Virtual buffer stores (char, data, faction) tuples")
    print("  • Faction zone background rendering with ░ character")
    print("  • Dynamic faction color assignment")
    print("  • Current zone display in HUD when toggle is ON")
    print()
    
    print("Visual Elements:")
    print("  • 11 distinct faction colors for zone identification")
    print("  • Systems in faction space get colored backgrounds")
    print("  • ░ (light shade) fills faction-controlled areas")
    print("  • Header updates to show 'FACTION ZONES' mode")
    print("  • Legend updates to explain faction visualization")
    print()
    
    # Show faction zone coverage
    print("=" * 80)
    print("FACTION ZONE COVERAGE")
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
    
    total = len(galaxy.systems)
    faction_total = total - neutral_count
    
    print(f"Total Systems: {total}")
    print(f"Faction-Controlled: {faction_total} ({(faction_total/total)*100:.1f}%)")
    print(f"Neutral Space: {neutral_count} ({(neutral_count/total)*100:.1f}%)")
    print()
    
    print("Top 5 Faction Zones by System Count:")
    for idx, (faction_name, count) in enumerate(sorted(faction_system_counts.items(), 
                                                        key=lambda x: x[1], reverse=True)[:5], 1):
        percentage = (count / total) * 100
        bar = "█" * int(percentage * 2)
        print(f"  {idx}. {faction_name:30s}: {count:3d} systems ({percentage:5.1f}%) {bar}")
    
    print()
    print("=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)
    print()
    print("The faction zone toggle is ready to use!")
    print("Start the game with: python3 nethack_interface.py")
    print("Then press 'f' on the map screen to toggle faction visualization.")
    print()

if __name__ == "__main__":
    demo_faction_toggle()
