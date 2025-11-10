"""
Galactic Event System
Generates random events that affect the game world
"""

import random
import math
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

class EventType:
    """Event type categories"""
    ECONOMIC = "economic"
    POLITICAL = "political"
    SCIENTIFIC = "scientific"
    MILITARY = "military"
    NATURAL = "natural"
    SOCIAL = "social"
    TRAVEL = "travel"
    TABLOID = "tabloid"
    SCANDAL = "scandal"

class Event:
    """Represents a single galactic event"""
    
    def __init__(self, event_type: str, name: str, description: str, 
                 effects: Dict[str, Any], duration: int = 0, 
                 affected_systems: List[str] = None, severity: int = 1):
        self.event_type = event_type
        self.name = name
        self.description = description
        self.effects = effects
        self.duration = duration  # How long the event lasts (0 = permanent)
        self.affected_systems = affected_systems or []
        self.severity = severity  # 1-10 scale
        self.timestamp = datetime.now()
        self.id = f"{event_type}_{random.randint(1000, 9999)}"
        
    def is_active(self, current_time: datetime) -> bool:
        """Check if event is still active"""
        if self.duration == 0:
            return True
        time_diff = (current_time - self.timestamp).total_seconds() / 3600  # hours
        return time_diff < self.duration

class EventSystem:
    """Main event system that generates and manages galactic events"""
    
    def __init__(self, game):
        self.game = game
        self.active_events: List[Event] = []
        self.event_history: List[Event] = []
        self.news_feed: List[Dict[str, Any]] = []
        self.dangerous_regions: Dict[Tuple[int, int, int], Dict[str, Any]] = {}
        
        # Event generation probabilities
        self.event_chances = {
            EventType.ECONOMIC: 0.25,
            EventType.POLITICAL: 0.15,
            EventType.SCIENTIFIC: 0.12,
            EventType.MILITARY: 0.08,
            EventType.NATURAL: 0.08,
            EventType.SOCIAL: 0.08,
            EventType.TRAVEL: 0.04,
            EventType.SCANDAL: 0.2
        }
        
        # Initialize with some starting events
        self.generate_initial_events()
    
    def generate_initial_events(self):
        """Generate some initial events when the game starts"""
        for _ in range(random.randint(2, 5)):
            event = self.generate_random_event()
            if event:
                self.add_event(event)
    
    def generate_random_event(self) -> Optional[Event]:
        """Generate a random event based on probabilities"""
        event_type = self.choose_event_type()
        
        if event_type == EventType.ECONOMIC:
            return self.generate_economic_event()
        elif event_type == EventType.POLITICAL:
            return self.generate_political_event()
        elif event_type == EventType.SCIENTIFIC:
            return self.generate_scientific_event()
        elif event_type == EventType.MILITARY:
            return self.generate_military_event()
        elif event_type == EventType.NATURAL:
            return self.generate_natural_event()
        elif event_type == EventType.SOCIAL:
            return self.generate_social_event()
        elif event_type == EventType.TRAVEL:
            return self.generate_travel_event()
        elif event_type == EventType.TABLOID:
            return self.generate_tabloid_event()
        elif event_type == EventType.SCANDAL:
            return self.generate_scandal_event()
        
        return None
    
    def choose_event_type(self) -> str:
        """Choose event type based on probabilities"""
        rand = random.random()
        cumulative = 0
        
        for event_type, probability in self.event_chances.items():
            cumulative += probability
            if rand <= cumulative:
                return event_type
        
        return EventType.ECONOMIC  # fallback
    
    def generate_economic_event(self) -> Event:
        """Generate economic events that affect supply/demand/prices"""
        events = [
            {
                'name': 'Mining Boom',
                'description': 'Rich ore deposits discovered in multiple systems! Mining corporations report record yields.',
                'effects': {
                    'type': 'supply_increase',
                    'commodities': ['Zerite Crystals', 'Crythium Ore', 'Gravossils', 'Carboxite Slabs'],
                    'multiplier': random.uniform(1.5, 2.5),
                    'systems': self.get_random_systems(3, 5)
                },
                'severity': random.randint(2, 4)
            },
            {
                'name': 'Agricultural Crisis',
                'description': 'Blight spreads across agricultural worlds, threatening food supplies galaxy-wide.',
                'effects': {
                    'type': 'supply_decrease',
                    'commodities': ['Ethergrain', 'Sporemilk', 'Glowfruit', 'Synthmeat Matrix'],
                    'multiplier': random.uniform(0.3, 0.7),
                    'systems': self.get_random_systems(2, 4)
                },
                'severity': random.randint(3, 6)
            },
            {
                'name': 'Trade War',
                'description': 'Political tensions escalate into economic warfare between major factions.',
                'effects': {
                    'type': 'price_increase',
                    'commodities': 'all',
                    'multiplier': random.uniform(1.2, 1.8),
                    'systems': self.get_random_systems(4, 8)
                },
                'severity': random.randint(4, 7)
            },
            {
                'name': 'Technology Breakthrough',
                'description': 'Revolutionary manufacturing techniques reduce production costs across industries.',
                'effects': {
                    'type': 'supply_increase',
                    'commodities': ['Quantum Sand', 'Phasemetal', 'Voidglass Shards', 'Neural Threadwire'],
                    'multiplier': random.uniform(1.3, 2.0),
                    'systems': self.get_random_systems(2, 4)
                },
                'severity': random.randint(2, 4)
            },
            {
                'name': 'Pirate Raids',
                'description': 'Organized pirate fleets target luxury goods convoys, creating supply shortages.',
                'effects': {
                    'type': 'supply_decrease',
                    'commodities': ['Aetherwine', 'Starweave Fabric', 'Chrono-music Scrolls', 'Solar Glass Jewelry'],
                    'multiplier': random.uniform(0.4, 0.8),
                    'systems': self.get_random_systems(3, 6)
                },
                'severity': random.randint(3, 5)
            },
            {
                'name': 'Market Crash',
                'description': 'Speculation bubble bursts, causing widespread economic instability.',
                'effects': {
                    'type': 'price_decrease',
                    'commodities': 'all',
                    'multiplier': random.uniform(0.6, 0.9),
                    'systems': self.get_random_systems(5, 10)
                },
                'severity': random.randint(5, 8)
            }
        ]
        
        event_data = random.choice(events)
        return Event(
            event_type=EventType.ECONOMIC,
            name=event_data['name'],
            description=event_data['description'],
            effects=event_data['effects'],
            duration=random.randint(24, 168),  # 1-7 days
            affected_systems=event_data['effects'].get('systems', []),
            severity=event_data['severity']
        )
    
    def generate_political_event(self) -> Event:
        """Generate political events"""
        events = [
            {
                'name': 'Diplomatic Summit',
                'description': 'Major factions convene for peace talks, potentially ending long-standing conflicts.',
                'effects': {
                    'type': 'faction_relations',
                    'change': random.uniform(5, 15),
                    'factions': self.get_random_factions(2, 4)
                },
                'severity': random.randint(3, 6)
            },
            {
                'name': 'Government Overthrow',
                'description': 'Revolutionary forces seize control of a major system, creating political instability.',
                'effects': {
                    'type': 'system_instability',
                    'threat_increase': random.randint(2, 5),
                    'systems': self.get_random_systems(1, 2)
                },
                'severity': random.randint(4, 7)
            },
            {
                'name': 'Trade Agreement',
                'description': 'New interstellar trade pacts reduce tariffs and boost commerce.',
                'effects': {
                    'type': 'trade_boost',
                    'multiplier': random.uniform(1.1, 1.3),
                    'systems': self.get_random_systems(3, 6)
                },
                'severity': random.randint(2, 4)
            },
            {
                'name': 'Embargo Declaration',
                'description': 'A major faction declares economic embargo against another, disrupting trade routes.',
                'effects': {
                    'type': 'trade_disruption',
                    'systems': self.get_random_systems(2, 4)
                },
                'severity': random.randint(5, 8)
            }
        ]
        
        event_data = random.choice(events)
        return Event(
            event_type=EventType.POLITICAL,
            name=event_data['name'],
            description=event_data['description'],
            effects=event_data['effects'],
            duration=random.randint(48, 336),  # 2-14 days
            affected_systems=event_data['effects'].get('systems', []),
            severity=event_data['severity']
        )
    
    def generate_scientific_event(self) -> Event:
        """Generate scientific discovery events"""
        events = [
            {
                'name': 'Ancient Technology Discovery',
                'description': 'Archaeologists uncover advanced technology from a lost civilization.',
                'effects': {
                    'type': 'technology_boost',
                    'systems': self.get_random_systems(1, 2)
                },
                'severity': random.randint(3, 6)
            },
            {
                'name': 'Quantum Anomaly',
                'description': 'Scientists detect strange quantum fluctuations affecting local space-time.',
                'effects': {
                    'type': 'space_anomaly',
                    'systems': self.get_random_systems(1, 3)
                },
                'severity': random.randint(4, 7)
            },
            {
                'name': 'Medical Breakthrough',
                'description': 'New medical treatments extend lifespans and improve quality of life.',
                'effects': {
                    'type': 'population_boost',
                    'multiplier': random.uniform(1.1, 1.2),
                    'systems': self.get_random_systems(2, 4)
                },
                'severity': random.randint(2, 4)
            }
        ]
        
        event_data = random.choice(events)
        return Event(
            event_type=EventType.SCIENTIFIC,
            name=event_data['name'],
            description=event_data['description'],
            effects=event_data['effects'],
            duration=random.randint(72, 720),  # 3-30 days
            affected_systems=event_data['effects'].get('systems', []),
            severity=event_data['severity']
        )
    
    def generate_military_event(self) -> Event:
        """Generate military conflict events"""
        events = [
            {
                'name': 'Border Skirmish',
                'description': 'Minor military conflict erupts between rival factions.',
                'effects': {
                    'type': 'military_conflict',
                    'threat_increase': random.randint(1, 3),
                    'systems': self.get_random_systems(2, 4)
                },
                'severity': random.randint(3, 5)
            },
            {
                'name': 'Fleet Mobilization',
                'description': 'Major military buildup detected, raising tensions across the sector.',
                'effects': {
                    'type': 'military_buildup',
                    'threat_increase': random.randint(2, 4),
                    'systems': self.get_random_systems(3, 6)
                },
                'severity': random.randint(4, 7)
            },
            {
                'name': 'Peace Treaty',
                'description': 'Warring factions sign peace agreement, reducing military tensions.',
                'effects': {
                    'type': 'military_reduction',
                    'threat_decrease': random.randint(1, 3),
                    'systems': self.get_random_systems(2, 5)
                },
                'severity': random.randint(2, 4)
            }
        ]
        
        event_data = random.choice(events)
        return Event(
            event_type=EventType.MILITARY,
            name=event_data['name'],
            description=event_data['description'],
            effects=event_data['effects'],
            duration=random.randint(24, 168),  # 1-7 days
            affected_systems=event_data['effects'].get('systems', []),
            severity=event_data['severity']
        )
    
    def generate_natural_event(self) -> Event:
        """Generate natural disaster events"""
        events = [
            {
                'name': 'Solar Flare',
                'description': 'Massive solar flare disrupts communications and navigation systems.',
                'effects': {
                    'type': 'communication_disruption',
                    'systems': self.get_random_systems(2, 4)
                },
                'severity': random.randint(3, 6)
            },
            {
                'name': 'Asteroid Impact',
                'description': 'Large asteroid impacts cause widespread damage to infrastructure.',
                'effects': {
                    'type': 'infrastructure_damage',
                    'systems': self.get_random_systems(1, 2)
                },
                'severity': random.randint(5, 8)
            },
            {
                'name': 'Nebula Formation',
                'description': 'New nebula forms, creating beautiful but dangerous navigation hazards.',
                'effects': {
                    'type': 'navigation_hazard',
                    'systems': self.get_random_systems(1, 3)
                },
                'severity': random.randint(2, 5)
            }
        ]
        
        event_data = random.choice(events)
        return Event(
            event_type=EventType.NATURAL,
            name=event_data['name'],
            description=event_data['description'],
            effects=event_data['effects'],
            duration=random.randint(48, 336),  # 2-14 days
            affected_systems=event_data['effects'].get('systems', []),
            severity=event_data['severity']
        )
    
    def generate_social_event(self) -> Event:
        """Generate social/cultural events"""
        events = [
            {
                'name': 'Cultural Festival',
                'description': 'Galaxy-wide cultural celebration boosts morale and tourism.',
                'effects': {
                    'type': 'morale_boost',
                    'systems': self.get_random_systems(3, 6)
                },
                'severity': random.randint(1, 3)
            },
            {
                'name': 'Labor Strike',
                'description': 'Workers across multiple systems go on strike, disrupting production.',
                'effects': {
                    'type': 'production_disruption',
                    'systems': self.get_random_systems(2, 4)
                },
                'severity': random.randint(3, 6)
            },
            {
                'name': 'Celebrity Scandal',
                'description': 'Major celebrity involved in scandal, creating media frenzy.',
                'effects': {
                    'type': 'media_frenzy',
                    'systems': self.get_random_systems(1, 3)
                },
                'severity': random.randint(2, 4)
            }
        ]
        
        event_data = random.choice(events)
        return Event(
            event_type=EventType.SOCIAL,
            name=event_data['name'],
            description=event_data['description'],
            effects=event_data['effects'],
            duration=random.randint(24, 168),  # 1-7 days
            affected_systems=event_data['effects'].get('systems', []),
            severity=event_data['severity']
        )
    
    def generate_travel_event(self) -> Event:
        """Generate events that affect space travel"""
        events = [
            {
                'name': 'Pirate Activity',
                'description': 'Increased pirate activity makes certain regions dangerous for travel.',
                'effects': {
                    'type': 'dangerous_region',
                    'threat_level': random.randint(6, 9),
                    'radius': random.randint(3, 8),
                    'center': self.get_random_coordinates()
                },
                'severity': random.randint(4, 7)
            },
            {
                'name': 'Navigation Beacon Failure',
                'description': 'Critical navigation beacons malfunction, making travel more difficult.',
                'effects': {
                    'type': 'navigation_difficulty',
                    'fuel_cost_multiplier': random.uniform(1.2, 1.5),
                    'systems': self.get_random_systems(2, 4)
                },
                'severity': random.randint(3, 5)
            },
            {
                'name': 'Wormhole Discovery',
                'description': 'New stable wormhole provides faster travel between distant systems.',
                'effects': {
                    'type': 'travel_boost',
                    'fuel_cost_multiplier': random.uniform(0.7, 0.9),
                    'systems': self.get_random_systems(2, 3)
                },
                'severity': random.randint(2, 4)
            },
            {
                'name': 'Space Storm',
                'description': 'Massive space storm creates dangerous conditions for travel.',
                'effects': {
                    'type': 'dangerous_region',
                    'threat_level': random.randint(7, 10),
                    'radius': random.randint(5, 12),
                    'center': self.get_random_coordinates()
                },
                'severity': random.randint(6, 9)
            }
        ]
        
        event_data = random.choice(events)
        return Event(
            event_type=EventType.TRAVEL,
            name=event_data['name'],
            description=event_data['description'],
            effects=event_data['effects'],
            duration=random.randint(12, 72),  # 12 hours to 3 days
            affected_systems=event_data['effects'].get('systems', []),
            severity=event_data['severity']
        )
    
    def generate_tabloid_event(self) -> Event:
        """Generate tabloid/entertainment events"""
        events = [
            {
                'name': 'Alien Romance Scandal',
                'description': 'Famous diplomat caught in romantic affair with alien ambassador!',
                'effects': {
                    'type': 'entertainment',
                    'systems': self.get_random_systems(1, 3)
                },
                'severity': random.randint(1, 3)
            },
            {
                'name': 'Space Whale Sighting',
                'description': 'Rare space whales spotted near tourist destinations, boosting local economy.',
                'effects': {
                    'type': 'tourism_boost',
                    'systems': self.get_random_systems(1, 2)
                },
                'severity': random.randint(1, 2)
            },
            {
                'name': 'Celebrity Wedding',
                'description': 'Galaxy-famous couple announces wedding, creating media spectacle.',
                'effects': {
                    'type': 'media_event',
                    'systems': self.get_random_systems(1, 2)
                },
                'severity': random.randint(1, 2)
            },
            {
                'name': 'Mysterious Crop Circles',
                'description': 'Strange patterns appear in agricultural fields, sparking conspiracy theories.',
                'effects': {
                    'type': 'mystery_event',
                    'systems': self.get_random_systems(1, 2)
                },
                'severity': random.randint(2, 4)
            }
        ]
        
        event_data = random.choice(events)
        return Event(
            event_type=EventType.TABLOID,
            name=event_data['name'],
            description=event_data['description'],
            effects=event_data['effects'],
            duration=random.randint(24, 168),  # 1-7 days
            affected_systems=event_data['effects'].get('systems', []),
            severity=event_data['severity']
        )
    
    def generate_scandal_event(self) -> Event:
        """Generate political scandal events (PG-13 to R-rated humor)"""
        scandals = [
            {
                'name': 'Diplomatic Hologram Leak',
                'description': 'Embarrassing holographic messages from a high-ranking diplomat are leaked, showing them practicing speeches in their underwear while arguing with their pet space-cat.',
                'effects': {
                    'type': 'reputation_damage',
                    'faction_relations': -10,
                    'systems': self.get_random_systems(2, 4)
                },
                'severity': random.randint(3, 6)
            },
            {
                'name': 'Senator\'s Secret Hobby',
                'description': 'A prominent senator is caught running an illegal "Alien Petting Zoo" in their basement, complete with smuggled creatures from restricted worlds.',
                'effects': {
                    'type': 'corruption_scandal',
                    'faction_relations': -15,
                    'systems': self.get_random_systems(1, 3)
                },
                'severity': random.randint(4, 7)
            },
            {
                'name': 'Ambassador\'s Dating App Debacle',
                'description': 'An ambassador\'s dating profile is discovered, featuring photoshopped images and the bio "Looking for someone who can handle my intergalactic baggage."',
                'effects': {
                    'type': 'embarrassment',
                    'faction_relations': -5,
                    'systems': self.get_random_systems(1, 2)
                },
                'severity': random.randint(2, 4)
            },
            {
                'name': 'Space Station Karaoke Scandal',
                'description': 'Security footage reveals a council member performing terrible karaoke at 3 AM while wearing nothing but a bathrobe and singing "Space Oddity" off-key.',
                'effects': {
                    'type': 'humiliation',
                    'faction_relations': -8,
                    'systems': self.get_random_systems(1, 2)
                },
                'severity': random.randint(3, 5)
            },
            {
                'name': 'Trade Minister\'s Crypto Scheme',
                'description': 'A trade minister is exposed for running a pyramid scheme involving "Quantum Coins" and convincing other politicians to invest their life savings.',
                'effects': {
                    'type': 'financial_scandal',
                    'faction_relations': -20,
                    'systems': self.get_random_systems(3, 6)
                },
                'severity': random.randint(6, 8)
            },
            {
                'name': 'Fleet Admiral\'s Collectible Obsession',
                'description': 'A fleet admiral is caught using military resources to hunt down rare "Space Pokemon" trading cards, deploying entire squadrons to search for holographic Charizards.',
                'effects': {
                    'type': 'misuse_of_resources',
                    'faction_relations': -12,
                    'systems': self.get_random_systems(2, 4)
                },
                'severity': random.randint(4, 6)
            },
            {
                'name': 'Diplomat\'s Food Delivery Addiction',
                'description': 'A diplomat is discovered to have spent their entire expense account on intergalactic food delivery, ordering 47 different types of alien pizza in one week.',
                'effects': {
                    'type': 'expense_scandal',
                    'faction_relations': -7,
                    'systems': self.get_random_systems(1, 2)
                },
                'severity': random.randint(2, 4)
            },
            {
                'name': 'Senator\'s Secret Fan Fiction',
                'description': 'A senator\'s secret fan fiction about themselves and their political rivals is leaked, complete with steamy romance scenes and dramatic plot twists.',
                'effects': {
                    'type': 'embarrassment',
                    'faction_relations': -10,
                    'systems': self.get_random_systems(2, 3)
                },
                'severity': random.randint(4, 6)
            },
            {
                'name': 'Ambassador\'s Gaming Addiction',
                'description': 'An ambassador is caught playing "Galactic Civilization" during important diplomatic meetings, having achieved a 2000-hour playtime while supposedly negotiating peace treaties.',
                'effects': {
                    'type': 'neglect_of_duty',
                    'faction_relations': -15,
                    'systems': self.get_random_systems(2, 4)
                },
                'severity': random.randint(5, 7)
            },
            {
                'name': 'Council Member\'s Social Media Meltdown',
                'description': 'A council member goes on a social media rant about their neighbor\'s "stupid space-lawn decorations" and accidentally posts it to their official government account.',
                'effects': {
                    'type': 'unprofessional_behavior',
                    'faction_relations': -8,
                    'systems': self.get_random_systems(1, 3)
                },
                'severity': random.randint(3, 5)
            },
            {
                'name': 'Trade Representative\'s Side Hustle',
                'description': 'A trade representative is exposed for running a "Space Uber" service using government vehicles, complete with a 5-star rating and customer reviews.',
                'effects': {
                    'type': 'misuse_of_government_resources',
                    'faction_relations': -12,
                    'systems': self.get_random_systems(2, 3)
                },
                'severity': random.randint(4, 6)
            },
            {
                'name': 'Fleet Commander\'s Pet Project',
                'description': 'A fleet commander is caught using military AI to create a "perfect dating algorithm" and has been secretly running a matchmaking service for lonely space pilots.',
                'effects': {
                    'type': 'misuse_of_technology',
                    'faction_relations': -10,
                    'systems': self.get_random_systems(1, 2)
                },
                'severity': random.randint(3, 5)
            },
            {
                'name': 'Diplomat\'s Secret Identity',
                'description': 'A diplomat is revealed to be secretly running a popular anonymous blog called "Diplomatic Disasters Daily" where they roast their own colleagues.',
                'effects': {
                    'type': 'betrayal',
                    'faction_relations': -18,
                    'systems': self.get_random_systems(3, 5)
                },
                'severity': random.randint(6, 8)
            },
            {
                'name': 'Senator\'s Holographic Therapy Sessions',
                'description': 'A senator\'s private therapy sessions are leaked, revealing they have been role-playing as a "space pirate" to deal with stress and have been practicing their "arrr" in meetings.',
                'effects': {
                    'type': 'privacy_violation',
                    'faction_relations': -6,
                    'systems': self.get_random_systems(1, 2)
                },
                'severity': random.randint(2, 4)
            },
            {
                'name': 'Ambassador\'s Competitive Eating Career',
                'description': 'An ambassador is discovered to have a secret career as a competitive eater, having won the "Galactic Hot Dog Championship" three years running under an alias.',
                'effects': {
                    'type': 'secret_double_life',
                    'faction_relations': -5,
                    'systems': self.get_random_systems(1, 2)
                },
                'severity': random.randint(2, 3)
            }
        ]
        
        scandal_data = random.choice(scandals)
        return Event(
            event_type=EventType.SCANDAL,
            name=scandal_data['name'],
            description=scandal_data['description'],
            effects=scandal_data['effects'],
            duration=random.randint(48, 336),  # 2-14 days
            affected_systems=scandal_data['effects'].get('systems', []),
            severity=scandal_data['severity']
        )
    
    def get_random_systems(self, min_count: int, max_count: int) -> List[str]:
        """Get random system names from the galaxy"""
        if not hasattr(self.game, 'navigation') or not self.game.navigation.galaxy:
            return []
        
        systems = list(self.game.navigation.galaxy.systems.keys())
        count = random.randint(min_count, max_count)
        selected = random.sample(systems, min(count, len(systems)))
        
        # Convert coordinates to system names
        system_names = []
        for coords in selected:
            system = self.game.navigation.galaxy.systems[coords]
            system_names.append(system['name'])
        
        return system_names
    
    def get_random_factions(self, min_count: int, max_count: int) -> List[str]:
        """Get random faction names"""
        if not hasattr(self.game, 'faction_system'):
            return []
        
        factions = list(self.game.faction_system.player_relations.keys())
        count = random.randint(min_count, max_count)
        return random.sample(factions, min(count, len(factions)))
    
    def get_random_coordinates(self) -> Tuple[int, int, int]:
        """Get random coordinates within galaxy bounds"""
        if not hasattr(self.game, 'navigation') or not self.game.navigation.galaxy:
            return (50, 50, 25)  # Default center
        
        galaxy = self.game.navigation.galaxy
        x = random.randint(10, galaxy.size_x - 10)
        y = random.randint(10, galaxy.size_y - 10)
        z = random.randint(5, galaxy.size_z - 5)
        return (x, y, z)
    
    def add_event(self, event: Event):
        """Add an event to the active events list"""
        self.active_events.append(event)
        self.add_to_news_feed(event)
        self.apply_event_effects(event)
    
    def apply_event_effects(self, event: Event):
        """Apply the effects of an event to the game world"""
        effects = event.effects
        
        if effects['type'] == 'supply_increase':
            self.apply_supply_change(effects, increase=True)
        elif effects['type'] == 'supply_decrease':
            self.apply_supply_change(effects, increase=False)
        elif effects['type'] == 'price_increase':
            self.apply_price_change(effects, increase=True)
        elif effects['type'] == 'price_decrease':
            self.apply_price_change(effects, increase=False)
        elif effects['type'] == 'dangerous_region':
            self.create_dangerous_region(effects)
        elif effects['type'] == 'navigation_difficulty':
            self.apply_navigation_effects(effects)
        elif effects['type'] == 'travel_boost':
            self.apply_travel_boost(effects)
        elif effects['type'] == 'system_instability':
            self.apply_system_instability(effects)
        elif effects['type'] == 'faction_relations':
            self.apply_faction_relations_change(effects)
        elif effects['type'] in ['reputation_damage', 'corruption_scandal', 'embarrassment', 'humiliation', 
                                'financial_scandal', 'misuse_of_resources', 'expense_scandal', 'neglect_of_duty',
                                'unprofessional_behavior', 'misuse_of_government_resources', 'misuse_of_technology',
                                'betrayal', 'privacy_violation', 'secret_double_life']:
            self.apply_scandal_effects(effects)
    
    def apply_supply_change(self, effects: Dict[str, Any], increase: bool):
        """Apply supply changes to markets"""
        if not hasattr(self.game, 'economy'):
            return
        
        commodities = effects['commodities']
        multiplier = effects['multiplier']
        systems = effects.get('systems', [])
        
        for system_name in systems:
            if system_name in self.game.economy.markets:
                market = self.game.economy.markets[system_name]
                
                if commodities == 'all':
                    target_commodities = list(market['supply'].keys())
                else:
                    target_commodities = [c for c in commodities if c in market['supply']]
                
                for commodity in target_commodities:
                    if increase:
                        market['supply'][commodity] = int(market['supply'][commodity] * multiplier)
                    else:
                        market['supply'][commodity] = int(market['supply'][commodity] * multiplier)
    
    def apply_price_change(self, effects: Dict[str, Any], increase: bool):
        """Apply price changes to markets"""
        if not hasattr(self.game, 'economy'):
            return
        
        commodities = effects['commodities']
        multiplier = effects['multiplier']
        systems = effects.get('systems', [])
        
        for system_name in systems:
            if system_name in self.game.economy.markets:
                market = self.game.economy.markets[system_name]
                
                if commodities == 'all':
                    target_commodities = list(market['prices'].keys())
                else:
                    target_commodities = [c for c in commodities if c in market['prices']]
                
                for commodity in target_commodities:
                    if increase:
                        market['prices'][commodity] = int(market['prices'][commodity] * multiplier)
                    else:
                        market['prices'][commodity] = int(market['prices'][commodity] * multiplier)
    
    def create_dangerous_region(self, effects: Dict[str, Any]):
        """Create a dangerous region of space"""
        center = effects['center']
        radius = effects['radius']
        threat_level = effects['threat_level']
        
        self.dangerous_regions[center] = {
            'threat_level': threat_level,
            'radius': radius,
            'description': f"Dangerous region with threat level {threat_level}",
            'created_by': 'event'
        }
    
    def apply_navigation_effects(self, effects: Dict[str, Any]):
        """Apply navigation difficulty effects"""
        # This would affect fuel costs for travel in affected systems
        # Implementation depends on how navigation system handles fuel costs
        pass
    
    def apply_travel_boost(self, effects: Dict[str, Any]):
        """Apply travel boost effects"""
        # This would reduce fuel costs for travel in affected systems
        pass
    
    def apply_system_instability(self, effects: Dict[str, Any]):
        """Apply system instability effects"""
        threat_increase = effects['threat_increase']
        systems = effects.get('systems', [])
        
        if not hasattr(self.game, 'navigation') or not self.game.navigation.galaxy:
            return
        
        for system_name in systems:
            # Find system by name and increase threat level
            for coords, system in self.game.navigation.galaxy.systems.items():
                if system['name'] == system_name:
                    system['threat_level'] = min(10, system['threat_level'] + threat_increase)
                    break
    
    def apply_faction_relations_change(self, effects: Dict[str, Any]):
        """Apply faction relations changes"""
        if not hasattr(self.game, 'faction_system'):
            return
        
        change = effects['change']
        factions = effects.get('factions', [])
        
        for faction in factions:
            if faction in self.game.faction_system.player_relations:
                current_rep = self.game.faction_system.player_relations[faction]
                self.game.faction_system.player_relations[faction] = max(-100, min(100, current_rep + change))
    
    def apply_scandal_effects(self, effects: Dict[str, Any]):
        """Apply scandal effects to faction relations"""
        if not hasattr(self.game, 'faction_system'):
            return
        
        # Get random factions to affect (scandals affect multiple factions)
        factions = self.get_random_factions(1, 3)
        relation_change = effects.get('faction_relations', -10)
        
        for faction in factions:
            if faction in self.game.faction_system.player_relations:
                current_rep = self.game.faction_system.player_relations[faction]
                # Scandals can have more dramatic effects
                new_rep = max(-100, min(100, current_rep + relation_change))
                self.game.faction_system.player_relations[faction] = new_rep
    
    def add_to_news_feed(self, event: Event):
        """Add event to news feed"""
        news_item = {
            'timestamp': event.timestamp,
            'type': event.event_type,
            'headline': event.name,
            'description': event.description,
            'severity': event.severity,
            'affected_systems': event.affected_systems
        }
        
        self.news_feed.append(news_item)
        
        # Keep only last 50 news items
        if len(self.news_feed) > 50:
            self.news_feed.pop(0)
    
    def update_events(self):
        """Update active events and generate new ones"""
        current_time = datetime.now()
        
        # Filter out any non-Event objects (safety check for corrupted data)
        self.active_events = [e for e in self.active_events if isinstance(e, Event)]
        
        # Remove expired events
        expired_events = []
        for event in self.active_events:
            if not event.is_active(current_time):
                expired_events.append(event)
        
        for event in expired_events:
            self.active_events.remove(event)
            self.event_history.append(event)
        
        # Generate new events occasionally
        if random.random() < 0.1:  # 10% chance per update
            new_event = self.generate_random_event()
            if new_event:
                self.add_event(new_event)
    
    def get_news_feed(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent news items"""
        return self.news_feed[-limit:]
    
    def get_active_events(self) -> List[Event]:
        """Get currently active events"""
        return self.active_events.copy()
    
    def is_location_dangerous(self, coordinates: Tuple[int, int, int]) -> bool:
        """Check if a location is in a dangerous region"""
        for center, region_data in self.dangerous_regions.items():
            distance = math.sqrt(
                (coordinates[0] - center[0])**2 +
                (coordinates[1] - center[1])**2 +
                (coordinates[2] - center[2])**2
            )
            if distance <= region_data['radius']:
                return True
        return False
    
    def get_dangerous_regions(self) -> Dict[Tuple[int, int, int], Dict[str, Any]]:
        """Get all dangerous regions"""
        return self.dangerous_regions.copy()
    
    def clear_dangerous_region(self, center: Tuple[int, int, int]):
        """Clear a dangerous region"""
        if center in self.dangerous_regions:
            del self.dangerous_regions[center]
