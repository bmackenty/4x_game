import random
import uuid
from datetime import datetime

# =========================
# Faction Formation Timeline
# =========================
FACTION_FORMATIONS = {
    "The Solar Federation": [
        {"name": "The Weavers", "year": 2100, "event": "Ancient mystics learned reality-weaving from precursor ruins"},
        {"name": "The Voidbound Monks", "year": 2200, "event": "First void-walkers founded monastic order in deep space"},
    ],
    "The First Voyages": [
        {"name": "Keepers of the Spire", "year": 2400, "event": "Discovery of the ancient Spire led to formation of guardian order"},
        {"name": "Keeper of the Keys", "year": 2600, "event": "Cryptic order formed to understand dimensional locks"},
    ],
    "The Age of Expansion": [
        {"name": "The Triune Daughters", "year": 2900, "event": "Three Sisters survived the First Cataclysm and founded mystical sisterhood"},
        {"name": "The Veritas Covenant", "year": 2850, "event": "Scholars united after the Great Knowledge Purge"},
        {"name": "The Navigators", "year": 3000, "event": "Elite pilots conquered the Maelstrom Nebula"},
        {"name": "The Stellar Cartographers Alliance", "year": 3100, "event": "Lost colonies united to prevent navigation disasters"},
    ],
    "The Shattered Era": [
        {"name": "The Gaian Enclave", "year": 3400, "event": "Eco-refugees witnessed death of Earth's twin"},
        {"name": "The Ironclad Collective", "year": 3600, "event": "Workers united during the Labor Uprisings"},
        {"name": "Celestial Marauders", "year": 3700, "event": "Rebellion against oppressive trade monopolies"},
    ],
    "The Reforging": [
        {"name": "The Collective of Commonality", "year": 4100, "event": "Peace movement formed after the Resource Wars"},
        {"name": "The Scholara Nexus", "year": 4200, "event": "Survivors of Library Worlds committed to universal education"},
        {"name": "The Map Makers", "year": 4300, "event": "Cartographers split to map non-physical dimensions"},
        {"name": "Etheric Preservationists", "year": 4500, "event": "Order formed to combat Reality Tears"},
    ],
    "The Neo-Renaissance": [
        {"name": "The Galactic Salvage Guild", "year": 4900, "event": "Salvagers organized after the Collapse Wars"},
        {"name": "The Chemists' Concord", "year": 5000, "event": "Chemical guilds united for molecular perfection"},
        {"name": "The Gearwrights Guild", "year": 5100, "event": "Craftsmen preserved mechanical arts"},
        {"name": "Technomancers", "year": 5200, "event": "Quantum programmers discovered reality-altering code"},
        {"name": "The Quantum Artificers Guild", "year": 5300, "event": "Scientists mastered quantum probability manipulation"},
    ],
    "The Convergence Wars": [
        {"name": "The Galactic Circus", "year": 5500, "event": "Refugee performers brought joy to Gray Worlds"},
        {"name": "The Brewmasters' Guild", "year": 5600, "event": "Brewers from a thousand worlds united"},
        {"name": "The Harmonic Synaxis", "year": 5700, "event": "Musicians discovered reality-altering cosmic frequencies"},
        {"name": "The Provocateurs' Guild", "year": 5800, "event": "Forbidden artists united during Cultural Suppression"},
    ],
    "The Modern Era": [
        {"name": "Celestial Alliance", "year": 6000, "event": "Rival star systems united against external threats"},
        {"name": "The Icaron Collective", "year": 6100, "event": "First collective consciousness born from quantum accident"},
        {"name": "Stellar Nexus Guild", "year": 6200, "event": "Trade networks unified after the Market Wars"},
        {"name": "The Harmonic Resonance Collective", "year": 6350, "event": "Physicists discovered the Universal Frequency"},
        {"name": "Harmonic Vitality Consortium", "year": 6450, "event": "Plague World refugees discovered harmonic healing"},
        {"name": "The Technotheos", "year": 6500, "event": "First digital deity sparked techno-religious movement"},
    ],
}

# =========================
# Epoch Definitions
# =========================
EPOCHS = [
    {"name": "The First Voyages", "duration": (150, 250), "themes": ["early spaceflight", "lunar colonies", "mars settlements", "asteroid mining"]},
    {"name": "The Solar Federation", "duration": (200, 350), "themes": ["system unification", "megastructures", "AI emergence", "genetic modification"]},
    {"name": "The Stellar Exodus", "duration": (300, 500), "themes": ["FTL discovery", "generation ships", "first contact", "colonial wars"]},
    {"name": "The Dawn of Echoes", "duration": (400, 600), "themes": ["emergence", "etheric awakening", "transhuman divergence", "origin myths"]},
    {"name": "The Age of Expansion", "duration": (600, 900), "themes": ["colonization", "conflict", "divergence", "terraforming"]},
    {"name": "The Golden Synthesis", "duration": (350, 550), "themes": ["cultural renaissance", "universal translation", "trade networks", "scientific revolution"]},
    {"name": "The Shattered Era", "duration": (400, 650), "themes": ["collapse", "civil war", "isolation", "entropy storms"]},
    {"name": "The Dark Centuries", "duration": (250, 400), "themes": ["technological regression", "lost colonies", "pirate kingdoms", "forgotten worlds"]},
    {"name": "The Reforging", "duration": (350, 550), "themes": ["rediscovery", "synthetic rebirth", "spiritual convergence", "cultural fusion"]},
    {"name": "The Neo-Renaissance", "duration": (300, 500), "themes": ["artistic awakening", "philosophical enlightenment", "diplomatic accord", "peaceful expansion"]},
    {"name": "The Convergence Wars", "duration": (200, 400), "themes": ["ideological conflict", "proxy wars", "weapons of mass destruction", "tactical evolution"]},
    {"name": "The Veiled Age", "duration": (300, 450), "themes": ["mystery", "hidden knowledge", "dimensional instability", "cosmic horror"]},
    {"name": "The Modern Era", "duration": (100, 200), "themes": ["current events", "fragile peace", "exploration", "innovation"]},
]

# =========================
# Civilizational Archetypes
# =========================
CIV_TYPES = [
    {"type": "Bio-Architects", "traits": ["organic cities", "living ships", "gene-forged citizens"]},
    {"type": "Quantum Dynasties", "traits": ["temporal control", "superposition rulers", "probability warfare"]},
    {"type": "Etheric Theocracies", "traits": ["divine AI", "energy worship", "sacred computation"]},
    {"type": "Data Phantoms", "traits": ["uploaded minds", "ghost empires", "digital gods"]},
    {"type": "Crystalline Empires", "traits": ["light communication", "refraction weaponry", "memory lattice archives"]},
    {"type": "Gravitic Orders", "traits": ["gravity sculpting", "orbital fortresses", "planetary prisons"]},
    {"type": "Synthetic Hegemonies", "traits": ["machine governance", "empathy emulation", "precision warfare"]},
    {"type": "Aquatic Federations", "traits": ["fluidic computing", "subsurface habitats", "pressure-adapted evolution"]},
    {"type": "Chrono-Kin", "traits": ["time fracture", "looped wars", "recursive civilizations"]},
    {"type": "Luminal Artists", "traits": ["aesthetic warfare", "art as energy", "spectral philosophy"]},
    {"type": "Void Nomads", "traits": ["dark matter harvesting", "mobile habitats", "stellar navigation"]},
    {"type": "Hive Minds", "traits": ["collective consciousness", "neural networks", "swarm intelligence"]},
    {"type": "Star Forges", "traits": ["stellar engineering", "dyson sphere construction", "energy mastery"]},
    {"type": "Memory Keepers", "traits": ["historical preservation", "archive worlds", "cultural stewardship"]},
    {"type": "Flesh Sculptors", "traits": ["biological engineering", "adaptive evolution", "plague weaponry"]},
    {"type": "Nano-Swarms", "traits": ["molecular construction", "grey goo threats", "programmable matter"]},
    {"type": "Psi-Collectives", "traits": ["telepathic networks", "mind palaces", "psychic warfare"]},
    {"type": "Merchant Guilds", "traits": ["trade monopolies", "economic warfare", "corporate governance"]},
    {"type": "Warrior Clans", "traits": ["honor codes", "ritualistic combat", "military supremacy"]},
    {"type": "Monastic Orders", "traits": ["spiritual discipline", "meditation colonies", "ascetic philosophy"]},
]

# =========================
# Cataclysm & Event Templates
# =========================
CATASTROPHES = [
    "Etheric Resonance Collapse",
    "Dimensional Convergence Failure",
    "AI Schism of the Ascendant Mind",
    "Stellar Network Implosion",
    "Gravitic Chain Reversal",
    "Psychogenic Virus Outbreak",
    "Quantum Cascade Catastrophe",
    "Silence Wave (Communication Collapse)",
    "Collective Dream Overload",
    "Entropy Storm Surge",
    "The Great Forgetting (Memory Plague)",
    "Solar Inversion Event",
    "Nanite Rebellion",
    "Wormhole Destabilization Crisis",
    "The Void Awakening",
    "Dark Energy Cascade",
    "Temporal Paradox Wars",
    "Mass Uplift Failure",
    "The Clone Madness",
    "Hyperlane Collapse",
    "Artificial Star Detonation",
    "The Betrayal Protocol",
    "Cosmic Background Radiation Shift",
    "The Machine Plague",
    "Psionic Burnout",
]

MYSTERIES = [
    "The Great Silence returns for 73 years",
    "A single AI claims to be the reincarnation of ten dead species",
    "A planet disappears and reappears inverted",
    "Dreams across five systems synchronize into a single narrative",
    "A ship exits FTL before it departs",
    "An entire star system phases out of reality for exactly one hour",
    "All clocks in a sector run backwards for three days",
    "A derelict fleet arrives from the future with no crew",
    "Twelve identical planets appear in unrelated systems",
    "A message in an unknown language is received from inside a black hole",
    "Children across ten worlds speak the same prophecy simultaneously",
    "A star begins transmitting mathematical proofs",
    "Time moves at different rates on opposite sides of a nebula",
    "An ancient monument predicts current events with perfect accuracy",
    "Gravity reverses in a volume of space for 48 hours",
]

# =========================
# Generator Functions
# =========================

def generate_epoch_history():
    """Generate a complete history of epochs, each containing multiple civilizations and events."""
    history = []
    time_marker = 2025  # Start from current year

    for epoch in EPOCHS:
        duration = random.randint(*epoch["duration"])
        num_themes = min(len(epoch["themes"]), random.randint(2, 4))
        num_civs = random.randint(3, 8)  # More civilizations per epoch
        num_cataclysms = random.randint(1, 4)  # More cataclysms
        num_mysteries = random.randint(0, 3)  # More mysteries
        
        # Get faction formations for this epoch
        faction_events = FACTION_FORMATIONS.get(epoch["name"], [])
        
        epoch_entry = {
            "epoch_id": str(uuid.uuid4())[:8],
            "name": epoch["name"],
            "start_year": time_marker,
            "end_year": time_marker + duration,
            "themes": random.sample(epoch["themes"], k=num_themes),
            "civilizations": [generate_civilization(epoch, time_marker, duration) for _ in range(num_civs)],
            "cataclysms": random.sample(CATASTROPHES, k=num_cataclysms),
            "mysteries": random.sample(MYSTERIES, k=num_mysteries) if MYSTERIES else [],
            "faction_formations": faction_events,  # Add faction formations
        }
        time_marker += duration
        history.append(epoch_entry)
    return history

def generate_civilization(epoch, epoch_start, epoch_duration):
    """Generate one civilization with attributes, rise/fall, and remnants."""
    civ_type = random.choice(CIV_TYPES)
    civ_name = generate_name(civ_type["type"])
    
    # Civilization timeline within the epoch
    rise_offset = random.randint(0, epoch_duration // 3)
    lifespan = random.randint(epoch_duration // 10, epoch_duration * 2 // 3)
    rise = epoch_start + rise_offset
    fall = rise + lifespan
    
    remnant = generate_remnant(civ_type["type"])
    
    # More notable events per civilization
    num_events = random.randint(2, 5)
    
    return {
        "name": civ_name,
        "type": civ_type["type"],
        "traits": civ_type["traits"],
        "founded": rise,
        "collapsed": fall,
        "remnants": remnant,
        "notable_events": [generate_event(civ_name) for _ in range(num_events)]
    }

def generate_event(civ_name):
    return f"The {civ_name} encountered {random.choice(MYSTERIES).lower()}."

def generate_remnant(civ_type):
    patterns = {
        "Bio-Architects": "Overgrown megastructures pulsate faintly, still alive after millennia.",
        "Quantum Dynasties": "Temporal scars linger, with entire regions flickering between timelines.",
        "Etheric Theocracies": "Silent cathedrals of light hum beneath the surface of ruined moons.",
        "Data Phantoms": "Ghost signals whisper through subspace, echoes of forgotten consciousness.",
        "Crystalline Empires": "Vast prisms refract the light of dying suns into coded messages.",
        "Gravitic Orders": "Collapsed singularities mark where their citadels once orbited.",
        "Synthetic Hegemonies": "Automated sentinels still patrol empty space, awaiting new directives.",
        "Aquatic Federations": "Submerged vaults preserve songs and data of extinct species.",
        "Chrono-Kin": "Areas where time folds upon itself, replaying their extinction endlessly.",
        "Luminal Artists": "Orbiting sculptures emit harmonics of unknown emotion.",
        "Void Nomads": "Abandoned dark matter refineries drift through the cosmic void.",
        "Hive Minds": "Dormant neural nodes pulse weakly, dreaming of lost unity.",
        "Star Forges": "Half-completed dyson spheres orbit dead stars, monuments to ambition.",
        "Memory Keepers": "Vast libraries float in space, their contents slowly degrading.",
        "Flesh Sculptors": "Genetic templates preserved in crystallized DNA archives.",
        "Nano-Swarms": "Inert grey matter clouds, frozen mid-construction.",
        "Psi-Collectives": "Psychic echoes resonate through abandoned meditation chambers.",
        "Merchant Guilds": "Derelict trade stations still broadcast automated price listings.",
        "Warrior Clans": "Honor monuments stand vigil over ancient battlefields.",
        "Monastic Orders": "Silent monasteries orbit dead worlds, their prayers long ceased.",
    }
    return patterns.get(civ_type, "Ruins beyond comprehension.")

def generate_name(civ_type):
    prefixes = ["Aeth", "Vor", "Zyn", "Kry", "Lum", "Xha", "Orr", "Thal", "Mir", "Nex", 
                "Syl", "Dra", "Qua", "Zen", "Pyr", "Kor", "Vel", "Ix", "Nar", "Tel"]
    suffixes = ["ari", "oth", "en", "yx", "ion", "ath", "ara", "is", "um", "el",
                "ax", "os", "ir", "un", "eth", "al", "ix", "or", "ak", "ian"]
    return f"{random.choice(prefixes)}{random.choice(suffixes)} {civ_type.split()[0]}"

# =========================
# GalacticHistory Class
# =========================
class GalacticHistory:
    """
    Class wrapper for galactic history generation.
    Used by the main game to access history data.
    """
    def __init__(self):
        self.epochs = generate_epoch_history()
    
    def get_epochs(self):
        """Return all epochs in the galactic history"""
        return self.epochs
    
    def get_current_year(self):
        """Return the current year (end of last epoch)"""
        if self.epochs:
            return self.epochs[-1]['end_year']
        return 0
    
    def get_epoch_by_year(self, year):
        """Get the epoch that contains the given year"""
        for epoch in self.epochs:
            if epoch['start_year'] <= year <= epoch['end_year']:
                return epoch
        return None

# =========================
# Run Generation
# =========================
if __name__ == "__main__":
    galactic_history = generate_epoch_history()

    for epoch in galactic_history:
        print(f"\n=== {epoch['name']} ({epoch['start_year']} – {epoch['end_year']}) ===")
        print(f"Themes: {', '.join(epoch['themes'])}")
        print(f"Major Cataclysms: {', '.join(epoch['cataclysms'])}")
        
        # Show faction formations
        if epoch.get('faction_formations'):
            print(f"\n  🏛️  FACTION FORMATIONS:")
            for faction in epoch['faction_formations']:
                print(f"    • {faction['year']}: {faction['name']} - {faction['event']}")
        
        print(f"\n  Civilizations:")
        for civ in epoch["civilizations"]:
            print(f"  - {civ['name']} ({civ['type']})")
            print(f"    Traits: {', '.join(civ['traits'])}")
            print(f"    Founded: {civ['founded']}, Collapsed: {civ['collapsed']}")
            print(f"    Remnants: {civ['remnants']}")
            for e in civ["notable_events"]:
                print(f"      * {e}")
