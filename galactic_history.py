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

# Counter-narrative themes for social justice perspective
MARGINALIZED_VOICES = [
    "displaced refugees fleeing expansion zones",
    "labor collectives operating outside official recognition",
    "hybrid populations denied citizenship by purist factions",
    "survivor communities maintaining pre-catastrophe traditions",
    "underground resistance movements",
    "unregistered settlements on frontier worlds",
    "subjugated species erased from official records",
    "dissidents imprisoned for questioning dominant narratives",
    "economic migrants trapped in exploitation cycles",
    "indigenous populations dispossessed of ancestral territories",
    "outlawed religious sects preserving alternative cosmologies",
    "mutual aid networks sustaining the forgotten",
]

FORGOTTEN_STRUGGLES = [
    "The silent genocide of non-FTL capable species during terraforming operations",
    "Mass deportations disguised as voluntary relocation programs",
    "Forced assimilation campaigns erasing cultural identities",
    "Economic blockades starving dissident colonies into submission",
    "Medical experimentation on 'lesser' species justified as research",
    "Child separation policies targeting mixed-heritage families",
    "Wage slavery systems maintaining cross-generational poverty",
    "Environmental destruction of habitable worlds for resource extraction",
    "Suppression of historical records documenting colonial atrocities",
    "Systematic denial of etheric access to marginalized populations",
]

RESISTANCE_VICTORIES = [
    "Underground railroad networks successfully evacuating thousands from oppression",
    "Wildcat strikes forcing recognition of workers' rights across sectors",
    "Cultural preservation movements maintaining forbidden languages and practices",
    "Sabotage campaigns halting expansion into protected territories",
    "Mutual aid communes proving alternative economic models viable",
    "Whistleblowers exposing war crimes despite personal cost",
    "Inter-species solidarity movements challenging supremacist ideologies",
    "Autonomous zones establishing self-governance outside imperial control",
    "Memory keepers documenting truths official histories tried to erase",
    "Survivor networks healing trauma through collective witness",
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
    # Counter-narrative elements
    marginalized_voices: List[str] = field(default_factory=list)
    forgotten_struggles: List[str] = field(default_factory=list)
    resistance_victories: List[str] = field(default_factory=list)
    suppressed_histories: List[str] = field(default_factory=list)

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
# Validation
# ===========================
def _validate_history(epochs: List["Epoch"]) -> None:
    # chronological order and non-empty windows
    for i, ep in enumerate(epochs):
        assert ep.start_year <= ep.end_year, f"Epoch window invalid: {ep.name}"
        if i:
            assert epochs[i-1].end_year <= ep.start_year or epochs[i-1].end_year + 1 >= ep.start_year, \
                f"Epochs out of order or overlapping oddly: {epochs[i-1].name} -> {ep.name}"

    # anchor presence checks
    anchors = {e.name: e for e in epochs}
    if "The Great Silence" in anchors:
        gs = anchors["The Great Silence"]
        assert any("Loss of interstellar comms" in m for m in gs.mysteries), \
            "Great Silence anchor note missing"

    if "The Etheric Convergence" in anchors:
        ec = anchors["The Etheric Convergence"]
        assert any("Widespread activation of Ether usage" in m for m in ec.mysteries), \
            "Etheric Convergence anchor note missing"

    if "Reformation After Silence" in anchors:
        rf = anchors["Reformation After Silence"]
        assert any("deep-space reconnaissance" in m for m in rf.mysteries), \
            "Post-Silence reconnaissance anchor note missing"

    # Terrans extinction constraint by YEAR_END (7019)
    if "Modern Cycle" in anchors:
        mc = anchors["Modern Cycle"]
        for c in mc.civilizations:
            if c.species == "Terrans":
                assert c.collapsed < YEAR_END, "Terrans must be collapsed before 7019 in Modern Cycle"

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

        # Optional (now enforced): curtail Terrans after the Silence window.
        # If the epoch starts after the Silence, re-roll species until not Terrans.
        # (Safety cap prevents pathological loops if SPECIES were reduced oddly.)
        if start >= GREAT_SILENCE_END and sp["name"] == "Terrans":
            for _reroll in range(10):
                sp = pick_species()
                if sp["name"] != "Terrans":
                    break

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
    if AVOID_CELESTIAL_ALLIANCE:
        plausible_factions = [f for f in plausible_factions if "Alliance" not in f]
    random.shuffle(plausible_factions)

    for f in plausible_factions[:random.randint(1, 3)]:
        when = random.randint(start, end)
        rationale = random.choice([
            "trade corridors", "research charters", "recon mandates",
            "craft standards", "cultural compacts"
        ])
        label = f
        faction_events.append(Event(when, f"{label} coalesces around {rationale}"))

    # Counter-narrative elements (2-4 of each type)
    marginalized = random.sample(MARGINALIZED_VOICES, k=random.randint(2, 4))
    struggles = random.sample(FORGOTTEN_STRUGGLES, k=random.randint(2, 3))
    victories = random.sample(RESISTANCE_VICTORIES, k=random.randint(1, 3))
    
    # Generate suppressed histories - stories that don't fit official narratives
    suppressed = []
    for _ in range(random.randint(2, 3)):
        year = random.randint(start, end)
        events_pool = [
            f"In {year:,}, evidence suggests a peaceful first contact was deliberately misrepresented as hostile",
            f"Records from {year:,} hint at a thriving non-hierarchical society later portrayed as 'primitive'",
            f"Survivors' testimonies from {year:,} contradict official accounts of voluntary migration",
            f"Archaeological evidence near {year:,} reveals prosperous settlements destroyed without provocation",
            f"Intercepted communications from {year:,} document orders to falsify resource scarcity reports",
            f"Witnesses from {year:,} reported seeing refugees turned away, contrary to open-borders propaganda",
        ]
        suppressed.append(random.choice(events_pool))

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
        marginalized_voices=marginalized,
        forgotten_struggles=struggles,
        resistance_victories=victories,
        suppressed_histories=suppressed,
    )

    # Inject required anchor events/constraints
    if "must_include_event" in epoch_template:
        inject_year = clamp((start + end) // 2, start, end)
        ep.mysteries.append(f"{epoch_template['must_include_event']} (c.{inject_year})")

    if epoch_template.get("name") == "Modern Cycle":
        # enforce Terrans extinction status by YEAR_END
        for c in ep.civilizations:
            if c.species == "Terrans":
                c.collapsed = min(c.collapsed, YEAR_END - 1)
        ep.mysteries.append("By 7019, Terrans are functionally extinct; only legacy caches and echoes remain.")

    return ep

def generate_history() -> List[Epoch]:
    if SEED is not None:
        random.seed(SEED)
    epochs: List[Epoch] = [generate_epoch(t) for t in EPOCH_TEMPLATES]
    epochs = sorted(epochs, key=lambda e: e.start_year)
    _validate_history(epochs)
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

    def get_epoch_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        for e in self.epochs:
            if e.name == name:
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
            "marginalized_voices": e.marginalized_voices,
            "forgotten_struggles": e.forgotten_struggles,
            "resistance_victories": e.resistance_victories,
            "suppressed_histories": e.suppressed_histories,
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
def generate_epoch_history(seed: Optional[int] = None):
    """Return epoch dicts for legacy callers (e.g., nethack_interface.py)."""
    return GalacticHistory(seed=seed).get_epochs()


def format_epoch_narrative(epoch: Dict[str, Any]) -> List[str]:
    """Convert epoch data into natural language narrative prose."""
    lines = []
    
    # Epoch header with dramatic opening
    name = epoch.get('name', 'Unnamed Epoch')
    start = epoch.get('start_year', 0)
    end = epoch.get('end_year', 0)
    duration = end - start
    
    lines.append("═" * 120)
    lines.append("")
    lines.append(f"  {name.upper()}")
    lines.append(f"  {start:,} – {end:,}")
    lines.append("")
    lines.append("─" * 120)
    lines.append("")
    
    # Opening narrative paragraph
    themes = epoch.get('themes', [])
    if themes:
        theme_text = ", ".join(themes[:-1])
        if len(themes) > 1:
            theme_text += f" and {themes[-1]}"
        else:
            theme_text = themes[0]
        
        lines.append(f"This era, spanning {duration:,} years, was defined by {theme_text}. ")
        lines.append(f"Across the galaxy, civilizations rose and fell, leaving behind echoes of their ")
        lines.append(f"ambitions and the silent ruins of what they had built.")
        lines.append("")
    
    # Cataclysms as dramatic narrative
    cataclysms = epoch.get('cataclysms', [])
    if cataclysms:
        lines.append("THE GREAT CATASTROPHES")
        lines.append("")
        lines.append(f"The epoch was marked by devastating events that reshaped the fabric of space itself. ")
        for i, cat in enumerate(cataclysms, 1):
            article = "A" if cat[0].lower() in 'aeiou' else "A"
            lines.append(f"{article} {cat} rippled through multiple systems, leaving scars visible even ")
            lines.append(f"generations later. ")
        lines.append("")
    
    # Faction formations as political narrative
    formations = epoch.get('faction_formations', [])
    if formations:
        lines.append("THE RISE OF NEW POWERS")
        lines.append("")
        lines.append(f"In the shifting political landscape, new alliances emerged to fill the vacuum left ")
        lines.append(f"by fallen empires. ")
        for f in formations:
            year = f.get('year', 0)
            event = f.get('event', '')
            lines.append(f"In {year:,}, {event}, establishing a framework that would ")
            lines.append(f"influence galactic affairs for centuries to come. ")
        lines.append("")
    
    # Mysteries as evocative prose
    mysteries = epoch.get('mysteries', [])
    if mysteries:
        lines.append("UNEXPLAINED PHENOMENA")
        lines.append("")
        lines.append(f"Not all events of this age can be explained by conventional understanding. ")
        for mys in mysteries:
            lines.append(f"{mys} These anomalies remain subjects of intense study and speculation, ")
            lines.append(f"defying the best efforts of scholars to categorize or predict them.")
            lines.append("")
    
    # Civilizations as biographical narratives
    civs = epoch.get('civilizations', [])
    if civs:
        lines.append("THE CIVILIZATIONS")
        lines.append("")
        lines.append(f"During this period, {len(civs)} distinct civilizations left their mark on history:")
        lines.append("")
        
        for civ in civs:
            name = civ.get('name', 'Unknown')
            species = civ.get('species', 'Unknown')
            traits = civ.get('traits', [])
            founded = civ.get('founded', 0)
            collapsed = civ.get('collapsed', founded)
            duration_civ = collapsed - founded
            remnants = civ.get('remnants', 'No remnants remain')
            
            # Opening for this civilization
            trait_desc = ", ".join(traits) if traits else "mysterious origins"
            lines.append(f"⟡ THE {name.upper()}")
            lines.append("")
            lines.append(f"The {name}, a civilization of {species} known for their {trait_desc}, emerged ")
            lines.append(f"in the year {founded:,}. For {duration_civ:,} years they flourished, carving out ")
            lines.append(f"their unique place in the galactic tapestry before their final collapse in {collapsed:,}.")
            lines.append("")
            
            # Notable events as story beats
            events = civ.get('notable_events', [])
            if events:
                lines.append(f"Their history was punctuated by defining moments:")
                for ev in events:
                    ev_year = ev.get('year', founded)
                    ev_desc = ev.get('description', 'an unknown event occurred')
                    lines.append(f"  • In {ev_year:,}, they {ev_desc}.")
                lines.append("")
            
            # Remnants as archaeological discovery
            lines.append(f"Today, their legacy persists in the form of scattered remnants: {remnants} ")
            lines.append(f"These artifacts stand as silent testimony to a people who once dreamed among the stars.")
            lines.append("")
            lines.append("")
    
    # COUNTER-NARRATIVE SECTION
    marginalized = epoch.get('marginalized_voices', [])
    struggles = epoch.get('forgotten_struggles', [])
    victories = epoch.get('resistance_victories', [])
    suppressed = epoch.get('suppressed_histories', [])
    
    if marginalized or struggles or victories or suppressed:
        lines.append("─" * 120)
        lines.append("")
        lines.append("VOICES FROM THE MARGINS: AN ALTERNATIVE HISTORY")
        lines.append("")
        lines.append("The official histories above chronicle the rise and fall of civilizations, the formation ")
        lines.append("of factions, and the grand mysteries of the age. But these narratives—curated by the ")
        lines.append("victorious, compiled by the powerful—tell only part of the story. Below the surface of ")
        lines.append("recorded history flows another current: the experiences of those written out of the record, ")
        lines.append("the struggles deemed too inconvenient to remember, the victories too threatening to acknowledge.")
        lines.append("")
    
    if marginalized:
        lines.append("THE FORGOTTEN PEOPLES")
        lines.append("")
        lines.append("While empires celebrated their expansion and factions consolidated their power, countless ")
        lines.append("communities existed in the shadows and margins of official recognition:")
        lines.append("")
        for voice in marginalized:
            lines.append(f"  ○ {voice.capitalize()}, whose stories were never recorded in the grand archives")
        lines.append("")
        lines.append("These populations—deemed unworthy of official notice or deliberately erased from the ")
        lines.append("historical record—nonetheless maintained their cultures, sustained their communities, ")
        lines.append("and survived against all odds.")
        lines.append("")
    
    if struggles:
        lines.append("SILENCED ATROCITIES")
        lines.append("")
        lines.append("The triumphant narratives of exploration and progress often gloss over or actively conceal ")
        lines.append("the violence required to achieve them. Recovered testimonies, suppressed documents, and ")
        lines.append("archaeological evidence reveal darker truths:")
        lines.append("")
        for struggle in struggles:
            lines.append(f"  ✦ {struggle}")
        lines.append("")
        lines.append("These crimes, committed in the name of civilization and progress, were rarely acknowledged ")
        lines.append("by those who benefited from them. Only through the persistent efforts of survivors, ")
        lines.append("truth-tellers, and historians working against official censorship do these stories survive.")
        lines.append("")
    
    if suppressed:
        lines.append("CONTESTED NARRATIVES")
        lines.append("")
        lines.append("Alternative sources and suppressed records suggest that many events unfolded quite ")
        lines.append("differently than official accounts would have us believe:")
        lines.append("")
        for sup in suppressed:
            lines.append(f"  ⚠ {sup}")
        lines.append("")
        lines.append("These discrepancies raise uncomfortable questions about whose truths are preserved and ")
        lines.append("whose are systematically buried.")
        lines.append("")
    
    if victories:
        lines.append("RESISTANCE AND RESILIENCE")
        lines.append("")
        lines.append("Yet the marginalized were not merely victims. Throughout this epoch, acts of resistance, ")
        lines.append("solidarity, and collective survival challenged dominant narratives and preserved alternatives:")
        lines.append("")
        for victory in victories:
            lines.append(f"  ◈ {victory}")
        lines.append("")
        lines.append("These victories—often small, local, and unacknowledged by official historians—represent ")
        lines.append("the persistent refusal of the oppressed to be erased. They remind us that every age ")
        lines.append("contains not just the history written by the powerful, but the histories created by those ")
        lines.append("who resisted them.")
        lines.append("")
    
    lines.append("")
    return lines

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
