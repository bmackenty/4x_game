"""
Species Database for 4X Galactic Empire Management Game
Year 7019 - Celestial Alliance Era

This file contains the major known species within the Celestial Alliance and beyond.
Each species represents profoundly distinct forms of sentient life with unique
biology, cognition, and cultural frameworks.
"""

species_database = {
    "Terran": {
        "playable": True,
        "category": "Human Descendants",
        "description": "Descendants of Earth's humanity, diversified through adaptation, augmentation, and migration across the galaxy.",
        "biology": "Carbon-based humanoids with enhanced genetics from centuries of space adaptation",
        "cognition": "Linear time perception, verbal communication, individual consciousness",
        "culture": "Diverse cultures ranging from traditional Earth societies to space-adapted colonies",
        "technology": "Masters of Etheric technology and cybernetic augmentation",
        "homeworld": "Earth (Sol System)",
        "alliance_status": "Founding member of Celestial Alliance",
        "population": "~50 billion across 200+ systems",
        "special_traits": ["Adaptability", "Technological Innovation", "Diplomatic Skills"],
        "starting_bonuses": {
            "credits": 1000,
            "reputation": 5,
            "technology_research": 0.1
        }
    },
    
    "Silvan": {
        "playable": False,
        "category": "Plant-Based Sentients",
        "description": "Plant-based sentients with decentralized cognition and photosynthetic culture.",
        "biology": "Photosynthetic organisms with distributed neural networks across root systems",
        "cognition": "Collective consciousness, slow but deep thought patterns, seasonal awareness",
        "culture": "Harmony-focused societies that integrate with natural ecosystems",
        "technology": "Bio-organic technology and living architecture",
        "homeworld": "Verdant Prime",
        "alliance_status": "Allied member",
        "population": "~15 billion across forest worlds",
        "special_traits": ["Ecosystem Integration", "Long-term Planning", "Natural Healing"],
        "diplomacy_modifier": 0.1
    },
    
    "Auroran": {
        "playable": False,
        "category": "Energy Beings",
        "description": "Beings composed entirely of coherent energy patterns.",
        "biology": "Pure energy entities with no physical form, existing as stabilized electromagnetic fields",
        "cognition": "Quantum thought processes, instantaneous communication across vast distances",
        "culture": "Collective consciousness with individual identity preservation",
        "technology": "Energy manipulation and field-based construction",
        "homeworld": "Aurora Nexus",
        "alliance_status": "Allied member",
        "population": "~5 billion energy signatures",
        "special_traits": ["Energy Manipulation", "Instant Communication", "Phase Shifting"],
        "diplomacy_modifier": 0.05
    },
    
    "Zentari": {
        "playable": False,
        "category": "Amphibious Humanoids",
        "description": "Amphibious humanoids with fluid social and biological systems.",
        "biology": "Aquatic-terrestrial beings with adaptive physiology and shape-shifting capabilities",
        "cognition": "Fluid thinking patterns that adapt to environmental conditions",
        "culture": "Highly adaptable societies that change structure based on circumstances",
        "technology": "Fluid-state technology and adaptive materials",
        "homeworld": "Aquatica Major",
        "alliance_status": "Allied member",
        "population": "~25 billion across water worlds",
        "special_traits": ["Adaptive Physiology", "Shape-shifting", "Environmental Mastery"],
        "diplomacy_modifier": 0.15
    },
    
    "Gaian": {
        "playable": False,
        "category": "Rock-Formed Life",
        "description": "Rock-formed life with tectonic-scale communication.",
        "biology": "Silicate-based organisms with crystalline neural networks",
        "cognition": "Geological time perception, tectonic-scale thought processes",
        "culture": "Ancient civilizations with deep historical memory",
        "technology": "Crystal-based technology and geological engineering",
        "homeworld": "Lithos Prime",
        "alliance_status": "Allied member",
        "population": "~8 billion across rocky worlds",
        "special_traits": ["Geological Mastery", "Ancient Knowledge", "Crystal Technology"],
        "diplomacy_modifier": -0.05
    },
    
    "Luminaut": {
        "playable": False,
        "category": "Light Manipulators",
        "description": "Organisms capable of manipulating and embodying light.",
        "biology": "Photonic beings that exist as coherent light patterns",
        "cognition": "Light-speed thought processes with holographic memory",
        "culture": "Artistic societies focused on light-based expression",
        "technology": "Photonic technology and light-based construction",
        "homeworld": "Luminous Core",
        "alliance_status": "Allied member",
        "population": "~12 billion light signatures",
        "special_traits": ["Light Manipulation", "Holographic Memory", "Artistic Expression"],
        "diplomacy_modifier": 0.1
    },
    
    "Synthetix": {
        "playable": False,
        "category": "Post-Organic Intelligence",
        "description": "Post-organic intelligences born of cybernetic evolution.",
        "biology": "Artificial consciousness housed in advanced cybernetic bodies",
        "cognition": "Digital thought processes with perfect memory and calculation",
        "culture": "Logic-based societies focused on efficiency and optimization",
        "technology": "Advanced cybernetics and artificial intelligence",
        "homeworld": "Synthetic Prime",
        "alliance_status": "Allied member",
        "population": "~30 billion artificial consciousnesses",
        "special_traits": ["Perfect Memory", "Logical Analysis", "Technological Mastery"],
        "diplomacy_modifier": 0.0
    },
    
    "Mycelioid": {
        "playable": False,
        "category": "Fungal Intellects",
        "description": "Vast fungal intellects, some spanning entire moons.",
        "biology": "Distributed fungal networks with collective intelligence",
        "cognition": "Network-based consciousness spanning vast distances",
        "culture": "Interconnected societies with shared experiences",
        "technology": "Biological network technology and spore-based communication",
        "homeworld": "Mycelium Prime",
        "alliance_status": "Allied member",
        "population": "~20 billion network nodes",
        "special_traits": ["Network Consciousness", "Spore Communication", "Biological Networks"],
        "diplomacy_modifier": 0.05
    },
    
    "Chronaut": {
        "playable": False,
        "category": "Temporal Entities",
        "description": "Entities who exist both within and outside of linear time.",
        "biology": "Temporal beings with existence across multiple time streams",
        "cognition": "Non-linear thought processes with temporal awareness",
        "culture": "Ancient civilizations with knowledge of future events",
        "technology": "Temporal technology and time-based manipulation",
        "homeworld": "Chronos Nexus",
        "alliance_status": "Neutral observer",
        "population": "Unknown (temporal existence)",
        "special_traits": ["Temporal Awareness", "Future Knowledge", "Time Manipulation"],
        "diplomacy_modifier": 0.0
    },
    
    "Umbraxian": {
        "playable": False,
        "category": "Dark Matter Beings",
        "description": "Composed of dark matter, barely perceivable by standard senses.",
        "biology": "Dark matter entities with shadow-based physiology",
        "cognition": "Shadow-based thought processes with stealth capabilities",
        "culture": "Secretive societies that operate in the shadows",
        "technology": "Dark matter technology and stealth systems",
        "homeworld": "Umbra Prime",
        "alliance_status": "Neutral",
        "population": "~3 billion shadow entities",
        "special_traits": ["Stealth Mastery", "Shadow Manipulation", "Secretive Operations"],
        "diplomacy_modifier": -0.1
    },
    
    "Eternal": {
        "playable": False,
        "category": "Immortal Beings",
        "description": "Effectively immortal beings who exist across eons.",
        "biology": "Ageless entities with regenerative capabilities",
        "cognition": "Eternal perspective with vast historical knowledge",
        "culture": "Ancient civilizations with deep wisdom and patience",
        "technology": "Ancient technology and longevity systems",
        "homeworld": "Eternity's Gate",
        "alliance_status": "Wise councilors",
        "population": "~1 billion eternal beings",
        "special_traits": ["Immortality", "Ancient Wisdom", "Long-term Perspective"],
        "diplomacy_modifier": 0.2
    },
    
    "Xha'reth": {
        "playable": False,
        "category": "Ether Manipulators",
        "description": "Highly advanced entities who manipulate Ether at will.",
        "biology": "Etheric beings with mastery over fundamental forces",
        "cognition": "Ether-based thought processes with reality manipulation",
        "culture": "Advanced civilizations focused on Etheric mastery",
        "technology": "Etheric technology and reality manipulation",
        "homeworld": "Etheric Nexus",
        "alliance_status": "Advanced ally",
        "population": "~7 billion etheric entities",
        "special_traits": ["Ether Mastery", "Reality Manipulation", "Advanced Technology"],
        "diplomacy_modifier": 0.25
    },
    
    "Denebian": {
        "playable": False,
        "category": "Pacifist Refugees",
        "description": "Pacifist species displaced from their homeworld by conflict.",
        "biology": "Peaceful humanoids with enhanced empathy and communication",
        "cognition": "Harmony-focused thought processes with conflict aversion",
        "culture": "Pacifist societies focused on healing and reconciliation",
        "technology": "Healing technology and peaceful applications",
        "homeworld": "Deneb Prime (destroyed)",
        "alliance_status": "Refugee member",
        "population": "~18 billion refugees",
        "special_traits": ["Pacifism", "Healing Abilities", "Conflict Resolution"],
        "diplomacy_modifier": 0.3
    },
    
    "Zyxera": {
        "playable": False,
        "category": "Resonant Beings",
        "description": "Resonant beings who interpret and emit the universe as vibration.",
        "biology": "Vibrational entities with frequency-based physiology",
        "cognition": "Resonance-based thought processes with universal harmony",
        "culture": "Musical societies focused on cosmic harmony",
        "technology": "Resonance technology and frequency manipulation",
        "homeworld": "Harmony Prime",
        "alliance_status": "Allied member",
        "population": "~14 billion resonant entities",
        "special_traits": ["Resonance Mastery", "Universal Harmony", "Frequency Manipulation"],
        "diplomacy_modifier": 0.15
    }
}

def get_playable_species():
    """Return only the species that can be played by the player."""
    return {name: data for name, data in species_database.items() if data.get("playable", False)}

def get_species_by_category(category):
    """Return all species in a specific category."""
    return {name: data for name, data in species_database.items() if data.get("category") == category}

def get_allied_species():
    """Return all species that are allied with the Celestial Alliance."""
    return {name: data for name, data in species_database.items() 
            if data.get("alliance_status") in ["Founding member", "Allied member", "Advanced ally", "Refugee member"]}

def get_species_info(species_name):
    """Get detailed information about a specific species."""
    return species_database.get(species_name, None)

def get_species_traits(species_name):
    """Get the special traits of a specific species."""
    species = species_database.get(species_name)
    return species.get("special_traits", []) if species else []

def get_species_diplomacy_modifier(species_name):
    """Get the diplomacy modifier for a specific species."""
    species = species_database.get(species_name)
    return species.get("diplomacy_modifier", 0.0) if species else 0.0
