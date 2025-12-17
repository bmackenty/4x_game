# Copilot instructions for `4x_game`

## Big picture (where to start)
- **Engine orchestration** lives in `game.py` (`Game`), which wires subsystems: `NavigationSystem` (`navigation.py`), `EconomicSystem` (`economy.py`), `FactionSystem` (`factions.py`), `EventSystem` (`events.py`), `NewsSystem` (`news_system.py`).
- This repo is **flat (no package/)**: most modules import each other by filename from repo root.

## Entry points / how to run
- **Primary UI (agents should use this)**: `python3 pyqt_interface.py` (requires `PyQt6`; see imports at top of the file).
- Terminal UI: `python3 game.py`.
- Textual UI is **legacy**: `./run_ui.sh` / `python3 textual_interface.py` (avoid adding new features here unless you’re explicitly doing legacy maintenance).

## Python version
- Minimum supported Python: **3.10+** (the codebase uses modern type syntax like `dict | None`).

## Key architecture & data flow
- **Turns**: prefer routing per-turn updates through `Game.advance_turn(...)` (returns a structured list of log entries) and have UIs render those messages.
- **Galaxy + movement**: `NavigationSystem` owns `Galaxy` and NPC ships; ship movement consumes fuel via `calculate_fuel_consumption(...)` in `navigation.py`.
- **Events → News**: `EventSystem` maintains active events and a `news_feed`; `NewsSystem.get_all_news(...)` formats that feed for UI display.
- **Save/load**: `save_game.py` persists game state to `saves/*.json` and writes debug traces to `save_debug.log`.

## Project-specific conventions (important)
- **Static game data is module-global**:
  - Commodities: `goods.py` (`commodities` dict)
  - Faction zones & colors: `systems.py` (`FACTION_ZONES`, `FACTION_COLORS`)
  - Factions & diplomacy: `factions.py` (`factions` dict + `FactionSystem`)
  Update these sources rather than duplicating literals in UIs.

- **Ship system is hybrid (be careful)**:
  - Runtime ship object is `navigation.Ship`.
  - Its stats are derived via `navigation.Ship.calculate_stats_from_components()`, which calls `ship_builder.compute_ship_profile(...)` and maps canonical attributes back into legacy fields like `max_fuel`, `jump_range`, and `scan_range`.
  - When changing ship balance, prefer adjusting canonical component/attribute definitions in `ship_builder.py` / `ship_attributes.py` so all UIs stay consistent.

## Tests / demos (not pytest)
- “Tests” are runnable scripts: `python3 test_news.py`, `python3 test_scanning.py`, `python3 test_functionality.py`, etc.
- Feature docs and demos to consult when changing subsystems:
  - `SCANNING_SYSTEM.md` (ties `navigation.py` + `nethack_interface.py`)
  - `NEWS_SYSTEM.md` (events/news expectations)
  - `FACTION_TOGGLE_IMPLEMENTATION.md` + `FACTION_ZONES.md` (faction map conventions)

## UI integration guidance
- Keep the engine **UI-agnostic**: put game rules/state transitions in engine modules; UIs should mostly orchestrate and render.
- Prefer integrating with the PyQt UI (`pyqt_interface.py`). The Textual UI is legacy.
- Some UIs support “demo mode” when imports fail (see the `try/except ImportError` pattern in `pyqt_interface.py`).
