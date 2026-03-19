# Coherence Redesign: The Implemented Subset

> **This is a design document, not code.** Everything here is a proposal.
> Edit freely. Items marked ⚠️ are flagged problems. Items marked ✏️ are
> proposed changes awaiting your approval. Items marked ✓ already work.
>
> **Scope:** The 17 research gates currently wired to buildings/colony systems,
> the 11 implemented character classes, and the 10 active factions.
> The full lore (163 projects, 54 classes, 30 factions) stays untouched for now.

---

## The Organizing Principle

Every choice the player makes belongs to one of six **archetype tracks**.
A player commits to 1–2 tracks at character creation and deepens into them
through research. Each track has three tiers:

- **Tier 1 — Apprentice:** First 20 turns. "I have begun."
- **Tier 2 — Practitioner:** Turns 40–80. "I have mastered the instrument."
- **Tier 3 — Master:** Late game. "I have changed the nature of the game."

The six tracks and their identity:

| Track | Core question | Stat home | Color |
|-------|--------------|-----------|-------|
| **Scholar** | *What can be known?* | INT + COH | Cyan |
| **Mystic** | *What lies beyond the material?* | AEF + COH | Purple |
| **Engineer** | *What can be built?* | INT + SYN | Teal |
| **Conqueror** | *What can be taken?* | KIN + VIT | Red |
| **Naturalist** | *What can be grown?* | AEF + VIT | Green |
| **Diplomat** | *What can be negotiated?* | INF + SYN | Gold |

---

## Part 1: Research Gates Redesign

Below are all 17 currently implemented research gates. For each: the current name,
what it gates, which archetype track it belongs to, what tier it should be, and —
where the current name fails the "of course" test — a proposed rename.

**The "of course" test:** A player should be able to predict roughly what a
research project unlocks just from reading its name.

---

### Scholar Track

*The Scholar does not begin from ignorance. They inherit a mature technical civilization and push it past its limits. Research begins at the point where classical systems meet Ether — and from that fusion, new epistemologies unfold. Each tier transforms how knowledge is produced: first by integrating Ether into existing systems, then by restructuring cognition itself, and finally by treating time as an operational dimension of inquiry.*

---

#### ✏️ TIER 1 — "Etheric Systems Integration"

**Currently named:** Advanced Research

**Gates:** Research Node (3 research/turn)

**"Of course" test:** PASS. If a civilization already possesses advanced computational, industrial, and scientific systems, the next natural step is integrating Ether into those systems to expand their capabilities.

**Proposed name:** `Etheric Systems Integration`

**Proposed description:**

> *You begin not with discovery, but with synthesis. Existing computational,
> industrial, and scientific systems are infused with Ether, allowing them to
> operate beyond classical constraints. Observation becomes resonance, and
> measurement becomes interaction. The first ether-integrated research
> infrastructure becomes buildable.*

**Why this works:** This reflects the reality of 7019 — civilizations are already advanced. The breakthrough is not “doing research,” but transforming how systems process reality. A Research Node becomes an ether-sensitive computation cluster capable of modeling phenomena that classical systems cannot.

---

#### ✏️ TIER 2 — "Cognitive Architecture"

**Currently named:** Cognitive Enhancement Systems

**Gates:** Neural Institute (5 research + 1 ether), Psych-Net Hub (4 research + 2 ether), Command Citadel (3 defense + 5 fleet)

**"Of course" test:** PARTIAL. Neural Institute and Psych-Net Hub follow naturally. Command Citadel does not.

**Proposed name:** `Cognitive Architecture`

**Proposed description:**

> *With Ether integrated into core systems, the boundary between mind and
> machine dissolves. Cognition itself becomes an engineered system — scalable,
> networked, and partially ether-resonant. Colonies are designed around
> distributed intelligence rather than isolated individuals.*

**⚠️ Action required:** Command Citadel should be moved to the Conqueror track,
gated by a Conqueror Tier 2 research. This tier is about cognition as
infrastructure, not military command.

---

#### ✏️ TIER 2 (colony systems) — "Predictive Systems Theory"

**Currently named:** Predictive Logic Crystals

**Gates:** Algorithmic Legitimacy (political system: +15% all_production, +10% research, −5% pop_growth)

**"Of course" test:** PASS. Once cognition and data systems are integrated and enhanced by Ether, predictive governance naturally emerges.

**Proposed name:** `Predictive Systems Theory`

**Proposed description:**

> *You formalize the fusion of data, cognition, and Ether into predictive
> systems capable of modeling complex societal outcomes. Governance shifts
> from authority to performance — legitimacy emerges from predictive accuracy
> and system optimization.*

---

#### ✏️ TIER 3 — "Chronometric Theory"

**Currently named:** Quantum Temporal Dynamics

**Gates:** Quantum Relay (3 research), Deep Space Observatory (6 research),
Time Economy (economic system: +8% all_production), Temporal Layer Governance
(political system: +15% research, +10% all_production, −10 stability)

**"Of course" test:** STRONG PASS. Once Ether is integrated into systems and cognition, the next boundary is time itself.

**Proposed name:** `Chronometric Theory`

**Proposed description:**

> *With Ether-enabled cognition and predictive systems in place, time becomes
> observable as a structured medium rather than a passive flow. You develop
> methods to measure, model, and interact with temporal layers. Communication
> across time-adjacent states becomes possible, and temporal differentials
> can be exploited economically.*

---

#### ✏️ TIER 3 (colony systems) — "Noospheric Integration"

**Currently named:** Collective Metaconsciousness Networks

**Gates:** Consciousness-Labor Economy (+20% research, +10% fleet),
Consciousness Swarm Deliberation (+30% research, +15% all_production, −10% pop),
Distributed Selfhood social system (+15% trade, +10% all_production, −5 stability)

**"Of course" test:** STRONG PASS. This is the culmination of Ether + cognition + systems.

**Proposed name:** `Noospheric Integration`

**Proposed description:**

> *The colony’s cognitive systems — biological, artificial, and etheric —
> converge into a unified noosphere. Thought is no longer produced by
> individuals alone, but emerges from a shared field of awareness. Identity
> persists, but cognition becomes collective, fluid, and continuously
> recombined. The most advanced colony-scale cognitive systems become
> available.*


---

### Mystic Track

*The Mystic learns to perceive, then channel, then command forces that
material science cannot explain. Each tier deepens their relationship with
the etheric field — first sensing it, then mapping it, then owning the void.*

---

#### ✏️ TIER 1 — "Etheric Attunement"
**Currently named:** Advanced Etheric Weaving

**Gates:** Ether Conduit (2 ether), Etheric Purifier (2 ether, volcanic/geothermal
only), Crystal Resonance Array (6 ether + 2 research, crystal only)

**"Of course" test:** PASS for Ether Conduit and Crystal Resonance Array.
PARTIAL for Etheric Purifier — "purifying" corrupted ether zones is slightly
different from "weaving." All three are ether-production buildings, so the
research makes sense. But "Advanced" is a lazy modifier.

**Proposed name:** `Etheric Attunement`

**Proposed description:**
> *You have learned to sense and shape the ambient Etheric field — the
> invisible current that flows through all matter. Structures that channel,
> purify, and amplify this energy become buildable for the first time.*

**Why this works:** "Attunement" is exactly what a practitioner does at the
start — they learn to feel the field before they can use it.

---

#### ✏️ TIER 2 — "Deep Ether Cartography"
**Currently named:** Primordial Ether Research

**Gates:** Oracle-Mediated Governance (political system: +20% research, +5% all_production)

**"Of course" test:** FAIL. "Primordial Ether Research" unlocks a *governance
system* — Oracle-Mediated Governance (authority interpreted through etheric
prediction). The connection between "primordial ether" and governance is opaque.

**Proposed name:** `Deep Ether Cartography`

**Proposed description:**
> *You have mapped the etheric field at depth — its fault lines, its nodes,
> its predictive harmonics. Colony leaders who can read this field gain
> profound strategic foresight. Oracle-Mediated Governance becomes available.*

**Why this works:** Mapping the ether for *foresight* logically unlocks a
governance system built around predictive authority.

---

#### ✏️ TIER 3 — "Void Sovereignty"
**Currently named:** Null Space Exploration

**Gates:** Void Anchor (5 ether, void terrain only),
Planetary Shield Generator (5 defense)

**"Of course" test:** PARTIAL. Void Anchor follows obviously — you explored
null space and can now anchor into it. Planetary Shield Generator is weak —
null space exploration doesn't obviously produce a planetary shield. This
feels like it was assigned here arbitrarily.

**Proposed name:** `Void Sovereignty`

**Proposed description:**
> *You do not merely explore the void — you claim it. Gravitational anchors
> can be planted in void rifts to harvest dark energy. The techniques for
> projecting a graviton barrier across a planetary atmosphere — learned
> from void physics — become available.*

**Note:** Planetary Shield Generator can stay here if we add one sentence to the
description connecting void physics → graviton barriers. Alternatively, move it
to the Conqueror track under a defense-research gate (see below).

---

#### TIER 3 (colony systems — shared with Naturalist)

**Gates:** Memory Economy (+25% research, +10% pop_growth),
Memory-Pooled Identity social system (+20% research, +20 stability, +5% pop_growth)

See **Naturalist Track: Bio-Digital Convergence** below. This research sits on
both tracks. A Mystic reaches it through consciousness; a Naturalist reaches it
through biology. Both paths are valid.

---

### Engineer Track

*The Engineer masters physical reality — extraction, fabrication, automation.
Each tier extends their ability to reshape the material world: first organizing
labor, then harnessing energy at industrial scale, then building structures
that think and build themselves.*

---

#### ✏️ TIER 1 — "Industrial Systematization"
**Currently named:** Mining Automation

**Gates:** Deep Core Drill (8 minerals, mountains only), Munitions Factory
(4 fleet + 2 refined_ore), Ore Processor (4 refined_ore), Industrial Fabricator
(6 credits + 2 minerals)

**"Of course" test:** PARTIAL. "Mining Automation" perfectly explains Deep Core
Drill and Ore Processor. But Munitions Factory (military production) and Industrial
Fabricator (consumer goods) don't follow from mining automation — they're general
industrial processes.

**Proposed name:** `Industrial Systematization`

**Proposed description:**
> *You have automated and systematized the full industrial chain — from raw
> extraction deep in the planetary crust, through ore refining, to fabricated
> goods and ordnance. Every link in the production chain becomes buildable.*

**Why this works:** "Systematization" covers the full chain (extraction → processing
→ fabrication → ordnance), not just mining. All four buildings make sense.

---

#### ✏️ TIER 2 — "Plasma Energy Mastery"
**Currently named:** Plasma Energy Dynamics

**Gates:** Solar Harvester (2 minerals + 1 credit), Anti-Orbital Battery
(4 defense, mountains/volcanic/tundra), Geothermal Tap (4 ether + 2 minerals)

**"Of course" test:** PASS for Solar Harvester and Geothermal Tap (both are
energy-harvesting). WEAK for Anti-Orbital Battery — plasma cannon makes sense,
but "dynamics" sounds academic. The name is technically fine; "Mastery" makes it
sound like a practitioner tier.

**Proposed name:** `Plasma Energy Mastery`

**Proposed description:**
> *You have moved from studying plasma to commanding it — in orbital solar arrays,
> deep geothermal conduits, and directed-energy surface-to-orbit weapons. Energy
> at this scale reshapes the colony's industrial and military capacity.*

**Note:** Anti-Orbital Battery here is fine because plasma cannon = plasma energy.
This is one of the stronger existing name→unlock connections.

---

#### ✏️ TIER 3 — "Autonomous Architecture"
**Currently named:** Sentient Architecture

**Gates:** Synthetic Mind Core (10 research), Orbital Drydock (18 fleet_points)

**"Of course" test:** PARTIAL. Synthetic Mind Core is perfect — a self-directing
AI research engine, the pinnacle of the Scholar and Engineer tracks both.
Orbital Drydock is weaker — orbital construction platforms don't obviously
require "sentient architecture." They require precision engineering.

**Proposed name:** `Autonomous Architecture`

**Proposed description:**
> *Your construction methods have crossed a threshold — structures that design,
> adapt, and maintain themselves. The Synthetic Mind Core operates without
> oversight. The Orbital Drydock assembles capital vessels using autonomous
> construction swarms.*

**Why this works:** "Autonomous" covers both the AI research engine and the
self-directing construction platform. It's also a better master-tier word than
"Sentient" (which implies consciousness, not just self-direction).

---

### Conqueror Track

*The Conqueror secures, defends, and projects force. Each tier transforms
their ability to hold what they have and take what they want: first
hardening their position, then projecting power at scale, then commanding
forces that overwhelm opposition.*

---

#### ⚠️ TIER 1 — CURRENT PROBLEM: "Cloaking Technology"
**Currently named:** Cloaking Technology

**Gates:** Defense Array (2 defense)

**"Of course" test:** FAIL. **This is the worst name→unlock mismatch in the
current system.** Cloaking is stealth — it makes things *invisible*. A Defense
Array is a planetary defense *grid* — it makes you harder to attack. These are
opposite concepts (concealment vs. fortification).

**Proposed name:** `Orbital Defense Doctrine`

**Proposed description:**
> *You have formalized the theory of layered planetary defense — sensor networks,
> automated response systems, and coordinated defensive grids. The first planetary
> Defense Array becomes buildable.*

**Also gates (proposed addition):** Command Citadel should move here from
Cognitive Architecture (Scholar T2). A joint-operations military command center
obviously follows from defense doctrine, not from cognitive research.

**Command Citadel revised gate:** `Orbital Defense Doctrine` (Conqueror T1 or T2)

---

#### TIER 2 — Shared with Engineer
**Currently named:** Plasma Energy Dynamics → proposed `Plasma Energy Mastery`

The Anti-Orbital Battery (4 defense, plasma cannon) is the Conqueror's prize
from this research. The Engineer and Conqueror both complete this research, but
for different reasons — the Engineer wants the Solar Harvester and Geothermal Tap;
the Conqueror wants the Anti-Orbital Battery.

---

#### TIER 3 — Shared with Engineer
**Currently named:** Sentient Architecture → proposed `Autonomous Architecture`

The Orbital Drydock (18 fleet_points) is the Conqueror's prize. An Engineer
completing this research builds the Synthetic Mind Core; a Conqueror builds the
Orbital Drydock. Both are valid master-tier outcomes from the same discovery.

---

#### ⚠️ TIER 3 (defense) — PROPOSED ADDITION
**Currently:** Planetary Shield Generator is gated by Null Space Exploration
(Mystic track). This is a weak connection narratively.

**Proposed move:** Gate Planetary Shield Generator under a new Conqueror Tier 3
research, OR keep it under Void Sovereignty but accept the Mystic/Conqueror overlap.

**Recommendation:** Keep it under Void Sovereignty with better description
(void physics → graviton barriers). No new gate needed.

---

### Naturalist Track

*The Naturalist learns to work with living systems — first cultivating and
engineering them, then studying alien life to understand what biology can
become, then crossing the threshold where biological and digital are no longer
separate categories.*

---

#### ✏️ TIER 1 — "Living Systems Engineering"
**Currently named:** Bio-Engineering

**Gates:** Bio-Synthesis Lab (3 food + 2 research), Atmospheric Processor
(3 food + 1 mineral, tundra/desert/volcanic only), Agri-Industrial Complex
(6 food + 3 minerals)

**"Of course" test:** PASS. "Bio-Engineering" clearly implies engineering
biological systems. All three buildings are biological production structures.
The name is fine — but "Bio-Engineering" is generic. A master-track name should
feel more specific.

**Proposed name:** `Living Systems Engineering`

**Proposed description:**
> *You have moved beyond cultivating what nature provides to designing
> living systems from first principles — synthesizing bio-materials,
> engineering microbes to convert hostile atmospheres, integrating
> biological and industrial production chains.*

**Why this works:** "Living Systems" is more evocative than "Bio-Engineering"
and makes the atmosphere-conversion (Atmospheric Processor) feel intentional
rather than accidental.

---

#### ✏️ TIER 2 — "Xenobiological Integration"
**Currently named:** Xenogenetics

**Gates:** Xenobiology Station (4 research), Xenolinguistics Center (3 research + 3 credits)

**"Of course" test:** PARTIAL. Xenobiology Station obviously follows from
"Xenogenetics." Xenolinguistics Center (decoding alien communication artifacts)
is a stretch — linguistics is not genetics.

**Proposed name:** `Xenobiological Integration`

**Proposed description:**
> *You have moved from observing alien life to integrating with it — studying
> how alien biomes encode information, decode signals, and communicate across
> species boundaries. This research produces both biological insights and
> unexpected diplomatic value.*

**Note:** The Xenolinguistics Center unlock becomes more coherent — alien
*biological* signals happen to be linguistic. The research + credits output
from the Center also makes sense: alien communication artifacts = trade value.

**⚠️ Alternative:** Move Xenolinguistics Center to the Diplomat track (see below).
It's a more natural fit there. Your call.

---

#### ✏️ TIER 3 — "Bio-Digital Convergence"
**Currently named:** Bio-Digital Symbiosis

**Gates:** Memory Economy (+25% research, +10% pop_growth),
Memory-Pooled Identity social system (+20% research, +20 stability, +5% pop_growth)

**"Of course" test:** PASS. Memory as a tradeable commodity (Memory Economy)
follows beautifully from biological-digital synthesis — memories stored as data,
traded as capital. Memory-Pooled Identity (shared memory archives across the
population) is equally coherent.

**Proposed name:** `Bio-Digital Convergence`

**Proposed description:**
> *The boundary between biological memory and digital storage dissolves.
> Experience can be archived, transferred, and traded. Colony populations
> begin to share identity through networked memory pools. This is the
> Naturalist's threshold moment.*

**Note on cross-track:** The Mystic can also reach this research — their path
is through consciousness expansion rather than biology. Both routes are valid
and both lead to the same discovery from different angles.

---

#### TIER 3 (colony systems) — Trans-Phasic Genetics

**Currently named:** Trans-Phasic Genetics

**Gates:** Rotating Embodiment Systems (social: +5% all_diplomacy, +5% all_production, −10 stability)

**"Of course" test:** PASS. Consciousness moving between bodies (Rotating
Embodiment) logically follows from genetics that transcends phase boundaries.
The name is already strong.

**Proposed rename:** None needed. Keep `Trans-Phasic Genetics`.

---

### Diplomat Track

*The Diplomat's power comes from relationships. Unlike other tracks, their
early advantages need no research — free colony systems (Ritualized Exchange,
Consensus Field, Narrative-Bound Societies) give them a head start in
reputation building. Research deepens their capacity to read, predict, and
finally shape the social field at civilizational scale.*

---

#### ⚠️ TIER 1 — CURRENT GAP
**The Diplomat has no Tier 1 research gate.** All their early colony systems
(Ritualized Exchange, Consensus Field Governance, Narrative-Bound Societies)
are available from turn 1. This is actually narratively appropriate — a Diplomat
starts with relationships, not research.

**BUT:** There's no research that *deepens* early diplomatic capability. The
Diplomat's first research gate is Causal Integrity Theory (Tier 2), which is
a significant jump.

**Proposed Tier 1:** `Interstellar Diplomatic Protocols`

**Proposed gates:**
- Xenolinguistics Center (moved from Naturalist — 3 research + 3 credits; decoding
  alien communication is a diplomatic tool, not a biological one)
- A future "Embassy" building (placeholder for Phase 6)

**Proposed description:**
> *You have codified the principles of cross-species communication — the
> rituals, signal protocols, and cultural translation frameworks that make
> interstellar diplomacy possible. Alien communication artifacts become
> legible and valuable.*

**Note:** This would require moving Xenolinguistics Center's `unlock_required`
from `"Xenogenetics"` to `"Interstellar Diplomatic Protocols"` in `backend/colony.py`.
One-line change, significant coherence improvement.

---

#### ✏️ TIER 2 — "Predictive Economics"
**Currently named:** Causal Integrity Theory

**Gates:** Probability Economy (economic system: +20% credits)

**"Of course" test:** FAIL. "Causal Integrity Theory" is a philosophy of
causation, not an economic framework. The Probability Economy (trading futures,
hedging on outcomes) does follow from probability theory, but "causal integrity"
implies studying chains of cause-and-effect, not predicting markets.

**Proposed name:** `Predictive Economics`

**Proposed description:**
> *You have formalized the mathematics of outcome prediction — probability
> markets, futures trading, reflexivity modeling. The economy becomes a
> tool for shaping outcomes rather than just recording them. Probability
> Economy becomes available as an economic system.*

---

#### TIER 3 — Shared with Scholar
**Currently named:** Collective Metaconsciousness Networks → proposed `Noospheric Integration`

The Diplomat reaches this from the social side — networked minds that can reach
consensus at civilizational scale. The Scholar reaches it from the intellectual
side — distributed cognition as a research amplifier. The same discovery, two
different motivations.

---

## Part 2: Character Classes → Archetype Map

Each class is assigned to 1–2 primary archetypes and a **bonus stat** — the stat
that, if high, gives this class an affinity for their archetype's research track.

The mechanism: if a player's primary stat (highest allocation) matches a class's
bonus stat, research in that archetype track costs ~10% less RP. This creates a
felt connection between day-1 stat choices and late-game research pace.

| Class | Primary archetype | Secondary archetype | Bonus stat | Starting asset |
|-------|------------------|--------------------|-----------|--------------------|
| Scientist | Scholar | Engineer | INT | Nebula Drifter + Archive of Echoes |
| Archaeologist | Mystic | Scholar | AEF | Deep Explorer |
| Terraformer | Naturalist | Engineer | AEF | Genesis Transport + Atmospheric Processor |
| Industrial Magnate | Engineer | Conqueror | SYN | Basic Transport + Nanoforge Spires |
| Military Commander | Conqueror | Engineer | KIN | Aurora Ascendant |
| Bounty Hunter | Conqueror | Diplomat | KIN | Pursuit Vessel |
| Diplomat | Diplomat | Scholar | INF | Celestium-Class Comm Ship |
| Merchant Captain | Diplomat | Engineer | INF | Aurora-Class Freighter |
| Corporate Spy | Diplomat | Conqueror | SYN | Phantom Interceptor |
| Explorer | Scholar | Naturalist | COH | Stellar Voyager |
| Smuggler | Conqueror | Diplomat | KIN | Shadow Runner |

**Notes on archetype fit:**
- **Archaeologist → Mystic** makes strong narrative sense: studying ancient
  artifacts is the beginning of understanding forces beyond material science.
- **Explorer → Scholar** works because exploration is systematic inquiry applied
  to space. COH (Coherence) as bonus stat: an explorer's clarity of mind in
  unfamiliar territory.
- **Corporate Spy → Diplomat** works because espionage is a form of social
  engineering. SYN (Synthesis) as bonus stat: adapting to any environment.
- **Smuggler → Conqueror** is the edgiest assignment. Smugglers are not
  conquerors by nature, but their KIN advantage and stealth orientation map
  better to Conqueror than Diplomat. Consider: should Smuggler be Diplomat +
  Conqueror, or purely Diplomat? ✏️ *Your call.*

---

## Part 3: Factions → Archetype Families

The 10 active factions organized into the 6 archetype families, with each
faction's **signature colony system stack** — the Economic + Political + Social
combination that aligns with their philosophy and generates positive faction
affinity when the player adopts it.

---

### Scholar Family

**Factions:** The Veritas Covenant · The Scholara Nexus

| Faction | Philosophy | System alignment |
|---------|-----------|-----------------|
| The Veritas Covenant | Truth through scientific inquiry | Memory Economy + Oracle-Mediated + Memory-Pooled Identity |
| The Scholara Nexus | Universal education and knowledge sharing | Consciousness-Labor + Algorithmic Legitimacy + Distributed Selfhood |

**Signature stack:** Memory Economy + Oracle-Mediated Governance + Memory-Pooled Identity

> *"We observe. We record. We know."*
> Allied benefit: +50% research speed. Research is the Scholar's currency.

---

### Mystic Family

**Factions:** The Harmonic Resonance Collective · The Quantum Artificers Guild

| Faction | Philosophy | System alignment |
|---------|-----------|-----------------|
| The Harmonic Resonance Collective | All existence vibrates in harmony | Ritualized Exchange + Consensus Field + Resonance-Based Cohesion |
| The Quantum Artificers Guild | Masters of quantum mechanics; bend reality | Time Economy + Oracle-Mediated + Distributed Selfhood |

**Signature stack:** Ritualized Exchange + Consensus Field Governance + Resonance-Based Cohesion

> *"The field speaks. We listen."*
> Allied benefit: Etheric building discounts; faction-locked etheric ship components.

**⚠️ Note:** The Harmonic Resonance Collective and Quantum Artificers Guild have very
different flavors (one is mystical/musical, one is tech-quantum). They share an
archetype but different system stacks. This is intentional — "Mystic" contains both
the spiritual and the quantum-physical approaches to forces beyond material science.

---

### Engineer Family

**Factions:** The Gearwrights Guild · The Icaron Collective

| Faction | Philosophy | System alignment |
|---------|-----------|-----------------|
| The Gearwrights Guild | Mechanical perfection through craft | Energy-State Economy + Algorithmic Legitimacy + Symbiotic Networks |
| The Icaron Collective | Unity through technology (AI/bio integration) | Consciousness-Labor + Algorithmic Legitimacy + Distributed Selfhood |

**Signature stack:** Energy-State Economy + Algorithmic Legitimacy + Symbiotic Networks

> *"If it can be built, it can be improved."*
> Allied benefit: Industrial discounts; faction-locked hull/engine components.

---

### Conqueror Family

**Factions:** *(currently no active faction is a pure Conqueror archetype)*

**⚠️ GAP:** The 10 active factions have no explicitly military/conquest faction.
The Gearwrights Guild is the closest (industry feeds fleets), but their philosophy
is "mechanical perfection," not "territorial dominance."

**Options:**
1. Assign Gearwrights to both Engineer and Conqueror families (industrial capacity
   enables conquest — this is historically accurate)
2. Promote one of the 20 inactive factions (e.g. "The Ironclad Collective" or
   "Celestial Marauders") to active status as the Conqueror's home faction
3. Leave Conquerors as a class/stat path without a dedicated faction, making
   them inherently mercenary — they ally with whoever is useful

**✏️ Your call.** Option 3 has narrative appeal (the Conqueror answers to no one),
but leaves them without a +50% research bonus from an allied faction.

---

### Naturalist Family

**Factions:** The Gaian Enclave · Harmonic Vitality Consortium

| Faction | Philosophy | System alignment |
|---------|-----------|-----------------|
| The Gaian Enclave | Natural harmony; protect living worlds | Ritualized Exchange + Consensus Field + Narrative-Bound Societies |
| Harmonic Vitality Consortium | Balance and health through harmonic frequencies | Memory Economy + Consensus Field + Symbiotic Networks |

**Signature stack:** Ritualized Exchange + Consensus Field Governance + Narrative-Bound Societies

> *"Life finds a way. We help it."*
> Allied benefit: Bio-building discounts; terraforming acceleration.

---

### Diplomat Family

**Factions:** Stellar Nexus Guild · The Provocateurs' Guild

| Faction | Philosophy | System alignment |
|---------|-----------|-----------------|
| Stellar Nexus Guild | Interconnectedness through trade | Probability Economy + Distributed Sovereignty + Narrative-Bound Societies |
| The Provocateurs' Guild | Creative chaos challenges conventions | Ritualized Exchange + Distributed Sovereignty + Narrative-Bound Societies |

**Signature stack:** Probability Economy + Distributed Micro-Sovereignty + Narrative-Bound Societies

> *"Everyone wants something. We know what it is."*
> Allied benefit: Trade discounts; reputation gain acceleration.

---

## Part 4: The "Of Course" Audit — Full Results

Complete pass/fail for every current research→building connection.

| Research gate | Building/system unlocked | Test result | Issue |
|---------------|--------------------------|-------------|-------|
| Advanced Research | Research Node | ⚠️ RENAME | "Advanced Research" is circular |
| Advanced Etheric Weaving | Ether Conduit | ⚠️ RENAME | "Advanced" is lazy; "Weaving" is evocative but T1 should feel like beginning, not advancing |
| Advanced Etheric Weaving | Etheric Purifier | ✓ PASS | Purifying ether = weaving the field |
| Advanced Etheric Weaving | Crystal Resonance Array | ✓ PASS | Amplifying crystal resonance = weaving |
| Cloaking Technology | Defense Array | ❌ FAIL | Stealth ≠ defense fortification. Worst mismatch in the system. |
| Cognitive Enhancement Systems | Neural Institute | ✓ PASS | Cognitive enhancement → neural-digital mind interface |
| Cognitive Enhancement Systems | Psych-Net Hub | ✓ PASS | Cognitive enhancement → psionic computation network |
| Cognitive Enhancement Systems | Command Citadel | ❌ FAIL | Military fortress ≠ cognitive research |
| Quantum Temporal Dynamics | Quantum Relay | ✓ PASS | Quantum time physics → quantum communication |
| Quantum Temporal Dynamics | Deep Space Observatory | ✓ PASS | Temporal observation → deep-space telescope |
| Quantum Temporal Dynamics | Time Economy | ✓ PASS | Understanding time → trading time |
| Quantum Temporal Dynamics | Temporal Layer Governance | ⚠️ WEAK | Time-phase governance feels more political than physical |
| Bio-Engineering | Bio-Synthesis Lab | ✓ PASS | Obvious |
| Bio-Engineering | Atmospheric Processor | ✓ PASS | Engineered microbes convert atmosphere |
| Bio-Engineering | Agri-Industrial Complex | ✓ PASS | Integrated bio-industrial farming |
| Mining Automation | Deep Core Drill | ✓ PASS | Automated deep mining |
| Mining Automation | Ore Processor | ✓ PASS | Automated ore refining |
| Mining Automation | Munitions Factory | ⚠️ WEAK | Military ordnance ≠ mining automation |
| Mining Automation | Industrial Fabricator | ⚠️ WEAK | Consumer goods ≠ mining |
| Null Space Exploration | Void Anchor | ✓ PASS | Explored null space → can anchor in it |
| Null Space Exploration | Planetary Shield Generator | ⚠️ WEAK | Void physics → graviton barrier is plausible but not obvious |
| Plasma Energy Dynamics | Solar Harvester | ✓ PASS | Plasma/energy → orbital solar array |
| Plasma Energy Dynamics | Anti-Orbital Battery | ✓ PASS | Plasma energy → plasma cannon |
| Plasma Energy Dynamics | Geothermal Tap | ✓ PASS | Plasma energy → geothermal extraction |
| Xenogenetics | Xenobiology Station | ✓ PASS | Alien genetics → study alien biomes |
| Xenogenetics | Xenolinguistics Center | ⚠️ WEAK | Genetics ≠ linguistics (should move to Diplomat track) |
| Sentient Architecture | Synthetic Mind Core | ✓ PASS | Self-directing architecture → AI research engine |
| Sentient Architecture | Orbital Drydock | ⚠️ WEAK | Autonomous construction swarms make it work, but needs description support |
| Primordial Ether Research | Oracle-Mediated Governance | ⚠️ FAIL | No clear connection between "primordial ether" and governance philosophy |
| Predictive Logic Crystals | Algorithmic Legitimacy | ⚠️ FAIL | A noun-object (crystals) as the gate for a governance philosophy |
| Causal Integrity Theory | Probability Economy | ⚠️ WEAK | Causation theory → probability markets is an intellectual leap |
| Collective Metaconsciousness | Consciousness-Labor Economy | ✓ PASS | Distributed minds → cognitive labor economy |
| Collective Metaconsciousness | Consciousness Swarm Deliberation | ✓ PASS | Metaconsciousness → swarm decision-making |
| Collective Metaconsciousness | Distributed Selfhood | ✓ PASS | Networked consciousness → distributed identity |
| Bio-Digital Symbiosis | Memory Economy | ✓ PASS | Bio-digital merger → memory as capital |
| Bio-Digital Symbiosis | Memory-Pooled Identity | ✓ PASS | Bio-digital merger → shared memory identity |
| Trans-Phasic Genetics | Rotating Embodiment | ✓ PASS | Trans-phasic (crossing phases) → consciousness in different bodies |

**Summary:**
- ✓ PASS: 22 connections
- ⚠️ WEAK/RENAME: 11 connections (fixable with name change or description addition)
- ❌ FAIL: 3 connections (require gate reassignment)

---

## Part 5: Summary of Proposed Changes

A clean list of every change proposed in this document, ordered by impact.

### Required (❌ FAIL fixes)
1. Rename `Cloaking Technology` → `Orbital Defense Doctrine`. Move Command Citadel gate here.
2. Move Command Citadel from `Cognitive Enhancement Systems` → `Orbital Defense Doctrine`
3. Rename `Primordial Ether Research` → `Deep Ether Cartography` with updated description
4. Rename `Predictive Logic Crystals` → `Predictive Systems Theory`

### High value (⚠️ WEAK fixes)
5. Rename `Advanced Research` → `Empirical Methods`
6. Rename `Advanced Etheric Weaving` → `Etheric Attunement`
7. Rename `Cognitive Enhancement Systems` → `Cognitive Architecture`
8. Rename `Mining Automation` → `Industrial Systematization`
9. Rename `Null Space Exploration` → `Void Sovereignty`
10. Rename `Xenogenetics` → `Xenobiological Integration`
11. Rename `Bio-Engineering` → `Living Systems Engineering`
12. Rename `Causal Integrity Theory` → `Predictive Economics`
13. Rename `Collective Metaconsciousness Networks` → `Noospheric Integration`
14. Rename `Bio-Digital Symbiosis` → `Bio-Digital Convergence`
15. Rename `Sentient Architecture` → `Autonomous Architecture`
16. Rename `Quantum Temporal Dynamics` → `Chronometric Theory`
17. Move `Xenolinguistics Center` gate from `Xenogenetics` → new `Interstellar Diplomatic Protocols`

### Design decisions needed (your call before implementing)
18. Add `Interstellar Diplomatic Protocols` as Diplomat Tier 1 gate (new research project)
19. Decide: should Smuggler be Conqueror/Diplomat or purely Diplomat archetype?
20. Decide: active Conqueror faction — share Gearwrights, promote The Ironclad Collective, or leave Conqueror factionless?
21. Decide: move Planetary Shield Generator to Conqueror track, or keep under Void Sovereignty with better description?

---

*Edit this document freely. When you're satisfied with the proposals, the
implementation follows these files:*
- *Research renames: `lore/research.json`*
- *Building gate changes: `backend/colony.py` (unlock_required fields)*
- *Colony system gate changes: `backend/colony_systems.py` (research_required fields)*
- *Class archetype tags: `lore/classes.json` (add archetype + bonus_stat fields)*
- *Faction system prefs: `lore/faction_systems.json`*
