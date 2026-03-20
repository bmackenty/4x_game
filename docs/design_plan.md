# Plan: Narrative & Gameplay Coherence Redesign

---

## NEXT TASK: Remove Command Path from Character Creation

### Context

Character creation has 7 steps. Steps 3 (Command Path) and 4 (Background History) are redundant:
- **Command Path** (54 classes): no stat bonuses, no meaningful choice weight — its only job is to constrain which 4 backgrounds are available. Professional Specialization already covers "career role."
- **Background History** (20 options): the mechanically real early-life choice — flat stat bonuses and a unique talent. This is the one the user values.
- Decision: remove Command Path entirely, leaving Background unconstrained (all 20 freely available).

### What Changes

**1. `backend/main.py`**
- `NewGameRequest` Pydantic model: make `character_class` optional with default `"Explorer"`
  ```python
  character_class: str = "Explorer"
  ```
- Starting ship lookup (lines ~959-963): wrap in a `.get()` with fallback so a missing/default class never crashes

**2. `frontend/js/views/setup.js`**
- Remove "Command Path" from the steps array (currently step index 2 of 7; line ~48)
- Remove the class card grid tab render (lines ~146-157)
- Remove `form.character_class` from the form object and card-click handler
- Remove class validation from the submit guard (line ~599 checks `!form.character_class`)
- Remove `character_class` from the `newGame()` call (line ~626)
- All 20 backgrounds become freely selectable — remove any filtering that hid non-class-compatible backgrounds

**3. `frontend/js/api.js`** (optional cleanup)
- Update JSDoc on `newGame()` to remove `character_class` from documented shape (line ~65)

**4. `lore/classes.json`**
- No change — keep as lore reference, just not surfaced in character creation

**5. `docs/attributes.md`**
- Remove "classes.json" from the source files table in Section I (backgrounds and species remain)

### Key Risk (already verified safe)
The game engine `game.py` reads `character_data.get('character_class', 'Explorer')` — it already has a fallback default, so passing nothing (or `"Explorer"`) is safe.

### Verification
1. `python3 run.py` — start new game, confirm setup has 6 steps (no Command Path tab)
2. Complete character creation — confirm no 422 validation error from backend
3. Confirm all 20 backgrounds are selectable regardless of other choices
4. Confirm game initializes correctly and starting ship is assigned (Explorer default)

---

## Context

The game has accumulated rich lore (163 research projects, 54 classes, 30 factions,
49 energy types, 20 backgrounds) but the systems weren't designed together from a
single coherent vision. The result: the progression graph exists but doesn't *tell a
story*. The user wants to redesign so that every choice — from character creation
through late-game research — feels like a natural next chapter of the same narrative.
No code changes yet. This is a design methodology and ordering-of-work document.

---

## The Core Problem, Precisely Stated

A game has **narrative coherence** when a player can say:
> "I am an X who chose Y, so of course I'm researching Z and aligned with faction W."

Right now the game has the pieces but not that sentence. The research tree, colony
systems, faction bonuses, and character abilities all exist in parallel without enough
cross-referencing. Research names don't consistently imply what they unlock. Faction
philosophies don't clearly connect to which research tracks they accelerate. A
"Diplomat" class and a "Scientist" class may end up with identical mid-game options.

There's also a **lore/implementation gap** that must be decided before redesigning:
- Lore: 163 research projects, 54 classes, 30 factions
- Backend (currently implemented): ~11 research gates, 10-11 classes, 10 factions

---

## Proposed Design Methodology: Archetype-First

### Step 0: Define the Archetypes (must happen before anything else)

The archetypes are the 4–6 *stories* a player can live. Everything downstream
should legibly reinforce at least one of them. Good candidates, based on existing
lore content:

| Archetype | Core identity | Stat home | Energy type | Faction home |
|-----------|--------------|-----------|-------------|-------------|
| **The Engineer** | Build, expand, control material reality | INT + SYN | Plasma / Kinetic / Nuclear | Gearwrights, Icaron Collective |
| **The Mystic** | Channel etheric forces, transcend material limits | AEF + COH | Etheric / Void Essence / Leyline | Gaian Enclave, Harmonic Resonance, Voidbound Monks |
| **The Conqueror** | Military dominance, fleet supremacy, territorial control | KIN + VIT | Kinetic / Plasma / Antimatter | Ironclad Collective, Celestial Marauders |
| **The Scholar** | Research supremacy, unlock the deepest truths | INT + COH | Quantum Flux / Noospheric / Veritas Pulse | Veritas Covenant, Scholara Nexus |
| **The Diplomat** | Reputation, trade, faction mastery | INF + SYN | Empathic Resonance / Concordant Harmony | Stellar Nexus, Celestial Alliance |
| **The Naturalist** | Biological mastery, terraforming, living worlds | AEF + VIT | Synthetic Bio-Energy / Geo-Energy | Gaian Enclave, Chemists' Concord |

> **Key decision for the user:** Are these 6 right? Could be 4 (combine Mystic +
> Naturalist, combine Scholar + Engineer). The right number is however many distinct
> *mid-game experiences* you want a player to have.

---

### Step 1: Character Generation — Lock the Starting Identity

Character creation should commit the player to 1–2 archetypes. The choices don't
need to be mutually exclusive, but they should have a *center of gravity*.

**Current problem:** 54 classes is too many to be legible. The player can't hold
54 distinct identities in mind. Recommendation: organize them into the archetype
families and display them that way, even if all 54 remain available.

**Background → Archetype alignment** (already fairly coherent):
- AEF-heavy backgrounds (Etherborn Nomad, Dreamlink Initiate) → Mystic / Naturalist
- INT-heavy (Quantum Savant, AI Scribe) → Scholar / Engineer
- INF-heavy (Drift-Station Merchant, Industrial Heir) → Diplomat
- KIN/VIT-heavy (Warfleet Remnant, Deep-Core Miner) → Conqueror

**What coherence means here:** Choosing "Etherborn Nomad" background should give you
an *advantage* in Mystic research tracks, not just a stat number that has no
downstream narrative meaning.

**Mechanism:** Each archetype should have a designated "bonus stat" (e.g. AEF for
Mystic). Research in the Etheric/Mystic track costs −10% RP if your primary stat
is AEF. This creates a felt connection between day-1 choice and late-game research.

---

### Step 2: Research — The Hardest Part

**Current problem:** 163 projects in 11 categories. Engineering alone has 46.
The categories don't map to the archetypes cleanly. "Ethics and Philosophy" (21
projects) has no clear gameplay consequence. The implemented research gates (~11)
are a tiny random subset.

**Proposed redesign approach:**

#### 2a. Collapse categories to match archetypes

| New track | Old categories it absorbs | Archetype |
|-----------|--------------------------|-----------|
| Applied Sciences | Engineering, Computational | Engineer / Scholar |
| Etheric Arts | Etheric and Cosmic, Existential/Metaconscious | Mystic |
| Life Sciences | Biological/Xenogenetic, Health/Medicine, Planetary/Environmental | Naturalist |
| Transcendent Theory | Quantum/Transdimensional, Theoretical/Foundational | Scholar (late-game) |
| Martial Science | subset of Engineering (weapons/shields/propulsion) | Conqueror |
| Social Sciences | Ethics/Philosophy, subset of Computational | Diplomat |

Each track has: **Early tier → Mid tier → Late tier → Apex (1-2 projects)**

#### 2b. Tier structure — the narrative arc of research

Each track should have 3 tiers that tell a story:

- **Tier 1 (Foundation):** What you discover in the first 20 turns. Unlocks basic
  buildings and colony systems. Should feel attainable, like "getting started."
- **Tier 2 (Mastery):** What you earn by turn 50-80. Requires 2-3 Tier 1 projects.
  Unlocks the signature capabilities of the archetype.
- **Tier 3 (Transcendence):** End-game. Requires multiple Tier 2 projects. Unlocks
  the most powerful colony systems, faction-locked ships, unique commodities.

#### 2c. Cross-track prerequisites — the coherence mechanism

Some Tier 3 projects should require one project from *another* track. This models
that true mastery requires breadth:
> "Consciousness Swarm Deliberation (Mystic T3) requires Collective Metaconsciousness
> Networks AND one Computational project"

This creates natural multi-archetype builds without forcing them.

#### 2d. Research names → colony/system unlocks should be *obvious*

"Plasma Energy Dynamics" unlocks Solar Harvester ✓ — that makes sense.
"Cloaking Technology" unlocks Defense Array ✗ — cloaking is stealth, not defense.

Every gate should pass the "of course" test: a player should be able to predict
roughly what a research project unlocks just from its name.

---

### Step 3: Colony Systems — Archetype Expression

**Current state:** Well-designed but factions aren't strongly connected to systems.
**What coherence means here:** Each archetype has a "signature stack" of
Economic + Political + Social systems that clearly expresses its identity.

Examples:
- **Scholar stack:** Memory Economy + Oracle-Mediated + Memory-Pooled Identity
- **Conqueror stack:** Energy-State Economy + Algorithmic Legitimacy + Resonance-Based Cohesion
- **Diplomat stack:** Ritualized Exchange + Consensus Field + Narrative-Bound Societies

These stacks should also align with faction preferences — so a Scholar-path player
who is Allied with Veritas Covenant automatically has their preferred systems align.

---

### Step 4: Faction Redesign — Reduce and Sharpen

**Current problem:** 30 factions is too many. With 10 active in the backend,
the other 20 exist only in lore. Players can't maintain meaningful relationships
with 30 factions.

**Recommendation:** Organize 30 factions into 6 archetype-aligned *families*.
Keep ~4-5 per family active (the rest become minor/background). Player starts
with one family as home (Allied), others as Neutral.

**This also solves the energy type orphan problem:** Faction-specific energies
(Veritas Pulse, Concordant Harmony, Technotheos Charge) become the unique
commodities produced by late-game Economic systems when Allied with that faction.

---

### Step 5: Energy Types — Connect to Research Unlocks

**Current problem:** 49 energy types listed in lore but most don't connect to
gameplay bonuses. The related_energy field on research nodes is set but not used
for gating.

**Recommendation:** Each research track's Tier 2 and Tier 3 projects should
require (or produce bonuses for) a specific energy category:
- Mystic track T2: requires Etheric Energy infrastructure
- Scholar track T3: uses Quantum Flux
- Conqueror track T2: uses Plasma Energy

This connects the energy lore to the progression system without massive rework.

---

## What "Deepening Mastery" Means for Research Names

The name and description of each research project should signal *how far down the path
you've gone*, not just *what domain you're in*. The escalation pattern within each
archetype track should read like a journey:

**Example — Scholar track (currently: "Advanced Research" → "Cognitive Enhancement Systems"
→ "Quantum Temporal Dynamics"):**
- T1: "Systematic Inquiry" — *You have begun to formalize knowledge. Basic research
  infrastructure unlocked.*
- T2: "Cognitive Architecture" — *Your mind, and your colony's minds, become the
  instrument. Neural Institute, Psych-Net Hub.*
- T3: "Temporal Epistemology" — *You no longer just observe — you shape the conditions
  of knowing itself. Quantum Relay, Deep Space Observatory.*

The player should feel the stakes rising with every tier. Tier 1 names should sound
like the beginning of a discipline. Tier 3 names should sound like mastery of
something that changes the nature of the game.

---

## Ordering of Work (when ready to implement)

1. **Define archetypes** (user decision — not code)
2. **Restructure research categories** in `lore/research.json` — rename, reassign tiers
3. **Update prerequisites** to reflect the new tier/track structure
4. **Update `unlock_required` fields** in `backend/colony.py` to match new research names
5. **Update `research_required` fields** in `backend/colony_systems.py` to match
6. **Add archetype_affinity field** to classes.json and backgrounds.json
7. **Update faction system preferences** in `lore/faction_systems.json`
8. **Update the research view** in `frontend/js/views/research.js` if category display changes

---

## Confirmed Design Decisions

- **Scope:** Implemented subset first — make the ~11 research gates, 10 classes,
  10 factions coherent. Expand outward from that stable core afterward.
- **Archetypes:** 6, all kept: Engineer · Mystic · Conqueror · Scholar · Diplomat · Naturalist
- **Research feel:** Deepening mastery — Tier 1 = apprentice, Tier 2 = practitioner,
  Tier 3 = master. Names should escalate in ambition within the same domain,
  not jump across domains.

---

## Specific Coherence Issues to Fix (flagged from data)

1. **Cloaking Technology → Defense Array**: Name mismatch (stealth ≠ defense)
2. **Engineering category (46 projects)**: Needs splitting into Martial vs. Applied tracks
3. **Ethics/Philosophy (21 projects)**: Currently has no gameplay gates — should unlock Diplomat social systems
4. **Silvan Bloomforce / Quantum Choir energies**: Reference factions that don't exist in factions.json
5. **Chaotic Potential energy**: Lore says "forbidden / banned" but no gameplay mechanism enforces this — opportunity for a risk/reward mechanic
6. **"Advanced Research" gates Research Node**: Too generic a name for such a fundamental gate; should be named after a specific discovery
7. **Colony systems 5-turn cooldown**: Good mechanic, but needs narrative justification — why 5 turns? Should be "social transition period" or similar flavor
