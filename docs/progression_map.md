# Game Progression Interrelationship Map

> **Purpose:** This document maps every choice and bonus in the game to what it
> affects downstream, and traces every desirable outcome back to the choices that
> produce it.  Read it forward ("I chose X — what do I unlock?") or backward
> ("I want Y — what do I need?").

---

## Table of Contents

1. [Character Creation Cascade](#1-character-creation-cascade)
2. [Research as the Master Gate](#2-research-as-the-master-gate)
3. [Colony Buildings — Full Dependency Table](#3-colony-buildings--full-dependency-table)
4. [Colony Systems (Economic / Political / Social)](#4-colony-systems)
5. [Faction Reputation Cascade](#5-faction-reputation-cascade)
6. [Crew Bonus Pipeline](#6-crew-bonus-pipeline)
7. [Ship Attributes Web](#7-ship-attributes-web)
8. [Experience & Profession Bonuses](#8-experience--profession-bonuses)
9. [Empire-Wide Production Indices](#9-empire-wide-production-indices)
10. [Reverse Lookup — "How do I get X?"](#10-reverse-lookup)

---

## 1. Character Creation Cascade

Character creation sets permanent starting conditions and shapes every
system that follows.  Three choices are made: **Species → Class → Background**.
Then the player distributes 30 stat points across 7 core attributes.

---

### 1a. Species

Only **Terran** is playable.

| Bonus | Value | What it affects |
|-------|-------|-----------------|
| Starting credits | +1,000 | ECI; early building purchases |
| Reputation (all factions) | +5 | Brings all factions slightly toward Neutral at game start |
| Research speed | +10% | RP/turn calculation; KII |

---

### 1b. Character Class

Each class gives a **starting ship**, optional **starting station**, a **credit
bonus**, and several **skill multipliers** that feed into profession, trade,
diplomacy, and research calculations.

| Class | Credits | Starting asset(s) | Key skill bonuses |
|-------|---------|-------------------|-------------------|
| Merchant Captain | +15,000 | Aurora-Class Freighter | trade_discount +10%, negotiation +15% |
| Explorer | +8,000 | Stellar Voyager | exploration +20%, fuel_efficiency +15% |
| Industrial Magnate | +12,000 | Basic Transport + Nanoforge Spires | production_efficiency +20%, construction_discount +15% |
| Military Commander | +10,000 | Aurora Ascendant | combat_effectiveness +25%, crew_morale +20% |
| Diplomat | +12,000 | Celestium-Class Comm Ship | diplomatic_relations +30%, information_access +20% |
| Scientist | +9,000 | Nebula Drifter + Archive of Echoes | research_speed +25%, technology_discount +15% |
| Smuggler | +7,500 | Shadow Runner | stealth_operations +30%, black_market_access +25% |
| Archaeologist | +8,500 | Deep Explorer | artifact_discovery +40%, ancient_tech_bonus +25% |
| Corporate Spy | +11,000 | Phantom Interceptor | intelligence_gathering +35%, infiltration_success +30% |
| Bounty Hunter | +9,500 | Pursuit Vessel | tracking_ability +35%, combat_initiative +20% |
| Terraformer | +13,000 | Genesis Transport + Atmospheric Processor | terraforming_speed +40%, colony_development +30% |

**Downstream effects of class:**
- Higher starting credits → earlier colony founding → faster production loop
- Starting ship stats determine initial fuel range, scanning radius (fog-of-war),
  and combat viability
- Skill bonuses feed into: RP/turn (research_speed), faction reputation gain
  (diplomatic_relations), trade prices (trade_discount), fleet effectiveness
  (combat_effectiveness, crew_morale)

---

### 1c. Background

Backgrounds add flat stat points to one or two of the 7 core attributes.

| Background | Stat bonus(es) | Special trait |
|------------|---------------|---------------|
| Orbital Foundling | KIN+1, SYN+1 | Microgravity Adaptation |
| Deep-Core Miner | VIT+2 | Pressure Hardened |
| AI Scribe | INT+1, COH+1 | Cognitive Compression |
| Etherborn Nomad | AEF+2 | Resonant Sense |
| Reclamation Diver | KIN+1, VIT+1 | Pressure Seal |
| Neo-Monastic Archivist | COH+2 | Memory Sanctuary |
| Bioforge Technician | SYN+1, INT+1 | Bio-Interface |
| Street Synth | KIN+1, INF+1 | Urban Ghost |
| Voidfarer Crew | AEF+1, VIT+1 | Zero Drift |
| Chrono-Refugee | COH+1, AEF+1 | Temporal Flicker |
| Planetary Ranger | VIT+1, INF+1 | Field Survivalist |
| Quantum Savant | INT+2 | Quantum Insight |
| Drift-Station Merchant | INF+2 | Polyglot Interface |
| Nanite Ascetic | COH+1, VIT+1 | Self-Repair |
| Warfleet Remnant | KIN+2 | Combat Instinct |
| Datawalker | SYN+1, COH+1 | Digital Doppel |
| Brewmasters' Acolyte | AEF+1, INF+1 | Liquid Resonance |
| Industrial Heir | INT+1, INF+1 | Corporate Protocol |
| Dust-Wanderer | VIT+1, COH+1 | Storm-Hardened |
| Dreamlink Initiate | AEF+2 | Dream Gate |

---

### 1d. Core Stats → Derived Attributes

All 7 stats start at 30 (base).  Point-buy budget: 30 additional points.  Max: 100 per stat.

| Stat | Full name | Feeds into |
|------|-----------|-----------|
| VIT | Vitality | Health (VIT×10 + COH×5); colony resilience; crew morale floor |
| KIN | Kinetics | Processing Speed (INT+KIN); initiative in combat; evasion |
| INT | Intellect | RP/turn bonus; Processing Speed; Innovation Quotient (INT+SYN) |
| AEF | Aetheric Affinity | Etheric Capacity (AEF×8 + COH×4); ether production bonus; REI |
| COH | Coherence | Health; Etheric Stability (AEF+COH); Resilience Index (VIT+COH); colony coherence multiplier |
| INF | Influence | Social Engineering Potential (INF+SYN); diplomatic_relations modifier; faction rep gain rate |
| SYN | Synthesis | Adaptation Index ((SYN+COH+INT)/3); crew cohesion; alien system compatibility |

**Key derived metrics:**

| Derived metric | Formula | Used for |
|----------------|---------|---------|
| Health | VIT×10 + COH×5 | Crew survival, character durability |
| Etheric Capacity | AEF×8 + COH×4 | Ether channel limit, etheric-gated abilities |
| Processing Speed | INT + KIN | Reaction time, first-strike chance |
| Adaptation Index | (SYN+COH+INT) / 3 | Alien system bonuses, crew cohesion |
| Resilience Index | VIT + COH | Damage soak, crisis resistance |
| Innovation Quotient | INT + SYN | Research bonus modifier, tech adaptation |
| Etheric Stability | AEF + COH | Ether weapon viability, mystic crew synergy |
| Social Engineering | INF + SYN | Diplomatic success rate, faction rep gain modifier |

---

## 2. Research as the Master Gate

Research is the **primary progression gate** in the game.  Almost every advanced
building, colony system, and extended unlock requires completing specific research
projects first.

### 2a. How RP/turn is calculated

```
RP/turn = character_base_RP
        + colony_research_output          ← sum of all tiles producing "research"
        + profession_bonus                ← scales with profession level
        + faction_bonus                   ← e.g. Allied with Veritas Covenant
```

**Sources that feed colony research output:**

| Building | Base research/turn | Best terrain |
|----------|--------------------|-------------|
| Research Node | 3 | crystal (+20%) |
| Bio-Synthesis Lab | 2 | forest (+30%) |
| Academy of Sciences | 4 | coastal (+20%) |
| Psych-Net Hub | 4 + 2 ether | crystal (+30%) |
| Quantum Relay | 3 | crystal (+40%) |
| Neural Institute | 5 + 1 ether | (none — any tile) |
| Xenobiology Station | 4 | forest (+20%) |
| Xenolinguistics Center | 3 + 3 credits | plains/coastal/forest (+10%) |
| Deep Space Observatory | 6 | mountains (+40%) |
| Crystal Resonance Array | 2 + 6 ether | **crystal ×2.0** |
| Synthetic Mind Core | 10 | crystal (+40%) |

---

### 2b. Research Projects → What They Unlock

The table below shows every research project that gates game content, and
exactly what becomes available once it is completed.

| Research project | Unlocks — buildings | Unlocks — colony systems | Unlocks — other |
|-----------------|--------------------|--------------------------|--------------------|
| **Advanced Research** | Research Node | — | — |
| **Advanced Etheric Weaving** | Ether Conduit, Etheric Purifier, Crystal Resonance Array | — | Extended: etheric abilities |
| **Bio-Engineering** | Bio-Synthesis Lab, Atmospheric Processor, Agri-Industrial Complex | Memory Economy (econ) | Extended: bio abilities |
| **Bio-Digital Symbiosis** | — | Memory Economy (econ), Memory-Pooled Identity (social) | Extended: economic functions |
| **Causal Integrity Theory** | — | Probability Economy (econ) | Extended: predictive abilities |
| **Cloaking Technology** | Defense Array | — | Extended: stealth ship functions |
| **Cognitive Enhancement Systems** | Neural Institute, Command Citadel, Psych-Net Hub | — | Extended: crew roles, security functions |
| **Collective Metaconsciousness Networks** | — | Consciousness-Labor (econ), Consciousness Swarm Deliberation (political), Distributed Selfhood (social) | Extended: hive-mind abilities |
| **Mining Automation** | Deep Core Drill, Munitions Factory, Ore Processor, Industrial Fabricator | — | Extended: industrial functions |
| **Null Space Exploration** | Void Anchor, Planetary Shield Generator | — | Extended: void navigation |
| **Plasma Energy Dynamics** | Solar Harvester, Anti-Orbital Battery, Geothermal Tap | — | Extended: energy weapons |
| **Predictive Logic Crystals** | — | Algorithmic Legitimacy (political) | — |
| **Primordial Ether Research** | — | Oracle-Mediated Governance (political) | Extended: etheric divination |
| **Quantum Temporal Dynamics** | Quantum Relay, Deep Space Observatory | Time Economy (econ), Temporal Layer Governance (political) | Extended: temporal abilities |
| **Sentient Architecture** | Synthetic Mind Core, Orbital Drydock | — | Extended: AI crew roles |
| **Symbiotic Existential Anchors** | — | *(future social system)* | Extended: symbiotic abilities |
| **Trans-Phasic Genetics** | — | Rotating Embodiment (social) | Extended: genetic abilities |
| **Xenogenetics** | Xenobiology Station, Xenolinguistics Center | — | Extended: diplomacy options |

---

## 3. Colony Buildings — Full Dependency Table

**Production formula per tile:**
`output = base_production × improvement_terrain_bonus × terrain_modifier × upgrade_multiplier`

**Upgrade multipliers:** Tier 1 = 1.0×, Tier 2 = 1.5×, Tier 3 = 2.2×
**Upgrade costs:** Tier 1→2 = 60% of base cost; Tier 2→3 = 90% of base cost

### 3a. Research-free buildings (available turn 1)

| Building | Cost | Output/turn (base) | Best terrain | Terrain restriction | Empire index |
|----------|------|--------------------|-------------|---------------------|-------------|
| Mineral Extractor | 2,000 | minerals +3 | mountains ×1.5, volcanic ×1.2 | any | REI |
| Biofarm Complex | 1,800 | food +4, credits +1 | plains/forest ×1.4 | any | ECI |
| Trade Nexus | 6,000 | credits +8 | coastal ×1.25 | any (ocean −50%) | ECI; also enables market |
| Population Hub | 4,500 | food +2, credits +3 | plains/coastal ×1.2 | plains, coastal, forest, desert | ECI; +1.5% pop growth |
| Jungle Harvester | 3,500 | food +5, ether +1 | forest ×1.6 | **forest only** | REI |
| Tidal Energy Plant | 4,500 | ether +2, credits +2 | coastal ×1.5, ocean ×1.3 | **coastal/ocean only** | REI |
| Academy of Sciences | 5,000 | research +4 | coastal ×1.2, plains ×1.1 | any | KII |
| Ground Forces Barracks | 6,000 | defense +1, fleet_points +2 | plains ×1.2, desert ×1.1 | any | SPI |
| Shipyard | 12,000 | fleet_points +6 | coastal ×1.2 | any | SPI (scales with refined_ore) |
| Spaceport Hub | 8,500 | credits +12 | plains ×1.3, coastal ×1.2 | any | ECI; also enables market |
| Luxury Habitat Complex | 5,500 | food +3, credits +5 | plains/coastal/forest ×1.2-1.3 | plains, coastal, forest | ECI; +0.8% pop growth |
| Interstellar Bank | 16,000 | credits +20 | coastal ×1.3, plains ×1.2 | any | ECI |

### 3b. Research-gated buildings

| Building | Research required | Cost | Output/turn (base) | Terrain restriction | Empire index |
|----------|-----------------|------|--------------------|---------------------|-------------|
| Research Node | Advanced Research | 3,500 | research +3 | any (crystal ×1.2) | KII |
| Ether Conduit | Advanced Etheric Weaving | 4,000 | ether +2 | any (crystal ×1.6) | REI |
| Etheric Purifier | Advanced Etheric Weaving | 5,500 | ether +2 | **volcanic/geothermal only** | REI |
| Crystal Resonance Array | Advanced Etheric Weaving | 12,000 | ether +6, research +2 | **crystal only** (×2.0) | REI+KII |
| Defense Array | Cloaking Technology | 5,000 | defense +2 | any (mountains ×1.3) | SPI |
| Neural Institute | Cognitive Enhancement Systems | 8,000 | research +5, ether +1 | any | KII |
| Command Citadel | Cognitive Enhancement Systems | 20,000 | defense +3, fleet_points +5 | any (mountains ×1.3) | SPI |
| Psych-Net Hub | Cognitive Enhancement Systems | 11,000 | research +4, ether +2 | any (crystal ×1.3) | KII |
| Quantum Relay | Quantum Temporal Dynamics | 10,000 | research +3 | any (crystal ×1.4) | KII |
| Deep Space Observatory | Quantum Temporal Dynamics | 9,000 | research +6 | **mountains/tundra/desert only** (mtn ×1.4) | KII |
| Bio-Synthesis Lab | Bio-Engineering | 7,000 | food +3, research +2 | any (forest ×1.3) | ECI+KII |
| Atmospheric Processor | Bio-Engineering | 5,000 | food +3, minerals +1 | **tundra/desert/volcanic only** | REI |
| Agri-Industrial Complex | Bio-Engineering | 9,500 | food +6, minerals +3 | any (plains ×1.4) | ECI+REI |
| Deep Core Drill | Mining Automation | 9,000 | minerals +8, food −1 | **mountains only** | REI |
| Munitions Factory | Mining Automation | 10,000 | fleet_points +4, refined_ore +2 | any (plains ×1.2) | SPI |
| Ore Processor | Mining Automation | 8,000 | refined_ore +4 | any (mountains ×1.5) | SPI (amplifier) |
| Industrial Fabricator | Mining Automation | 6,500 | credits +6, minerals +2 | any (plains ×1.2) | ECI |
| Solar Harvester | Plasma Energy Dynamics | 3,000 | minerals +2, credits +1 | any | REI |
| Anti-Orbital Battery | Plasma Energy Dynamics | 14,000 | defense +4 | **mountains/volcanic/tundra only** | SPI |
| Geothermal Tap | Plasma Energy Dynamics | 7,000 | ether +4, minerals +2 | **geothermal/volcanic only** | REI |
| Void Anchor | Null Space Exploration | 15,000 | ether +5 | **void only** | REI |
| Planetary Shield Generator | Null Space Exploration | 18,000 | defense +5 | any (mountains ×1.2) | SPI |
| Xenobiology Station | Xenogenetics | 12,000 | research +4 | any (forest ×1.2) | KII |
| Xenolinguistics Center | Xenogenetics | 7,500 | research +3, credits +3 | any (plains/coastal/forest ×1.1) | KII+ECI |
| Synthetic Mind Core | Sentient Architecture | 22,000 | research +10 | any (crystal ×1.4) | KII |
| Orbital Drydock | Sentient Architecture | 25,000 | fleet_points +18 | any | SPI |

### 3c. Fleet production chain

```
Ore Processor (Mining Automation) → refined_ore per turn
                                    ↓
Shipyard / Orbital Drydock → fleet_points × (1.0 + min(2.0, refined_ore × 0.05))
                                              ↑ capped at +100% bonus
                                              ↑ e.g. 10 refined_ore/turn → +50% fleet output
                                                     40+ refined_ore/turn → +100% (cap)
                              → added to game.fleet_pool (capped 99,999)
```

### 3d. Population growth chain

```
food_production (all buildings) → pop growth
+ Population Hub (×1.5%/building)
+ Luxury Habitat Complex (×0.8%/building)
+ Biofarm Complex (×0.5%/building)
+ Colony social system bonuses (pop_growth modifier)
= raw growth rate (clamped to 8% max)
→ population → tax income (75 credits per 10,000 colonists/turn)
```

### 3e. Terrain modifier cheat sheet

| Terrain | food | minerals | research | ether | credits | credits |
|---------|------|----------|----------|-------|---------|---------|
| plains | ×1.2 | ×0.9 | — | — | — | — |
| forest | ×1.3 | — | ×1.1 | ×1.1 | — | — |
| ocean | ×0.8 | ×0.5 | — | ×0.9 | — | — |
| mountains | ×0.7 | ×1.4 | — | — | — | — |
| tundra | ×0.5 | ×1.1 | — | ×0.8 | — | — |
| volcanic | ×0.0 | ×1.3 | — | ×1.2 | — | — |
| crystal | — | ×1.1 | ×1.2 | ×1.5 | — | — |
| void | ×0.0 | ×0.0 | — | ×2.0 | — | — |
| desert | ×0.4 | ×1.0 | — | ×0.9 | — | — |
| coastal | ×1.1 | ×0.9 | — | — | ×1.2 | — |
| geothermal | ×0.8 | ×1.2 | — | ×1.3 | — | — |

### 3f. Planet type → terrain distribution

| Planet type | Dominant terrain | Grid size | Strategic notes |
|-------------|-----------------|-----------|-----------------|
| Garden World | plains 40%, forest 30%, ocean 20% | radius 6 | Best food + pop growth |
| Terrestrial | plains 30%, mountains 25%, desert 25% | radius 5 | Balanced minerals + food |
| Ocean World | ocean 60%, coastal 20%, mountains 20% | radius 6 | Coastal trade + tidal ether |
| Crystal World | crystal 30%, mountains 30%, void 20% | radius 5 | Best ether + research |
| Jungle World | forest 50%, ocean 20%, mountains 15% | radius 6 | Best food + bio research |
| Lava World | volcanic 40%, mountains 30%, geothermal 30% | radius 4 | Best minerals + ether, no food |
| Frozen World | tundra 40%, ocean 30%, mountains 20% | radius 4 | Mining + geothermal only |
| Desert Planet | desert 50%, mountains 30%, plains 20% | radius 4 | Observatory sites; harsh |
| Industrial World | plains 35%, mountains 25%, desert 20% | radius 5 | General-purpose |

---

## 4. Colony Systems

Each colony independently selects **one Economic, one Political, and one Social
system**.  Changes are subject to a **5-turn cooldown** per category.

Combined modifier layering:
```
colony_production = building_output × (1.0 + economic_modifier)
                                     × (1.0 + political_modifier)
                                     × (1.0 + social_modifier)
                                     × coherence_multiplier
```

The **coherence multiplier** (~0.85–1.15×) rewards selecting mutually compatible
systems (same faction affinities).  Mismatched systems impose a "Chaotic" penalty.

---

### 4a. Economic Systems

| System | Research required | +/− modifiers | Unique commodity (per turn) |
|--------|------------------|---------------|-----------------------------|
| Energy-State Economy | *(none)* | minerals +15%, credits +10%, research −5% | Energy Credits (2) |
| Ritualized Exchange | *(none)* | pop_growth +15%, faction_rep_gain +10% | Ritual Tokens (3) |
| Consciousness-Labor Economy | Collective Metaconsciousness Networks | research +20%, fleet_points +10% | Cognitive Cycles (2) |
| Memory Economy | Bio-Digital Symbiosis | research +25%, pop_growth +10% | Archived Experience (2) |
| Time Economy | Quantum Temporal Dynamics | all_production +8% | Temporal Slices (1) |
| Probability Economy | Causal Integrity Theory | credits +20% | Probability Futures (1) |

### 4b. Political Systems

| System | Research required | +/− modifiers |
|--------|------------------|---------------|
| Consensus Field Governance | *(none)* | faction_rep_gain +10%, stability +15, all_production −5% |
| Distributed Micro-Sovereignty | *(none)* | trade_volume +20%, all_production +5%, faction_rep_gain −5% |
| Algorithmic Legitimacy | Predictive Logic Crystals | all_production +15%, research +10%, pop_growth −5% |
| Oracle-Mediated Governance | Primordial Ether Research | research +20%, all_production +5% |
| Temporal Layer Governance | Quantum Temporal Dynamics | research +15%, all_production +10%, stability −10 |
| Consciousness Swarm Deliberation | Collective Metaconsciousness Networks | research +30%, all_production +15%, pop_growth −10% |

### 4c. Social Systems

| System | Research required | +/− modifiers |
|--------|------------------|---------------|
| Resonance-Based Cohesion | *(none)* | fleet_points +10%, stability +10, pop_growth +5% |
| Narrative-Bound Societies | *(none)* | faction_rep_gain +15%, pop_growth +10%, stability +15 |
| Symbiotic Social Networks | *(none)* | pop_growth +20%, food +10%, all_production +5% |
| Memory-Pooled Identity | Bio-Digital Symbiosis | research +20%, stability +20, pop_growth +5% |
| Distributed Selfhood | Collective Metaconsciousness Networks | trade_volume +15%, all_production +10%, stability −5 |
| Rotating Embodiment Systems | Trans-Phasic Genetics | all_diplomacy +5%, all_production +5%, stability −10 |

### 4d. Highest-research stack (for reference)

The combination that maximises research output once late-game research is done:
- **Economic:** Memory Economy (+25% research) — requires *Bio-Digital Symbiosis*
- **Political:** Consciousness Swarm Deliberation (+30% research, +15% all) — requires *Collective Metaconsciousness Networks*
- **Social:** Memory-Pooled Identity (+20% research, +20 stability) — requires *Bio-Digital Symbiosis*

Combined research modifier: **+75% research** on top of all building output.

---

## 5. Faction Reputation Cascade

### 5a. How reputation is earned

| Source | Amount | Notes |
|--------|--------|-------|
| Game start — home faction | +80 (Allied) | Set at character creation |
| Game start — all factions | +5 (Terran species bonus) | Applies to every faction |
| Diplomatic gift | Up to +20/action | Cost: 500 credits per point |
| Colony system alignment | −15 to +15 | Calculated each turn from `faction_systems.json` prefs vs. your systems |
| Ritualized Exchange economy | +10% to all rep gains | Stacks with other sources |
| Consensus Field / Narrative-Bound social | +10%/+15% to rep gains | Stacks |

### 5b. Reputation thresholds → benefits

| Threshold | Status | Trade | Research | Repair | Refuel | Shipyard | Other |
|-----------|--------|-------|----------|--------|--------|---------|-------|
| < −75 | Enemy | blocked | blocked | blocked | blocked | blocked | Hostile encounters |
| −75 to −50 | Hostile | blocked | blocked | limited | limited | limited | — |
| −50 to −25 | Unfriendly | guarded | — | — | — | — | — |
| −25 to +25 | Neutral | — | — | −10% repair | −5% refuel | — | — |
| +25 to +50 | Cordial | −5% trade | +10% research | −10% repair | −10% refuel | — | Station access |
| +50 to +75 | Friendly | −15% trade | +25% research | −25% repair | −15% refuel | −15% shipyard | Ship mods |
| +75+ | Allied | −30% trade | +50% research | −40% repair | −40% refuel | −40% shipyard | Colony support; SPI bonus |

### 5c. The 10 factions and what they provide

| Faction | Primary focus | Best benefit at Allied |
|---------|--------------|------------------------|
| The Veritas Covenant | Research | +50% research speed; joint research projects |
| Stellar Nexus Guild | Trade | −30% trade prices; exclusive trade routes |
| Harmonic Vitality Consortium | Health/Culture | Genetic optimization; bio-enhancement |
| The Icaron Collective | Technology | AI assistance; neural integration |
| The Gaian Enclave | Mysticism/Ecology | Terraforming; ecological restoration |
| The Gearwrights Guild | Industry | Custom machinery; master-crafted equipment |
| The Scholara Nexus | Research | Educational training; skill enhancement |
| The Harmonic Resonance Collective | Mysticism | Harmonic weapons; shields |
| The Provocateurs' Guild | Culture | Social transformation; art inspiration |
| The Quantum Artificers Guild | Technology | Quantum devices; reality stabilizers |

### 5d. SPI faction bonus

If you are **Allied (rep >75)** with a faction whose primary_focus is **Industry
or Technology**:
- Rep >75 → +25 SPI
- Rep >50 → +12 SPI
- Rep >10 → +4 SPI

### 5e. Colony system alignment → faction affinity

Each faction has preferred Economic, Political, and Social system types.  Your
colony system choices are compared against these preferences each turn and
generate an alignment score (−15 to +15) that feeds into reputation gain.
See `lore/faction_systems.json` for per-faction preferences.

---

## 6. Crew Bonus Pipeline

### 6a. Bonus formula

```
effective_bonus = base_bonus × level_multiplier × morale_multiplier

level_multiplier  = 1.0 + (level - 1) × 0.055     (1.0× at L1 → ~1.50× at L10)
morale_multiplier = 0.75 + (morale / 100) × 0.25  (0.75× at 0% → 1.25× at 150%)
salary            = base_salary × (1.0 + (level - 1) × 0.2)
XP per level      = level × 100  (100 XP for L2, 200 for L3, … 900 for L10)
```

### 6b. Crew roster and ship attributes they improve

| Crew role | Rarity | Ship attributes boosted | Base salary | Recruit at |
|-----------|--------|------------------------|-------------|------------|
| Engineer | Common | engine_efficiency +8, power_efficiency +6 | 200 | Industrial Station, Mining Colony, Trading Hub |
| Navigator | Common | ftl_jump_capacity +10, detection_range +5 | 250 | Trading Hub, Research Station, Frontier Outpost |
| Sensor Specialist | Common | detection_range +12, signal_processing +8 | 220 | Research Station, Military Outpost, Trading Hub |
| Medical Officer | Common | crew_morale +15, crew_efficiency +8 | 280 | Trading Hub, Industrial Station, Research Station |
| Quartermaster | Common | mass_efficiency +10, cargo_security +8 | 240 | Trading Hub, Industrial Station |
| Communications Officer | Common | signal_strength +10, signal_processing +8 | 230 | Trading Hub, Frontier Outpost |
| Weapons Officer | Uncommon | weapon_output +10, targeting_accuracy +8 | 300 | Military Outpost, Frontier Outpost |
| Shield Technician | Uncommon | shield_strength +10, shield_recharge +8 | 280 | Military Outpost, Trading Hub |
| Pilot | Uncommon | maneuverability +12, engine_output +8 | 320 | Military Outpost, Frontier Outpost, Trading Hub |
| Systems Analyst | Uncommon | computing_power +15, system_reliability +8 | 340 | Research Station, Trading Hub |
| Etheric Harmonizer | Rare | etheric_sensitivity +15, etheric_stability +12 | 450 | Research Station, Ancient Site |
| Chief Engineer | Rare | engine_efficiency +15, power_efficiency +12, system_reliability +10 | 500 | Industrial Station, Research Station |
| Xeno-Biologist | Rare | bioscience_capacity +18, crew_morale +8 | 420 | Research Station |
| Void Mystic | Legendary | etheric_sensitivity +20, anomaly_detection +18, crew_morale +10 | 800 | Ancient Site |

### 6c. Crew morale chain

```
Medical Officer (crew_morale +15) ──┐
Void Mystic (crew_morale +10) ──────┤
Xeno-Biologist (crew_morale +8) ────┘
→ morale_multiplier → scales ALL crew bonuses empire-wide
→ also affects: crew_efficiency → fuel consumption, engine output
```

---

## 7. Ship Attributes Web

Ships have **49 attributes** across 8 categories.  Attributes are set by hull/engine
components at build time, then modified by installed upgrades and crew bonuses.

### 7a. Attribute categories and downstream effects

| Category | Key attributes | Downstream effects |
|----------|---------------|-------------------|
| **Structural** | hull_integrity, armor_strength, structural_redundancy | Damage absorption; combat survival turns |
| **Propulsion** | engine_output, engine_efficiency, maneuverability, top_velocity, ftl_jump_capacity | Fuel cost/jump; distance per action; evasion |
| **Power** | reactor_output, energy_storage, power_distribution_efficiency, flux_stability | Power budget for weapons/shields; etheric channel |
| **Defense** | shield_capacity, shield_regeneration, shield_modulation, ecm_strength, point_defense_accuracy | Incoming damage reduction; missile intercept |
| **Offense** | weapon_power, weapon_accuracy, weapon_range, targeting_speed, fire_control_intelligence | DPS; hit chance; first-strike advantage |
| **Sensors** | detection_range, scan_resolution, scan_refresh_rate, target_tracking_stability | Fog-of-war radius; scan quality |
| **Etheric/Special** | etheric_affinity, etheric_resonance, crew_efficiency, crew_morale | Etheric weapon viability; fuel modifier; morale |
| **Signatures** | thermal_signature, electromagnetic_signature, radar_lidar_cross_section, signature_dampening | Detection by hostiles; stealth viability |

### 7b. Fuel cost formula

```
base_fuel = travel_distance × 2.0
adjusted  = base_fuel
          × (1 − engine_efficiency/100)
          × (1 − crew_efficiency/100 × 0.5)
          + ether_friction_coefficient   ← local region drag
          + dangerous_region_penalty     ← +50% in hazard zones
```

**To reduce fuel cost:** Engineer/Chief Engineer crew (engine_efficiency),
Pilot crew (engine_output → indirectly reduces per-hop cost),
Medical Officer (crew_efficiency via crew_morale chain).

### 7c. Attribute sources

| Attribute | Improved by |
|-----------|------------|
| engine_efficiency | Hull components, Engineer crew, Chief Engineer crew, station upgrades |
| detection_range | Sensor components, Navigator crew (+5), Sensor Specialist crew (+12), station upgrades |
| weapon_power/accuracy | Weapon components, Weapons Officer crew, station upgrades |
| shield_capacity/regen | Shield components, Shield Technician crew, station upgrades |
| maneuverability | Hull/engine components, Pilot crew (+12) |
| ftl_jump_capacity | Engine components, Navigator crew (+10) |
| etheric_sensitivity | Etheric components, Etheric Harmonizer crew (+15), Void Mystic crew (+20) |
| computing_power | Computing components, Systems Analyst crew (+15) |
| signature_dampening | Stealth hull (e.g. Eidolon Veil), Chorus of Silence faction-locked components |

### 7d. Faction-locked ship components (examples)

Some hull/engine/weapon components are locked to players who are **Allied with
specific factions**.

| Component | Faction required | Key attribute bonus |
|-----------|-----------------|---------------------|
| Aegis Bastion Hull | Solar Wardens | hull_integrity +35, armor +30 |
| Eidolon Veil Hull | Chorus of Silence | signature_dampening +26, sensor_discipline +10 |
| Whisperstream Coil | Chorus of Silence | engine_efficiency +18, thermal_signature −22 |

---

## 8. Experience & Profession Bonuses

### 8a. Leveling formula

```
XP to reach level N = N × 100  (e.g. level 5 requires 500 total XP)
Max level = 10
Bonus tier unlocks:
  Levels 1–2:  Foundational skills
  Levels 3–5:  Enhanced bonuses, new abilities
  Levels 6–8:  Advanced capabilities
  Levels 9–10: Apex mastery
```

### 8b. Profession categories and pay scales

| Category | Pay range (credits/job) | Bonuses affect |
|----------|------------------------|----------------|
| Etheric | 4,000 – 16,000 | ether production, etheric ship attributes, AEF-derived metrics |
| Engineering | 4,000 – 12,000 | engine attributes, repair costs, production_efficiency |
| Scientific | 5,000 – 15,000 | RP/turn, research speed, KII |
| Medical | 6,000 – 18,000 | crew morale, crew efficiency, Health derived stat |
| Diplomatic | 5,000 – 14,000 | faction rep gain rate, diplomatic_relations modifier |
| Operations | 3,000 – 10,000 | logistics, cargo, fleet_points, REI |
| Artistic | 2,000 – 8,000 | faction_rep_gain (cultural factions), Social Engineering potential |

### 8c. Class → profession alignment

| Class | Natural profession fit | Stat synergy |
|-------|----------------------|--------------|
| Scientist | Scientific | INT → research speed; Innovation Quotient |
| Diplomat | Diplomatic | INF → diplomatic_relations; Social Engineering |
| Military Commander | Operations | KIN → combat_initiative; crew_morale bonus |
| Industrial Magnate | Engineering | SYN → adaptation; production_efficiency |
| Merchant Captain | Operations/Diplomatic | INF → negotiation; trade_discount |
| Explorer | Operations/Scientific | SYN → alien system compatibility; fuel_efficiency |
| Archaeologist | Etheric/Scientific | AEF → artifact detection; ancient_tech_bonus |

---

## 9. Empire-Wide Production Indices

Four indices summarize empire strength.  They are visible in the Colonies overview panel.

### SPI — Strategic Power Index

```
SPI = fleet_strength        ← active_ship.combat_rating + fleet_pool/1000
    + defense_grid          ← sum of defense production across all colonies
    + combat_doctrine       ← character_military_skill × 2
    + intelligence          ← military research progress / 100
    + faction_bonus         ← +4/+12/+25 if Allied with Industry/Tech faction
```

**Best buildings for SPI:**
Orbital Drydock (+18 fleet/turn) > Command Citadel (+3 def, +5 fleet) >
Planetary Shield Generator (+5 def) > Anti-Orbital Battery (+4 def) >
Munitions Factory (+4 fleet, +2 refined_ore) > Shipyard (+6 fleet × ore bonus)

### REI — Resource Extraction Index

```
REI = raw_material_access   ← minerals×8 + refined_ore×6 + visited_systems×2
    + energy_production     ← ether×10 + AEF_stat/5
    + logistics_capacity    ← active_ships×12 + visited_systems×3
    + extraction_aptitude   ← KIN/8 + SYN/10 + COH/12
    + prospecting_advantage ← AEF/6 + visited_systems
    + profession_bonus      ← profession_level/10
    + faction_bonus         ← if Allied with Industry/Exploration faction
```

### KII — Knowledge & Innovation Index

```
KII = research_output × 2   ← all "research" production empire-wide
    + ether_yield           ← all "ether" production
    + academic_buildings × 5 ← count of Research Nodes, Neural Institutes, etc.
    + profession_bonus      ← researcher/scholar professions
```

### ECI — Economic Capability Index

```
ECI = credits_per_turn × 0.5   ← all credit production + population tax
    + trade_volume              ← goods bought/sold via market
    + food_surplus              ← food_production − consumption
    + system modifiers          ← trade_volume bonus from Political/Social systems
```

---

## 10. Reverse Lookup

*"I want X. What choices and actions produce it?"*

---

### To increase RP/turn (research output)

1. **Stats:** High INT (feeds Innovation Quotient, character RP bonus)
2. **Class:** Scientist (+25% research_speed)
3. **Buildings (no research req.):** Academy of Sciences (4/turn)
4. **Buildings (gated):** Research Node (3), Neural Institute (5), Psych-Net Hub (4),
   Quantum Relay (3), Deep Space Observatory (6), Crystal Resonance Array (2),
   Xenobiology Station (4), Xenolinguistics Center (3), Synthetic Mind Core (10)
5. **Planet type:** Crystal World (×1.5 ether/research terrain modifier)
6. **Economic system:** Memory Economy (+25% research) or Consciousness-Labor (+20%)
7. **Political system:** Consciousness Swarm (+30%) or Oracle-Mediated (+20%)
8. **Social system:** Memory-Pooled Identity (+20%) or Distributed Selfhood (+10%)
9. **Faction:** Allied with Veritas Covenant or Scholara Nexus (+50% research speed)
10. **Profession:** Scientific profession leveled up

---

### To increase credits/turn

1. **Buildings:** Interstellar Bank (20), Spaceport Hub (12), Trade Nexus (8),
   Luxury Habitat Complex (5), Industrial Fabricator (6), Xenolinguistics Center (3)
2. **Terrain:** Coastal tiles amplify credit buildings (×1.2 on coastal modifier)
3. **Economic system:** Probability Economy (+20% credits) or Energy-State (+10%)
4. **Political system:** Distributed Micro-Sovereignty (+5% all production)
5. **Population growth:** More colonists → more tax income (75 cr per 10,000/turn)
6. **Faction:** Allied with Stellar Nexus Guild (−30% trade prices → profit margin)
7. **Class:** Merchant Captain (trade_discount +10%)

---

### To increase fleet_points (SPI / military power)

1. **Buildings:** Orbital Drydock (18), Shipyard (6 × ore bonus), Command Citadel (5),
   Munitions Factory (4 + ore), Ground Forces Barracks (2)
2. **Fleet chain:** Ore Processor → refined_ore → Shipyard multiplier (up to +100%)
3. **Economic system:** Consciousness-Labor (+10% fleet_points)
4. **Social system:** Resonance-Based Cohesion (+10% fleet_points)
5. **Faction:** Allied with Industry/Technology faction → SPI faction bonus
6. **Class:** Military Commander (+25% combat_effectiveness)

---

### To increase ether output

1. **Buildings:** Crystal Resonance Array (6 + 2 research; crystal only), Void Anchor (5; void only),
   Geothermal Tap (4; geothermal/volcanic only), Tidal Energy Plant (2; coastal/ocean only),
   Psych-Net Hub (2), Neural Institute (1), Ether Conduit (2), Etheric Purifier (2)
2. **Terrain:** Void (×2.0 ether), Crystal (×1.5), Geothermal (×1.3)
3. **Planet type:** Crystal World (30% crystal terrain) or Lava World (high geothermal)
4. **Stats:** High AEF → REI energy_production sub-score (+AEF/5)

---

### To improve ship combat effectiveness

1. **Crew:** Weapons Officer (+10 weapon_output, +8 targeting), Pilot (+12 maneuver),
   Shield Technician (+10 shield), Chief Engineer (+15 engine_efficiency)
2. **Crew leveling:** Level 10 crew = 1.5× all bonuses
3. **Crew morale:** Medical Officer (+15 morale) → raises all crew bonuses to ×1.25
4. **Station upgrades:** Weapon/shield/engine components at equipped stations
5. **Class:** Military Commander (+25% combat_effectiveness)
6. **Faction:** Allied with faction that unlocks superior hull/engine components

---

### To improve fuel efficiency (longer range)

1. **Crew:** Engineer (+8 engine_efficiency), Chief Engineer (+15), Pilot (+8 engine_output)
2. **Hull/engine components:** High engine_efficiency base value
3. **Class:** Explorer (+15% fuel_efficiency)
4. **Avoid:** Dangerous regions (+50% fuel penalty), heavy cargo loads

---

### To increase faction reputation

1. **Diplomatic gifts:** 500 credits per reputation point (max +20/action)
2. **Colony system alignment:** Match Economic/Political/Social systems to faction preferences
3. **Economic system:** Ritualized Exchange (+10% to all rep gains)
4. **Social system:** Narrative-Bound Societies (+15% rep gains)
5. **Political system:** Consensus Field Governance (+10% rep gains)
6. **Stats:** High INF → Social Engineering Potential → diplomatic effectiveness
7. **Class:** Diplomat (+30% diplomatic_relations)
8. **Profession:** Diplomatic profession leveled up

---

### To unlock Ether Conduit / Crystal Resonance Array / Etheric Purifier

→ Complete **Advanced Etheric Weaving** research (prerequisite varies — check research tree)

### To unlock Neural Institute / Command Citadel / Psych-Net Hub

→ Complete **Cognitive Enhancement Systems** research

### To unlock Quantum Relay / Deep Space Observatory

→ Complete **Quantum Temporal Dynamics** research

### To unlock Synthetic Mind Core / Orbital Drydock

→ Complete **Sentient Architecture** research (highest-tier; multiple prerequisites)

### To unlock Memory Economy + Memory-Pooled Identity (social)

→ Complete **Bio-Digital Symbiosis** research

### To unlock Consciousness Swarm Deliberation (political) + Consciousness-Labor (econ) + Distributed Selfhood (social)

→ Complete **Collective Metaconsciousness Networks** research

---

*Last updated: auto-generated from source analysis of `backend/colony.py`,
`backend/colony_systems.py`, `crew.py`, `factions.py`, `characters.py`,
`classes.py`, `backgrounds.py`, `ship_attributes.py`.*
