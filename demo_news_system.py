#!/usr/bin/env python3
"""
Demo of the Galactic News System
Shows how events are generated and displayed
"""

from game import Game
from events import EventType

def demo_news_system():
    """Demonstrate the galactic news feed"""
    print("╔" + "═" * 78 + "╗")
    print("║" + "GALACTIC NEWS NETWORK - SYSTEM DEMO".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    # Create a game instance
    game = Game()
    
    print("📡 Initializing Event System...")
    print(f"✓ Event system active")
    print(f"✓ Initial events generated: {len(game.event_system.get_active_events())}")
    print()
    
    # Display initial news
    print("╔" + "═" * 78 + "╗")
    print("║" + "BREAKING NEWS - INITIAL HEADLINES".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    news_feed = game.event_system.get_news_feed(limit=10)
    
    for i, item in enumerate(news_feed, 1):
        # Color indicators for different event types
        type_symbols = {
            'economic': '💰',
            'political': '⚖️ ',
            'scientific': '🔬',
            'military': '⚔️ ',
            'natural': '🌊',
            'social': '👥',
            'travel': '🚀',
            'scandal': '💥',
            'tabloid': '📰'
        }
        
        event_type = item.get('type', 'system')
        symbol = type_symbols.get(event_type, '📋')
        severity = item.get('severity', 1)
        
        # Severity indicator
        urgency = "!" * min(severity, 5)
        
        print(f"{symbol} [{urgency:5}] {item.get('headline', 'Unknown Event')}")
        print(f"   Type: {event_type.upper()}")
        print(f"   {item.get('description', 'No description')}")
        
        affected = item.get('affected_systems', [])
        if affected:
            systems_str = ", ".join(affected[:3])
            if len(affected) > 3:
                systems_str += f" (+{len(affected) - 3} more)"
            print(f"   📍 Affected: {systems_str}")
        print()
    
    # Simulate turns to show event updates
    print("╔" + "═" * 78 + "╗")
    print("║" + "SIMULATING GALACTIC TIME PASSAGE".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    print("⏰ Advancing time and generating new events...\n")
    
    for turn in range(1, 11):
        print(f"Turn {turn:2d}: ", end="")
        
        # Update events
        old_count = len(game.event_system.get_news_feed())
        game.event_system.update_events()
        new_count = len(game.event_system.get_news_feed())
        
        active = len(game.event_system.get_active_events())
        
        print(f"Active Events: {active:2d} | Total News: {new_count:2d}", end="")
        
        # Check if new event was generated
        if new_count > old_count:
            latest = game.event_system.get_news_feed(limit=1)
            if latest:
                print(f" | 🆕 {latest[-1].get('headline', 'Unknown')}")
        else:
            print()
    
    # Show event type distribution
    print("\n╔" + "═" * 78 + "╗")
    print("║" + "EVENT TYPE DISTRIBUTION".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    all_news = game.event_system.get_news_feed(limit=50)
    type_counts = {}
    for item in all_news:
        event_type = item.get('type', 'unknown')
        type_counts[event_type] = type_counts.get(event_type, 0) + 1
    
    for event_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * count
        print(f"{event_type.upper():12s}: {bar} ({count})")
    
    # Show severity distribution
    print("\n╔" + "═" * 78 + "╗")
    print("║" + "SEVERITY ANALYSIS".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    severity_counts = [0] * 11  # 0-10 severity
    for item in all_news:
        severity = item.get('severity', 1)
        severity_counts[severity] += 1
    
    for sev, count in enumerate(severity_counts):
        if count > 0:
            bar = "█" * count
            label = "Low" if sev < 4 else "Medium" if sev < 7 else "High"
            print(f"Severity {sev:2d} ({label:6s}): {bar} ({count})")
    
    print("\n" + "═" * 80)
    print("📺 News System Demo Complete!")
    print("═" * 80)
    print("\n💡 In the game:")
    print("   • Press 'n' to open the Galactic News Network")
    print("   • Events update automatically every 3 turns/moves")
    print("   • News displays recent galactic events with severity and type")
    print("   • Use j/k to scroll through news items")
    print()

if __name__ == "__main__":
    demo_news_system()
