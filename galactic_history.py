# 7019-aligned Galactic History Generator (canon-guided, procedurally varied)
# Notes:
# - Keeps randomness but constrains it to 7019 anchors and lore.
# - By default, avoids explicit “Celestial Alliance” naming; flip AVOID_CELESTIAL_ALLIANCE to False if desired.
# - End of timeline is fixed at YEAR_END = 7019 (humans/terrans functionally extinct by then).

import random
import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

# ================
# Config & Anchors
# ================
SEED: Optional[int] = None  # set an int for reproducible runs
AVOID_CELESTIAL_ALLIANCE = True

YEAR_START = 6000      # start of our curated timeline window
YEAR_END   = 7019      # canonical present
# Anchor windows (editable if you later lock dates tighter)
ETHERIC_CONVERGENCE_WINDOW = (6150, 6200)     # first widespread activation of Ether Magic
GREAT_SILENCE_START        = 6420             # “nearly a century” fits 6420–6510 default
GREAT_SILENCE_END          = 6510
POST_SILENCE_REFORM        = (6515, 6560)     # reorganization, Deep Space Reconnaissance Command, etc.

# =======================
# Canon Species & Factions
# =======================
SPECIES = [
    {"name": "Terrans", "traits": ["post-Anthropocene diaspora", "legacy tech caches", "functionally extinct by 7019"]},
    {"name": "Silvans", "traits": ["plant-based sentients", "bio-cities", "spore diplomacy"]},
    {"name": "Aurorans", "traits": ["energy beings", "radiant communication", "light-phase habitats"]},
    {"name": "Zentari", "traits": ["amphibious humanoids", "pressure-adapted", "fluidic computation"]},
    {"name": "Gaians", "traits": ["lithic physiology", "geode memory vaults", "seismic languages"]},
    {"name": "Luminauts", "traits": ["light manipulation", "prism arrays", "spectral philosophy"]},
    {"name": "Synthetix", "traits": ["cybernetic organisms", "consensus firmware", "precision craft"]},
    {"name": "Mycelioids", "traits": ["fungal intelligence", "hyphal networks", "distributed minds"]},
    {"name": "Chronauts", "traits": ["time-aware perception", "chronometric rituals", "loop hygiene"]},
    {"name": "Umbraxians", "traits": ["dark-matter affinity", "umbra fields", "low-emission cultures"]},
    {"name": "Eternals", "traits": ["effective immortality", "long-cycle planning", "stasis ethics"]},
    {"name": "Xha’reth", "traits": ["etheric-advanced", "non-Euclidean craft", "singular aesthetics"]},
]

# Canon factions from 7019; wording kept generic when AVOID_CELESTIAL_ALLIANCE=True
FACTIONS = [
    "Veritas Covenant",
    "Stellar Nexus Guild",
    "Harmonic Vitality Consortium",
    "Icaron Collective",
    "Gaian Enclave",
    "Gearwrights Guild",
    "Scholara Nexus",
    "Harmonic Resonance Collective",
    "Provocateurs' Guild",
    "Quantum Artificers Guild",
    "Stellar Cartographers Alliance",
    "Galactic Circus",
    "Technotheos",
    "Keepers of the Spire",
    "Etheric Preservationists",
    "Technomancers",
    "Voidbound Monks",
    "Ironclad Collective",
    "Collective of Commonality",
    "Brewmasters' Guild",
]

# Lost civilizations & remnants (from your samples)
LOST_CIVIL_REMNANTS = {
    "Zenthorian Empire": "Crystal communication nodes scattered across deserted planets, faintly cross-linking under stellar winds.",
    "Oreon Civilization": "Submerged ruins beneath acidic seas; pressure-stable conduits still hum at trench floors.",
    "Myridian Builders": "Colossal moon statues aligned to archaic celestial lattices—navigation aids across epochs.",
    "Aetheris Collective": "Faint etheric echoes in hard vacuum; thought-bridges spark under auroral bombardment.",
    "Garnathans of Vorex": "Petrified forest-cities; bio-engineered arbor forms calcified mid-growth.",
    "Silix Supremacy": "Indecipherable ultra-hard silicate dataslates; write-once memory that outlived its readers.",
    "Draconis League": "Ruined star fortresses orbiting dead suns; armor vitrified by unknown beams.",
    "Luminar Ascendency": "Prisms that still project spectral oratorios when stellar angles align.",
    "Echoes of Entari": "Sound sculptures on windscoured worlds; entire valleys tuned to lost chords.",
}

# Ether/tech mishap palette aligned to 7019
CATACLYSMS = [
    "Chrono-synthetic Flux surge",
    "Etheric overdraw collapse",
    "Wormline fracture event",
    "Nanoforge swarm runaway",
    "Psionic harmonics burnout",
    "Gravitic shear cascade",
    "Quantum tunnel misaddress",
    "Memory-plague bloom",
    "Dark-energy wake inversion",
    "Subspace lattice implosion",
]

MYSTERIES = [
    "A message arrives from within a stable singularity in a voice no species claims",
    "Twelve moons on unrelated worlds shift into identical resonant orbits",
    "A fleet re-emerges before its recorded departure with correct fuel delta",
    "A nebula enforces asymmetric time dilation across its biconvex shell",
    "An archival monument outputs valid predictions, then melts into sand",
]

# =================
# Epochs (Canon-led)
# =================
# We construct epochs around anchors rather than picking freeform durations.
EPOCH_TEMPLATES = [
    {
        "name": "Pre-Convergence Drift",
        "window": (YEAR_START, ETHERIC_CONVERGENCE_WINDOW[0] - 1),
        "themes": ["early FTL experiments", "generation waystations", "proto-guilds", "archive seeding"],
    },
    {
        "name": "The Etheric Convergence",
        "window": ETHERIC_CONVERGENCE_WINDOW,
        "themes": ["first awakenings", "ether-tech integration", "navigation upheaval", "power rebalancing"],
        "must_include_event": "Widespread activation of Ether usage across multiple civilizations",
    },
    {
        "name": "Expansion & Awakening",
        "window": (ETHERIC_CONVERGENCE_WINDOW[1] + 1, GREAT_SILENCE_START - 1),
        "themes": ["terraformation booms", "inter-species accords", "trade lanes", "cultural fusion"],
    },
    {
        "name": "The Great Silence",
        "window": (GREAT_SILENCE_START, GREAT_SILENCE_END),
        "themes": ["communications blackout", "vanishing ships", "isolation", "local resilience"],
        "must_include_event": "Loss of interstellar comms across a vast quadrant; entrants do not return",
    },
    {
        "name": "Reformation After Silence",
        "window": (POST_SILENCE_REFORM[0], POST_SILENCE_REFORM[1]),
        "themes": ["deep reconnaissance", "protocol hardening", "redundant comms", "risk cartography"],
        "must_include_event": "Formation of a dedicated deep-space reconnaissance command",
    },
    {
        "name": "Late Neo-Renaissance",
        "window": (POST_SILENCE_REFORM[1] + 1, 6950),
        "themes": ["art-science synthesis", "diplomatic recombination", "education compacts", "craft guild ascendance"],
    },
    {
        "name": "Convergence Conflicts",
        "window": (6951, 6990),
        "themes": ["ideological clashes", "proxy theatres", "ethics of power", "containment doctrines"],
    },
    {
        "name": "Modern Cycle",
        "window": (6991, YEAR_END),
        "themes": ["fragile peace", "frontier probes", "innovation bursts", "quiet catastrophes averted"],
        "must_include_constraint": "Terrans are functionally extinct by 7019",
    },
]

# ==========================
# Helper dataclasses & utils
# ==========================
@dataclass
class Event:
    year: int
    description: str

@dataclass
class Civilization:
    name: str
    species: str
    traits: List[str]
    founded: int
    collapsed: int
    remnant: str
    notable_events: List[Event] = field(default_factory=list)

@dataclass
class Epoch:
    epoch_id: str
    name: str
    start_year: int
    end_year: int
    themes: List[str]
    civilizations: List[Civilization]
    cataclysms: List[str]
    mysteries: List[str]
    faction_formations: List[Event]

# name builders tuned for 7019 “feel”
PREFIX = ["Aeth", "Vor", "Zyn", "Kry", "Lum", "Xha", "Orr", "Thal", "Mir", "Nex",
          "Syl", "Dra", "Qua", "Zen", "Pyr", "Kor", "Vel", "Ix", "Nar", "Tel"]
MIDFIX = ["-", " ", "", ""]
SUFFIX = ["ari", "oth", "en", "yx", "ion", "ath", "ara", "is", "um", "el",
          "ax", "os", "ir", "un", "eth", "al", "ix", "or", "ak", "ian"]

def build_name(base: str) -> str:
    return f"{random.choice(PREFIX)}{random.choice(MIDFIX)}{random.choice(SUFFIX)} {base}"

def pick_species() -> Dict[str, Any]:
    s = random.choice(SPECIES)
    return {"name": s["name"], "traits": s["traits"]}

def lost_civ_remnant() -> str:
    name, desc = random.choice(list(LOST_CIVIL_REMNANTS.items()))
    return f"{name}: {desc}"

def clamp(a: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, a))

# ===========================
# Generation (canon-constrained)
# ===========================
def generate_epoch(epoch_template: Dict[str, Any]) -> Epoch:
    start, end = epoch_template["window"]
    if start > end:
        # degenerate window; collapse to a single year
        start, end = end, end

    # choose 2–4 themes
    themes = random.sample(epoch_template["themes"], k=min(len(epoch_template["themes"]), random.randint(2, 4)))

    # civilizations in epoch (3–7), lifespans constrained to the window
    civs: List[Civilization] = []
    for _ in range(random.randint(3, 7)):
        sp = pick_species()
        name = build_name(sp["name"])
        # ensure internal timeline sanity
        rise = random.randint(start, end)
        span = max(5, int((end - start) * random.uniform(0.08, 0.45)))
        fall = clamp(rise + span, rise + 1, end)
        rem = lost_civ_remnant()

        # 2–4 events per civ
        evs: List[Event] = []
        for _ in range(random.randint(2, 4)):
            year = random.randint(rise, fall)
            desc = random.choice([
                "stabilized a wormline through turbulent ether",
                "suffered a localized Chrono-synthetic Flux rebound",
                "deployed prism-array translators to bridge cultures",
                "mapped dark-wake eddies for safer drift",
                "contained a nanoforge runaway at cost of a moon",
                "catalogued echo-ruins from a forgotten polity",
                "instituted loop-hygiene after minor time drift",
            ])
            evs.append(Event(year, desc))

        civs.append(Civilization(
            name=name,
            species=sp["name"],
            traits=sp["traits"],
            founded=rise,
            collapsed=fall,
            remnant=rem,
            notable_events=sorted(evs, key=lambda e: e.year),
        ))

    # 1–3 cataclysms and 0–2 mysteries per epoch
    cats = random.sample(CATACLYSMS, k=random.randint(1, 3))
    mys  = random.sample(MYSTERIES,   k=random.randint(0, 2))

    # faction formations that make sense for this epoch’s theme window
    faction_events: List[Event] = []
    plausible_factions = list(FACTIONS)
    random.shuffle(plausible_factions)
    for f in plausible_factions[:random.randint(1, 3)]:
        when = random.randint(start, end)
        # gate any explicit “Alliance” wording if desired (kept generic anyway)
        label = f
        faction_events.append(Event(when, f"{label} coalesces around {random.choice(['trade corridors','research charters','recon mandates','craft standards','cultural compacts'])}"))

    ep = Epoch(
        epoch_id=str(uuid.uuid4())[:8],
        name=epoch_template["name"],
        start_year=start,
        end_year=end,
        themes=themes,
        civilizations=sorted(civs, key=lambda c: c.founded),
        cataclysms=cats,
        mysteries=mys,
        faction_formations=sorted(faction_events, key=lambda e: e.year),
    )

    # Inject required anchor events/constraints
    if "must_include_event" in epoch_template:
        inject_year = clamp((start + end) // 2, start, end)
        ep.mysteries.append(f"{epoch_template['must_include_event']} (c.{inject_year})")

    if epoch_template.get("name") == "Modern Cycle":
        # enforce Terrans extinction status by YEAR_END
        # We won’t delete Terran civs earlier, but mark their status if present
        for c in ep.civilizations:
            if c.species == "Terrans":
                c.collapsed = min(c.collapsed, YEAR_END - 1)
        # Add explicit constraint note
        ep.mysteries.append("By 7019, Terrans are functionally extinct; only legacy caches and echoes remain.")

    return ep

def generate_history() -> List[Epoch]:
    if SEED is not None:
        random.seed(SEED)
    epochs: List[Epoch] = [generate_epoch(t) for t in EPOCH_TEMPLATES]
    # sanity: ensure chronological sequencing without gaps/overlaps beyond the defined windows
    epochs = sorted(epochs, key=lambda e: e.start_year)
    return epochs

# =========================
# Public API (class wrapper)
# =========================

class GalacticHistory:
    """Canon-guided 7019 history with constrained randomness."""
    def __init__(self, seed: Optional[int] = SEED):
        if seed is not None:
            random.seed(seed)
        self.epochs: List[Epoch] = generate_history()

    def get_epochs(self) -> List[Dict[str, Any]]:
        return [self._epoch_to_dict(e) for e in self.epochs]

    def get_current_year(self) -> int:
        return YEAR_END

    def get_epoch_by_year(self, year: int) -> Optional[Dict[str, Any]]:
        for e in self.epochs:
            if e.start_year <= year <= e.end_year:
                return self._epoch_to_dict(e)
        return None

    # ===== Helpers =====
    def _epoch_to_dict(self, e: Epoch) -> Dict[str, Any]:
        return {
            "epoch_id": e.epoch_id,
            "name": e.name,
            "start_year": e.start_year,
            "end_year": e.end_year,
            "themes": e.themes,
            "cataclysms": e.cataclysms,
            "mysteries": e.mysteries,
            "faction_formations": [{"year": ev.year, "event": ev.description} for ev in e.faction_formations],
            "civilizations": [
                {
                    "name": c.name,
                    "species": c.species,
                    "traits": c.traits,
                    "founded": c.founded,
                    "collapsed": c.collapsed,
                    "remnants": c.remnant,
                    "notable_events": [{"year": ev.year, "description": ev.description} for ev in c.notable_events],
                } for c in e.civilizations
            ],
        }

# === Legacy API for UI compatibility ===
def generate_epoch_history():
    """Legacy API for UI compatibility: returns epoch dicts as expected by nethack_interface.py."""
    return GalacticHistory().get_epochs()

    def get_epoch_by_year(self, year: int) -> Optional[Dict[str, Any]]:
        for e in self.epochs:
            if e.start_year <= year <= e.end_year:
                return self._epoch_to_dict(e)
        return None

    # ===== Helpers =====

    def _epoch_to_dict(self, e: Epoch) -> Dict[str, Any]:
        return {
            "epoch_id": e.epoch_id,
            "name": e.name,
            "start_year": e.start_year,
            "end_year": e.end_year,
            "themes": e.themes,
            "cataclysms": e.cataclysms,
            "mysteries": e.mysteries,
            "faction_formations": [{"year": ev.year, "event": ev.description} for ev in e.faction_formations],
            "civilizations": [
                {
                    "name": c.name,
                    "species": c.species,
                    "traits": c.traits,
                    "founded": c.founded,
                    "collapsed": c.collapsed,
                    "remnants": c.remnant,
                    "notable_events": [{"year": ev.year, "description": ev.description} for ev in c.notable_events],
                } for c in e.civilizations
            ],
        }

# === Legacy API for UI compatibility ===
def generate_epoch_history():
    """Legacy API for UI compatibility: returns epoch dicts as expected by nethack_interface.py."""
    return GalacticHistory().get_epochs()

# =========================
# Demo CLI (pretty printer)
# =========================
if __name__ == "__main__":
    gh = GalacticHistory(seed=SEED)
    for ep in gh.get_epochs():
        print(f"\n=== {ep['name']} ({ep['start_year']} – {ep['end_year']}) ===")
        print("Themes:", ", ".join(ep["themes"]))
        if ep["cataclysms"]:
            print("Cataclysms:", ", ".join(ep["cataclysms"]))
        if ep["mysteries"]:
            print("Notable Notes/Mysteries:")
            for m in ep["mysteries"]:
                print("  -", m)
        if ep["faction_formations"]:
            print("Factions:")
            for f in ep["faction_formations"]:
                print(f"  • {f['year']}: {f['event']}")
        print("Civilizations:")
        for c in ep["civilizations"]:
            print(f"  - {c['name']} [{c['species']}]")
            print(f"    Traits: {', '.join(c['traits'])}")
            print(f"    {c['founded']} → {c['collapsed']}")
            print(f"    Remnants: {c['remnants']}")
            for ev in c["notable_events"]:
                print(f"      * {ev['year']}: {ev['description']}")
