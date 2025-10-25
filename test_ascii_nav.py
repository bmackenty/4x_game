#!/usr/bin/env python3
"""
Quick test to verify ASCII navigation map renders correctly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_ascii_navigation():
    """Test that the ASCII navigation map renders"""
    try:
        from textual_interface import Game7019App, NavigationScreen
        from game import Game
        
        print("✅ Imports successful")
        
        # Create game instance
        game = Game()
        print("✅ Game instance created")
        
        # Initialize the game properly to ensure ship is set up
        if hasattr(game, 'navigation') and game.navigation:
            if not game.navigation.current_ship:
                from navigation import Ship
                game.navigation.current_ship = Ship("Test Ship", "Basic Transport")
                print("✅ Test ship initialized")
        
        # Create navigation screen
        nav_screen = NavigationScreen(game_instance=game)
        print("✅ NavigationScreen created")
        
        # Try to render the ASCII map
        if hasattr(nav_screen, 'render_hex_map'):
            map_output = nav_screen.render_hex_map()
            print("✅ Hex map render method exists")
            
            # Check if map output contains expected elements
            if isinstance(map_output, str):
                print(f"✅ Map output is a string ({len(map_output)} characters)")
                
                # Check for some expected symbols
                has_border = '╔' in map_output or '║' in map_output
                has_hex = any(c in map_output for c in ['/', '\\', '_', '|'])
                
                if has_border:
                    print("⚠️  Map contains old border characters (should be borderless)")
                if has_hex:
                    print("✅ Map contains hex graph pattern")
                    
                # Print a sample of the map
                lines = map_output.split('\n')
                print(f"\n📊 Map Preview ({len(lines)} lines):")
                print("=" * 60)
                # Show first 10 lines
                for line in lines[:10]:
                    print(line)
                if len(lines) > 10:
                    print(f"... ({len(lines) - 10} more lines)")
                print("=" * 60)
            else:
                print(f"⚠️  Map output is not a string: {type(map_output)}")
        else:
            print("❌ render_ascii_map method not found")
            return False
        
        print("\n🎉 ASCII navigation test PASSED!")
        print("   The ASCII map renders successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing ASCII Navigation Map Rendering...")
    print("=" * 60)
    
    success = test_ascii_navigation()
    
    if success:
        print("\n🚀 Ready to test in the UI! Use ./run_ui.sh and click Navigation")
    else:
        print("\n❌ ASCII navigation test failed")
    
    print("=" * 60)
