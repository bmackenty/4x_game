"""
AI Bot System for 4X Game
Non-hostile NPCs with autonomous behavior
"""

import random
import time
from navigation import Ship

class AIBot:
    def __init__(self, name, bot_type, starting_system, game):
        self.name = name
        self.bot_type = bot_type
        self.game = game
        self.credits = random.randint(50000, 200000)
        self.inventory = {}
        self.ship = None
        self.current_goal = None
        self.goal_target = None
        self.reputation = 0  # Player's reputation with this bot
        self.last_action_time = 0
        self.trade_history = []
        self.personality = self.generate_personality()
        
        # Create bot's ship
        self.create_bot_ship(starting_system)
        
        # Set initial goal
        self.set_new_goal()
    
    def generate_personality(self):
        """Generate personality traits that affect bot behavior"""
        personalities = {
            "Cautious": {"risk_tolerance": 0.3, "trade_frequency": 0.4, "exploration_tendency": 0.2},
            "Aggressive": {"risk_tolerance": 0.8, "trade_frequency": 0.7, "exploration_tendency": 0.9},
            "Balanced": {"risk_tolerance": 0.5, "trade_frequency": 0.6, "exploration_tendency": 0.5},
            "Conservative": {"risk_tolerance": 0.2, "trade_frequency": 0.3, "exploration_tendency": 0.1},
            "Opportunistic": {"risk_tolerance": 0.7, "trade_frequency": 0.9, "exploration_tendency": 0.6}
        }
        
        personality_type = random.choice(list(personalities.keys()))
        return {"type": personality_type, **personalities[personality_type]}
    
    def create_bot_ship(self, starting_system):
        """Create a ship for the bot"""
        ship_types = ["Aurora-Class Freighter", "Stellar Voyager", "Nebula Drifter", "Basic Transport"]
        ship_class = random.choice(ship_types)
        
        self.ship = Ship(f"{self.name}'s Ship", ship_class)
        self.ship.coordinates = starting_system['coordinates']
        
        # Give bot some starting cargo
        from goods import commodities
        for category, items in commodities.items():
            if random.random() < 0.3:  # 30% chance for each category
                item = random.choice(items)
                quantity = random.randint(5, 25)
                self.inventory[item['name']] = quantity
    
    def set_new_goal(self):
        """Set a new goal based on bot type and personality"""
        goals = []
        
        if self.bot_type == "Trader":
            goals = ["trade", "explore_market", "collect_goods"]
        elif self.bot_type == "Explorer":
            goals = ["explore", "visit_unvisited", "survey_system"]
        elif self.bot_type == "Researcher":
            goals = ["research", "visit_research_stations", "collect_data"]
        elif self.bot_type == "Industrialist":
            goals = ["purchase_station", "visit_industrial", "collect_resources"]
        elif self.bot_type == "Diplomat":
            goals = ["visit_core_worlds", "establish_relations", "trade"]
        
        # Add personality influence
        if self.personality["exploration_tendency"] > 0.7:
            goals.extend(["explore", "visit_unvisited"])
        if self.personality["trade_frequency"] > 0.7:
            goals.extend(["trade", "collect_goods"])
        
        self.current_goal = random.choice(goals)
        self.find_goal_target()
    
    def find_goal_target(self):
        """Find a target location for the current goal"""
        galaxy = self.game.navigation.galaxy
        
        if self.current_goal == "trade":
            # Find a system with good trade opportunities
            systems_with_markets = [s for s in galaxy.systems.values() 
                                   if s['type'] in ['Trading Hub', 'Core World', 'Industrial']]
            self.goal_target = random.choice(systems_with_markets) if systems_with_markets else None
            
        elif self.current_goal == "explore":
            # Find an unvisited system
            unvisited = [s for s in galaxy.systems.values() if not s['visited']]
            self.goal_target = random.choice(unvisited) if unvisited else random.choice(list(galaxy.systems.values()))
            
        elif self.current_goal == "visit_research_stations":
            # Find research systems
            research_systems = [s for s in galaxy.systems.values() if s['type'] == 'Research']
            self.goal_target = random.choice(research_systems) if research_systems else None
            
        elif self.current_goal == "visit_industrial":
            # Find industrial systems
            industrial_systems = [s for s in galaxy.systems.values() if s['type'] == 'Industrial']
            self.goal_target = random.choice(industrial_systems) if industrial_systems else None
            
        elif self.current_goal == "visit_core_worlds":
            # Find core world systems
            core_systems = [s for s in galaxy.systems.values() if s['type'] == 'Core World']
            self.goal_target = random.choice(core_systems) if core_systems else None
            
        else:
            # Default: random system
            self.goal_target = random.choice(list(galaxy.systems.values()))
    
    def update_behavior(self):
        """Update bot behavior - called periodically"""
        current_time = time.time()
        
        # Only act every few seconds to avoid spam
        if current_time - self.last_action_time < 3:
            return
        
        self.last_action_time = current_time
        
        # Decide what to do based on current state
        if self.current_goal is None or self.goal_target is None:
            self.set_new_goal()
            return
        
        # Check if at goal location
        if self.ship.coordinates == self.goal_target['coordinates']:
            self.execute_goal_action()
            self.set_new_goal()  # Set new goal after completing current one
        else:
            # Move toward goal
            self.move_toward_goal()
    
    def move_toward_goal(self):
        """Move ship toward the goal target"""
        if not self.goal_target:
            return
        
        target_coords = self.goal_target['coordinates']
        galaxy = self.game.navigation.galaxy
        
        # Check if we can reach the target
        if self.ship.can_jump_to(target_coords, galaxy):
            success, message = self.ship.jump_to(target_coords, galaxy, self.game)
            if success:
                # Mark system as visited
                system = galaxy.get_system_at(*target_coords)
                if system:
                    system['visited'] = True
        else:
            # Can't reach target directly, find intermediate destination
            nearby_systems = galaxy.get_nearby_systems(
                *self.ship.coordinates, self.ship.jump_range
            )
            
            if nearby_systems:
                # Choose system closest to our goal
                best_system = None
                best_distance = float('inf')
                
                for system, distance in nearby_systems:
                    goal_distance = galaxy.calculate_distance(
                        system['coordinates'], target_coords
                    )
                    if goal_distance < best_distance:
                        best_distance = goal_distance
                        best_system = system
                
                if best_system and self.ship.can_jump_to(best_system['coordinates'], galaxy):
                    self.ship.jump_to(best_system['coordinates'], galaxy, self.game)
    
    def execute_goal_action(self):
        """Execute action at goal location"""
        if self.current_goal == "trade":
            self.attempt_trade()
        elif self.current_goal == "explore":
            self.explore_system()
        elif self.current_goal in ["visit_research_stations", "visit_industrial", "visit_core_worlds"]:
            self.visit_system()
        elif self.current_goal == "collect_goods":
            self.collect_local_goods()
        elif self.current_goal == "purchase_station":
            self.attempt_station_purchase()
    
    def attempt_trade(self):
        """Attempt to trade at current location"""
        system = self.game.navigation.galaxy.get_system_at(*self.ship.coordinates)
        if not system:
            return
        
        # Try to trade with the market
        if system['name'] in self.game.economy.markets:
            market_info = self.game.economy.get_market_info(system['name'])
            if market_info:
                # Try to sell something
                self.bot_sell_goods(system['name'], market_info)
                # Try to buy something
                self.bot_buy_goods(system['name'], market_info)
    
    def bot_sell_goods(self, system_name, market_info):
        """Bot attempts to sell goods"""
        market = market_info['market']
        
        for commodity, quantity in list(self.inventory.items()):
            if commodity in market['demand'] and market['demand'][commodity] > 0:
                sell_quantity = min(quantity, market['demand'][commodity], random.randint(1, 10))
                
                if sell_quantity > 0:
                    success, message, credits_earned = self.game.economy.sell_commodity(
                        system_name, commodity, sell_quantity, self.inventory
                    )
                    
                    if success:
                        self.credits += credits_earned
                        self.inventory[commodity] -= sell_quantity
                        if self.inventory[commodity] <= 0:
                            del self.inventory[commodity]
                        break  # Only sell one type per visit
    
    def bot_buy_goods(self, system_name, market_info):
        """Bot attempts to buy goods"""
        market = market_info['market']
        
        # Look for good buying opportunities
        for commodity, supply in market['supply'].items():
            if supply > 10:  # Only buy if good supply
                price = market['prices'][commodity]
                max_affordable = self.credits // price
                
                if max_affordable > 0:
                    buy_quantity = min(max_affordable, supply, random.randint(1, 15))
                    
                    success, message = self.game.economy.buy_commodity(
                        system_name, commodity, buy_quantity, self.credits
                    )
                    
                    if success:
                        cost = buy_quantity * price
                        self.credits -= cost
                        
                        if commodity in self.inventory:
                            self.inventory[commodity] += buy_quantity
                        else:
                            self.inventory[commodity] = buy_quantity
                        break  # Only buy one type per visit
    
    def explore_system(self):
        """Explore current system"""
        system = self.game.navigation.galaxy.get_system_at(*self.ship.coordinates)
        if system:
            system['visited'] = True
            # Could add exploration bonuses or discoveries here
    
    def visit_system(self):
        """Visit system for specific purpose"""
        system = self.game.navigation.galaxy.get_system_at(*self.ship.coordinates)
        if system:
            system['visited'] = True
            
            # Refuel if needed
            if self.ship.fuel < self.ship.max_fuel * 0.3:  # Refuel if below 30%
                fuel_needed = self.ship.max_fuel - self.ship.fuel
                fuel_cost = fuel_needed * 10
                
                if fuel_cost <= self.credits:
                    self.credits -= fuel_cost
                    self.ship.refuel()
    
    def collect_local_goods(self):
        """Collect goods available locally"""
        # Similar to trading but focused on buying
        self.attempt_trade()
    
    def attempt_station_purchase(self):
        """Attempt to purchase a space station"""
        if not self.game.station_manager:
            return
        
        coords = self.ship.coordinates
        station = self.game.station_manager.get_station_at_location(coords)
        
        if station and station['owner'] is None:
            station_type = station['type']
            cost = self.game.station_manager.station_types[station_type]['cost']
            
            # Bots are more willing to buy cheaper stations
            if cost <= self.credits and (cost < 800000 or random.random() < 0.3):
                # "Purchase" the station (set owner to bot name instead of "Player")
                station['owner'] = self.name
                self.credits -= cost
    
    def get_status(self):
        """Get current status of the bot"""
        system = self.game.navigation.galaxy.get_system_at(*self.ship.coordinates)
        system_name = system['name'] if system else "Deep Space"
        
        return {
            'name': self.name,
            'type': self.bot_type,
            'location': system_name,
            'coordinates': self.ship.coordinates,
            'credits': self.credits,
            'fuel': f"{self.ship.fuel}/{self.ship.max_fuel}",
            'current_goal': self.current_goal,
            'goal_target': self.goal_target['name'] if self.goal_target else "None",
            'personality': self.personality['type'],
            'reputation': self.reputation,
            'inventory_items': len(self.inventory)
        }
    
    def interact_with_player(self, interaction_type):
        """Handle player interaction with bot"""
        responses = {
            "greeting": {
                "Trader": [
                    "Greetings! Looking for good trade opportunities?",
                    "Welcome! I'm always interested in profitable ventures.",
                    "Hello there! The markets have been quite volatile lately."
                ],
                "Explorer": [
                    "Greetings, fellow traveler! Seen any interesting systems lately?",
                    "Hello! The frontier holds so many mysteries, doesn't it?",
                    "Ah, another explorer! Safe travels among the stars."
                ],
                "Researcher": [
                    "Fascinating! Another sentient being in this vast cosmos.",
                    "Greetings! Have you encountered any unusual phenomena recently?",
                    "Hello! The data streams in this sector are quite intriguing."
                ],
                "Industrialist": [
                    "Greetings! Industry drives civilization forward, wouldn't you agree?",
                    "Hello! Always good to meet someone else who appreciates infrastructure.",
                    "Welcome! The foundation of any empire is solid industrial capacity."
                ],
                "Diplomat": [
                    "Greetings and salutations! Peaceful relations benefit all.",
                    "Hello! Diplomacy opens doors that force cannot.",
                    "Welcome, friend! Communication is the key to prosperity."
                ]
            }
        }
        
        if interaction_type in responses and self.bot_type in responses[interaction_type]:
            return random.choice(responses[interaction_type][self.bot_type])
        
        return f"{self.name} acknowledges your presence."

class BotManager:
    def __init__(self, game):
        self.game = game
        self.bots = []
        self.create_initial_bots()
    
    def create_initial_bots(self):
        """Create 4-5 initial AI bots"""
        bot_configs = [
            {"name": "Captain Vex", "type": "Trader"},
            {"name": "Dr. Cosmos", "type": "Researcher"}, 
            {"name": "Explorer Zara", "type": "Explorer"},
            {"name": "Industrialist Kane", "type": "Industrialist"},
            {"name": "Ambassador Nova", "type": "Diplomat"}
        ]
        
        # Get random starting systems for each bot
        galaxy = self.game.navigation.galaxy
        systems = list(galaxy.systems.values())
        
        for i, config in enumerate(bot_configs):
            if i < len(systems):
                starting_system = systems[i]
                bot = AIBot(config["name"], config["type"], starting_system, self.game)
                self.bots.append(bot)
    
    def update_all_bots(self):
        """Update all bots - call this periodically"""
        for bot in self.bots:
            bot.update_behavior()
    
    def get_bot_at_location(self, coordinates):
        """Get bot at specific coordinates"""
        for bot in self.bots:
            if bot.ship.coordinates == coordinates:
                return bot
        return None
    
    def get_all_bot_status(self):
        """Get status of all bots"""
        return [bot.get_status() for bot in self.bots]
    
    def get_bot_by_name(self, name):
        """Get specific bot by name"""
        for bot in self.bots:
            if bot.name == name:
                return bot
        return None