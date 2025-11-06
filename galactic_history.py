import random
import uuid
from datetime import datetime

# =========================
# Epoch Definitions
# =========================
EPOCHS = [
    {"name": "The Dawn of Echoes", "duration": (2000, 5000), "themes": ["emergence", "etheric awakening", "first contact", "origin myths"]},
    {"name": "The Age of Expansion", "duration": (5000, 10000), "themes": ["colonization", "conflict", "divergence", "terraforming"]},
    {"name": "The Shattered Era", "duration": (1000, 3000), "themes": ["collapse", "civil war", "isolation", "entropy storms"]},
    {"name": "The Reforging", "duration": (2000, 6000), "themes": ["rediscovery", "synthetic rebirth", "spiritual convergence", "cultural fusion"]},
    {"name": "The Veiled Age", "duration": (1000, 2000), "themes": ["mystery", "hidden knowledge", "dimensional instability"]},
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
]

MYSTERIES = [
    "The Great Silence returns for 73 years",
    "A single AI claims to be the reincarnation of ten dead species",
    "A planet disappears and reappears inverted",
    "Dreams across five systems synchronize into a single narrative",
    "A ship exits FTL before it departs",
]

# =========================
# Generator Functions
# =========================

def generate_epoch_history():
    """Generate a complete history of epochs, each containing multiple civilizations and events."""
    history = []
    time_marker = 0

    for epoch in EPOCHS:
        duration = random.randint(*epoch["duration"])
        epoch_entry = {
            "epoch_id": str(uuid.uuid4())[:8],
            "name": epoch["name"],
            "start_year": time_marker,
            "end_year": time_marker + duration,
            "themes": random.sample(epoch["themes"], k=2),
            "civilizations": [generate_civilization(epoch) for _ in range(random.randint(2, 6))],
            "cataclysms": random.sample(CATASTROPHES, k=random.randint(1, 3)),
            "mysteries": random.sample(MYSTERIES, k=random.randint(0, 2)),
        }
        time_marker += duration
        history.append(epoch_entry)
    return history

def generate_civilization(epoch):
    """Generate one civilization with attributes, rise/fall, and remnants."""
    civ_type = random.choice(CIV_TYPES)
    civ_name = generate_name(civ_type["type"])
    rise = random.randint(epoch["duration"][0]//10, epoch["duration"][1]//2)
    fall = rise + random.randint(300, 3000)
    remnant = generate_remnant(civ_type["type"])
    return {
        "name": civ_name,
        "type": civ_type["type"],
        "traits": civ_type["traits"],
        "founded": rise,
        "collapsed": fall,
        "remnants": remnant,
        "notable_events": [generate_event(civ_name) for _ in range(random.randint(1, 3))]
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
    }
    return patterns.get(civ_type, "Ruins beyond comprehension.")

def generate_name(civ_type):
    prefixes = ["Aeth", "Vor", "Zyn", "Kry", "Lum", "Xha", "Orr", "Thal", "Mir", "Nex"]
    suffixes = ["ari", "oth", "en", "yx", "ion", "ath", "ara", "is", "um", "el"]
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
        for civ in epoch["civilizations"]:
            print(f"  - {civ['name']} ({civ['type']})")
            print(f"    Traits: {', '.join(civ['traits'])}")
            print(f"    Founded: {civ['founded']}, Collapsed: {civ['collapsed']}")
            print(f"    Remnants: {civ['remnants']}")
            for e in civ["notable_events"]:
                print(f"      * {e}")
