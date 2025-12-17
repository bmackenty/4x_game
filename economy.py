"""economy.py

Economic System with Supply/Demand trading.

This module is intentionally UI-agnostic. UIs (CLI/PyQt/bots) should call
into `EconomicSystem` for:
- market creation and updates
- buy/sell transactions
- cross-market trade opportunity analysis

The `Game.advance_turn()` method expects an `EconomicSystem.tick_global_state()`
method that advances the economy and returns a list of human-readable messages.
"""

from __future__ import annotations

import math
import random
from collections import defaultdict
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple


class EconomicSystem:
    """Supply/demand economy with per-system markets."""

    HISTORY_LIMIT = 100
    PRICE_MULTIPLIER_MIN = 0.2
    PRICE_MULTIPLIER_MAX = 3.0

    def __init__(self):
        self.markets: Dict[str, Dict[str, Any]] = {}  # system_name -> market dict
        self.base_prices: Dict[str, int] = {}  # commodity_name -> base price
        self.global_events: List[Dict[str, Any]] = []  # recent economy events
        self.trade_routes: Dict[str, Any] = {}  # reserved for future expansion
        # Price history: key is "{system}_{commodity}" -> list[int]
        self.market_history: MutableMapping[str, List[int]] = defaultdict(list)

        self._commodity_names_cache: Optional[List[str]] = None
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

        # Reset cache
        self._commodity_names_cache = None

    # ------------------------------------------------------------------
    # Commodity helpers
    # ------------------------------------------------------------------

    def get_all_commodity_names(self) -> List[str]:
        """Return flattened commodity names from goods.py."""
        if self._commodity_names_cache is not None:
            return list(self._commodity_names_cache)

        from goods import commodities

        names: List[str] = []
        for _category, items in commodities.items():
            for item in items:
                name = item.get("name")
                if name:
                    names.append(str(name))
        self._commodity_names_cache = names
        return list(names)

    def _expand_commodity_selector(self, selector: Any, market: Dict[str, Any]) -> List[str]:
        """Expand selectors like 'all'/'luxury'/[names] into concrete commodity names."""
        if selector == 'all':
            return list(market.get('supply', {}).keys())

        if selector == 'luxury':
            # Map to the luxury goods category in goods.py.
            try:
                from goods import commodities

                luxury_items = commodities.get("Cultural and Luxury Goods", [])
                luxury_names = [str(i.get("name")) for i in luxury_items if i.get("name")]
                return [c for c in luxury_names if c in market.get('supply', {})]
            except Exception:
                return []

        if isinstance(selector, (list, tuple, set)):
            return [str(c) for c in selector if str(c) in market.get('supply', {})]

        if isinstance(selector, str):
            return [selector] if selector in market.get('supply', {}) else []

        return []

    def _get_history_bucket(self, key: str) -> List[int]:
        """Return the history list for a key, even if market_history was loaded as a plain dict."""
        mh = self.market_history
        if isinstance(mh, dict):
            if key not in mh or not isinstance(mh.get(key), list):
                mh[key] = []
            return mh[key]
        # defaultdict path
        return mh[key]

    # ------------------------------------------------------------------
    # Market creation / normalization
    # ------------------------------------------------------------------

    def _normalize_market(self, market: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure older/saved market dicts have required keys and sane values."""
        market.setdefault('supply', {})
        market.setdefault('demand', {})
        market.setdefault('prices', {})
        market.setdefault('production', {})
        market.setdefault('consumption', {})
        market.setdefault('last_updated', 0)
        # Temporary multipliers (from economy-driven events). 1.0 means no shock.
        market.setdefault('price_shocks', {})

        # Clamp negative values (can happen after external edits or older saves)
        for key in ('supply', 'demand'):
            d = market.get(key, {})
            if isinstance(d, dict):
                for k, v in list(d.items()):
                    try:
                        d[k] = max(0, int(v))
                    except Exception:
                        d[k] = 0

        shocks = market.get('price_shocks', {})
        if isinstance(shocks, dict):
            for k, v in list(shocks.items()):
                try:
                    shocks[k] = max(0.1, min(10.0, float(v)))
                except Exception:
                    shocks[k] = 1.0

        return market
    
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
            'last_updated': 0,
            'price_shocks': {},  # commodity -> multiplier (decays over time)
        }
        
        self.generate_market_profile(market)
        self.markets[system_name] = self._normalize_market(market)
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
        all_commodities = self.get_all_commodity_names()
        
        for commodity in all_commodities:
            base_price = self.base_prices.get(commodity, 5)
            
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

        self._normalize_market(market)
    
    def update_market(self, market_name):
        """Update market prices based on supply, demand, and production"""
        if market_name not in self.markets:
            return

        market = self._normalize_market(self.markets[market_name])

        # Let transient shocks decay toward 1.0
        shocks = market.get('price_shocks', {})
        if isinstance(shocks, dict) and shocks:
            for commodity in list(shocks.keys()):
                current = float(shocks.get(commodity, 1.0) or 1.0)
                # decay 15% per tick toward 1.0
                shocks[commodity] = 1.0 + (current - 1.0) * 0.85
                if abs(shocks[commodity] - 1.0) < 0.02:
                    shocks[commodity] = 1.0

        # Precompute some mean-reversion targets
        population_factor = float(market.get('population', 1_000_000)) / 1_000_000.0
        resources = market.get('resources', 'Moderate')
        resource_factor = {'Poor': 0.5, 'Moderate': 1.0, 'Rich': 1.5, 'Abundant': 2.0, 'Depleted': 0.2}.get(resources, 1.0)
        
        # Simulate production and consumption
        for commodity in list(market['supply'].keys()):
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
                    market['demand'][commodity] += int((consumption - consumed) * 0.75)

            # Mean-revert demand slowly (prevents runaway values)
            current_demand = int(market['demand'].get(commodity, 0))
            baseline = 50 + int(population_factor * 25)
            if commodity in market.get('consumption', {}):
                baseline += int(market['consumption'].get(commodity, 0)) * 2
            # Reversion step
            market['demand'][commodity] = max(10, int(current_demand + (baseline - current_demand) * 0.08))

            # Mean-revert supply a bit to keep markets stocked (esp. Frontier/Trading Hub)
            current_supply = int(market['supply'].get(commodity, 0))
            supply_baseline = 60 + int(resource_factor * 40)
            if commodity in market.get('production', {}):
                supply_baseline += int(market['production'].get(commodity, 0)) * 2
            # if supply is very low, add some restock
            if current_supply < max(10, int(supply_baseline * 0.2)):
                market['supply'][commodity] += random.randint(0, 10) + int(resource_factor * 3)
            
            # Random market fluctuations
            if random.random() < 0.1:  # 10% chance of fluctuation
                supply_change = random.randint(-20, 20)
                demand_change = random.randint(-15, 15)
                
                market['supply'][commodity] = max(0, market['supply'][commodity] + supply_change)
                market['demand'][commodity] = max(10, market['demand'][commodity] + demand_change)

            # Recalculate price from supply/demand (+ shock multiplier)
            self.update_single_commodity_price(market, commodity, market_name=market_name)
        
        market['last_updated'] += 1
    
    def get_market_info(self, system_name):
        """Get market information for a system"""
        if system_name not in self.markets:
            return None

        market = self._normalize_market(self.markets[system_name])
        
        # Find best deals (high supply, low price for buying; high demand, high price for selling)
        best_buys = []
        best_sells = []
        
        for commodity in market['supply']:
            supply = market['supply'][commodity]
            demand = market['demand'][commodity]
            price = market['prices'][commodity]
            base_price = self.base_prices.get(commodity, price)
            
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

        if quantity <= 0:
            return False, "Quantity must be greater than zero"

        market = self._normalize_market(self.markets[system_name])
        
        if commodity not in market['supply']:
            return False, f"{commodity} not available at this market"
        
        available = market['supply'][commodity]
        if quantity > available:
            return False, f"Only {available} {commodity} available"
        
        price_per_unit = market['prices'][commodity]
        total_cost = price_per_unit * quantity
        
        if total_cost > player_credits:
            return False, f"Insufficient credits. Need {total_cost:,}, have {player_credits:,}"
        
        # Execute trade: remove inventory from market.
        market['supply'][commodity] -= quantity

        # Buying tends to increase scarcity pressure slightly.
        market['demand'][commodity] = max(10, int(market['demand'][commodity] + math.ceil(quantity * 0.05)))
        
        # Update price due to reduced supply
        self.update_single_commodity_price(market, commodity, market_name=system_name)
        
        return True, f"Bought {quantity} {commodity} for {total_cost:,} credits"
    
    def sell_commodity(self, system_name, commodity, quantity, player_inventory):
        """Sell commodity to a market"""
        if system_name not in self.markets:
            return False, "No market at this location", 0

        if quantity <= 0:
            return False, "Quantity must be greater than zero", 0

        market = self._normalize_market(self.markets[system_name])
        
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
        market['demand'][commodity] = max(0, int(market['demand'][commodity]) - quantity)
        
        # Update price due to increased supply
        self.update_single_commodity_price(market, commodity, market_name=system_name)
        
        return True, f"Sold {quantity} {commodity} for {total_value:,} credits", total_value

    def update_single_commodity_price(self, market, commodity, market_name: Optional[str] = None):
        """Update price for a single commodity based on supply/demand and any price shocks."""
        try:
            supply = max(1, int(market['supply'].get(commodity, 0)))
            demand = max(0, int(market['demand'].get(commodity, 0)))
        except Exception:
            return

        ratio = demand / supply
        base_price = int(self.base_prices.get(commodity, 5))
        price_multiplier = 0.5 + (ratio * 0.5)
        price_multiplier = max(self.PRICE_MULTIPLIER_MIN, min(self.PRICE_MULTIPLIER_MAX, price_multiplier))

        shock = 1.0
        shocks = market.get('price_shocks', {})
        if isinstance(shocks, dict):
            shock = float(shocks.get(commodity, 1.0) or 1.0)

        new_price = max(1, int(base_price * price_multiplier * shock))
        market['prices'][commodity] = new_price

        if market_name:
            key = f"{market_name}_{commodity}"
            bucket = self._get_history_bucket(key)
            bucket.append(new_price)
            if len(bucket) > self.HISTORY_LIMIT:
                del bucket[:-self.HISTORY_LIMIT]
    
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

        for market_name, market in self.markets.items():
            market = self._normalize_market(market)
            commodities = self._expand_commodity_selector(effect.get('commodities'), market)

            if effect['type'] in ('supply_increase', 'supply_decrease'):
                for commodity in commodities:
                    market['supply'][commodity] = max(0, int(market['supply'].get(commodity, 0) * float(effect.get('multiplier', 1.0))))
                    self.update_single_commodity_price(market, commodity, market_name=market_name)

            elif effect['type'] in ('price_increase', 'price_decrease'):
                # Price changes are modeled as a temporary shock multiplier that decays over time.
                mult = float(effect.get('multiplier', 1.0))
                shocks = market.get('price_shocks', {})
                if not isinstance(shocks, dict):
                    market['price_shocks'] = {}
                    shocks = market['price_shocks']

                for commodity in commodities:
                    shocks[commodity] = float(shocks.get(commodity, 1.0) or 1.0) * mult
                    shocks[commodity] = max(0.1, min(10.0, shocks[commodity]))
                    self.update_single_commodity_price(market, commodity, market_name=market_name)
        
        self.global_events.append(event)
        if len(self.global_events) > 5:
            self.global_events.pop(0)

    # ------------------------------------------------------------------
    # Turn/global tick integration
    # ------------------------------------------------------------------

    def tick_global_state(self, markets_per_tick: int = 12) -> List[str]:
        """Advance the economy by one global tick.

        Called from `Game.advance_turn()`. Returns human-readable messages
        describing notable economic changes (events, volatility spikes, etc.).
        """
        messages: List[str] = []

        if not self.markets:
            return messages

        # Occasionally generate a macro event and apply it.
        if random.random() < 0.18:
            event = self.create_economic_event()
            try:
                self.apply_economic_event(event)
                messages.append(f"Economic event: {event.get('name', 'Unknown')} — {event.get('description', '')}")
            except Exception as exc:
                messages.append(f"Economic event failed: {exc}")

        # Update a subset of markets each tick (keeps turn time reasonable).
        market_names = list(self.markets.keys())
        if markets_per_tick >= len(market_names):
            chosen = market_names
        else:
            chosen = random.sample(market_names, max(1, markets_per_tick))

        for name in chosen:
            try:
                self.update_market(name)
            except Exception:
                # Keep ticking other markets even if one fails.
                continue

        return messages
    
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
