# 4X — Chronicles of the Ether

A single-player 4X strategy game inspired by Alpha Centauri.  Built on a
deep Python game engine (~37 K lines) with a browser-based frontend:
hex-grid galaxy map, hex-grid colony surface, research tech tree, faction
diplomacy, commodity trading, and a full social / economic / political
system that shapes every colony's production, research, and diplomatic
relationships.

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
├── backend/                # FastAPI application (web UI layer)
│   ├── __init__.py
│   ├── main.py             # All /api/* endpoints, singleton Game + ColonyManager
│   ├── colony.py           # Hex tile colony system (planet surface builder)
│   ├── colony_systems.py   # Social / economic / political system definitions
│   │                       #   and modifier / coherence / faction-affinity logic
│   └── hex_utils.py        # Axial hex math, 3D galaxy→2D hex projection
│
├── frontend/               # Browser UI (vanilla JS ES6 modules, no bundler)
│   ├── index.html          # Single-page app shell
│   ├── css/
│   │   ├── main.css        # Design tokens (Alpha Centauri dark palette)
│   │   ├── layout.css      # Three-column layout + HUD
│   │   └── components.css  # Buttons, modals, colony tiles, build menu, toasts,
│   │                       #   systems panel, coherence bar, affinity rows
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
│       │   ├── galaxy.js       # Galaxy map: systems, jump, system detail + market panel
│       │   ├── colony.js       # Planet surface: hex tiles, build/demolish,
│       │   │                   #   SYSTEMS tab (social / economic / political config)
│       │   ├── research.js     # Tech tree browser and research queue
│       │   └── diplomacy.js    # Faction reputation, diplomatic actions,
│       │                       #   system compatibility panel
│       └── ui/
│           ├── hud.js              # HUD bar updates (credits, turn, actions, research bar)
│           ├── modal.js            # Reusable modal dialog + confirm helper
│           └── notifications.js    # Toast notification queue
│
├── lore/
│   ├── energies.json       # 50 energy types with descriptions, stats, and category
│   └── faction_systems.json  # Preferred social / economic / political system for
│                             #   each of the 32 NPC factions (editable data file)
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
4. **Configure** — Assign a **Social**, **Economic**, and **Political** system
   to each colony from the Systems panel.  These choices apply modifier layers
   on top of tile production, unlock unique tradeable commodities, shape
   diplomatic standing, and interact with each other via a coherence score.
5. **Research** — Advance through the tech tree to unlock superior buildings,
   ship components, faction bonuses, and advanced governing system types.
6. **Trade** — Buy and sell commodities at system markets.  Prices shift with
   supply, demand, and galactic events.  Each colony's economic system also
   produces a unique commodity per turn (e.g. Archived Experience, Cognitive
   Cycles, Ritual Tokens).
7. **Diplomacy** — Manage reputation with the galaxy's 30+ factions.  Players
   start at Allied standing (reputation 80) with their chosen faction.  Colony
   system choices passively improve or reduce standing with factions whose
   worldview aligns or conflicts with your configuration.

---

## Character Creation

| Choice | Options |
|--------|---------|
| Class | 11 classes (Explorer, Engineer, Diplomat, Trader, …) |
| Background | 18+ narrative backgrounds, each with stat boosts and talents |
| Species | 14 alien species with distinct biology and cognitive frameworks |
| Faction | Align with one of the galaxy's 30+ major powers (starts Allied) |
| Stats | 7 attributes (VIT, KIN, INT, AEF, COH, INF, SYN) — point-buy |

---

## Colony System

Each colonised planet has a **hex tile grid** (radius 4–6 depending on
planet type) with terrain generated from a seeded RNG — the same planet
always has the same layout across saves.

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

## Colony Systems

Each colony has three orthogonal **governing systems** configured from the
**SYSTEMS tab** in the colony view.  They act as multiplier layers on top of
tile production and interact with research, diplomacy, and trade.

### Economic Systems

| ID | Name | Research Required | Key Modifiers | Unique Commodity |
|----|------|------------------|---------------|-----------------|
| `energy_state` | Energy-State Economy | — | Minerals +15%, Credits +10%, Research −5% | Energy Credits (2/turn) |
| `ritualized_exchange` | Ritualized Exchange | — | Pop Growth +15%, Rep Gain +10% | Ritual Tokens (3/turn) |
| `consciousness_labor` | Consciousness-Labor | Collective Metaconsciousness Networks | Research +20%, Fleet +10% | Cognitive Cycles (2/turn) |
| `memory_economy` | Memory Economy | Bio-Digital Symbiosis | Research +25%, Pop Growth +10% | Archived Experience (2/turn) |
| `time_economy` | Time Economy | Quantum Temporal Dynamics | All Output +8% | Temporal Slices (1/turn) |
| `probability_economy` | Probability Economy | Causal Integrity Theory | Credits +20%, trade price variance −30% | Probability Futures (1/turn) |

### Political Systems

| ID | Name | Research Required | Key Modifiers |
|----|------|------------------|---------------|
| `consensus_field` | Consensus Field Governance | — | Rep Gain +10%, Stability +15, Output −5% |
| `distributed_sovereignty` | Distributed Micro-Sovereignty | — | Trade +20%, Output +5%, Rep Gain −5% |
| `algorithmic_legitimacy` | Algorithmic Legitimacy | Predictive Logic Crystals | Output +15%, Research +10%, Pop −5% |
| `oracle_mediated` | Oracle-Mediated Governance | Primordial Ether Research | Research +20%, Output +5% |
| `temporal_layer` | Temporal Layer Governance | Quantum Temporal Dynamics | Research +15%, Output +10%, Stability −10 |
| `consciousness_swarm` | Consciousness Swarm Deliberation | Collective Metaconsciousness Networks | Research +30%, Output +15%, Pop −10% |

### Social Systems

| ID | Name | Research Required | Key Modifiers |
|----|------|------------------|---------------|
| `resonance_cohesion` | Resonance-Based Cohesion | — | Fleet +10%, Stability +10, Pop +5% |
| `narrative_bound` | Narrative-Bound Societies | — | Rep Gain +15%, Pop +10%, Stability +15 |
| `symbiotic_networks` | Symbiotic Social Networks | — | Pop +20%, Food +10%, Output +5% |
| `memory_pooled` | Memory-Pooled Identity | Bio-Digital Symbiosis | Research +20%, Stability +20, Pop +5% |
| `distributed_selfhood` | Distributed Selfhood | Collective Metaconsciousness Networks | Trade +15%, Output +10%, Stability −5 |
| `rotating_embodiment` | Rotating Embodiment | Trans-Phasic Genetics | Diplomacy +5%, Output +5%, Stability −10 |

### Coherence

Combining systems that complement each other (e.g. Memory-Pooled Identity +
Memory Economy + Consensus Field) earns a **High Coherence** bonus (×1.15 to
all production).  Conflicting combinations create **Friction** (×0.80).

| Score | Label | Production Multiplier |
|-------|-------|-----------------------|
| ≥ +4 | High Coherence | ×1.15 |
| ≥ +1 | Aligned | ×1.05 |
| ≥ −1 | Stable | ×1.00 |
| ≥ −3 | Friction | ×0.90 |
| < −3 | High Friction | ×0.80 |

### System Changes

Systems are free to change but carry a **5-turn cooldown** per category.
Advanced systems are locked behind research — the UI always shows the
specific research requirement.

---

## Research System

The full tech tree is browsable in the **Research** view (keyboard: `R`).
Technologies are organised into prerequisite chains; each node shows:

- Turn cost to complete
- Prerequisites (greyed out if not yet researched)
- Which colony improvements and ship components it unlocks
- Linked energy-type lore tooltip

The active research project is displayed in the HUD bar at all times.
Only one technology can be researched at a time; cancellation is free.

---

## Faction Diplomacy

The **Diplomacy** view (keyboard: `D`) lists all factions sorted by
reputation (Allied → Enemy).

### Reputation Tiers

| Score | Status |
|-------|--------|
| ≥ 75 | Allied |
| ≥ 50 | Friendly |
| ≥ 25 | Cordial |
| ≥ −25 | Neutral |
| ≥ −50 | Unfriendly |
| ≥ −75 | Hostile |
| < −75 | Enemy |

### Starting Relations

Players begin at **Allied (80)** with their chosen faction.  All other
factions start near neutral (−10 to +10).

### Diplomatic Actions

- **Gift** — spend 500 credits per reputation point to improve standing
  (1–20 points per action).

### System Compatibility

The **Diplomacy** view shows a **System Compatibility** panel for each
faction — how well the player's current colony configurations align with
that faction's preferred social / economic / political worldview.  Each
matching system category contributes +5 to a passive affinity score
(−15 to +15) that modifies diplomatic effectiveness.

NPC faction preferred systems are defined in `lore/faction_systems.json`
and can be edited without touching any Python or JS code.

Future hooks (quests, trade deals, missions) are designed to call
`faction_system.modify_reputation()` to nudge relations up or down.

### Zone Benefits

When operating in a faction's controlled systems, reputation determines
available discounts and bonuses:

| Threshold | Benefits |
|-----------|----------|
| Neutral | Faction-focus bonus (trade discounts, repair, research speed) |
| Cordial (25) | Additional 5% trade discount, 10% refuel discount |
| Friendly (50) | Major discounts on trade, repair, refuel, shipyard, research |
| Allied (75) | Maximum benefits on all categories |

---

## Trade System

Commodity markets appear in the **system detail panel** on the galaxy map.
Each inhabited system has a local market seeded from the system's resource
profile and the global economy.

- **Buy** a commodity: costs 1 action point; price reflects current demand.
- **Sell** a commodity: costs 1 action point; price reflects current supply.
- Prices shift each turn based on supply, demand, and galactic events.
- Faction territory modifies buy/sell prices according to reputation tier.

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

Energy types appear as tooltips on research tree nodes and are stored in
`lore/energies.json` for frontend consumption.

---

## API Reference

All routes are prefixed `/api/`.  Static files are mounted last so API
routes always win.

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
| GET | `/api/colony/{planet}` | Full tile grid + production + systems block |
| POST | `/api/colony/{planet}/found` | Found a new colony |
| POST | `/api/colony/{planet}/build` | Build improvement on a tile |
| DELETE | `/api/colony/{planet}/build` | Demolish improvement (50% refund) |
| GET | `/api/colony/{planet}/systems` | Current systems, coherence, options, faction affinity |
| POST | `/api/colony/{planet}/systems` | Change one governing system (research + cooldown gated) |

### Research

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/research/tree` | Full tech tree with completion and unlock status |
| POST | `/api/research/start` | Begin researching a technology |
| POST | `/api/research/cancel` | Cancel active research |
| GET | `/api/research/status` | Current research progress |

### Factions & Diplomacy

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/factions` | All factions + reputation + system_affinity score |
| GET | `/api/faction/{name}` | Faction detail + benefits + system compatibility data |
| POST | `/api/faction/{name}/action` | Diplomatic action (gift, etc.) |

### Trade

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
| GET | `/api/lore/factions` | Faction origin stories and philosophies (static) |

### Character

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/character` | Full character sheet (stats, class, faction, species, XP) |

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | End turn |
| `G` | Galaxy map |
| `C` | Colony view (if planet selected) |
| `R` | Research tree |
| `D` | Diplomacy |

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
- **Everything commented**: every function in backend and frontend carries a
  docstring or block comment explaining intent.

---

## Build Status

| Phase | Contents | Status |
|-------|----------|--------|
| 1 — Foundation | FastAPI app, character creation, CSS framework | ✅ Complete |
| 2 — Galaxy Map | Hex map, system panel, ship navigation | ✅ Complete |
| 3 — Colony System | Planet surface, build/demolish, production | ✅ Complete |
| 4 — Research & Diplomacy | Tech tree, faction UI, energy lore, HUD bar | ✅ Complete |
| 5 — Trade | Market UI, buy/sell flow in system panel | ✅ Complete |
| 5b — Governing Systems | Social/economic/political systems per colony, coherence scoring, faction affinity, unique commodities | ✅ Complete |
| 6 — Polish | Ether overlays, animations, win conditions, quest hooks | 🔲 Pending |

---

## Requirements

```
Python 3.10+
fastapi
uvicorn[standard]
```

No other Python dependencies.  The frontend uses no npm packages — just
vanilla ES6 modules loaded directly by the browser.
