"""
Classes (Occupations) for 7019 - Character Creation
Each class provides a career path, abilities, and starting equipment.
Classes are linked to backgrounds - only certain classes are available based on background.
"""

classes = {
    "Salvage Diver": {
        "description": "Expert in recovering technology and resources from dangerous ruins and wrecks.",
        "available_backgrounds": ["Orbital Foundling", "Reclamation Diver", "Voidfarer Crew", "Drift-Station Merchant"],
        "primary_stats": ["KIN", "VIT"],
        "starting_abilities": ["Advanced Salvage Techniques", "Hazard Detection", "Equipment Restoration"],
        "starting_equipment": ["Reinforced diving suit", "Plasma cutter", "Salvage drone"],
        "career_path": "Exploration and Resource Recovery",
        "typical_employers": ["Independent salvagers", "Corporate recovery teams", "Archaeological expeditions"]
    },
    
    "Neural Engineer": {
        "description": "Specialist in brain-machine interfaces, consciousness transfer, and cognitive enhancement.",
        "available_backgrounds": ["AI Scribe", "Quantum Savant", "Neo-Monastic Archivist", "Bioforge Technician"],
        "primary_stats": ["INT", "SYN"],
        "starting_abilities": ["Neural Interface Design", "Consciousness Mapping", "Cognitive Debugging"],
        "starting_equipment": ["Neural toolkit", "Diagnostic headset", "Cortical scanner"],
        "career_path": "Technology and Research",
        "typical_employers": ["The Icaron Collective", "Medical institutions", "AI research labs"]
    },
    
    "Ether Channeler": {
        "description": "Manipulator of etheric energies for power generation, propulsion, and combat.",
        "available_backgrounds": ["Etherborn Nomad", "Chrono-Refugee", "Voidfarer Crew", "Quantum Savant"],
        "primary_stats": ["AEF", "COH"],
        "starting_abilities": ["Energy Channeling", "Etheric Shield", "Power Surge"],
        "starting_equipment": ["Resonance amplifier", "Etheric batteries", "Personal shield generator"],
        "career_path": "Energy Manipulation and Defense",
        "typical_employers": ["Power corporations", "Military forces", "Research stations"]
    },
    
    "Bio-Sculptor": {
        "description": "Artist and engineer who designs living organisms, symbiotic tools, and biological systems.",
        "available_backgrounds": ["Bioforge Technician", "Deep-Core Miner", "Planetary Ranger", "Reclamation Diver"],
        "primary_stats": ["SYN", "INT"],
        "starting_abilities": ["Genetic Engineering", "Symbiote Bonding", "Rapid Evolution"],
        "starting_equipment": ["Gene splicer", "Bio-catalyst injector", "Living sample kit"],
        "career_path": "Biotechnology and Creation",
        "typical_employers": ["Harmonic Vitality Consortium", "Agricultural corps", "Military bio-divisions"]
    },
    
    "Void Navigator": {
        "description": "Pilot and astrogator who charts courses through hyperspace, quantum foam, and ether currents.",
        "available_backgrounds": ["Voidfarer Crew", "Etherborn Nomad", "Quantum Savant", "Chrono-Refugee"],
        "primary_stats": ["INT", "AEF"],
        "starting_abilities": ["Quantum Navigation", "Hyperspace Plotting", "Emergency Maneuvering"],
        "starting_equipment": ["Navigation computer", "Star charts", "Quantum compass"],
        "career_path": "Exploration and Transportation",
        "typical_employers": ["Trading guilds", "Exploration fleets", "Private shipping companies"]
    },
    
    "Combat Medic": {
        "description": "Battlefield healer combining traditional medicine with biotech and harmonic therapy.",
        "available_backgrounds": ["Bioforge Technician", "Voidfarer Crew", "Street Synth", "Planetary Ranger"],
        "primary_stats": ["VIT", "COH"],
        "starting_abilities": ["Emergency Stabilization", "Combat Triage", "Bio-Regeneration"],
        "starting_equipment": ["Medical kit", "Bio-foam dispenser", "Harmonic healing device"],
        "career_path": "Medical and Support",
        "typical_employers": ["Military units", "Harmonic Vitality Consortium", "Mercenary groups"]
    },
    
    "Data Archaeologist": {
        "description": "Recovers and reconstructs lost information from ancient databases and corrupted archives.",
        "available_backgrounds": ["AI Scribe", "Neo-Monastic Archivist", "Quantum Savant", "Drift-Station Merchant"],
        "primary_stats": ["INT", "COH"],
        "starting_abilities": ["Data Recovery", "Encryption Breaking", "Digital Reconstruction"],
        "starting_equipment": ["Decryption suite", "Archive scanner", "Backup core"],
        "career_path": "Research and Information",
        "typical_employers": ["The Veritas Covenant", "Corporate intelligence", "Archaeological teams"]
    },
    
    "Street Fixer": {
        "description": "Problem solver and deal maker who navigates urban underworlds and grey markets.",
        "available_backgrounds": ["Street Synth", "Drift-Station Merchant", "Orbital Foundling", "Voidfarer Crew"],
        "primary_stats": ["INF", "KIN"],
        "starting_abilities": ["Black Market Access", "Fast Talk", "Urban Navigation"],
        "starting_equipment": ["Concealed weapon", "Encrypted commlink", "Forged credentials"],
        "career_path": "Commerce and Intrigue",
        "typical_employers": ["Criminal syndicates", "Information brokers", "Independent operators"]
    },
    
    "Terraformer": {
        "description": "Environmental engineer who designs and maintains habitable ecosystems on alien worlds.",
        "available_backgrounds": ["Planetary Ranger", "Deep-Core Miner", "Bioforge Technician", "Neo-Monastic Archivist"],
        "primary_stats": ["SYN", "VIT"],
        "starting_abilities": ["Atmospheric Engineering", "Ecosystem Design", "Climate Control"],
        "starting_equipment": ["Atmosphere analyzer", "Seed vault", "Terraforming nanites"],
        "career_path": "Environmental Engineering",
        "typical_employers": ["The Gaian Enclave", "Colonial administrations", "Mega-corporations"]
    },
    
    "Quantum Analyst": {
        "description": "Specialist in probability manipulation, quantum computing, and predictive modeling.",
        "available_backgrounds": ["Quantum Savant", "AI Scribe", "Chrono-Refugee", "Neo-Monastic Archivist"],
        "primary_stats": ["INT", "AEF"],
        "starting_abilities": ["Probability Analysis", "Quantum Computation", "Future Modeling"],
        "starting_equipment": ["Quantum processor", "Probability calculator", "Temporal sensor"],
        "career_path": "Advanced Research",
        "typical_employers": ["The Veritas Covenant", "Financial institutions", "Military intelligence"]
    },
    
    "Mech Pilot": {
        "description": "Operator of large combat or industrial exosuits and mechanized armor.",
        "available_backgrounds": ["Deep-Core Miner", "Voidfarer Crew", "Street Synth", "Orbital Foundling"],
        "primary_stats": ["KIN", "COH"],
        "starting_abilities": ["Mech Combat", "Precision Control", "System Override"],
        "starting_equipment": ["Light exosuit", "Control interface", "Maintenance toolkit"],
        "career_path": "Combat and Industrial Operations",
        "typical_employers": ["Military forces", "Mining corporations", "Security contractors"]
    },
    
    "Psi-Operative": {
        "description": "Trained psychic specializing in mental influence, telepathy, and perception manipulation.",
        "available_backgrounds": ["Chrono-Refugee", "Etherborn Nomad", "Quantum Savant", "Neo-Monastic Archivist"],
        "primary_stats": ["COH", "INF"],
        "starting_abilities": ["Telepathic Link", "Mental Shield", "Emotional Influence"],
        "starting_equipment": ["Psi-amplifier", "Mental dampener", "Neural recorder"],
        "career_path": "Covert Operations and Diplomacy",
        "typical_employers": ["Intelligence agencies", "Diplomatic corps", "Corporate espionage"]
    },
    
    "Synth Designer": {
        "description": "Creator of synthetic organisms, artificial life forms, and bio-mechanical hybrids.",
        "available_backgrounds": ["Bioforge Technician", "AI Scribe", "Street Synth", "Quantum Savant"],
        "primary_stats": ["SYN", "INT"],
        "starting_abilities": ["Synthetic Life Creation", "Hybrid Engineering", "Biological Programming"],
        "starting_equipment": ["Synthesis chamber", "DNA sequencer", "Nano-assembler"],
        "career_path": "Advanced Biotechnology",
        "typical_employers": ["The Icaron Collective", "Biotech corporations", "Military R&D"]
    },
    
    "Trade Diplomat": {
        "description": "Negotiator and mediator specializing in inter-faction commerce and conflict resolution.",
        "available_backgrounds": ["Drift-Station Merchant", "Street Synth", "Planetary Ranger", "AI Scribe"],
        "primary_stats": ["INF", "COH"],
        "starting_abilities": ["Master Negotiation", "Cultural Analysis", "Conflict De-escalation"],
        "starting_equipment": ["Universal translator", "Diplomatic credentials", "Gift portfolio"],
        "career_path": "Diplomacy and Commerce",
        "typical_employers": ["Stellar Nexus Guild", "Diplomatic missions", "Independent mediators"]
    },
    
    "Relic Hunter": {
        "description": "Adventurer seeking ancient artifacts, lost technology, and forbidden knowledge.",
        "available_backgrounds": ["Reclamation Diver", "Neo-Monastic Archivist", "Voidfarer Crew", "Orbital Foundling"],
        "primary_stats": ["KIN", "INT"],
        "starting_abilities": ["Artifact Identification", "Trap Detection", "Ancient Language Comprehension"],
        "starting_equipment": ["Scanning device", "Climbing gear", "Protective field generator"],
        "career_path": "Exploration and Archaeology",
        "typical_employers": ["The Veritas Covenant", "Private collectors", "Archaeological foundations"]
    },
    
    "Harmonic Healer": {
        "description": "Practitioner of frequency-based medicine using sound, light, and vibration for healing.",
        "available_backgrounds": ["Etherborn Nomad", "Bioforge Technician", "Planetary Ranger", "Neo-Monastic Archivist"],
        "primary_stats": ["COH", "AEF"],
        "starting_abilities": ["Frequency Healing", "Resonance Diagnosis", "Harmonic Stabilization"],
        "starting_equipment": ["Harmonic tuner", "Frequency generator", "Bio-resonance scanner"],
        "career_path": "Alternative Medicine",
        "typical_employers": ["Harmonic Vitality Consortium", "Wellness centers", "Spiritual communities"]
    },
    
    "Systems Hacker": {
        "description": "Expert in penetrating digital systems, subverting AI, and electronic warfare.",
        "available_backgrounds": ["AI Scribe", "Street Synth", "Quantum Savant", "Orbital Foundling"],
        "primary_stats": ["INT", "KIN"],
        "starting_abilities": ["System Intrusion", "AI Manipulation", "Electronic Countermeasures"],
        "starting_equipment": ["Hacking deck", "Signal jammer", "Virus library"],
        "career_path": "Cyber Operations",
        "typical_employers": ["Corporate security", "Criminal networks", "Military intelligence"]
    },
    
    "Xenobiologist": {
        "description": "Scientist studying alien life forms, exotic ecosystems, and non-human biology.",
        "available_backgrounds": ["Planetary Ranger", "Bioforge Technician", "Reclamation Diver", "Voidfarer Crew"],
        "primary_stats": ["INT", "SYN"],
        "starting_abilities": ["Alien Analysis", "Ecosystem Mapping", "Xenoform Communication"],
        "starting_equipment": ["Field laboratory", "Sample containment", "Universal biology scanner"],
        "career_path": "Xenological Research",
        "typical_employers": ["The Veritas Covenant", "Exploration fleets", "Biotech corporations"]
    },
    
    "Energy Trader": {
        "description": "Merchant specializing in etheric fuel, power cells, and energy commodities.",
        "available_backgrounds": ["Drift-Station Merchant", "Etherborn Nomad", "Street Synth", "Voidfarer Crew"],
        "primary_stats": ["INF", "AEF"],
        "starting_abilities": ["Energy Market Analysis", "Fuel Quality Assessment", "Price Negotiation"],
        "starting_equipment": ["Energy scanner", "Trading terminal", "Sample containers"],
        "career_path": "Specialized Commerce",
        "typical_employers": ["Stellar Nexus Guild", "Energy corporations", "Independent traders"]
    },
    
    "Consciousness Engineer": {
        "description": "Specialist in mind uploading, personality transfer, and digital immortality.",
        "available_backgrounds": ["AI Scribe", "Quantum Savant", "Chrono-Refugee", "Neo-Monastic Archivist"],
        "primary_stats": ["INT", "COH"],
        "starting_abilities": ["Consciousness Mapping", "Digital Soul Transfer", "Personality Integration"],
        "starting_equipment": ["Neural transfer pod", "Consciousness matrix", "Identity backup system"],
        "career_path": "Advanced Neurotechnology",
        "typical_employers": ["The Icaron Collective", "Immortality clinics", "Research institutions"]
    },
    
    "Void Marine": {
        "description": "Elite soldier trained for combat in zero-gravity, hostile atmospheres, and void conditions.",
        "available_backgrounds": ["Voidfarer Crew", "Deep-Core Miner", "Orbital Foundling", "Street Synth"],
        "primary_stats": ["VIT", "KIN"],
        "starting_abilities": ["Zero-G Combat", "Breach and Clear", "Survival Training"],
        "starting_equipment": ["Void armor", "Magnetic boots", "Multi-environment weapon"],
        "career_path": "Military Combat",
        "typical_employers": ["Planetary defense forces", "Corporate security", "Mercenary companies"]
    },
    
    "Temporal Mechanic": {
        "description": "Technician who repairs and maintains time-distorted equipment and causality engines.",
        "available_backgrounds": ["Chrono-Refugee", "Quantum Savant", "AI Scribe", "Voidfarer Crew"],
        "primary_stats": ["INT", "AEF"],
        "starting_abilities": ["Temporal Repair", "Causality Stabilization", "Timeline Analysis"],
        "starting_equipment": ["Temporal toolkit", "Chronometer", "Phase stabilizer"],
        "career_path": "Specialized Engineering",
        "typical_employers": ["Research stations", "Time-anomaly zones", "Advanced laboratories"]
    },
    
    "Corporate Infiltrator": {
        "description": "Covert operative specializing in industrial espionage and corporate sabotage.",
        "available_backgrounds": ["Street Synth", "AI Scribe", "Orbital Foundling", "Drift-Station Merchant"],
        "primary_stats": ["KIN", "INF"],
        "starting_abilities": ["Stealth Infiltration", "Data Theft", "Social Engineering"],
        "starting_equipment": ["Stealth suit", "ID spoofer", "Mini surveillance drone"],
        "career_path": "Corporate Espionage",
        "typical_employers": ["Mega-corporations", "Intelligence agencies", "Rival companies"]
    },
    
    "Eco-Guardian": {
        "description": "Protector of natural environments and enforcer of ecological preservation laws.",
        "available_backgrounds": ["Planetary Ranger", "Bioforge Technician", "Etherborn Nomad", "Voidfarer Crew"],
        "primary_stats": ["VIT", "INF"],
        "starting_abilities": ["Environmental Assessment", "Conservation Enforcement", "Wildlife Handling"],
        "starting_equipment": ["Eco-monitor", "Non-lethal restraints", "Emergency shelter"],
        "career_path": "Environmental Protection",
        "typical_employers": ["The Gaian Enclave", "Planetary governments", "Conservation organizations"]
    },
    
    "Reality Theorist": {
        "description": "Philosopher-scientist exploring the nature of existence, simulation theory, and dimensional physics.",
        "available_backgrounds": ["Quantum Savant", "Chrono-Refugee", "Neo-Monastic Archivist", "AI Scribe"],
        "primary_stats": ["INT", "COH"],
        "starting_abilities": ["Reality Analysis", "Dimensional Perception", "Existential Paradox Resolution"],
        "starting_equipment": ["Reality sensor", "Philosophical database", "Meditation chamber access"],
        "career_path": "Theoretical Research",
        "typical_employers": ["The Veritas Covenant", "Universities", "Think tanks"]
    },
    
    "Smuggler": {
        "description": "Transporter of restricted goods, contraband, and illicit cargo across borders.",
        "available_backgrounds": ["Voidfarer Crew", "Drift-Station Merchant", "Street Synth", "Orbital Foundling"],
        "primary_stats": ["KIN", "INF"],
        "starting_abilities": ["Contraband Concealment", "Customs Evasion", "Fast Ship Handling"],
        "starting_equipment": ["Hidden cargo holds", "False transponder", "Emergency escape pod"],
        "career_path": "Illegal Transportation",
        "typical_employers": ["Criminal syndicates", "Rebel groups", "Independent operators"]
    },
    
    "Fusion Technician": {
        "description": "Engineer maintaining reactors, power cores, and fusion-based energy systems.",
        "available_backgrounds": ["Deep-Core Miner", "Voidfarer Crew", "AI Scribe", "Bioforge Technician"],
        "primary_stats": ["INT", "VIT"],
        "starting_abilities": ["Reactor Maintenance", "Fusion Control", "Emergency Shutdown"],
        "starting_equipment": ["Radiation suit", "Fusion tools", "Safety protocols"],
        "career_path": "Power Engineering",
        "typical_employers": ["Power stations", "Starship crews", "Industrial facilities"]
    },
    
    "Memory Curator": {
        "description": "Specialist in preserving, editing, and sharing memories through neural interfaces.",
        "available_backgrounds": ["Neo-Monastic Archivist", "AI Scribe", "Chrono-Refugee", "Street Synth"],
        "primary_stats": ["COH", "INT"],
        "starting_abilities": ["Memory Extraction", "Experience Sharing", "Memory Editing"],
        "starting_equipment": ["Memory recorder", "Neural playback device", "Archive vault"],
        "career_path": "Memory Services",
        "typical_employers": ["Entertainment industry", "Legal services", "Therapeutic clinics"]
    },
    
    "Bounty Hunter": {
        "description": "Tracker and captor of fugitives, wanted criminals, and contractual targets.",
        "available_backgrounds": ["Voidfarer Crew", "Street Synth", "Planetary Ranger", "Orbital Foundling"],
        "primary_stats": ["KIN", "VIT"],
        "starting_abilities": ["Target Tracking", "Capture Techniques", "Combat Proficiency"],
        "starting_equipment": ["Tracking device", "Stun weapons", "Restraint gear"],
        "career_path": "Law Enforcement",
        "typical_employers": ["Bounty guilds", "Law enforcement", "Private clients"]
    },
    
    "Synesthetic Artist": {
        "description": "Creator who translates between sensory modalities - sound into color, emotion into texture.",
        "available_backgrounds": ["Etherborn Nomad", "Chrono-Refugee", "Bioforge Technician", "Neo-Monastic Archivist"],
        "primary_stats": ["SYN", "COH"],
        "starting_abilities": ["Sensory Translation", "Artistic Expression", "Emotional Resonance"],
        "starting_equipment": ["Synesthetic converter", "Art supplies", "Experience recorder"],
        "career_path": "Creative Arts",
        "typical_employers": ["Art collectives", "Entertainment corporations", "Therapeutic centers"]
    },
    
    "Warp Drive Specialist": {
        "description": "Expert in faster-than-light propulsion systems and hyperspace mechanics.",
        "available_backgrounds": ["Voidfarer Crew", "Quantum Savant", "AI Scribe", "Deep-Core Miner"],
        "primary_stats": ["INT", "AEF"],
        "starting_abilities": ["FTL Navigation", "Hyperspace Calculation", "Drive Maintenance"],
        "starting_equipment": ["Warp calibrator", "Hyperspace charts", "Emergency beacon"],
        "career_path": "Advanced Engineering",
        "typical_employers": ["Starship manufacturers", "Exploration fleets", "Military navies"]
    },
    
    "Social Architect": {
        "description": "Designer of social systems, cultural movements, and collective behavioral patterns.",
        "available_backgrounds": ["Drift-Station Merchant", "Neo-Monastic Archivist", "AI Scribe", "Planetary Ranger"],
        "primary_stats": ["INF", "SYN"],
        "starting_abilities": ["Cultural Engineering", "Memetic Design", "Social Prediction"],
        "starting_equipment": ["Social analysis software", "Memetic toolkit", "Communication network"],
        "career_path": "Social Engineering",
        "typical_employers": ["Governments", "Marketing firms", "Political movements"]
    },
    
    "Nanotech Surgeon": {
        "description": "Medical specialist using nanomachines for precision surgery and cellular repair.",
        "available_backgrounds": ["Bioforge Technician", "AI Scribe", "Street Synth", "Quantum Savant"],
        "primary_stats": ["INT", "KIN"],
        "starting_abilities": ["Nano-Surgery", "Cellular Repair", "Precision Medicine"],
        "starting_equipment": ["Nano-injector", "Medical scanner", "Surgical nanites"],
        "career_path": "Advanced Medicine",
        "typical_employers": ["Harmonic Vitality Consortium", "Elite hospitals", "Military medical"]
    },
    
    "Astro-Cartographer": {
        "description": "Mapper of star systems, spatial anomalies, and uncharted regions of space.",
        "available_backgrounds": ["Voidfarer Crew", "Quantum Savant", "Planetary Ranger", "Neo-Monastic Archivist"],
        "primary_stats": ["INT", "KIN"],
        "starting_abilities": ["Stellar Mapping", "Anomaly Detection", "Navigation Route Design"],
        "starting_equipment": ["Mapping computer", "Spatial sensors", "Chart database"],
        "career_path": "Exploration and Surveying",
        "typical_employers": ["Exploration guilds", "Military survey corps", "Private expeditions"]
    },
    
    "Etherforger": {
        "description": "Craftsperson who shapes raw etheric energy into solid objects and tools.",
        "available_backgrounds": ["Etherborn Nomad", "Deep-Core Miner", "Bioforge Technician", "Chrono-Refugee"],
        "primary_stats": ["AEF", "SYN"],
        "starting_abilities": ["Energy Materialization", "Etheric Crafting", "Matter Stabilization"],
        "starting_equipment": ["Forging matrix", "Energy molds", "Stabilizer field"],
        "career_path": "Exotic Manufacturing",
        "typical_employers": ["Artisan guilds", "Military contractors", "Research facilities"]
    },
    
    "Crisis Negotiator": {
        "description": "Expert in resolving hostage situations, conflicts, and high-stakes negotiations.",
        "available_backgrounds": ["Drift-Station Merchant", "Street Synth", "AI Scribe", "Planetary Ranger"],
        "primary_stats": ["INF", "COH"],
        "starting_abilities": ["Hostage Negotiation", "Stress Management", "Conflict Resolution"],
        "starting_equipment": ["Secure commlink", "Psychological profiles", "Non-lethal options"],
        "career_path": "Crisis Management",
        "typical_employers": ["Law enforcement", "Corporate security", "Diplomatic services"]
    },
    
    "Void Shaman": {
        "description": "Mystic who communes with the spirits of space, stellar consciousness, and cosmic forces.",
        "available_backgrounds": ["Etherborn Nomad", "Chrono-Refugee", "Neo-Monastic Archivist", "Voidfarer Crew"],
        "primary_stats": ["AEF", "COH"],
        "starting_abilities": ["Cosmic Communion", "Stellar Divination", "Void Walking"],
        "starting_equipment": ["Ritual tools", "Star map", "Meditation chamber"],
        "career_path": "Mysticism and Spirituality",
        "typical_employers": ["Spiritual communities", "The Gaian Enclave", "Independent practice"]
    },
    
    "Combat Engineer": {
        "description": "Military technician specializing in fortifications, demolitions, and battlefield construction.",
        "available_backgrounds": ["Deep-Core Miner", "Voidfarer Crew", "Orbital Foundling", "AI Scribe"],
        "primary_stats": ["INT", "VIT"],
        "starting_abilities": ["Demolitions", "Field Fortification", "Equipment Fabrication"],
        "starting_equipment": ["Engineering kit", "Explosives", "Portable fabricator"],
        "career_path": "Military Engineering",
        "typical_employers": ["Armed forces", "Mercenary companies", "Defense contractors"]
    },
    
    "Identity Broker": {
        "description": "Dealer in personas, false identities, and consciousness trading on the grey market.",
        "available_backgrounds": ["Street Synth", "Drift-Station Merchant", "AI Scribe", "Chrono-Refugee"],
        "primary_stats": ["INF", "INT"],
        "starting_abilities": ["Identity Fabrication", "Persona Trading", "Memory Manipulation"],
        "starting_equipment": ["ID fabricator", "Neural override codes", "Identity vault"],
        "career_path": "Black Market Services",
        "typical_employers": ["Criminal networks", "Intelligence agencies", "Underground markets"]
    },
    
    "Stellar Ranger": {
        "description": "Law enforcement officer patrolling frontier systems and maintaining order in the outer reaches.",
        "available_backgrounds": ["Voidfarer Crew", "Planetary Ranger", "Orbital Foundling", "Deep-Core Miner"],
        "primary_stats": ["VIT", "INF"],
        "starting_abilities": ["Frontier Justice", "Investigation", "Long-Range Pursuit"],
        "starting_equipment": ["Badge and credentials", "Multi-tool", "Personal spacecraft access"],
        "career_path": "Law Enforcement",
        "typical_employers": ["Frontier law agencies", "Colonial governments", "Ranger guilds"]
    },
    
    "Nanite Sculptor": {
        "description": "Artist and engineer who programs nanomachines to create intricate structures and living art.",
        "available_backgrounds": ["Nanite Ascetic", "Bioforge Technician", "AI Scribe", "Quantum Savant"],
        "primary_stats": ["INT", "SYN"],
        "starting_abilities": ["Nano-Programming", "Molecular Assembly", "Swarm Coordination"],
        "starting_equipment": ["Nanite control suite", "Molecular templates", "Assembly chamber"],
        "career_path": "Nanotechnology and Art",
        "typical_employers": ["Art collectives", "Manufacturing corps", "Research institutions"]
    },
    
    "Swarm Tactician": {
        "description": "Military specialist in coordinating nanite swarms for combat and defense applications.",
        "available_backgrounds": ["Nanite Ascetic", "Warfleet Remnant", "AI Scribe", "Deep-Core Miner"],
        "primary_stats": ["INT", "COH"],
        "starting_abilities": ["Swarm Combat", "Defensive Formations", "Nano-Repair"],
        "starting_equipment": ["Combat nanites", "Tactical control interface", "Defensive swarm"],
        "career_path": "Military Nanotechnology",
        "typical_employers": ["Military forces", "Security contractors", "Defense research"]
    },
    
    "Fleet Commander": {
        "description": "Veteran officer trained in large-scale space combat and fleet coordination.",
        "available_backgrounds": ["Warfleet Remnant", "Voidfarer Crew", "AI Scribe", "Street Synth"],
        "primary_stats": ["INT", "INF"],
        "starting_abilities": ["Fleet Tactics", "Strategic Planning", "Command Presence"],
        "starting_equipment": ["Command interface", "Tactical holodisplay", "Fleet communication suite"],
        "career_path": "Military Leadership",
        "typical_employers": ["Naval forces", "Mercenary fleets", "Corporate armadas"]
    },
    
    "War Machine Pilot": {
        "description": "Specialist in operating heavy combat vehicles and assault mechs from military service.",
        "available_backgrounds": ["Warfleet Remnant", "Deep-Core Miner", "Orbital Foundling", "Street Synth"],
        "primary_stats": ["KIN", "VIT"],
        "starting_abilities": ["Heavy Weapons", "Armored Combat", "Emergency Repairs"],
        "starting_equipment": ["Combat mech access", "Heavy armor", "Weapon maintenance kit"],
        "career_path": "Mechanized Warfare",
        "typical_employers": ["Military contractors", "Security forces", "Salvage operations"]
    },
    
    "Digital Infiltrator": {
        "description": "Expert in navigating virtual realities, data networks, and digital consciousness spaces.",
        "available_backgrounds": ["Datawalker", "AI Scribe", "Street Synth", "Quantum Savant"],
        "primary_stats": ["INT", "KIN"],
        "starting_abilities": ["Virtual Navigation", "Data Extraction", "Digital Combat"],
        "starting_equipment": ["Neural interface rig", "ICE breaker suite", "Virtual avatar"],
        "career_path": "Cyberspace Operations",
        "typical_employers": ["Corporate espionage", "Information brokers", "Digital security"]
    },
    
    "Reality Hacker": {
        "description": "Manipulator of simulated realities and virtual world architectures.",
        "available_backgrounds": ["Datawalker", "Quantum Savant", "AI Scribe", "Chrono-Refugee"],
        "primary_stats": ["INT", "SYN"],
        "starting_abilities": ["Reality Editing", "Simulation Design", "Code Manipulation"],
        "starting_equipment": ["Reality editor", "Simulation templates", "Quantum processor"],
        "career_path": "Virtual World Engineering",
        "typical_employers": ["Entertainment industry", "Research labs", "Virtual world corporations"]
    },
    
    "Brewmaster": {
        "description": "Alchemist and chemist specializing in fermentation, distillation, and molecular gastronomy.",
        "available_backgrounds": ["Brewmasters' Acolyte", "Bioforge Technician", "Drift-Station Merchant", "Planetary Ranger"],
        "primary_stats": ["SYN", "COH"],
        "starting_abilities": ["Master Brewing", "Chemical Analysis", "Flavor Engineering"],
        "starting_equipment": ["Brewing equipment", "Molecular analyzer", "Recipe vault"],
        "career_path": "Culinary Chemistry",
        "typical_employers": ["Hospitality industry", "Chemical companies", "Luxury trade"]
    },
    
    "Biochemical Engineer": {
        "description": "Specialist in designing biological compounds, fermentation processes, and living chemistry.",
        "available_backgrounds": ["Brewmasters' Acolyte", "Bioforge Technician", "AI Scribe", "Deep-Core Miner"],
        "primary_stats": ["INT", "SYN"],
        "starting_abilities": ["Compound Synthesis", "Fermentation Control", "Biological Catalysis"],
        "starting_equipment": ["Synthesis lab", "Fermentation tanks", "Chemical scanner"],
        "career_path": "Industrial Biotechnology",
        "typical_employers": ["Pharmaceutical companies", "Food industry", "Bio-manufacturing"]
    },
    
    "Corporate Executive": {
        "description": "Business leader trained in management, finance, and strategic corporate operations.",
        "available_backgrounds": ["Industrial Heir", "Drift-Station Merchant", "AI Scribe", "Street Synth"],
        "primary_stats": ["INF", "INT"],
        "starting_abilities": ["Business Strategy", "Resource Management", "Negotiation"],
        "starting_equipment": ["Corporate credentials", "Financial terminal", "Executive suite access"],
        "career_path": "Corporate Leadership",
        "typical_employers": ["Mega-corporations", "Trading guilds", "Financial institutions"]
    },
    
    "Supply Chain Director": {
        "description": "Logistics expert managing complex trade networks and industrial supply chains.",
        "available_backgrounds": ["Industrial Heir", "Drift-Station Merchant", "Voidfarer Crew", "AI Scribe"],
        "primary_stats": ["INT", "INF"],
        "starting_abilities": ["Logistics Optimization", "Trade Network Management", "Resource Forecasting"],
        "starting_equipment": ["Supply chain software", "Trade manifests", "Warehouse access codes"],
        "career_path": "Industrial Logistics",
        "typical_employers": ["Manufacturing corporations", "Trading guilds", "Colonial administrations"]
    },
    
    "Desert Scout": {
        "description": "Survivalist and guide specializing in extreme arid environments and wasteland navigation.",
        "available_backgrounds": ["Dust-Wanderer", "Planetary Ranger", "Reclamation Diver", "Voidfarer Crew"],
        "primary_stats": ["VIT", "KIN"],
        "starting_abilities": ["Desert Survival", "Water Finding", "Sand Navigation"],
        "starting_equipment": ["Environmental suit", "Water reclamator", "Navigation beacon"],
        "career_path": "Extreme Environment Survival",
        "typical_employers": ["Exploration teams", "Salvage operations", "Colonial scouts"]
    },
    
    "Wasteland Scavenger": {
        "description": "Expert in surviving and thriving in harsh desert ruins and abandoned settlements.",
        "available_backgrounds": ["Dust-Wanderer", "Reclamation Diver", "Orbital Foundling", "Street Synth"],
        "primary_stats": ["KIN", "VIT"],
        "starting_abilities": ["Scavenging", "Sandstorm Survival", "Resource Extraction"],
        "starting_equipment": ["Salvage tools", "Protective gear", "Storage containers"],
        "career_path": "Survival and Recovery",
        "typical_employers": ["Independent salvagers", "Wasteland traders", "Survival communes"]
    },
    
    "Dream Weaver": {
        "description": "Psychic artist who crafts shared dreams and explores collective unconscious spaces.",
        "available_backgrounds": ["Dreamlink Initiate", "Chrono-Refugee", "Neo-Monastic Archivist", "Etherborn Nomad"],
        "primary_stats": ["AEF", "SYN"],
        "starting_abilities": ["Dream Crafting", "Shared Vision", "Subconscious Navigation"],
        "starting_equipment": ["Dream amplifier", "Neural sync device", "Meditation chamber"],
        "career_path": "Psychic Arts",
        "typical_employers": ["Entertainment industry", "Therapeutic centers", "Spiritual communities"]
    },
    
    "Oneiromancer": {
        "description": "Mystic who uses dreams for divination, healing, and exploring alternate realities.",
        "available_backgrounds": ["Dreamlink Initiate", "Chrono-Refugee", "Etherborn Nomad", "Quantum Savant"],
        "primary_stats": ["COH", "AEF"],
        "starting_abilities": ["Dream Divination", "Psychic Healing", "Reality Perception"],
        "starting_equipment": ["Divination tools", "Dream journal", "Psychic focus"],
        "career_path": "Mysticism and Divination",
        "typical_employers": ["Spiritual orders", "Independent practice", "Research institutions"]
    }
}


def get_available_classes(background_name):
    """
    Get list of classes available for a given background.
    
    Args:
        background_name: Name of the character's background
        
    Returns:
        List of class names available for this background
    """
    available = []
    for class_name, class_data in classes.items():
        if background_name in class_data['available_backgrounds']:
            available.append(class_name)
    return available


def get_class_info(class_name):
    """
    Get complete information about a class.
    
    Args:
        class_name: Name of the class
        
    Returns:
        Dictionary with class data, or None if not found
    """
    return classes.get(class_name, None)


def get_classes_by_stat(stat_name):
    """
    Get all classes that prioritize a given stat.
    
    Args:
        stat_name: Name of the stat (e.g., "INT", "VIT")
        
    Returns:
        List of class names that use this as a primary stat
    """
    matching_classes = []
    for class_name, class_data in classes.items():
        if stat_name in class_data['primary_stats']:
            matching_classes.append(class_name)
    return matching_classes


def get_classes_by_career(career_path):
    """
    Get all classes in a given career path.
    
    Args:
        career_path: Career path string (e.g., "Military Combat")
        
    Returns:
        List of class names in this career path
    """
    matching_classes = []
    for class_name, class_data in classes.items():
        if career_path.lower() in class_data['career_path'].lower():
            matching_classes.append(class_name)
    return matching_classes
