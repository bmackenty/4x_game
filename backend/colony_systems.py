"""
colony_systems.py — Social, Economic, and Political system definitions.

Each colony has three orthogonal system types.  These systems act as
multiplier layers on production, research, diplomacy, and trade.  They
are pure data + logic; no game-engine imports live here.

System IDs are stable string keys used throughout save data — never rename
an existing ID without a migration.

Structure of each system entry:
    name            — Display name
    description     — One-sentence lore/gameplay summary
    modifiers       — Dict of resource/stat keys → fractional multiplier deltas
                      e.g. {"minerals": 0.15} means +15 % to mineral output.
                      Keys: minerals, credits, research, food, fleet_points,
                            pop_growth, trade_volume, stability, all_production,
                            faction_rep_gain, all_diplomacy
    unique_commodity — Tradeable good produced each turn by this economy type
                      (economic systems only; 1–3 units/turn)
    commodity_amount — Units produced per turn (int, economic systems only)
    research_required — Research node name that must be completed before this
                        system is available.  None = always available (tier-1).
    faction_affinities — List of faction names that prefer / are aligned with
                         this system type (used when no faction_systems.json
                         entry exists for a given faction).
"""

# ---------------------------------------------------------------------------
# ECONOMIC SYSTEMS
# ---------------------------------------------------------------------------

ECONOMIC_SYSTEMS = {
    "energy_state": {
        "name":               "Energy-State Economy",
        "description":        "Value is tied to measurable energy production and storage; "
                              "favors industrial output and raw-material throughput.",
        "modifiers": {
            "minerals":       0.15,   # +15 % minerals
            "credits":        0.10,   # +10 % credits
            "research":      -0.05,   # -5  % research (reductionist worldview)
        },
        "unique_commodity":   "Energy Credits",
        "commodity_amount":   2,
        "research_required":  None,
        "faction_affinities": [
            "The Gearwrights Guild",
            "Stellar Nexus Guild",
            "The Ironclad Collective",
        ],
    },

    "consciousness_labor": {
        "name":               "Consciousness-Labor Economy",
        "description":        "Cognitive processing cycles are the primary unit of value; "
                              "minds contribute to distributed tasks at scale.",
        "modifiers": {
            "research":       0.20,   # +20 % research
            "fleet_points":   0.10,   # +10 % fleet points (optimised logistics)
        },
        "unique_commodity":   "Cognitive Cycles",
        "commodity_amount":   2,
        "research_required":  "Collective Metaconsciousness Networks",
        "faction_affinities": [
            "The Icaron Collective",
            "The Harmonic Resonance Collective",
        ],
    },

    "memory_economy": {
        "name":               "Memory Economy",
        "description":        "Experience and narrative are stored, traded, and embedded "
                              "as economic capital; cultural richness drives growth.",
        "modifiers": {
            "research":       0.25,   # +25 % research
            "pop_growth":     0.10,   # +10 % population growth
        },
        "unique_commodity":   "Archived Experience",
        "commodity_amount":   2,
        "research_required":  "Bio-Digital Symbiosis",
        "faction_affinities": [
            "The Veritas Covenant",
            "Keepers of the Spire",
            "The Scholara Nexus",
        ],
    },

    "time_economy": {
        "name":               "Time Economy",
        "description":        "Lifespan, attention, and temporal positioning are traded "
                              "directly, giving precise control over productivity.",
        "modifiers": {
            "all_production": 0.08,   # +8 % across all production categories
        },
        "unique_commodity":   "Temporal Slices",
        "commodity_amount":   1,
        "research_required":  "Quantum Temporal Dynamics",
        "faction_affinities": [
            "The Navigators",
            "The Quantum Artificers Guild",
        ],
    },

    "probability_economy": {
        "name":               "Probability Economy",
        "description":        "Futures markets trade likelihood of outcomes; strong "
                              "predictive optimization but reflexivity risk.",
        "modifiers": {
            "credits":        0.20,   # +20 % credit generation
            # trade_price_variance handled separately in market endpoint
        },
        "unique_commodity":   "Probability Futures",
        "commodity_amount":   1,
        "research_required":  "Causal Integrity Theory",
        "faction_affinities": [
            "The Map Makers",
            "Stellar Nexus Guild",
            "The Stellar Cartographers Alliance",
        ],
    },

    "ritualized_exchange": {
        "name":               "Ritualized Exchange",
        "description":        "Exchange is embedded in ceremony and cultural meaning, "
                              "building deep trust and social cohesion.",
        "modifiers": {
            "pop_growth":         0.15,   # +15 % population growth
            "faction_rep_gain":   0.10,   # +10 % rep gains from diplomatic actions
        },
        "unique_commodity":   "Ritual Tokens",
        "commodity_amount":   3,
        "research_required":  None,
        "faction_affinities": [
            "The Gaian Enclave",
            "The Harmonic Synaxis",
            "The Triune Daughters",
            "The Weavers",
        ],
    },
}

# ---------------------------------------------------------------------------
# POLITICAL SYSTEMS
# ---------------------------------------------------------------------------

POLITICAL_SYSTEMS = {
    "consensus_field": {
        "name":               "Consensus Field Governance",
        "description":        "Aggregated emotional and cognitive states form a shared "
                              "decision field; deep alignment, but slow to act.",
        "modifiers": {
            "faction_rep_gain": 0.10,  # +10 % rep from diplomatic actions
            "stability":        15,    # flat +15 stability points
            "all_production":  -0.05,  # -5 % production (slower decisions)
        },
        "research_required":  None,
        "faction_affinities": [
            "The Harmonic Resonance Collective",
            "The Harmonic Synaxis",
            "The Collective of Commonality",
        ],
    },

    "algorithmic_legitimacy": {
        "name":               "Algorithmic Legitimacy",
        "description":        "Authority derived from performance metrics; efficient "
                              "and adaptive but dependent on metric trust.",
        "modifiers": {
            "all_production": 0.15,   # +15 % production efficiency
            "research":       0.10,   # +10 % research
            "pop_growth":    -0.05,   # -5 % pop growth (optimisation over expansion)
        },
        "research_required":  "Predictive Logic Crystals",
        "faction_affinities": [
            "The Icaron Collective",
            "The Technotheos",
            "Technomancers",
        ],
    },

    "oracle_mediated": {
        "name":               "Oracle-Mediated Governance",
        "description":        "Decisions interpreted through predictive or etheric "
                              "systems; high strategic foresight, opaque process.",
        "modifiers": {
            "research":       0.20,   # +20 % research
            "all_production": 0.05,   # +5 % production
        },
        "research_required":  "Primordial Ether Research",
        "faction_affinities": [
            "Etheric Preservationists",
            "The Voidbound Monks",
            "Keepers of the Spire",
            "The Weavers",
        ],
    },

    "temporal_layer": {
        "name":               "Temporal Layer Governance",
        "description":        "Different time-phase populations govern different domains "
                              "in parallel; powerful but prone to coordination gaps.",
        "modifiers": {
            "research":       0.15,   # +15 % research
            "all_production": 0.10,   # +10 % production
            "stability":     -10,     # flat -10 stability (coordination cost)
        },
        "research_required":  "Quantum Temporal Dynamics",
        "faction_affinities": [
            "The Quantum Artificers Guild",
            "The Navigators",
        ],
    },

    "distributed_sovereignty": {
        "name":               "Distributed Micro-Sovereignty",
        "description":        "Authority distributed to individuals and nodes; maximum "
                              "autonomy but fragmentation risk.",
        "modifiers": {
            "trade_volume":       0.20,  # +20 % trade volume
            "all_production":     0.05,  # +5 % production
            "faction_rep_gain":  -0.05,  # -5 % rep gains (no unified voice)
        },
        "research_required":  None,
        "faction_affinities": [
            "Stellar Nexus Guild",
            "The Galactic Salvage Guild",
            "The Provocateurs' Guild",
        ],
    },

    "consciousness_swarm": {
        "name":               "Consciousness Swarm Deliberation",
        "description":        "Minds temporarily merge for decision-making; "
                              "highest-quality decisions at psychological cost.",
        "modifiers": {
            "research":       0.30,   # +30 % research
            "all_production": 0.15,   # +15 % production
            "pop_growth":    -0.10,   # -10 % pop growth (cognitive overhead)
        },
        "research_required":  "Collective Metaconsciousness Networks",
        "faction_affinities": [
            "The Harmonic Resonance Collective",
            "The Icaron Collective",
        ],
    },
}

# ---------------------------------------------------------------------------
# SOCIAL SYSTEMS
# ---------------------------------------------------------------------------

SOCIAL_SYSTEMS = {
    "resonance_cohesion": {
        "name":               "Resonance-Based Cohesion",
        "description":        "Groups form around shared emotional or etheric frequency; "
                              "rapid coordination within groups.",
        "modifiers": {
            "fleet_points":  0.10,   # +10 % fleet (disciplined cohesive units)
            "stability":     10,     # flat +10 stability
            "pop_growth":    0.05,   # +5 % population growth
        },
        "research_required":  None,
        "faction_affinities": [
            "The Harmonic Resonance Collective",
            "The Harmonic Synaxis",
            "The Gaian Enclave",
        ],
    },

    "memory_pooled": {
        "name":               "Memory-Pooled Identity",
        "description":        "Shared memory archives maintain continuity and accelerate "
                              "knowledge transfer across the population.",
        "modifiers": {
            "research":      0.20,   # +20 % research
            "stability":     20,     # flat +20 stability
            "pop_growth":    0.05,   # +5 % population growth
        },
        "research_required":  "Bio-Digital Symbiosis",
        "faction_affinities": [
            "The Veritas Covenant",
            "Keepers of the Spire",
            "The Scholara Nexus",
        ],
    },

    "distributed_selfhood": {
        "name":               "Distributed Selfhood",
        "description":        "Consciousness spreads across multiple nodes; resilient "
                              "and parallel but identity fragmentation is a risk.",
        "modifiers": {
            "trade_volume":   0.15,  # +15 % trade (multi-node market presence)
            "all_production": 0.10,  # +10 % production
            "stability":     -5,     # flat -5 stability (identity cost)
        },
        "research_required":  "Collective Metaconsciousness Networks",
        "faction_affinities": [
            "The Icaron Collective",
            "The Stellar Cartographers Alliance",
        ],
    },

    "narrative_bound": {
        "name":               "Narrative-Bound Societies",
        "description":        "A shared story defines roles and meaning; strong purpose "
                              "and cohesion, fragile if the narrative fails.",
        "modifiers": {
            "faction_rep_gain": 0.15,  # +15 % rep gains (unified cultural voice)
            "pop_growth":       0.10,  # +10 % population growth
            "stability":        15,    # flat +15 stability
        },
        "research_required":  None,
        "faction_affinities": [
            "The Gaian Enclave",
            "The Triune Daughters",
            "The Weavers",
            "The Galactic Circus",
        ],
    },

    "rotating_embodiment": {
        "name":               "Rotating Embodiment Systems",
        "description":        "Consciousness moves between bodies, cultivating cross-"
                              "species empathy at the cost of identity stability.",
        "modifiers": {
            "all_diplomacy":  0.05,  # +5 % all diplomacy modifiers
            "all_production": 0.05,  # +5 % production
            "stability":     -10,    # flat -10 stability
        },
        "research_required":  "Trans-Phasic Genetics",
        "faction_affinities": [
            "Harmonic Vitality Consortium",
            "The Galactic Circus",
        ],
    },

    "symbiotic_networks": {
        "name":               "Symbiotic Social Networks",
        "description":        "Individuals exist in bonded pairs or groups; high "
                              "stability and efficiency through mutual dependency.",
        "modifiers": {
            "pop_growth":     0.20,  # +20 % population growth
            "food":           0.10,  # +10 % food production
            "all_production": 0.05,  # +5 % production
        },
        "research_required":  None,
        "faction_affinities": [
            "The Brewmasters' Guild",
            "Harmonic Vitality Consortium",
            "The Gaian Enclave",
        ],
    },
}

# ---------------------------------------------------------------------------
# COHERENCE COMPATIBILITY
# ---------------------------------------------------------------------------
# Each tuple is (system_id_a, system_id_b, score).  Score is +2 for synergy,
# -2 for friction.  Pairs are order-independent (a,b == b,a).
# Total coherence score maps to a production multiplier (see calculate_coherence).

COMPATIBILITY_PAIRS = [
    # --- Synergies (+2 each) ---
    ("memory_pooled",           "memory_economy",           +2),
    ("memory_economy",          "consensus_field",          +2),
    ("resonance_cohesion",      "consensus_field",          +2),
    ("distributed_selfhood",    "distributed_sovereignty",  +2),
    ("narrative_bound",         "ritualized_exchange",      +2),
    ("consciousness_swarm",     "consciousness_labor",      +2),
    ("memory_pooled",           "oracle_mediated",          +2),
    ("symbiotic_networks",      "ritualized_exchange",      +2),

    # --- Frictions (-2 each) ---
    ("distributed_selfhood",    "energy_state",             -2),
    ("symbiotic_networks",      "algorithmic_legitimacy",   -2),
    ("rotating_embodiment",     "consensus_field",          -2),
    ("narrative_bound",         "distributed_sovereignty",  -2),
]

# Coherence score → (label, production multiplier)
COHERENCE_LEVELS = [
    (+4,  "High Coherence", 1.15),
    (+1,  "Aligned",        1.05),
    (-1,  "Stable",         1.00),
    (-3,  "Friction",       0.90),
    (-99, "High Friction",  0.80),
]

# ---------------------------------------------------------------------------
# PUBLIC API
# ---------------------------------------------------------------------------

def _all_systems():
    """Return combined lookup dict across all three categories."""
    combined = {}
    combined.update(ECONOMIC_SYSTEMS)
    combined.update(POLITICAL_SYSTEMS)
    combined.update(SOCIAL_SYSTEMS)
    return combined


def get_system_def(system_id: str) -> dict:
    """Return the definition dict for any system ID, or {} if unknown."""
    return _all_systems().get(system_id, {})


def get_production_modifiers(social: str, economic: str, political: str) -> dict:
    """
    Combine all three systems' modifiers into a single {resource: multiplier}
    dict.  Deltas are additive before being returned as the total multiplier
    (so 1.0 = no change, 1.15 = +15 %).

    Resources returned: minerals, credits, research, food, fleet_points,
    pop_growth, trade_volume, stability, all_production,
    faction_rep_gain, all_diplomacy.
    """
    # Start with identity multipliers (1.0) for every tracked resource.
    resources = [
        "minerals", "credits", "research", "food", "fleet_points",
        "pop_growth", "trade_volume", "all_production",
        "faction_rep_gain", "all_diplomacy",
    ]
    result = {r: 1.0 for r in resources}
    # stability is an additive flat integer, not a multiplier
    result["stability"] = 0

    for system_id in (social, economic, political):
        defn = get_system_def(system_id)
        for key, delta in defn.get("modifiers", {}).items():
            if key == "stability":
                result["stability"] = result.get("stability", 0) + delta
            else:
                result[key] = result.get(key, 1.0) + delta

    return result


def calculate_coherence(social: str, economic: str, political: str) -> tuple:
    """
    Compute the coherence score and return (score: int, label: str, multiplier: float).

    The multiplier is applied to all non-stability production resources in
    calculate_colony_production().
    """
    active = {social, economic, political}
    score = 0
    for id_a, id_b, delta in COMPATIBILITY_PAIRS:
        if id_a in active and id_b in active:
            score += delta

    for threshold, label, multiplier in COHERENCE_LEVELS:
        if score >= threshold:
            return score, label, multiplier

    # Fallback (should not be reached)
    return score, "High Friction", 0.80


def calculate_faction_affinity(
    social: str,
    economic: str,
    political: str,
    faction_prefs: dict,
) -> int:
    """
    Given a faction's preferred system configuration (dict with keys
    preferred_social, preferred_economic, preferred_political), return an
    integer reputation modifier in [-15, +15] representing how compatible
    the colony's systems are with this faction's worldview.

    +5 per matching system category, +0 per mismatch.
    Bonus +0 for faction_affinities fallback handled by caller.
    """
    matches = 0
    if faction_prefs.get("preferred_social")    == social:   matches += 1
    if faction_prefs.get("preferred_economic")  == economic: matches += 1
    if faction_prefs.get("preferred_political") == political: matches += 1

    # 0 → -5,  1 → 0,  2 → +5,  3 → +15
    affinity_map = {0: -5, 1: 0, 2: 5, 3: 15}
    return affinity_map[matches]


def get_available_systems(category: str, completed_research: list) -> list:
    """
    Return a list of system option dicts for the given category
    ('economic', 'political', 'social'), each annotated with lock state.

    Returned dict shape:
        id, name, description, modifiers, unique_commodity (economic only),
        commodity_amount (economic only), locked (bool), lock_reason (str|None),
        faction_affinities (list)
    """
    catalogue = {
        "economic":  ECONOMIC_SYSTEMS,
        "political": POLITICAL_SYSTEMS,
        "social":    SOCIAL_SYSTEMS,
    }.get(category, {})

    options = []
    for sys_id, defn in catalogue.items():
        req = defn.get("research_required")
        locked = bool(req and req not in completed_research)
        entry = {
            "id":                 sys_id,
            "name":               defn["name"],
            "description":        defn["description"],
            "modifiers":          defn.get("modifiers", {}),
            "research_required":  req,
            "locked":             locked,
            "lock_reason":        f"Requires research: {req}" if locked else None,
            "faction_affinities": defn.get("faction_affinities", []),
        }
        if category == "economic":
            entry["unique_commodity"]  = defn.get("unique_commodity")
            entry["commodity_amount"]  = defn.get("commodity_amount", 1)
        options.append(entry)

    return options


# Cooldown in turns before a system can be changed again.
SYSTEM_CHANGE_COOLDOWN = 5
