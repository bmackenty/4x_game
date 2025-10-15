#!/usr/bin/env python3
"""
ASCII-based Interface System for 4X Game
Cross-platform terminal interface with color support
"""

import sys
import os
import time
import threading
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

# Cross-platform color support
class Colors:
    """ANSI color codes for cross-platform terminal coloring"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    
    # Standard colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

class GameScreen(Enum):
    """Different game screens/activities"""
    MAIN_MENU = "main_menu"
    CHARACTER_CREATION = "character_creation"
    GALAXY_MAP = "galaxy_map"
    SHIP_STATUS = "ship_status"
    TRADING = "trading"
    SHIP_BUILDER = "ship_builder"
    STATION_MANAGEMENT = "station_management"
    FACTION_RELATIONS = "faction_relations"
    PROFESSION_PROGRESS = "profession_progress"
    ARCHAEOLOGY = "archaeology"
    BOT_INTERACTION = "bot_interaction"
    INVENTORY = "inventory"
    HELP = "help"

class InterfaceManager:
    """Main interface manager for the 4X game"""
    
    def __init__(self, game_instance):
        self.game = game_instance
        self.current_screen = GameScreen.MAIN_MENU
        self.screen_stack = []  # For screen history
        self.terminal_width = 80
        self.terminal_height = 24
        self.color_support = True
        
        # Input handling
        self.input_buffer = ""
        self.input_mode = "menu"  # "menu", "coordinate", "text", "number"
        self.input_prompt = ""
        self.input_callback = None
        
        # Status bar data
        self.status_data = {}
        
        # Character creation data
        self.selected_class = None
        self.selected_background = None
        self.character_name = "Captain"
        self.character_created = False
        
        # Screen refresh control
        self.needs_refresh = True
        self.refresh_thread = None
        self.running = True
        
        # Initialize terminal
        self.init_terminal()
        self.start_refresh_thread()
    
    def init_terminal(self):
        """Initialize terminal settings"""
        # Clear screen and hide cursor
        print("\033[2J\033[H", end="")
        print("\033[?25l", end="")  # Hide cursor
        
        # Try to get terminal size
        try:
            if os.name == 'nt':  # Windows
                import msvcrt
                import shutil
                self.terminal_width, self.terminal_height = shutil.get_terminal_size()
            else:  # Unix-like
                import termios
                import tty
                import struct
                import fcntl
                # Get terminal size
                h, w, hp, wp = struct.unpack('HHHH', fcntl.ioctl(0, termios.TIOCGWINSZ, struct.pack('HHHH', 0, 0, 0, 0)))
                self.terminal_width = w
                self.terminal_height = h
        except:
            # Fallback to default size
            self.terminal_width = 80
            self.terminal_height = 24
        
        # Check color support
        self.color_support = os.environ.get('TERM') != 'dumb' and sys.stdout.isatty()
        
        # Set up signal handlers for cleanup
        import signal
        signal.signal(signal.SIGINT, self.cleanup)
        signal.signal(signal.SIGTERM, self.cleanup)
    
    def cleanup(self, signum=None, frame=None):
        """Clean up terminal on exit"""
        self.running = False
        print("\033[?25h", end="")  # Show cursor
        print("\033[0m", end="")    # Reset colors
        print("\033[2J\033[H", end="")  # Clear screen
        sys.exit(0)
    
    def start_refresh_thread(self):
        """Start background refresh thread"""
        self.refresh_thread = threading.Thread(target=self.refresh_loop, daemon=True)
        self.refresh_thread.start()
    
    def refresh_loop(self):
        """Background thread for screen refresh"""
        while self.running:
            if self.needs_refresh:
                self.refresh_screen()
                self.needs_refresh = False
            time.sleep(0.1)  # 10 FPS refresh rate
    
    def refresh_screen(self):
        """Refresh the entire screen"""
        # Clear screen
        print("\033[2J\033[H", end="")
        
        # Draw current screen
        self.draw_screen()
        
        # Draw status bar
        self.draw_status_bar()
        
        # Draw input area
        self.draw_input_area()
        
        # Flush output
        sys.stdout.flush()
    
    def draw_screen(self):
        """Draw the current screen content with borders"""
        # Draw main border around the entire interface
        self.draw_main_border()
        
        # Draw screen-specific content
        if self.current_screen == GameScreen.MAIN_MENU:
            self.draw_main_menu()
        elif self.current_screen == GameScreen.CHARACTER_CREATION:
            self.draw_character_creation()
        elif self.current_screen == GameScreen.GALAXY_MAP:
            self.draw_galaxy_map()
        elif self.current_screen == GameScreen.SHIP_STATUS:
            self.draw_ship_status()
        elif self.current_screen == GameScreen.TRADING:
            self.draw_trading_interface()
        elif self.current_screen == GameScreen.SHIP_BUILDER:
            self.draw_ship_builder()
        elif self.current_screen == GameScreen.STATION_MANAGEMENT:
            self.draw_station_management()
        elif self.current_screen == GameScreen.FACTION_RELATIONS:
            self.draw_faction_relations()
        elif self.current_screen == GameScreen.PROFESSION_PROGRESS:
            self.draw_profession_progress()
        elif self.current_screen == GameScreen.ARCHAEOLOGY:
            self.draw_archaeology()
        elif self.current_screen == GameScreen.BOT_INTERACTION:
            self.draw_bot_interaction()
        elif self.current_screen == GameScreen.INVENTORY:
            self.draw_inventory()
        elif self.current_screen == GameScreen.HELP:
            self.draw_help()
    
    def draw_main_menu(self):
        """Draw the main menu screen"""
        # Title
        title = "4X GALACTIC EMPIRE MANAGEMENT GAME"
        title_x = (self.terminal_width - len(title)) // 2
        self.print_at(title_x, 3, title, Colors.BRIGHT_CYAN + Colors.BOLD)
        
        # Main menu section
        menu_width = 40
        menu_height = 12
        menu_x = (self.terminal_width - menu_width) // 2
        menu_y = 6
        
        self.draw_section_border(menu_x, menu_y, menu_width, menu_height, "MAIN MENU", Colors.CYAN)
        
        # Menu options
        menu_options = [
            "1. Start New Game",
            "2. Load Game (Coming Soon)",
            "3. Character Creation",
            "4. Help",
            "5. Quit"
        ]
        
        start_y = menu_y + 2
        for i, option in enumerate(menu_options):
            self.print_at(menu_x + 4, start_y + i * 2, option, Colors.WHITE)
        
        # ASCII art decoration
        self.draw_ascii_decoration()
    
    def draw_character_creation(self):
        """Draw character creation screen"""
        title = "CHARACTER CREATION"
        title_x = (self.terminal_width - len(title)) // 2
        self.print_at(title_x, 3, title, Colors.BRIGHT_YELLOW + Colors.BOLD)
        
        # Character class selection section
        class_width = 50
        class_height = 20
        class_x = 5
        class_y = 5
        
        self.draw_section_border(class_x, class_y, class_width, class_height, "CHARACTER CLASSES", Colors.CYAN)
        
        classes = [
            ("1", "Merchant Captain", "Trade specialist with bonus credits"),
            ("2", "Explorer", "Frontier scout with exploration bonuses"),
            ("3", "Industrial Magnate", "Manufacturing expert"),
            ("4", "Military Commander", "Combat veteran with tactical advantages"),
            ("5", "Diplomat", "Negotiation specialist"),
            ("6", "Scientist", "Research focused with technology bonuses")
        ]
        
        y = class_y + 2
        for num, name, desc in classes:
            # Highlight selected class
            if self.selected_class == num:
                color = Colors.BRIGHT_CYAN + Colors.BOLD
                marker = "✓ "
            else:
                color = Colors.CYAN
                marker = "  "
            self.print_at(class_x + 3, y, f"{marker}{num}. {name}", color)
            self.print_at(class_x + 7, y + 1, desc, Colors.DIM + Colors.WHITE)
            y += 3
        
        # Background selection section
        bg_width = 35
        bg_height = 10
        bg_x = 60
        bg_y = 5
        
        self.draw_section_border(bg_x, bg_y, bg_width, bg_height, "BACKGROUNDS", Colors.GREEN)
        
        backgrounds = [
            ("a", "Core Worlds Noble"),
            ("b", "Frontier Survivor"),
            ("c", "Corporate Executive"),
            ("d", "Military Veteran"),
            ("e", "Academic Researcher"),
            ("f", "Pirate Reformed")
        ]
        
        y = bg_y + 2
        for letter, name in backgrounds:
            # Highlight selected background
            if self.selected_background == letter:
                color = Colors.BRIGHT_GREEN + Colors.BOLD
                marker = "✓ "
            else:
                color = Colors.GREEN
                marker = "  "
            self.print_at(bg_x + 3, y, f"{marker}{letter}. {name}", color)
            y += 1
        
        # Character summary section
        summary_width = 50
        summary_height = 12
        summary_x = 5
        summary_y = 26
        
        self.draw_section_border(summary_x, summary_y, summary_width, summary_height, "CHARACTER SUMMARY", Colors.BRIGHT_WHITE)
        
        # Show current selections with confirmation
        y = summary_y + 2
        
        # Character name
        self.print_at(summary_x + 2, y, f"Name: {self.character_name}", Colors.CYAN)
        y += 1
        
        # Class selection
        if self.selected_class:
            class_names = {
                "1": "Merchant Captain", "2": "Explorer", "3": "Industrial Magnate",
                "4": "Military Commander", "5": "Diplomat", "6": "Scientist"
            }
            class_name = class_names.get(self.selected_class, 'Unknown')
            self.print_at(summary_x + 2, y, f"Class: {class_name} ✓", Colors.BRIGHT_GREEN)
            
            # Show class description
            class_descriptions = {
                "1": "Trade specialist with bonus credits",
                "2": "Frontier scout with exploration bonuses", 
                "3": "Manufacturing expert",
                "4": "Combat veteran with tactical advantages",
                "5": "Negotiation specialist",
                "6": "Research focused with technology bonuses"
            }
            y += 1
            desc = class_descriptions.get(self.selected_class, "")
            if desc:
                self.print_at(summary_x + 4, y, desc, Colors.DIM + Colors.WHITE)
        else:
            self.print_at(summary_x + 2, y, "Class: Not selected", Colors.DIM + Colors.WHITE)
        
        y += 2
        
        # Background selection
        if self.selected_background:
            bg_names = {
                "a": "Core Worlds Noble", "b": "Frontier Survivor", "c": "Corporate Executive",
                "d": "Military Veteran", "e": "Academic Researcher", "f": "Pirate Reformed"
            }
            bg_name = bg_names.get(self.selected_background, 'Unknown')
            self.print_at(summary_x + 2, y, f"Background: {bg_name} ✓", Colors.BRIGHT_GREEN)
        else:
            self.print_at(summary_x + 2, y, "Background: Not selected", Colors.DIM + Colors.WHITE)
        
        y += 2
        
        # Start game button
        if self.selected_class and self.selected_background:
            self.print_at(summary_x + 2, y, "Press 's' to START GAME", Colors.BRIGHT_YELLOW + Colors.BOLD)
            y += 1
            self.print_at(summary_x + 4, y, "✓ Character creation complete!", Colors.BRIGHT_GREEN)
        else:
            self.print_at(summary_x + 2, y, "Select class and background to continue", Colors.DIM + Colors.WHITE)
        
    
    def draw_galaxy_map(self):
        """Draw galaxy map screen with ASCII visualization"""
        title = "GALAXY MAP"
        title_x = (self.terminal_width - len(title)) // 2
        self.print_at(title_x, 2, title, Colors.BRIGHT_BLUE + Colors.BOLD)
        
        # Current location
        if hasattr(self.game, 'navigation') and self.game.navigation.current_ship:
            ship = self.game.navigation.current_ship
            x, y, z = ship.coordinates
            self.print_at(5, 4, f"Current Location: ({x}, {y}, {z})", Colors.WHITE)
            
            # System info
            system = self.game.navigation.galaxy.get_system_at(x, y, z)
            if system:
                self.print_at(5, 5, f"System: {system['name']} ({system['type']})", Colors.CYAN)
                self.print_at(5, 6, f"Population: {system['population']:,}", Colors.WHITE)
                self.print_at(5, 7, f"Resources: {system['resources']}", Colors.YELLOW)
        
        # ASCII Galaxy Map (2D projection)
        self.draw_ascii_galaxy_map()
        
        # Navigation options
        self.print_at(5, 20, "Navigation Options:", Colors.BRIGHT_WHITE + Colors.BOLD)
        self.print_at(8, 21, "1. Jump to System", Colors.WHITE)
        self.print_at(8, 22, "2. Navigate to Coordinates", Colors.WHITE)
        self.print_at(8, 23, "3. View Local Map", Colors.WHITE)
        self.print_at(8, 24, "4. Refuel Ship", Colors.WHITE)
        self.print_at(8, 25, "5. Select Different Ship", Colors.WHITE)
        self.print_at(8, 26, "6. Return to Main Menu", Colors.WHITE)
        
        # Nearby systems list
        if hasattr(self.game, 'navigation') and self.game.navigation.current_ship:
            self.print_at(60, 20, "Nearby Systems:", Colors.BRIGHT_WHITE + Colors.BOLD)
            nearby = self.game.navigation.galaxy.get_nearby_systems(
                *self.game.navigation.current_ship.coordinates, 
                self.game.navigation.current_ship.jump_range
            )
            
            y = 21
            for i, (system, distance) in enumerate(nearby[:6]):  # Show first 6
                fuel_cost = int(distance * 2)
                status = "✓" if fuel_cost <= self.game.navigation.current_ship.fuel else "✗"
                system_info = f"{system['name'][:15]:<15} {distance:.1f} {status}"
                self.print_at(63, y, system_info, Colors.WHITE)
                y += 1
    
    def draw_ascii_galaxy_map(self):
        """Draw ASCII representation of the galaxy"""
        if not hasattr(self.game, 'navigation'):
            return
        
        galaxy = self.game.navigation.galaxy
        current_ship = self.game.navigation.current_ship
        
        if not current_ship:
            return
        
        # Map dimensions (ASCII representation)
        map_width = 45
        map_height = 12
        map_start_x = 5
        map_start_y = 9
        
        # Draw map border
        self.print_at(map_start_x, map_start_y, "┌" + "─" * map_width + "┐", Colors.DIM + Colors.WHITE)
        for i in range(map_height):
            self.print_at(map_start_x, map_start_y + i + 1, "│", Colors.DIM + Colors.WHITE)
            self.print_at(map_start_x + map_width + 1, map_start_y + i + 1, "│", Colors.DIM + Colors.WHITE)
        self.print_at(map_start_x, map_start_y + map_height + 1, "└" + "─" * map_width + "┘", Colors.DIM + Colors.WHITE)
        
        # Plot systems on the map
        current_x, current_y, current_z = current_ship.coordinates
        
        # Convert 3D coordinates to 2D map coordinates
        for system_coords, system in galaxy.systems.items():
            sx, sy, sz = system_coords
            
            # Project 3D to 2D (XY plane with Z as depth indicator)
            map_x = int((sx / galaxy.size_x) * map_width) + 1
            map_y = int((sy / galaxy.size_y) * map_height) + 1
            
            # Clamp to map bounds
            map_x = max(1, min(map_x, map_width))
            map_y = max(1, min(map_y, map_height))
            
            # Choose symbol based on system type
            symbols = {
                'Core World': '●',
                'Industrial': '■',
                'Military': '▲',
                'Research': '◆',
                'Trading Hub': '★',
                'Mining': '♦',
                'Agricultural': '♠',
                'Frontier': '○'
            }
            
            symbol = symbols.get(system['type'], '•')
            
            # Color based on system properties
            if system['visited']:
                color = Colors.BRIGHT_WHITE
            elif system['resources'] == 'Rich':
                color = Colors.BRIGHT_YELLOW
            elif system['resources'] == 'Abundant':
                color = Colors.BRIGHT_GREEN
            elif system['threat_level'] > 7:
                color = Colors.BRIGHT_RED
            else:
                color = Colors.DIM + Colors.WHITE
            
            # Highlight current system
            if (sx, sy, sz) == (current_x, current_y, current_z):
                symbol = '@'
                color = Colors.BRIGHT_CYAN + Colors.BOLD
            
            self.print_at(map_start_x + map_x, map_start_y + map_y, symbol, color)
        
        # Add legend
        legend_y = map_start_y + map_height + 3
        self.print_at(map_start_x, legend_y, "Legend:", Colors.BRIGHT_WHITE + Colors.BOLD)
        self.print_at(map_start_x, legend_y + 1, "@ You  ● Core  ■ Industrial  ▲ Military", Colors.WHITE)
        self.print_at(map_start_x, legend_y + 2, "★ Trade  ◆ Research  ♦ Mining  ♠ Agri", Colors.WHITE)
        self.print_at(map_start_x, legend_y + 3, "○ Frontier  • Other", Colors.WHITE)
    
    def draw_ship_status(self):
        """Draw ship status screen"""
        title = "SHIP STATUS"
        title_x = (self.terminal_width - len(title)) // 2
        self.print_at(title_x, 2, title, Colors.BRIGHT_GREEN + Colors.BOLD)
        
        if hasattr(self.game, 'navigation') and self.game.navigation.current_ship:
            ship = self.game.navigation.current_ship
            x, y, z = ship.coordinates
            
            # Ship info
            self.print_at(5, 4, f"Ship: {ship.name} ({ship.ship_class})", Colors.CYAN)
            self.print_at(5, 5, f"Location: ({x}, {y}, {z})", Colors.WHITE)
            self.print_at(5, 6, f"Fuel: {ship.fuel}/{ship.max_fuel}", Colors.YELLOW)
            self.print_at(5, 7, f"Jump Range: {ship.jump_range} units", Colors.WHITE)
            
            # Cargo info
            cargo_total = sum(ship.cargo.values()) if ship.cargo else 0
            self.print_at(5, 8, f"Cargo: {cargo_total}/{ship.max_cargo}", Colors.MAGENTA)
            
            # System info
            system = self.game.navigation.galaxy.get_system_at(x, y, z)
            if system:
                self.print_at(5, 10, f"Current System: {system['name']}", Colors.BRIGHT_WHITE + Colors.BOLD)
                self.print_at(5, 11, f"Type: {system['type']}", Colors.CYAN)
                self.print_at(5, 12, f"Population: {system['population']:,}", Colors.WHITE)
                self.print_at(5, 13, f"Resources: {system['resources']}", Colors.YELLOW)
                self.print_at(5, 14, f"Threat Level: {system['threat_level']}/10", Colors.RED)
                self.print_at(5, 15, f"Description: {system['description']}", Colors.DIM + Colors.WHITE)
        
        # Action options
        self.print_at(5, 17, "Actions:", Colors.BRIGHT_WHITE + Colors.BOLD)
        self.print_at(8, 18, "1. View Galaxy Map", Colors.WHITE)
        self.print_at(8, 19, "2. Trade at Market", Colors.WHITE)
        self.print_at(8, 20, "3. Visit Station", Colors.WHITE)
        self.print_at(8, 21, "4. Return to Main Menu", Colors.WHITE)
    
    def draw_trading_interface(self):
        """Draw enhanced split-screen trading interface"""
        title = "TRADING INTERFACE"
        title_x = (self.terminal_width - len(title)) // 2
        self.print_at(title_x, 3, title, Colors.BRIGHT_GREEN + Colors.BOLD)
        
        # Split screen layout with borders
        left_width = self.terminal_width // 2 - 4
        right_width = self.terminal_width // 2 - 4
        
        # Left side - Buy opportunities
        self.draw_section_border(2, 5, left_width, 12, "BUY OPPORTUNITIES", Colors.CYAN)
        self.print_at(4, 7, "# Commodity           Price  Supply", Colors.DIM + Colors.WHITE)
        
        # Right side - Sell opportunities  
        self.draw_section_border(left_width + 4, 5, right_width, 12, "SELL OPPORTUNITIES", Colors.YELLOW)
        self.print_at(left_width + 6, 7, "L Commodity           Price  Demand", Colors.DIM + Colors.WHITE)
        
        # Market data
        if hasattr(self.game, 'economy') and hasattr(self.game, 'navigation'):
            system = self.game.navigation.galaxy.get_system_at(*self.game.navigation.current_ship.coordinates)
            if system and system['name'] in self.game.economy.markets:
                market_info = self.game.economy.get_market_info(system['name'])
                market = market_info['market']
                
                # Buy opportunities (left side)
                y = 8
                buy_list = []
                for i, (commodity, price, supply) in enumerate(market_info['best_buys'][:8]):
                    # Check if player can afford it
                    affordable = self.game.credits >= price
                    color = Colors.WHITE if affordable else Colors.DIM + Colors.RED
                    
                    line = f"{i+1} {commodity[:18]:<18} {price:>5}c {supply:>4}"
                    self.print_at(4, y, line, color)
                    buy_list.append(commodity)
                    y += 1
                
                # Sell opportunities (right side)
                y = 8
                sell_list = []
                for i, (commodity, price, demand) in enumerate(market_info['best_sells'][:8]):
                    # Check if player has this commodity
                    player_has = 0
                    if hasattr(self.game, 'inventory') and commodity in self.game.inventory:
                        player_has = self.game.inventory[commodity]
                    
                    if player_has > 0:
                        color = Colors.BRIGHT_GREEN
                    else:
                        color = Colors.DIM + Colors.WHITE
                    
                    line = f"{chr(ord('a')+i)} {commodity[:18]:<18} {price:>5}c {demand:>4}"
                    self.print_at(left_width + 6, y, line, color)
                    sell_list.append(commodity)
                    y += 1
                
                # Store lists for input handling
                self.buy_commodities = buy_list
                self.sell_commodities = sell_list
            else:
                self.print_at(4, 8, "No market available at this location", Colors.RED)
                self.buy_commodities = []
                self.sell_commodities = []
        
        # Market summary section
        summary_width = self.terminal_width - 6
        summary_height = 6
        summary_x = 3
        summary_y = 18
        
        self.draw_section_border(summary_x, summary_y, summary_width, summary_height, "MARKET SUMMARY", Colors.BRIGHT_WHITE)
        
        if hasattr(self.game, 'economy') and hasattr(self.game, 'navigation'):
            system = self.game.navigation.galaxy.get_system_at(*self.game.navigation.current_ship.coordinates)
            if system and system['name'] in self.game.economy.markets:
                self.print_at(summary_x + 2, summary_y + 2, f"Market: {system['name']} ({system['type']})", Colors.BRIGHT_WHITE + Colors.BOLD)
                self.print_at(summary_x + 2, summary_y + 3, f"Your Credits: {self.game.credits:,}", Colors.BRIGHT_GREEN)
                
                # Cargo info
                if hasattr(self.game, 'inventory'):
                    cargo_items = len(self.game.inventory)
                    cargo_total = sum(self.game.inventory.values()) if self.game.inventory else 0
                    self.print_at(summary_x + 2, summary_y + 4, f"Cargo: {cargo_items} types, {cargo_total} total items", Colors.CYAN)
        
        # Trading controls section
        controls_width = self.terminal_width - 6
        controls_height = 8
        controls_x = 3
        controls_y = 25
        
        self.draw_section_border(controls_x, controls_y, controls_width, controls_height, "TRADING CONTROLS", Colors.BRIGHT_WHITE)
        
        self.print_at(controls_x + 2, controls_y + 2, "1-8. Buy commodity by number", Colors.WHITE)
        self.print_at(controls_x + 2, controls_y + 3, "a-h. Sell commodity by letter", Colors.WHITE)
        self.print_at(controls_x + 2, controls_y + 4, "m. View market analysis", Colors.WHITE)
        self.print_at(controls_x + 2, controls_y + 5, "i. View inventory", Colors.WHITE)
        self.print_at(controls_x + 2, controls_y + 6, "r. Return to ship status", Colors.WHITE)
        
        # Show recent trades if any
        if hasattr(self, 'recent_trades') and self.recent_trades:
            self.print_at(controls_x + 2, controls_y + 7, "Recent Trades:", Colors.BRIGHT_WHITE + Colors.BOLD)
            for i, trade in enumerate(self.recent_trades[-2:]):  # Show last 2 trades
                self.print_at(controls_x + 4, controls_y + 8 + i, trade, Colors.DIM + Colors.WHITE)
    
    def draw_ship_builder(self):
        """Draw ship builder interface"""
        title = "SHIP BUILDER"
        title_x = (self.terminal_width - len(title)) // 2
        self.print_at(title_x, 3, title, Colors.BRIGHT_MAGENTA + Colors.BOLD)
        
        # Component categories section
        categories_width = 35
        categories_height = 12
        categories_x = 5
        categories_y = 5
        
        self.draw_section_border(categories_x, categories_y, categories_width, categories_height, "COMPONENT CATEGORIES", Colors.MAGENTA)
        
        categories = [
            ("1", "Hull Types"),
            ("2", "Engines"), 
            ("3", "Weapons"),
            ("4", "Shields"),
            ("5", "Special Systems"),
            ("6", "View Ship Stats"),
            ("7", "Purchase Ship"),
            ("8", "Return to Main Menu")
        ]
        
        y = categories_y + 2
        for num, category in categories:
            self.print_at(categories_x + 3, y, f"{num}. {category}", Colors.WHITE)
            y += 1
        
        # Current ship design section
        design_width = 45
        design_height = 12
        design_x = 45
        design_y = 5
        
        self.draw_section_border(design_x, design_y, design_width, design_height, "CURRENT SHIP DESIGN", Colors.CYAN)
        
        if hasattr(self.game, 'ship_design'):
            design = self.game.ship_design
            y = design_y + 2
            for component_type, component in design.items():
                if component:
                    self.print_at(design_x + 3, y, f"{component_type}: {component}", Colors.CYAN)
                    y += 1
        else:
            self.print_at(design_x + 3, design_y + 2, "No ship design selected", Colors.DIM + Colors.WHITE)
    
    def draw_station_management(self):
        """Draw station management interface"""
        title = "STATION MANAGEMENT"
        title_x = (self.terminal_width - len(title)) // 2
        self.print_at(title_x, 3, title, Colors.BRIGHT_YELLOW + Colors.BOLD)
        
        # Player stations section
        stations_width = 50
        stations_height = 12
        stations_x = 5
        stations_y = 5
        
        self.draw_section_border(stations_x, stations_y, stations_width, stations_height, "YOUR STATIONS", Colors.CYAN)
        
        if hasattr(self.game, 'station_manager'):
            stations = self.game.station_manager.get_player_stations()
            
            if stations:
                y = stations_y + 2
                for station in stations:
                    self.print_at(stations_x + 3, y, f"{station['name']} ({station['type']})", Colors.CYAN)
                    self.print_at(stations_x + 3, y + 1, f"Income: {station['income']:,} credits/cycle (Level {station['upgrade_level']})", Colors.GREEN)
                    y += 3
            else:
                self.print_at(stations_x + 3, stations_y + 2, "No stations owned", Colors.DIM + Colors.WHITE)
        
        # Available stations section
        available_width = 45
        available_height = 8
        available_x = 60
        available_y = 5
        
        self.draw_section_border(available_x, available_y, available_width, available_height, "STATION OPTIONS", Colors.YELLOW)
        
        self.print_at(available_x + 3, available_y + 2, "1. View Available Stations", Colors.WHITE)
        self.print_at(available_x + 3, available_y + 3, "2. Purchase Station", Colors.WHITE)
        self.print_at(available_x + 3, available_y + 4, "3. Return to Main Menu", Colors.WHITE)
    
    def draw_faction_relations(self):
        """Draw faction relations screen"""
        title = "FACTION RELATIONS"
        title_x = (self.terminal_width - len(title)) // 2
        self.print_at(title_x, 3, title, Colors.BRIGHT_RED + Colors.BOLD)
        
        # Faction list section
        factions_width = 60
        factions_height = 18
        factions_x = 5
        factions_y = 5
        
        self.draw_section_border(factions_x, factions_y, factions_width, factions_height, "FACTION RELATIONS", Colors.RED)
        
        if hasattr(self.game, 'faction_system'):
            y = factions_y + 2
            for faction_name in list(self.game.faction_system.player_relations.keys())[:15]:  # Show first 15
                rep = self.game.faction_system.player_relations[faction_name]
                status = self.game.faction_system.get_reputation_status(faction_name)
                
                # Color based on reputation
                if rep >= 50:
                    color = Colors.BRIGHT_GREEN
                elif rep >= 0:
                    color = Colors.YELLOW
                else:
                    color = Colors.RED
                
                line = f"{faction_name[:30]:<30} {status:<12} ({rep:+3})"
                self.print_at(factions_x + 3, y, line, color)
                y += 1
        
        # Options section
        options_width = 30
        options_height = 6
        options_x = 70
        options_y = 5
        
        self.draw_section_border(options_x, options_y, options_width, options_height, "OPTIONS", Colors.WHITE)
        
        self.print_at(options_x + 3, options_y + 2, "1. View Faction Details", Colors.WHITE)
        self.print_at(options_x + 3, options_y + 3, "2. Return to Main Menu", Colors.WHITE)
    
    def draw_profession_progress(self):
        """Draw profession progress screen"""
        title = "PROFESSION PROGRESS"
        title_x = (self.terminal_width - len(title)) // 2
        self.print_at(title_x, 2, title, Colors.BRIGHT_CYAN + Colors.BOLD)
        
        # Current profession
        if hasattr(self.game, 'profession_system'):
            prof_system = self.game.profession_system
            if prof_system.character_profession:
                self.print_at(5, 4, f"Current Profession: {prof_system.character_profession}", Colors.BRIGHT_WHITE + Colors.BOLD)
                
                level = prof_system.profession_levels.get(prof_system.character_profession, 1)
                exp = prof_system.profession_experience.get(prof_system.character_profession, 0)
                
                self.print_at(8, 5, f"Level: {level}/10", Colors.CYAN)
                self.print_at(8, 6, f"Experience: {exp}", Colors.YELLOW)
                
                # Progress bar
                progress = (exp % 100) / 100
                bar_width = 30
                filled = int(progress * bar_width)
                bar = "█" * filled + "░" * (bar_width - filled)
                self.print_at(8, 7, f"Progress: [{bar}] {progress*100:.1f}%", Colors.GREEN)
        
        self.print_at(5, 10, "1. View All Professions", Colors.WHITE)
        self.print_at(5, 11, "2. Return to Main Menu", Colors.WHITE)
    
    def draw_archaeology(self):
        """Draw archaeology screen"""
        title = "ARCHAEOLOGY"
        title_x = (self.terminal_width - len(title)) // 2
        self.print_at(title_x, 2, title, Colors.BRIGHT_MAGENTA + Colors.BOLD)
        
        # Archaeological sites
        if hasattr(self.game, 'galactic_history'):
            history = self.game.galactic_history
            summary = history.get_historical_summary()
            
            self.print_at(5, 4, "Discovery Summary:", Colors.BRIGHT_WHITE + Colors.BOLD)
            self.print_at(8, 5, f"Sites Discovered: {summary['discovered_sites']}/{summary['archaeological_sites']}", Colors.CYAN)
            self.print_at(8, 6, f"Artifacts Found: {summary['artifacts_discovered']}", Colors.YELLOW)
            self.print_at(8, 7, f"Ancient Civilizations: {summary['ancient_civilizations']}", Colors.MAGENTA)
        
        self.print_at(5, 10, "1. Explore Current Location", Colors.WHITE)
        self.print_at(5, 11, "2. View Discovered Artifacts", Colors.WHITE)
        self.print_at(5, 12, "3. Return to Main Menu", Colors.WHITE)
    
    def draw_bot_interaction(self):
        """Draw bot interaction screen"""
        title = "BOT INTERACTION"
        title_x = (self.terminal_width - len(title)) // 2
        self.print_at(title_x, 2, title, Colors.BRIGHT_BLUE + Colors.BOLD)
        
        # Current bot info
        if hasattr(self.game, 'navigation') and hasattr(self.game, 'bot_manager'):
            coords = self.game.navigation.current_ship.coordinates
            bot = self.game.bot_manager.get_bot_at_location(coords)
            
            if bot:
                self.print_at(5, 4, f"Meeting: {bot.name} ({bot.bot_type})", Colors.BRIGHT_WHITE + Colors.BOLD)
                self.print_at(8, 5, f"Activity: {bot.current_goal}", Colors.CYAN)
                self.print_at(8, 6, f"Personality: {bot.personality['type']}", Colors.YELLOW)
                self.print_at(8, 7, f"Credits: {bot.credits:,}", Colors.GREEN)
                self.print_at(8, 8, f"Reputation: {bot.reputation}", Colors.MAGENTA)
                
                # Interaction options
                self.print_at(5, 10, "Interaction Options:", Colors.BRIGHT_WHITE + Colors.BOLD)
                self.print_at(8, 11, "1. Greet", Colors.WHITE)
                self.print_at(8, 12, "2. Trade", Colors.WHITE)
                self.print_at(8, 13, "3. Exchange Information", Colors.WHITE)
                self.print_at(8, 14, "4. Return to Ship Status", Colors.WHITE)
            else:
                self.print_at(5, 4, "No bots at current location", Colors.DIM + Colors.WHITE)
                self.print_at(5, 6, "1. Return to Ship Status", Colors.WHITE)
    
    def draw_inventory(self):
        """Draw inventory screen"""
        title = "INVENTORY"
        title_x = (self.terminal_width - len(title)) // 2
        self.print_at(title_x, 2, title, Colors.BRIGHT_YELLOW + Colors.BOLD)
        
        # Inventory items
        if hasattr(self.game, 'inventory') and self.game.inventory:
            self.print_at(5, 4, "Your Inventory:", Colors.BRIGHT_WHITE + Colors.BOLD)
            
            y = 6
            for item, quantity in list(self.game.inventory.items())[:20]:  # Show first 20 items
                line = f"{item[:30]:<30} x{quantity:>4}"
                self.print_at(8, y, line, Colors.WHITE)
                y += 1
        else:
            self.print_at(8, 6, "Inventory is empty", Colors.DIM + Colors.WHITE)
        
        self.print_at(5, 15, "1. Return to Main Menu", Colors.WHITE)
    
    def draw_help(self):
        """Draw help screen"""
        title = "HELP"
        title_x = (self.terminal_width - len(title)) // 2
        self.print_at(title_x, 3, title, Colors.BRIGHT_CYAN + Colors.BOLD)
        
        # Help content section
        help_width = self.terminal_width - 6
        help_height = 22
        help_x = 3
        help_y = 5
        
        self.draw_section_border(help_x, help_y, help_width, help_height, "GAME HELP", Colors.CYAN)
        
        help_text = [
            "Controls:",
            "  Numbers (1-9): Select menu options",
            "  Letters (a-z): Alternative shortcuts", 
            "  Arrow Keys: Navigate menus",
            "  Enter: Confirm selection",
            "  ESC: Go back/exit",
            "",
            "Game Screens:",
            "  Galaxy Map: Navigate between star systems",
            "  Trading: Buy and sell commodities",
            "  Ship Builder: Design custom ships",
            "  Station Management: Manage owned stations",
            "  Faction Relations: View diplomatic standing",
            "  Archaeology: Explore ancient sites",
            "",
            "Tips:",
            "  Watch the status bar for key information",
            "  Use coordinates to navigate precisely",
            "  Trade for profit between systems",
            "  Build relationships with factions",
            "  Explore archaeological sites for artifacts"
        ]
        
        y = help_y + 2
        for line in help_text:
            self.print_at(help_x + 2, y, line, Colors.WHITE)
            y += 1
        
        # Instructions section
        instructions_width = self.terminal_width - 6
        instructions_height = 4
        instructions_x = 3
        instructions_y = 28
        
        self.draw_section_border(instructions_x, instructions_y, instructions_width, instructions_height, "CONTROLS", Colors.BRIGHT_WHITE)
        
        self.print_at(instructions_x + 2, instructions_y + 2, "Press ESC or 'q' to return to main menu", Colors.BRIGHT_YELLOW)
    
    def draw_main_border(self):
        """Draw main border around the entire interface"""
        # Top border
        self.print_at(1, 1, "┌" + "─" * (self.terminal_width - 2) + "┐", Colors.DIM + Colors.WHITE)
        
        # Side borders
        for y in range(2, self.terminal_height - 2):
            self.print_at(1, y, "│", Colors.DIM + Colors.WHITE)
            self.print_at(self.terminal_width, y, "│", Colors.DIM + Colors.WHITE)
        
        # Bottom border (above status bar)
        self.print_at(1, self.terminal_height - 3, "└" + "─" * (self.terminal_width - 2) + "┘", Colors.DIM + Colors.WHITE)
    
    def draw_section_border(self, x, y, width, height, title="", color=None):
        """Draw a bordered section with optional title"""
        if color is None:
            color = Colors.DIM + Colors.WHITE
        
        # Calculate the content width (excluding border characters)
        content_width = width - 2
        
        # Top border with title
        if title:
            title_len = len(title)
            if title_len + 4 <= content_width:
                border = "┌─ " + title + " " + "─" * (content_width - title_len - 4) + "┐"
            else:
                border = "┌─ " + title[:content_width-4] + "─┐"
        else:
            border = "┌" + "─" * content_width + "┐"
        
        self.print_at(x, y, border, color)
        
        # Side borders
        for i in range(1, height):
            self.print_at(x, y + i, "│", color)
            self.print_at(x + width - 1, y + i, "│", color)
        
        # Bottom border
        self.print_at(x, y + height, "└" + "─" * content_width + "┘", color)
    
    def draw_ascii_decoration(self):
        """Draw ASCII art decoration"""
        # Simple starfield
        import random
        random.seed(42)  # Consistent decoration
        
        for _ in range(20):
            x = random.randint(60, 75)
            y = random.randint(3, 20)
            self.print_at(x, y, "*", Colors.DIM + Colors.WHITE)
    
    def draw_status_bar(self):
        """Draw always-visible status bar"""
        status_y = self.terminal_height - 2
        
        # Character info (if created)
        if self.character_created and 'character' in self.status_data:
            char = self.status_data['character']
            char_text = f"{char['name']} ({char['class_name']})"
            self.print_at(2, status_y, char_text, Colors.BRIGHT_YELLOW)
        
        # Player info
        if hasattr(self.game, 'credits'):
            credits_text = f"Credits: {self.game.credits:,}"
            credits_x = 25 if self.character_created else 2
            self.print_at(credits_x, status_y, credits_text, Colors.BRIGHT_GREEN)
        
        # Ship info
        if hasattr(self.game, 'navigation') and self.game.navigation.current_ship:
            ship = self.game.navigation.current_ship
            ship_text = f"Ship: {ship.name}"
            ship_x = 50 if self.character_created else 25
            self.print_at(ship_x, status_y, ship_text, Colors.CYAN)
            
            # Location
            x, y, z = ship.coordinates
            location_text = f"Location: ({x},{y},{z})"
            location_x = 70 if self.character_created else 45
            self.print_at(location_x, status_y, location_text, Colors.WHITE)
            
            # Fuel
            fuel_text = f"Fuel: {ship.fuel}/{ship.max_fuel}"
            fuel_color = Colors.RED if ship.fuel < ship.max_fuel * 0.2 else Colors.YELLOW
            fuel_x = 90 if self.character_created else 65
            self.print_at(fuel_x, status_y, fuel_text, fuel_color)
        
        # Current screen
        screen_text = f"Screen: {self.current_screen.value}"
        self.print_at(2, status_y + 1, screen_text, Colors.DIM + Colors.WHITE)
    
    def draw_input_area(self):
        """Draw input prompt area"""
        input_y = self.terminal_height - 1
        
        if self.input_prompt:
            prompt_text = f"{self.input_prompt}: {self.input_buffer}"
            self.print_at(2, input_y, prompt_text, Colors.BRIGHT_WHITE)
        else:
            # Default prompt
            self.print_at(2, input_y, "Enter command: ", Colors.WHITE)
    
    def print_at(self, x: int, y: int, text: str, color: str = ""):
        """Print text at specific coordinates with color"""
        if not self.color_support:
            color = ""
        
        # Ensure coordinates are within bounds
        x = max(1, min(x, self.terminal_width))
        y = max(1, min(y, self.terminal_height))
        
        # Move cursor to position and print
        print(f"\033[{y};{x}H{color}{text}{Colors.RESET if color else ''}", end="")
    
    def set_screen(self, screen: GameScreen):
        """Change to a different screen"""
        self.screen_stack.append(self.current_screen)
        self.current_screen = screen
        self.needs_refresh = True
    
    def go_back(self):
        """Go back to previous screen"""
        if self.screen_stack:
            self.current_screen = self.screen_stack.pop()
            self.needs_refresh = True
    
    def set_input_mode(self, mode: str, prompt: str = "", callback=None):
        """Set input mode and prompt"""
        self.input_mode = mode
        self.input_prompt = prompt
        self.input_callback = callback
        self.input_buffer = ""
    
    def handle_input(self, key: str):
        """Handle input based on current mode"""
        if self.input_mode == "coordinate":
            self.handle_coordinate_input(key)
        elif self.input_mode == "number":
            self.handle_number_input(key)
        elif self.input_mode == "text":
            self.handle_text_input(key)
        else:  # menu mode
            self.handle_menu_input(key)
    
    def handle_menu_input(self, key: str):
        """Handle menu navigation input"""
        # Handle escape key and 'q' for going back
        if key == "\x1b" or key == "escape" or key.lower() == "q":  # ESC key or 'q'
            if self.current_screen == GameScreen.HELP:
                self.set_screen(GameScreen.MAIN_MENU)
            elif self.current_screen == GameScreen.CHARACTER_CREATION:
                self.set_screen(GameScreen.MAIN_MENU)
            elif self.current_screen in [GameScreen.GALAXY_MAP, GameScreen.SHIP_STATUS, 
                                       GameScreen.TRADING, GameScreen.SHIP_BUILDER,
                                       GameScreen.STATION_MANAGEMENT, GameScreen.FACTION_RELATIONS,
                                       GameScreen.PROFESSION_PROGRESS, GameScreen.ARCHAEOLOGY,
                                       GameScreen.BOT_INTERACTION, GameScreen.INVENTORY]:
                self.set_screen(GameScreen.MAIN_MENU)
            return
        
        # Process menu selection based on current screen
        if self.current_screen == GameScreen.MAIN_MENU:
            if key == "1":
                # Start new game - go to character creation
                self.set_screen(GameScreen.CHARACTER_CREATION)
            elif key == "3":
                self.set_screen(GameScreen.CHARACTER_CREATION)
            elif key == "4":
                self.set_screen(GameScreen.HELP)
            elif key == "5":
                self.cleanup()
        
        elif self.current_screen == GameScreen.CHARACTER_CREATION:
            if key in "123456":
                # Character class selection
                self.handle_character_class_selection(key)
            elif key in "abcdef":
                # Background selection
                self.handle_background_selection(key)
            elif key.lower() == "s" and self.selected_class and self.selected_background:
                # Start game with selected character
                self.start_new_game()
        
        elif self.current_screen == GameScreen.GALAXY_MAP:
            if key == "1":
                # Jump to system
                self.handle_system_jump()
            elif key == "2":
                # Navigate to coordinates
                self.set_input_mode("coordinate", "Enter coordinates (x,y,z)")
            elif key == "3":
                # View local map
                self.show_local_map()
            elif key == "4":
                # Refuel ship
                self.refuel_ship()
            elif key == "5":
                # Select different ship
                self.select_ship()
            elif key == "6":
                self.go_back()
        
        elif self.current_screen == GameScreen.SHIP_STATUS:
            if key == "1":
                self.set_screen(GameScreen.GALAXY_MAP)
            elif key == "2":
                self.set_screen(GameScreen.TRADING)
            elif key == "3":
                self.set_screen(GameScreen.STATION_MANAGEMENT)
            elif key == "4":
                self.set_screen(GameScreen.MAIN_MENU)
        
        # Add more screen handlers as needed
    
    def handle_coordinate_input(self, key: str):
        """Handle coordinate input"""
        if key == "\r" or key == "\n":  # Enter
            try:
                # Parse coordinates
                coords = [int(x.strip()) for x in self.input_buffer.split(",")]
                if len(coords) == 3:
                    x, y, z = coords
                    self.navigate_to_coordinates(x, y, z)
                else:
                    self.show_message("Invalid coordinates. Use format: x,y,z")
            except ValueError:
                self.show_message("Invalid coordinates. Use numbers only.")
            
            self.set_input_mode("menu")
        elif key == "\x1b":  # Escape
            self.set_input_mode("menu")
        else:
            self.input_buffer += key
    
    def handle_number_input(self, key: str):
        """Handle number input"""
        if key == "\r" or key == "\n":  # Enter
            if self.input_callback:
                self.input_callback(self.input_buffer)
            self.set_input_mode("menu")
        elif key == "\x1b":  # Escape
            self.set_input_mode("menu")
        elif key.isdigit():
            self.input_buffer += key
    
    def handle_text_input(self, key: str):
        """Handle text input"""
        if key == "\r" or key == "\n":  # Enter
            if self.input_callback:
                self.input_callback(self.input_buffer)
            self.set_input_mode("menu")
        elif key == "\x1b":  # Escape
            self.set_input_mode("menu")
        elif key == "\b" or key == "\x7f":  # Backspace
            self.input_buffer = self.input_buffer[:-1]
        else:
            self.input_buffer += key
    
    def show_message(self, message: str, color: str = Colors.WHITE):
        """Show a temporary message"""
        # Print message to console for immediate feedback
        print(f"\n{color}{message}{Colors.RESET}")
        # Trigger screen refresh to update the display
        self.needs_refresh = True
    
    # Game action handlers
    def handle_character_class_selection(self, key: str):
        """Handle character class selection with feedback"""
        self.selected_class = key
        class_name = self.get_class_name(key)
        self.show_message(f"Selected character class: {class_name}", Colors.BRIGHT_GREEN)
        # Force immediate screen refresh
        self.refresh_screen()
    
    def handle_background_selection(self, key: str):
        """Handle background selection with feedback"""
        self.selected_background = key
        bg_name = self.get_background_name(key)
        self.show_message(f"Selected background: {bg_name}", Colors.BRIGHT_GREEN)
        # Force immediate screen refresh
        self.refresh_screen()
    
    def get_class_name(self, key: str) -> str:
        """Get class name from key"""
        class_names = {
            "1": "Merchant Captain", "2": "Explorer", "3": "Industrial Magnate",
            "4": "Military Commander", "5": "Diplomat", "6": "Scientist"
        }
        return class_names.get(key, "Unknown")
    
    def get_background_name(self, key: str) -> str:
        """Get background name from key"""
        bg_names = {
            "a": "Core Worlds Noble", "b": "Frontier Survivor", "c": "Corporate Executive",
            "d": "Military Veteran", "e": "Academic Researcher", "f": "Pirate Reformed"
        }
        return bg_names.get(key, "Unknown")
    
    def start_new_game(self):
        """Start a new game with selected character"""
        if not self.selected_class or not self.selected_background:
            self.show_message("Please select both class and background first!", Colors.RED)
            return
        
        # Create character data
        character_data = {
            'class': self.selected_class,
            'class_name': self.get_class_name(self.selected_class),
            'background': self.selected_background,
            'background_name': self.get_background_name(self.selected_background),
            'name': self.character_name
        }
        
        # Store character data in status
        self.status_data['character'] = character_data
        self.character_created = True
        
        # Initialize game with character (handle errors gracefully)
        try:
            if hasattr(self.game, 'initialize_new_game'):
                self.game.initialize_new_game(character_data)
            self.show_message(f"Character created as {character_data['class_name']} with {character_data['background_name']} background!", Colors.BRIGHT_GREEN)
            # Go to ship status screen
            self.set_screen(GameScreen.SHIP_STATUS)
        except Exception as e:
            self.show_message(f"Character created as {character_data['class_name']} with {character_data['background_name']} background! (Game systems still loading...)", Colors.BRIGHT_YELLOW)
            # Still go to ship status screen even if game init failed
            self.set_screen(GameScreen.SHIP_STATUS)
    
    def complete_character_creation(self):
        """Complete character creation and start game"""
        self.show_message("Character created! Starting game...")
        self.set_screen(GameScreen.SHIP_STATUS)
    
    def navigate_to_coordinates(self, x: int, y: int, z: int):
        """Navigate ship to specific coordinates"""
        if hasattr(self.game, 'navigation'):
            target = (x, y, z)
            success, message = self.game.navigation.current_ship.jump_to(target, self.game.navigation.galaxy, self.game)
            self.show_message(message)
    
    def handle_system_jump(self):
        """Handle jumping to a nearby system"""
        # This would show a list of nearby systems for selection
        self.show_message("System jump functionality - to be implemented")
    
    def show_local_map(self):
        """Show local map of nearby systems"""
        self.show_message("Local map functionality - to be implemented")
    
    def refuel_ship(self):
        """Refuel the current ship"""
        if hasattr(self.game, 'navigation'):
            self.game.navigation.refuel_ship()
            self.show_message("Ship refueled!")
    
    def select_ship(self):
        """Select a different ship"""
        self.show_message("Ship selection functionality - to be implemented")

# Input handling functions
def get_input():
    """Get input from terminal (cross-platform)"""
    import sys
    
    if os.name == 'nt':  # Windows
        import msvcrt
        if msvcrt.kbhit():
            key = msvcrt.getch().decode('utf-8')
            return key
    else:  # Unix-like
        import tty
        import termios
        import select
        
        if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            return sys.stdin.read(1)
    
    return None

# Main interface loop
def run_interface_loop(interface_manager):
    """Main input loop for the interface"""
    while interface_manager.running:
        key = get_input()
        if key:
            interface_manager.handle_input(key)
            interface_manager.needs_refresh = True
        time.sleep(0.01)  # Small delay to prevent high CPU usage
