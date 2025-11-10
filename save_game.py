"""
Game Save/Load System

Handles saving and loading game state including:
- Character data (stats, species, background, faction, etc.)
- Ship data (current ship, owned ships, custom ships)
- Game state (credits, inventory, stations, platforms)
- Navigation state (galaxy, current position)
- Faction relationships
- Events and news
- Research progress
- Turn information
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional, List, Any
from pathlib import Path


SAVE_DIR = Path("saves")
SAVE_DIR.mkdir(exist_ok=True)

# Debug log file
DEBUG_LOG = Path("save_debug.log")

def _debug_log(message: str):
    """Write debug message to log file"""
    try:
        with open(DEBUG_LOG, 'a') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
            f.flush()
    except Exception:
        pass  # Don't fail if we can't write debug log


def get_save_files() -> List[Dict[str, Any]]:
    """Get list of all save files with metadata"""
    saves = []
    if not SAVE_DIR.exists():
        return saves
    
    for save_file in SAVE_DIR.glob("*.json"):
        try:
            with open(save_file, 'r') as f:
                data = json.load(f)
                saves.append({
                    'filename': save_file.name,
                    'path': str(save_file),
                    'name': data.get('save_name', save_file.stem),
                    'timestamp': data.get('timestamp', ''),
                    'player_name': data.get('player_name', 'Unknown'),
                    'character_class': data.get('character_class', 'Unknown'),
                    'credits': data.get('credits', 0),
                    'turn': data.get('current_turn', 0),
                })
        except Exception:
            continue
    
    # Sort by timestamp (newest first)
    saves.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return saves


def save_game(game, save_name: Optional[str] = None) -> bool:
    """
    Save game state to a JSON file
    
    Args:
        game: Game instance to save
        save_name: Optional custom save name (defaults to timestamp-based name)
    
    Returns:
        True if save successful, False otherwise
    """
    _debug_log("save_game called")
    try:
        # Ensure save directory exists
        SAVE_DIR.mkdir(exist_ok=True)
        _debug_log(f"Save directory: {SAVE_DIR.absolute()}")
        
        # Generate save filename
        if save_name:
            # Sanitize save name for filename
            safe_name = "".join(c for c in save_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_')
            filename = f"{safe_name}.json"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"save_{timestamp}.json"
        
        save_path = SAVE_DIR / filename
        _debug_log(f"Attempting to save to: {save_path}")
        print(f"[SAVE] Attempting to save to: {save_path}")
        
        # Collect all game state
        save_data = {
            'version': '1.0',
            'timestamp': datetime.now().isoformat(),
            'save_name': save_name or f"Save {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            
            # Character data
            'player_name': getattr(game, 'player_name', ''),
            'character_class': getattr(game, 'character_class', ''),
            'character_background': getattr(game, 'character_background', ''),
            'character_species': getattr(game, 'character_species', ''),
            'character_faction': getattr(game, 'character_faction', ''),
            'character_research_paths': getattr(game, 'character_research_paths', []),
            'character_stats': getattr(game, 'character_stats', {}),
            'character_created': getattr(game, 'character_created', False),
            
            # Game state
            'credits': getattr(game, 'credits', 10000),
            'inventory': getattr(game, 'inventory', {}),
            'completed_research': getattr(game, 'completed_research', []),
            'active_research': getattr(game, 'active_research', None),
            'research_progress': getattr(game, 'research_progress', 0),
            
            # Turn system
            'current_turn': getattr(game, 'current_turn', 1),
            'max_turns': getattr(game, 'max_turns', 100),
            'turn_actions_remaining': getattr(game, 'turn_actions_remaining', 3),
            'max_actions_per_turn': getattr(game, 'max_actions_per_turn', 3),
            'game_ended': getattr(game, 'game_ended', False),
            
            # Ships
            'owned_ships': getattr(game, 'owned_ships', []),
            'custom_ships': getattr(game, 'custom_ships', []),
            
            # Current ship state (if exists)
            'current_ship_state': _save_current_ship(getattr(game, 'navigation', None)),
            
            # Stations and platforms
            'owned_stations': getattr(game, 'owned_stations', []),
            'owned_platforms': getattr(game, 'owned_platforms', []),
            
            # Navigation state
            'navigation_state': _save_navigation(getattr(game, 'navigation', None)),
            
            # Faction system
            'faction_state': _save_factions(getattr(game, 'faction_system', None)),
            
            # Events and news
            'event_state': _save_events(getattr(game, 'event_system', None)),
            'news_state': _save_news(getattr(game, 'news_system', None)),
            
            # Galactic history
            'galactic_history_state': _save_galactic_history(getattr(game, 'galactic_history', None)),
            
            # Economy state
            'economy_state': _save_economy(getattr(game, 'economy', None)),
            
            # Station manager state
            'station_manager_state': _save_station_manager(getattr(game, 'station_manager', None)),
            
            # Bot manager state
            'bot_manager_state': _save_bot_manager(getattr(game, 'bot_manager', None)),
            
            # Player log
            'player_log': getattr(game, 'player_log', [])[-getattr(game, 'max_log_entries', 100):],
        }
        
        _debug_log(f"Collected save data, writing to file...")
        print(f"[SAVE] Collected save data, writing to file...")
        
        # Write to file
        with open(save_path, 'w') as f:
            json.dump(save_data, f, indent=2, default=str)
        
        _debug_log(f"Successfully saved to: {save_path}")
        print(f"[SAVE] Successfully saved to: {save_path}")
        
        # Verify file was written
        if save_path.exists():
            file_size = save_path.stat().st_size
            _debug_log(f"File exists, size: {file_size} bytes")
            return True
        else:
            _debug_log("ERROR: File was not created!")
            return False
        
    except Exception as e:
        error_msg = f"Error saving game: {e}"
        _debug_log(error_msg)
        print(f"[SAVE ERROR] {error_msg}")
        import traceback
        traceback.print_exc()
        _debug_log(traceback.format_exc())
        return False


def load_game(game, save_path: str) -> bool:
    """
    Load game state from a JSON file
    
    Args:
        game: Game instance to load into
        save_path: Path to save file
    
    Returns:
        True if load successful, False otherwise
    """
    try:
        with open(save_path, 'r') as f:
            save_data = json.load(f)
        
        # Load character data
        game.player_name = save_data.get('player_name', '')
        game.character_class = save_data.get('character_class', '')
        game.character_background = save_data.get('character_background', '')
        game.character_species = save_data.get('character_species', '')
        game.character_faction = save_data.get('character_faction', '')
        game.character_research_paths = save_data.get('character_research_paths', [])
        game.character_stats = save_data.get('character_stats', {})
        game.character_created = save_data.get('character_created', False)
        
        # Load game state
        game.credits = save_data.get('credits', 10000)
        game.inventory = save_data.get('inventory', {})
        game.completed_research = save_data.get('completed_research', [])
        game.active_research = save_data.get('active_research', None)
        game.research_progress = save_data.get('research_progress', 0)
        
        # Load turn system
        game.current_turn = save_data.get('current_turn', 1)
        game.max_turns = save_data.get('max_turns', 100)
        game.turn_actions_remaining = save_data.get('turn_actions_remaining', 3)
        game.max_actions_per_turn = save_data.get('max_actions_per_turn', 3)
        game.game_ended = save_data.get('game_ended', False)
        
        # Load ships
        game.owned_ships = save_data.get('owned_ships', [])
        game.custom_ships = save_data.get('custom_ships', [])
        
        # Load stations and platforms
        game.owned_stations = save_data.get('owned_stations', [])
        game.owned_platforms = save_data.get('owned_platforms', [])
        
        # Load navigation state
        if 'navigation_state' in save_data and game.navigation:
            _load_navigation(game.navigation, save_data['navigation_state'])
        
        # Load current ship state (must be after navigation is initialized)
        if 'current_ship_state' in save_data and save_data.get('current_ship_state') and game.navigation:
            _load_current_ship(game.navigation, save_data['current_ship_state'])
        elif game.navigation and game.owned_ships:
            # If no saved ship but we have owned ships, select the first one
            try:
                from navigation import Ship
                first_ship_name = game.owned_ships[0]
                game.navigation.current_ship = Ship(first_ship_name, first_ship_name)
            except Exception:
                pass
        
        # Load faction system
        if 'faction_state' in save_data:
            _load_factions(game.faction_system, save_data['faction_state'])
        
        # Load events and news
        if 'event_state' in save_data:
            _load_events(game.event_system, save_data['event_state'])
        if 'news_state' in save_data:
            _load_news(game.news_system, save_data['news_state'])
        
        # Load galactic history
        if 'galactic_history_state' in save_data:
            _load_galactic_history(game.galactic_history, save_data['galactic_history_state'])
        
        # Load economy state
        if 'economy_state' in save_data:
            _load_economy(game.economy, save_data['economy_state'])
        
        # Load station manager state
        if 'station_manager_state' in save_data:
            _load_station_manager(game.station_manager, save_data['station_manager_state'])
        
        # Load bot manager state
        if 'bot_manager_state' in save_data:
            _load_bot_manager(game.bot_manager, save_data['bot_manager_state'])
        
        # Load player log
        game.player_log = save_data.get('player_log', [])
        
        return True
        
    except Exception as e:
        print(f"Error loading game: {e}")
        import traceback
        traceback.print_exc()
        return False


# Helper functions for saving/loading subsystems

def _save_current_ship(nav) -> Optional[Dict[str, Any]]:
    """Save current ship state"""
    if not nav or not nav.current_ship:
        return None
    
    ship = nav.current_ship
    return {
        'name': ship.name,
        'ship_class': ship.ship_class,
        'coordinates': ship.coordinates,
        'fuel': ship.fuel,
        'max_fuel': ship.max_fuel,
        'jump_range': ship.jump_range,
        'cargo': ship.cargo,
        'max_cargo': ship.max_cargo,
        'scan_range': ship.scan_range,
        'components': getattr(ship, 'components', {}),
        'attribute_profile': getattr(ship, 'attribute_profile', {}),
    }


def _load_current_ship(nav, state: Dict[str, Any]):
    """Load current ship state"""
    if not nav or not state:
        return
    
    from navigation import Ship
    
    # Create ship from saved state
    ship = Ship(state['name'], state.get('ship_class', 'Basic Transport'))
    ship.coordinates = tuple(state.get('coordinates', (50, 50, 25)))
    ship.fuel = state.get('fuel', 100)
    ship.max_fuel = state.get('max_fuel', 100)
    ship.jump_range = state.get('jump_range', 15)
    ship.cargo = state.get('cargo', {})
    ship.max_cargo = state.get('max_cargo', 100)
    ship.scan_range = state.get('scan_range', 5.0)
    
    # Restore components if they exist
    if 'components' in state:
        ship.components = state['components']
        # Recalculate stats from components
        if hasattr(ship, 'calculate_stats_from_components'):
            ship.calculate_stats_from_components()
    
    # Restore attribute profile if it exists
    if 'attribute_profile' in state:
        ship.attribute_profile = state['attribute_profile']
    
    nav.current_ship = ship


def _save_navigation(nav) -> Dict[str, Any]:
    """Save navigation system state"""
    if not nav:
        return {}
    
    state = {
        'selected_ship_index': nav.selected_ship_index,
    }
    
    # Save NPC ships
    if hasattr(nav, 'npc_ships'):
        state['npc_ships'] = [
            {
                'name': npc.name,
                'ship_class': npc.ship_class,
                'coordinates': list(npc.coordinates) if npc.coordinates else None,
                'destination': list(npc.destination) if npc.destination else None,
                'personality': npc.personality,
                'trade_goods': npc.trade_goods,
                'credits': npc.credits,
            }
            for npc in nav.npc_ships
        ]
    
    return state


def _load_navigation(nav, state: Dict[str, Any]):
    """Load navigation system state"""
    if not nav or not state:
        return
    
    # Restore current ship selection
    nav.selected_ship_index = state.get('selected_ship_index', 0)
    
    # Restore NPC ships
    if 'npc_ships' in state and hasattr(nav, 'npc_ships'):
        from navigation import NPCShip
        nav.npc_ships = []
        for npc_data in state['npc_ships']:
            npc = NPCShip(
                npc_data['name'],
                npc_data['ship_class'],
                tuple(npc_data['coordinates']),
                nav.galaxy
            )
            npc.destination = tuple(npc_data['destination']) if npc_data.get('destination') else None
            npc.personality = npc_data.get('personality', 'Friendly')
            npc.trade_goods = npc_data.get('trade_goods', {})
            npc.credits = npc_data.get('credits', 0)
            nav.npc_ships.append(npc)
    
    # Restore current ship (will be set when game initializes)


def _save_factions(faction_system) -> Dict[str, Any]:
    """Save faction system state"""
    if not faction_system:
        return {}
    
    return {
        'reputations': getattr(faction_system, 'reputations', {}),
        'relationships': getattr(faction_system, 'relationships', {}),
    }


def _load_factions(faction_system, state: Dict[str, Any]):
    """Load faction system state"""
    if not faction_system or not state:
        return
    
    if hasattr(faction_system, 'reputations'):
        faction_system.reputations = state.get('reputations', {})
    if hasattr(faction_system, 'relationships'):
        faction_system.relationships = state.get('relationships', {})


def _save_events(event_system) -> Dict[str, Any]:
    """Save event system state"""
    if not event_system:
        return {}
    
    # Serialize Event objects to dictionaries
    active_events_data = []
    for event in getattr(event_system, 'active_events', []):
        if hasattr(event, '__dict__'):
            # It's an Event object
            event_dict = {
                'event_type': getattr(event, 'event_type', ''),
                'name': getattr(event, 'name', ''),
                'description': getattr(event, 'description', ''),
                'effects': getattr(event, 'effects', {}),
                'duration': getattr(event, 'duration', 0),
                'affected_systems': getattr(event, 'affected_systems', []),
                'severity': getattr(event, 'severity', 1),
                'timestamp': getattr(event, 'timestamp', datetime.now()).isoformat() if hasattr(getattr(event, 'timestamp', None), 'isoformat') else str(getattr(event, 'timestamp', datetime.now())),
                'id': getattr(event, 'id', ''),
            }
            active_events_data.append(event_dict)
        else:
            # Already a dict or string, save as-is
            active_events_data.append(event)
    
    event_history_data = []
    for event in getattr(event_system, 'event_history', [])[-100:]:
        if hasattr(event, '__dict__'):
            # It's an Event object
            event_dict = {
                'event_type': getattr(event, 'event_type', ''),
                'name': getattr(event, 'name', ''),
                'description': getattr(event, 'description', ''),
                'effects': getattr(event, 'effects', {}),
                'duration': getattr(event, 'duration', 0),
                'affected_systems': getattr(event, 'affected_systems', []),
                'severity': getattr(event, 'severity', 1),
                'timestamp': getattr(event, 'timestamp', datetime.now()).isoformat() if hasattr(getattr(event, 'timestamp', None), 'isoformat') else str(getattr(event, 'timestamp', datetime.now())),
                'id': getattr(event, 'id', ''),
            }
            event_history_data.append(event_dict)
        else:
            # Already a dict or string, save as-is
            event_history_data.append(event)
    
    return {
        'active_events': active_events_data,
        'event_history': event_history_data,
    }


def _load_events(event_system, state: Dict[str, Any]):
    """Load event system state"""
    if not event_system or not state:
        return
    
    # Reconstruct Event objects from dictionaries
    try:
        from events import Event
        
        active_events = []
        for event_data in state.get('active_events', []):
            if isinstance(event_data, dict):
                # Reconstruct Event object
                timestamp_str = event_data.get('timestamp', '')
                if timestamp_str:
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str)
                    except (ValueError, AttributeError):
                        timestamp = datetime.now()
                else:
                    timestamp = datetime.now()
                
                event = Event(
                    event_type=event_data.get('event_type', ''),
                    name=event_data.get('name', ''),
                    description=event_data.get('description', ''),
                    effects=event_data.get('effects', {}),
                    duration=event_data.get('duration', 0),
                    affected_systems=event_data.get('affected_systems', []),
                    severity=event_data.get('severity', 1),
                )
                # Restore timestamp and id
                event.timestamp = timestamp
                event.id = event_data.get('id', event.id)
                active_events.append(event)
            else:
                # Keep as-is if not a dict (shouldn't happen, but be safe)
                active_events.append(event_data)
        
        event_history = []
        for event_data in state.get('event_history', []):
            if isinstance(event_data, dict):
                # Reconstruct Event object
                timestamp_str = event_data.get('timestamp', '')
                if timestamp_str:
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str)
                    except (ValueError, AttributeError):
                        timestamp = datetime.now()
                else:
                    timestamp = datetime.now()
                
                event = Event(
                    event_type=event_data.get('event_type', ''),
                    name=event_data.get('name', ''),
                    description=event_data.get('description', ''),
                    effects=event_data.get('effects', {}),
                    duration=event_data.get('duration', 0),
                    affected_systems=event_data.get('affected_systems', []),
                    severity=event_data.get('severity', 1),
                )
                # Restore timestamp and id
                event.timestamp = timestamp
                event.id = event_data.get('id', event.id)
                event_history.append(event)
            else:
                # Keep as-is if not a dict
                event_history.append(event_data)
        
        if hasattr(event_system, 'active_events'):
            event_system.active_events = active_events
        if hasattr(event_system, 'event_history'):
            event_system.event_history = event_history
    except ImportError:
        # If events module not available, skip loading events
        pass


def _save_news(news_system) -> Dict[str, Any]:
    """Save news system state"""
    if not news_system:
        return {}
    
    return {
        'news_feed': getattr(news_system, 'news_feed', [])[-50:],  # Keep last 50
    }


def _load_news(news_system, state: Dict[str, Any]):
    """Load news system state"""
    if not news_system or not state:
        return
    
    if hasattr(news_system, 'news_feed'):
        news_system.news_feed = state.get('news_feed', [])


def _save_galactic_history(galactic_history) -> Dict[str, Any]:
    """Save galactic history state"""
    if not galactic_history:
        return {}
    
    return {
        'archaeological_sites': getattr(galactic_history, 'archaeological_sites', []),
        'discovered_civilizations': getattr(galactic_history, 'discovered_civilizations', []),
    }


def _load_galactic_history(galactic_history, state: Dict[str, Any]):
    """Load galactic history state"""
    if not galactic_history or not state:
        return
    
    if hasattr(galactic_history, 'archaeological_sites'):
        galactic_history.archaeological_sites = state.get('archaeological_sites', [])
    if hasattr(galactic_history, 'discovered_civilizations'):
        galactic_history.discovered_civilizations = state.get('discovered_civilizations', [])


def _save_economy(economy) -> Dict[str, Any]:
    """Save economy system state"""
    if not economy:
        return {}
    
    market_history = getattr(economy, 'market_history', {})
    # If market_history is a dict, limit each market's history to last 100 entries
    if isinstance(market_history, dict):
        limited_history = {}
        for market_name, history_list in market_history.items():
            if isinstance(history_list, list):
                limited_history[market_name] = history_list[-100:]
            else:
                limited_history[market_name] = history_list
        market_history = limited_history
    elif isinstance(market_history, list):
        # If it's a list, just take last 100
        market_history = market_history[-100:]
    
    return {
        'markets': getattr(economy, 'markets', {}),
        'market_history': market_history,
    }


def _load_economy(economy, state: Dict[str, Any]):
    """Load economy system state"""
    if not economy or not state:
        return
    
    if hasattr(economy, 'markets'):
        economy.markets = state.get('markets', {})
    if hasattr(economy, 'market_history'):
        economy.market_history = state.get('market_history', {})


def _save_station_manager(station_manager) -> Dict[str, Any]:
    """Save station manager state"""
    if not station_manager:
        return {}
    
    return {
        'stations': getattr(station_manager, 'stations', []),
    }


def _load_station_manager(station_manager, state: Dict[str, Any]):
    """Load station manager state"""
    if not station_manager or not state:
        return
    
    if hasattr(station_manager, 'stations'):
        station_manager.stations = state.get('stations', [])


def _save_bot_manager(bot_manager) -> Dict[str, Any]:
    """Save bot manager state"""
    if not bot_manager:
        return {}
    
    return {
        'bots': [
            {
                'name': bot.name,
                'bot_type': bot.bot_type,
                'coordinates': bot.coordinates,
                'current_goal': getattr(bot, 'current_goal', ''),
                'personality': getattr(bot, 'personality', {}),
            }
            for bot in getattr(bot_manager, 'bots', [])
        ],
    }


def _load_bot_manager(bot_manager, state: Dict[str, Any]):
    """Load bot manager state"""
    if not bot_manager or not state:
        return
    
    # Bots will be recreated when bot manager initializes
    # Just store the data for reference
    pass

