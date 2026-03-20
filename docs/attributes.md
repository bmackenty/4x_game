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

**Modifier sources:** species origin, background history, class path,
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

| Key | Unit | Notes |
|-----|------|-------|
| `jump_range` | game units | Maximum distance per jump |
| `fuel_capacity` | units | Tank size; determines range between refuels |
| `fuel_efficiency` | % modifier | Reduces fuel consumed per jump |
| `cargo_capacity` | units | Total cargo hold volume |
| `hull_integrity` | HP | Effective health; modified by armour research |
| `sensor_range` | hex radius | Detection radius on galaxy map |
| `drive_efficiency` | % modifier | Affects propulsion and jump speed |
| `combat_rating` | score | Ship combat effectiveness |

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
| Character stats (VIT–SYN) | `lore/backgrounds.json`, `lore/classes.json`, `lore/species.json` |
| Colony production | `backend/colony.py`, `backend/colony_systems.py` |
| Research output | `backend/main.py` (RP breakdown), `lore/research.json` |
| Ship attributes | `backend/main.py` (ship endpoints), research `extended_unlocks` |
| Diplomacy & reputation | `backend/main.py` (faction endpoints), `lore/faction_systems.json` |
| Trade & economy | `backend/main.py` (market endpoints), colony economic systems |
| Unlock gates | `lore/research.json` (`extended_unlocks`), `lore/intersections.json` |
| Coherence | `backend/colony_systems.py` |
