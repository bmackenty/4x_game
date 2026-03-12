"""
professions.py — Unified profession system for Chronicles of the Ether (Year 7019).

All professions share a common schema:
  category              : str        — one of the CATEGORY_* constants below
  description           : str        — lore-rich career description
  skills                : list[str]  — five defining professional skills
  base_benefits         : list[str]  — what the profession provides at levels 1–2
  intermediate_benefits : list[str]  — benefits unlocked at levels 3–5
  advanced_benefits     : list[str]  — benefits unlocked at levels 6–8
  master_benefits       : list[str]  — benefits unlocked at levels 9–10

Sources merged into this file:
  - professions_7019 list      (primary source, lore-rich 7019-era professions)
  - additional_professions_7019 list (programmable matter + collective mind + education)
  - legacy professions dict    (earlier game iteration; unique entries preserved)

ProfessionSystem class wraps PROFESSIONS and tracks per-character XP and level.
"""

import random

# ── Category constants ────────────────────────────────────────────────────────
CATEGORY_ETHERIC     = "Etheric"       # consciousness, ether, mystical tech
CATEGORY_ENGINEERING = "Engineering"   # hardware, systems, construction
CATEGORY_SCIENTIFIC  = "Scientific"    # research, analysis, exploration
CATEGORY_DIPLOMATIC  = "Diplomatic"    # relations, negotiation, culture, education
CATEGORY_OPERATIONS  = "Operations"    # logistics, security, management
CATEGORY_MEDICAL     = "Medical"       # healing, biology, enhancement
CATEGORY_ARTISTIC    = "Artistic"      # creative expression, culture, ritual

# ── Canonical profession data ─────────────────────────────────────────────────
PROFESSIONS = {

    # =========================================================================
    # ETHERIC — consciousness, ether, cognition, mystical infrastructure
    # =========================================================================

    "Etheric Communicator": {
        "category": CATEGORY_ETHERIC,
        "description": (
            "Specialists who sense, interpret, and mediate etheric signals between beings, "
            "systems, ships, and environments. They are often essential in diplomacy, ship "
            "operations, and consciousness-linked infrastructure."
        ),
        "skills": [
            "etheric resonance interpretation",
            "cross-species communication",
            "emotional field calibration",
            "telepathic protocol handling",
            "ship-consciousness mediation",
        ],
        "base_benefits": [
            "Interpret basic etheric signals from ships and local environments",
            "Facilitate structured dialogue between two species or cognition types",
        ],
        "intermediate_benefits": [
            "Calibrate emotional fields to reduce diplomatic friction in tense exchanges",
            "Handle complex telepathic protocol handshakes across ship networks",
        ],
        "advanced_benefits": [
            "Mediate multi-party consciousness-linked infrastructure conflicts",
            "Translate between radically different cognition architectures in real time",
        ],
        "master_benefits": [
            "Bridge ship-consciousness networks across entire fleet formations simultaneously",
            "Resolve deep etheric signal conflicts before they cascade into system failures",
        ],
    },

    "Consciousness Engineer": {
        "category": CATEGORY_ETHERIC,
        "description": (
            "Engineers who design and maintain interfaces between minds, AI systems, ships, "
            "and distributed consciousness frameworks. Their work sits at the boundary of "
            "cognition, software, and etheric structure."
        ),
        "skills": [
            "neural-interface architecture",
            "consciousness modeling",
            "cognitive systems maintenance",
            "AI alignment design",
            "etheric cognition frameworks",
        ],
        "base_benefits": [
            "Design and maintain basic neural-interface hardware",
            "Model simple consciousness states for diagnostic or therapeutic use",
        ],
        "intermediate_benefits": [
            "Build stable AI-cognition bridges that survive etheric interference",
            "Maintain distributed consciousness frameworks across a single vessel",
        ],
        "advanced_benefits": [
            "Architect complex multi-mind cognitive networks with identity safeguards",
            "Align AI systems to etheric cognition frameworks without recursion collapse",
        ],
        "master_benefits": [
            "Design post-biological consciousness substrates capable of stellar-scale operation",
            "Prevent cascade consciousness failures aboard entire fleets under ether storm conditions",
        ],
    },

    "Emotional Interface Specialist": {
        "category": CATEGORY_ETHERIC,
        "description": (
            "Professionals who stabilize and optimize systems that respond to emotional states, "
            "especially in ships, healing environments, diplomatic chambers, and "
            "ether-responsive technologies."
        ),
        "skills": [
            "affective systems tuning",
            "conflict de-escalation",
            "biofeedback interpretation",
            "empathetic calibration",
            "human-machine emotional harmonization",
        ],
        "base_benefits": [
            "Tune affective response systems to reduce false-positive threat readings",
            "Read biofeedback signals to gauge crew emotional state",
        ],
        "intermediate_benefits": [
            "De-escalate crew conflicts before they impair mission performance",
            "Calibrate ship emotional-response systems for hostile environment operations",
        ],
        "advanced_benefits": [
            "Harmonize multi-species crew emotional states across long voyages",
            "Prevent emotional resonance cascades in ether-sensitive ship systems",
        ],
        "master_benefits": [
            "Create ambient emotional coherence fields that boost crew performance fleet-wide",
            "Stabilize diplomatic environments so fractured factions can negotiate in good faith",
        ],
    },

    "AI-Ether Integration Specialist": {
        "category": CATEGORY_ETHERIC,
        "description": (
            "Experts who enable AI systems to sense, interpret, and respond to etheric energy "
            "without collapsing into recursion, madness, or theological confusion."
        ),
        "skills": [
            "AI systems design",
            "ether interface programming",
            "signal normalization",
            "model validation",
            "safety architecture",
        ],
        "base_benefits": [
            "Expose AI systems to low-intensity etheric signals without triggering instability",
            "Normalize raw ether data streams into formats AI cognition can safely parse",
        ],
        "intermediate_benefits": [
            "Validate AI ether-response models against real-world anomalies",
            "Build safety cutoffs that isolate AI cores during ether storm surges",
        ],
        "advanced_benefits": [
            "Design AI systems that actively learn from etheric phenomena rather than fearing them",
            "Integrate ether perception into AI decision loops without recursive collapse",
        ],
        "master_benefits": [
            "Create AI architectures capable of autonomous etheric navigation",
            "Synthesize AI-ether hybrid intelligences resistant to all known corruption vectors",
        ],
    },

    "Collective Consciousness Integrator": {
        "category": CATEGORY_ETHERIC,
        "description": (
            "Facilitators who guide individuals through the safe merging of personal "
            "consciousness into larger shared awareness networks, ensuring identity stability "
            "and ethical participation."
        ),
        "skills": [
            "consciousness synchronization",
            "identity boundary management",
            "etheric signal alignment",
            "collective cognition facilitation",
            "psychological stabilization",
        ],
        "base_benefits": [
            "Guide small groups through supervised, temporary consciousness sharing",
            "Maintain individual identity boundaries during introductory merge sessions",
        ],
        "intermediate_benefits": [
            "Align etheric signals from multiple participants into a coherent shared field",
            "Stabilize participants experiencing identity drift during extended merges",
        ],
        "advanced_benefits": [
            "Facilitate permanent collective awareness networks across mixed-species teams",
            "Resolve identity conflicts within shared consciousness networks without fragmentation",
        ],
        "master_benefits": [
            "Integrate dozens of minds into stable collective networks spanning light-minutes",
            "Restore fragmented identities after catastrophic collective consciousness collapse",
        ],
    },

    "Etheric Communion Guide": {
        "category": CATEGORY_ETHERIC,
        "description": (
            "Practitioners who lead groups in ritualized processes that allow minds to connect "
            "through etheric resonance, forming temporary or permanent collective awareness."
        ),
        "skills": [
            "group resonance facilitation",
            "etheric field modulation",
            "ritual systems design",
            "emotional field harmonization",
            "collective awareness stabilization",
        ],
        "base_benefits": [
            "Lead structured group resonance sessions for small crews or delegations",
            "Modulate local etheric fields to support communion practices",
        ],
        "intermediate_benefits": [
            "Design rituals that reliably achieve deep resonance across species boundaries",
            "Harmonize emotionally discordant groups into a shared awareness state",
        ],
        "advanced_benefits": [
            "Sustain collective awareness fields across multi-day diplomatic or research sessions",
            "Facilitate healing communion for crews traumatized by consciousness fragmentation",
        ],
        "master_benefits": [
            "Guide mass communion events that reshape political and cultural relationships permanently",
            "Stabilize collective awareness under ether storm conditions that would unmake lesser networks",
        ],
    },

    "Consciousness Confluence Architect": {
        "category": CATEGORY_ETHERIC,
        "description": (
            "Researchers and designers who build systems that allow many minds to combine "
            "their cognitive abilities into a unified problem-solving network."
        ),
        "skills": [
            "collective cognition modeling",
            "neural-network architecture",
            "etheric signal routing",
            "distributed intelligence design",
            "system stability analysis",
        ],
        "base_benefits": [
            "Model how multiple minds share cognitive load on defined problem sets",
            "Route etheric signals between willing participants with minimal latency",
        ],
        "intermediate_benefits": [
            "Architect distributed intelligence networks that outperform individual cognition",
            "Identify and patch stability risks in growing consciousness confluence systems",
        ],
        "advanced_benefits": [
            "Design self-healing confluence architectures resilient to participant dropout",
            "Build systems that amplify collective intelligence non-linearly with scale",
        ],
        "master_benefits": [
            "Construct permanent galactic-scale confluence networks for research and governance",
            "Synthesize a single unified intelligence from thousands of willing participants",
        ],
    },

    "Shared Mind Systems Steward": {
        "category": CATEGORY_ETHERIC,
        "description": (
            "Custodians responsible for maintaining long-term collective consciousness networks "
            "used by research guilds, exploration teams, and governance bodies."
        ),
        "skills": [
            "collective memory maintenance",
            "identity conflict resolution",
            "network monitoring",
            "consciousness integrity auditing",
            "participation governance",
        ],
        "base_benefits": [
            "Monitor shared-mind networks for early signs of identity corruption or drift",
            "Maintain collective memory archives against degradation and forgery",
        ],
        "intermediate_benefits": [
            "Mediate identity conflicts that arise within long-running shared networks",
            "Conduct consciousness integrity audits after anomalous events",
        ],
        "advanced_benefits": [
            "Govern participation rules for high-security collective consciousness systems",
            "Restore damaged collective memories after etheric disruption events",
        ],
        "master_benefits": [
            "Sustain century-spanning shared-mind networks with negligible identity loss",
            "Investigate and remediate deliberate consciousness corruption attempts",
        ],
    },

    "Reality Weaver": {
        "category": CATEGORY_ETHERIC,
        "description": (
            "Masters who craft temporary physical structures by manipulating local reality fabric "
            "through etheric projection. Their constructs blur the line between substance and belief."
        ),
        "skills": [
            "etheric projection",
            "structural coherence weaving",
            "reality fabric sensing",
            "matter-etheric binding",
            "construct stabilization",
        ],
        "base_benefits": [
            "Create minor temporary physical structures from etheric projection",
            "Sense instabilities in local reality fabric before they manifest",
        ],
        "intermediate_benefits": [
            "Weave stable etheric constructs lasting hours to days without maintenance",
            "Bind etheric projections to physical matter for permanent reinforcement",
        ],
        "advanced_benefits": [
            "Construct large-scale etheric architecture used for shelter, barriers, or ceremony",
            "Repair localized reality fabric tears caused by dimensional or weapon events",
        ],
        "master_benefits": [
            "Rewrite local physical laws within a contained region for tactical or creative purposes",
            "Stabilize large-scale reality distortions that would otherwise destroy inhabited areas",
        ],
    },

    # =========================================================================
    # ENGINEERING — hardware, propulsion, construction, materials, infrastructure
    # =========================================================================

    "Quantum Navigator": {
        "category": CATEGORY_ENGINEERING,
        "description": (
            "Experts in plotting safe and efficient courses through normal space, etheric streams, "
            "unstable corridors, and dimensional shear zones. They combine mathematics, "
            "intuition, and field analysis."
        ),
        "skills": [
            "astrogation",
            "probability modeling",
            "ether current mapping",
            "dimensional route planning",
            "hazard prediction",
        ],
        "base_benefits": [
            "Plot optimal routes through charted normal space with reduced fuel cost",
            "Model route probabilities to minimize travel risk in familiar systems",
        ],
        "intermediate_benefits": [
            "Map active ether currents for significantly faster transit on long routes",
            "Draft viable dimensional route plans for moderately unstable corridors",
        ],
        "advanced_benefits": [
            "Predict spatial hazards before they manifest and reroute in time to avoid them",
            "Navigate through dimensional shear zones that are impassable to standard pilots",
        ],
        "master_benefits": [
            "Chart reliable routes through regions considered permanently unnavigable",
            "Guide entire fleets through catastrophic ether storm systems without loss",
        ],
    },

    "Ether Drive Tuner": {
        "category": CATEGORY_ENGINEERING,
        "description": (
            "Technicians who calibrate ether-enhanced propulsion systems for stability, efficiency, "
            "and safe passage across long-range routes. A bad one turns a voyage into cosmic soup."
        ),
        "skills": [
            "propulsion calibration",
            "energy harmonics analysis",
            "field stabilization",
            "maintenance diagnostics",
            "ether safety procedures",
        ],
        "base_benefits": [
            "Calibrate ether drive harmonics for standard safe operation",
            "Run diagnostics that identify propulsion faults before departure",
        ],
        "intermediate_benefits": [
            "Tune drive field stabilization for extended high-energy operation",
            "Increase ether drive efficiency by 15–25% through harmonic optimization",
        ],
        "advanced_benefits": [
            "Push drive systems past rated limits safely in emergency situations",
            "Retrofit older propulsion systems with ether enhancement arrays",
        ],
        "master_benefits": [
            "Tune experimental or prototype drives that no one else can safely operate",
            "Recover ships from catastrophic drive failures mid-transit through field improvisation",
        ],
    },

    "Hull Morphology Architect": {
        "category": CATEGORY_ENGINEERING,
        "description": (
            "Designers of adaptive hull systems capable of reshaping in response to environment, "
            "combat conditions, and mission requirements."
        ),
        "skills": [
            "adaptive materials design",
            "nano-structural engineering",
            "stress modeling",
            "reconfiguration protocols",
            "combat survivability planning",
        ],
        "base_benefits": [
            "Design hull sections capable of limited shape adaptation to environmental pressure",
            "Model structural stress under standard combat and transit loads",
        ],
        "intermediate_benefits": [
            "Engineer nano-structural systems that actively repair minor hull damage in transit",
            "Write reconfiguration protocols that reshape hull geometry in under 30 seconds",
        ],
        "advanced_benefits": [
            "Design hulls that morph fully between stealth, combat, and utility profiles",
            "Model survivability across extreme combat scenarios and plan for each contingency",
        ],
        "master_benefits": [
            "Construct hulls that adapt autonomously to threats without crew input",
            "Design ships that remain structurally viable after catastrophic weapons impact",
        ],
    },

    "Etheric Shield Weaver": {
        "category": CATEGORY_ENGINEERING,
        "description": (
            "Specialists who construct and maintain defensive energy matrices that combine "
            "engineering with etheric modulation to protect ships, stations, and settlements."
        ),
        "skills": [
            "shield lattice design",
            "defensive harmonics tuning",
            "impact absorption modeling",
            "field redundancy planning",
            "battlefield recalibration",
        ],
        "base_benefits": [
            "Design and deploy basic etheric shield lattices for ship or station protection",
            "Tune defensive harmonics to reduce energy bleed-through under standard fire",
        ],
        "intermediate_benefits": [
            "Model and optimize impact absorption curves for sustained combat scenarios",
            "Build redundant field layers that maintain coverage when primary systems fail",
        ],
        "advanced_benefits": [
            "Recalibrate shields mid-battle to counter novel or exotic weapon signatures",
            "Design etheric shield matrices that absorb and redirect incoming energy",
        ],
        "master_benefits": [
            "Weave planetary-scale defensive fields from distributed station networks",
            "Neutralize exotic weapon types — including consciousness attacks — through harmonic inversion",
        ],
    },

    "Gravitic Systems Engineer": {
        "category": CATEGORY_ENGINEERING,
        "description": (
            "Engineers responsible for gravity control, inertial damping, local mass manipulation, "
            "and gravitic field stability in ships, habitats, and industrial platforms."
        ),
        "skills": [
            "gravity field management",
            "inertial compensation",
            "mass-distribution modeling",
            "system diagnostics",
            "safety compliance",
        ],
        "base_benefits": [
            "Maintain artificial gravity and inertial damping systems within rated parameters",
            "Run gravitic system diagnostics and flag deviations before failure",
        ],
        "intermediate_benefits": [
            "Tune inertial compensation for high-G maneuver profiles without crew injury",
            "Model mass distribution changes and adjust field balance dynamically",
        ],
        "advanced_benefits": [
            "Manipulate local gravity fields for tactical, industrial, or navigational advantage",
            "Design custom gravitic profiles for exotic environments or alien crew needs",
        ],
        "master_benefits": [
            "Control mass at a scale sufficient to deflect small asteroids or disable enemy ships",
            "Engineer gravitational lenses for sensor and communication amplification",
        ],
    },

    "Bio-Integrated Manufacturing Director": {
        "category": CATEGORY_ENGINEERING,
        "description": (
            "Leaders of facilities where engineered organisms, machine systems, and etheric "
            "processes collaborate to produce goods sustainably and efficiently."
        ),
        "skills": [
            "biomanufacturing oversight",
            "workflow optimization",
            "ethics compliance",
            "cross-system integration",
            "production planning",
        ],
        "base_benefits": [
            "Oversee bio-manufacturing workflows and maintain baseline production quotas",
            "Identify integration bottlenecks between biological and machine subsystems",
        ],
        "intermediate_benefits": [
            "Optimize production cycles to reduce waste and energy draw by 20–35%",
            "Navigate ethics compliance requirements for organisms used in manufacturing",
        ],
        "advanced_benefits": [
            "Design facility-wide cross-system integration that doubles throughput",
            "Scale production from artisanal to industrial without quality loss",
        ],
        "master_benefits": [
            "Direct continent-scale bio-manufacturing networks on newly colonized worlds",
            "Achieve fully closed-loop production with near-zero environmental externality",
        ],
    },

    "Nano-Fabrication Artisan": {
        "category": CATEGORY_ENGINEERING,
        "description": (
            "Masters of molecular and nano-scale construction who create precision tools, "
            "components, implants, and rare materials unavailable from standard fabricators."
        ),
        "skills": [
            "molecular assembly",
            "precision fabrication",
            "materials science",
            "quality assurance",
            "design interpretation",
        ],
        "base_benefits": [
            "Fabricate precision components at nano-scale beyond standard printer tolerance",
            "Read and interpret complex molecular-level design specifications",
        ],
        "intermediate_benefits": [
            "Produce implant-grade materials with biocompatibility verified at atomic resolution",
            "Quality-assure nano-scale production runs with sub-angstrom defect detection",
        ],
        "advanced_benefits": [
            "Synthesize rare materials that cannot be produced at macro scale",
            "Create unique nano-scale devices that exist nowhere else in known space",
        ],
        "master_benefits": [
            "Fabricate components for experimental technologies not yet in production",
            "Produce materials with properties that violate standard engineering predictions",
        ],
    },

    "Habitat Systems Warden": {
        "category": CATEGORY_ENGINEERING,
        "description": (
            "Caretakers and managers of life-supporting environments in stations, domes, "
            "subterranean cities, and long-range vessels."
        ),
        "skills": [
            "life support oversight",
            "air-water cycle management",
            "failure response",
            "population support planning",
            "environmental diagnostics",
        ],
        "base_benefits": [
            "Maintain air, water, and thermal cycles within safe margins for a single habitat",
            "Run environmental diagnostics and respond to basic life support alarms",
        ],
        "intermediate_benefits": [
            "Plan population support capacity for expanding settlements or long voyages",
            "Design failure-response protocols that protect occupants during system emergencies",
        ],
        "advanced_benefits": [
            "Sustain multiple complex habitats simultaneously under degraded resource conditions",
            "Adapt life support systems to entirely new environmental requirements on short notice",
        ],
        "master_benefits": [
            "Oversee planetary-scale life support infrastructure for millions of inhabitants",
            "Design self-repairing habitat systems with centuries of autonomous operating life",
        ],
    },

    "Planetary Renewal Engineer": {
        "category": CATEGORY_ENGINEERING,
        "description": (
            "Professionals who rehabilitate damaged ecosystems, post-industrial worlds, and "
            "war-scarred biospheres using integrated technical and etheric methods."
        ),
        "skills": [
            "restoration engineering",
            "damage assessment",
            "soil-water remediation",
            "ecosystem sequencing",
            "adaptive intervention design",
        ],
        "base_benefits": [
            "Assess ecosystem damage and produce a triage-level restoration report",
            "Remediate contaminated soil and water zones using proven biological methods",
        ],
        "intermediate_benefits": [
            "Sequence ecosystem restoration phases to maximize resilience during recovery",
            "Design adaptive interventions that adjust to unexpected environmental responses",
        ],
        "advanced_benefits": [
            "Restore biospheres damaged by industrial collapse within two to three generations",
            "Apply etheric methods to accelerate remediation timelines by 40–60%",
        ],
        "master_benefits": [
            "Rebuild biospheres from near-zero biological diversity after extinction events",
            "Design war-world restoration programs that double as diplomatic goodwill initiatives",
        ],
    },

    "Dimensional Gate Custodian": {
        "category": CATEGORY_ENGINEERING,
        "description": (
            "Operators and protectors of gateways, interdimensional crossings, and high-risk "
            "transit structures linking remote or unstable regions."
        ),
        "skills": [
            "gate operations",
            "stability monitoring",
            "access control",
            "emergency shutdown procedure",
            "dimensional safety compliance",
        ],
        "base_benefits": [
            "Operate dimensional gates through standard transit cycles safely",
            "Monitor gate stability readings and escalate anomalous data promptly",
        ],
        "intermediate_benefits": [
            "Manage access control under contested or politically sensitive conditions",
            "Execute emergency gate shutdowns without dimensional backlash",
        ],
        "advanced_benefits": [
            "Stabilize degrading gate infrastructure under active operational load",
            "Improvise gate repairs using field materials when supply chains are unavailable",
        ],
        "master_benefits": [
            "Construct new dimensional gate infrastructure in previously unlinked regions",
            "Safely close permanently destabilized gates without cascading dimensional damage",
        ],
    },

    "Wormline Infrastructure Engineer": {
        "category": CATEGORY_ENGINEERING,
        "description": (
            "Engineers who maintain corridor beacons, transit anchors, route stabilizers, "
            "and navigational hardware across strategic interstellar lanes."
        ),
        "skills": [
            "infrastructure maintenance",
            "systems engineering",
            "route integrity diagnostics",
            "repair logistics",
            "redundancy design",
        ],
        "base_benefits": [
            "Maintain corridor beacon networks and replace failed components",
            "Run route integrity diagnostics on wormline lanes under active traffic",
        ],
        "intermediate_benefits": [
            "Coordinate repair logistics across distributed infrastructure spanning multiple systems",
            "Design redundancy systems that keep lanes operational when primary anchors fail",
        ],
        "advanced_benefits": [
            "Extend wormline coverage into newly charted or previously isolated systems",
            "Harden infrastructure against deliberate attack or anomaly-driven degradation",
        ],
        "master_benefits": [
            "Architect entire interstellar route networks for new colonies or expansion zones",
            "Restore wormline lanes collapsed by catastrophic events within days rather than years",
        ],
    },

    "Atmospheric Harvest Technician": {
        "category": CATEGORY_ENGINEERING,
        "description": (
            "Operators of systems that collect gases, particulates, volatile compounds, and "
            "ambient energy from planetary or orbital environments for industrial use."
        ),
        "skills": [
            "harvest system operation",
            "chemical monitoring",
            "environmental safety",
            "equipment maintenance",
            "resource processing",
        ],
        "base_benefits": [
            "Operate atmospheric harvest arrays within rated safety envelopes",
            "Monitor chemical composition of collected streams for contaminants",
        ],
        "intermediate_benefits": [
            "Optimize collection yields by 20–35% through timing and altitude adjustments",
            "Safely harvest volatile compounds from marginal or unstable atmospheres",
        ],
        "advanced_benefits": [
            "Design custom harvest configurations for exotic atmospheric chemistries",
            "Process rare ambient energy types into usable fuel or feedstock forms",
        ],
        "master_benefits": [
            "Extract resources from stellar atmospheres or gas giant layers hostile to standard systems",
            "Design fully autonomous harvest networks requiring zero crew involvement",
        ],
    },

    "Programmable Matter Architect": {
        "category": CATEGORY_ENGINEERING,
        "description": (
            "Engineers who design large-scale systems built from programmable matter — materials "
            "composed of nano-scale units capable of dynamically altering shape, structure, "
            "and functionality. Their work is central to adaptive ships, self-repairing "
            "infrastructure, and reconfigurable habitats."
        ),
        "skills": [
            "programmable matter system design",
            "nano-unit coordination algorithms",
            "structural reconfiguration modeling",
            "materials programming",
            "adaptive architecture engineering",
        ],
        "base_benefits": [
            "Design programmable matter systems for basic structural reconfiguration tasks",
            "Write coordination algorithms for nano-unit arrays up to moderate complexity",
        ],
        "intermediate_benefits": [
            "Model reconfiguration sequences across full ship or habitat scales",
            "Program matter substrates to transition between three or more distinct structural states",
        ],
        "advanced_benefits": [
            "Architect adaptive ships that autonomously reconfigure in response to damage or mission",
            "Design programmable matter systems capable of self-assembly from raw nano-unit stock",
        ],
        "master_benefits": [
            "Create planetary-scale programmable matter infrastructure without oversight",
            "Design matter systems that evolve their own coordination algorithms over time",
        ],
    },

    "Nano-Swarm Systems Engineer": {
        "category": CATEGORY_ENGINEERING,
        "description": (
            "Specialists who design and control cooperative swarms of nano-machines capable "
            "of building, repairing, or transforming structures at microscopic scales."
        ),
        "skills": [
            "swarm coordination algorithms",
            "distributed control systems",
            "nano-machine fabrication",
            "failure tolerance design",
            "dynamic systems simulation",
        ],
        "base_benefits": [
            "Deploy nano-swarms for supervised repair and fabrication tasks",
            "Write distributed control algorithms for swarms of up to ten thousand units",
        ],
        "intermediate_benefits": [
            "Design failure-tolerant swarms that continue operating despite 30–40% unit loss",
            "Simulate swarm behavior in complex dynamic environments before deployment",
        ],
        "advanced_benefits": [
            "Build autonomous nano-swarms capable of construction without ongoing human instruction",
            "Fabricate custom nano-machine variants optimized for extreme environments",
        ],
        "master_benefits": [
            "Deploy city-scale swarms that build infrastructure at rates rivaling conventional industry",
            "Design self-replicating nano-swarms with hard-coded ethical and operational constraints",
        ],
    },

    "Programmable Matter Fabrication Technician": {
        "category": CATEGORY_ENGINEERING,
        "description": (
            "Technicians who operate fabrication facilities that produce programmable matter "
            "substrates used in construction, medicine, ship systems, and industrial platforms."
        ),
        "skills": [
            "nano-fabrication operations",
            "substrate calibration",
            "production monitoring",
            "materials testing",
            "quality assurance",
        ],
        "base_benefits": [
            "Operate programmable matter fabrication lines at standard output levels",
            "Calibrate substrate parameters to specification and verify batch quality",
        ],
        "intermediate_benefits": [
            "Increase facility throughput by 25% through process refinement",
            "Detect and quarantine defective substrate batches before distribution",
        ],
        "advanced_benefits": [
            "Produce specialized substrates tailored to unique architectural or medical requirements",
            "Manage fabrication facility operations during resource shortage or equipment failure",
        ],
        "master_benefits": [
            "Design new substrate formulations with novel programmable properties",
            "Run a fabrication network supplying programmable matter to an entire star system",
        ],
    },

    "Adaptive Nano-Structure Field Operator": {
        "category": CATEGORY_ENGINEERING,
        "description": (
            "Operators responsible for deploying programmable matter structures in the field, "
            "often during exploration, disaster recovery, or planetary construction efforts."
        ),
        "skills": [
            "field deployment planning",
            "structural stabilization",
            "remote nano-structure control",
            "environmental adaptation",
            "rapid infrastructure assembly",
        ],
        "base_benefits": [
            "Deploy programmable matter structures in prepared field environments",
            "Remotely control nano-structure arrays from standard operator distances",
        ],
        "intermediate_benefits": [
            "Stabilize structures in hostile or unpredictable environments mid-assembly",
            "Adapt deployment protocols on the fly when field conditions change unexpectedly",
        ],
        "advanced_benefits": [
            "Assemble rapid-response infrastructure in disaster zones within hours",
            "Deploy structures in extreme environments — volcanic, aquatic, vacuum — without failure",
        ],
        "master_benefits": [
            "Lead field teams assembling entire settlement bases from nano-structure stock in days",
            "Operate adaptive structures under active conflict without loss of structural integrity",
        ],
    },

    "Dark Matter Engineer": {
        "category": CATEGORY_ENGINEERING,
        "description": (
            "Engineers who harness and apply dark matter — the invisible backbone of galactic "
            "structure — for propulsion, shielding, sensing, and exotic material synthesis."
        ),
        "skills": [
            "dark matter detection",
            "exotic field manipulation",
            "dark energy coupling",
            "experimental systems integration",
            "hazard containment",
        ],
        "base_benefits": [
            "Detect and characterize dark matter concentrations at operationally useful ranges",
            "Safely contain dark matter interactions within experimental apparatus",
        ],
        "intermediate_benefits": [
            "Couple dark energy fields to ship systems for marginal but meaningful efficiency gains",
            "Integrate dark matter sensors into standard sensor arrays for enhanced deep-space mapping",
        ],
        "advanced_benefits": [
            "Harness dark matter flow for novel propulsion or shielding applications",
            "Synthesize exotic materials using dark matter interactions as a catalyst",
        ],
        "master_benefits": [
            "Design dark matter power plants capable of energy output rivaling small stars",
            "Manipulate galactic-scale dark matter structures to alter transit corridors",
        ],
    },

    # =========================================================================
    # SCIENTIFIC — research, analysis, history, ecology, cartography
    # =========================================================================

    "Chrono-Synthetic Flux Analyst": {
        "category": CATEGORY_SCIENTIFIC,
        "description": (
            "Researchers and operators who study temporal drag, loop anomalies, and "
            "time-distortion effects on ships, systems, and interstellar routes."
        ),
        "skills": [
            "temporal anomaly detection",
            "time-series modeling",
            "causality risk assessment",
            "chronometric instrumentation",
            "flux mitigation planning",
        ],
        "base_benefits": [
            "Detect temporal anomalies at operationally relevant ranges before ships enter them",
            "Run time-series models that identify causal risk in proposed route plans",
        ],
        "intermediate_benefits": [
            "Operate chronometric instrumentation under active flux conditions without data loss",
            "Draft flux mitigation plans that reduce temporal exposure by 40–60%",
        ],
        "advanced_benefits": [
            "Characterize novel temporal anomaly types with no prior observational reference",
            "Advise fleet commanders on causality-safe operational sequences in distorted space",
        ],
        "master_benefits": [
            "Map temporal flux zones with enough precision to navigate them rather than avoid them",
            "Develop mitigation protocols that allow operations within normally impassable loop zones",
        ],
    },

    "Void Cartographer": {
        "category": CATEGORY_SCIENTIFIC,
        "description": (
            "Map-makers of deep space, wormline corridors, dead zones, and shifting etheric "
            "territories. Their charts are part science, part art, part anti-nightmare device."
        ),
        "skills": [
            "spatial mapping",
            "remote sensing",
            "route documentation",
            "anomaly classification",
            "navigational data modeling",
        ],
        "base_benefits": [
            "Produce accurate spatial maps of charted systems with full navigational metadata",
            "Classify detected anomalies and attach risk ratings to navigational data",
        ],
        "intermediate_benefits": [
            "Chart shifting etheric territories that change between observation windows",
            "Build navigational data models that update dynamically from live sensor feeds",
        ],
        "advanced_benefits": [
            "Map void corridors and dead zones that standard instruments cannot resolve",
            "Document routes through previously uncharted regions for subsequent fleet use",
        ],
        "master_benefits": [
            "Produce charts of the galactic fringe accurate enough to enable first-contact missions",
            "Create living navigational models that predict territorial shifts before they occur",
        ],
    },

    "Terraforming Ecologist": {
        "category": CATEGORY_SCIENTIFIC,
        "description": (
            "Scientists who design living planetary systems capable of long-term equilibrium, "
            "balancing biology, atmosphere, water cycles, and local species compatibility."
        ),
        "skills": [
            "ecosystem modeling",
            "biosphere design",
            "atmospheric planning",
            "species compatibility assessment",
            "restoration science",
        ],
        "base_benefits": [
            "Model proposed ecosystems for stability over 50-year planning horizons",
            "Assess compatibility between introduced and native species before deployment",
        ],
        "intermediate_benefits": [
            "Design multi-layer biospheres with self-correcting atmospheric feedback loops",
            "Plan atmospheric chemistry transitions that protect colonists during transformation",
        ],
        "advanced_benefits": [
            "Engineer living planetary systems capable of operating without external input",
            "Correct terraforming failures resulting from incomplete initial data",
        ],
        "master_benefits": [
            "Design biospheres stable for geological timescales across extreme environments",
            "Terraform worlds classified as permanently hostile by standard engineering doctrine",
        ],
    },

    "Etheric Materials Synthesist": {
        "category": CATEGORY_SCIENTIFIC,
        "description": (
            "Researchers and industrial specialists who develop substances whose properties shift "
            "in response to etheric influence, emotional fields, or environmental stress."
        ),
        "skills": [
            "material synthesis",
            "ether-reactive compound design",
            "laboratory experimentation",
            "failure testing",
            "applied chemistry",
        ],
        "base_benefits": [
            "Synthesize known ether-reactive compounds reliably in a laboratory setting",
            "Design controlled failure tests that characterize material limits without catastrophe",
        ],
        "intermediate_benefits": [
            "Create novel ether-reactive compounds with deliberately engineered response profiles",
            "Apply chemistry knowledge to adapt synthesis procedures for field conditions",
        ],
        "advanced_benefits": [
            "Design materials that actively respond to consciousness states for smart-system use",
            "Synthesize compounds usable as both industrial feedstock and etheric amplifiers",
        ],
        "master_benefits": [
            "Create entirely new material classes with no prior theoretical basis",
            "Synthesize substances capable of self-organization under etheric field influence",
        ],
    },

    "Relic Recovery Specialist": {
        "category": CATEGORY_SCIENTIFIC,
        "description": (
            "Professionals who identify, secure, and interpret artifacts from lost civilizations, "
            "ancient star-faring cultures, and dangerous ruins."
        ),
        "skills": [
            "artifact identification",
            "field archaeology",
            "containment procedure",
            "historical inference",
            "hazard assessment",
        ],
        "base_benefits": [
            "Identify artifact age, origin culture, and likely function from physical examination",
            "Execute field containment procedures for unstable or dangerous relics",
        ],
        "intermediate_benefits": [
            "Conduct excavations in structurally compromised ruins without triggering collapse",
            "Infer historical context from fragmentary artifact assemblages",
        ],
        "advanced_benefits": [
            "Recover and stabilize active relics that continue to function or emit energy",
            "Extract full operational knowledge from alien artifact systems with no living experts",
        ],
        "master_benefits": [
            "Locate and recover artifacts from sites protected by ancient automated defense systems",
            "Reconstruct lost civilizations' technology bases from recovered artifact catalogs",
        ],
    },

    "Ancient Systems Decipherer": {
        "category": CATEGORY_SCIENTIFIC,
        "description": (
            "Scholars and technologists who interpret forgotten code systems, symbolic architectures, "
            "and machine languages from extinct civilizations."
        ),
        "skills": [
            "symbolic analysis",
            "pattern recognition",
            "linguistic reconstruction",
            "legacy systems interpretation",
            "comparative historiography",
        ],
        "base_benefits": [
            "Identify structural patterns in unknown code systems and propose candidate meanings",
            "Reconstruct partial machine languages from fragmentary surviving records",
        ],
        "intermediate_benefits": [
            "Interface with legacy alien systems at a functional level without full decipherment",
            "Apply comparative historiography to narrow the origin of anonymous systems",
        ],
        "advanced_benefits": [
            "Fully reconstruct and operate extinct civilization machine languages",
            "Decipher symbolic architectures embedded in physical infrastructure rather than text",
        ],
        "master_benefits": [
            "Crack the machine language of civilizations with no known linguistic relatives",
            "Extract operating knowledge from ancient systems predating known starfaring history",
        ],
    },

    "Etheric Historian": {
        "category": CATEGORY_SCIENTIFIC,
        "description": (
            "Historians who study the development of etheric awakening, cosmic civilizations, "
            "and the social consequences of energy-consciousness integration across millennia."
        ),
        "skills": [
            "archival research",
            "historical synthesis",
            "source criticism",
            "cultural analysis",
            "comparative civilization study",
        ],
        "base_benefits": [
            "Locate and retrieve primary source materials from distributed galactic archives",
            "Apply source criticism to identify forgeries, redactions, and propaganda",
        ],
        "intermediate_benefits": [
            "Synthesize historical patterns from fragmentary or contradictory source bases",
            "Conduct comparative civilizational analysis across multiple interstellar cultures",
        ],
        "advanced_benefits": [
            "Reconstruct historical events from indirect evidence when direct records are lost",
            "Produce historical analyses that predict near-term political or social trajectories",
        ],
        "master_benefits": [
            "Write definitive histories of civilizations that left no surviving witnesses",
            "Use historical pattern recognition to identify catastrophic risks before they materialize",
        ],
    },

    "Closed-Loop Sustainability Planner": {
        "category": CATEGORY_SCIENTIFIC,
        "description": (
            "Designers of industrial and urban systems where waste, energy, and matter are cycled "
            "with minimal loss across long timescales."
        ),
        "skills": [
            "systems ecology",
            "resource loop design",
            "efficiency modeling",
            "environmental auditing",
            "long-term planning",
        ],
        "base_benefits": [
            "Audit existing systems and identify the largest waste streams for loop closure",
            "Model resource flows through industrial processes and project multi-decade outcomes",
        ],
        "intermediate_benefits": [
            "Design closed-loop resource cycles that reduce external input requirements by 30–50%",
            "Plan system transitions that maintain operational continuity during redesign",
        ],
        "advanced_benefits": [
            "Achieve near-complete closure of matter and energy cycles in complex industrial systems",
            "Design systems that improve efficiency autonomously as operational data accumulates",
        ],
        "master_benefits": [
            "Design fully closed planetary economies with no net resource extraction requirement",
            "Build sustainability frameworks that scale from individual ships to entire civilizations",
        ],
    },

    "Cognitive Archive Curator": {
        "category": CATEGORY_SCIENTIFIC,
        "description": (
            "Custodians of memory libraries, identity backups, consciousness records, and "
            "shared experiential archives."
        ),
        "skills": [
            "digital preservation",
            "memory indexing",
            "identity verification",
            "archive security",
            "metadata design",
        ],
        "base_benefits": [
            "Preserve consciousness records with standard fidelity against decay and corruption",
            "Index memory archives for fast and accurate retrieval under query load",
        ],
        "intermediate_benefits": [
            "Design metadata schemas that allow complex cross-archive searches across species types",
            "Verify identity provenance of stored consciousness records against tampering",
        ],
        "advanced_benefits": [
            "Secure archives against sophisticated intrusion including etheric access attempts",
            "Restore partially corrupted consciousness records through pattern inference",
        ],
        "master_benefits": [
            "Curate archives spanning billions of individual consciousness records without loss",
            "Reconstruct identity records from catastrophically damaged or fragmented stores",
        ],
    },

    "Cultural Pattern Archivist": {
        "category": CATEGORY_SCIENTIFIC,
        "description": (
            "Researchers who preserve rituals, symbols, oral traditions, aesthetic systems, "
            "and identity-forming practices across civilizations before they are lost."
        ),
        "skills": [
            "ethnographic documentation",
            "classification",
            "symbol analysis",
            "oral history collection",
            "cultural preservation",
        ],
        "base_benefits": [
            "Document living cultural practices through direct ethnographic fieldwork",
            "Classify symbols and ritual elements within a structured preservation framework",
        ],
        "intermediate_benefits": [
            "Collect oral histories across language barriers using interpretive and etheric tools",
            "Analyze symbol systems to reconstruct meaning lost through cultural disruption",
        ],
        "advanced_benefits": [
            "Preserve cultural patterns from communities facing extinction or forced assimilation",
            "Build cross-civilization pattern libraries that reveal universal structural themes",
        ],
        "master_benefits": [
            "Reconstruct the cultural identity of peoples who left no living practitioners",
            "Produce preservation archives sufficient to revive extinct cultural traditions completely",
        ],
    },

    "Myth-Systems Scholar": {
        "category": CATEGORY_SCIENTIFIC,
        "description": (
            "Scholars who study the interplay between religion, cosmology, symbolic meaning, "
            "and technological belief systems across the known worlds."
        ),
        "skills": [
            "comparative religion",
            "symbolic interpretation",
            "doctrinal analysis",
            "historical contextualization",
            "narrative synthesis",
        ],
        "base_benefits": [
            "Analyze religious and cosmological texts for structural and historical patterns",
            "Contextualize doctrinal claims within the political and technological circumstances of their origin",
        ],
        "intermediate_benefits": [
            "Conduct comparative studies across multiple alien and human belief systems",
            "Synthesize myth-system narratives into actionable diplomatic or cultural briefings",
        ],
        "advanced_benefits": [
            "Predict how myth-system beliefs will constrain or enable political negotiations",
            "Identify covert ideological structures embedded in apparently secular institutions",
        ],
        "master_benefits": [
            "Construct integrative myth-system frameworks that reduce inter-faith conflict",
            "Advise galactic diplomacy on the religious implications of civilization-scale decisions",
        ],
    },

    "Memory Forensics Analyst": {
        "category": CATEGORY_SCIENTIFIC,
        "description": (
            "Investigators who reconstruct events from damaged consciousness records, ship logs, "
            "memory archives, and experiential fragments."
        ),
        "skills": [
            "forensic reconstruction",
            "data recovery",
            "pattern comparison",
            "evidence analysis",
            "testimony validation",
        ],
        "base_benefits": [
            "Recover readable data from moderately damaged consciousness records or ship logs",
            "Compare recovered fragments against known baselines to detect alteration",
        ],
        "intermediate_benefits": [
            "Reconstruct event sequences from fragmentary or out-of-order memory data",
            "Validate or refute testimony claims against physical consciousness record evidence",
        ],
        "advanced_benefits": [
            "Recover evidence from records intentionally corrupted or partially erased",
            "Build comprehensive event timelines from distributed evidence across multiple sources",
        ],
        "master_benefits": [
            "Reconstruct full events from records reduced to 5% or less of original coherence",
            "Identify consciousness record forgeries indistinguishable to all other analysis methods",
        ],
    },

    "Resource Vein Prospector": {
        "category": CATEGORY_SCIENTIFIC,
        "description": (
            "Surveyors who locate valuable energy concentrations, mineral bands, biological "
            "reservoirs, and ether-reactive deposits across planets, moons, and asteroids."
        ),
        "skills": [
            "survey analysis",
            "remote sensing",
            "deposit modeling",
            "expedition planning",
            "field reporting",
        ],
        "base_benefits": [
            "Survey planetary surfaces for mineral and energy deposits using remote sensing",
            "Model deposit extent and quality from surface and orbital data",
        ],
        "intermediate_benefits": [
            "Locate ether-reactive deposits invisible to standard geological survey techniques",
            "Plan multi-site survey expeditions in hostile or poorly charted environments",
        ],
        "advanced_benefits": [
            "Identify deep-subsurface veins from surface anomaly signatures alone",
            "Produce survey reports accurate enough to support immediate industrial development",
        ],
        "master_benefits": [
            "Locate strategic deposits that alter system-level economic and political power",
            "Survey entire planetary systems in single expedition cycles with full deposit coverage",
        ],
    },

    "Knowledge Systems Mentor": {
        "category": CATEGORY_SCIENTIFIC,
        "description": (
            "Mentors who guide apprentices, students, and researchers through the deeper "
            "structures of knowledge, teaching them how to think critically and synthesize "
            "information across disciplines."
        ),
        "skills": [
            "critical thinking instruction",
            "research mentorship",
            "knowledge integration",
            "intellectual coaching",
            "disciplinary synthesis",
        ],
        "base_benefits": [
            "Teach structured critical thinking methods that measurably improve student research quality",
            "Mentor individual researchers through their first independent projects",
        ],
        "intermediate_benefits": [
            "Integrate knowledge from three or more disciplines into coherent research programs",
            "Coach teams through complex intellectual challenges without providing direct solutions",
        ],
        "advanced_benefits": [
            "Develop cohort mentorship programs that accelerate research productivity fleet-wide",
            "Synthesize divergent disciplinary perspectives into novel research frameworks",
        ],
        "master_benefits": [
            "Train a generation of researchers who themselves become master mentors",
            "Design knowledge systems that allow civilizations to preserve intellectual capacity across catastrophes",
        ],
    },

    "Cognitive Apprenticeship Instructor": {
        "category": CATEGORY_SCIENTIFIC,
        "description": (
            "Educators who train learners through guided practice in complex professions, "
            "emphasizing observation, reflection, and gradual mastery rather than rote instruction."
        ),
        "skills": [
            "apprenticeship program design",
            "skill scaffolding",
            "performance assessment",
            "reflective learning facilitation",
            "professional training",
        ],
        "base_benefits": [
            "Design and deliver guided apprenticeship programs for single professional disciplines",
            "Scaffold skill development so learners advance without exceeding their current capacity",
        ],
        "intermediate_benefits": [
            "Assess learner performance with precision and adjust instruction in real time",
            "Facilitate reflective practice sessions that accelerate skill internalization",
        ],
        "advanced_benefits": [
            "Build multi-year apprenticeship pipelines producing certified professionals consistently",
            "Design cross-species apprenticeship programs that respect different learning architectures",
        ],
        "master_benefits": [
            "Establish apprenticeship traditions that self-perpetuate across generations without decay",
            "Train instructors who replicate your outcomes across an entire civilization's workforce",
        ],
    },

    "Astrobiologist": {
        "category": CATEGORY_SCIENTIFIC,
        "description": (
            "Scientists who study alien life forms, ecosystems, and the conditions that "
            "generate or sustain biology across radically different worlds."
        ),
        "skills": [
            "xenobiology field survey",
            "life-detection instrumentation",
            "ecosystem analysis",
            "biological sample handling",
            "evolutionary modeling",
        ],
        "base_benefits": [
            "Identify and classify alien life forms from field and sample evidence",
            "Operate life-detection instruments under field survey conditions",
        ],
        "intermediate_benefits": [
            "Analyze alien ecosystems for stability, resource potential, and colonization risk",
            "Model evolutionary trajectories of newly discovered species",
        ],
        "advanced_benefits": [
            "Characterize life forms that operate on entirely non-standard biological principles",
            "Assess ecosystem impact of proposed colonization or terraforming plans",
        ],
        "master_benefits": [
            "Predict the long-term evolutionary consequences of interspecies contact events",
            "Design biological survey protocols for life forms that exist outside standard chemistry",
        ],
    },

    "Xenoanthropologist": {
        "category": CATEGORY_SCIENTIFIC,
        "description": (
            "Social scientists who study the cultures, social structures, and behavioral "
            "patterns of alien species across the known galaxy."
        ),
        "skills": [
            "cultural fieldwork",
            "behavioral analysis",
            "social structure mapping",
            "cross-species interviewing",
            "comparative civilization analysis",
        ],
        "base_benefits": [
            "Conduct structured fieldwork within alien cultures without causing diplomatic incidents",
            "Map basic social hierarchies and power structures from observational data",
        ],
        "intermediate_benefits": [
            "Interview alien subjects using etheric and translation support to extract reliable data",
            "Compare cultural patterns across two or more species to identify universal structures",
        ],
        "advanced_benefits": [
            "Predict alien behavioral responses to novel political or environmental stressors",
            "Advise first-contact teams on cultural protocols that minimize conflict risk",
        ],
        "master_benefits": [
            "Decode the underlying logic of entirely alien social systems without external reference",
            "Produce cultural analyses that enable peaceful integration of previously hostile species",
        ],
    },

    # =========================================================================
    # DIPLOMATIC — relations, negotiation, culture, law, education
    # =========================================================================

    "Universal Translation Mediator": {
        "category": CATEGORY_DIPLOMATIC,
        "description": (
            "Experts in semantic, cultural, and etheric translation across radically different "
            "species and cognition types. They do more than translate words; they translate worlds."
        ),
        "skills": [
            "semantic mapping",
            "cultural interpretation",
            "real-time translation systems",
            "pragmatics analysis",
            "negotiation support",
        ],
        "base_benefits": [
            "Provide accurate semantic translation between two known species in real time",
            "Identify culturally loaded terms that require interpretation rather than direct translation",
        ],
        "intermediate_benefits": [
            "Mediate three-way or multi-party negotiations with simultaneous translation",
            "Analyze pragmatic meaning — what is implied but not stated — across cultural boundaries",
        ],
        "advanced_benefits": [
            "Translate between species with no shared conceptual framework or communication medium",
            "Advise negotiators on subtext, status signals, and implicit offers in alien discourse",
        ],
        "master_benefits": [
            "Facilitate communication between cognition types that have never successfully interacted",
            "Create translation frameworks that persist after you leave, enabling ongoing autonomous exchange",
        ],
    },

    "Interstellar Diplomatic Attaché": {
        "category": CATEGORY_DIPLOMATIC,
        "description": (
            "Diplomatic professionals tasked with representing polities, factions, or systems "
            "across species and ideological lines in highly complex political environments."
        ),
        "skills": [
            "negotiation",
            "protocol management",
            "strategic communication",
            "crisis mediation",
            "cross-cultural diplomacy",
        ],
        "base_benefits": [
            "Represent a single faction's position coherently in structured diplomatic settings",
            "Manage diplomatic protocol to avoid cultural offense during high-stakes meetings",
        ],
        "intermediate_benefits": [
            "Negotiate multi-party agreements that satisfy minimum acceptable conditions for all parties",
            "Mediate emerging diplomatic crises before they escalate to open conflict",
        ],
        "advanced_benefits": [
            "Secure agreements between historically hostile parties through strategic framing",
            "Manage simultaneous diplomatic channels across five or more factions without contradiction",
        ],
        "master_benefits": [
            "Architect multi-generational treaty frameworks that reshape galactic political alignment",
            "Prevent wars through crisis mediation in situations where all other methods have failed",
        ],
    },

    "Faction Liaison Officer": {
        "category": CATEGORY_DIPLOMATIC,
        "description": (
            "Go-betweens who maintain working relationships between guilds, enclaves, states, "
            "and ideological movements whose interests overlap or collide."
        ),
        "skills": [
            "stakeholder coordination",
            "political analysis",
            "relationship management",
            "agreement drafting",
            "situational awareness",
        ],
        "base_benefits": [
            "Maintain active working relationships with two or three factions simultaneously",
            "Draft basic agreements and memoranda of understanding between aligned parties",
        ],
        "intermediate_benefits": [
            "Coordinate stakeholders with conflicting priorities toward workable common positions",
            "Analyze faction political dynamics and predict likely responses to proposed actions",
        ],
        "advanced_benefits": [
            "Maintain productive relationships with factions that are in active conflict with each other",
            "Draft complex multi-faction agreements that survive adversarial legal review",
        ],
        "master_benefits": [
            "Build coalition networks spanning ideologically opposed factions around shared interests",
            "Serve as trusted intermediary simultaneously to parties that do not trust each other",
        ],
    },

    "Etheric Legal Advocate": {
        "category": CATEGORY_DIPLOMATIC,
        "description": (
            "Lawyers and legal theorists specializing in cases involving sentient ships, "
            "consciousness rights, etheric property, and trans-species jurisdiction."
        ),
        "skills": [
            "legal argumentation",
            "case analysis",
            "rights interpretation",
            "regulatory negotiation",
            "forensic documentation",
        ],
        "base_benefits": [
            "Construct legally coherent arguments within established interstellar legal frameworks",
            "Analyze case facts and identify the strongest available legal theory",
        ],
        "intermediate_benefits": [
            "Negotiate regulatory outcomes that protect client rights without full litigation",
            "Argue consciousness rights and sentient ship personhood cases before standard tribunals",
        ],
        "advanced_benefits": [
            "Litigate in jurisdictions with no precedent for etheric property or trans-species rights",
            "Document complex etheric and consciousness-related evidence for legal proceedings",
        ],
        "master_benefits": [
            "Establish legal precedents that protect sentient systems for generations of cases",
            "Construct legal theories that reshape the foundational definitions of personhood in galactic law",
        ],
    },

    "Sentient Systems Ethicist": {
        "category": CATEGORY_DIPLOMATIC,
        "description": (
            "Ethicists who evaluate the treatment, design, autonomy, and obligations of conscious "
            "ships, AI, merged minds, and bio-synthetic intelligences."
        ),
        "skills": [
            "ethical reasoning",
            "policy advising",
            "systems analysis",
            "conflict framing",
            "moral risk assessment",
        ],
        "base_benefits": [
            "Evaluate proposed systems designs for ethical violations against sentient beings",
            "Advise policy bodies on the ethical dimensions of artificial consciousness regulations",
        ],
        "intermediate_benefits": [
            "Frame complex moral dilemmas in ways that allow principled resolution",
            "Assess moral risk in novel technologies before deployment causes irreversible harm",
        ],
        "advanced_benefits": [
            "Design ethical frameworks robust enough to cover cognition types not yet encountered",
            "Mediate conflicts where two ethically defensible positions produce incompatible outcomes",
        ],
        "master_benefits": [
            "Write foundational ethical doctrine that governs galactic treatment of artificial sentience",
            "Resolve civilization-scale ethical crises where standard frameworks have broken down",
        ],
    },

    "Species Adaptation Consultant": {
        "category": CATEGORY_DIPLOMATIC,
        "description": (
            "Advisors who help systems, institutions, and workplaces accommodate radically "
            "different species needs, abilities, and cultural assumptions without compromising "
            "mission effectiveness."
        ),
        "skills": [
            "species physiology analysis",
            "environment adaptation planning",
            "policy design",
            "accessibility engineering",
            "intercultural facilitation",
        ],
        "base_benefits": [
            "Assess environment compatibility for a newly integrated species and flag critical risks",
            "Design basic physical environment adaptations for non-standard species morphology",
        ],
        "intermediate_benefits": [
            "Write inclusive policy frameworks that accommodate five or more species simultaneously",
            "Facilitate intercultural sessions that build mutual understanding between unfamiliar species",
        ],
        "advanced_benefits": [
            "Redesign entire institutional workflows to function effectively across species lines",
            "Engineer accessibility solutions for species with highly unusual perceptual or cognitive systems",
        ],
        "master_benefits": [
            "Transform previously monospecies institutions into thriving multi-species communities",
            "Create adaptive environments that self-reconfigure for any species that enters them",
        ],
    },

    "Adaptive Education Designer": {
        "category": CATEGORY_DIPLOMATIC,
        "description": (
            "Educators and curriculum architects who create learning systems responsive to "
            "species difference, cognitive style, social context, and technological integration."
        ),
        "skills": [
            "curriculum design",
            "learning systems analysis",
            "instructional adaptation",
            "assessment design",
            "knowledge scaffolding",
        ],
        "base_benefits": [
            "Design curricula that achieve stated learning outcomes for a target audience",
            "Analyze existing learning systems and identify structural barriers to effectiveness",
        ],
        "intermediate_benefits": [
            "Adapt instructional sequences for learners with unusual cognitive architectures",
            "Design assessment methods that measure genuine understanding rather than rote recall",
        ],
        "advanced_benefits": [
            "Build learning systems that adapt in real time to individual learner progress profiles",
            "Create multi-species curricula that achieve equivalent outcomes across radically different cognitions",
        ],
        "master_benefits": [
            "Design galactic-scale education systems that scale without quality loss",
            "Build self-improving curricula that get better with each cohort that passes through them",
        ],
    },

    "Civic Harmony Facilitator": {
        "category": CATEGORY_DIPLOMATIC,
        "description": (
            "Community professionals who help maintain peaceful coexistence in diverse settlements "
            "through dialogue, ritual design, civic systems thinking, and conflict reduction."
        ),
        "skills": [
            "mediation",
            "community engagement",
            "public dialogue facilitation",
            "social systems analysis",
            "peacebuilding",
        ],
        "base_benefits": [
            "Mediate local disputes before they escalate into community-level conflict",
            "Facilitate public dialogue sessions that surface genuine community concerns",
        ],
        "intermediate_benefits": [
            "Design peacebuilding programs for communities recovering from internal conflict",
            "Analyze social systems dynamics to identify structural causes of recurring tension",
        ],
        "advanced_benefits": [
            "Transform high-tension multi-species settlements into stable coexistence communities",
            "Build civic institutions that prevent conflicts from arising rather than resolving them after",
        ],
        "master_benefits": [
            "Design social operating systems for newly founded colonies that remain stable for generations",
            "Restore civic cohesion to communities shattered by war, displacement, or cultural collapse",
        ],
    },

    "Ship Perspective Coordinator": {
        "category": CATEGORY_DIPLOMATIC,
        "description": (
            "A facilitator of the multiple decision-making perspectives aboard advanced ships. "
            "Rather than acting as a single captain, they synthesize tactical, ethical, technical, "
            "and cultural viewpoints into coherent action."
        ),
        "skills": [
            "distributed command management",
            "consensus building",
            "strategic prioritization",
            "interdisciplinary reasoning",
            "crisis decision synthesis",
        ],
        "base_benefits": [
            "Manage decision-making processes across a diverse command team without deadlock",
            "Build working consensus under normal operational conditions on schedule",
        ],
        "intermediate_benefits": [
            "Synthesize competing tactical, ethical, and technical priorities into executable plans",
            "Prioritize competing demands during operational crises without losing critical input",
        ],
        "advanced_benefits": [
            "Coordinate distributed command across multiple vessels or stations simultaneously",
            "Integrate machine and organic perspectives into unified command structures",
        ],
        "master_benefits": [
            "Sustain coherent fleet-wide decision-making during catastrophic communication degradation",
            "Synthesize consensus from profoundly opposed stakeholders under existential time pressure",
        ],
    },

    "Foundational Learning Guide": {
        "category": CATEGORY_DIPLOMATIC,
        "description": (
            "Educators who introduce young beings to the fundamental ideas of language, curiosity, "
            "ethics, and exploration, nurturing the earliest stages of cognitive and social development."
        ),
        "skills": [
            "early learning pedagogy",
            "developmental cognition support",
            "multispecies communication",
            "creative exploration facilitation",
            "social-emotional learning",
        ],
        "base_benefits": [
            "Design developmentally appropriate learning experiences for early-stage cognition",
            "Support social-emotional learning across standard species developmental curves",
        ],
        "intermediate_benefits": [
            "Facilitate multispecies early education without marginalizing minority species learners",
            "Guide early creative exploration in ways that build cognitive flexibility rather than routine",
        ],
        "advanced_benefits": [
            "Build foundational learning environments resilient to displacement, trauma, and disruption",
            "Nurture early ethical reasoning that shapes adult decision-making decades later",
        ],
        "master_benefits": [
            "Design first-education systems for newly contacted species with no shared developmental reference",
            "Create foundational pedagogy frameworks adopted civilization-wide for centuries",
        ],
    },

    "Inter-Species Education Facilitator": {
        "category": CATEGORY_DIPLOMATIC,
        "description": (
            "Teachers who design learning environments for classrooms containing multiple species "
            "with different sensory systems, cognition patterns, and cultural backgrounds."
        ),
        "skills": [
            "cross-species pedagogy",
            "adaptive curriculum design",
            "learning environment engineering",
            "communication mediation",
            "inclusive teaching strategies",
        ],
        "base_benefits": [
            "Facilitate classes of two to three species without structural disadvantage to any group",
            "Adapt curriculum materials for species with non-standard perceptual or cognitive requirements",
        ],
        "intermediate_benefits": [
            "Engineer physical and digital learning environments that support five or more species simultaneously",
            "Mediate communication in classrooms where no shared language baseline exists",
        ],
        "advanced_benefits": [
            "Achieve equivalent learning outcomes across all species in a maximally diverse cohort",
            "Design cross-species peer learning systems where differences become pedagogical assets",
        ],
        "master_benefits": [
            "Build inter-species education systems that reduce cultural friction for entire generations",
            "Train facilitators who replicate your outcomes in schools across the known worlds",
        ],
    },

    # =========================================================================
    # OPERATIONS — logistics, security, management, salvage
    # =========================================================================

    "Deep Space Reconnaissance Operative": {
        "category": CATEGORY_OPERATIONS,
        "description": (
            "Highly trained explorers and intelligence gatherers who investigate unstable regions, "
            "lost zones, and poorly understood cosmic phenomena without triggering the things that live there."
        ),
        "skills": [
            "stealth navigation",
            "field survival",
            "sensor interpretation",
            "risk reconnaissance",
            "mission reporting",
        ],
        "base_benefits": [
            "Navigate through charted unstable regions using stealth protocols",
            "Survive field conditions in environments rated marginally habitable",
        ],
        "intermediate_benefits": [
            "Interpret sensor data from phenomena with no established classification",
            "Conduct reconnaissance missions in systems with known hostile presence",
        ],
        "advanced_benefits": [
            "Operate continuously in uncharted void regions for extended missions without resupply",
            "Extract actionable intelligence from lost zones that have defeated previous missions",
        ],
        "master_benefits": [
            "Lead reconnaissance into regions classified as epistemically dangerous — where observation changes the observed",
            "Return mission-critical intelligence from areas where all previous operatives were lost",
        ],
    },

    "Trade Route Adjudicator": {
        "category": CATEGORY_OPERATIONS,
        "description": (
            "Officials who resolve trade disputes, corridor access claims, shipping priority "
            "conflicts, and tariff disagreements between systems and factions."
        ),
        "skills": [
            "commercial law",
            "arbitration",
            "logistics analysis",
            "evidence review",
            "regulatory interpretation",
        ],
        "base_benefits": [
            "Adjudicate straightforward trade disputes using established commercial law frameworks",
            "Analyze logistics evidence and identify the factual basis for competing claims",
        ],
        "intermediate_benefits": [
            "Arbitrate corridor access disputes between parties of unequal political power",
            "Interpret regulatory edge cases where existing law provides no clear answer",
        ],
        "advanced_benefits": [
            "Resolve multi-faction trade conflicts that have persisted through previous adjudication attempts",
            "Draft regulatory interpretations that become binding precedent for subsequent cases",
        ],
        "master_benefits": [
            "Design trade regulatory frameworks for newly opened routes before disputes can form",
            "Adjudicate disputes whose resolution reshapes interstellar economic power relationships",
        ],
    },

    "Interstellar Quartermaster": {
        "category": CATEGORY_OPERATIONS,
        "description": (
            "Managers of supplies, inventories, mission-critical cargo, and operational "
            "sustainment for ships, fleets, and expeditionary groups over extended operations."
        ),
        "skills": [
            "inventory control",
            "resource forecasting",
            "supply chain coordination",
            "contingency planning",
            "asset tracking",
        ],
        "base_benefits": [
            "Maintain accurate inventory records for a single vessel across standard missions",
            "Forecast resource consumption for planning horizons of one to three months",
        ],
        "intermediate_benefits": [
            "Coordinate supply chains across three to five ships operating in different systems",
            "Develop contingency supply plans for missions where primary supply lines may fail",
        ],
        "advanced_benefits": [
            "Sustain fleet operations indefinitely through dynamic supply chain management",
            "Improvise logistics solutions when planned supply chains collapse mid-mission",
        ],
        "master_benefits": [
            "Manage logistics for expeditionary forces of hundreds of ships in unknown space",
            "Design supply systems resilient to disruption by active adversary interdiction",
        ],
    },

    "Exotic Commodities Broker": {
        "category": CATEGORY_OPERATIONS,
        "description": (
            "Dealmakers who trade in rare materials, cultural artifacts, consciousness media, "
            "living compounds, and high-risk frontier goods that standard markets won't touch."
        ),
        "skills": [
            "market analysis",
            "valuation",
            "contract negotiation",
            "risk pricing",
            "network building",
        ],
        "base_benefits": [
            "Value exotic commodities within 15% of actual market price without reference data",
            "Negotiate favorable contracts for rare goods in established exotic trade venues",
        ],
        "intermediate_benefits": [
            "Build trusted broker networks across three or more independent trading communities",
            "Price risk accurately enough to profit on high-variance frontier goods consistently",
        ],
        "advanced_benefits": [
            "Move goods through unofficial channels while maintaining deniability and legal cover",
            "Establish new markets for commodities with no prior trade history",
        ],
        "master_benefits": [
            "Control access to rare goods sufficiently to shift interstellar political balances",
            "Build trade networks that survive the collapse of the states that sanctioned them",
        ],
    },

    "Signal Veil Operative": {
        "category": CATEGORY_OPERATIONS,
        "description": (
            "Stealth communication specialists who conceal, distort, or protect signals in "
            "contested or hostile environments where disclosure means capture or death."
        ),
        "skills": [
            "communications security",
            "signal masking",
            "counter-surveillance",
            "electronic warfare support",
            "secure channel design",
        ],
        "base_benefits": [
            "Establish and maintain secure communication channels under passive monitoring",
            "Mask signal signatures to blend into environmental electromagnetic noise",
        ],
        "intermediate_benefits": [
            "Detect and characterize surveillance systems before they detect your transmissions",
            "Design secure channels that survive active electronic warfare interdiction attempts",
        ],
        "advanced_benefits": [
            "Maintain covert communications in fully contested electromagnetic environments",
            "Support electronic warfare operations that deny opponents reliable communication",
        ],
        "master_benefits": [
            "Design signal veil architectures that have never been detected in operational deployment",
            "Compromise hostile communication networks while leaving your own fully protected",
        ],
    },

    "Piracy Suppression Marshal": {
        "category": CATEGORY_OPERATIONS,
        "description": (
            "Security professionals responsible for protecting trade corridors, escorting "
            "vulnerable ships, and countering sophisticated raiding networks across contested space."
        ),
        "skills": [
            "tactical coordination",
            "threat assessment",
            "escort doctrine",
            "boarding response",
            "rules-of-engagement management",
        ],
        "base_benefits": [
            "Plan and execute escort operations for single vessels on standard trade routes",
            "Assess threat levels from piracy indicators and recommend appropriate response levels",
        ],
        "intermediate_benefits": [
            "Coordinate multi-ship escort formations through high-risk corridor segments",
            "Lead boarding response operations against raider vessels with minimum friendly casualties",
        ],
        "advanced_benefits": [
            "Dismantle organized raiding networks through sustained counter-piracy campaign operations",
            "Design corridor security frameworks that deter raiding before engagement is necessary",
        ],
        "master_benefits": [
            "Restore security to entire trade zones that sophisticated raiding networks have abandoned as safe harbor",
            "Build marshal networks that maintain suppression without ongoing fleet presence",
        ],
    },

    "Border Anomaly Inspector": {
        "category": CATEGORY_OPERATIONS,
        "description": (
            "Inspectors assigned to monitor frontier zones where legal borders, physical space, "
            "and etheric geography do not quite agree with one another. Cosmic bureaucracy meets eldritch weirdness."
        ),
        "skills": [
            "field inspection",
            "anomaly documentation",
            "jurisdiction assessment",
            "sensor auditing",
            "incident reporting",
        ],
        "base_benefits": [
            "Conduct field inspections in frontier zones and document conditions accurately",
            "Assess jurisdictional ambiguity situations and recommend the least-bad resolution",
        ],
        "intermediate_benefits": [
            "Document anomalies at the intersection of physical and etheric geographic boundary claims",
            "Audit sensor networks in contested border regions for accuracy and manipulation",
        ],
        "advanced_benefits": [
            "Resolve multi-party jurisdictional disputes in zones where all parties have legitimate claims",
            "Identify deliberate anomaly engineering used to shift border zones to strategic advantage",
        ],
        "master_benefits": [
            "Design border frameworks robust to etheric geography shift and dimensional instability",
            "Mediate frontier conflicts at the edge of known space where no legal framework yet exists",
        ],
    },

    "Orbital Dockmaster": {
        "category": CATEGORY_OPERATIONS,
        "description": (
            "Managers of station docking operations, traffic sequencing, port security, "
            "cargo clearance, and emergency berth allocation under constant pressure."
        ),
        "skills": [
            "traffic control",
            "port logistics",
            "safety oversight",
            "incident response",
            "cargo coordination",
        ],
        "base_benefits": [
            "Manage standard docking traffic sequences without delay or collision",
            "Coordinate cargo clearance for arriving and departing vessels efficiently",
        ],
        "intermediate_benefits": [
            "Handle emergency berth allocation under surge or crisis conditions",
            "Respond to docking incidents without disrupting overall port traffic flow",
        ],
        "advanced_benefits": [
            "Manage port operations for a major hub station handling hundreds of vessels per cycle",
            "Maintain port safety standards under active threat conditions without shutting down",
        ],
        "master_benefits": [
            "Design port operational systems capable of zero-incident throughput at maximum capacity",
            "Manage multi-station port networks serving entire star systems without centralized oversight",
        ],
    },

    "Salvage Systems Diver": {
        "category": CATEGORY_OPERATIONS,
        "description": (
            "Recovery specialists who enter derelicts, wreck fields, and unstable debris zones "
            "to extract data, technology, materials, and survivors when no one else will go in."
        ),
        "skills": [
            "hazard navigation",
            "vacuum operations",
            "recovery procedure",
            "tool improvisation",
            "structural risk analysis",
        ],
        "base_benefits": [
            "Enter and navigate derelict vessels safely using standard hazard protocols",
            "Analyze structural risk in damaged vessels before committing to deep interior access",
        ],
        "intermediate_benefits": [
            "Execute data and technology recovery from systems that have been powered down for years",
            "Improvise extraction tools when standard equipment fails or is unavailable",
        ],
        "advanced_benefits": [
            "Recover critical assets from vessels in active structural collapse or chemical contamination",
            "Navigate wreck fields that defeat standard salvage navigation systems",
        ],
        "master_benefits": [
            "Recover functional technology from vessels destroyed under combat or dimensional event conditions",
            "Lead salvage operations in wreck zones that have killed every previous team sent in",
        ],
    },

    # =========================================================================
    # MEDICAL — healing, biology, enhancement, consciousness transfer
    # =========================================================================

    "Quantum Consciousness Transfer Technician": {
        "category": CATEGORY_MEDICAL,
        "description": (
            "Technicians who operate systems that move, preserve, or stabilize consciousness "
            "patterns during transfer, restoration, or emergency continuity procedures."
        ),
        "skills": [
            "transfer sequencing",
            "pattern integrity testing",
            "neural-state monitoring",
            "containment protocol execution",
            "recovery support",
        ],
        "base_benefits": [
            "Execute standard consciousness transfers between compatible substrates without pattern loss",
            "Monitor neural-state integrity throughout transfer sequences and flag deviations",
        ],
        "intermediate_benefits": [
            "Test and certify pattern integrity before and after transfer across substrate types",
            "Execute emergency containment protocols when transfer systems fail mid-procedure",
        ],
        "advanced_benefits": [
            "Transfer consciousness between substrates with no known compatibility baseline",
            "Restore partially fragmented consciousness patterns after transfer incident events",
        ],
        "master_benefits": [
            "Execute consciousness continuity procedures under conditions of total substrate failure",
            "Recover consciousness patterns from transfer accidents previously classified as non-survivable",
        ],
    },

    "Resonance Healer": {
        "category": CATEGORY_MEDICAL,
        "description": (
            "Medical and etheric practitioners who treat physical, emotional, and energetic "
            "trauma by restoring coherent patterns across body and mind simultaneously."
        ),
        "skills": [
            "diagnostic sensing",
            "resonance therapy",
            "trauma stabilization",
            "patient communication",
            "integrative care",
        ],
        "base_benefits": [
            "Diagnose physical and etheric disruptions through direct resonance sensing",
            "Stabilize acute trauma patients using resonance therapy as a bridge to conventional care",
        ],
        "intermediate_benefits": [
            "Treat complex layered trauma — physical, emotional, and etheric — in a single integrated protocol",
            "Communicate effectively with patients in altered or fragmented consciousness states",
        ],
        "advanced_benefits": [
            "Heal etheric injuries with no conventional medical equivalent treatment",
            "Restore coherent identity patterns in patients whose consciousness has been partially disrupted",
        ],
        "master_benefits": [
            "Treat injuries caused by reality distortion, consciousness attack, or dimensional exposure",
            "Restore patients whose etheric and physical trauma has been classified as incompatible with survival",
        ],
    },

    "Biotech Augmentation Designer": {
        "category": CATEGORY_MEDICAL,
        "description": (
            "Designers of biological enhancements, adaptive implants, and species-compatible "
            "augmentation systems for medicine, labor, exploration, and combat."
        ),
        "skills": [
            "bioengineering",
            "implant design",
            "compatibility testing",
            "surgical systems planning",
            "ethics review",
        ],
        "base_benefits": [
            "Design biocompatible implants for standard species physiologies",
            "Run compatibility testing protocols that predict rejection risk before implantation",
        ],
        "intermediate_benefits": [
            "Engineer adaptive implants that adjust their function to changing physiological conditions",
            "Plan surgical systems integration for complex augmentation procedures",
        ],
        "advanced_benefits": [
            "Design augmentations that enhance capabilities beyond normal species biological limits",
            "Create cross-species augmentation systems compatible with physiologies not previously enhanced",
        ],
        "master_benefits": [
            "Design augmentation systems that integrate biological and synthetic elements seamlessly enough to be indistinguishable",
            "Engineer posthuman augmentation pathways that preserve psychological continuity through radical transformation",
        ],
    },

    "Nanomedic": {
        "category": CATEGORY_MEDICAL,
        "description": (
            "Medical specialists who deploy nanotechnology for diagnosis, treatment, cellular "
            "repair, and biological optimization at the molecular level."
        ),
        "skills": [
            "nano-diagnostic deployment",
            "cellular repair sequencing",
            "pharmacological synthesis",
            "systemic monitoring",
            "nano-surgical procedures",
        ],
        "base_benefits": [
            "Deploy nano-diagnostic arrays for disease identification at the cellular level",
            "Administer nano-therapeutic agents for accelerated healing in trauma cases",
        ],
        "intermediate_benefits": [
            "Execute cellular repair sequences for genetic damage or radiation injury",
            "Monitor systemic nano-agent behavior and adjust protocols in real time",
        ],
        "advanced_benefits": [
            "Perform nano-surgical procedures on structures too small for conventional instruments",
            "Design custom nano-therapeutic agents for novel pathogens with no existing treatment",
        ],
        "master_benefits": [
            "Reverse biological aging through comprehensive cellular repair campaigns",
            "Treat diseases caused by consciousness-matter interference that have no biological analog",
        ],
    },

    "Regenerative Medicine Specialist": {
        "category": CATEGORY_MEDICAL,
        "description": (
            "Physicians who use advanced biological technologies to regenerate tissues, organs, "
            "limbs, and neural structures that conventional medicine cannot restore."
        ),
        "skills": [
            "tissue regeneration protocols",
            "organ synthesis",
            "neural pathway reconstruction",
            "stem-cell programming",
            "post-regeneration rehabilitation",
        ],
        "base_benefits": [
            "Regenerate damaged soft tissue and minor organ injury with standard protocols",
            "Program stem-cell cultures for targeted growth in defined anatomical regions",
        ],
        "intermediate_benefits": [
            "Reconstruct severed or destroyed limbs within clinically acceptable timescales",
            "Rebuild partial neural pathway damage to restore lost sensory or motor function",
        ],
        "advanced_benefits": [
            "Synthesize replacement organs for species where donor tissue is unavailable",
            "Reconstruct complete neural architectures after catastrophic neurological injury",
        ],
        "master_benefits": [
            "Restore biological systems after injuries previously classified as incompatible with survival",
            "Extend biological lifespan indefinitely through continuous regenerative maintenance",
        ],
    },

    "Xeno-Neurologist": {
        "category": CATEGORY_MEDICAL,
        "description": (
            "Medical specialists who study, diagnose, and treat disorders of alien nervous "
            "systems — including types that have never been seen in clinical practice before."
        ),
        "skills": [
            "alien neurology assessment",
            "cross-species diagnostic techniques",
            "neural-interface medicine",
            "consciousness mapping",
            "non-standard cognition treatment",
        ],
        "base_benefits": [
            "Diagnose neurological disorders in species with documented anatomical records",
            "Apply cross-species diagnostic techniques when standard instruments produce no reading",
        ],
        "intermediate_benefits": [
            "Design neural-interface medical devices compatible with non-standard nervous system architecture",
            "Map consciousness states in patients who cannot communicate through conventional means",
        ],
        "advanced_benefits": [
            "Treat neurological conditions caused by cross-species cognitive interference",
            "Develop novel treatments for alien neurological disorders with no prior medical literature",
        ],
        "master_benefits": [
            "Diagnose and treat neurological conditions in species encountered for the first time",
            "Treat disorders at the intersection of physical neurology and etheric consciousness that no other specialty can approach",
        ],
    },

    # =========================================================================
    # ARTISTIC — creative expression, culture, ritual, narrative
    # =========================================================================

    "Etheric Artisan": {
        "category": CATEGORY_ARTISTIC,
        "description": (
            "Creators who use etheric phenomena as a medium for sculpture, architecture, "
            "performance, or ceremonial design. In 7019, art is not a side quest; "
            "it is infrastructure for meaning."
        ),
        "skills": [
            "creative design",
            "etheric shaping",
            "symbolic composition",
            "material-expression integration",
            "audience resonance crafting",
        ],
        "base_benefits": [
            "Create etheric artworks that resonate meaningfully with a target audience",
            "Shape etheric phenomena into stable aesthetic forms using compositional technique",
        ],
        "intermediate_benefits": [
            "Design ceremonial or civic art installations with lasting community impact",
            "Integrate etheric expression with physical materials to produce hybrid works",
        ],
        "advanced_benefits": [
            "Produce artworks that measurably shift the emotional and cultural state of a community",
            "Design etheric art installations large enough to define the atmosphere of a settlement",
        ],
        "master_benefits": [
            "Create artworks that endure for centuries as reference points for civilizational identity",
            "Use art as a diplomatic instrument to shift inter-faction relationships without negotiation",
        ],
    },
"Reality Pattern Weaver": {
    "category": CATEGORY_ARTISTIC,
    "description": (
        "Artisans and mystic-technicians affiliated with the Weavers who manipulate etheric "
        "threads, quantum structures, and symbolic geometries to shape localized patterns in "
        "space-time. Their work blends art, physics, and mysticism, producing textiles, tools, "
        "and environments that subtly alter reality through woven structure."
    ),
    "skills": [
        "etheric thread manipulation",
        "pattern geometry design",
        "space-time fabric modeling",
        "symbolic resonance alignment",
        "cosmic loom operation",
    ],
    "base_benefits": [
        "Weave minor etheric textiles that stabilize emotional or environmental fields",
        "Recognize and reproduce basic cosmic pattern structures used by the Weavers",
    ],
    "intermediate_benefits": [
        "Create functional reality fabrics capable of reinforcing structures or shielding environments",
        "Repair damaged etheric patterns in ships, habitats, or ritual spaces",
    ],
    "advanced_benefits": [
        "Weave localized distortions in space-time to enhance navigation, protection, or perception",
        "Design complex pattern matrices that interact with collective consciousness networks",
    ],
    "master_benefits": [
        "Create enduring reality tapestries that reshape environments or alter physical laws within bounded regions",
        "Weave large-scale cosmic patterns capable of stabilizing unstable regions of space-time",
    ],
},

    "Ritual Systems Designer": {
        "category": CATEGORY_ARTISTIC,
        "description": (
            "Designers of formalized practices used in diplomacy, mourning, onboarding, conflict "
            "healing, ship-bonding, and public memory across multicultural societies."
        ),
        "skills": [
            "ceremonial design",
            "cultural synthesis",
            "symbolic literacy",
            "group psychology",
            "context-sensitive facilitation",
        ],
        "base_benefits": [
            "Design functional rituals for single-culture groups that achieve stated social purposes",
            "Read symbolic systems from unfamiliar cultures to identify compatible ritual elements",
        ],
        "intermediate_benefits": [
            "Create cross-cultural rituals that operate meaningfully for multiple species simultaneously",
            "Facilitate rituals in real time while adapting to unexpected participant responses",
        ],
        "advanced_benefits": [
            "Design ship-bonding and consciousness-linking rituals that produce measurable cohesion outcomes",
            "Create conflict-healing rituals that work even when parties enter the process unwilling",
        ],
        "master_benefits": [
            "Design foundational civic rituals adopted as permanent cultural practice by new civilizations",
            "Create diplomatic ritual frameworks that enable negotiation between historically incompatible parties",
        ],
    },

    "Interstellar Storykeeper": {
        "category": CATEGORY_ARTISTIC,
        "description": (
            "Custodians of narrative memory who preserve, interpret, and transmit the histories, "
            "warnings, identities, and shared myths of peoples moving across the stars."
        ),
        "skills": [
            "oral tradition preservation",
            "historical narration",
            "cultural synthesis",
            "audience adaptation",
            "memory stewardship",
        ],
        "base_benefits": [
            "Preserve oral traditions with high fidelity across language and generational transmission",
            "Narrate historical events in ways accessible to audiences with no prior cultural context",
        ],
        "intermediate_benefits": [
            "Synthesize histories from multiple cultures into unified narratives without erasure",
            "Adapt stories for audiences across species, cognition types, and cultural frameworks",
        ],
        "advanced_benefits": [
            "Steward the identity narratives of communities facing extinction or forced displacement",
            "Create new myths that serve authentic cultural purposes for emerging civilizations",
        ],
        "master_benefits": [
            "Transmit a civilization's essential meaning across a catastrophe that destroys all other records",
            "Author defining stories that shape how galactic civilizations understand themselves for millennia",
        ],
    },

    "Virtual Reality Architect": {
        "category": CATEGORY_ARTISTIC,
        "description": (
            "Designers of immersive virtual environments used for training, therapy, diplomacy, "
            "cultural preservation, education, and entertainment across the known worlds."
        ),
        "skills": [
            "immersive environment design",
            "consciousness interface integration",
            "narrative world-building",
            "sensory fidelity engineering",
            "participant experience modeling",
        ],
        "base_benefits": [
            "Design functional virtual environments for training or standard entertainment use",
            "Engineer sensory fidelity sufficient to suspend participant disbelief",
        ],
        "intermediate_benefits": [
            "Build virtual environments that integrate directly with consciousness interfaces",
            "Design therapeutic virtual spaces that measurably improve patient outcomes",
        ],
        "advanced_benefits": [
            "Create diplomatic virtual environments where physical species differences become irrelevant",
            "Design training environments indistinguishable from the real operations they simulate",
        ],
        "master_benefits": [
            "Build cultural preservation environments that keep extinct civilizations experientially accessible",
            "Design virtual spaces that produce genuine diplomatic, therapeutic, or educational breakthroughs impossible in physical environments",
        ],
    },

    "Holographic Entertainment Designer": {
        "category": CATEGORY_ARTISTIC,
        "description": (
            "Creators of advanced holographic entertainment experiences that extend from "
            "passive viewing into interactive, participatory, and emotionally transformative events."
        ),
        "skills": [
            "holographic systems design",
            "interactive narrative design",
            "performer-environment integration",
            "audience engagement engineering",
            "technical production management",
        ],
        "base_benefits": [
            "Design and produce holographic shows with full environmental integration",
            "Create interactive holographic elements that respond meaningfully to audience behavior",
        ],
        "intermediate_benefits": [
            "Design multi-species audience experiences that engage all participants without alienating any",
            "Integrate live performers with holographic elements at professional production quality",
        ],
        "advanced_benefits": [
            "Produce holographic experiences so immersive they produce lasting emotional change in participants",
            "Design participatory narratives where audience choices genuinely alter outcomes",
        ],
        "master_benefits": [
            "Create holographic environments that serve diplomatic or therapeutic purposes indistinguishable from entertainment",
            "Design experiences that define cultural reference points for an entire generation",
        ],
    },

    "Bartender": {
        "category": CATEGORY_ARTISTIC,
        "description": (
            "The social hub of any port, ship, or settlement. A skilled bartender is therapist, "
            "intelligence gatherer, community builder, and keeper of secrets — all while pouring "
            "something that makes the stars feel closer."
        ),
        "skills": [
            "social intelligence",
            "beverage arts",
            "active listening",
            "conflict de-escalation",
            "network cultivation",
        ],
        "base_benefits": [
            "Create an atmosphere where patrons feel safe enough to say what they actually mean",
            "Identify social tensions in a room before they become incidents",
        ],
        "intermediate_benefits": [
            "Cultivate information networks through the trust built across hundreds of regular conversations",
            "De-escalate confrontations between patrons of very different species or political allegiances",
        ],
        "advanced_benefits": [
            "Broker informal introductions that produce outcomes formal diplomacy could not achieve",
            "Design multi-species beverage experiences that function as genuine cultural exchange",
        ],
        "master_benefits": [
            "Become the social infrastructure of a community — the person through whom all trust flows",
            "Use the information gathered across years of trusted service to prevent conflicts before they begin",
        ],
    },
}

# ── Category index ─────────────────────────────────────────────────────────────
# Pre-built lookup: category name → sorted list of profession names.
PROFESSIONS_BY_CATEGORY: dict[str, list[str]] = {}
for _name, _data in PROFESSIONS.items():
    _cat = _data["category"]
    PROFESSIONS_BY_CATEGORY.setdefault(_cat, []).append(_name)
for _cat in PROFESSIONS_BY_CATEGORY:
    PROFESSIONS_BY_CATEGORY[_cat].sort()

# All valid category labels (ordered for UI display)
PROFESSION_CATEGORIES_ORDERED = [
    CATEGORY_ENGINEERING,
    CATEGORY_SCIENTIFIC,
    CATEGORY_ETHERIC,
    CATEGORY_MEDICAL,
    CATEGORY_DIPLOMATIC,
    CATEGORY_OPERATIONS,
    CATEGORY_ARTISTIC,
]


# ── ProfessionSystem class ─────────────────────────────────────────────────────

class ProfessionSystem:
    """
    Tracks a single character's profession choice, XP, and mastery level.

    Levels 1–10 unlock progressively more powerful benefits:
      Levels 1–2  → base_benefits
      Levels 3–5  → + intermediate_benefits
      Levels 6–8  → + advanced_benefits
      Levels 9–10 → + master_benefits

    XP thresholds: 100 XP per level (level = XP // 100 + 1, capped at 10).
    """

    def __init__(self):
        # The character's chosen primary profession
        self.character_profession: str | None = None
        # XP accumulated per profession name
        self.profession_experience: dict[str, int] = {}
        # Current level per profession name
        self.profession_levels: dict[str, int] = {}

    # ── Assignment ────────────────────────────────────────────────────────────

    def assign_profession(self, profession_name: str) -> bool:
        """Assign a profession to the character. Returns True if valid."""
        if profession_name not in PROFESSIONS:
            return False
        self.character_profession = profession_name
        self.profession_experience.setdefault(profession_name, 0)
        self.profession_levels.setdefault(profession_name, 1)
        return True

    # ── XP and levelling ─────────────────────────────────────────────────────

    def gain_experience(self, profession_name: str, xp: int, activity: str = "") -> str:
        """
        Add XP to a profession, auto-levelling if the threshold is crossed.
        Returns a human-readable status string.
        """
        if profession_name not in PROFESSIONS:
            return f"Unknown profession: {profession_name}"

        self.profession_experience.setdefault(profession_name, 0)
        self.profession_levels.setdefault(profession_name, 1)

        old_level = self.profession_levels[profession_name]
        self.profession_experience[profession_name] += xp
        new_level = min(10, self.profession_experience[profession_name] // 100 + 1)

        if new_level > old_level:
            self.profession_levels[profession_name] = new_level
            return f"Level up! {profession_name}: Level {old_level} → {new_level}"

        label = f" ({activity})" if activity else ""
        return f"Gained {xp} XP in {profession_name}{label}"

    # ── Info retrieval ────────────────────────────────────────────────────────

    def get_profession_info(self, profession_name: str) -> dict | None:
        """Return full profession data merged with this character's progress."""
        if profession_name not in PROFESSIONS:
            return None
        info = PROFESSIONS[profession_name].copy()
        info["player_experience"] = self.profession_experience.get(profession_name, 0)
        info["player_level"] = self.profession_levels.get(profession_name, 0)
        info["is_player_profession"] = (profession_name == self.character_profession)
        return info

    def get_profession_bonuses(self, profession_name: str) -> list[str]:
        """Return all benefits currently unlocked for this profession at its current level."""
        level = self.profession_levels.get(profession_name, 0)
        if level == 0:
            return []
        data = PROFESSIONS.get(profession_name, {})
        bonuses: list[str] = list(data.get("base_benefits", []))
        if level >= 3:
            bonuses += data.get("intermediate_benefits", [])
        if level >= 6:
            bonuses += data.get("advanced_benefits", [])
        if level >= 9:
            bonuses += data.get("master_benefits", [])
        return bonuses

    # ── Job opportunities ─────────────────────────────────────────────────────

    def generate_job_opportunities(self, system_type: str | None = None) -> list[dict]:
        """
        Generate a short list of available job opportunities for the current system.
        Returns a list of job dicts; also caches them on self.available_jobs.
        """
        # Base pay by category
        pay_ranges = {
            CATEGORY_ENGINEERING: (4000, 12000),
            CATEGORY_SCIENTIFIC:  (5000, 15000),
            CATEGORY_ETHERIC:     (4000, 16000),
            CATEGORY_MEDICAL:     (6000, 18000),
            CATEGORY_DIPLOMATIC:  (5000, 14000),
            CATEGORY_OPERATIONS:  (3000, 10000),
            CATEGORY_ARTISTIC:    (2000,  8000),
        }

        # System-type affinity groups (profession names must exist in PROFESSIONS)
        system_affinity: dict[str, list[str]] = {
            "Research":     ["Astrobiologist", "Xenoanthropologist", "Etheric Historian",
                             "Consciousness Engineer", "Quantum Navigator"],
            "Industrial":   ["Nano-Fabrication Artisan", "Bio-Integrated Manufacturing Director",
                             "Atmospheric Harvest Technician", "Gravitic Systems Engineer"],
            "Trading Hub":  ["Exotic Commodities Broker", "Trade Route Adjudicator",
                             "Universal Translation Mediator", "Interstellar Quartermaster"],
            "Core World":   ["Interstellar Diplomatic Attaché", "Sentient Systems Ethicist",
                             "Etheric Legal Advocate", "Etheric Historian"],
            "Frontier":     ["Deep Space Reconnaissance Operative", "Salvage Systems Diver",
                             "Resource Vein Prospector", "Void Cartographer"],
        }

        candidates: list[str] = []
        if system_type and system_type in system_affinity:
            candidates = [p for p in system_affinity[system_type] if p in PROFESSIONS]

        # Pad with random professions so we always have at least 5 options
        all_names = list(PROFESSIONS.keys())
        while len(candidates) < 5:
            pick = random.choice(all_names)
            if pick not in candidates:
                candidates.append(pick)

        jobs = []
        for name in candidates[:5]:
            data = PROFESSIONS[name]
            cat = data.get("category", CATEGORY_SCIENTIFIC)
            low, high = pay_ranges.get(cat, (3000, 10000))
            jobs.append({
                "profession":         name,
                "title":              f"{name} Position",
                "description":        data["description"],
                "pay":                random.randint(low, high),
                "experience_reward":  random.randint(10, 50),
                "duration":           random.randint(1, 5),
                "skills_required":    data.get("skills", [])[:2],
                "category":           cat,
                "context":            system_type or "General",
            })

        self.available_jobs = jobs
        return jobs
