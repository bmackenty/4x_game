
"""
Galactic History System for 4X Game
Procedural ancient civilizations, archaeological discoveries, and historical events
"""

import random
import time

class GalacticHistory:
    def __init__(self):
        self.ancient_civilizations = {}
        self.historical_events = []
        self.archaeological_sites = {}  # coordinates: site_info
        self.discovered_artifacts = []
        self.timeline = {}  # year: [events]
        self.current_galactic_age = 2387  # Current game year
        
        self.initialize_ancient_civilizations()
        self.generate_historical_timeline()
    
    def initialize_ancient_civilizations(self):
        """Initialize the ancient civilizations and their remnants"""
        self.ancient_civilizations = {
            "Zenthorian Empire": {
                "era": "Crystal Age",
                "years_ago": random.randint(50000, 100000),
                "technology_focus": "Crystal Communication Networks",
                "remnant_type": "Crystal Communication Arrays",
                "description": "A vast empire that spanned thousands of systems, connected by instantaneous crystal-based communication networks.",
                "downfall": "Sudden silence - all communication ceased simultaneously across the empire",
                "signature_technology": ["Quantum Crystal Networks", "Harmonic Resonance", "Crystal Memory Storage"],
                "archaeological_value": "Extremely High",
                "sites_per_galaxy": random.randint(3, 7),
                "artifact_types": ["Crystal Communication Nodes", "Harmonic Resonance Chambers", "Memory Crystals"],
                "discovery_benefits": ["Advanced Communication Tech", "Quantum Network Research", "Crystal Engineering"]
            },
            
            "Oreon Civilization": {
                "era": "Aquatic Dominion",
                "years_ago": random.randint(75000, 150000),
                "technology_focus": "Aquatic Bio-Engineering",
                "remnant_type": "Submerged Cities",
                "description": "Masters of aquatic environments who developed advanced bio-engineering beneath the waves.",
                "downfall": "Acidification catastrophe that dissolved their oceanic infrastructure",
                "signature_technology": ["Aquatic Bio-Engineering", "Pressure Adaptation", "Liquid-State Computing"],
                "archaeological_value": "High",
                "sites_per_galaxy": random.randint(2, 5),
                "artifact_types": ["Bio-Engineering Pods", "Pressure Adaptation Devices", "Aquatic Computing Cores"],
                "discovery_benefits": ["Bio-Engineering Mastery", "Environmental Adaptation", "Liquid Computing"]
            },
            
            "Myridian Builders": {
                "era": "Stellar Navigation Period",
                "years_ago": random.randint(80000, 120000),
                "technology_focus": "Astronomical Engineering",
                "remnant_type": "Celestial Monuments",
                "description": "Colossal builders who created galaxy-spanning navigational aids and astronomical computers.",
                "downfall": "Vanished during a galactic alignment event they were attempting to harness",
                "signature_technology": ["Gravitational Sculpture", "Celestial Computing", "Stellar Navigation"],
                "archaeological_value": "Very High",
                "sites_per_galaxy": random.randint(4, 8),
                "artifact_types": ["Gravitational Anchors", "Star Charts", "Celestial Computation Matrices"],
                "discovery_benefits": ["Perfect Navigation", "Gravitational Mastery", "Stellar Engineering"]
            },
            
            "Aetheris Collective": {
                "era": "Etheric Transcendence",
                "years_ago": random.randint(60000, 90000),
                "technology_focus": "Consciousness Transfer",
                "remnant_type": "Etheric Echo Fields",
                "description": "A collective consciousness that achieved instantaneous thought transfer across vast distances.",
                "downfall": "Transcendence event - uploaded themselves beyond physical reality",
                "signature_technology": ["Consciousness Transfer", "Etheric Manipulation", "Thought Networking"],
                "archaeological_value": "Transcendent",
                "sites_per_galaxy": random.randint(2, 4),
                "artifact_types": ["Consciousness Matrices", "Etheric Amplifiers", "Thought Crystals"],
                "discovery_benefits": ["Consciousness Technology", "Etheric Mastery", "Mental Enhancement"]
            },
            
            "Garnathans of Vorex": {
                "era": "Living Architecture Era",
                "years_ago": random.randint(45000, 85000),
                "technology_focus": "Bio-Architecture",
                "remnant_type": "Petrified Bio-Cities",
                "description": "Masters of living architecture who grew their cities from modified organisms.",
                "downfall": "Bio-plague that turned their living cities to stone",
                "signature_technology": ["Living Architecture", "Organic Computing", "Bio-Integration"],
                "archaeological_value": "High",
                "sites_per_galaxy": random.randint(3, 6),
                "artifact_types": ["Living Structure Seeds", "Bio-Computational Cores", "Organic Blueprints"],
                "discovery_benefits": ["Bio-Architecture", "Living Technology", "Organic Integration"]
            },
            
            "Silix Supremacy": {
                "era": "Information Dominion",
                "years_ago": random.randint(70000, 110000),
                "technology_focus": "Information Storage",
                "remnant_type": "Data Monuments",
                "description": "Information hoarders who stored the knowledge of civilizations in indestructible data slates.",
                "downfall": "Information overload - became lost in their own data networks",
                "signature_technology": ["Ultra-Dense Data Storage", "Information Processing", "Knowledge Networks"],
                "archaeological_value": "Invaluable",
                "sites_per_galaxy": random.randint(2, 5),
                "artifact_types": ["Data Slates", "Information Matrices", "Knowledge Cores"],
                "discovery_benefits": ["Perfect Information Storage", "Data Mastery", "Knowledge Networks"]
            },
            
            "Draconis League": {
                "era": "Stellar Warfare Period",
                "years_ago": random.randint(55000, 95000),
                "technology_focus": "Military Engineering",
                "remnant_type": "Star Fortresses",
                "description": "Warrior-engineers who built impregnable fortresses around stars themselves.",
                "downfall": "Final war that consumed their stellar fortresses in cosmic fire",
                "signature_technology": ["Stellar Fortification", "Cosmic Weaponry", "Space Combat Systems"],
                "archaeological_value": "Very High",
                "sites_per_galaxy": random.randint(3, 6),
                "artifact_types": ["Fortress Cores", "Stellar Weapons", "Combat Protocols"],
                "discovery_benefits": ["Advanced Weapons", "Stellar Engineering", "Military Technology"]
            },
            
            "Luminar Ascendency": {
                "era": "Spectral Renaissance",
                "years_ago": random.randint(40000, 70000),
                "technology_focus": "Light Manipulation",
                "remnant_type": "Prism Networks",
                "description": "Artists and scientists who mastered light itself, creating beauty and communication through spectral displays.",
                "downfall": "Faded away as their light-based consciousness dispersed into the cosmic background",
                "signature_technology": ["Light Manipulation", "Spectral Communication", "Photonic Art"],
                "archaeological_value": "High",
                "sites_per_galaxy": random.randint(4, 7),
                "artifact_types": ["Spectral Prisms", "Light Matrices", "Photonic Computers"],
                "discovery_benefits": ["Light Mastery", "Spectral Technology", "Photonic Engineering"]
            },
            
            "Echoes of Entari": {
                "era": "Harmonic Civilization",
                "years_ago": random.randint(35000, 65000),
                "technology_focus": "Sound Engineering",
                "remnant_type": "Sound Sculptures",
                "description": "Musical civilization that encoded their entire culture in resonant frequencies and sound sculptures.",
                "downfall": "The Great Silence - a cosmic event that absorbed all sound from their worlds",
                "signature_technology": ["Sonic Engineering", "Frequency Manipulation", "Harmonic Computing"],
                "archaeological_value": "High",
                "sites_per_galaxy": random.randint(3, 6),
                "artifact_types": ["Sound Crystals", "Harmonic Resonators", "Frequency Generators"],
                "discovery_benefits": ["Sound Technology", "Harmonic Mastery", "Frequency Control"]
            },
            
            "Chronos Civilization": {
                "era": "Temporal Mastery Period",
                "years_ago": random.randint(25000, 50000),
                "technology_focus": "Time Manipulation",
                "remnant_type": "Temporal Anomalies",
                "description": "Time masters who bent causality itself, creating pocket dimensions and temporal loops.",
                "downfall": "Temporal paradox cascade that scattered them across multiple timelines",
                "signature_technology": ["Time Manipulation", "Causality Engineering", "Temporal Computing"],
                "archaeological_value": "Transcendent",
                "sites_per_galaxy": random.randint(2, 4),
                "artifact_types": ["Temporal Anchors", "Causality Matrices", "Time Crystals"],
                "discovery_benefits": ["Time Technology", "Temporal Mastery", "Causality Control"]
            }
        }
    
    def generate_historical_timeline(self):
        """Generate a procedural timeline of galactic events"""
        self.timeline = {}
        
        # Add ancient civilization events
        for civ_name, civ_data in self.ancient_civilizations.items():
            rise_year = self.current_galactic_age - civ_data["years_ago"] - random.randint(5000, 15000)
            fall_year = self.current_galactic_age - civ_data["years_ago"]
            
            if rise_year not in self.timeline:
                self.timeline[rise_year] = []
            if fall_year not in self.timeline:
                self.timeline[fall_year] = []
            
            self.timeline[rise_year].append({
                "type": "civilization_rise",
                "civilization": civ_name,
                "description": f"The {civ_name} begins their dominion over the galaxy",
                "significance": "Major"
            })
            
            self.timeline[fall_year].append({
                "type": "civilization_fall", 
                "civilization": civ_name,
                "description": f"The {civ_name} meets their end: {civ_data['downfall']}",
                "significance": "Major"
            })
        
        # Add intermediate historical events
        self.generate_intermediate_events()
    
    def generate_intermediate_events(self):
        """Generate events between major civilizations"""
        event_types = [
            "cosmic_phenomenon", "discovery", "war", "alliance", "exploration",
            "technological_breakthrough", "natural_disaster", "first_contact"
        ]
        
        # Generate 20-30 intermediate events
        for _ in range(random.randint(20, 30)):
            year = random.randint(1, self.current_galactic_age - 1000)
            event_type = random.choice(event_types)
            
            if year not in self.timeline:
                self.timeline[year] = []
            
            event = self.generate_historical_event(event_type, year)
            self.timeline[year].append(event)
    
    def generate_historical_event(self, event_type, year):
        """Generate a specific historical event"""
        events = {
            "cosmic_phenomenon": [
                "Supernova chain reaction illuminates entire spiral arm",
                "Gravitational anomaly creates stable wormhole network",
                "Dark matter storm disrupts hyperspace travel for centuries",
                "Pulsar alignment creates galaxy-wide energy surge"
            ],
            "discovery": [
                "Unknown element with reality-altering properties discovered",
                "Ancient star maps reveal hidden galactic structure",
                "Breakthrough in consciousness transfer technology achieved",
                "Portal to parallel dimension accidentally opened"
            ],
            "war": [
                "The Silicon Wars devastate three spiral arms",
                "Machine Intelligence uprising spans 500 systems",
                "Temporal warriors engage in battles across time",
                "Hive mind collective assimilates entire star clusters"
            ],
            "alliance": [
                "Great Alliance of 47 species forms first galactic government",
                "Crystal Beings and Energy Entities create symbiotic partnership",
                "Trade confederation spans 200 star systems",
                "Scientific consortium shares breakthrough technologies"
            ]
        }
        
        if event_type in events:
            description = random.choice(events[event_type])
        else:
            description = f"Significant {event_type} occurs in galactic history"
        
        return {
            "type": event_type,
            "description": description,
            "year": year,
            "significance": random.choice(["Minor", "Moderate", "Major"])
        }
    
    def place_archaeological_sites(self, galaxy):
        """Place archaeological sites throughout the galaxy"""
        systems = list(galaxy.systems.values())
        
        for civ_name, civ_data in self.ancient_civilizations.items():
            sites_to_place = civ_data["sites_per_galaxy"]
            
            # Select random systems for this civilization's sites
            selected_systems = random.sample(systems, min(sites_to_place, len(systems)))
            
            for system in selected_systems:
                coords = system['coordinates']
                
                site_info = {
                    "civilization": civ_name,
                    "site_type": civ_data["remnant_type"],
                    "discovered": False,
                    "excavation_progress": 0,
                    "artifacts_found": [],
                    "research_value": civ_data["archaeological_value"],
                    "description": f"Mysterious {civ_data['remnant_type'].lower()} of unknown origin",
                    "system_name": system['name'],
                    "danger_level": random.randint(1, 5),
                    "exploration_requirements": self.generate_exploration_requirements(civ_data)
                }
                
                self.archaeological_sites[coords] = site_info
        
        return len(self.archaeological_sites)
    
    def generate_exploration_requirements(self, civ_data):
        """Generate requirements for exploring a site"""
        requirements = []
        
        if civ_data["archaeological_value"] == "Transcendent":
            requirements.extend(["Advanced Sensors", "Temporal Shielding", "Reality Stabilizers"])
        elif civ_data["archaeological_value"] == "Extremely High":
            requirements.extend(["Quantum Scanners", "Etheric Dampeners"])
        elif civ_data["archaeological_value"] == "Very High":
            requirements.extend(["Deep Space Sensors", "Radiation Shielding"])
        else:
            requirements.extend(["Basic Scanners", "Standard Equipment"])
        
        return requirements
    
    def discover_site(self, coordinates):
        """Discover an archaeological site"""
        if coordinates in self.archaeological_sites:
            site = self.archaeological_sites[coordinates]
            if not site["discovered"]:
                site["discovered"] = True
                
                civ_data = self.ancient_civilizations[site["civilization"]]
                
                discovery_info = {
                    "civilization": site["civilization"],
                    "era": civ_data["era"],
                    "technology_focus": civ_data["technology_focus"],
                    "site_description": civ_data["description"],
                    "years_ago": civ_data["years_ago"],
                    "significance": site["research_value"]
                }
                
                return True, discovery_info
        
        return False, None
    
    def excavate_site(self, coordinates, excavation_points=1):
        """Perform excavation at a site"""
        if coordinates in self.archaeological_sites:
            site = self.archaeological_sites[coordinates]
            if site["discovered"]:
                site["excavation_progress"] += excavation_points
                
                # Check for artifact discovery
                artifacts_possible = len(self.ancient_civilizations[site["civilization"]]["artifact_types"])
                artifacts_found = len(site["artifacts_found"])
                
                # Chance of finding artifact based on progress
                if (site["excavation_progress"] >= (artifacts_found + 1) * 25 and 
                    artifacts_found < artifacts_possible):
                    
                    artifact_types = self.ancient_civilizations[site["civilization"]]["artifact_types"]
                    new_artifact = artifact_types[artifacts_found]
                    
                    artifact_info = {
                        "name": new_artifact,
                        "civilization": site["civilization"],
                        "discovery_location": coordinates,
                        "research_value": random.randint(100, 1000),
                        "benefits": self.ancient_civilizations[site["civilization"]]["discovery_benefits"]
                    }
                    
                    site["artifacts_found"].append(artifact_info)
                    self.discovered_artifacts.append(artifact_info)
                    
                    return True, artifact_info
                
                return False, f"Excavation progress: {site['excavation_progress']}%"
        
        return False, "No site at this location"
    
    def get_site_info(self, coordinates):
        """Get information about a site"""
        if coordinates in self.archaeological_sites:
            return self.archaeological_sites[coordinates]
        return None
    
    def get_historical_summary(self):
        """Get a summary of galactic history"""
        summary = {
            "ancient_civilizations": len(self.ancient_civilizations),
            "archaeological_sites": len(self.archaeological_sites),
            "discovered_sites": len([s for s in self.archaeological_sites.values() if s["discovered"]]),
            "artifacts_discovered": len(self.discovered_artifacts),
            "timeline_events": sum(len(events) for events in self.timeline.values()),
            "current_age": self.current_galactic_age
        }
        
        return summary
    
    def get_civilization_info(self, civ_name):
        """Get detailed information about an ancient civilization"""
        if civ_name in self.ancient_civilizations:
            return self.ancient_civilizations[civ_name]
        return None
    
    def search_timeline(self, start_year=None, end_year=None, event_type=None):
        """Search historical timeline for specific events"""
        results = []
        
        for year, events in self.timeline.items():
            if start_year and year < start_year:
                continue
            if end_year and year > end_year:
                continue
            
            for event in events:
                if event_type and event.get("type") != event_type:
                    continue
                
                results.append({
                    "year": year,
                    "event": event
                })
        
        return results
    
    def get_discovered_artifacts(self):
        """Get all discovered artifacts organized by civilization"""
        return self.discovered_artifacts
    
    def get_archaeological_sites_near(self, x, y, z, radius=5):
        """Get archaeological sites within a certain radius of coordinates"""
        nearby_sites = []
        
        for coords, site in self.archaeological_sites.items():
            distance = ((x - coords[0])**2 + (y - coords[1])**2 + (z - coords[2])**2)**0.5
            if distance <= radius:
                site_copy = site.copy()
                site_copy['coordinates'] = coords
                nearby_sites.append(site_copy)
        
        return nearby_sites
    
    def generate_random_discovery(self):
        """Generate a random historical discovery event"""
        discoveries = [
            "Ancient star charts revealing hidden jump routes",
            "Fossilized remains of unknown sentient species", 
            "Crystallized time fragments showing past events",
            "Dormant AI containing million-year-old memories",
            "Portal anchor points to lost dimensions",
            "Genetic templates of extinct civilizations",
            "Quantum fossils of impossible technologies",
            "Echo chambers preserving ancient voices"
        ]
        
        return {
            "discovery": random.choice(discoveries),
            "research_value": random.randint(500, 2000),
            "year_discovered": self.current_galactic_age,
            "significance": random.choice(["Archaeological", "Technological", "Historical"])
        }