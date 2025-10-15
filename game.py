#!/usr/bin/env python3
"""
4X Game - Simple Text Frontend
A space-based 4X strategy game with manufacturing, trading, and exploration.
"""

import sys
import os
import random
from manufacturing import industrial_platforms
from goods import commodities
from ship_classes import ship_classes
from space_stations import space_stations
from characters import character_classes, character_backgrounds, create_character_stats
from ship_builder import ship_components, ship_templates, calculate_ship_stats
from navigation import NavigationSystem
from economy import EconomicSystem
from station_manager import ShipUpgradeSystem, SpaceStationManager
from ai_bots import BotManager
from factions import FactionSystem
from professions import ProfessionSystem
from galactic_history import GalacticHistory
import threading
import time

class Game:
    def __init__(self):
        self.player_name = ""
        self.character_class = ""
        self.character_background = ""
        self.character_stats = {}
        self.credits = 10000
        self.inventory = {}
        self.owned_ships = []
        self.custom_ships = []  # Player-built ships
        self.owned_stations = []
        self.owned_platforms = []
        self.navigation = NavigationSystem(self)
        self.economy = EconomicSystem()
        self.upgrade_system = ShipUpgradeSystem()
        self.station_manager = None  # Will be initialized after navigation
        self.bot_manager = None  # Will be initialized after navigation
        self.bot_update_thread = None
        self.game_running = True
        self.faction_system = FactionSystem()
        self.profession_system = ProfessionSystem()
        self.galactic_history = GalacticHistory()
        
    def display_header(self):
        print("\n" + "="*60)
        print("           GALACTIC EMPIRE MANAGEMENT SYSTEM")
        print("="*60)
        print(f"Commander: {self.player_name}")
        if self.character_class:
            print(f"Class: {self.character_class} | Background: {self.character_background}")
        print(f"Credits: {self.credits:,}")
        
        # Display current ship information
        if self.navigation.current_ship:
            ship = self.navigation.current_ship
            x, y, z = ship.coordinates
            cargo_count = sum(ship.cargo.values()) if ship.cargo else 0
            
            print(f"\n[SHIP] Current Ship: {ship.name} ({ship.ship_class})")
            print(f"   Location: ({x}, {y}, {z}) | Fuel: {ship.fuel}/{ship.max_fuel}")
            print(f"   Cargo: {cargo_count}/{ship.max_cargo} units")
            
            # Show cargo details if any
            if ship.cargo:
                cargo_items = []
                for item, quantity in ship.cargo.items():
                    if quantity > 0:
                        cargo_items.append(f"{item}: {quantity}")
                if cargo_items:
                    print(f"   Contents: {', '.join(cargo_items)}")
            
            # Show current system if at one
            system = self.navigation.galaxy.get_system_at(x, y, z)
            if system:
                print(f"   System: {system['name']} ({system['type']})")
        else:
            print("\n[SHIP] No ship selected - use Navigation menu to select a vessel")
        
        print("="*60)

    def main_menu(self):
        while True:
            # Occasionally trigger economic events (5% chance per menu access)
            if random.random() < 0.05:
                self.trigger_economic_event()
            
            self.display_header()
            print("\nMAIN MENU:")
            print("1. Browse Manufacturing Platforms")
            print("2. View Commodities Market") 
            print("3. Ship Classes Catalog")
            print("4. Space Stations Directory")
            print("5. View Your Assets")
            print("6. Trade Goods")
            print("7. Purchase Assets")
            print("8. Ship Builder")
            print("9. Ship Upgrades")
            print("10. Navigate Space")
            print("11. Station Management")
            print("12. AI Bots Status")
            print("13. Faction Relations")
            print("14. Profession & Career")
            print("15. Galactic History & Archaeology")
            print("16. Character Profile")
            print("17. Save & Exit")
            
            choice = input("\nEnter your choice (1-17): ").strip()
            
            if choice == "1":
                self.browse_manufacturing()
            elif choice == "2":
                self.view_commodities()
            elif choice == "3":
                self.view_ships()
            elif choice == "4":
                self.view_stations()
            elif choice == "5":
                self.view_assets()
            elif choice == "6":
                self.trade_menu()
            elif choice == "7":
                self.purchase_menu()
            elif choice == "8":
                self.ship_builder_menu()
            elif choice == "9":
                self.ship_upgrade_menu()
            elif choice == "10":
                self.navigation_menu()
            elif choice == "11":
                self.station_management_menu()
            elif choice == "12":
                self.ai_bots_menu()
            elif choice == "13":
                self.faction_relations_menu()
            elif choice == "14":
                self.profession_career_menu()
            elif choice == "15":
                self.galactic_history_menu()
            elif choice == "16":
                self.character_profile()
            elif choice == "17":
                self.save_and_exit()
                break
            else:
                print("Invalid choice. Please try again.")
                input("\nPress Enter to continue...")

    def browse_manufacturing(self):
        print("\n" + "="*60)
        print("           MANUFACTURING PLATFORMS")
        print("="*60)
        
        categories = {}
        for name, info in industrial_platforms.items():
            category = info["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append((name, info))
        
        for category, platforms in categories.items():
            print(f"\n[{category.upper()}]")
            print("-" * (len(category) + 2))
            for name, info in platforms:
                print(f"• {name}")
                print(f"  Type: {info['type']}")
                print(f"  Description: {info['description']}")
                print()
        
        input("\nPress Enter to return to main menu...")

    def view_commodities(self):
        print("\n" + "="*60)
        print("           COMMODITIES MARKET")
        print("="*60)
        
        for category, items in commodities.items():
            print(f"\n[{category.upper()}]")
            print("-" * (len(category) + 2))
            for item in items:
                print(f"• {item['name']} - {item['value']} credits")
                print(f"  {item['description']}")
                print()
        
        input("\nPress Enter to return to main menu...")

    def view_ships(self):
        print("\n" + "="*60)
        print("           SHIP CLASSES CATALOG")
        print("="*60)
        
        ship_types = {}
        for name, info in ship_classes.items():
            ship_class = info["Class"]
            if ship_class not in ship_types:
                ship_types[ship_class] = []
            ship_types[ship_class].append((name, info))
        
        for ship_type, ships in ship_types.items():
            print(f"\n[{ship_type.upper()}]")
            print("-" * (len(ship_type) + 2))
            for name, info in ships:
                print(f"• {name}")
                print(f"  Description: {info['Description']}")
                print()
        
        input("\nPress Enter to return to main menu...")

    def auto_select_ship(self):
        """Automatically select the first available ship if none is currently selected"""
        if self.navigation.current_ship:
            return  # Already have a ship selected
        
        all_ships = self.owned_ships + [ship['name'] for ship in self.custom_ships]
        
        if all_ships:
            # Select the first available ship
            ship_name = all_ships[0]
            
            # Determine ship class
            if ship_name in self.owned_ships:
                ship_class = ship_name
            else:
                # Custom ship - find its class
                for custom_ship in self.custom_ships:
                    if custom_ship['name'] == ship_name:
                        ship_class = "Custom Ship"
                        break
                else:
                    ship_class = "Custom Ship"
            
            # Create and select the ship
            from navigation import Ship
            self.navigation.current_ship = Ship(ship_name, ship_class)
            print(f"\n[SHIP] Automatically selected ship: {ship_name}")

    def view_stations(self):
        print("\n" + "="*60)
        print("           SPACE STATIONS DIRECTORY")
        print("="*60)
        
        station_categories = {}
        for name, info in space_stations.items():
            category = info["category"]
            if category not in station_categories:
                station_categories[category] = []
            station_categories[category].append((name, info))
        
        for category, stations in station_categories.items():
            print(f"\n[{category.upper()}]")
            print("-" * (len(category) + 2))
            for name, info in stations:
                print(f"• {name}")
                print(f"  Type: {info['type']}")
                print(f"  Description: {info['description']}")
                print()
        
        input("\nPress Enter to return to main menu...")

    def view_assets(self):
        print("\n" + "="*60)
        print("           YOUR ASSETS")
        print("="*60)
        
        print(f"Credits: {self.credits:,}")
        
        print("\nINVENTORY:")
        if self.inventory:
            for item, quantity in self.inventory.items():
                print(f"  • {item}: {quantity}")
        else:
            print("  (Empty)")
            
        print("\nOWNED SHIPS:")
        if self.owned_ships:
            for ship in self.owned_ships:
                print(f"  • {ship}")
        else:
            print("  (None)")
            
        print("\nCUSTOM SHIPS:")
        if self.custom_ships:
            for ship in self.custom_ships:
                print(f"  • {ship['name']} ({ship['role']})")
        else:
            print("  (None)")
            
        print("\nOWNED STATIONS:")
        if self.owned_stations:
            for station in self.owned_stations:
                print(f"  • {station}")
        else:
            print("  (None)")
            
        print("\nOWNED SPACE STATIONS:")
        if self.station_manager:
            player_stations = self.station_manager.get_player_stations()
            if player_stations:
                for station in player_stations:
                    coords = station['coordinates']
                    print(f"  • {station['name']} ({station['type']}) at ({coords[0]}, {coords[1]}, {coords[2]})")
            else:
                print("  (None)")
        else:
            print("  (System not initialized)")
            
        print("\nOWNED MANUFACTURING PLATFORMS:")
        if self.owned_platforms:
            for platform in self.owned_platforms:
                print(f"  • {platform}")
        else:
            print("  (None)")
        
        input("\nPress Enter to return to main menu...")

    def trade_menu(self):
        print("\n" + "="*60)
        print("           TRADE GOODS")
        print("="*60)
        
        # Check if at a star system
        if not self.navigation.current_ship:
            print("No ship selected for trading!")
            input("\nPress Enter to continue...")
            return
        
        x, y, z = self.navigation.current_ship.coordinates
        system = self.navigation.galaxy.get_system_at(x, y, z)
        
        if not system:
            print("You must be at a star system to trade!")
            print("Navigate to a star system first.")
            input("\nPress Enter to continue...")
            return
        
        print(f"Trading at: {system['name']}")
        print("1. View Market")
        print("2. Buy Commodities")
        print("3. Sell Commodities")
        print("4. Market Analysis")
        print("5. Trade Opportunities")
        print("6. Back to Main Menu")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            self.view_market(system['name'])
        elif choice == "2":
            self.buy_commodities_new(system['name'])
        elif choice == "3":
            self.sell_commodities_new(system['name'])
        elif choice == "4":
            self.market_analysis(system['name'])
        elif choice == "5":
            self.trade_opportunities()
        elif choice == "6":
            return
        else:
            print("Invalid choice.")
            input("\nPress Enter to continue...")
            self.trade_menu()

    def buy_commodities(self):
        print("\n" + "="*60)
        print("           BUY COMMODITIES")
        print("="*60)
        
        all_items = []
        for category, items in commodities.items():
            all_items.extend(items)
        
        print("Available items:")
        for i, item in enumerate(all_items, 1):
            print(f"{i}. {item['name']} - {item['value']} credits")
        
        try:
            item_choice = int(input("\nSelect item number: ")) - 1
            if 0 <= item_choice < len(all_items):
                item = all_items[item_choice]
                quantity = int(input(f"How many {item['name']} to buy? "))
                total_cost = item['value'] * quantity
                
                if total_cost <= self.credits:
                    self.credits -= total_cost
                    if item['name'] in self.inventory:
                        self.inventory[item['name']] += quantity
                    else:
                        self.inventory[item['name']] = quantity
                    print(f"\nPurchased {quantity} {item['name']} for {total_cost} credits.")
                else:
                    print(f"\nInsufficient credits. Need {total_cost}, have {self.credits}.")
            else:
                print("Invalid item selection.")
        except ValueError:
            print("Invalid input.")
        
        input("\nPress Enter to continue...")

    def sell_commodities(self):
        print("\n" + "="*60)
        print("           SELL COMMODITIES")
        print("="*60)
        
        if not self.inventory:
            print("No items to sell.")
            input("\nPress Enter to continue...")
            return
        
        items = list(self.inventory.items())
        print("Your inventory:")
        for i, (item, quantity) in enumerate(items, 1):
            # Find item value
            item_value = 0
            for category, commodity_list in commodities.items():
                for commodity in commodity_list:
                    if commodity['name'] == item:
                        item_value = commodity['value']
                        break
            print(f"{i}. {item} (Qty: {quantity}) - {item_value} credits each")
        
        try:
            item_choice = int(input("\nSelect item number: ")) - 1
            if 0 <= item_choice < len(items):
                item_name, available_qty = items[item_choice]
                quantity = int(input(f"How many {item_name} to sell? (Available: {available_qty}): "))
                
                if quantity <= available_qty:
                    # Find item value
                    item_value = 0
                    for category, commodity_list in commodities.items():
                        for commodity in commodity_list:
                            if commodity['name'] == item_name:
                                item_value = commodity['value']
                                break
                    
                    total_value = item_value * quantity
                    self.credits += total_value
                    self.inventory[item_name] -= quantity
                    if self.inventory[item_name] == 0:
                        del self.inventory[item_name]
                    
                    print(f"\nSold {quantity} {item_name} for {total_value} credits.")
                else:
                    print(f"You only have {available_qty} {item_name}.")
            else:
                print("Invalid item selection.")
        except ValueError:
            print("Invalid input.")
        
        input("\nPress Enter to continue...")

    def view_market(self, system_name):
        """View current market prices and availability"""
        print("\n" + "="*60)
        print(f"           MARKET - {system_name}")
        print("="*60)
        
        market_info = self.economy.get_market_info(system_name)
        if not market_info:
            print("No market data available.")
            input("\nPress Enter to continue...")
            return
        
        market = market_info['market']
        
        print(f"System Type: {market['system_type']}")
        print(f"Population: {market['population']:,}")
        print(f"Resources: {market['resources']}")
        
        print("\nBEST BUYING OPPORTUNITIES:")
        if market_info['best_buys']:
            for commodity, price, supply in market_info['best_buys']:
                print(f"  {commodity}: {price:,} credits (Supply: {supply})")
        else:
            print("  No good buying opportunities")
        
        print("\nBEST SELLING OPPORTUNITIES:")
        if market_info['best_sells']:
            for commodity, price, demand in market_info['best_sells']:
                print(f"  {commodity}: {price:,} credits (Demand: {demand})")
        else:
            print("  No good selling opportunities")
        
        input("\nPress Enter to continue...")

    def buy_commodities_new(self, system_name):
        """Buy commodities using the new economic system"""
        print("\n" + "="*60)
        print(f"           BUY COMMODITIES - {system_name}")
        print("="*60)
        
        market_info = self.economy.get_market_info(system_name)
        if not market_info:
            print("No market available.")
            input("\nPress Enter to continue...")
            return
        
        market = market_info['market']
        
        # Show available commodities with supply > 0
        available_commodities = []
        for commodity, supply in market['supply'].items():
            if supply > 0:
                price = market['prices'][commodity]
                available_commodities.append((commodity, price, supply))
        
        available_commodities.sort(key=lambda x: x[1])  # Sort by price
        
        if not available_commodities:
            print("No commodities available for purchase.")
            input("\nPress Enter to continue...")
            return
        
        print("Available commodities:")
        for i, (commodity, price, supply) in enumerate(available_commodities[:20], 1):
            print(f"{i:2d}. {commodity:<25} - {price:,} credits (Supply: {supply})")
        
        try:
            choice = int(input("\nSelect commodity number: ")) - 1
            if 0 <= choice < len(available_commodities):
                commodity, price, supply = available_commodities[choice]
                
                print(f"\nSelected: {commodity}")
                print(f"Price: {price:,} credits each")
                print(f"Available: {supply}")
                print(f"Your credits: {self.credits:,}")
                
                max_affordable = self.credits // price
                max_buyable = min(max_affordable, supply)
                
                if max_buyable == 0:
                    print("You cannot afford any of this commodity.")
                    input("\nPress Enter to continue...")
                    return
                
                print(f"You can buy up to {max_buyable}")
                
                quantity = int(input(f"How many to buy? (0-{max_buyable}): "))
                
                if 0 < quantity <= max_buyable:
                    success, message = self.economy.buy_commodity(system_name, commodity, quantity, self.credits)
                    
                    if success:
                        cost = quantity * price
                        self.credits -= cost
                        
                        if commodity in self.inventory:
                            self.inventory[commodity] += quantity
                        else:
                            self.inventory[commodity] = quantity
                        
                        # Faction reputation bonus for trade
                        if self.navigation.current_ship:
                            coords = self.navigation.current_ship.coordinates
                            faction = self.faction_system.get_system_faction(coords)
                            if faction:
                                rep_change = max(1, quantity // 10)  # 1 rep per 10 units
                                result = self.faction_system.modify_reputation(faction, rep_change, "trade")
                                print(f"Faction Relations: {result}")
                        
                        # Profession experience for trading
                        trade_xp = max(5, quantity // 5)  # 5-20+ XP based on quantity
                        if self.profession_system.character_profession == "Interstellar Trade Broker":
                            xp_result = self.profession_system.gain_experience("Interstellar Trade Broker", trade_xp * 2, "major trade")
                            print(f"Professional Development: {xp_result}")
                        elif self.profession_system.character_profession == "Intergalactic Trader":
                            xp_result = self.profession_system.gain_experience("Intergalactic Trader", trade_xp * 2, "trade transaction")
                            print(f"Professional Development: {xp_result}")
                        else:
                            # Generic trade experience for any profession
                            if self.profession_system.character_profession:
                                xp_result = self.profession_system.gain_experience(self.profession_system.character_profession, trade_xp, "trade activity")
                                print(f"Professional Development: {xp_result}")
                        
                        print(f"\n{message}")
                    else:
                        print(f"\nTrade failed: {message}")
                elif quantity == 0:
                    print("Purchase cancelled.")
                else:
                    print("Invalid quantity.")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")
        
        input("\nPress Enter to continue...")

    def sell_commodities_new(self, system_name):
        """Sell commodities using the new economic system"""
        print("\n" + "="*60)
        print(f"           SELL COMMODITIES - {system_name}")
        print("="*60)
        
        if not self.inventory:
            print("No commodities to sell.")
            input("\nPress Enter to continue...")
            return
        
        market_info = self.economy.get_market_info(system_name)
        if not market_info:
            print("No market available.")
            input("\nPress Enter to continue...")
            return
        
        market = market_info['market']
        
        # Show player's commodities and market demand/prices
        sellable_items = []
        for commodity, quantity in self.inventory.items():
            if commodity in market['demand'] and market['demand'][commodity] > 0:
                price = market['prices'][commodity]
                demand = market['demand'][commodity]
                sellable_items.append((commodity, quantity, price, demand))
        
        if not sellable_items:
            print("No market demand for your commodities at this location.")
            input("\nPress Enter to continue...")
            return
        
        sellable_items.sort(key=lambda x: x[2], reverse=True)  # Sort by price (descending)
        
        print("Your commodities with market demand:")
        for i, (commodity, quantity, price, demand) in enumerate(sellable_items, 1):
            max_sellable = min(quantity, demand)
            print(f"{i:2d}. {commodity:<25} - {price:,} credits (You have: {quantity}, Demand: {demand})")
        
        try:
            choice = int(input("\nSelect commodity number: ")) - 1
            if 0 <= choice < len(sellable_items):
                commodity, owned_qty, price, demand = sellable_items[choice]
                
                print(f"\nSelected: {commodity}")
                print(f"Price: {price:,} credits each")
                print(f"You have: {owned_qty}")
                print(f"Market demand: {demand}")
                
                max_sellable = min(owned_qty, demand)
                print(f"You can sell up to {max_sellable}")
                
                quantity = int(input(f"How many to sell? (0-{max_sellable}): "))
                
                if 0 < quantity <= max_sellable:
                    success, message, credits_earned = self.economy.sell_commodity(
                        system_name, commodity, quantity, self.inventory
                    )
                    
                    if success:
                        self.credits += credits_earned
                        self.inventory[commodity] -= quantity
                        if self.inventory[commodity] == 0:
                            del self.inventory[commodity]
                        
                        print(f"\n{message}")
                    else:
                        print(f"\nTrade failed: {message}")
                elif quantity == 0:
                    print("Sale cancelled.")
                else:
                    print("Invalid quantity.")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")
        
        input("\nPress Enter to continue...")

    def market_analysis(self, system_name):
        """Show detailed market analysis"""
        print("\n" + "="*60)
        print(f"           MARKET ANALYSIS - {system_name}")
        print("="*60)
        
        market_info = self.economy.get_market_info(system_name)
        if not market_info:
            print("No market data available.")
            input("\nPress Enter to continue...")
            return
        
        market = market_info['market']
        
        print(f"System: {system_name}")
        print(f"Type: {market['system_type']}")
        print(f"Population: {market['population']:,}")
        print(f"Resources: {market['resources']}")
        
        print("\nPRODUCTION (What this system makes):")
        if market['production']:
            for commodity, rate in market['production'].items():
                supply = market['supply'][commodity]
                price = market['prices'][commodity]
                print(f"  {commodity}: {rate}/cycle (Current supply: {supply}, Price: {price:,})")
        else:
            print("  No major production")
        
        print("\nCONSUMPTION (What this system needs):")
        if market['consumption']:
            for commodity, rate in market['consumption'].items():
                demand = market['demand'][commodity]
                price = market['prices'][commodity]
                print(f"  {commodity}: {rate}/cycle (Current demand: {demand}, Price: {price:,})")
        else:
            print("  No major consumption")
        
        # Show recent economic events
        if self.economy.global_events:
            print("\nRECENT ECONOMIC EVENTS:")
            for event in self.economy.global_events[-3:]:
                print(f"  • {event['name']}: {event['description']}")
        
        input("\nPress Enter to continue...")

    def trade_opportunities(self):
        """Show profitable trade routes"""
        print("\n" + "="*60)
        print("           TRADE OPPORTUNITIES")
        print("="*60)
        
        opportunities = self.economy.get_trade_opportunities()
        
        if not opportunities:
            print("No profitable trade opportunities found.")
            input("\nPress Enter to continue...")
            return
        
        print("Most profitable trade routes:")
        print(f"{'Commodity':<20} {'From':<15} {'To':<15} {'Buy':<8} {'Sell':<8} {'Profit':<8}")
        print("-" * 80)
        
        for opp in opportunities[:15]:
            print(f"{opp['commodity']:<20} {opp['source'][:14]:<15} {opp['destination'][:14]:<15} "
                  f"{opp['buy_price']:<8,} {opp['sell_price']:<8,} {opp['profit_margin']:<7.1f}%")
        
        print("\nNote: Prices change based on supply and demand.")
        print("Trade routes may no longer be profitable by the time you arrive!")
        
        input("\nPress Enter to continue...")

    def purchase_menu(self):
        print("\n" + "="*60)
        print("           PURCHASE ASSETS")
        print("="*60)
        
        print("1. Purchase Ships")
        print("2. Purchase Space Stations")
        print("3. Purchase Manufacturing Platforms")
        print("4. Back to Main Menu")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            self.purchase_ships()
        elif choice == "2":
            self.purchase_stations()
        elif choice == "3":
            self.purchase_platforms()
        elif choice == "4":
            return
        else:
            print("Invalid choice.")
            input("\nPress Enter to continue...")
            self.purchase_menu()

    def purchase_ships(self):
        print("\n" + "="*60)
        print("           PURCHASE SHIPS")
        print("="*60)
        
        ship_list = list(ship_classes.items())
        for i, (name, info) in enumerate(ship_list, 1):
            # Base price calculation based on ship class
            base_prices = {
                "Starter Vessel": 25000,
                "Freighter": 50000,
                "Light Cruiser": 100000,
                "Stealth Frigate": 150000,
                "Exploration Vessel": 80000,
                "Deep Space Probe": 60000,
                "Survey Ship": 70000
            }
            price = base_prices.get(info["Class"], 100000)
            print(f"{i}. {name} ({info['Class']}) - {price:,} credits")
        
        try:
            choice = int(input("\nSelect ship number: ")) - 1
            if 0 <= choice < len(ship_list):
                ship_name, ship_info = ship_list[choice]
                base_prices = {
                    "Starter Vessel": 25000,
                    "Freighter": 50000,
                    "Light Cruiser": 100000,
                    "Stealth Frigate": 150000,
                    "Exploration Vessel": 80000,
                    "Deep Space Probe": 60000,
                    "Survey Ship": 70000
                }
                price = base_prices.get(ship_info["Class"], 100000)
                
                if price <= self.credits:
                    self.credits -= price
                    self.owned_ships.append(ship_name)
                    print(f"\nPurchased {ship_name} for {price:,} credits!")
                else:
                    print(f"\nInsufficient credits. Need {price:,}, have {self.credits:,}.")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")
        
        input("\nPress Enter to continue...")

    def purchase_stations(self):
        print("\n" + "="*60)
        print("           PURCHASE SPACE STATIONS")
        print("="*60)
        
        station_list = list(space_stations.items())
        for i, (name, info) in enumerate(station_list, 1):
            # Base price calculation
            price = 500000  # All stations cost 500k for simplicity
            print(f"{i}. {name} ({info['type']}) - {price:,} credits")
        
        try:
            choice = int(input("\nSelect station number: ")) - 1
            if 0 <= choice < len(station_list):
                station_name, station_info = station_list[choice]
                price = 500000
                
                if price <= self.credits:
                    self.credits -= price
                    self.owned_stations.append(station_name)
                    print(f"\nPurchased {station_name} for {price:,} credits!")
                else:
                    print(f"\nInsufficient credits. Need {price:,}, have {self.credits:,}.")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")
        
        input("\nPress Enter to continue...")

    def purchase_platforms(self):
        print("\n" + "="*60)
        print("           PURCHASE MANUFACTURING PLATFORMS")
        print("="*60)
        
        platform_list = list(industrial_platforms.items())
        for i, (name, info) in enumerate(platform_list, 1):
            price = 250000  # All platforms cost 250k for simplicity
            print(f"{i}. {name} ({info['type']}) - {price:,} credits")
        
        try:
            choice = int(input("\nSelect platform number: ")) - 1
            if 0 <= choice < len(platform_list):
                platform_name, platform_info = platform_list[choice]
                price = 250000
                
                if price <= self.credits:
                    self.credits -= price
                    self.owned_platforms.append(platform_name)
                    print(f"\nPurchased {platform_name} for {price:,} credits!")
                else:
                    print(f"\nInsufficient credits. Need {price:,}, have {self.credits:,}.")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")
        
        input("\nPress Enter to continue...")

    def save_and_exit(self):
        # Stop bot updates
        self.stop_bot_updates()
        
        print("\nThank you for playing Galactic Empire Management!")
        print("Your progress has been saved.")
        print("\nMay the stars guide your journey, Commander!")

    def character_creation(self):
        print("\n" + "="*60)
        print("           CHARACTER CREATION")
        print("="*60)
        
        # Choose character class
        print("\nSelect your character class:")
        classes = list(character_classes.keys())
        for i, char_class in enumerate(classes, 1):
            info = character_classes[char_class]
            print(f"{i}. {char_class}")
            print(f"   {info['description']}")
            print(f"   Starting Credits: {info['starting_credits']:,}")
            print(f"   Skills: {', '.join(info['skills'])}")
            print()
        
        try:
            choice = int(input("Enter class number: ")) - 1
            if 0 <= choice < len(classes):
                self.character_class = classes[choice]
                class_info = character_classes[self.character_class]
                
                # Apply class bonuses
                self.credits = class_info["starting_credits"]
                
                # Add starting ships
                if "starting_ships" in class_info:
                    self.owned_ships.extend(class_info["starting_ships"])
                
                # Add starting platforms
                if "starting_platforms" in class_info:
                    self.owned_platforms.extend(class_info["starting_platforms"])
                
                # Add starting stations
                if "starting_stations" in class_info:
                    self.owned_stations.extend(class_info["starting_stations"])
                
                print(f"\nSelected: {self.character_class}")
            else:
                print("Invalid selection.")
                return self.character_creation()
        except ValueError:
            print("Invalid input.")
            return self.character_creation()
        
        # Choose background
        print("\nSelect your background:")
        backgrounds = list(character_backgrounds.keys())
        for i, background in enumerate(backgrounds, 1):
            info = character_backgrounds[background]
            print(f"{i}. {background}")
            print(f"   {info['description']}")
            print(f"   Traits: {', '.join(info['traits'])}")
            print()
        
        try:
            choice = int(input("Enter background number: ")) - 1
            if 0 <= choice < len(backgrounds):
                self.character_background = backgrounds[choice]
                bg_info = character_backgrounds[self.character_background]
                
                # Apply background bonuses
                if "credit_bonus" in bg_info:
                    self.credits += bg_info["credit_bonus"]
                elif "credit_penalty" in bg_info:
                    self.credits += bg_info["credit_penalty"]  # Already negative
                
                print(f"\nSelected: {self.character_background}")
            else:
                print("Invalid selection.")
                return self.character_creation()
        except ValueError:
            print("Invalid input.")
            return self.character_creation()
        
        # Profession selection
        self.select_profession()
        
        # Generate character stats
        self.character_stats = create_character_stats()
        
        # Ensure every character has at least a basic ship
        if not self.owned_ships:
            self.owned_ships.append("Basic Transport")
            print("\nYou've been assigned a Basic Transport as your starter ship.")
        
        print(f"\nCharacter created successfully!")
        print(f"Final starting credits: {self.credits:,}")
        print(f"Starting ships: {', '.join(self.owned_ships)}")
        if hasattr(self.profession_system, 'character_profession') and self.profession_system.character_profession:
            print(f"Profession: {self.profession_system.character_profession}")
        input("\nPress Enter to continue...")

    def select_profession(self):
        """Select character profession during creation"""
        from professions import professions, profession_categories
        
        print("\n" + "="*60)
        print("           PROFESSION SELECTION")
        print("="*60)
        print("Choose your character's profession:")
        
        # Display by categories
        all_profs = []
        for category, prof_list in profession_categories.items():
            print(f"\n[{category.upper()}]")
            print("-" * (len(category) + 2))
            
            for prof_name in prof_list:
                if prof_name in professions:
                    prof_num = len(all_profs) + 1
                    all_profs.append(prof_name)
                    prof_info = professions[prof_name]
                    print(f"{prof_num:2d}. {prof_name}")
                    print(f"    {prof_info['description']}")
        
        # Add remaining professions not in categories
        remaining_profs = [p for p in professions.keys() if p not in all_profs]
        if remaining_profs:
            print(f"\n[OTHER PROFESSIONS]")
            print("-" * 18)
            for prof_name in remaining_profs:
                prof_num = len(all_profs) + 1
                all_profs.append(prof_name)
                prof_info = professions[prof_name]
                print(f"{prof_num:2d}. {prof_name}")
                print(f"    {prof_info['description']}")
        
        try:
            choice = int(input(f"\nSelect profession (1-{len(all_profs)}): ")) - 1
            if 0 <= choice < len(all_profs):
                selected_profession = all_profs[choice]
                success = self.profession_system.assign_profession(selected_profession)
                
                if success:
                    prof_info = professions[selected_profession]
                    print(f"\nSelected: {selected_profession}")
                    print(f"Category: {prof_info['category']}")
                    print(f"Requirements: {', '.join(prof_info['requirements'])}")
                    
                    # Give starting benefits
                    benefits = self.profession_system.get_profession_bonuses(selected_profession)
                    if benefits:
                        print(f"Starting Benefits: {', '.join(benefits[:2])}")  # Show first 2
                else:
                    print("Error assigning profession.")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input. Skipping profession selection.")

    def character_profile(self):
        print("\n" + "="*60)
        print("           CHARACTER PROFILE")
        print("="*60)
        
        if not self.character_class:
            print("No character created yet.")
            create_now = input("\nWould you like to create a character now? (y/n): ").lower()
            if create_now == 'y':
                self.character_creation()
            return
        
        print(f"Commander: {self.player_name}")
        print(f"Class: {self.character_class}")
        print(f"Background: {self.character_background}")
        print(f"Credits: {self.credits:,}")
        
        # Show profession info
        if self.profession_system.character_profession:
            prof_level = self.profession_system.profession_levels.get(self.profession_system.character_profession, 1)
            prof_xp = self.profession_system.profession_experience.get(self.profession_system.character_profession, 0)
            print(f"Profession: {self.profession_system.character_profession} (Level {prof_level})")
            print(f"Professional Experience: {prof_xp} XP")
            
            # Show active benefits
            benefits = self.profession_system.get_profession_bonuses(self.profession_system.character_profession)
            if benefits:
                print(f"Active Benefits: {len(benefits)} skills unlocked")
        else:
            print(f"Profession: None assigned")
        
        print("\nCHARACTER STATISTICS:")
        for stat, value in self.character_stats.items():
            print(f"  {stat.title()}: {value}/10")
        
        print("\nCLASS ABILITIES:")
        class_info = character_classes[self.character_class]
        for skill in class_info['skills']:
            print(f"  • {skill}")
        
        print("\nBACKGROUND TRAITS:")
        bg_info = character_backgrounds[self.character_background]
        for trait in bg_info['traits']:
            print(f"  • {trait}")
        
        input("\nPress Enter to return to main menu...")

    def galactic_history_menu(self):
        """Galactic History and Archaeology menu interface"""
        while True:
            print("\n" + "="*60)
            print("           GALACTIC HISTORY & ARCHAEOLOGY")
            print("="*60)
            
            print("1. View Ancient Civilizations")
            print("2. Browse Historical Timeline")
            print("3. Archaeological Site Scanner")
            print("4. Excavate at Current Location")
            print("5. Discovered Artifacts")
            print("6. Archaeological Research")
            print("7. Back to Main Menu")
            
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == "1":
                self.view_ancient_civilizations()
            elif choice == "2":
                self.browse_historical_timeline()
            elif choice == "3":
                self.archaeological_site_scanner()
            elif choice == "4":
                self.excavate_current_location()
            elif choice == "5":
                self.view_discovered_artifacts()
            elif choice == "6":
                self.archaeological_research()
            elif choice == "7":
                break
            else:
                print("Invalid choice. Please try again.")
                input("\nPress Enter to continue...")

    def view_ancient_civilizations(self):
        """Display information about ancient civilizations"""
        print("\n" + "="*60)
        print("           ANCIENT CIVILIZATIONS DATABASE")
        print("="*60)
        
        civilizations = self.galactic_history.ancient_civilizations
        
        for i, (name, data) in enumerate(civilizations.items(), 1):
            print(f"\n{i}. {name}")
            print(f"   Era: {data['era']}")
            print(f"   Technology Focus: {data['technology_focus']}")
            print(f"   {data['description'][:100]}...")
            
            # Show discovery status
            if data.get('discovered', False):
                artifacts = len(data.get('discovered_artifacts', []))
                print(f"   Status: DISCOVERED ({artifacts} artifacts found)")
            else:
                print(f"   Status: Unknown civilization")
        
        print(f"\nTotal: {len(civilizations)} ancient civilizations in database")
        
        # Allow detailed view
        try:
            choice = input(f"\nView details for civilization (1-{len(civilizations)}) or Enter to return: ").strip()
            if choice:
                choice = int(choice) - 1
                if 0 <= choice < len(civilizations):
                    civ_name = list(civilizations.keys())[choice]
                    self.view_civilization_details(civ_name)
        except (ValueError, IndexError):
            pass
        
        input("\nPress Enter to continue...")

    def view_civilization_details(self, civilization_name):
        """Show detailed information about a specific ancient civilization"""
        civ_data = self.galactic_history.ancient_civilizations.get(civilization_name)
        if not civ_data:
            print("Civilization not found.")
            return
        
        print("\n" + "="*60)
        print(f"           {civilization_name.upper()}")
        print("="*60)
        
        print(f"Era: {civ_data['era']}")
        print(f"Technology Focus: {civ_data['technology_focus']}")
        print(f"\nDescription:")
        print(f"{civ_data['description']}")
        
        print(f"\nRemnant Type:")
        print(f"  • {civ_data['remnant_type']}")
        
        print(f"\nArchaeological Value: {civ_data['archaeological_value']}")
        
        if civ_data.get('discovered', False):
            print(f"\nDISCOVERY STATUS: CONFIRMED")
            artifacts = civ_data.get('discovered_artifacts', [])
            if artifacts:
                print(f"Discovered Artifacts ({len(artifacts)}):")
                for artifact in artifacts:
                    print(f"  • {artifact}")
            
            sites = civ_data.get('known_sites', [])
            if sites:
                print(f"Known Archaeological Sites ({len(sites)}):")
                for site in sites:
                    coords = site['coordinates']
                    print(f"  • {site['name']} at ({coords[0]}, {coords[1]}, {coords[2]})")
        else:
            print(f"\nDISCOVERY STATUS: THEORETICAL")
            print("No confirmed archaeological evidence found yet.")

    def browse_historical_timeline(self):
        """Browse the galactic historical timeline"""
        print("\n" + "="*60)
        print("           GALACTIC HISTORICAL TIMELINE")
        print("="*60)
        
        timeline_data = []
        for year, events in sorted(self.galactic_history.timeline.items()):
            for event in events:
                timeline_data.append({
                    'year': year,
                    'event': event['description'],
                    'civilization': event.get('civilization', '')
                })
        
        print("Major Historical Events:")
        for event in timeline_data:
            print(f"\n{event['year']:>6} GY: {event['event']}")
            if event.get('civilization'):
                print(f"        Related to: {event['civilization']}")
        
        print(f"\nGY = Galactic Years (years since galactic standardization)")
        input("\nPress Enter to continue...")

    def archaeological_site_scanner(self):
        """Scan for archaeological sites in the current area"""
        if not self.navigation.current_ship:
            print("\nNo ship selected! Use Navigation -> Select Ship first.")
            input("\nPress Enter to continue...")
            return
        
        print("\n" + "="*60)
        print("           ARCHAEOLOGICAL SITE SCANNER")
        print("="*60)
        
        x, y, z = self.navigation.current_ship.coordinates
        nearby_sites = self.galactic_history.get_archaeological_sites_near(x, y, z, radius=5)
        
        if not nearby_sites:
            print("No archaeological sites detected within scanner range (5 units).")
            print("Try moving to different star systems or expanding your search radius.")
        else:
            print(f"Detected {len(nearby_sites)} archaeological site(s) nearby:")
            
            for i, site in enumerate(nearby_sites, 1):
                coords = site['coordinates']
                distance = ((x - coords[0])**2 + (y - coords[1])**2 + (z - coords[2])**2)**0.5
                
                print(f"\n{i}. {site['name']}")
                print(f"   Civilization: {site['civilization']}")
                print(f"   Type: {site['type']}")
                print(f"   Distance: {distance:.1f} units")
                print(f"   Coordinates: ({coords[0]}, {coords[1]}, {coords[2]})")
                
                if site.get('excavated', False):
                    print(f"   Status: EXCAVATED")
                else:
                    print(f"   Status: Unexplored")
        
        input("\nPress Enter to continue...")

    def excavate_current_location(self):
        """Attempt archaeological excavation at current location"""
        if not self.navigation.current_ship:
            print("\nNo ship selected! Use Navigation -> Select Ship first.")
            input("\nPress Enter to continue...")
            return
        
        x, y, z = self.navigation.current_ship.coordinates
        result = self.galactic_history.excavate_site(x, y, z)
        
        print("\n" + "="*60)
        print("           ARCHAEOLOGICAL EXCAVATION")
        print("="*60)
        
        print(f"Excavation at coordinates ({x}, {y}, {z})")
        print(f"Result: {result}")
        
        input("\nPress Enter to continue...")

    def view_discovered_artifacts(self):
        """View all discovered artifacts"""
        print("\n" + "="*60)
        print("           DISCOVERED ARTIFACTS")
        print("="*60)
        
        artifacts = self.galactic_history.get_discovered_artifacts()
        
        if not artifacts:
            print("No artifacts discovered yet.")
            print("Explore archaeological sites to find ancient relics!")
        else:
            total_count = 0
            for civ_name, civ_artifacts in artifacts.items():
                if civ_artifacts:
                    print(f"\n{civ_name}:")
                    for artifact in civ_artifacts:
                        print(f"  • {artifact}")
                        total_count += 1
            
            print(f"\nTotal artifacts discovered: {total_count}")
        
        input("\nPress Enter to continue...")

    def archaeological_research(self):
        """Research interface for analyzing artifacts and sites"""
        print("\n" + "="*60)
        print("           ARCHAEOLOGICAL RESEARCH")
        print("="*60)
        
        artifacts = self.galactic_history.get_discovered_artifacts()
        total_artifacts = sum(len(arts) for arts in artifacts.values())
        
        if total_artifacts == 0:
            print("No artifacts to research yet.")
            print("Discover artifacts through excavation to unlock research.")
            input("\nPress Enter to continue...")
            return
        
        print(f"Available for Research: {total_artifacts} artifacts")
        print("\nResearch unlocks:")
        print("• Detailed civilization information")
        print("• Advanced archaeological scanning")
        print("• Historical technology blueprints")
        print("• Ancient navigation charts")
        
        print("\n[RESEARCH SYSTEM - Coming Soon]")
        print("This feature will allow you to study discovered artifacts")
        print("to unlock new technologies and historical insights.")
        
        input("\nPress Enter to continue...")

    def ship_builder_menu(self):
        print("\n" + "="*60)
        print("           SHIP BUILDER")
        print("="*60)
        
        print("1. Build Custom Ship")
        print("2. Use Ship Template")
        print("3. View Ship Components")
        print("4. View Your Custom Ships")
        print("5. Back to Main Menu")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            self.build_custom_ship()
        elif choice == "2":
            self.use_ship_template()
        elif choice == "3":
            self.view_ship_components()
        elif choice == "4":
            self.view_custom_ships()
        elif choice == "5":
            return
        else:
            print("Invalid choice.")
            input("\nPress Enter to continue...")
            self.ship_builder_menu()

    def build_custom_ship(self):
        print("\n" + "="*60)
        print("           BUILD CUSTOM SHIP")
        print("="*60)
        
        ship_design = {}
        
        # Choose hull
        print("Select Hull Type:")
        hulls = list(ship_components["Hull Types"].items())
        for i, (name, info) in enumerate(hulls, 1):
            print(f"{i}. {name} - {info['cost']:,} credits")
            print(f"   {info['description']}")
        
        try:
            choice = int(input("\nEnter hull number: ")) - 1
            if 0 <= choice < len(hulls):
                ship_design["hull"] = hulls[choice][0]
            else:
                print("Invalid selection.")
                return
        except ValueError:
            print("Invalid input.")
            return
        
        # Choose engine
        print("\nSelect Engine:")
        engines = list(ship_components["Engines"].items())
        for i, (name, info) in enumerate(engines, 1):
            print(f"{i}. {name} - {info['cost']:,} credits")
            print(f"   {info['description']}")
        
        try:
            choice = int(input("\nEnter engine number: ")) - 1
            if 0 <= choice < len(engines):
                ship_design["engine"] = engines[choice][0]
            else:
                print("Invalid selection.")
                return
        except ValueError:
            print("Invalid input.")
            return
        
        # Choose shields
        print("\nSelect Shields:")
        shields = list(ship_components["Shields"].items())
        for i, (name, info) in enumerate(shields, 1):
            print(f"{i}. {name} - {info['cost']:,} credits")
            print(f"   {info['description']}")
        
        try:
            choice = int(input("\nEnter shield number: ")) - 1
            if 0 <= choice < len(shields):
                ship_design["shields"] = shields[choice][0]
            else:
                print("Invalid selection.")
                return
        except ValueError:
            print("Invalid input.")
            return
        
        # Calculate stats and cost
        stats = calculate_ship_stats(ship_design)
        
        print(f"\nShip Design Summary:")
        print(f"Hull: {ship_design['hull']}")
        print(f"Engine: {ship_design['engine']}")
        print(f"Shields: {ship_design['shields']}")
        print(f"\nEstimated Stats:")
        print(f"Health: {stats['health']}")
        print(f"Cargo Space: {stats['cargo_space']}")
        print(f"Speed Modifier: {stats['speed']:.1f}x")
        print(f"Total Cost: {stats['total_cost']:,} credits")
        
        if stats['total_cost'] > self.credits:
            print(f"\nInsufficient credits! You need {stats['total_cost'] - self.credits:,} more credits.")
            input("\nPress Enter to continue...")
            return
        
        ship_name = input("\nEnter ship name: ").strip()
        if not ship_name:
            ship_name = f"Custom Ship {len(self.custom_ships) + 1}"
        
        ship_role = input("Enter ship role/purpose: ").strip()
        if not ship_role:
            ship_role = "Multi-purpose"
        
        confirm = input(f"\nBuild {ship_name} for {stats['total_cost']:,} credits? (y/n): ")
        if confirm.lower() == 'y':
            self.credits -= stats['total_cost']
            
            custom_ship = {
                "name": ship_name,
                "role": ship_role,
                "design": ship_design,
                "stats": stats
            }
            
            self.custom_ships.append(custom_ship)
            print(f"\n{ship_name} built successfully!")
        
        input("\nPress Enter to continue...")

    def use_ship_template(self):
        print("\n" + "="*60)
        print("           SHIP TEMPLATES")
        print("="*60)
        
        templates = list(ship_templates.items())
        for i, (name, info) in enumerate(templates, 1):
            print(f"{i}. {name} - {info['total_cost']:,} credits")
            print(f"   Role: {info['role']}")
            print(f"   Components: Hull({info['hull']}), Engine({info['engine']})")
            print()
        
        try:
            choice = int(input("Select template number: ")) - 1
            if 0 <= choice < len(templates):
                template_name, template_info = templates[choice]
                
                if template_info['total_cost'] > self.credits:
                    print(f"\nInsufficient credits! Need {template_info['total_cost']:,}, have {self.credits:,}")
                    input("\nPress Enter to continue...")
                    return
                
                ship_name = input(f"\nEnter name for your {template_name}: ").strip()
                if not ship_name:
                    ship_name = f"My {template_name}"
                
                confirm = input(f"\nBuild {ship_name} for {template_info['total_cost']:,} credits? (y/n): ")
                if confirm.lower() == 'y':
                    self.credits -= template_info['total_cost']
                    
                    # Calculate stats for template
                    stats = calculate_ship_stats(template_info)
                    
                    custom_ship = {
                        "name": ship_name,
                        "role": template_info['role'],
                        "design": template_info,
                        "stats": stats
                    }
                    
                    self.custom_ships.append(custom_ship)
                    print(f"\n{ship_name} built successfully!")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")
        
        input("\nPress Enter to continue...")

    def view_ship_components(self):
        print("\n" + "="*60)
        print("           SHIP COMPONENTS")
        print("="*60)
        
        for category, components in ship_components.items():
            print(f"\n[{category.upper()}]")
            print("-" * (len(category) + 2))
            for name, info in components.items():
                print(f"• {name} - {info['cost']:,} credits")
                print(f"  {info['description']}")
                print()
        
        input("\nPress Enter to continue...")

    def view_custom_ships(self):
        print("\n" + "="*60)
        print("           YOUR CUSTOM SHIPS")
        print("="*60)
        
        if not self.custom_ships:
            print("No custom ships built yet.")
            input("\nPress Enter to continue...")
            return
        
        for i, ship in enumerate(self.custom_ships, 1):
            print(f"{i}. {ship['name']}")
            print(f"   Role: {ship['role']}")
            print(f"   Health: {ship['stats']['health']}")
            print(f"   Cargo: {ship['stats']['cargo_space']}")
            print(f"   Speed: {ship['stats']['speed']:.1f}x")
            print(f"   Value: {ship['stats']['total_cost']:,} credits")
            print()
        
        input("\nPress Enter to continue...")

    def trigger_economic_event(self):
        """Trigger a random economic event"""
        event = self.economy.create_economic_event()
        
        print("\n" + "!"*60)
        print("           BREAKING NEWS")
        print("!"*60)
        print(f"EVENT: {event['name']}")
        print(f"{event['description']}")
        print("This may affect markets across the galaxy!")
        print("!"*60)
        
        self.economy.apply_economic_event(event)
        input("\nPress Enter to continue...")

    def ship_upgrade_menu(self):
        """Ship upgrade interface"""
        if not self.navigation.current_ship:
            print("\nNo ship selected! Use Navigation -> Select Ship first.")
            input("\nPress Enter to continue...")
            return
        
        # Check if at a station that offers upgrades
        x, y, z = self.navigation.current_ship.coordinates
        station = None
        if self.station_manager:
            station = self.station_manager.get_station_at_location((x, y, z))
        
        if not station or "Ship Upgrades" not in station.get('services', []):
            print("\nShip upgrades are only available at certain space stations.")
            print("Look for Research Labs, Military Bases, or Shipyards.")
            input("\nPress Enter to continue...")
            return
        
        while True:
            print("\n" + "="*60)
            print(f"           SHIP UPGRADES - {station['name']}")
            print("="*60)
            
            current_ship = self.navigation.current_ship
            print(f"Current Ship: {current_ship.name} ({current_ship.ship_class})")
            print(f"Credits: {self.credits:,}")
            
            # Show current upgrades
            if hasattr(current_ship, 'upgrades') and current_ship.upgrades:
                print("\nInstalled Upgrades:")
                for upgrade_name in current_ship.upgrades:
                    print(f"  • {upgrade_name}")
            else:
                print("\nNo upgrades installed")
            
            print("\nAVAILABLE UPGRADES:")
            print("1. View Upgrade Categories")
            print("2. Install Upgrade")
            print("3. Ship Status")
            print("4. Back to Main Menu")
            
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == "1":
                self.view_upgrade_categories()
            elif choice == "2":
                self.install_ship_upgrade()
            elif choice == "3":
                self.show_detailed_ship_status()
            elif choice == "4":
                break
            else:
                print("Invalid choice.")
                input("\nPress Enter to continue...")

    def view_upgrade_categories(self):
        """Show available upgrade categories"""
        print("\n" + "="*60)
        print("           UPGRADE CATEGORIES")
        print("="*60)
        
        current_ship = self.navigation.current_ship
        available = self.upgrade_system.get_available_upgrades(current_ship)
        
        for category, upgrades in available.items():
            if upgrades:  # Only show categories with available upgrades
                print(f"\n[{category.upper()}]")
                print("-" * (len(category) + 2))
                for name, data in upgrades.items():
                    print(f"• {name} - {data['cost']:,} credits")
                    print(f"  {data['description']}")
                    print()
        
        input("\nPress Enter to continue...")

    def install_ship_upgrade(self):
        """Install an upgrade on the current ship"""
        current_ship = self.navigation.current_ship
        available = self.upgrade_system.get_available_upgrades(current_ship)
        
        # Create flat list of available upgrades
        upgrade_list = []
        for category, upgrades in available.items():
            for name, data in upgrades.items():
                upgrade_list.append((name, data, category))
        
        if not upgrade_list:
            print("\nNo upgrades available for this ship.")
            input("\nPress Enter to continue...")
            return
        
        print("\n" + "="*60)
        print("           INSTALL UPGRADE")
        print("="*60)
        
        print("Available upgrades:")
        for i, (name, data, category) in enumerate(upgrade_list, 1):
            affordable = "✓" if data['cost'] <= self.credits else "✗"
            print(f"{i:2d}. {name:<30} {data['cost']:>8,} credits {affordable}")
            print(f"     {data['description']}")
        
        try:
            choice = int(input(f"\nSelect upgrade (1-{len(upgrade_list)}): ")) - 1
            if 0 <= choice < len(upgrade_list):
                name, data, category = upgrade_list[choice]
                
                if data['cost'] > self.credits:
                    print(f"\nInsufficient credits! Need {data['cost']:,}, have {self.credits:,}")
                    input("\nPress Enter to continue...")
                    return
                
                print(f"\nUpgrade: {name}")
                print(f"Cost: {data['cost']:,} credits")
                print(f"Description: {data['description']}")
                
                confirm = input("\nInstall this upgrade? (y/n): ")
                if confirm.lower() == 'y':
                    success, message = self.upgrade_system.install_upgrade(current_ship, name, data)
                    
                    if success:
                        self.credits -= data['cost']
                        print(f"\n{message}")
                        print(f"Remaining credits: {self.credits:,}")
                    else:
                        print(f"\nUpgrade failed: {message}")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")
        
        input("\nPress Enter to continue...")

    def show_detailed_ship_status(self):
        """Show detailed ship status including upgrades"""
        ship = self.navigation.current_ship
        if not ship:
            print("No ship selected!")
            return
        
        print("\n" + "="*60)
        print(f"           SHIP STATUS - {ship.name}")
        print("="*60)
        
        print(f"Class: {ship.ship_class}")
        print(f"Location: {ship.coordinates}")
        print(f"Fuel: {ship.fuel}/{ship.max_fuel}")
        print(f"Jump Range: {ship.jump_range} units")
        print(f"Cargo: {sum(ship.cargo.values()) if ship.cargo else 0}/{ship.max_cargo}")
        
        if hasattr(ship, 'upgrades') and ship.upgrades:
            print("\nINSTALLED UPGRADES:")
            for upgrade_name, upgrade_data in ship.upgrades.items():
                print(f"• {upgrade_name}")
                print(f"  {upgrade_data['description']}")
        else:
            print("\nNo upgrades installed")
        
        input("\nPress Enter to continue...")

    def station_management_menu(self):
        """Space station management interface"""
        while True:
            print("\n" + "="*60)
            print("           STATION MANAGEMENT")
            print("="*60)
            
            if not self.station_manager:
                print("Station system not initialized.")
                input("\nPress Enter to continue...")
                return
            
            print("1. View All Stations")
            print("2. Purchase Station (at current location)")
            print("3. Manage Owned Stations")
            print("4. Collect Station Income")
            print("5. Upgrade Station")
            print("6. Back to Main Menu")
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == "1":
                self.view_all_stations()
            elif choice == "2":
                self.purchase_station()
            elif choice == "3":
                self.manage_owned_stations()
            elif choice == "4":
                self.collect_station_income()
            elif choice == "5":
                self.upgrade_owned_station()
            elif choice == "6":
                break
            else:
                print("Invalid choice.")
                input("\nPress Enter to continue...")

    def view_all_stations(self):
        """View all stations in the galaxy"""
        print("\n" + "="*60)
        print("           GALAXY STATIONS")
        print("="*60)
        
        stations_by_system = self.station_manager.get_all_stations_info()
        
        for system_name, stations in stations_by_system.items():
            print(f"\n{system_name}:")
            for station in stations:
                owner_status = "OWNED" if station['owner'] == "Player" else "Available"
                coords = station['coordinates']
                print(f"  • {station['name']} ({station['type']}) - {owner_status}")
                print(f"    Location: ({coords[0]}, {coords[1]}, {coords[2]})")
                print(f"    Services: {', '.join(station['services'])}")
                if station['owner'] == "Player":
                    print(f"    Income: {station['income']:,} credits/cycle (Level {station['upgrade_level']})")
        
        input("\nPress Enter to continue...")

    def purchase_station(self):
        """Purchase station at current location"""
        if not self.navigation.current_ship:
            print("\nNo ship selected! Use Navigation -> Select Ship first.")
            input("\nPress Enter to continue...")
            return
        
        x, y, z = self.navigation.current_ship.coordinates
        station = self.station_manager.get_station_at_location((x, y, z))
        
        if not station:
            print("\nNo station at your current location.")
            input("\nPress Enter to continue...")
            return
        
        if station['owner'] == "Player":
            print(f"\nYou already own {station['name']}!")
            input("\nPress Enter to continue...")
            return
        
        station_type = station['type']
        cost = self.station_manager.station_types[station_type]['cost']
        
        print(f"\nStation: {station['name']}")
        print(f"Type: {station_type}")
        print(f"Services: {', '.join(station['services'])}")
        print(f"Description: {station['description']}")
        print(f"Base Income: {station['income']:,} credits/cycle")
        print(f"Purchase Cost: {cost:,} credits")
        print(f"Your Credits: {self.credits:,}")
        
        if cost > self.credits:
            print("\nInsufficient credits!")
            input("\nPress Enter to continue...")
            return
        
        confirm = input(f"\nPurchase {station['name']} for {cost:,} credits? (y/n): ")
        if confirm.lower() == 'y':
            success, message, actual_cost = self.station_manager.purchase_station((x, y, z), self.credits)
            
            if success:
                self.credits -= actual_cost
                print(f"\n{message}")
                print(f"Remaining credits: {self.credits:,}")
            else:
                print(f"\nPurchase failed: {message}")
        
        input("\nPress Enter to continue...")

    def manage_owned_stations(self):
        """Manage player-owned stations"""
        owned_stations = self.station_manager.get_player_stations()
        
        if not owned_stations:
            print("\nYou don't own any stations yet.")
            input("\nPress Enter to continue...")
            return
        
        print("\n" + "="*60)
        print("           YOUR STATIONS")
        print("="*60)
        
        total_income = 0
        for station in owned_stations:
            coords = station['coordinates']
            print(f"\n{station['name']} ({station['type']})")
            print(f"  Location: ({coords[0]}, {coords[1]}, {coords[2]})")
            print(f"  System: {station['system_name']}")
            print(f"  Level: {station['upgrade_level']}")
            print(f"  Income: {station['income']:,} credits/cycle")
            print(f"  Services: {', '.join(station['services'])}")
            total_income += station['income']
        
        print(f"\nTotal Income: {total_income:,} credits/cycle")
        input("\nPress Enter to continue...")

    def collect_station_income(self):
        """Collect income from all owned stations"""
        owned_stations = self.station_manager.get_player_stations()
        
        if not owned_stations:
            print("\nNo stations to collect income from.")
            input("\nPress Enter to continue...")
            return
        
        total_income = 0
        for station in owned_stations:
            income = self.station_manager.collect_station_income(station)
            total_income += income
        
        self.credits += total_income
        
        print(f"\nCollected {total_income:,} credits from {len(owned_stations)} stations!")
        print(f"New balance: {self.credits:,} credits")
        
        input("\nPress Enter to continue...")

    def upgrade_owned_station(self):
        """Upgrade a player-owned station"""
        owned_stations = self.station_manager.get_player_stations()
        
        if not owned_stations:
            print("\nNo stations to upgrade.")
            input("\nPress Enter to continue...")
            return
        
        print("\n" + "="*60)
        print("           UPGRADE STATION")
        print("="*60)
        
        print("Your stations:")
        for i, station in enumerate(owned_stations, 1):
            coords = station['coordinates']
            upgrade_cost = station['income'] * station['upgrade_level'] * 10
            affordable = "✓" if upgrade_cost <= self.credits else "✗"
            
            print(f"{i}. {station['name']} (Level {station['upgrade_level']})")
            print(f"   Upgrade Cost: {upgrade_cost:,} credits {affordable}")
        
        try:
            choice = int(input(f"\nSelect station to upgrade (1-{len(owned_stations)}): ")) - 1
            if 0 <= choice < len(owned_stations):
                station = owned_stations[choice]
                coords = station['coordinates']
                
                success, message, cost = self.station_manager.upgrade_station(coords, self.credits)
                
                if success:
                    self.credits -= cost
                    print(f"\n{message}")
                    print(f"Remaining credits: {self.credits:,}")
                else:
                    print(f"\nUpgrade failed: {message}")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")
        
        input("\nPress Enter to continue...")

    def navigation_menu(self):
        """Space navigation and flight interface"""
        while True:
            # Display current ship status if one is selected
            if self.navigation.current_ship:
                self.navigation.display_ship_status()
            else:
                print("\n" + "="*60)
                print("           SPACE NAVIGATION")
                print("="*60)
                print("No ship selected for navigation.")
            
            print("\nNAVIGATION OPTIONS:")
            print("1. Select Ship to Pilot")
            print("2. Local Space Map")
            print("3. Jump to Star System")
            print("4. Jump to Coordinates")
            print("5. Refuel Ship")
            print("6. Galaxy Map Overview")
            print("7. Ship Status")
            print("8. Return to Main Menu")
            
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == "1":
                self.navigation.select_ship()
            elif choice == "2":
                self.navigation.display_local_map()
                input("\nPress Enter to continue...")
            elif choice == "3":
                self.navigation.navigate_to_system()
                input("\nPress Enter to continue...")
            elif choice == "4":
                self.navigation.navigate_to_coordinates()
                input("\nPress Enter to continue...")
            elif choice == "5":
                self.navigation.refuel_ship()
                input("\nPress Enter to continue...")
            elif choice == "6":
                self.show_galaxy_overview()
            elif choice == "7":
                if self.navigation.current_ship:
                    self.navigation.display_ship_status()
                else:
                    print("No ship selected!")
                input("\nPress Enter to continue...")
            elif choice == "8":
                break
            else:
                print("Invalid choice. Please try again.")
                input("\nPress Enter to continue...")

    def show_galaxy_overview(self):
        """Display overview of the entire galaxy"""
        print("\n" + "="*60)
        print("           GALAXY MAP OVERVIEW")
        print("="*60)
        
        galaxy = self.navigation.galaxy
        
        print(f"Galaxy Size: {galaxy.size_x} x {galaxy.size_y} x {galaxy.size_z}")
        print(f"Total Star Systems: {len(galaxy.systems)}")
        
        visited = sum(1 for s in galaxy.systems.values() if s["visited"])
        print(f"Systems Visited: {visited}/{len(galaxy.systems)}")
        
        # Show systems by type
        system_types = {}
        for system in galaxy.systems.values():
            system_type = system["type"]
            if system_type not in system_types:
                system_types[system_type] = 0
            system_types[system_type] += 1
        
        print("\nSystems by Type:")
        for system_type, count in sorted(system_types.items()):
            print(f"  {system_type}: {count}")
        
        # Show visited systems
        if visited > 0:
            print("\nVisited Systems:")
            for system in galaxy.systems.values():
                if system["visited"]:
                    coords = system["coordinates"]
                    print(f"  {system['name']} at ({coords[0]}, {coords[1]}, {coords[2]})")
        
        if self.navigation.current_ship:
            x, y, z = self.navigation.current_ship.coordinates
            print(f"\nCurrent Position: ({x}, {y}, {z})")
        
        input("\nPress Enter to continue...")

    def profession_career_menu(self):
        """Profession and career management menu"""
        while True:
            print("\n" + "="*60)
            print("           PROFESSION & CAREER")
            print("="*60)
            
            print("1. View Your Profession")
            print("2. Browse All Professions")
            print("3. View Job Opportunities")
            print("4. Check Experience & Levels")
            print("5. Profession Benefits")
            print("6. Back to Main Menu")
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == "1":
                self.view_current_profession()
            elif choice == "2":
                self.browse_all_professions()
            elif choice == "3":
                self.view_job_opportunities()
            elif choice == "4":
                self.check_profession_experience()
            elif choice == "5":
                self.view_profession_benefits()
            elif choice == "6":
                break
            else:
                print("Invalid choice. Please try again.")
                input("\nPress Enter to continue...")
    
    def view_current_profession(self):
        """Display current character profession details"""
        print("\n" + "="*60)
        print("           YOUR PROFESSION")
        print("="*60)
        
        if self.profession_system.character_profession:
            prof_info = self.profession_system.get_profession_info(self.profession_system.character_profession)
            
            print(f"Current Profession: {self.profession_system.character_profession}")
            print(f"Category: {prof_info['category']}")
            print(f"Description: {prof_info['description']}")
            print(f"Experience: {prof_info['player_experience']} XP")
            print(f"Level: {prof_info['player_level']}/10")
            
            # Show current benefits
            benefits = self.profession_system.get_profession_bonuses(self.profession_system.character_profession)
            if benefits:
                print(f"\nCurrent Benefits:")
                for benefit in benefits:
                    print(f"  • {benefit}")
            
            # Show requirements
            print(f"\nRequirements: {', '.join(prof_info['requirements'])}")
            
        else:
            print("No profession assigned.")
            print("Visit Character Creation to select a profession.")
        
        input("\nPress Enter to continue...")
    
    def browse_all_professions(self):
        """Browse and view details of all available professions"""
        from professions import professions, profession_categories
        
        print("\n" + "="*60)
        print("           ALL PROFESSIONS")
        print("="*60)
        
        # Group by category
        for category, prof_list in profession_categories.items():
            print(f"\n[{category.upper()}]")
            print("-" * (len(category) + 2))
            
            for prof_name in prof_list:
                if prof_name in professions:
                    prof_info = professions[prof_name]
                    level = self.profession_system.profession_levels.get(prof_name, 0)
                    
                    status = "★" if prof_name == self.profession_system.character_profession else ""
                    level_str = f" (Lv.{level})" if level > 0 else ""
                    
                    print(f"• {prof_name}{status}{level_str}")
                    print(f"  {prof_info['description']}")
        
        input("\nPress Enter to continue...")
    
    def view_job_opportunities(self):
        """View available job opportunities"""
        print("\n" + "="*60)
        print("           JOB OPPORTUNITIES")
        print("="*60)
        
        # Generate jobs based on current location
        current_system_type = None
        if self.navigation.current_ship:
            coords = self.navigation.current_ship.coordinates
            system = self.navigation.galaxy.get_system_at(*coords)
            if system:
                current_system_type = system['type']
        
        jobs = self.profession_system.generate_job_opportunities(current_system_type)
        
        if jobs:
            for i, job in enumerate(jobs, 1):
                player_level = self.profession_system.profession_levels.get(job['profession'], 0)
                qualified = "✓" if player_level > 0 else "○"
                
                print(f"{i}. {job['title']} [{job['context']}] {qualified}")
                print(f"   Profession: {job['profession']}")
                print(f"   Pay: {job['pay']:,} credits")
                print(f"   Experience: +{job['experience_reward']} XP")
                print(f"   Duration: {job['duration']} time units")
                print(f"   Requirements: {', '.join(job['requirements'])}")
                print()
        else:
            print("No job opportunities available at this time.")
            print("Try visiting different systems or developing your skills!")
        
        input("\nPress Enter to continue...")
    
    def check_profession_experience(self):
        """Check experience and levels in all professions"""
        print("\n" + "="*60)
        print("           EXPERIENCE & LEVELS")
        print("="*60)
        
        if self.profession_system.profession_experience:
            # Sort by experience
            sorted_profs = sorted(
                self.profession_system.profession_experience.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            print("Your profession development:")
            
            for prof_name, experience in sorted_profs:
                level = self.profession_system.profession_levels.get(prof_name, 1)
                next_level_xp = level * 100
                
                current_marker = "★" if prof_name == self.profession_system.character_profession else " "
                
                print(f"{current_marker} {prof_name:<35} Level {level}/10 ({experience}/{next_level_xp} XP)")
                
                # Show progress bar
                if level < 10:
                    current_level_xp = experience - ((level - 1) * 100)
                    progress = current_level_xp / 100
                    bar_length = 20
                    filled = int(progress * bar_length)
                    bar = "█" * filled + "░" * (bar_length - filled)
                    print(f"   [{bar}] {current_level_xp}/100 to next level")
        else:
            print("No profession experience yet.")
            print("Complete activities related to your profession to gain experience!")
        
        input("\nPress Enter to continue...")
    
    def view_profession_benefits(self):
        """View benefits from all known professions"""
        print("\n" + "="*60)
        print("           PROFESSION BENEFITS")
        print("="*60)
        
        total_benefits = []
        
        for prof_name, level in self.profession_system.profession_levels.items():
            if level > 0:
                benefits = self.profession_system.get_profession_bonuses(prof_name)
                if benefits:
                    print(f"\n{prof_name} (Level {level}):")
                    for benefit in benefits:
                        print(f"  • {benefit}")
                        total_benefits.append(benefit)
        
        if not total_benefits:
            print("No profession benefits unlocked yet.")
            print("Develop your profession skills to unlock powerful benefits!")
        else:
            print(f"\nTotal Active Benefits: {len(total_benefits)}")
        
        input("\nPress Enter to continue...")

    def faction_relations_menu(self):
        """Faction relations and diplomacy menu"""
        while True:
            print("\n" + "="*60)
            print("           FACTION RELATIONS")
            print("="*60)
            
            print("1. View All Factions")
            print("2. View Faction Details")
            print("3. Check Faction Territories")
            print("4. View Your Reputation")
            print("5. Faction Activities")
            print("6. Back to Main Menu")
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == "1":
                self.view_all_factions()
            elif choice == "2":
                self.view_faction_details()
            elif choice == "3":
                self.check_faction_territories()
            elif choice == "4":
                self.view_player_reputation()
            elif choice == "5":
                self.view_faction_activities()
            elif choice == "6":
                break
            else:
                print("Invalid choice. Please try again.")
                input("\nPress Enter to continue...")
    
    def view_all_factions(self):
        """Display all factions with basic info"""
        print("\n" + "="*60)
        print("           GALACTIC FACTIONS")
        print("="*60)
        
        from factions import factions
        
        # Group by philosophy
        philosophies = {}
        for name, data in factions.items():
            phil = data['philosophy']
            if phil not in philosophies:
                philosophies[phil] = []
            philosophies[phil].append((name, data))
        
        for philosophy, faction_list in philosophies.items():
            print(f"\n[{philosophy.upper()}]")
            print("-" * (len(philosophy) + 2))
            
            for name, data in faction_list:
                rep_status = self.faction_system.get_reputation_status(name)
                rep_value = self.faction_system.player_relations.get(name, 0)
                
                print(f"• {name}")
                print(f"  Focus: {data['primary_focus']} | Reputation: {rep_status} ({rep_value:+d})")
                print(f"  Government: {data['government_type']}")
        
        input("\nPress Enter to continue...")
    
    def view_faction_details(self):
        """View detailed information about a specific faction"""
        from factions import factions
        
        print("\n" + "="*60)
        print("           FACTION DETAILS")
        print("="*60)
        
        faction_names = list(factions.keys())
        
        print("Select a faction:")
        for i, name in enumerate(faction_names, 1):
            print(f"{i:2d}. {name}")
        
        try:
            choice = int(input(f"\nEnter faction number (1-{len(faction_names)}): ")) - 1
            if 0 <= choice < len(faction_names):
                faction_name = faction_names[choice]
                faction_info = self.faction_system.get_faction_info(faction_name)
                
                if faction_info:
                    print(f"\n{'='*60}")
                    print(f"           {faction_name.upper()}")
                    print(f"{'='*60}")
                    
                    print(f"Philosophy: {faction_info['philosophy']}")
                    print(f"Primary Focus: {faction_info['primary_focus']}")
                    print(f"Government: {faction_info['government_type']}")
                    print(f"Description: {faction_info['description']}")
                    
                    rep_status = self.faction_system.get_reputation_status(faction_name)
                    rep_value = faction_info['player_reputation']
                    print(f"\nYour Reputation: {rep_status} ({rep_value:+d})")
                    
                    print(f"Current Activity: {faction_info['current_activity']}")
                    print(f"Controlled Systems: {faction_info['territory_count']}")
                    
                    # Show benefits available at current reputation
                    benefits = self.faction_system.get_faction_benefits(faction_name)
                    if benefits:
                        print(f"\nAvailable Benefits:")
                        for benefit in benefits:
                            print(f"  • {benefit}")
                    
                    print(f"\nPreferred Trades:")
                    for trade in faction_info['preferred_trades']:
                        print(f"  • {trade}")
                    
                    print(f"\nTypical Activities:")
                    for activity in faction_info['typical_activities']:
                        print(f"  • {activity}")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")
        
        input("\nPress Enter to continue...")
    
    def check_faction_territories(self):
        """View faction control of star systems"""
        print("\n" + "="*60)
        print("           FACTION TERRITORIES")
        print("="*60)
        
        # Initialize territories if not done
        if not self.faction_system.faction_territories:
            self.faction_system.assign_faction_territories(self.navigation.galaxy)
        
        controlled_systems = 0
        uncontrolled_systems = 0
        
        print("Faction-controlled systems:")
        for faction_name, territories in self.faction_system.faction_territories.items():
            if territories:
                print(f"\n{faction_name}:")
                controlled_systems += len(territories)
                
                for coords in territories:
                    system = self.navigation.galaxy.get_system_at(*coords)
                    if system:
                        print(f"  • {system['name']} - {coords}")
        
        total_systems = len(self.navigation.galaxy.systems)
        uncontrolled_systems = total_systems - controlled_systems
        
        print(f"\nSummary:")
        print(f"  Faction-controlled: {controlled_systems}")
        print(f"  Independent: {uncontrolled_systems}")
        print(f"  Total systems: {total_systems}")
        
        input("\nPress Enter to continue...")
    
    def view_player_reputation(self):
        """View player's reputation with all factions"""
        print("\n" + "="*60)
        print("           YOUR REPUTATION")
        print("="*60)
        
        # Sort factions by reputation (highest first)
        sorted_factions = sorted(
            self.faction_system.player_relations.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        print("Reputation standings:")
        
        for faction_name, reputation in sorted_factions:
            status = self.faction_system.get_reputation_status(faction_name)
            
            # Color coding based on reputation
            if reputation >= 50:
                marker = "✓"
            elif reputation >= 0:
                marker = "○"
            elif reputation >= -25:
                marker = "△"
            else:
                marker = "✗"
            
            print(f"{marker} {faction_name:<35} {status:<12} ({reputation:+3d})")
        
        # Show summary
        allied = sum(1 for r in sorted_factions if r[1] >= 75)
        friendly = sum(1 for r in sorted_factions if 50 <= r[1] < 75)
        neutral = sum(1 for r in sorted_factions if -25 <= r[1] < 50)
        hostile = sum(1 for r in sorted_factions if r[1] < -25)
        
        print(f"\nSummary:")
        print(f"  Allied: {allied}")
        print(f"  Friendly: {friendly}")
        print(f"  Neutral: {neutral}")
        print(f"  Hostile: {hostile}")
        
        input("\nPress Enter to continue...")
    
    def view_faction_activities(self):
        """View current faction activities"""
        print("\n" + "="*60)
        print("           FACTION ACTIVITIES")
        print("="*60)
        
        from factions import factions
        
        for faction_name in factions.keys():
            activity = self.faction_system.faction_activities.get(faction_name, "Unknown")
            rep_status = self.faction_system.get_reputation_status(faction_name)
            
            print(f"{faction_name}:")
            print(f"  Current Activity: {activity}")
            print(f"  Your Standing: {rep_status}")
            print()
        
        print("Note: Faction activities change periodically based on their goals and circumstances.")
        input("\nPress Enter to continue...")

    def start_bot_update_thread(self):
        """Start the background thread for bot updates"""
        def bot_update_loop():
            while self.game_running:
                if self.bot_manager:
                    self.bot_manager.update_all_bots()
                time.sleep(5)  # Update every 5 seconds
        
        self.bot_update_thread = threading.Thread(target=bot_update_loop, daemon=True)
        self.bot_update_thread.start()
    
    def stop_bot_updates(self):
        """Stop bot updates"""
        self.game_running = False
    
    def ai_bots_menu(self):
        """AI Bots status and interaction menu"""
        while True:
            print("\n" + "="*60)
            print("           AI BOTS STATUS")
            print("="*60)
            
            if not self.bot_manager:
                print("AI bot system not initialized.")
                input("\nPress Enter to continue...")
                return
            
            print("1. View All Bots Status")
            print("2. View Bots at Current Location")
            print("3. Interact with Bot")
            print("4. Bot Trading Information")
            print("5. Back to Main Menu")
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                self.view_all_bots_status()
            elif choice == "2":
                self.view_bots_at_location()
            elif choice == "3":
                self.interact_with_bot()
            elif choice == "4":
                self.view_bot_trading_info()
            elif choice == "5":
                break
            else:
                print("Invalid choice. Please try again.")
                input("\nPress Enter to continue...")
    
    def view_all_bots_status(self):
        """View status of all AI bots"""
        print("\n" + "="*60)
        print("           ALL AI BOTS STATUS")
        print("="*60)
        
        bots_status = self.bot_manager.get_all_bot_status()
        
        for status in bots_status:
            print(f"\n{status['name']} ({status['type']})")
            print(f"  Location: {status['location']}")
            print(f"  Coordinates: ({status['coordinates'][0]}, {status['coordinates'][1]}, {status['coordinates'][2]})")
            print(f"  Credits: {status['credits']:,}")
            print(f"  Fuel: {status['fuel']}")
            print(f"  Current Goal: {status['current_goal']}")
            print(f"  Target: {status['goal_target']}")
            print(f"  Personality: {status['personality']}")
            print(f"  Reputation with you: {status['reputation']}")
            print(f"  Inventory Items: {status['inventory_items']}")
        
        input("\nPress Enter to continue...")
    
    def view_bots_at_location(self):
        """View bots at player's current location"""
        if not self.navigation.current_ship:
            print("\nNo ship selected! Use Navigation -> Select Ship first.")
            input("\nPress Enter to continue...")
            return
        
        player_coords = self.navigation.current_ship.coordinates
        bot_at_location = self.bot_manager.get_bot_at_location(player_coords)
        
        print("\n" + "="*60)
        print("           BOTS AT YOUR LOCATION")
        print("="*60)
        
        if bot_at_location:
            status = bot_at_location.get_status()
            print(f"\n{status['name']} ({status['type']}) is here!")
            print(f"  Credits: {status['credits']:,}")
            print(f"  Current Goal: {status['current_goal']}")
            print(f"  Personality: {status['personality']}")
            print(f"  Reputation with you: {status['reputation']}")
            print(f"  Inventory Items: {status['inventory_items']}")
        else:
            system = self.navigation.galaxy.get_system_at(*player_coords)
            system_name = system['name'] if system else "Deep Space"
            print(f"\nNo bots currently at {system_name}")
        
        input("\nPress Enter to continue...")
    
    def interact_with_bot(self):
        """Interact with a bot at current location"""
        if not self.navigation.current_ship:
            print("\nNo ship selected! Use Navigation -> Select Ship first.")
            input("\nPress Enter to continue...")
            return
        
        player_coords = self.navigation.current_ship.coordinates
        bot_at_location = self.bot_manager.get_bot_at_location(player_coords)
        
        if not bot_at_location:
            print("\nNo bots at your current location.")
            input("\nPress Enter to continue...")
            return
        
        print("\n" + "="*60)
        print(f"           INTERACTING WITH {bot_at_location.name.upper()}")
        print("="*60)
        
        # Bot greeting
        greeting = bot_at_location.interact_with_player("greeting")
        print(f"\n{bot_at_location.name}: \"{greeting}\"")
        
        print("\nInteraction Options:")
        print("1. Friendly Greeting")
        print("2. Ask about Trade Opportunities") 
        print("3. Ask about Local Systems")
        print("4. Offer Trade")
        print("5. Leave")
        
        choice = input("\nChoose interaction (1-5): ").strip()
        
        if choice == "1":
            print(f"\n{bot_at_location.name}: \"Safe travels, commander. May the stars guide your path.\"")
            bot_at_location.reputation += 1
        elif choice == "2":
            print(f"\n{bot_at_location.name}: \"The markets in {bot_at_location.goal_target['name'] if bot_at_location.goal_target else 'various systems'} have been quite active lately.\"")
        elif choice == "3":
            print(f"\n{bot_at_location.name}: \"I've been exploring the {bot_at_location.personality['type'].lower()} routes. The frontier holds many surprises.\"")
        elif choice == "4":
            self.attempt_bot_trade(bot_at_location)
        elif choice == "5":
            print(f"\n{bot_at_location.name}: \"Farewell, commander.\"")
        
        input("\nPress Enter to continue...")
    
    def attempt_bot_trade(self, bot):
        """Attempt to trade with a bot"""
        print(f"\n{bot.name}: \"What did you have in mind?\"")
        
        if not bot.inventory:
            print(f"{bot.name}: \"I don't have anything to trade right now. Check back later.\"")
            return
        
        print(f"\n{bot.name}'s Inventory:")
        items = list(bot.inventory.items())
        for i, (item, quantity) in enumerate(items, 1):
            print(f"  {i}. {item} (Quantity: {quantity})")
        
        print(f"\nYour Credits: {self.credits:,}")
        print("Note: Bot trading is currently for demonstration - full implementation coming soon!")
    
    def view_bot_trading_info(self):
        """View bot trading patterns and information"""
        print("\n" + "="*60)
        print("           BOT TRADING PATTERNS")
        print("="*60)
        
        for bot in self.bot_manager.bots:
            print(f"\n{bot.name} ({bot.bot_type}):")
            print(f"  Personality: {bot.personality['type']}")
            print(f"  Trade Frequency: {bot.personality['trade_frequency']:.1%}")
            print(f"  Risk Tolerance: {bot.personality['risk_tolerance']:.1%}")
            print(f"  Exploration Tendency: {bot.personality['exploration_tendency']:.1%}")
            
            if bot.inventory:
                print(f"  Currently Carrying: {', '.join(bot.inventory.keys())}")
            else:
                print(f"  Currently Carrying: Nothing")
        
        input("\nPress Enter to continue...")

    def start_game(self):
        print("="*60)
        print("    WELCOME TO THE GALACTIC EMPIRE MANAGEMENT SYSTEM")
        print("="*60)
        print("\nIn this vast universe of trade, exploration, and conquest,")
        print("you will build an interstellar empire spanning the galaxy.")
        print("\nManage manufacturing platforms, trade exotic commodities,")
        print("command mighty starships, and construct space stations")
        print("to dominate the known worlds!")
        
        self.player_name = input("\nEnter your commander name: ").strip()
        if not self.player_name:
            self.player_name = "Anonymous Commander"
        
        print(f"\nWelcome, {self.player_name}!")
        
        # Character creation
        print("\nNow let's create your character...")
        input("Press Enter to proceed to character creation...")
        self.character_creation()
        
        # Automatically select the first available ship if none is selected
        self.auto_select_ship()
        
        print(f"\nYou begin your journey with {self.credits:,} credits.")
        print("Use them wisely to build your galactic empire!")
        
        input("\nPress Enter to begin...")
        self.main_menu()

def main():
    game = Game()
    game.start_game()

if __name__ == "__main__":
    main()