"""
Economic System with Supply and Demand
"""

import random
import math
from collections import defaultdict

class EconomicSystem:
    def __init__(self):
        self.markets = {}  # Markets at each star system
        self.base_prices = {}  # Base commodity prices
        self.global_events = []  # Events that affect markets
        self.trade_routes = {}  # Active trade routes
        self.market_history = defaultdict(list)  # Price history
        
        self.initialize_base_prices()
    
    def initialize_base_prices(self):
        """Set base prices for all commodities"""
        from goods import commodities
        
        for category, items in commodities.items():
            for item in items:
                # Base price with some variation
                base = item['value']
                variation = random.uniform(0.8, 1.2)
                self.base_prices[item['name']] = int(base * variation)
    
    def create_market(self, system):
        """Create a market for a star system"""
        system_name = system['name']
        system_type = system['type']
        population = system['population']
        resources = system['resources']
        
        market = {
            'system_name': system_name,
            'system_type': system_type,
            'population': population,
            'resources': resources,
            'supply': {},  # How much of each good is available
            'demand': {},  # How much of each good is wanted
            'prices': {},  # Current prices
            'production': {},  # What this system produces
            'consumption': {},  # What this system consumes
            'last_updated': 0
        }
        
        self.generate_market_profile(market)
        self.markets[system_name] = market
        return market
    
    def generate_market_profile(self, market):
        """Generate production and consumption patterns based on system type"""
        from goods import commodities
        
        # Production bonuses based on system type
        production_bonuses = {
            'Industrial': ['Zerite Crystals', 'Crythium Ore', 'Phasemetal', 'Voidglass Shards'],
            'Mining': ['Gravossils', 'Carboxite Slabs', 'Quantum Sand', 'Nullstone', 'Living Ore'],
            'Agricultural': ['Ethergrain', 'Dreamroot', 'Synthmeat Matrix', 'Sporemilk', 'Glowfruit'],
            'Research': ['Chrono-silt', 'Temporal Anomaly Data', 'Quantum Computing Cores'],
            'Trading Hub': [],  # Balanced production/consumption
            'Military': ['Weapons Components', 'Armor Plating', 'Shield Generators'],
            'Core World': ['Luxury Goods', 'Information', 'Financial Instruments'],
            'Frontier': ['Basic Supplies', 'Raw Materials']
        }
        
        # Consumption patterns
        consumption_bonuses = {
            'Industrial': ['Raw Materials', 'Energy Sources'],
            'Mining': ['Equipment', 'Life Support'],
            'Agricultural': ['Machinery', 'Fertilizers'],
            'Research': ['Exotic Materials', 'Computing Hardware'],
            'Trading Hub': ['Everything'],
            'Military': ['Weapons', 'Armor', 'Fuel'],
            'Core World': ['Luxury Items', 'Art', 'Entertainment'],
            'Frontier': ['Basic Necessities', 'Tools']
        }
        
        system_type = market['system_type']
        population_factor = market['population'] / 1000000  # Scale factor
        resource_factor = {'Poor': 0.5, 'Moderate': 1.0, 'Rich': 1.5, 'Abundant': 2.0, 'Depleted': 0.2}[market['resources']]
        
        # Generate supply and demand for each commodity
        all_commodities = []
        for category, items in commodities.items():
            all_commodities.extend([item['name'] for item in items])
        
        for commodity in all_commodities:
            base_price = self.base_prices[commodity]
            
            # Default supply and demand
            supply = random.randint(50, 200)
            demand = random.randint(50, 200)
            
            # Modify based on system type and characteristics
            produces = commodity in production_bonuses.get(system_type, [])
            consumes = commodity in consumption_bonuses.get(system_type, []) or 'Everything' in consumption_bonuses.get(system_type, [])
            
            if produces:
                supply = int(supply * resource_factor * random.uniform(1.5, 3.0))
                market['production'][commodity] = random.randint(10, 50)
            
            if consumes:
                demand = int(demand * population_factor * random.uniform(1.2, 2.5))
                market['consumption'][commodity] = random.randint(5, 30)
            
            # Calculate price based on supply/demand ratio
            if supply > 0:
                ratio = demand / supply
                price_multiplier = 0.5 + (ratio * 0.5)  # 0.5x to 1.5x+ base price
                price_multiplier = max(0.2, min(3.0, price_multiplier))  # Cap between 0.2x and 3.0x
            else:
                price_multiplier = 3.0  # Very high price if no supply
            
            market['supply'][commodity] = supply
            market['demand'][commodity] = demand
            market['prices'][commodity] = int(base_price * price_multiplier)
    
    def update_market(self, market_name):
        """Update market prices based on supply, demand, and production"""
        if market_name not in self.markets:
            return
        
        market = self.markets[market_name]
        
        # Simulate production and consumption
        for commodity in market['supply']:
            # Production adds to supply
            if commodity in market['production']:
                production = market['production'][commodity]
                variation = random.uniform(0.8, 1.2)
                market['supply'][commodity] += int(production * variation)
            
            # Consumption reduces supply
            if commodity in market['consumption']:
                consumption = market['consumption'][commodity]
                variation = random.uniform(0.8, 1.2)
                consumed = min(market['supply'][commodity], int(consumption * variation))
                market['supply'][commodity] -= consumed
                
                # If we can't meet demand, increase demand (creates scarcity)
                if consumed < consumption:
                    market['demand'][commodity] += int((consumption - consumed) * 0.5)
            
            # Random market fluctuations
            if random.random() < 0.1:  # 10% chance of fluctuation
                supply_change = random.randint(-20, 20)
                demand_change = random.randint(-15, 15)
                
                market['supply'][commodity] = max(0, market['supply'][commodity] + supply_change)
                market['demand'][commodity] = max(10, market['demand'][commodity] + demand_change)
            
            # Recalculate prices
            supply = max(1, market['supply'][commodity])  # Avoid division by zero
            demand = market['demand'][commodity]
            
            ratio = demand / supply
            base_price = self.base_prices[commodity]
            price_multiplier = 0.5 + (ratio * 0.5)
            price_multiplier = max(0.2, min(3.0, price_multiplier))
            
            new_price = int(base_price * price_multiplier)
            
            # Store price history
            self.market_history[f"{market_name}_{commodity}"].append(new_price)
            if len(self.market_history[f"{market_name}_{commodity}"]) > 10:
                self.market_history[f"{market_name}_{commodity}"].pop(0)
            
            market['prices'][commodity] = new_price
        
        market['last_updated'] += 1
    
    def get_market_info(self, system_name):
        """Get market information for a system"""
        if system_name not in self.markets:
            return None
        
        market = self.markets[system_name]
        
        # Find best deals (high supply, low price for buying; high demand, high price for selling)
        best_buys = []
        best_sells = []
        
        for commodity in market['supply']:
            supply = market['supply'][commodity]
            demand = market['demand'][commodity]
            price = market['prices'][commodity]
            base_price = self.base_prices[commodity]
            
            if supply > 100 and price < base_price * 0.8:  # Good buying opportunity
                best_buys.append((commodity, price, supply))
            
            if demand > 100 and price > base_price * 1.2:  # Good selling opportunity
                best_sells.append((commodity, price, demand))
        
        # Sort by best deals
        best_buys.sort(key=lambda x: x[1])  # Sort by price (ascending)
        best_sells.sort(key=lambda x: x[1], reverse=True)  # Sort by price (descending)
        
        return {
            'market': market,
            'best_buys': best_buys[:5],
            'best_sells': best_sells[:5]
        }
    
    def buy_commodity(self, system_name, commodity, quantity, player_credits):
        """Buy commodity from a market"""
        if system_name not in self.markets:
            return False, "No market at this location"
        
        market = self.markets[system_name]
        
        if commodity not in market['supply']:
            return False, f"{commodity} not available at this market"
        
        available = market['supply'][commodity]
        if quantity > available:
            return False, f"Only {available} {commodity} available"
        
        price_per_unit = market['prices'][commodity]
        total_cost = price_per_unit * quantity
        
        if total_cost > player_credits:
            return False, f"Insufficient credits. Need {total_cost:,}, have {player_credits:,}"
        
        # Execute trade
        market['supply'][commodity] -= quantity
        market['demand'][commodity] = max(0, market['demand'][commodity] - int(quantity * 0.1))  # Slight demand reduction
        
        # Update price due to reduced supply
        self.update_single_commodity_price(market, commodity)
        
        return True, f"Bought {quantity} {commodity} for {total_cost:,} credits"
    
    def sell_commodity(self, system_name, commodity, quantity, player_inventory):
        """Sell commodity to a market"""
        if system_name not in self.markets:
            return False, "No market at this location", 0
        
        market = self.markets[system_name]
        
        if commodity not in player_inventory:
            return False, f"You don't have any {commodity}", 0
        
        available = player_inventory[commodity]
        if quantity > available:
            return False, f"You only have {available} {commodity}", 0
        
        # Check market demand
        if commodity not in market['demand']:
            return False, f"No demand for {commodity} at this market", 0
        
        demand = market['demand'][commodity]
        if demand < quantity:
            return False, f"Market only wants {demand} {commodity}, you're trying to sell {quantity}", 0
        
        price_per_unit = market['prices'][commodity]
        total_value = price_per_unit * quantity
        
        # Execute trade
        market['supply'][commodity] += quantity
        market['demand'][commodity] -= quantity
        
        # Update price due to increased supply
        self.update_single_commodity_price(market, commodity)
        
        return True, f"Sold {quantity} {commodity} for {total_value:,} credits", total_value
    
    def update_single_commodity_price(self, market, commodity):
        """Update price for a single commodity"""
        supply = max(1, market['supply'][commodity])
        demand = market['demand'][commodity]
        
        ratio = demand / supply
        base_price = self.base_prices[commodity]
        price_multiplier = 0.5 + (ratio * 0.5)
        price_multiplier = max(0.2, min(3.0, price_multiplier))
        
        market['prices'][commodity] = int(base_price * price_multiplier)
    
    def create_economic_event(self):
        """Create random economic events that affect markets"""
        events = [
            {
                'name': 'Mining Boom',
                'description': 'Rich ore deposits discovered!',
                'effects': {'type': 'supply_increase', 'commodities': ['Zerite Crystals', 'Crythium Ore'], 'multiplier': 2.0}
            },
            {
                'name': 'Crop Failure',
                'description': 'Agricultural worlds hit by blight',
                'effects': {'type': 'supply_decrease', 'commodities': ['Ethergrain', 'Sporemilk'], 'multiplier': 0.3}
            },
            {
                'name': 'Trade War',
                'description': 'Political tensions disrupt trade routes',
                'effects': {'type': 'price_increase', 'commodities': 'all', 'multiplier': 1.3}
            },
            {
                'name': 'Technology Breakthrough',
                'description': 'New manufacturing techniques developed',
                'effects': {'type': 'supply_increase', 'commodities': ['Quantum Sand', 'Phasemetal'], 'multiplier': 1.8}
            },
            {
                'name': 'Pirate Raids',
                'description': 'Pirates attacking trade convoys',
                'effects': {'type': 'supply_decrease', 'commodities': 'luxury', 'multiplier': 0.6}
            }
        ]
        
        return random.choice(events)
    
    def apply_economic_event(self, event):
        """Apply an economic event to all markets"""
        effect = event['effects']
        
        for market in self.markets.values():
            if effect['type'] == 'supply_increase':
                commodities = effect['commodities']
                if commodities == 'all':
                    commodities = list(market['supply'].keys())
                
                for commodity in commodities:
                    if commodity in market['supply']:
                        market['supply'][commodity] = int(market['supply'][commodity] * effect['multiplier'])
            
            elif effect['type'] == 'supply_decrease':
                commodities = effect['commodities']
                if commodities == 'all':
                    commodities = list(market['supply'].keys())
                
                for commodity in commodities:
                    if commodity in market['supply']:
                        market['supply'][commodity] = int(market['supply'][commodity] * effect['multiplier'])
            
            elif effect['type'] == 'price_increase':
                commodities = effect['commodities']
                if commodities == 'all':
                    commodities = list(market['prices'].keys())
                
                for commodity in commodities:
                    if commodity in market['prices']:
                        market['prices'][commodity] = int(market['prices'][commodity] * effect['multiplier'])
        
        self.global_events.append(event)
        if len(self.global_events) > 5:
            self.global_events.pop(0)
    
    def get_trade_opportunities(self):
        """Find profitable trade routes between markets"""
        opportunities = []
        
        market_names = list(self.markets.keys())
        
        for i, source_name in enumerate(market_names):
            for j, dest_name in enumerate(market_names):
                if i >= j:  # Avoid duplicates and self-trading
                    continue
                
                source = self.markets[source_name]
                dest = self.markets[dest_name]
                
                # Find commodities that are cheap at source and expensive at destination
                for commodity in source['supply']:
                    if commodity in dest['prices'] and source['supply'][commodity] > 50:
                        source_price = source['prices'][commodity]
                        dest_price = dest['prices'][commodity]
                        
                        if dest_price > source_price * 1.3:  # At least 30% profit margin
                            profit_margin = ((dest_price - source_price) / source_price) * 100
                            
                            opportunities.append({
                                'commodity': commodity,
                                'source': source_name,
                                'destination': dest_name,
                                'buy_price': source_price,
                                'sell_price': dest_price,
                                'profit_margin': profit_margin,
                                'available_supply': source['supply'][commodity]
                            })
        
        # Sort by profit margin
        opportunities.sort(key=lambda x: x['profit_margin'], reverse=True)
        return opportunities[:10]  # Return top 10 opportunities