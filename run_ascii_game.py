#!/usr/bin/env python3
"""
ASCII 4X Game Launcher
Simple launcher for the ASCII-based 4X Galactic Empire Management Game
"""

import sys
import os

def main():
    """Launch the ASCII-based 4X game"""
    print("Starting 4X Galactic Empire Management Game...")
    print("ASCII Interface Version")
    print("-" * 50)
    
    try:
        # Import and run the game interface
        from game_interface import GameInterface
        
        game = GameInterface()
        game.run()
        
    except ImportError as e:
        print(f"Error importing game modules: {e}")
        print("Make sure all game files are in the same directory.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nGame interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
