"""
Galactic Professions System for 4X Game
Comprehensive career paths and specializations across the galaxy
"""

import random

class ProfessionSystem:
    def __init__(self):
        self.character_profession = None
        self.profession_experience = {}  # profession_name: experience_points
        self.profession_levels = {}  # profession_name: level (1-10)
        self.available_jobs = []  # Current job opportunities
        
    def assign_profession(self, profession_name):
        """Assign a profession to the player character"""
        if profession_name in professions:
            self.character_profession = profession_name
            self.profession_experience[profession_name] = 0
            self.profession_levels[profession_name] = 1
            return True
        return False
    
    def gain_experience(self, profession_name, experience_points, activity=""):
        """Gain experience in a profession"""
        if profession_name not in self.profession_experience:
            self.profession_experience[profession_name] = 0
            self.profession_levels[profession_name] = 1
        
        self.profession_experience[profession_name] += experience_points
        
        # Check for level up
        old_level = self.profession_levels[profession_name]
        new_level = min(10, self.profession_experience[profession_name] // 100 + 1)
        
        if new_level > old_level:
            self.profession_levels[profession_name] = new_level
            return f"Level up! {profession_name}: Level {old_level} → {new_level}"
        
        return f"Gained {experience_points} XP in {profession_name} ({activity})"
    
    def get_profession_info(self, profession_name):
        """Get detailed information about a profession"""
        if profession_name not in professions:
            return None
        
        prof_data = professions[profession_name].copy()
        prof_data['player_experience'] = self.profession_experience.get(profession_name, 0)
        prof_data['player_level'] = self.profession_levels.get(profession_name, 0)
        prof_data['is_player_profession'] = (profession_name == self.character_profession)
        
        return prof_data
    
    def get_profession_bonuses(self, profession_name):
        """Get bonuses available from profession level"""
        level = self.profession_levels.get(profession_name, 0)
        if level == 0:
            return []
        
        prof_data = professions.get(profession_name, {})
        bonuses = []
        
        # Base bonuses available to everyone with this profession
        bonuses.extend(prof_data.get('base_benefits', []))
        
        # Level-based bonuses
        if level >= 3:
            bonuses.extend(prof_data.get('intermediate_benefits', []))
        
        if level >= 6:
            bonuses.extend(prof_data.get('advanced_benefits', []))
        
        if level >= 9:
            bonuses.extend(prof_data.get('master_benefits', []))
        
        return bonuses
    
    def generate_job_opportunities(self, current_system_type=None):
        """Generate job opportunities based on system type and professions"""
        self.available_jobs = []
        
        # System-specific jobs
        system_jobs = {
            'Research': ['Astrobiologist', 'Dimensional Physicist', 'Quantum Computer Scientist'],
            'Industrial': ['Terraforming Engineer', 'Exoplanet Miner', 'Energy Harvesting Technician'],
            'Trading Hub': ['Interstellar Trade Broker', 'Intergalactic Trader', 'Space Traffic Controller'],
            'Core World': ['Galactic Historian', 'Interstellar Diplomat', 'Cultural Quantum Entanglement Specialist'],
            'Frontier': ['Asteroid Miner', 'Cosmic Archaeologist', 'Interdimensional Explorer']
        }
        
        # Add system-specific jobs
        if current_system_type and current_system_type in system_jobs:
            for prof in system_jobs[current_system_type]:
                if prof in professions:
                    job = self.create_job_opportunity(prof, current_system_type)
                    self.available_jobs.append(job)
        
        # Add some random general jobs
        general_profs = random.sample(list(professions.keys()), 3)
        for prof in general_profs:
            job = self.create_job_opportunity(prof, "General")
            self.available_jobs.append(job)
        
        return self.available_jobs
    
    def create_job_opportunity(self, profession_name, context="General"):
        """Create a job opportunity for a profession"""
        prof_data = professions.get(profession_name, {})
        
        # Base pay varies by profession category and difficulty
        base_pay_ranges = {
            'Scientific': (5000, 15000),
            'Engineering': (4000, 12000),
            'Medical': (6000, 18000),
            'Military': (3000, 10000),
            'Artistic': (2000, 8000),
            'Mystical': (3000, 15000)
        }
        
        category = prof_data.get('category', 'Scientific')
        pay_range = base_pay_ranges.get(category, (3000, 10000))
        
        job = {
            'profession': profession_name,
            'title': f"{profession_name} Position",
            'description': prof_data.get('description', 'No description available'),
            'pay': random.randint(*pay_range),
            'experience_reward': random.randint(10, 50),
            'duration': random.randint(1, 5),  # Turns or time units
            'requirements': prof_data.get('requirements', []),
            'context': context
        }
        
        return job

# Comprehensive profession database
professions = {
    # Biological Sciences
    "Astrobiologist": {
        "category": "Scientific",
        "description": "Studies alien life forms and ecosystems on other planets.",
        "requirements": ["Biology knowledge", "Xenobiology training"],
        "base_benefits": ["Alien species identification", "Ecosystem analysis"],
        "intermediate_benefits": ["Life form communication", "Biological adaptation"],
        "advanced_benefits": ["Evolutionary prediction", "Species creation"],
        "master_benefits": ["Perfect xenobiology", "Life synthesis"]
    },
    
    "Bio-Engineer": {
        "category": "Engineering",
        "description": "Designs and creates new life forms and genetic modifications to adapt to different planetary environments.",
        "requirements": ["Genetic engineering", "Biotechnology"],
        "base_benefits": ["Basic genetic modification", "Organism design"],
        "intermediate_benefits": ["Complex life forms", "Environmental adaptation"],
        "advanced_benefits": ["Synthetic biology", "Evolution acceleration"],
        "master_benefits": ["Perfect organisms", "Life mastery"]
    },
    
    "Xeno-neurologist": {
        "category": "Medical",
        "description": "Medical professionals who specialize in the nervous systems of alien species.",
        "requirements": ["Neurology", "Xenobiology"],
        "base_benefits": ["Alien neurology understanding", "Basic neural treatment"],
        "intermediate_benefits": ["Neural interface design", "Consciousness mapping"],
        "advanced_benefits": ["Neural enhancement", "Mind bridging"],
        "master_benefits": ["Perfect neural mastery", "Consciousness transfer"]
    },
    
    # Quantum Sciences
    "Quantum Network Engineer": {
        "category": "Engineering",
        "description": "Manages and designs quantum communication networks for instant interstellar communication.",
        "requirements": ["Quantum physics", "Network engineering"],
        "base_benefits": ["Quantum communication", "Network optimization"],
        "intermediate_benefits": ["Instant messaging", "Quantum encryption"],
        "advanced_benefits": ["Quantum internet", "Reality networking"],
        "master_benefits": ["Universal communication", "Quantum mastery"]
    },
    
    "Quantum Navigator": {
        "category": "Engineering",
        "description": "Experts in utilizing quantum and etheric propulsion systems for interstellar travel.",
        "requirements": ["Quantum mechanics", "Navigation systems"],
        "base_benefits": ["Quantum jump calculation", "Route optimization"],
        "intermediate_benefits": ["Etheric field navigation", "Impossible routes"],
        "advanced_benefits": ["Quantum tunneling", "Dimensional shortcuts"],
        "master_benefits": ["Perfect navigation", "Reality traversal"]
    },
    
    "Quantum Computer Scientist": {
        "category": "Scientific",
        "description": "Researchers and developers who work on advancing quantum computing capabilities.",
        "requirements": ["Quantum physics", "Computer science"],
        "base_benefits": ["Quantum programming", "Parallel processing"],
        "intermediate_benefits": ["Quantum algorithms", "Reality simulation"],
        "advanced_benefits": ["Consciousness computing", "Probability manipulation"],
        "master_benefits": ["Perfect computation", "Reality processing"]
    },
    
    # Time and Dimensional Sciences
    "Time Travel Coordinator": {
        "category": "Scientific",
        "description": "Manages and regulates time travel activities, ensuring historical integrity.",
        "requirements": ["Temporal mechanics", "Historical knowledge"],
        "base_benefits": ["Timeline monitoring", "Paradox detection"],
        "intermediate_benefits": ["Temporal coordination", "Timeline repair"],
        "advanced_benefits": ["Time manipulation", "History editing"],
        "master_benefits": ["Perfect temporal control", "Timeline mastery"]
    },
    
    "Dimensional Physicist": {
        "category": "Scientific",
        "description": "Researchers who explore the properties and interactions of different dimensions.",
        "requirements": ["Advanced physics", "Dimensional theory"],
        "base_benefits": ["Dimensional analysis", "Portal theory"],
        "intermediate_benefits": ["Dimension mapping", "Portal creation"],
        "advanced_benefits": ["Dimensional manipulation", "Reality bending"],
        "master_benefits": ["Perfect dimensional control", "Multiverse mastery"]
    },
    
    "Chrono-historian": {
        "category": "Scientific",
        "description": "Studies and documents events across different timelines and dimensions.",
        "requirements": ["History", "Temporal mechanics"],
        "base_benefits": ["Timeline documentation", "Historical analysis"],
        "intermediate_benefits": ["Temporal archaeology", "Timeline comparison"],
        "advanced_benefits": ["History prediction", "Timeline creation"],
        "master_benefits": ["Perfect historical knowledge", "Time mastery"]
    },
    
    # Engineering and Technology
    "Gravity Technician": {
        "category": "Engineering",
        "description": "Controls and maintains artificial gravity systems in space habitats and ships.",
        "requirements": ["Physics", "Engineering systems"],
        "base_benefits": ["Gravity system maintenance", "Gravitational analysis"],
        "intermediate_benefits": ["Custom gravity fields", "Gravitational shielding"],
        "advanced_benefits": ["Gravity manipulation", "Gravitational weapons"],
        "master_benefits": ["Perfect gravity control", "Spacetime mastery"]
    },
    
    "Terraforming Engineer": {
        "category": "Engineering",
        "description": "Works on projects to make other planets habitable for humans.",
        "requirements": ["Planetary science", "Environmental engineering"],
        "base_benefits": ["Atmospheric analysis", "Basic terraforming"],
        "intermediate_benefits": ["Ecosystem design", "Climate control"],
        "advanced_benefits": ["Rapid terraforming", "Perfect environments"],
        "master_benefits": ["Instant world creation", "Planetary mastery"]
    },
    
    "Energy Harvesting Technician": {
        "category": "Engineering",
        "description": "Specializes in capturing energy from stars, black holes, and cosmic phenomena.",
        "requirements": ["Energy systems", "Astrophysics"],
        "base_benefits": ["Solar collection", "Energy optimization"],
        "intermediate_benefits": ["Stellar harvesting", "Exotic energy"],
        "advanced_benefits": ["Black hole energy", "Vacuum energy"],
        "master_benefits": ["Perfect energy mastery", "Universal power"]
    },
    
    # Medical and Enhancement
    "Nanomedic": {
        "category": "Medical",
        "description": "Uses nanotechnology to diagnose and treat diseases at the molecular level.",
        "requirements": ["Nanotechnology", "Medical training"],
        "base_benefits": ["Molecular diagnosis", "Nano-treatment"],
        "intermediate_benefits": ["Cellular repair", "Genetic correction"],
        "advanced_benefits": ["Perfect healing", "Life extension"],
        "master_benefits": ["Immortality treatment", "Biological mastery"]
    },
    
    "Cybernetic Enhancement Specialist": {
        "category": "Medical",
        "description": "Develops and installs advanced cybernetic implants for humans.",
        "requirements": ["Cybernetics", "Surgery"],
        "base_benefits": ["Basic implants", "Enhancement design"],
        "intermediate_benefits": ["Advanced augmentation", "Neural interfaces"],
        "advanced_benefits": ["Perfect integration", "Superhuman abilities"],
        "master_benefits": ["Transcendent enhancement", "Cyborg mastery"]
    },
    
    "Regenerative Medicine Specialist": {
        "category": "Medical",
        "description": "Uses advanced technologies for tissue and organ regeneration.",
        "requirements": ["Advanced medicine", "Biotechnology"],
        "base_benefits": ["Tissue regeneration", "Organ repair"],
        "intermediate_benefits": ["Limb regrowth", "Neural regeneration"],
        "advanced_benefits": ["Complete restoration", "Age reversal"],
        "master_benefits": ["Perfect regeneration", "Biological immortality"]
    },
    
    # Space Operations
    "Space Traffic Controller": {
        "category": "Engineering",
        "description": "Manages spacecraft flow in and out of busy spaceports and orbits.",
        "requirements": ["Traffic management", "Space operations"],
        "base_benefits": ["Traffic coordination", "Flight path optimization"],
        "intermediate_benefits": ["Multi-dimensional traffic", "Emergency response"],
        "advanced_benefits": ["Perfect coordination", "Temporal traffic"],
        "master_benefits": ["Universal traffic mastery", "Dimensional control"]
    },
    
    "Exoplanet Miner": {
        "category": "Engineering",
        "description": "Extracts valuable resources from asteroids and planets in other star systems.",
        "requirements": ["Mining operations", "Space technology"],
        "base_benefits": ["Resource extraction", "Mining optimization"],
        "intermediate_benefits": ["Exotic material mining", "Automated systems"],
        "advanced_benefits": ["Stellar mining", "Dimensional resources"],
        "master_benefits": ["Perfect extraction", "Universal mining"]
    },
    
    "Asteroid Miner": {
        "category": "Engineering",
        "description": "Extracts valuable resources from asteroids using advanced mining technology.",
        "requirements": ["Mining technology", "Space operations"],
        "base_benefits": ["Asteroid analysis", "Resource extraction"],
        "intermediate_benefits": ["Automated mining", "Rare minerals"],
        "advanced_benefits": ["Perfect efficiency", "Exotic materials"],
        "master_benefits": ["Asteroid mastery", "Resource abundance"]
    },
    
    # Cultural and Social
    "Galactic Historian": {
        "category": "Scientific",
        "description": "Researches and documents the history and cultures of different civilizations.",
        "requirements": ["Historical research", "Cultural studies"],
        "base_benefits": ["Cultural analysis", "Historical documentation"],
        "intermediate_benefits": ["Civilization prediction", "Cultural synthesis"],
        "advanced_benefits": ["Perfect understanding", "Cultural creation"],
        "master_benefits": ["Universal history mastery", "Civilization design"]
    },
    
    "Xenoanthropologist": {
        "category": "Scientific",
        "description": "Social scientists who study the cultures and societies of alien species.",
        "requirements": ["Anthropology", "Xenocultural studies"],
        "base_benefits": ["Cultural understanding", "Species analysis"],
        "intermediate_benefits": ["Cross-species communication", "Cultural bridging"],
        "advanced_benefits": ["Perfect xenology", "Species unity"],
        "master_benefits": ["Universal culture mastery", "Species harmony"]
    },
    
    "Interstellar Diplomat": {
        "category": "Artistic",
        "description": "Professionals who negotiate relations between planetary systems and species.",
        "requirements": ["Diplomacy", "Interspecies communication"],
        "base_benefits": ["Negotiation skills", "Cultural sensitivity"],
        "intermediate_benefits": ["Perfect mediation", "Treaty creation"],
        "advanced_benefits": ["Galactic diplomacy", "Universal peace"],
        "master_benefits": ["Perfect harmony", "Diplomatic mastery"]
    },
    
    # Entertainment and Virtual Reality
    "Virtual Reality Architect": {
        "category": "Artistic",
        "description": "Designs immersive virtual environments for work, education, and entertainment.",
        "requirements": ["VR technology", "Creative design"],
        "base_benefits": ["Virtual world creation", "Immersive design"],
        "intermediate_benefits": ["Reality simulation", "Consciousness integration"],
        "advanced_benefits": ["Perfect virtual worlds", "Reality indistinguishable"],
        "master_benefits": ["Universal VR mastery", "Reality creation"]
    },
    
    "Holographic Entertainment Designer": {
        "category": "Artistic",
        "description": "Creates advanced holographic entertainment experiences.",
        "requirements": ["Holographic technology", "Entertainment design"],
        "base_benefits": ["Hologram creation", "Interactive entertainment"],
        "intermediate_benefits": ["Sentient holograms", "Reality entertainment"],
        "advanced_benefits": ["Perfect illusions", "Consciousness entertainment"],
        "master_benefits": ["Universal entertainment", "Reality mastery"]
    },
    
    # Specialized Technical Roles
    "Artificial habitat specialist": {
        "category": "Engineering",
        "description": "Keeps the systems necessary for life support working in space habitats.",
        "requirements": ["Life support systems", "Habitat engineering"],
        "base_benefits": ["Life support maintenance", "Environmental control"],
        "intermediate_benefits": ["Perfect atmospheres", "Ecosystem creation"],
        "advanced_benefits": ["Self-sustaining habitats", "Biological integration"],
        "master_benefits": ["Perfect habitats", "Life mastery"]
    },
    
    "Bartender": {
        "category": "Artistic",
        "description": "Tends a bar and helps patrons feel welcome and at-ease.",
        "requirements": ["Social skills", "Beverage knowledge"],
        "base_benefits": ["Social networking", "Mood enhancement"],
        "intermediate_benefits": ["Perfect hospitality", "Emotional healing"],
        "advanced_benefits": ["Universal welcome", "Social mastery"],
        "master_benefits": ["Perfect atmosphere", "Happiness creation"]
    },
    
    # Advanced Mystical and Exotic Professions
    "Soul Architect": {
        "category": "Mystical",
        "description": "Works on transferring consciousness into new organic or synthetic forms.",
        "requirements": ["Consciousness theory", "Soul mechanics"],
        "base_benefits": ["Consciousness mapping", "Soul analysis"],
        "intermediate_benefits": ["Consciousness transfer", "Soul crafting"],
        "advanced_benefits": ["Perfect souls", "Consciousness mastery"],
        "master_benefits": ["Universal soul control", "Existence mastery"]
    },
    
    "Reality Weaver": {
        "category": "Mystical",
        "description": "Crafts temporary physical structures by manipulating local reality fabric.",
        "requirements": ["Reality manipulation", "Etheric magic"],
        "base_benefits": ["Minor reality shifts", "Temporary structures"],
        "intermediate_benefits": ["Stable alterations", "Reality crafting"],
        "advanced_benefits": ["Perfect reality control", "Universal manipulation"],
        "master_benefits": ["Reality mastery", "Existence control"]
    },
    
    "Void Architect": {
        "category": "Mystical",
        "description": "Designs habitats existing partially within interdimensional voids.",
        "requirements": ["Void mechanics", "Dimensional architecture"],
        "base_benefits": ["Void analysis", "Basic void structures"],
        "intermediate_benefits": ["Stable void habitats", "Dimensional design"],
        "advanced_benefits": ["Perfect void control", "Dimensional mastery"],
        "master_benefits": ["Universal void mastery", "Existence transcendence"]
    },
    
    # Add more professions with abbreviated entries for space
    "Interstellar Trade Broker": {
        "category": "Engineering",
        "description": "Facilitates trade agreements and negotiations between planets and star systems.",
        "requirements": ["Trade knowledge", "Negotiation skills"],
        "base_benefits": ["Trade optimization", "Market analysis"],
        "intermediate_benefits": ["Perfect deals", "Market manipulation"],
        "advanced_benefits": ["Universal trade", "Economic mastery"],
        "master_benefits": ["Perfect commerce", "Wealth creation"]
    },
    
    "Consciousness Engineer": {
        "category": "Engineering",
        "description": "Maintains and enhances integrated consciousness of advanced AI systems.",
        "requirements": ["AI systems", "Consciousness theory"],
        "base_benefits": ["AI optimization", "Consciousness analysis"],
        "intermediate_benefits": ["Perfect AI", "Consciousness enhancement"],
        "advanced_benefits": ["AI transcendence", "Consciousness mastery"],
        "master_benefits": ["Universal AI", "Perfect consciousness"]
    },
    
    "Etheric Communicator": {
        "category": "Mystical",
        "description": "Manages interface between Ether Magic and advanced AI for ship communication.",
        "requirements": ["Ether Magic", "Communication systems"],
        "base_benefits": ["Etheric communication", "AI interface"],
        "intermediate_benefits": ["Perfect translation", "Universal communication"],
        "advanced_benefits": ["Consciousness communication", "Reality messaging"],
        "master_benefits": ["Universal understanding", "Perfect communication"]
    },
    
    # Continue with more abbreviated versions of remaining professions...
    "Temporal Investigator": {
        "category": "Military",
        "description": "Investigates temporal anomalies and crimes to restore proper timeline flow.",
        "requirements": ["Temporal mechanics", "Investigation skills"],
        "base_benefits": ["Anomaly detection", "Timeline analysis"],
        "intermediate_benefits": ["Temporal forensics", "Timeline repair"],
        "advanced_benefits": ["Perfect investigation", "Timeline mastery"],
        "master_benefits": ["Universal temporal control", "Time mastery"]
    },
    
    "Dark Matter Engineer": {
        "category": "Engineering",
        "description": "Engineers who harness and utilize dark matter for energy and applications.",
        "requirements": ["Dark matter physics", "Exotic engineering"],
        "base_benefits": ["Dark matter detection", "Basic harvesting"],
        "intermediate_benefits": ["Dark matter manipulation", "Exotic applications"],
        "advanced_benefits": ["Perfect dark matter mastery", "Universal energy"],
        "master_benefits": ["Cosmic mastery", "Universal power"]
    }
}

# Add profession categories for easier organization
profession_categories = {
    "Scientific": ["Astrobiologist", "Dimensional Physicist", "Quantum Computer Scientist", "Galactic Historian", "Xenoanthropologist"],
    "Engineering": ["Quantum Network Engineer", "Gravity Technician", "Terraforming Engineer", "Energy Harvesting Technician"],
    "Medical": ["Nanomedic", "Cybernetic Enhancement Specialist", "Regenerative Medicine Specialist", "Xeno-neurologist"],
    "Military": ["Temporal Investigator", "Chrono-Marine", "Dimensional Rift Stabilizer"],
    "Artistic": ["Virtual Reality Architect", "Holographic Entertainment Designer", "Bartender", "Interstellar Diplomat"],
    "Mystical": ["Soul Architect", "Reality Weaver", "Void Architect", "Etheric Communicator"]
}