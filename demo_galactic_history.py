#!/usr/bin/env python3
"""
Demo script for Galactic History feature
Shows the generated history without needing UI modules
"""

from galactic_history import generate_epoch_history

def display_history():
    """Display the galactic history in terminal"""
    print("=" * 120)
    print("GALACTIC HISTORY - DEMO MODE".center(120))
    print("The Ages of the Known Galaxy".center(120))
    print("=" * 120)
    print()
    
    history = generate_epoch_history()
    
    for epoch in history:
        print("═" * 120)
        print(f"  {epoch['name']}")
        print(f"  Years {epoch['start_year']:,} – {epoch['end_year']:,} (Duration: {epoch['end_year'] - epoch['start_year']:,} years)")
        print("─" * 120)
        print(f"  Themes: {', '.join(epoch['themes'])}")
        print()
        
        # Cataclysms
        if epoch.get('cataclysms'):
            print("  ⚠ Major Cataclysms:")
            for cataclysm in epoch['cataclysms']:
                print(f"    • {cataclysm}")
            print()
        
        # Faction Formations
        if epoch.get('faction_formations'):
            print("  🏛️  Faction Formations:")
            for faction in epoch['faction_formations']:
                print(f"    • Year {faction['year']:,}: {faction['name']}")
                print(f"      {faction['event']}")
            print()
        
        # Mysteries
        if epoch.get('mysteries'):
            print("  ✦ Mysteries of This Age:")
            for mystery in epoch['mysteries']:
                print(f"    • {mystery}")
            print()
        
        # Civilizations
        print("  Civilizations of This Epoch:")
        print()
        
        for civ in epoch['civilizations']:
            print(f"  ┌─ {civ['name']}")
            print(f"  │  Type: {civ['type']}")
            print(f"  │  Traits: {', '.join(civ['traits'])}")
            print(f"  │  Founded: Year {civ['founded']:,} | Collapsed: Year {civ['collapsed']:,}")
            print(f"  │  Duration: {civ['collapsed'] - civ['founded']:,} years")
            print(f"  │")
            print(f"  │  Remnants:")
            print(f"  │    {civ['remnants']}")
            
            if civ.get('notable_events'):
                print(f"  │")
                print(f"  │  Notable Events:")
                for event in civ['notable_events']:
                    print(f"  │    • {event}")
            
            print(f"  └{'─' * 118}")
            print()
        
        print()
    
    print("=" * 120)
    print("GALACTIC HISTORY COMPLETE")
    print("=" * 120)
    print()
    print("This history is procedurally generated and will be different each time!")
    print("In the game, press 'H' during character creation to view this history.")
    print()

if __name__ == "__main__":
    display_history()
