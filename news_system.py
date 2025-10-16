"""
Galactic News System
Provides news feed and reporting functionality for galactic events
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from events import EventSystem, EventType

class NewsSystem:
    """Manages galactic news and reporting"""
    
    def __init__(self, event_system: EventSystem):
        self.event_system = event_system
        self.news_categories = {
            'breaking': 'Breaking News',
            'economic': 'Economic Reports',
            'political': 'Political Updates',
            'scientific': 'Scientific Discoveries',
            'military': 'Military Intelligence',
            'travel': 'Travel Advisories',
            'entertainment': 'Entertainment & Culture',
            'weather': 'Space Weather'
        }
        
        # News sources for flavor
        self.news_sources = [
            'Galactic News Network',
            'Interstellar Times',
            'Cosmic Chronicle',
            'Stellar Sentinel',
            'Nebula News',
            'Quantum Quill',
            'Void Voice',
            'Astral Observer',
            'Celestial Courier',
            'Orbital Observer'
        ]
    
    def get_breaking_news(self) -> List[Dict[str, Any]]:
        """Get breaking news items (high severity events)"""
        breaking_news = []
        
        for event in self.event_system.get_active_events():
            if event.severity >= 6:  # High severity events
                news_item = self.format_news_item(event, 'breaking')
                breaking_news.append(news_item)
        
        # Sort by severity (highest first)
        breaking_news.sort(key=lambda x: x['severity'], reverse=True)
        return breaking_news[:5]  # Top 5 breaking news items
    
    def get_category_news(self, category: str) -> List[Dict[str, Any]]:
        """Get news items for a specific category"""
        category_events = []
        
        for event in self.event_system.get_active_events():
            if self.event_type_to_category(event.event_type) == category:
                news_item = self.format_news_item(event, category)
                category_events.append(news_item)
        
        # Sort by timestamp (newest first)
        category_events.sort(key=lambda x: x['timestamp'], reverse=True)
        return category_events
    
    def get_all_news(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get all recent news items"""
        all_news = []
        
        # Get recent events from news feed
        recent_events = self.event_system.get_news_feed(limit)
        
        for event_data in recent_events:
            # Convert event data to news format
            news_item = {
                'timestamp': event_data['timestamp'],
                'headline': event_data['headline'],
                'description': event_data['description'],
                'category': self.event_type_to_category(event_data['type']),
                'severity': event_data['severity'],
                'source': random.choice(self.news_sources),
                'affected_systems': event_data.get('affected_systems', []),
                'is_breaking': event_data['severity'] >= 6
            }
            all_news.append(news_item)
        
        # Sort by timestamp (newest first)
        all_news.sort(key=lambda x: x['timestamp'], reverse=True)
        return all_news
    
    def format_news_item(self, event, category: str) -> Dict[str, Any]:
        """Format an event into a news item"""
        return {
            'timestamp': event.timestamp,
            'headline': self.generate_headline(event),
            'description': event.description,
            'category': category,
            'severity': event.severity,
            'source': random.choice(self.news_sources),
            'affected_systems': event.affected_systems,
            'is_breaking': event.severity >= 6,
            'event_type': event.event_type
        }
    
    def generate_headline(self, event) -> str:
        """Generate a catchy headline for an event"""
        headlines = {
            EventType.ECONOMIC: {
                'Mining Boom': [
                    'Mining Corporations Strike Gold Across Galaxy!',
                    'Record Yields Reported in Multiple Systems',
                    'Mining Boom Creates Economic Opportunities'
                ],
                'Agricultural Crisis': [
                    'Food Crisis Looms as Blight Spreads',
                    'Agricultural Worlds Face Devastating Crop Losses',
                    'Galaxy-Wide Food Shortage Feared'
                ],
                'Trade War': [
                    'Economic Warfare Escalates Between Factions',
                    'Trade Routes Disrupted by Political Tensions',
                    'Galactic Commerce Under Siege'
                ],
                'Technology Breakthrough': [
                    'Revolutionary Manufacturing Techniques Unveiled',
                    'Production Costs Plummet Across Industries',
                    'New Technology Promises Economic Revolution'
                ],
                'Pirate Raids': [
                    'Pirate Fleets Target Luxury Goods Convoys',
                    'Organized Crime Disrupts Trade Routes',
                    'Luxury Markets Hit by Pirate Activity'
                ],
                'Market Crash': [
                    'Speculation Bubble Bursts, Markets Plunge',
                    'Economic Instability Spreads Galaxy-Wide',
                    'Financial Crisis Rocks Interstellar Markets'
                ]
            },
            EventType.POLITICAL: {
                'Diplomatic Summit': [
                    'Peace Talks Begin Between Major Factions',
                    'Historic Summit Aims to End Long Conflicts',
                    'Diplomats Gather for Galaxy-Wide Peace Conference'
                ],
                'Government Overthrow': [
                    'Revolutionary Forces Seize Control',
                    'Political Instability Grips Major System',
                    'Government Overthrown in Surprise Coup'
                ],
                'Trade Agreement': [
                    'New Trade Pacts Boost Interstellar Commerce',
                    'Tariff Reductions Promise Economic Growth',
                    'Trade Barriers Fall in Historic Agreement'
                ],
                'Embargo Declaration': [
                    'Economic Embargo Declared Between Factions',
                    'Trade Routes Severed by Political Dispute',
                    'Embargo Threatens Regional Stability'
                ]
            },
            EventType.SCIENTIFIC: {
                'Ancient Technology Discovery': [
                    'Lost Civilization Technology Unearthed',
                    'Archaeologists Discover Advanced Ancient Tech',
                    'Precursor Technology Could Change Everything'
                ],
                'Quantum Anomaly': [
                    'Scientists Detect Strange Quantum Fluctuations',
                    'Space-Time Anomaly Puzzles Researchers',
                    'Quantum Disturbance Affects Local Systems'
                ],
                'Medical Breakthrough': [
                    'Revolutionary Medical Treatment Extends Lifespans',
                    'New Medicine Promises Longer, Healthier Lives',
                    'Medical Breakthrough Could Transform Society'
                ]
            },
            EventType.MILITARY: {
                'Border Skirmish': [
                    'Military Conflict Erupts Between Rival Factions',
                    'Border Dispute Escalates to Armed Conflict',
                    'Tensions Boil Over in Sector Dispute'
                ],
                'Fleet Mobilization': [
                    'Major Military Buildup Detected',
                    'Fleet Movements Raise Tension Levels',
                    'Military Forces Mobilize Across Sector'
                ],
                'Peace Treaty': [
                    'Warring Factions Sign Historic Peace Agreement',
                    'Military Tensions Ease with New Treaty',
                    'Peace Deal Ends Long-Standing Conflict'
                ]
            },
            EventType.NATURAL: {
                'Solar Flare': [
                    'Massive Solar Flare Disrupts Communications',
                    'Navigation Systems Affected by Solar Activity',
                    'Solar Storm Creates Galaxy-Wide Disruptions'
                ],
                'Asteroid Impact': [
                    'Large Asteroid Causes Widespread Damage',
                    'Infrastructure Destroyed in Asteroid Strike',
                    'Asteroid Impact Devastates Local Systems'
                ],
                'Nebula Formation': [
                    'New Nebula Creates Navigation Hazards',
                    'Beautiful but Dangerous Nebula Forms',
                    'Space Travel Disrupted by Nebula Formation'
                ]
            },
            EventType.SOCIAL: {
                'Cultural Festival': [
                    'Galaxy-Wide Cultural Celebration Begins',
                    'Festival Boosts Morale Across Systems',
                    'Cultural Event Promotes Interstellar Unity'
                ],
                'Labor Strike': [
                    'Workers Strike Across Multiple Systems',
                    'Production Disrupted by Labor Disputes',
                    'Strikes Threaten Economic Stability'
                ],
                'Celebrity Scandal': [
                    'Major Celebrity Involved in Scandal',
                    'Media Frenzy Over Celebrity Controversy',
                    'Scandal Rocks Entertainment Industry'
                ]
            },
            EventType.TRAVEL: {
                'Pirate Activity': [
                    'Increased Pirate Activity Makes Travel Dangerous',
                    'Pirates Target Shipping Lanes',
                    'Travel Advisory: Avoid Pirate-Infested Regions'
                ],
                'Navigation Beacon Failure': [
                    'Critical Navigation Beacons Malfunction',
                    'Travel Becomes More Difficult and Expensive',
                    'Navigation System Failures Disrupt Commerce'
                ],
                'Wormhole Discovery': [
                    'New Wormhole Provides Faster Travel',
                    'Revolutionary Travel Route Discovered',
                    'Wormhole Could Transform Interstellar Commerce'
                ],
                'Space Storm': [
                    'Massive Space Storm Creates Dangerous Conditions',
                    'Travel Advisory: Avoid Storm-Affected Regions',
                    'Space Weather Threatens Navigation'
                ]
            },
            EventType.TABLOID: {
                'Alien Romance Scandal': [
                    'Diplomat Caught in Alien Romance Scandal!',
                    'Inter-Species Romance Shocks Galaxy',
                    'Alien Affair Rocks Diplomatic Community'
                ],
                'Space Whale Sighting': [
                    'Rare Space Whales Spotted Near Tourist Destinations',
                    'Space Whale Sighting Boosts Local Tourism',
                    'Majestic Space Whales Captivate Observers'
                ],
                'Celebrity Wedding': [
                    'Galaxy-Famous Couple Announces Wedding',
                    'Celebrity Wedding Creates Media Spectacle',
                    'Star-Crossed Lovers Plan Galactic Wedding'
                ],
                'Mysterious Crop Circles': [
                    'Strange Patterns Appear in Agricultural Fields',
                    'Crop Circles Spark Conspiracy Theories',
                    'Mysterious Crop Circles Puzzle Scientists'
                ]
            }
        }
        
        event_headlines = headlines.get(event.event_type, {}).get(event.name, [])
        if event_headlines:
            return random.choice(event_headlines)
        else:
            return event.name
    
    def event_type_to_category(self, event_type: str) -> str:
        """Convert event type to news category"""
        mapping = {
            EventType.ECONOMIC: 'economic',
            EventType.POLITICAL: 'political',
            EventType.SCIENTIFIC: 'scientific',
            EventType.MILITARY: 'military',
            EventType.NATURAL: 'weather',
            EventType.SOCIAL: 'entertainment',
            EventType.TRAVEL: 'travel',
            EventType.TABLOID: 'entertainment'
        }
        return mapping.get(event_type, 'breaking')
    
    def get_travel_advisories(self) -> List[Dict[str, Any]]:
        """Get current travel advisories"""
        advisories = []
        
        # Get dangerous regions
        dangerous_regions = self.event_system.get_dangerous_regions()
        
        for center, region_data in dangerous_regions.items():
            advisory = {
                'type': 'dangerous_region',
                'location': center,
                'threat_level': region_data['threat_level'],
                'radius': region_data['radius'],
                'description': region_data['description'],
                'recommendation': self.get_travel_recommendation(region_data['threat_level'])
            }
            advisories.append(advisory)
        
        # Get travel-related events
        for event in self.event_system.get_active_events():
            if event.event_type == EventType.TRAVEL:
                advisory = {
                    'type': 'event',
                    'name': event.name,
                    'description': event.description,
                    'severity': event.severity,
                    'affected_systems': event.affected_systems,
                    'recommendation': self.get_travel_recommendation(event.severity)
                }
                advisories.append(advisory)
        
        return advisories
    
    def get_travel_recommendation(self, threat_level: int) -> str:
        """Get travel recommendation based on threat level"""
        if threat_level >= 8:
            return "AVOID - Extremely dangerous conditions"
        elif threat_level >= 6:
            return "CAUTION - High risk, travel at your own peril"
        elif threat_level >= 4:
            return "WARNING - Moderate risk, exercise caution"
        elif threat_level >= 2:
            return "ADVISORY - Minor risks, stay alert"
        else:
            return "CLEAR - Safe for travel"
    
    def get_market_analysis(self) -> List[Dict[str, Any]]:
        """Get market analysis based on current events"""
        analysis = []
        
        # Analyze economic events
        economic_events = [e for e in self.event_system.get_active_events() 
                          if e.event_type == EventType.ECONOMIC]
        
        for event in economic_events:
            if 'commodities' in event.effects:
                commodities = event.effects['commodities']
                effect_type = event.effects['type']
                
                if effect_type in ['supply_increase', 'supply_decrease']:
                    trend = 'increasing' if effect_type == 'supply_increase' else 'decreasing'
                    analysis.append({
                        'type': 'supply_trend',
                        'commodities': commodities if commodities != 'all' else 'All commodities',
                        'trend': trend,
                        'reason': event.description,
                        'impact': 'high' if event.severity >= 6 else 'moderate'
                    })
                
                elif effect_type in ['price_increase', 'price_decrease']:
                    trend = 'rising' if effect_type == 'price_increase' else 'falling'
                    analysis.append({
                        'type': 'price_trend',
                        'commodities': commodities if commodities != 'all' else 'All commodities',
                        'trend': trend,
                        'reason': event.description,
                        'impact': 'high' if event.severity >= 6 else 'moderate'
                    })
        
        return analysis
    
    def generate_news_summary(self) -> str:
        """Generate a summary of current galactic news"""
        breaking_news = self.get_breaking_news()
        all_news = self.get_all_news(10)
        
        summary = "=== GALACTIC NEWS SUMMARY ===\n\n"
        
        if breaking_news:
            summary += "🚨 BREAKING NEWS:\n"
            for news in breaking_news[:3]:
                summary += f"• {news['headline']}\n"
            summary += "\n"
        
        # Group news by category
        categories = {}
        for news in all_news:
            category = news['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(news)
        
        for category, news_list in categories.items():
            if news_list:
                category_name = self.news_categories.get(category, category.title())
                summary += f"{category_name.upper()}:\n"
                for news in news_list[:2]:  # Top 2 per category
                    summary += f"• {news['headline']}\n"
                summary += "\n"
        
        return summary
    
    def get_news_by_system(self, system_name: str) -> List[Dict[str, Any]]:
        """Get news items affecting a specific system"""
        system_news = []
        
        for news in self.get_all_news():
            if system_name in news.get('affected_systems', []):
                system_news.append(news)
        
        return system_news
    
    def get_news_statistics(self) -> Dict[str, Any]:
        """Get statistics about current news"""
        all_news = self.get_all_news()
        
        stats = {
            'total_news_items': len(all_news),
            'breaking_news_count': len(self.get_breaking_news()),
            'categories': {},
            'severity_distribution': {i: 0 for i in range(1, 11)},
            'recent_activity': 0
        }
        
        # Count by category
        for news in all_news:
            category = news['category']
            stats['categories'][category] = stats['categories'].get(category, 0) + 1
            stats['severity_distribution'][news['severity']] += 1
        
        # Count recent activity (last 24 hours)
        recent_time = datetime.now() - timedelta(hours=24)
        for news in all_news:
            if news['timestamp'] > recent_time:
                stats['recent_activity'] += 1
        
        return stats
