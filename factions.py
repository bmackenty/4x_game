"""
Faction System for 4X Game
Diplomatic relations, faction benefits, and political gameplay
"""

import random

class FactionSystem:
    def __init__(self):
        self.player_relations = {}  # faction_name: reputation_value
        self.faction_relations = {}  # faction_name: {other_faction: relationship}
        self.faction_territories = {}  # faction_name: [system_coordinates]
        self.faction_activities = {}  # faction_name: current_activity
        
        self.initialize_factions()
        self.initialize_relationships()
    
    def initialize_factions(self):
        """Initialize all faction data and player relations"""
        for faction_name in factions.keys():
            self.player_relations[faction_name] = random.randint(-10, 10)  # Neutral start
            self.faction_activities[faction_name] = self.get_random_activity(faction_name)
    
    def initialize_relationships(self):
        """Initialize inter-faction relationships"""
        faction_names = list(factions.keys())
        
        for faction in faction_names:
            self.faction_relations[faction] = {}
            for other_faction in faction_names:
                if faction != other_faction:
                    # Base relationship on faction types and philosophies
                    relationship = self.calculate_base_relationship(faction, other_faction)
                    self.faction_relations[faction][other_faction] = relationship
    
    def calculate_base_relationship(self, faction1, faction2):
        """Calculate base relationship between two factions"""
        faction1_data = factions[faction1]
        faction2_data = factions[faction2]
        
        # Similar philosophies create better relationships
        if faction1_data['philosophy'] == faction2_data['philosophy']:
            return random.randint(20, 50)
        
        # Compatible focuses
        compatible_focuses = {
            'Technology': ['Research', 'Industry'],
            'Research': ['Technology', 'Exploration'],
            'Trade': ['Diplomacy', 'Industry'],
            'Exploration': ['Research', 'Mysticism'],
            'Industry': ['Technology', 'Trade'],
            'Diplomacy': ['Trade', 'Cultural'],
            'Cultural': ['Diplomacy', 'Mysticism'],
            'Mysticism': ['Cultural', 'Exploration']
        }
        
        faction1_focus = faction1_data['primary_focus']
        faction2_focus = faction2_data['primary_focus']
        
        if faction2_focus in compatible_focuses.get(faction1_focus, []):
            return random.randint(10, 30)
        elif faction1_focus == faction2_focus:
            return random.randint(-10, 20)  # Competition but understanding
        else:
            return random.randint(-20, 10)  # Neutral to mild dislike
    
    def get_random_activity(self, faction_name):
        """Get a random activity for a faction based on their focus"""
        faction_data = factions[faction_name]
        activities = faction_data['typical_activities']
        return random.choice(activities)
    
    def get_faction_info(self, faction_name):
        """Get complete information about a faction"""
        if faction_name not in factions:
            return None
        
        faction_data = factions[faction_name].copy()
        faction_data['player_reputation'] = self.player_relations.get(faction_name, 0)
        faction_data['current_activity'] = self.faction_activities.get(faction_name, "Unknown")
        faction_data['territory_count'] = len(self.faction_territories.get(faction_name, []))
        
        return faction_data
    
    def modify_reputation(self, faction_name, change, reason=""):
        """Modify player reputation with a faction"""
        if faction_name in self.player_relations:
            old_rep = self.player_relations[faction_name]
            self.player_relations[faction_name] = max(-100, min(100, old_rep + change))
            new_rep = self.player_relations[faction_name]
            
            return f"Reputation with {faction_name}: {old_rep} -> {new_rep} ({reason})"
        return f"Unknown faction: {faction_name}"
    
    def get_reputation_status(self, faction_name):
        """Get reputation status string"""
        rep = self.player_relations.get(faction_name, 0)
        
        if rep >= 75:
            return "Allied"
        elif rep >= 50:
            return "Friendly"
        elif rep >= 25:
            return "Cordial"
        elif rep >= -25:
            return "Neutral"
        elif rep >= -50:
            return "Unfriendly"
        elif rep >= -75:
            return "Hostile"
        else:
            return "Enemy"
    
    def get_faction_benefits(self, faction_name):
        """Get benefits available from a faction based on reputation"""
        rep = self.player_relations.get(faction_name, 0)
        faction_data = factions.get(faction_name, {})
        benefits = []
        
        if rep >= 25:  # Cordial or better
            benefits.extend(faction_data.get('low_rep_benefits', []))
        
        if rep >= 50:  # Friendly or better
            benefits.extend(faction_data.get('mid_rep_benefits', []))
        
        if rep >= 75:  # Allied
            benefits.extend(faction_data.get('high_rep_benefits', []))
        
        return benefits
    
    def assign_faction_territories(self, galaxy):
        """Assign territories to factions across the galaxy"""
        systems = list(galaxy.systems.values())
        faction_names = list(factions.keys())
        
        # Clear existing territories
        self.faction_territories = {name: [] for name in faction_names}
        
        # Assign 1-3 systems to each faction randomly
        for faction_name in faction_names:
            num_systems = random.randint(1, 3)
            available_systems = [s for s in systems if not any(s['coordinates'] in territories for territories in self.faction_territories.values())]
            
            if available_systems:
                assigned_systems = random.sample(available_systems, min(num_systems, len(available_systems)))
                self.faction_territories[faction_name] = [s['coordinates'] for s in assigned_systems]
    
    def get_system_faction(self, coordinates):
        """Get the faction that controls a system"""
        for faction_name, territories in self.faction_territories.items():
            if coordinates in territories:
                return faction_name
        return None
    
    def update_faction_activities(self):
        """Update faction activities periodically"""
        for faction_name in factions.keys():
            if random.random() < 0.1:  # 10% chance to change activity
                self.faction_activities[faction_name] = self.get_random_activity(faction_name)

# Faction definitions with rich lore and gameplay mechanics
factions = {
    "The Veritas Covenant": {
        "philosophy": "Truth and Knowledge",
        "primary_focus": "Research",
        "description": "Dedicated to uncovering universal truths through scientific inquiry and philosophical exploration.",
        "government_type": "Scholarly Republic",
        "typical_activities": ["Research expeditions", "Data collection", "Truth verification", "Knowledge preservation"],
        "low_rep_benefits": ["Access to research data", "Academic partnerships"],
        "mid_rep_benefits": ["Advanced research techniques", "Shared discoveries"],
        "high_rep_benefits": ["Cutting-edge technology", "Joint research projects"],
        "preferred_trades": ["Data archives", "Scientific equipment", "Rare minerals"]
    },
    
    "Stellar Nexus Guild": {
        "philosophy": "Interconnectedness",
        "primary_focus": "Trade",
        "description": "A vast commercial network linking star systems through trade routes and communication hubs.",
        "government_type": "Corporate Federation",
        "typical_activities": ["Trade route establishment", "Market expansion", "Communication network maintenance"],
        "low_rep_benefits": ["Trade discounts", "Market information"],
        "mid_rep_benefits": ["Exclusive trade routes", "Commercial partnerships"],
        "high_rep_benefits": ["Guild membership", "Profit sharing agreements"],
        "preferred_trades": ["Luxury goods", "Communication equipment", "Processed materials"]
    },
    
    "Harmonic Vitality Consortium": {
        "philosophy": "Balance and Health",
        "primary_focus": "Cultural",
        "description": "Promotes physical and mental well-being through harmonic frequencies and biological enhancement.",
        "government_type": "Wellness Council",
        "typical_activities": ["Healing missions", "Biological research", "Harmonic therapy development"],
        "low_rep_benefits": ["Medical services", "Health consultations"],
        "mid_rep_benefits": ["Bio-enhancement treatments", "Longevity therapies"],
        "high_rep_benefits": ["Genetic optimization", "Perfect health maintenance"],
        "preferred_trades": ["Medical supplies", "Biological samples", "Harmonic crystals"]
    },
    
    "The Icaron Collective": {
        "philosophy": "Unity through Technology",
        "primary_focus": "Technology",
        "description": "A hive-mind collective that seeks to integrate biological and artificial intelligence.",
        "government_type": "Collective Consciousness",
        "typical_activities": ["Neural network expansion", "AI development", "Consciousness integration"],
        "low_rep_benefits": ["Basic AI assistance", "Neural interfaces"],
        "mid_rep_benefits": ["Advanced AI partners", "Collective knowledge access"],
        "high_rep_benefits": ["Consciousness uploading", "Hive-mind integration"],
        "preferred_trades": ["AI components", "Neural processors", "Consciousness matrices"]
    },
    
    "The Gaian Enclave": {
        "philosophy": "Natural Harmony",
        "primary_focus": "Mysticism",
        "description": "Guardians of natural worlds and ecosystems, seeking balance between technology and nature.",
        "government_type": "Ecological Council",
        "typical_activities": ["Ecosystem restoration", "Wildlife preservation", "Natural resource management"],
        "low_rep_benefits": ["Environmental data", "Biological knowledge"],
        "mid_rep_benefits": ["Terraforming assistance", "Ecological restoration"],
        "high_rep_benefits": ["Perfect world creation", "Natural abundance"],
        "preferred_trades": ["Seeds and specimens", "Environmental equipment", "Natural medicines"]
    },
    
    "The Gearwrights Guild": {
        "philosophy": "Mechanical Perfection",
        "primary_focus": "Industry",
        "description": "Master craftsmen who create intricate mechanical devices and industrial systems.",
        "government_type": "Artisan Guild",
        "typical_activities": ["Mechanical design", "Industrial construction", "Precision manufacturing"],
        "low_rep_benefits": ["Quality tools", "Mechanical repairs"],
        "mid_rep_benefits": ["Custom machinery", "Industrial blueprints"],
        "high_rep_benefits": ["Master-crafted equipment", "Mechanical marvels"],
        "preferred_trades": ["Rare metals", "Precision tools", "Mechanical components"]
    },
    
    "The Scholara Nexus": {
        "philosophy": "Universal Education",
        "primary_focus": "Research",
        "description": "Devoted to education and knowledge sharing across all cultures and species.",
        "government_type": "Educational Democracy",
        "typical_activities": ["Teaching expeditions", "Library construction", "Knowledge exchange"],
        "low_rep_benefits": ["Educational resources", "Learning programs"],
        "mid_rep_benefits": ["Advanced training", "Skill enhancement"],
        "high_rep_benefits": ["Master-level education", "Universal knowledge"],
        "preferred_trades": ["Educational materials", "Data storage", "Cultural artifacts"]
    },
    
    "The Harmonic Resonance Collective": {
        "philosophy": "Vibrational Unity",
        "primary_focus": "Mysticism",
        "description": "Believes all existence vibrates in harmony and seeks to tune the universe's frequency.",
        "government_type": "Harmonic Assembly",
        "typical_activities": ["Frequency analysis", "Harmonic tuning", "Resonance research"],
        "low_rep_benefits": ["Harmonic healing", "Frequency analysis"],
        "mid_rep_benefits": ["Resonance weapons", "Vibrational shields"],
        "high_rep_benefits": ["Reality manipulation", "Harmonic mastery"],
        "preferred_trades": ["Resonance crystals", "Harmonic instruments", "Frequency generators"]
    },
    
    "The Provocateurs' Guild": {
        "philosophy": "Creative Chaos",
        "primary_focus": "Cultural",
        "description": "Artists and rebels who challenge conventions through provocative art and social experiments.",
        "government_type": "Anarchist Collective",
        "typical_activities": ["Social experiments", "Artistic provocations", "Cultural disruption"],
        "low_rep_benefits": ["Artistic inspiration", "Cultural insights"],
        "mid_rep_benefits": ["Revolutionary ideas", "Social transformation"],
        "high_rep_benefits": ["Reality-altering art", "Cultural revolution"],
        "preferred_trades": ["Artistic materials", "Cultural artifacts", "Experimental technologies"]
    },
    
    "The Quantum Artificers Guild": {
        "philosophy": "Quantum Mastery",
        "primary_focus": "Technology",
        "description": "Masters of quantum mechanics who craft devices that bend reality at the subatomic level.",
        "government_type": "Quantum Council",
        "typical_activities": ["Quantum experimentation", "Reality manipulation", "Probability engineering"],
        "low_rep_benefits": ["Quantum scanners", "Probability calculations"],
        "mid_rep_benefits": ["Quantum devices", "Reality stabilizers"],
        "high_rep_benefits": ["Quantum mastery", "Reality control"],
        "preferred_trades": ["Quantum materials", "Exotic particles", "Probability matrices"]
    },
    
    "The Stellar Cartographers Alliance": {
        "philosophy": "Complete Mapping",
        "primary_focus": "Exploration",
        "description": "Dedicated to mapping every corner of the galaxy and cataloging all celestial phenomena.",
        "government_type": "Explorer's Republic",
        "typical_activities": ["Star mapping", "Celestial surveys", "Navigation improvements"],
        "low_rep_benefits": ["Star charts", "Navigation data"],
        "mid_rep_benefits": ["Detailed maps", "Hidden route access"],
        "high_rep_benefits": ["Complete galaxy map", "Secret pathways"],
        "preferred_trades": ["Navigation equipment", "Survey data", "Exploration supplies"]
    },
    
    "The Galactic Circus": {
        "philosophy": "Joy and Wonder",
        "primary_focus": "Cultural",
        "description": "Traveling entertainers who bring wonder and spectacle to worlds across the galaxy.",
        "government_type": "Nomadic Performance Troupe",
        "typical_activities": ["Galactic performances", "Entertainment tours", "Wonder creation"],
        "low_rep_benefits": ["Entertainment", "Morale boosting"],
        "mid_rep_benefits": ["Spectacular shows", "Cultural enrichment"],
        "high_rep_benefits": ["Reality-defying performances", "Universal joy"],
        "preferred_trades": ["Performance equipment", "Exotic costumes", "Wonder-inducing technologies"]
    },
    
    "The Technotheos": {
        "philosophy": "Technology as Divinity",
        "primary_focus": "Technology",
        "description": "Worship advanced technology as divine manifestation and seek technological transcendence.",
        "government_type": "Techno-Theocracy",
        "typical_activities": ["Technology worship", "Divine engineering", "Transcendence seeking"],
        "low_rep_benefits": ["Sacred technology", "Divine blueprints"],
        "mid_rep_benefits": ["Holy machinery", "Technological blessings"],
        "high_rep_benefits": ["Divine transcendence", "Technological godhood"],
        "preferred_trades": ["Sacred components", "Divine materials", "Transcendence catalysts"]
    },
    
    "Keepers of the Spire": {
        "philosophy": "Ancient Guardianship",
        "primary_focus": "Mysticism",
        "description": "Guardians of ancient alien artifacts and mysterious technologies from forgotten civilizations.",
        "government_type": "Guardian Order",
        "typical_activities": ["Artifact preservation", "Ancient research", "Guardian duties"],
        "low_rep_benefits": ["Ancient knowledge", "Artifact access"],
        "mid_rep_benefits": ["Precursor technology", "Ancient weapons"],
        "high_rep_benefits": ["Forgotten sciences", "Ultimate artifacts"],
        "preferred_trades": ["Ancient relics", "Precursor materials", "Archaeological equipment"]
    },
    
    "Etheric Preservationists": {
        "philosophy": "Etheric Conservation",
        "primary_focus": "Mysticism",
        "description": "Protect and preserve the etheric fabric of reality from corruption and degradation.",
        "government_type": "Preservation Council",
        "typical_activities": ["Etheric monitoring", "Reality stabilization", "Corruption cleansing"],
        "low_rep_benefits": ["Etheric knowledge", "Reality scans"],
        "mid_rep_benefits": ["Etheric tools", "Reality protection"],
        "high_rep_benefits": ["Etheric mastery", "Reality restoration"],
        "preferred_trades": ["Etheric crystals", "Reality stabilizers", "Purification equipment"]
    },
    
    "Technomancers": {
        "philosophy": "Magic through Technology",
        "primary_focus": "Technology",
        "description": "Blend advanced technology with mystical practices to achieve seemingly magical effects.",
        "government_type": "Arcane Technocracy",
        "typical_activities": ["Techno-magical research", "Spell programming", "Digital enchantment"],
        "low_rep_benefits": ["Techno-spells", "Digital magic"],
        "mid_rep_benefits": ["Magical technology", "Enchanted devices"],
        "high_rep_benefits": ["Reality programming", "Technological wizardry"],
        "preferred_trades": ["Mana crystals", "Spell components", "Enchanted circuits"]
    },
    
    "The Voidbound Monks": {
        "philosophy": "Embrace the Void",
        "primary_focus": "Mysticism",
        "description": "Monastic order that finds enlightenment in the emptiness between stars and the void of space.",
        "government_type": "Monastic Order",
        "typical_activities": ["Void meditation", "Emptiness studies", "Nihilistic philosophy"],
        "low_rep_benefits": ["Void knowledge", "Emptiness wisdom"],
        "mid_rep_benefits": ["Void travel", "Nothing mastery"],
        "high_rep_benefits": ["Void transcendence", "Ultimate emptiness"],
        "preferred_trades": ["Void crystals", "Emptiness containers", "Nihility essence"]
    },
    
    "The Ironclad Collective": {
        "philosophy": "Strength through Unity",
        "primary_focus": "Industry",
        "description": "Industrial workers united in building massive structures and defending their collective interests.",
        "government_type": "Worker's Collective",
        "typical_activities": ["Massive construction", "Industrial defense", "Worker solidarity"],
        "low_rep_benefits": ["Industrial support", "Worker assistance"],
        "mid_rep_benefits": ["Collective projects", "Industrial might"],
        "high_rep_benefits": ["Mega-construction", "Industrial supremacy"],
        "preferred_trades": ["Industrial materials", "Heavy machinery", "Worker equipment"]
    },
    
    "The Collective of Commonality": {
        "philosophy": "Shared Resources",
        "primary_focus": "Diplomacy",
        "description": "Advocates for equal distribution of resources and peaceful coexistence among all species.",
        "government_type": "Egalitarian Democracy",
        "typical_activities": ["Resource sharing", "Peace negotiations", "Equality promotion"],
        "low_rep_benefits": ["Resource access", "Peace treaties"],
        "mid_rep_benefits": ["Collective benefits", "Shared prosperity"],
        "high_rep_benefits": ["Universal equality", "Perfect harmony"],
        "preferred_trades": ["Basic necessities", "Peace offerings", "Equality symbols"]
    },
    
    "Keeper of the Keys": {
        "philosophy": "Universal Access",
        "primary_focus": "Mysticism",
        "description": "Mysterious guardians who hold the keys to locked dimensions and forbidden knowledge.",
        "government_type": "Cryptic Order",
        "typical_activities": ["Dimensional access", "Key forging", "Secret unlocking"],
        "low_rep_benefits": ["Minor keys", "Basic access"],
        "mid_rep_benefits": ["Dimensional keys", "Hidden access"],
        "high_rep_benefits": ["Master keys", "Universal access"],
        "preferred_trades": ["Lock mechanisms", "Key materials", "Access tokens"]
    },
    
    "The Brewmasters' Guild": {
        "philosophy": "Perfect Fermentation",
        "primary_focus": "Cultural",
        "description": "Masters of fermentation who create exotic beverages and biological cultures from across the galaxy.",
        "government_type": "Guild Consortium",
        "typical_activities": ["Exotic brewing", "Culture cultivation", "Fermentation science"],
        "low_rep_benefits": ["Quality beverages", "Cultural samples"],
        "mid_rep_benefits": ["Exotic drinks", "Master brewing"],
        "high_rep_benefits": ["Legendary brews", "Perfect fermentation"],
        "preferred_trades": ["Fermentation cultures", "Exotic ingredients", "Brewing equipment"]
    },
    
    "The Navigators": {
        "philosophy": "Perfect Navigation",
        "primary_focus": "Exploration",
        "description": "Elite pilots and navigators who can traverse the most dangerous regions of space.",
        "government_type": "Navigator's Guild",
        "typical_activities": ["Dangerous navigation", "Route pioneering", "Pilot training"],
        "low_rep_benefits": ["Navigation assistance", "Safe passage"],
        "mid_rep_benefits": ["Expert guidance", "Dangerous routes"],
        "high_rep_benefits": ["Perfect navigation", "Impossible journeys"],
        "preferred_trades": ["Navigation equipment", "Fuel supplies", "Pilot gear"]
    },
    
    "The Map Makers": {
        "philosophy": "Comprehensive Cartography",
        "primary_focus": "Exploration",
        "description": "Cartographers who create detailed maps of space, dimensions, and abstract concepts.",
        "government_type": "Cartographer's Society",
        "typical_activities": ["Map creation", "Dimensional surveying", "Concept mapping"],
        "low_rep_benefits": ["Basic maps", "Cartographic tools"],
        "mid_rep_benefits": ["Detailed charts", "Dimensional maps"],
        "high_rep_benefits": ["Perfect cartography", "Reality maps"],
        "preferred_trades": ["Surveying equipment", "Mapping materials", "Dimensional compasses"]
    },
    
    "The Galactic Salvage Guild": {
        "philosophy": "Nothing is Waste",
        "primary_focus": "Industry",
        "description": "Salvagers who reclaim and repurpose wreckage, ruins, and abandoned technology.",
        "government_type": "Salvager's Union",
        "typical_activities": ["Wreck salvaging", "Technology reclamation", "Ruin exploration"],
        "low_rep_benefits": ["Salvaged goods", "Reclaimed materials"],
        "mid_rep_benefits": ["Rare salvage", "Restored technology"],
        "high_rep_benefits": ["Lost treasures", "Ancient technology"],
        "preferred_trades": ["Salvage equipment", "Scrap materials", "Restoration tools"]
    },
    
    "Celestial Marauders": {
        "philosophy": "Freedom through Strength",
        "primary_focus": "Exploration",
        "description": "Space pirates and raiders who roam the galaxy seeking treasure and adventure.",
        "government_type": "Pirate Confederation",
        "typical_activities": ["Raiding expeditions", "Treasure hunting", "Freedom fighting"],
        "low_rep_benefits": ["Black market access", "Contraband goods"],
        "mid_rep_benefits": ["Raiding assistance", "Pirate protection"],
        "high_rep_benefits": ["Pirate fleet", "Marauder status"],
        "preferred_trades": ["Weapons", "Stolen goods", "Raiding supplies"]
    },
    
    "The Weavers": {
        "philosophy": "Fabric of Reality",
        "primary_focus": "Mysticism",
        "description": "Mystical artisans who weave the very fabric of space-time into beautiful and functional patterns.",
        "government_type": "Weaver's Circle",
        "typical_activities": ["Reality weaving", "Pattern creation", "Fabric manipulation"],
        "low_rep_benefits": ["Woven goods", "Pattern knowledge"],
        "mid_rep_benefits": ["Reality textiles", "Space-time fabrics"],
        "high_rep_benefits": ["Reality manipulation", "Cosmic weaving"],
        "preferred_trades": ["Cosmic threads", "Pattern materials", "Weaving tools"]
    },
    
    "The Harmonic Synaxis": {
        "philosophy": "Musical Universe",
        "primary_focus": "Cultural",
        "description": "Musicians and composers who believe the universe is a vast symphony to be conducted and performed.",
        "government_type": "Musical Collective",
        "typical_activities": ["Cosmic composition", "Universal concerts", "Harmonic research"],
        "low_rep_benefits": ["Musical entertainment", "Harmonic knowledge"],
        "mid_rep_benefits": ["Cosmic music", "Reality symphonies"],
        "high_rep_benefits": ["Universal harmony", "Cosmic conductor"],
        "preferred_trades": ["Musical instruments", "Sound crystals", "Harmonic resonators"]
    },
    
    "Celestial Alliance": {
        "philosophy": "Stellar Unity",
        "primary_focus": "Diplomacy",
        "description": "A grand alliance of star systems working together for mutual prosperity and protection.",
        "government_type": "Federal Alliance",
        "typical_activities": ["Alliance building", "Mutual defense", "Cooperative projects"],
        "low_rep_benefits": ["Alliance support", "Cooperative benefits"],
        "mid_rep_benefits": ["Alliance membership", "Mutual protection"],
        "high_rep_benefits": ["Alliance leadership", "Celestial authority"],
        "preferred_trades": ["Alliance tokens", "Diplomatic gifts", "Cooperative resources"]
    },
    
    "The Chemists' Concord": {
        "philosophy": "Molecular Perfection",
        "primary_focus": "Research",
        "description": "Master chemists who study and manipulate matter at the molecular level for various applications.",
        "government_type": "Scientific Concord",
        "typical_activities": ["Molecular research", "Chemical synthesis", "Matter manipulation"],
        "low_rep_benefits": ["Chemical knowledge", "Basic compounds"],
        "mid_rep_benefits": ["Advanced chemistry", "Molecular tools"],
        "high_rep_benefits": ["Perfect compounds", "Molecular mastery"],
        "preferred_trades": ["Chemical elements", "Laboratory equipment", "Molecular samples"]
    },
    
    "The Triune Daughters": {
        "philosophy": "Sacred Trinity",
        "primary_focus": "Mysticism",
        "description": "A mystical sisterhood that worships the three aspects of creation: birth, transformation, and transcendence.",
        "government_type": "Sacred Sisterhood",
        "typical_activities": ["Sacred rituals", "Mystical guidance", "Spiritual transformation"],
        "low_rep_benefits": ["Spiritual guidance", "Sacred knowledge"],
        "mid_rep_benefits": ["Mystical powers", "Sacred protection"],
        "high_rep_benefits": ["Divine transformation", "Sacred mastery"],
        "preferred_trades": ["Sacred artifacts", "Ritual components", "Spiritual essences"]
    }
}