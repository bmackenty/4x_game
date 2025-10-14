**Project Title:** Turn-Based 4X Strategy Game (Hex-Grid, 3D, Rust Server)  
**Version:** 1.0  
**Date:** July 10, 2025  

---

## 1. Executive Summary
This document outlines the comprehensive project scope, architecture, and development roadmap for a turn-based 4X strategy game built using vanilla JavaScript with Three.js on the client side and a Rust-based authoritative server backed by MariaDB.

The game will feature the classic pillars of 4X gameplay—Exploration, Expansion, Exploitation, and Extermination—on a zoomable, hexagonal 3D map. Players will control civilizations, manage resources, and compete against both AI-driven bots and human opponents in matches of up to five participants.

Initial development will focus on a single-player vertical slice, culminating in a playable demo within four months. Subsequent phases will introduce full multiplayer support and additional game systems.

---

## 2. Project Vision
The goal is to deliver a polished, web-based 4X strategy experience accessible in modern browsers without plugins. Emphasis will be on modular architecture, data-driven design, and clear separation between client and server responsibilities. 

The client will handle rendering, user input, and local ECS simulation for a responsive UI, while the Rust server will serve as the authoritative source of truth, resolving game turns, managing persistent storage, and broadcasting state updates to connected players.

**Key deliverables include:**
1. A zoomable, procedural or predefined 3D hex map rendered with Three.js.  
2. A full ECS implementation on both client (ECSY) and server (shared component definitions).  
3. A turn-based game loop integrating user input, AI decision-making (via behavior trees), simulation, and rendering.  
4. An authoritative Rust server exposing REST endpoints and WebSocket channels, persisting game state in MariaDB, and logging for debugging.  
5. A four-phase roadmap culminating in a vertical slice playable demo with AI and basic multiplayer lobby.  

---

## 3. Objectives and Success Criteria

### 3.1 Objectives
* **Responsive UI:** Use vanilla-DOM overlays and Three.js for seamless camera control and HUD elements.  
* **Robust ECS:** Data-driven component-system design to facilitate easy extension and maintenance.  
* **AI Competence:** Behavior3js-based decision trees for AI bots capable of exploration, expansion, and basic strategy.  
* **Authoritative Server:** Rust server that reliably processes turns, resolves conflicts, stores history, and broadcasts state.  
* **Scalability:** Architecture designed to support up to 10,000 concurrent entities and five simultaneous players per match.  

### 3.2 Success Criteria
* **Functional Demo:** By Month 4, deliver a working vertical slice with two human players and three AI opponents on a small map.  
* **Performance:** Client-side rendering must handle zoomable 3D hex-grid at interactive frame rates; server must resolve turns within 500ms under typical load.  
* **Reliability:** Server stability under match creation, join, save/load, and turn resolution operations.  
* **Extensibility:** Code architecture must allow easy addition of new systems (trade, diplomacy) without major refactoring.  

---

## 4. Scope

### 4.1 In Scope
* **Client:** 3D rendering (Three.js), vanilla-DOM UI, ECSY setup, input handling, AI integration, networking client.  
* **Server:** REST API (match creation, join, state fetch, action submission), WebSocket state broadcast, ECS-based turn resolution, MariaDB persistence, logging middleware.  
* **AI:** Behavior3js for layered decision trees (explore, move, build).  
* **Persistence:** MariaDB database schema for matches, players, actions, game states, and logs.  
* **Multiplayer Lobby:** Basic UI for match creation, player join, and lobby management.  

### 4.2 Out of Scope (Initial Phases)
* **Advanced Diplomacy/Trade:** To be introduced after vertical slice.  
* **Modding Support:** Not part of initial release.  
* **Mobile App Wrappers:** Browser-only deployment.  
* **Localization & Accessibility:** Deferred until core mechanics are stable.  

---

## 5. Architecture Overview

### 5.1 Client-Server Separation
* **Client (vanilla JS + Three.js):** Handles rendering loop at ~60Hz, local ECS tick for animation, user inputs, and UI. Advances game state on “End Turn” events by sending batched player actions to server.  
* **Server (Rust):** Authoritative turn resolver using shared ECS definitions, persists state to MariaDB, logs key events, and broadcasts updated game state over WebSockets.  

### 5.2 ECS Design Pattern
* **Entities:** Defined by unique IDs; components store data (Position, TileInfo, UnitStats, CityStats, etc.).  
* **Components:** Flat data objects; located in memory pools for cache efficiency.  
* **Systems:** Modular functions operating over component sets (RenderSystem, MovementSystem, ResourceSystem, AISystem, TurnSystem). Systems run in a predictable sequence.  

### 5.3 Networking Flow
1. **Match Management:** Client uses REST to create and join matches; server stores match metadata.  
2. **Turn Submission:** Client POSTs array of TurnAction JSON objects to `/api/matches/:id/actions`.  
3. **Authoritative Resolution:** Server Tick (triggered when all players submit or timeout) runs TurnSystem, updates world state, writes to `game_states` table.  
4. **State Broadcast:** New state is serialized and pushed via WebSocket to all connected clients.  
5. **Client Update:** Upon receiving new state, client deserializes into ECS world and re-renders scene.  

---

## 6. Tech Stack and Tools

| Layer | Technology | Rationale |
| ------ | ----------- | ---------- |
| Client Rendering | Three.js | Powerful WebGL abstraction, easy mesh and scene management |
| ECS (client) | ECSY | Lightweight JS ECS with good community support |
| AI | Behavior3js | Standard JS behavior tree library for layered decision logic |
| UI | Vanilla DOM + CSS | Low overhead, full control |
| Networking Client | Axios (REST) + native WebSockets | Simple HTTP and WS integration |
| Build Tooling | Vite | Fast bundling, ES module support, easy config |
| Server Framework | Actix-web (Rust) | High performance, asynchronous, robust ecosystem |
| Database | MariaDB | ACID-compliant SQL, self-hosted to Linode migration path |
| ORM / DB Layer | SQLx (Rust) | Compile-time checked queries, async support |
| Logging | Rust log + env_logger | Configurable log levels, easy integration |
| Shared Protocol | TypeScript type definitions (optional) / JSON schemas | Ensures consistency of payloads across client and server |

---

## 7. Module and Folder Structure

**Client**
client/
├── assets/
│ ├── models/ # .glb files for cities, units
│ └── textures/ # Hex tile textures, UI sprites
├── ecs/
│ ├── components/ # Position, Tile, Unit, City, Resource
│ └── systems/ # InputSystem, AISystem, MovementSystem, ResourceSystem, TurnSystem, RenderSystem
├── render/ # Three.js scene, camera, lights, hex-grid generator
├── ui/ # HUD, menus, vanilla-DOM controls & CSS
├── ai/ # Behavior3js tree definitions and configs
├── network/ # axios clients, WS handlers
├── main.js # Bootstraps ECS, rendering, game loop
└── index.html # Canvas and root DOM elements

**Server**
server/
├── src/
│ ├── api/
│ │ ├── matches.rs
│ │ ├── actions.rs
│ │ ├── state.rs
│ ├── game/
│ │ ├── components.rs # mirrored from client
│ │ └── systems.rs # TurnSystem, AISystem
│ ├── db/
│ │ ├── schema.rs # SQLx migrations
│ │ └── models.rs
│ └── logging.rs # centralized logging setup
├── Cargo.toml
└── build.rs

**Shared**
shared/
├── protocol/
│ ├── TurnAction.json
│ └── GameState.json
└── config/
└── constants.ts (or .rs) # map limits, timeouts


---

## 8. Database Schema

**matches**
| Column | Type | Description |
| ------- | ---- | ----------- |
| id | INT, PK, AI | Unique match identifier |
| name | VARCHAR(64) | Match name |
| max_players | INT | Maximum number of players |
| created_at | DATETIME | Timestamp of creation |

**match_players**
| Column | Type | Description |
| ------- | ---- | ----------- |
| id | INT, PK, AI | Unique record ID |
| match_id | INT, FK | Associated match |
| player_id | VARCHAR(36) | UUID of player |
| name | VARCHAR(32) | Player display name |
| joined_at | DATETIME | Timestamp of join |

**game_states**
| Column | Type | Description |
| ------- | ---- | ----------- |
| id | INT, PK, AI | State record ID |
| match_id | INT, FK | Associated match |
| turn_number | INT | Turn index |
| state_json | MEDIUMTEXT | Serialized ECS world state |
| created_at | DATETIME | Timestamp of record |

**actions**
| Column | Type | Description |
| ------- | ---- | ----------- |
| id | INT, PK, AI | Action record ID |
| match_id | INT, FK | Associated match |
| player_id | VARCHAR(36) | UUID of player |
| action_json | MEDIUMTEXT | Serialized action payload |
| submitted_at | DATETIME | Timestamp of submission |

**logs**
| Column | Type | Description |
| ------- | ---- | ----------- |
| id | INT, PK, AI | Log entry ID |
| match_id | INT, FK | Associated match (optional) |
| level | VARCHAR(10) | INFO, WARN, ERROR |
| message | TEXT | Log message |
| logged_at | DATETIME | Timestamp of log |

---

## 9. Core Engine Diagram

[Input Events] ──▶ InputSystem ──▶ ECS World ──▶ AISystem ──▶ TurnSystem ──▶ RenderSystem ──▶ [Three.js Canvas]
│ │
▼ ▼
NetworkSystem ResourceSystem

On End Turn: Client ▶ POST actions ▶ Server ECSWorld ▶ resolve ▶ persist ▶ WS broadcast ▶ Client updates ECSWorld


---

## 10. Development Roadmap

**Phase 1: Foundations (Month 0–1)**
* Initialize Git repo; configure Vite for client and Cargo workspace for server.
* Create basic Three.js scene with camera controls and procedurally generated hex grid mesh.
* Integrate ECSY; define Position and Tile components; stub RenderSystem to instantiate meshes per entity.
* Establish shared protocol JSON schemas; scaffold Rust project and verify cross-language JSON compatibility.

**Phase 2: Core Mechanics & AI (Month 1–2)**
* Implement MovementSystem (hex pathfinding using A* in JS), ResourceSystem (tile yields), CitySystem (city creation/production).
* Define Behavior3js trees for basic AI: explore unvisited tiles, found new cities, harvest resources.
* Build turn loop: UI "End Turn" button that triggers client-side mock persistence and updates ECS world locally.
* Add vanilla-DOM HUD displaying current turn, active player, resource counts.

**Phase 3: Server & Persistence (Month 2–3)**
* Deploy MariaDB locally; create initial schema using SQLx migrations.
* Implement Rust server with Actix-web: REST endpoints for match lifecycle and action submission.
* Develop server-side ECSWorld using shared component definitions; implement TurnSystem to apply actions authoritatively.
* Wire client to real backend: on "End Turn", POST actions; on load/join, GET latest game state; deserialize into ECS world.
* Integrate log/env_logger in Rust to record turn start/end, player actions, AI decisions.

**Phase 4: Multiplayer Skeleton & Demo (Month 3–4)**
* Implement WebSocket channels in Rust for broadcasting game state updates.
* Build lobby UI: create/join match, list players, ready checks.
* Enable client WebSocket connection; update ECS world on incoming state messages.
* Test 2-human & 3-bot match on 10×10 hex map; verify turn resolution latency <500ms.
* Polish camera zoom/pan, HUD overlays for debug logs, basic styling for menus.
* **Deliverable:** Playable vertical slice: five-player match (3 AI), turn-based 4X core loop, server-authenticated state.

**Phase 5 and Beyond (Post Month 4)**
* Add persistence export/import features if desired.
* Introduce trade, diplomacy, advanced AI heuristics, and scenario editor.
* Implement unit/integration tests and CI with GitHub Actions.
* Optimize performance: spatial partitioning, Web Workers for pathfinding, server scaling.
* Plan for mobile-responsive UI and eventual app wrapper (Electron/Cordova).

---

## 11. Risks & Mitigations

* **Complexity of Shared ECS Code:** Keeping client/server ECS definitions synchronized may introduce DRY violations.  
  *Mitigation:* Automate shared schema generation via JSON schemas or build scripts.  
* **Performance Bottlenecks:** Large entity counts (10,000+) may slow down JS pathfinding or rendering.  
  *Mitigation:* Use level-of-detail meshes, Web Workers for heavy computations, spatial indexing.  
* **Server Latency:** Authoritative server resolution under heavy load could exceed target response times.  
  *Mitigation:* Optimize Rust systems, use async DB operations, consider in-memory caching for interim states.  
* **Scope Creep:** Adding features beyond core 4X pillars may delay vertical slice.  
  *Mitigation:* Strict adherence to roadmap and MVP scope; backlog feature requests for post-demo.  

---

## 12. Conclusion
This project scope and description provides a clear, detailed blueprint for building a turn-based 4X strategy game in vanilla JavaScript and Three.js, powered by a Rust/MariaDB authoritative backend.

The outlined folder structure, tech-stack rationale, ECS architecture, API design, database schema, and four-month roadmap establish a strong foundation for rapid development of a vertical slice demo. Following this plan will yield a playable, extensible prototype by the end of Month 4, paving the way for further expansion into rich strategic systems and full multiplayer support.


