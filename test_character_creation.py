#!/usr/bin/env python3
"""
Test script for the new character creation system
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all necessary imports work"""
    try:
        from species import species_database, get_playable_species
        from characters import character_classes, character_backgrounds, create_character_stats
        from factions import factions
        from research import research_categories
        from game import Game
        
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_character_data_structure():
    """Test the new character data structure"""
    try:
        from species import get_playable_species
        from factions import factions
        from research import research_categories
        from characters import character_classes, character_backgrounds
        
        # Test species
        playable_species = get_playable_species()
        print(f"✅ Found {len(playable_species)} playable species: {list(playable_species.keys())}")
        
        # Test factions
        print(f"✅ Found {len(factions)} factions: {list(factions.keys())[:3]}...")
        
        # Test research categories
        print(f"✅ Found {len(research_categories)} research categories: {list(research_categories.keys())[:3]}...")
        
        # Test character classes
        print(f"✅ Found {len(character_classes)} character classes: {list(character_classes.keys())}")
        
        # Test character backgrounds
        print(f"✅ Found {len(character_backgrounds)} character backgrounds: {list(character_backgrounds.keys())}")
        
        return True
    except Exception as e:
        print(f"❌ Character data structure test failed: {e}")
        return False

def test_game_initialization():
    """Test game initialization with new character data"""
    try:
        from game import Game
        from characters import character_classes, character_backgrounds, create_character_stats
        from factions import factions
        from research import research_categories
        
        game = Game()
        
        # Test character data structure
        test_character_data = {
            'name': 'Test Captain',
            'species': 'Terran',
            'background': list(character_backgrounds.keys())[0],
            'faction': list(factions.keys())[0],
            'character_class': list(character_classes.keys())[0],
            'research_paths': list(research_categories.keys())[:2],
            'stats': create_base_character_stats()
        }
        
        result = game.initialize_new_game(test_character_data)
        if result:
            print("✅ Game initialization with new character data successful")
            print(f"   Character: {game.player_name} ({game.character_species})")
            print(f"   Class: {game.character_class}, Background: {game.character_background}")
            print(f"   Faction: {game.character_faction}")
            print(f"   Research Paths: {game.character_research_paths}")
            print(f"   Character Created: {game.character_created}")
        else:
            print("❌ Game initialization failed")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Game initialization test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing new character creation system...")
    print("=" * 50)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test character data
    if not test_character_data_structure():
        all_passed = False
    
    # Test game initialization
    if not test_game_initialization():
        all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("🎉 All tests passed! Character creation system ready.")
    else:
        print("❌ Some tests failed. Please check the issues above.")
    
    return all_passed

if __name__ == "__main__":
    main()