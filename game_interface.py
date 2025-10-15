#!/usr/bin/env python3
"""
Main Game Interface Integration
Connects the ASCII interface with the existing 4X game logic
"""

import sys
import time
import threading
from interface import InterfaceManager, GameScreen, Colors, get_input, run_interface_loop

class GameInterface:
    """Main game interface that integrates with the 4X game"""
    
    def __init__(self):
        # Import and initialize the main game
        self.game = None
        self.interface = None
        self.character_creation_data = {}
        self.initialized = False
        
    def initialize_game(self):
        """Initialize the game systems"""
        try:
            # Import the main game module
            import game as main_game
            
            # Create a new game instance
            self.game = main_game.Game()
            
            # Initialize the interface with the game instance
            self.interface = InterfaceManager(self.game)
            
            # Set up game event handlers
            self.setup_game_handlers()
            
            self.initialized = True
            return True
            
        except Exception as e:
            print(f"Error initializing game: {e}")
            return False
    
    def setup_game_handlers(self):
        """Set up handlers for game events"""
        # Override interface handlers to work with actual game logic
        self.interface.handle_character_class_selection = self.actual_character_class_selection
        self.interface.handle_background_selection = self.actual_background_selection
        self.interface.complete_character_creation = self.actual_complete_character_creation
        self.interface.navigate_to_coordinates = self.actual_navigate_to_coordinates
        self.interface.refuel_ship = self.actual_refuel_ship
        
        # Add more game-specific handlers
        self.setup_trading_handlers()
        self.setup_ship_builder_handlers()
        self.setup_station_handlers()
        self.setup_bot_handlers()
    
    def setup_trading_handlers(self):
        """Set up trading interface handlers"""
        def handle_trading_input(key):
            if self.interface.current_screen == GameScreen.TRADING:
                if key.isdigit() and key != "0":
                    # Buy commodity by number
                    self.handle_buy_commodity(int(key))
                elif key.isalpha() and key.islower():
                    # Sell commodity by letter
                    self.handle_sell_commodity(key)
                elif key == "r":
                    self.interface.go_back()
        
        # Add trading input handler
        original_handle_input = self.interface.handle_menu_input
        def enhanced_handle_input(key):
            handle_trading_input(key)
            original_handle_input(key)
        
        self.interface.handle_menu_input = enhanced_handle_input
    
    def setup_ship_builder_handlers(self):
        """Set up ship builder handlers"""
        def handle_ship_builder_input(key):
            if self.interface.current_screen == GameScreen.SHIP_BUILDER:
                if key.isdigit() and key != "0":
                    self.handle_ship_builder_option(int(key))
        
        # Add ship builder input handler
        original_handle_input = self.interface.handle_menu_input
        def enhanced_handle_input(key):
            handle_ship_builder_input(key)
            original_handle_input(key)
        
        self.interface.handle_menu_input = enhanced_handle_input
    
    def setup_station_handlers(self):
        """Set up station management handlers"""
        def handle_station_input(key):
            if self.interface.current_screen == GameScreen.STATION_MANAGEMENT:
                if key == "1":
                    self.show_available_stations()
                elif key == "2":
                    self.purchase_station()
                elif key == "3":
                    self.interface.go_back()
        
        # Add station input handler
        original_handle_input = self.interface.handle_menu_input
        def enhanced_handle_input(key):
            handle_station_input(key)
            original_handle_input(key)
        
        self.interface.handle_menu_input = enhanced_handle_input
    
    def setup_bot_handlers(self):
        """Set up bot interaction handlers"""
        def handle_bot_input(key):
            if self.interface.current_screen == GameScreen.BOT_INTERACTION:
                if key == "1":
                    self.greet_bot()
                elif key == "2":
                    self.trade_with_bot()
                elif key == "3":
                    self.exchange_information_with_bot()
                elif key == "4":
                    self.interface.go_back()
        
        # Add bot input handler
        original_handle_input = self.interface.handle_menu_input
        def enhanced_handle_input(key):
            handle_bot_input(key)
            original_handle_input(key)
        
        self.interface.handle_menu_input = enhanced_handle_input
    
    def actual_character_class_selection(self, key):
        """Handle actual character class selection"""
        classes = ["Merchant Captain", "Explorer", "Industrial Magnate", 
                  "Military Commander", "Diplomat", "Scientist"]
        class_index = int(key) - 1
        
        if 0 <= class_index < len(classes):
            selected_class = classes[class_index]
            self.character_creation_data['class'] = selected_class
            self.interface.show_message(f"Selected class: {selected_class}")
    
    def actual_background_selection(self, key):
        """Handle actual background selection"""
        backgrounds = ["Core Worlds Noble", "Frontier Survivor", "Corporate Executive",
                      "Military Veteran", "Academic Researcher", "Pirate Reformed"]
        bg_index = ord(key) - ord('a')
        
        if 0 <= bg_index < len(backgrounds):
            selected_bg = backgrounds[bg_index]
            self.character_creation_data['background'] = selected_bg
            self.actual_complete_character_creation()
    
    def actual_complete_character_creation(self):
        """Complete character creation with actual game logic"""
        try:
            # Create character using game's character system
            if 'class' in self.character_creation_data and 'background' in self.character_creation_data:
                class_name = self.character_creation_data['class']
                background_name = self.character_creation_data['background']
                
                # Get character data
                from characters import character_classes, character_backgrounds
                
                if class_name in character_classes and background_name in character_backgrounds:
                    # Set up character
                    self.game.character_class = class_name
                    self.game.character_background = background_name
                    
                    # Apply starting bonuses
                    class_data = character_classes[class_name]
                    bg_data = character_backgrounds[background_name]
                    
                    # Starting credits
                    base_credits = class_data['starting_credits']
                    if 'credit_bonus' in bg_data:
                        base_credits += bg_data['credit_bonus']
                    elif 'credit_penalty' in bg_data:
                        base_credits += bg_data['credit_penalty']
                    
                    self.game.credits = max(1000, base_credits)  # Minimum 1000 credits
                    
                    # Add starting ships
                    self.game.owned_ships = ["Basic Transport"]
                    if 'starting_ships' in class_data:
                        self.game.owned_ships.extend(class_data['starting_ships'])
                    
                    # Add starting platforms/stations
                    if 'starting_platforms' in class_data:
                        self.game.owned_platforms = class_data['starting_platforms']
                    if 'starting_stations' in class_data:
                        self.game.owned_stations = class_data['starting_stations']
                    
                    # Initialize inventory
                    self.game.inventory = {}
                    
                    # Initialize other systems
                    self.initialize_game_systems()
                    
                    self.interface.show_message("Character created successfully!")
                    self.interface.set_screen(GameScreen.SHIP_STATUS)
                else:
                    self.interface.show_message("Error: Invalid character data")
            else:
                self.interface.show_message("Please select both class and background")
                
        except Exception as e:
            self.interface.show_message(f"Error creating character: {e}")
    
    def initialize_game_systems(self):
        """Initialize game systems after character creation"""
        try:
            # Initialize navigation system
            from navigation import NavigationSystem
            self.game.navigation = NavigationSystem(self.game)
            
            # Initialize economy
            from economy import EconomicSystem
            self.game.economy = EconomicSystem()
            
            # Initialize faction system
            from factions import FactionSystem
            self.game.faction_system = FactionSystem()
            
            # Initialize profession system
            from professions import ProfessionSystem
            self.game.profession_system = ProfessionSystem()
            
            # Initialize galactic history
            from galactic_history import GalacticHistory
            self.game.galactic_history = GalacticHistory()
            
            # Initialize station manager
            from station_manager import SpaceStationManager
            self.game.station_manager = SpaceStationManager(self.game.navigation.galaxy)
            
            # Initialize bot manager
            from ai_bots import BotManager
            self.game.bot_manager = BotManager(self.game)
            
            # Set up ship
            if self.game.owned_ships:
                self.game.navigation.current_ship = self.game.navigation.Ship(
                    self.game.owned_ships[0], 
                    self.game.owned_ships[0]
                )
            
            # Create markets for all systems
            self.game.navigation.create_all_markets()
            
        except Exception as e:
            self.interface.show_message(f"Error initializing game systems: {e}")
    
    def actual_navigate_to_coordinates(self, x: int, y: int, z: int):
        """Navigate ship to specific coordinates using game logic"""
        if hasattr(self.game, 'navigation') and self.game.navigation.current_ship:
            target = (x, y, z)
            success, message = self.game.navigation.current_ship.jump_to(target, self.game.navigation.galaxy, self.game)
            
            if success:
                self.interface.show_message(f"Jumped to ({x}, {y}, {z})")
                # Check for events at new location
                self.check_location_events()
            else:
                self.interface.show_message(f"Jump failed: {message}")
    
    def actual_refuel_ship(self):
        """Refuel ship using game logic"""
        if hasattr(self.game, 'navigation'):
            self.game.navigation.refuel_ship()
            self.interface.show_message("Ship refueled!")
    
    def check_location_events(self):
        """Check for events at current location"""
        if not hasattr(self.game, 'navigation') or not self.game.navigation.current_ship:
            return
        
        coords = self.game.navigation.current_ship.coordinates
        
        # Check for bots
        if hasattr(self.game, 'bot_manager'):
            bot = self.game.bot_manager.get_bot_at_location(coords)
            if bot:
                self.interface.show_message(f"Encountered {bot.name} at this location!")
        
        # Check for archaeological sites
        if hasattr(self.game, 'galactic_history'):
            sites = self.game.galactic_history.get_archaeological_sites_near(*coords, radius=1)
            if sites:
                self.interface.show_message(f"Archaeological site detected nearby!")
        
        # Check for stations
        if hasattr(self.game, 'station_manager'):
            station = self.game.station_manager.get_station_at_location(coords)
            if station:
                self.interface.show_message(f"Space station '{station['name']}' at this location!")
    
    # Trading handlers
    def handle_buy_commodity(self, number):
        """Handle buying a commodity by number"""
        try:
            if hasattr(self.game, 'economy') and hasattr(self.game, 'navigation'):
                system = self.game.navigation.galaxy.get_system_at(*self.game.navigation.current_ship.coordinates)
                if system and system['name'] in self.game.economy.markets:
                    market_info = self.game.economy.get_market_info(system['name'])
                    if market_info and number <= len(market_info['best_buys']):
                        commodity, price, supply = market_info['best_buys'][number - 1]
                        
                        # Simple buy 1 unit for now
                        success, message = self.game.economy.buy_commodity(
                            system['name'], commodity, 1, self.game.credits
                        )
                        
                        if success:
                            self.game.credits -= price
                            if commodity in self.game.inventory:
                                self.game.inventory[commodity] += 1
                            else:
                                self.game.inventory[commodity] = 1
                            self.interface.show_message(f"Bought 1 {commodity} for {price} credits")
                        else:
                            self.interface.show_message(f"Buy failed: {message}")
        except Exception as e:
            self.interface.show_message(f"Error buying commodity: {e}")
    
    def handle_sell_commodity(self, letter):
        """Handle selling a commodity by letter"""
        try:
            if hasattr(self.game, 'economy') and hasattr(self.game, 'navigation'):
                system = self.game.navigation.galaxy.get_system_at(*self.game.navigation.current_ship.coordinates)
                if system and system['name'] in self.game.economy.markets:
                    market_info = self.game.economy.get_market_info(system['name'])
                    if market_info and letter <= len(market_info['best_sells']):
                        commodity, price, demand = market_info['best_sells'][ord(letter) - ord('a')]
                        
                        # Check if player has this commodity
                        if commodity in self.game.inventory and self.game.inventory[commodity] > 0:
                            success, message, credits_earned = self.game.economy.sell_commodity(
                                system['name'], commodity, 1, self.game.inventory
                            )
                            
                            if success:
                                self.game.credits += credits_earned
                                self.game.inventory[commodity] -= 1
                                if self.game.inventory[commodity] <= 0:
                                    del self.game.inventory[commodity]
                                self.interface.show_message(f"Sold 1 {commodity} for {credits_earned} credits")
                            else:
                                self.interface.show_message(f"Sell failed: {message}")
                        else:
                            self.interface.show_message("You don't have this commodity")
        except Exception as e:
            self.interface.show_message(f"Error selling commodity: {e}")
    
    # Ship builder handlers
    def handle_ship_builder_option(self, number):
        """Handle ship builder menu option"""
        if number == 1:
            self.show_hull_types()
        elif number == 2:
            self.show_engines()
        elif number == 3:
            self.show_weapons()
        elif number == 4:
            self.show_shields()
        elif number == 5:
            self.show_special_systems()
        elif number == 6:
            self.view_ship_stats()
        elif number == 7:
            self.purchase_ship()
        elif number == 8:
            self.interface.go_back()
    
    def show_hull_types(self):
        """Show hull types for ship building"""
        from ship_builder import ship_components
        
        self.interface.show_message("Hull Types:")
        hulls = ship_components["Hull Types"]
        for i, (name, data) in enumerate(hulls.items(), 1):
            self.interface.show_message(f"{i}. {name} - {data['cost']:,} credits")
    
    def show_engines(self):
        """Show engines for ship building"""
        from ship_builder import ship_components
        
        self.interface.show_message("Engines:")
        engines = ship_components["Engines"]
        for i, (name, data) in enumerate(engines.items(), 1):
            self.interface.show_message(f"{i}. {name} - {data['cost']:,} credits")
    
    def show_weapons(self):
        """Show weapons for ship building"""
        from ship_builder import ship_components
        
        self.interface.show_message("Weapons:")
        weapons = ship_components["Weapons"]
        for i, (name, data) in enumerate(weapons.items(), 1):
            self.interface.show_message(f"{i}. {name} - {data['cost']:,} credits")
    
    def show_shields(self):
        """Show shields for ship building"""
        from ship_builder import ship_components
        
        self.interface.show_message("Shields:")
        shields = ship_components["Shields"]
        for i, (name, data) in enumerate(shields.items(), 1):
            self.interface.show_message(f"{i}. {name} - {data['cost']:,} credits")
    
    def show_special_systems(self):
        """Show special systems for ship building"""
        from ship_builder import ship_components
        
        self.interface.show_message("Special Systems:")
        specials = ship_components["Special Systems"]
        for i, (name, data) in enumerate(specials.items(), 1):
            self.interface.show_message(f"{i}. {name} - {data['cost']:,} credits")
    
    def view_ship_stats(self):
        """View current ship design stats"""
        if hasattr(self.game, 'ship_design'):
            from ship_builder import calculate_ship_stats
            stats = calculate_ship_stats(self.game.ship_design)
            self.interface.show_message(f"Ship Stats - Health: {stats['health']}, Cargo: {stats['cargo_space']}, Cost: {stats['total_cost']:,}")
        else:
            self.interface.show_message("No ship design selected")
    
    def purchase_ship(self):
        """Purchase the designed ship"""
        if hasattr(self.game, 'ship_design'):
            from ship_builder import calculate_ship_stats
            stats = calculate_ship_stats(self.game.ship_design)
            cost = stats['total_cost']
            
            if self.game.credits >= cost:
                self.game.credits -= cost
                ship_name = f"Custom Ship {len(self.game.custom_ships) + 1}"
                self.game.custom_ships.append({
                    'name': ship_name,
                    'design': self.game.ship_design,
                    'stats': stats
                })
                self.interface.show_message(f"Purchased {ship_name} for {cost:,} credits!")
            else:
                self.interface.show_message(f"Insufficient credits. Need {cost:,}, have {self.game.credits:,}")
        else:
            self.interface.show_message("No ship design to purchase")
    
    # Station handlers
    def show_available_stations(self):
        """Show available stations for purchase"""
        if hasattr(self.game, 'station_manager'):
            coords = self.game.navigation.current_ship.coordinates
            station = self.game.station_manager.get_station_at_location(coords)
            
            if station:
                if station['owner'] is None:
                    self.interface.show_message(f"Available: {station['name']} ({station['type']}) - {self.game.station_manager.station_types[station['type']]['cost']:,} credits")
                else:
                    self.interface.show_message(f"Station {station['name']} is owned by {station['owner']}")
            else:
                self.interface.show_message("No station at this location")
    
    def purchase_station(self):
        """Purchase station at current location"""
        if hasattr(self.game, 'station_manager'):
            coords = self.game.navigation.current_ship.coordinates
            success, message, cost = self.game.station_manager.purchase_station(coords, self.game.credits)
            
            if success:
                self.game.credits -= cost
                self.interface.show_message(message)
            else:
                self.interface.show_message(message)
    
    # Bot handlers
    def greet_bot(self):
        """Greet the bot at current location"""
        if hasattr(self.game, 'bot_manager') and hasattr(self.game, 'navigation'):
            coords = self.game.navigation.current_ship.coordinates
            bot = self.game.bot_manager.get_bot_at_location(coords)
            
            if bot:
                response = bot.interact_with_player("greeting")
                self.interface.show_message(f"{bot.name}: {response}")
                # Increase reputation
                bot.reputation += 1
                self.interface.show_message("Reputation increased!")
            else:
                self.interface.show_message("No bot to greet")
    
    def trade_with_bot(self):
        """Trade with bot"""
        if hasattr(self.game, 'bot_manager') and hasattr(self.game, 'navigation'):
            coords = self.game.navigation.current_ship.coordinates
            bot = self.game.bot_manager.get_bot_at_location(coords)
            
            if bot:
                self.interface.show_message(f"Trading with {bot.name} - functionality to be implemented")
            else:
                self.interface.show_message("No bot to trade with")
    
    def exchange_information_with_bot(self):
        """Exchange information with bot"""
        if hasattr(self.game, 'bot_manager') and hasattr(self.game, 'navigation'):
            coords = self.game.navigation.current_ship.coordinates
            bot = self.game.bot_manager.get_bot_at_location(coords)
            
            if bot:
                self.interface.show_message(f"Information exchange with {bot.name} - functionality to be implemented")
            else:
                self.interface.show_message("No bot to exchange information with")
    
    def run(self):
        """Run the game interface"""
        if not self.initialize_game():
            print("Failed to initialize game. Exiting.")
            return
        
        # Start the interface loop
        try:
            run_interface_loop(self.interface)
        except KeyboardInterrupt:
            self.interface.cleanup()
        except Exception as e:
            print(f"Error running interface: {e}")
            self.interface.cleanup()

def main():
    """Main entry point"""
    game_interface = GameInterface()
    game_interface.run()

if __name__ == "__main__":
    main()
