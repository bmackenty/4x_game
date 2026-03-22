# Attributes — Authoritative Reference

This document is the single source of truth for every attribute in the game
that can be nudged up or down by any system: character creation, species
origin, backgrounds, research, colony systems, equipment, or abilities.

When adding a new modifier source, consult this document first. When adding
a new attribute, add it here first.

---

## I. Character Attributes

Seven core stats that define a commander. Set during character creation via
point-buy; modified by species, background, class, equipment, and abilities.

| Key | Full Name | What It Governs |
|-----|-----------|-----------------|
| `VIT` | Vitality | Physical endurance, survival, environmental resistance |
| `KIN` | Kinetics | Physical capability, combat movement, manual skill |
| `INT` | Intellect | Reasoning, research bonus, technical problem-solving |
| `AEF` | Aetheric Field | Etheric sensitivity, mystic ability, ether-based actions |
| `COH` | Coherence | Mental stability, resistance to psychic/temporal disruption |
| `INF` | Influence | Social power, persuasion, faction standing effects |
| `SYN` | Synergy | Interfacing with technology, crew, and symbiotic systems |

**Modifier sources:** species origin, early life, class path,
equipment, abilities, research completions.

---

## II. Colony Production

Per-turn outputs for each colony tile. Modifiers are expressed as flat
bonuses or percentage multipliers applied after tile base values.

| Key | Unit | What Produces It |
|-----|------|-----------------|
| `minerals` | minerals/turn | Extractors, drills, geothermal tiles |
| `food` | food/turn | Biofarms, coastal tiles, forest tiles |
| `research` | RP/turn | Research nodes, neural institutes, crystal tiles |
| `credits` | credits/turn | Trade nexuses, population hubs, market access |
| `ether` | ether/turn | Ether conduits, void anchors, etheric purifiers |
| `population_growth` | % rate | Food surplus, social system, hub improvements |
| `stability` | score (0–100) | Political system, social system, coherence, security |
| `all_output` | multiplier | Coherence bonus/penalty applied to all production |

**Modifier sources:** colony governing systems, coherence score, research
unlocks, tile terrain, improvements built.

---

## III. Research Output

Research points generated per turn and bonuses applied to the research system.

| Key | Unit | Notes |
|-----|------|-------|
| `rp_per_turn` | RP/turn | Base: `INT` stat + background + colony research tiles |
| `research_path_bonus` | RP/turn | +1 per matched research path category |
| `colony_rp_bonus` | RP/turn | Contributed by neural institutes and research nodes |
| `faction_rp_bonus` | RP/turn | Some faction alignments contribute a small bonus |
| `crew_rp_bonus` | RP/turn | Specialist crew roles (e.g. lab technician) |

**Modifier sources:** `INT` stat, colony improvements, research path
selection, crew roles, faction alignment.

---

## IV. Ship Attributes

Stats for the player's ship. Baseline set by starter ship; modified by
research, equipment, upgrades, and station services.

Attributes are stored on a 0–100 normalised scale in `ship_attributes.py`
and grouped into five categories. The header bar derives six gameplay values
from these attributes (see Derived Stats below).

### IV-a. Structural

| Key | Notes |
|-----|-------|
| `hull_integrity` | Physical resilience; drives effective health (HP = `hull_integrity × 10`). |
| `armor_strength` | Absorbs kinetic and energy impacts. |
| `mass_efficiency` | Strength-to-mass ratio; drives cargo capacity (`mass_efficiency × 3 + effective_hull`). |

### IV-b. Propulsion

| Key | Notes |
|-----|-------|
| `engine_output` | Total thrust; secondary driver of jump range. |
| `engine_efficiency` | Energy conversion per jump; reduces fuel cost (multiplier = `1 − (engine_efficiency − 30) / 100`, clamped 0.5–1.5). |
| `ftl_jump_capacity` | Primary driver of jump range (`ftl_jump_capacity / 2 + engine_output / 6`). |
| `maneuverability` | Agility and pilot responsiveness. |

### IV-c. Power & Energy

| Key | Notes |
|-----|-------|
| `reactor_output` | Overall energy generation. |
| `energy_storage` | Capacitor/etheric reserve; drives fuel tank size (`energy_storage × 3 + engine_efficiency × 2.5`, min 2000). |

### IV-d. Sensors

| Key | Notes |
|-----|-------|
| `detection_range` | Primary driver of galaxy-map sensor radius. |
| `scan_resolution` | Detail and fidelity of sensor imagery. |
| `etheric_sensitivity` | Secondary driver of sensor range. Combined formula: `detection_range / 3 + etheric_sensitivity / 6`, min 5. |

### IV-e. AI, Cognition & Sentience

| Key | Notes |
|-----|-------|
| `ai_processing_power` | Computational throughput for autonomous decisions. |
| `ai_convergence` | Fusion of digital logic with emergent etheric cognition. |
| `decision_latency` | Delay between stimulus and AI response. |
| `cognitive_security` | Resistance to hacking or etheric intrusion. |
| `ship_sentience` | Degree of self-awareness and independent reasoning. |
| `human_ai_symbiosis` | Harmony between human intuition and machine logic. |
| `ethical_constraints` | Adherence to safety and moral protocols. |
| `dream_state_processing` | Off-cycle cognition for creativity and pattern discovery. |

### IV-f. Derived Stats (HUD display)

These are computed from the attributes above and shown directly in the UI.

| Derived Stat | Formula / Source |
|---|---|
| `jump_range` | `max(3, int((ftl_jump_capacity/2 + engine_output/6) × hull_fraction))` |
| `fuel` / `max_fuel` | Tank: `max(2000, int(energy_storage×3 + engine_efficiency×2.5))`; cost per jump scaled by `engine_efficiency` |
| `cargo_capacity` | `max(20, int(mass_efficiency×3 + effective_hull))` |
| `hull_hp` | `max(50, int(hull_integrity×10))`, reduced by accumulated `ship_hull_damage` |
| `sensor_range` | `max(5, detection_range/3 + etheric_sensitivity/6)` |
| `fuel_efficiency` | Multiplier `1 − (engine_efficiency−30)/100`, clamped 0.5–1.5 |

**Modifier sources:** research (Engineering, Energetics, Topologies),
station upgrades, equipment slots, crew roles.

---

## V. Diplomacy & Reputation

Values that govern the player's standing with factions and effectiveness of
diplomatic interactions.

| Key | Unit | Notes |
|-----|------|-------|
| `reputation_gain` | % modifier | Passive rep gain rate from aligned colony systems |
| `faction_affinity` | score (–15 to +15) | Per-faction system compatibility score |
| `diplomatic_effectiveness` | % modifier | Scales success rate of diplomatic actions |
| `starting_reputation` | score | Reputation with chosen faction at game start (default 80) |

**Modifier sources:** colony governing systems, `INF` stat, research
(Diplomacy category), faction alignment choice, species traits.

---

## VI. Trade & Economy

Values that affect market pricing and trade income.

| Key | Unit | Notes |
|-----|------|-------|
| `trade_bonus` | % modifier | Bonus applied to all trade income |
| `buy_price` | % modifier | Modifies commodity purchase cost (negative = cheaper) |
| `sell_price` | % modifier | Modifies commodity sale price (positive = more income) |
| `price_variance` | % modifier | Reduces random market fluctuation (stability advantage) |

**Modifier sources:** colony economic systems, faction rep tier, research
(Diplomacy, Energetics), `INF` stat, unique commodities produced.

---

## VII. Unlock Gates

Boolean gates — off until unlocked by the relevant research or condition.
Not numeric, but part of the attribute surface because they are what research
and intersections primarily award.

| Category | What It Controls |
|----------|-----------------|
| `ship` | Ship modules and equipment slots |
| `abilities` | Character and ship combat abilities |
| `crew` | Specialist crew roles |
| `colony` | Colony improvement types |
| `economic` | Economic system options and commodity types |
| `diplomacy` | Diplomatic action types |
| `security` | Colonial security and defense features |
| `social` | Social governing system types |
| `political` | Political governing system types |
| `unit` | Military unit types |

**Modifier sources:** research completions (`research.json`
`extended_unlocks`), intersection unlocks (`intersections.json`).

---

## VIII. Coherence

Coherence is a derived score calculated from the combination of a colony's
three governing systems (Social + Economic + Political). It acts as a
multiplier on all colony production.

| Score | Label | Production Multiplier |
|-------|-------|-----------------------|
| ≥ +4 | High Coherence | ×1.15 |
| ≥ +1 | Aligned | ×1.05 |
| ≥ −1 | Stable | ×1.00 |
| ≥ −3 | Friction | ×0.90 |
| < −3 | High Friction | ×0.80 |

Coherence is not directly nudged — it is an outcome of system combination
choices. However, research and abilities may eventually modify the thresholds
or multipliers.

---

## Modifier Format Convention

When any system (species, background, research, equipment) applies a modifier,
it should reference attribute keys from this document using the following
convention:

```json
{
  "modifiers": {
    "INT": +1,
    "rp_per_turn": +2,
    "minerals": "+10%",
    "jump_range": "+15%",
    "reputation_gain": "+5%"
  }
}
```

- **Flat integer** — added directly to the attribute value
- **Percentage string** — multiplied on top of the base value
- **Unlock gates** — listed as an array under `"unlocks": [...]`

---

## Source Files

| Attribute Group | Defined / Modified In |
|-----------------|----------------------|
| Character stats (VIT–SYN) | `lore/backgrounds.json` (early life pathways), `lore/classes.json`, `lore/species.json` |
| Colony production | `backend/colony.py`, `backend/colony_systems.py` |
| Research output | `backend/main.py` (RP breakdown), `lore/research.json` |
| Ship attributes | `backend/main.py` (ship endpoints), research `extended_unlocks` |
| Diplomacy & reputation | `backend/main.py` (faction endpoints), `lore/faction_systems.json` |
| Trade & economy | `backend/main.py` (market endpoints), colony economic systems |
| Unlock gates | `lore/research.json` (`extended_unlocks`), `lore/intersections.json` |
| Coherence | `backend/colony_systems.py` |
