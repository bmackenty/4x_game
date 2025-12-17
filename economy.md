# Economy & Trading (`economy.py`)

This project implements a lightweight, **UI-agnostic** supply/demand economy.
All UIs (CLI, bots, PyQt) should call into `EconomicSystem` for market state and trading.

## Core concepts

- **Markets are per star-system**: each system has its own `market` dict keyed by system name in `EconomicSystem.markets`.
- **Prices are derived** from a supply/demand ratio:

  $$price = base\_price \times clamp(0.5 + 0.5\cdot(demand/supply),\ 0.2,\ 3.0) \times shock$$

- **Production/consumption** slowly push supply and demand each tick.
- **Events** can temporarily shock supply or prices (and shocks decay back to 1.0 over time).

## Data sources

- Commodity catalog lives in `goods.py` as `commodities` (a category → list-of-items dict).
- `EconomicSystem` flattens this into commodity names via `get_all_commodity_names()`.

## Market structure

Each market (`economy.markets[system_name]`) is a dict with (at minimum):

- `system_name`, `system_type`, `population`, `resources`
- `supply`: `{commodity_name: int}`
- `demand`: `{commodity_name: int}`
- `prices`: `{commodity_name: int}`
- `production`: `{commodity_name: int}` (units per tick)
- `consumption`: `{commodity_name: int}` (units per tick)
- `price_shocks`: `{commodity_name: float}` (multiplier; decays toward 1.0)
- `last_updated`: tick counter

Markets are created from galaxy systems in `navigation.py` via `NavigationSystem.create_all_markets()`.

## Public API (used by game/bots/UI)

### Create / read market

- `create_market(system: dict) -> dict`
- `get_market_info(system_name: str) -> dict | None`
  - Returns `{ "market": market, "best_buys": [...], "best_sells": [...] }`.

### Trading

- `buy_commodity(system_name, commodity, quantity, player_credits) -> (bool, str)`
  - Validates market exists, supply exists, credits sufficient.
  - Decreases market supply, nudges demand upward slightly, recalculates price.

- `sell_commodity(system_name, commodity, quantity, player_inventory) -> (bool, str, int)`
  - Validates player has inventory and market has demand.
  - Increases market supply, reduces demand, recalculates price.

Important: these functions **only mutate the market** and compute outcomes.
The caller (`Game.perform_trade_buy/sell`, bots, CLI) is responsible for updating player credits and inventory.

### Market evolution

- `update_market(system_name)`
  - Applies production/consumption, small random noise, and mean-reversion.
  - Decays `price_shocks`.

- `tick_global_state(markets_per_tick=12) -> list[str]`
  - Called by `Game.advance_turn()`.
  - Occasionally generates a macro event and applies it.
  - Updates a subset of markets for performance.

### Trade route hints

- `get_trade_opportunities() -> list[dict]`
  - Scans pairs of markets for commodities with ≥30% price spread.

## Events integration

There are two event paths:

1) **Economy-owned events**: `tick_global_state()` may create/apply a macro event.
2) **Game event system effects**: `events.py` applies supply/price changes directly to `game.economy.markets[...]`.

`economy.py` is designed to tolerate these external edits; `update_market()` and `_normalize_market()` clamp values.

## Save/load notes

- Saves store `economy.markets` and `economy.market_history` in `save_game.py`.
- On load, `market_history` may come back as a plain `dict` (not `defaultdict`).
  `economy.py` handles this via `_get_history_bucket()` so history updates don’t crash.

## Quick usage example

```python
from game import Game

game = Game()
market_name = next(iter(game.economy.markets.keys()))
info = game.economy.get_market_info(market_name)
market = info["market"]

# Pick any commodity with supply > 0
commodity = next(c for c, s in market["supply"].items() if s > 0)

# Buy 1 unit (caller updates credits/inventory)
ok, msg = game.economy.buy_commodity(market_name, commodity, 1, game.credits)
print(ok, msg)

# Advance the turn to tick the economy
log = game.advance_turn({"source": "demo"})
print(log)
```
