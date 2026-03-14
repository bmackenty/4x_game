# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Run the game:**
```bash
python3 run.py
```
Opens the browser at http://localhost:8765 with auto-reload enabled.

**Install dependencies:**
```bash
pip install fastapi "uvicorn[standard]"
```


---

## Architecture

```
Python FastAPI backend (port 8765)  ←→  Vanilla JS ES6 modules (no bundler)
```

### The Three Layers

1. **Game engine** (project root `.py` files — `game.py`, `navigation.py`, `research.py`, `factions.py`, etc.): ~37K lines of pure game logic. **Never modify these files.** They are treated as a black-box library.

2. **`backend/`** — Thin REST translation layer. `backend/main.py` holds all `/api/*` endpoints, a singleton `Game` instance, and a `ColonyManager`. It imports from the engine and exposes state via plain dicts. `backend/colony.py` owns the hex-tile colony building system. `backend/hex_utils.py` handles axial hex math and 3D→2D galaxy projection.

3. **`frontend/`** — Vanilla JS SPA. `frontend/js/main.js` is the entry point: boots the app, manages view routing via `switchView()`, and runs a 1-second polling loop. `frontend/js/api.js` is the **only** file that calls `fetch()`. `frontend/js/state.js` is a single shared global state object.

### Key Architectural Rules

- **Game logic never goes in `backend/` or `frontend/`** — the backend only calls engine methods and serializes results.
- **All `fetch()` calls live in `api.js`** — views import named functions from it.
- **Colony state is saved** via `game.colony_state = colony_manager.serialize()` before calling `save_game.save_game()` — the save module itself is untouched.
- **Research gates building**: `ColonyManager.build_improvement()` checks `game.completed_research` directly.
- **Colony terrain is reproducible**: seeded from the planet name so the same planet always generates the same hex layout.
- **Static files are mounted last** in FastAPI so `/api/*` routes always take priority.

### Frontend View System

Views live in `frontend/js/views/`. Each exports a `{ mount(context), unmount() }` object. `main.js` registers them in the `VIEWS` map and calls `switchView(name, context)` to transition. Current views: `setup`, `galaxy`, `colony`, `colonies`, `ship`, `research`, `diplomacy`, `trade`, `character`, `galaxy3d`.

### Hex Coordinate System

Both backend (`hex_utils.py`) and frontend (`hex/hex-math.js`) use **axial (q, r)** coordinates. The 3D galaxy star positions are projected to 2D hex coords in `hex_utils.py`.

### End-of-Turn Flow

`POST /api/game/turn/end` → engine processes turn → `backend/gnn.py` generates the Galactic News Network broadcast → response includes `gnn_summary` and `events` list → frontend shows a GNN modal and toast notifications.
