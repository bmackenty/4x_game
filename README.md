# 4X Galactic Empire — Web Edition

A single-player 4X strategy game inspired by Alpha Centauri.  Built on a
deep Python game engine (~37 K lines) with a new browser-based frontend:
hex-grid galaxy map, hex-grid colony surface, research tree, faction
diplomacy, and commodity trading.

---

## Quick Start

```bash
pip install fastapi "uvicorn[standard]"
python run.py
```

The launcher starts the FastAPI server on **http://localhost:8765** and opens
your default browser automatically.  Press **Ctrl+C** to shut down.

---

## Architecture

```
Python FastAPI backend  ←→  Vanilla JS + HTML5 Canvas frontend
     (port 8765)                   (served as static files)
```

The game engine lives entirely in the project-root Python modules and is
**never modified** — `backend/` is a thin REST translation layer, and
`frontend/` is the browser UI.

### Directory Layout

```
4x_game/
├── run.py                  # Single-command launcher (uvicorn + browser open)
│
├── backend/                # FastAPI application (new web UI layer)
│   ├── __init__.py
│   ├── main.py             # All /api/* endpoints, singleton Game + ColonyManager
│   ├── colony.py           # Hex tile colony system (planet surface builder)
│   └── hex_utils.py        # Axial hex math, 3D galaxy→2D hex projection
│
├── frontend/               # Browser UI (vanilla JS ES6 modules, no bundler)
│   ├── index.html          # Single-page app shell
│   ├── css/
│   │   ├── main.css        # Design tokens (Alpha Centauri dark palette)
│   │   ├── layout.css      # Three-column layout + HUD
│   │   └── components.css  # Buttons, modals, colony tiles, build menu, toasts
│   └── js/
│       ├── main.js         # Entry point, view router, 1 s polling loop
│       ├── api.js          # All fetch() calls — only file that uses fetch
│       ├── state.js        # Single global state object (plain JS)
│       ├── hex/
│       │   ├── hex-math.js     # Axial coordinate math (mirrors hex_utils.py)
│       │   ├── hex-render.js   # Canvas rendering: galaxy map + colony grid
│       │   └── hex-input.js    # Pan, zoom, click on hex canvas
│       ├── views/
│       │   ├── setup.js        # Character creation (multi-step form)
│       │   ├── galaxy.js       # Galaxy map: systems, jump, system detail panel
│       │   ├── colony.js       # Planet surface: hex tiles, build/demolish
│       │   ├── research.js     # Tech tree (Phase 4 — coming soon)
│       │   └── diplomacy.js    # Faction diplomacy (Phase 4 — coming soon)
│       └── ui/
│           ├── hud.js              # HUD bar updates (credits, turn, actions)
│           ├── modal.js            # Reusable modal dialog + confirm helper
│           └── notifications.js    # Toast notification queue
│
├── lore/
│   └── energies.json       # 50 energy types (Phase 4 — to be generated)
│
└── [game engine — DO NOT MODIFY]
    game.py, navigation.py, research.py, factions.py, economy.py,
    systems.py, events.py, ship_builder.py, save_game.py, species.py,
    characters.py, energies.py, …  (90+ files, ~37 K lines)
```

---

## Gameplay Overview

The loop closely follows Alpha Centauri:

1. **Explore** — Navigate a 3D galaxy of 30–40 star systems on the hex map.
   Each jump costs one action point and fuel.
2. **Colonise** — Land on habitable planets to found colonies.  Each colony
   gets a procedurally generated hex tile grid (terrain seeded from planet
   name for reproducibility).
3. **Build** — Place improvements on colony tiles to generate resources per
   turn (minerals, food, research, ether, credits).  Better improvements are
   locked behind research.
4. **Research** — Advance through the tech tree to unlock superior buildings,
   ship components, and faction bonuses.
5. **Diplomacy** — Manage reputation with the galaxy's factions.  Trade
   favours, complete missions, or risk conflict.
6. **Trade** — Buy and sell commodities at system markets.  Prices shift with
   supply, demand, and galactic events.
7. **Win** — Achieve domination, transcendence (research chain), or survive
   to the turn limit.

---

## Character Creation

| Choice | Options |
|--------|---------|
| Class | 11 classes (Explorer, Engineer, Diplomat, Trader, …) |
| Background | 18+ narrative backgrounds, each with stat boosts and talents |
| Species | 14 alien species with distinct biology and cognitive frameworks |
| Faction | Align with one of the galaxy's major powers |
| Stats | 7 attributes (VIT, KIN, INT, AEF, COH, INF, SYN) — point-buy |

---

## Colony System

Each colonised planet has a **hex tile grid** (radius 4–6 depending on
planet type) with terrain generated from a seeded RNG — the same planet
always has the same layout.

### Terrain Types

| Terrain | Character |
|---------|-----------|
| Plains | Good for farming |
| Forest | Bonus food and minerals |
| Mountains | Best for mining (+50% Mineral Extractor) |
| Ocean | Trade hub bonus, poor for most buildings |
| Crystal | Research bonus (+20–60%) |
| Void Rift | Ether Conduit and Void Anchor only |
| Volcanic | Mineral bonus, food penalty |
| Tundra / Ice | Limited production |
| Geothermal | Mining and ether bonus |
| Coastal | Trade and food bonus |

### Improvements (15 total)

| Improvement | Cost | Unlock | Production |
|-------------|------|--------|------------|
| Mineral Extractor | 2,000 | — | +3 minerals (+50% mountains) |
| Biofarm Complex | 1,800 | — | +4 food, +1 credit |
| Trade Nexus | 6,000 | — | +8 credits |
| Population Hub | 4,500 | — | +2 food, +3 credits |
| Solar Harvester | 3,000 | Plasma Energy Dynamics | +2 minerals, +1 credit |
| Research Node | 3,500 | Advanced Research | +3 research |
| Ether Conduit | 4,000 | Advanced Etheric Weaving | +2 ether |
| Defense Array | 5,000 | Cloaking Technology | +2 defense |
| Etheric Purifier | 5,500 | Advanced Etheric Weaving | +2 ether |
| Bio-Synthesis Lab | 7,000 | Bio-Engineering | +3 food, +2 research |
| Neural Institute | 8,000 | Cognitive Enhancement Systems | +5 research, +1 ether |
| Deep Core Drill | 9,000 | Mining Automation | +8 minerals (mountains only) |
| Quantum Relay | 10,000 | Quantum Temporal Dynamics | +3 research |
| Xenobiology Station | 12,000 | Xenogenetics | +4 research |
| Void Anchor | 15,000 | Null Space Exploration | +5 ether (void rifts only) |

Research-gating improvements is the core **research → build** loop.

---

## Energy Lore

The game features 50 distinct energy types across 7 categories, each with
lore descriptions, efficiency ratings, safety levels, and links to the
research tree:

| Category | Colour | Examples |
|----------|--------|---------|
| Physical & Technological | Cyan | Kinetic, Thermal, Plasma, Quantum Flux, Dark Matter |
| Mystical & Etheric | Purple | Etheric, Leyline, Soul, Aether Flames, Void Essence |
| Psychic & Consciousness | Gold | Psionic, Empathic Resonance, Noospheric, Dream |
| Exotic & Speculative | Orange | Hyperdimensional, Tachyonic, Anima, Probability Fields |
| Utility & Industrial | Teal | Synthetic Bio-Energy, Geo-Energy, Photonic Power |
| Ship/Faction-Specific | Varies | Concordant Harmony, Veritas Pulse, Quantum Choir |
| Chaotic | Red | Chaotic Potential (banned by Icaron Collective after three moons vanished) |

Energy types appear as tooltips on research tree nodes and as ether zone
overlays on the galaxy map (Phase 4+).

---

## API Reference

All routes are prefixed `/api/`.  Static files are mounted last so API routes
always win.

### Game Lifecycle
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/game/new` | Start a new game (character creation payload) |
| GET | `/api/game/state` | Poll current state (HUD, credits, turn, research) |
| POST | `/api/game/turn/end` | End turn; returns event list for toasts |
| POST | `/api/game/save` | Save to named slot |
| GET | `/api/game/saves` | List save files |
| POST | `/api/game/load` | Load a save file |
| GET | `/api/game/options` | Character creation choices (classes, species, …) |

### Galaxy & Navigation
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/galaxy/map` | All systems projected to 2D axial hex coords |
| GET | `/api/system/{name}` | System detail + planet list |
| POST | `/api/ship/jump` | Jump ship to (x, y, z) — costs 1 action |
| GET | `/api/ship/status` | Current ship stats (fuel, cargo, coords) |

### Colony
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/colony/all` | Summary list of all owned colonies |
| GET | `/api/colony/improvements` | Improvement catalogue with research unlock status |
| GET | `/api/colony/{planet}` | Full tile grid + production for one colony |
| POST | `/api/colony/{planet}/found` | Found a new colony |
| POST | `/api/colony/{planet}/build` | Build improvement on a tile |
| DELETE | `/api/colony/{planet}/build` | Demolish improvement (50% refund) |

### Research (Phase 4)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/research/tree` | Full tech tree with completion status |
| POST | `/api/research/start` | Begin researching a technology |
| POST | `/api/research/cancel` | Cancel active research |
| GET | `/api/research/status` | Current research progress |

### Factions & Diplomacy (Phase 4)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/factions` | All factions + player reputation |
| GET | `/api/faction/{name}` | Faction detail + benefits |
| POST | `/api/faction/{name}/action` | Gift / mission / provoke |

### Trade (Phase 5)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/market/{system}` | Commodity prices at a system |
| POST | `/api/trade/buy` | Buy commodities (costs 1 action) |
| POST | `/api/trade/sell` | Sell commodities (costs 1 action) |

### Lore
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/lore/energies` | All 50 energy types (static JSON) |
| GET | `/api/lore/species` | Species database |

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | End turn |
| `G` | Galaxy map |
| `C` | Colony view (if planet selected) |
| `R` | Research tree (Phase 4) |
| `D` | Diplomacy (Phase 4) |

---

## Design Principles

- **Strict separation**: game logic lives in the project-root Python modules
  and is never modified.  `backend/` only exposes it via REST.
- **Single fetch source**: `frontend/js/api.js` is the only file that calls
  `fetch()`.  All views import from it.
- **Reproducible worlds**: colony terrain is seeded from the planet name so
  the same planet always has the same layout, even across saves.
- **Research gates building**: `ColonyManager.build_improvement()` checks
  `game.completed_research` directly — no special-casing required.
- **Non-invasive save extension**: colony state is saved via
  `game.colony_state = colony_manager.serialize()` before `save_game.save_game()`.
  The save module is untouched.

---

## Build Status

| Phase | Contents | Status |
|-------|----------|--------|
| 1 — Foundation | FastAPI app, character creation, CSS framework | ✅ Complete |
| 2 — Galaxy Map | Hex map, system panel, ship navigation | ✅ Complete |
| 3 — Colony System | Planet surface, build/demolish, production | ✅ Complete |
| 4 — Research & Diplomacy | Tech tree, faction UI, energy lore | 🔲 Pending |
| 5 — Trade | Market UI, buy/sell flow | 🔲 Pending |
| 6 — Polish | Ether overlays, animations, win conditions, save UI | 🔲 Pending |

---

## Requirements

```
Python 3.10+
fastapi
uvicorn[standard]
```

No other Python dependencies.  The frontend uses no npm packages — just
vanilla ES6 modules loaded directly by the browser.
