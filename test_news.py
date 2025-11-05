#!/usr/bin/env python3
"""
Test script for the galactic news system
"""

from game import Game

def test_news_system():
    """Test the event and news system"""
    print("Testing Galactic News System")
    print("=" * 60)
    
    # Create a game instance
    game = Game()
    
    # Check if event system exists
    if hasattr(game, 'event_system'):
        print("✓ Event system initialized")
        
        # Get active events
        active_events = game.event_system.get_active_events()
        print(f"✓ Active events: {len(active_events)}")
        
        # Get news feed
        news_feed = game.event_system.get_news_feed(limit=10)
        print(f"✓ News items in feed: {len(news_feed)}")
        
        # Display some news
        print("\n" + "=" * 60)
        print("RECENT NEWS HEADLINES:")
        print("=" * 60)
        
        for i, item in enumerate(news_feed[:5], 1):
            print(f"\n{i}. {item.get('headline', 'Unknown')}")
            print(f"   Type: {item.get('type', 'unknown').upper()}")
            print(f"   {item.get('description', 'No description')}")
            
            affected = item.get('affected_systems', [])
            if affected:
                systems_str = ", ".join(affected[:3])
                if len(affected) > 3:
                    systems_str += f" (+{len(affected) - 3} more)"
                print(f"   Affected systems: {systems_str}")
        
        # Trigger event updates
        print("\n" + "=" * 60)
        print("Updating events (simulating turns)...")
        print("=" * 60)
        
        for turn in range(1, 6):
            print(f"\nTurn {turn}:")
            game.event_system.update_events()
            new_active = len(game.event_system.get_active_events())
            new_news = len(game.event_system.get_news_feed())
            print(f"  Active events: {new_active}")
            print(f"  Total news items: {new_news}")
            
            # Show latest headline if news count increased
            latest_news = game.event_system.get_news_feed(limit=1)
            if latest_news:
                print(f"  Latest: {latest_news[-1].get('headline', 'Unknown')}")
        
        print("\n" + "=" * 60)
        print("News system test complete!")
        print("=" * 60)
    else:
        print("✗ Event system not found!")
        return False
    
    return True

if __name__ == "__main__":
    test_news_system()
