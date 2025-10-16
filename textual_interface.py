#!/usr/bin/env python3
"""
Modern ASCII Interface using Textual
Retro look with modern functionality - mouse support, windows, etc.
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, Grid, ScrollableContainer
from textual.widgets import (
    Header, Footer, Static, Button, DataTable, ListView, ListItem, 
    Label, Input, TextArea, Tree, ProgressBar, Tabs, Tab, 
    Collapsible, RadioSet, RadioButton, Select, 
    Checkbox, Switch, Log, Pretty, Rule, Markdown
)
from textual.screen import Screen, ModalScreen
from textual.binding import Binding
from textual.reactive import reactive
from textual.message import Message
import asyncio
from typing import Dict, List, Optional, Any
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.console import Console
from rich.align import Align

# Import your existing game modules
try:
    from game import Game
    from navigation import NavigationSystem
    from factions import FactionSystem
    from ai_bots import BotManager
    from galactic_history import GalacticHistory
    from characters import character_classes, character_backgrounds, create_character_stats
    GAME_AVAILABLE = True
except ImportError:
    GAME_AVAILABLE = False
    print("Game modules not found - running in demo mode")

class StatusBar(Static):
    """Top status bar showing credits, location, etc."""
    
    def __init__(self):
        super().__init__()
        self.credits = 10000
        self.location = "Deep Space"
        self.ship_name = "No Ship Selected"
        
    def compose(self) -> ComposeResult:
        yield Label(f"Credits: {self.credits:,} | Location: {self.location} | Ship: {self.ship_name}")
        
    def update_status(self, credits: int = None, location: str = None, ship: str = None):
        if credits is not None:
            self.credits = credits
        if location is not None:
            self.location = location
        if ship is not None:
            self.ship_name = ship
        self.query_one(Label).update(f"Credits: {self.credits:,} | Location: {self.location} | Ship: {self.ship_name}")

class MainMenu(Static):
    """Main menu with ASCII art header and navigation buttons"""
    
    def compose(self) -> ComposeResult:
        # ASCII Art Header
        header_text = """
╔════════════════════════════════════════════════════════════════════════════════╗
║                    GALACTIC EMPIRE MANAGEMENT SYSTEM                          ║
║                                                                                ║
║    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░    ║
║    ░███████╗███╗   ███╗██████╗ ██╗██████╗ ███████╗                          ║
║    ░██╔════╝████╗ ████║██╔══██╗██║██╔══██╗██╔════╝                          ║
║    ░█████╗  ██╔████╔██║██████╔╝██║██████╔╝█████╗                            ║
║    ░██╔══╝  ██║╚██╔╝██║██╔═══╝ ██║██╔══██╗██╔══╝                            ║
║    ░███████╗██║ ╚═╝ ██║██║     ██║██║  ██║███████╗                          ║
║    ░╚══════╝╚═╝     ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝                          ║
║    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░    ║
╚════════════════════════════════════════════════════════════════════════════════╝"""
        
        yield Static(header_text, id="header")
        yield Static("═" * 80, classes="rule")
        yield Static("COMMAND CENTER", classes="section_header")
        
        # Main menu buttons in a grid
        with Grid(id="menu_grid"):
            yield Button("🏭 Manufacturing", id="manufacturing", variant="primary")
            yield Button("📈 Market Trading", id="trading", variant="primary") 
            yield Button("🚀 Navigation", id="navigation", variant="primary")
            yield Button("🏗️ Station Management", id="stations", variant="primary")
            yield Button("🤖 AI Bots", id="bots", variant="primary")
            yield Button("⚔️ Faction Relations", id="factions", variant="primary")
            yield Button("🎓 Professions", id="professions", variant="primary")
            yield Button("🏛️ Archaeology", id="archaeology", variant="primary")
            yield Button("📰 Galactic News", id="news", variant="primary")
            yield Button("⚙️ Ship Builder", id="shipbuilder", variant="primary")
            yield Button("📊 Character Profile", id="character", variant="primary")
            yield Button("💾 Save & Exit", id="exit", variant="warning")

class NavigationScreen(Static):
    """Space navigation interface with 3D map"""
    
    def __init__(self, game_instance=None, **kwargs):
        super().__init__(**kwargs)
        self.game_instance = game_instance
    
    def compose(self) -> ComposeResult:
        yield Static("╔═══ NAVIGATION CONTROL ═══╗", id="nav_header")
        
        with Horizontal():
            # Left panel - Ship status and controls
            with Vertical(id="nav_left"):
                yield Static("🚀 SHIP STATUS", classes="section_header")
                
                # Get real ship data
                if self.game_instance and hasattr(self.game_instance, 'navigation') and self.game_instance.navigation.current_ship:
                    ship = self.game_instance.navigation.current_ship
                    ship_info = f"""Ship: {ship.name}
Class: {ship.ship_class}
Fuel: {ship.fuel}/{ship.max_fuel}
Location: {ship.coordinates}
Cargo: {sum(ship.cargo.values()) if ship.cargo else 0}/{ship.max_cargo}"""
                else:
                    ship_info = """Ship: Not Selected
Class: N/A
Fuel: N/A
Location: Deep Space
Cargo: N/A"""
                
                yield Static(ship_info, id="ship_status")
                
                yield Static("─" * 30, classes="rule")
                yield Button("🗺️ Local Map", id="local_map", variant="success")
                yield Button("🌌 Galaxy Overview", id="galaxy_map", variant="success") 
                yield Button("⛽ Refuel", id="refuel", variant="warning")
                yield Button("🎯 Jump to System", id="jump", variant="primary")
                
            # Right panel - Space map
            with Vertical(id="nav_right"):
                yield Static("🌌 LOCAL SPACE", classes="section_header")
                
                # Generate real local space map
                if self.game_instance and hasattr(self.game_instance, 'navigation') and self.game_instance.navigation.current_ship:
                    x, y, z = self.game_instance.navigation.current_ship.coordinates
                    
                    # Get nearby systems from real navigation data
                    try:
                        nearby = self.game_instance.navigation.galaxy.get_nearby_systems(x, y, z, 10)
                        map_lines = [
                            "┌─────────────────────────────────────────┐",
                            "│             STAR SYSTEM MAP             │",
                            "│                                         │"
                        ]
                        
                        for i, (system, distance) in enumerate(nearby[:6]):  # Show max 6 systems
                            name = system['name'][:12]  # Truncate long names
                            status = "✓" if system.get('visited', False) else "?"
                            map_lines.append(f"│    ⭐ {name:<12} [{status}] {distance:.1f}u   │")
                        
                        # Add current position
                        map_lines.extend([
                            "│                                         │",
                            f"│         🚀 YOU ARE HERE                 │",
                            f"│            {x, y, z}                   │",
                            "│                                         │",
                            "└─────────────────────────────────────────┘"
                        ])
                        
                        map_display = "\n".join(map_lines)
                    except:
                        map_display = """
    ┌─────────────────────────────────────────┐
    │             STAR SYSTEM MAP             │
    │                                         │
    │    ⭐ Navigation Data Loading...          │
    │                                         │
    │         🚀 YOU ARE HERE                 │
    │            Deep Space                   │
    │                                         │
    └─────────────────────────────────────────┘"""
                else:
                    map_display = """
    ┌─────────────────────────────────────────┐
    │             STAR SYSTEM MAP             │
    │                                         │
    │    No ship selected for navigation      │
    │                                         │
    │         Use Navigation -> Select Ship   │
    │                                         │
    └─────────────────────────────────────────┘"""
                
                yield Static(map_display, id="space_map")

class TradingScreen(Static):
    """Trading and marketplace interface"""
    
    def __init__(self, game_instance=None, **kwargs):
        super().__init__(**kwargs)
        self.game_instance = game_instance
    
    def compose(self) -> ComposeResult:
        yield Static("💰 GALACTIC COMMODITIES EXCHANGE", classes="screen_title")
        
        with Horizontal():
            # Market prices table
            with Vertical(id="market_panel"):
                yield Static("📈 MARKET PRICES", classes="section_header")
                table = DataTable()
                table.add_columns("Commodity", "Price", "Supply", "Trend")
                
                # Get real commodity data
                try:
                    from goods import commodities
                    import random
                    
                    # Get some random commodities for display
                    raw_materials = commodities.get("Raw Materials", [])[:5]
                    bio_materials = commodities.get("Bio-Materials and Agriculture", [])[:3]
                    all_items = raw_materials + bio_materials
                    
                    rows = []
                    for item in all_items:
                        base_price = item["value"]
                        # Add some market variation
                        market_price = base_price * random.randint(50, 200)
                        supply_levels = ["Critical", "Low", "Medium", "High", "Abundant"]
                        trends = ["↗️", "↘️", "→", "⬆️", "⬇️"]
                        
                        rows.append((
                            item["name"],
                            f"{market_price:,} cr",
                            random.choice(supply_levels),
                            random.choice(trends)
                        ))
                    
                    table.add_rows(rows)
                except ImportError:
                    table.add_rows([("No market data", "0 cr", "None", "→")])
                
                yield table
                
            # Trading controls
            with Vertical(id="trade_controls"):
                yield Static("🛒 TRADING", classes="section_header")
                yield Input(placeholder="Enter quantity...", id="quantity_input")
                yield Button("💳 Buy", id="buy_btn", variant="success")
                yield Button("💰 Sell", id="sell_btn", variant="error") 
                yield Static("─" * 30, classes="rule")
                yield Static("💼 YOUR INVENTORY", classes="section_header")
                
                # Show real inventory
                if self.game_instance and self.game_instance.inventory:
                    inventory_text = ""
                    for item, quantity in self.game_instance.inventory.items():
                        inventory_text += f"{item}: {quantity}\n"
                    inventory_text = inventory_text.rstrip() or "Inventory empty"
                else:
                    inventory_text = "No inventory data available"
                    
                yield Static(inventory_text, id="inventory")

class ArchaeologyScreen(Static):
    """Archaeological discovery interface"""
    
    def __init__(self, game_instance=None, **kwargs):
        super().__init__(**kwargs)
        self.game_instance = game_instance
    
    def compose(self) -> ComposeResult:
        yield Static("🏛️ GALACTIC ARCHAEOLOGY & HISTORY", classes="screen_title")
        
        with Horizontal():
            # Ancient civilizations list
            with Vertical(id="civ_panel"):
                yield Static("📜 ANCIENT CIVILIZATIONS", classes="section_header")
                
                # Get real archaeology data
                if self.game_instance and hasattr(self.game_instance, 'galactic_history'):
                    civs = []
                    try:
                        # Get discovered civilizations
                        for civ_name, civ_data in self.game_instance.galactic_history.civilizations.items():
                            discovered = civ_data.get('discovered', False)
                            era = civ_data.get('era', 'Unknown Era')
                            status_icon = "�" if discovered else "❓"
                            civs.append(f"{status_icon} {civ_name} - {era}")
                        
                        if not civs:
                            civs = ["No civilizations discovered yet", "Explore and excavate to uncover history"]
                    except:
                        civs = [
                            "�🔮 Zenthorian Empire - Crystal Age",
                            "🌊 Oreon Civilization - Aquatic Dominion", 
                            "⭐ Myridian Builders - Stellar Navigation",
                            "🧠 Aetheris Collective - Consciousness Transfer",
                            "🏗️ Garnathans of Vorex - Living Architecture"
                        ]
                else:
                    civs = [
                        "🔮 Zenthorian Empire - Crystal Age",
                        "🌊 Oreon Civilization - Aquatic Dominion", 
                        "⭐ Myridian Builders - Stellar Navigation",
                        "🧠 Aetheris Collective - Consciousness Transfer",
                        "🏗️ Garnathans of Vorex - Living Architecture"
                    ]
                
                civ_list = ListView(*[ListItem(Label(civ)) for civ in civs])
                yield civ_list
                
            # Excavation controls  
            with Vertical(id="excavation_panel"):
                yield Static("⛏️ EXCAVATION", classes="section_header")
                yield Button("🔍 Scan for Sites", id="scan_sites", variant="primary")
                yield Button("⛏️ Excavate Here", id="excavate", variant="warning")
                yield Rule()
                yield Static("🏺 DISCOVERED ARTIFACTS", classes="section_header")
                
                # Get real artifact data
                if (self.game_instance and 
                    hasattr(self.game_instance, 'character') and 
                    hasattr(self.game_instance.character, 'inventory') and 
                    'artifacts' in self.game_instance.character.inventory):
                    
                    artifacts = self.game_instance.character.inventory['artifacts']
                    if artifacts:
                        artifact_text = "\n".join([f"• {name} ({qty}x)" for name, qty in artifacts.items()])
                    else:
                        artifact_text = "No artifacts discovered yet\nExcavate archaeological sites to find ancient relics"
                else:
                    artifact_text = """Ancient Crystal Resonator
Myridian Star Map Fragment
Etherfire Containment Unit
Zenthorian Memory Core"""
                
                yield Static(artifact_text, id="artifacts")
                yield Static("─" * 30, classes="rule")
                
                # Get excavation progress
                progress = 0
                if (self.game_instance and 
                    hasattr(self.game_instance, 'character') and 
                    hasattr(self.game_instance.character, 'excavation_progress')):
                    progress = self.game_instance.character.excavation_progress
                
                yield ProgressBar(total=100, value=progress, id="excavation_progress")
                yield Static(f"Excavation Progress: {progress}%", id="progress_text")

class CharacterScreen(Static):
    """Character profile and progression"""
    
    def __init__(self, game_instance=None, **kwargs):
        super().__init__(**kwargs)
        self.game_instance = game_instance
    
    def compose(self) -> ComposeResult:
        yield Static("👤 CHARACTER PROFILE", classes="screen_title")
        
        with Grid(id="character_grid"):
            # Basic info
            with Container(id="basic_info"):
                yield Static("📋 BASIC INFO", classes="section_header")
                
                # Get real game data
                if self.game_instance:
                    commander_name = self.game_instance.player_name or "Unknown Commander"
                    char_class = self.game_instance.character_class or "Unassigned"
                    char_background = self.game_instance.character_background or "Unknown"
                    credits = self.game_instance.credits or 0
                    
                    # Get profession info
                    profession_info = "None"
                    if hasattr(self.game_instance, 'profession_system') and self.game_instance.profession_system:
                        prof = self.game_instance.profession_system.character_profession
                        if prof:
                            level = self.game_instance.profession_system.profession_levels.get(prof, 1)
                            xp = self.game_instance.profession_system.profession_experience.get(prof, 0)
                            profession_info = f"{prof} (Level {level}, {xp} XP)"
                    
                    profile = f"""Commander: {commander_name}
Class: {char_class}  
Background: {char_background}
Profession: {profession_info}

Credits: {credits:,}
Ships Owned: {len(self.game_instance.owned_ships)}
Stations Owned: {len(self.game_instance.owned_stations)}"""
                else:
                    profile = "Game data unavailable"
                    
                yield Static(profile, id="profile_text")
                
            # Skills and stats
            with Container(id="skills_panel"):
                yield Static("⚡ ABILITIES & SKILLS", classes="section_header")
                
                if self.game_instance and self.game_instance.character_stats:
                    skills_text = ""
                    for stat_name, value in self.game_instance.character_stats.items():
                        bar = "█" * value + "░" * (10 - value)
                        skills_text += f"{stat_name.title()}: {bar} {value}/10\n"
                    skills_text = skills_text.rstrip()
                else:
                    skills_text = "Character stats not available"
                    
                yield Static(skills_text, id="skills_display")

class ManufacturingScreen(Static):
    """Manufacturing platforms interface"""
    
    def __init__(self, game_instance=None, **kwargs):
        super().__init__(**kwargs)
        self.game_instance = game_instance
        self.selected_platform = None
        self.platform_names = []
        
        # Load platforms during initialization
        try:
            from manufacturing import industrial_platforms
            self.platform_names = list(industrial_platforms.keys())[:10]  # Show first 10
            self.selected_platform = self.platform_names[0] if self.platform_names else None
        except ImportError as e:
            print(f"Manufacturing import error: {e}")
        except Exception as e:
            print(f"Unexpected error loading platforms: {e}")
    
    def compose(self) -> ComposeResult:
        yield Static("🏭 MANUFACTURING PLATFORMS", classes="screen_title")
        
        with Horizontal():
            # Platform categories
            with Vertical(id="platform_categories"):
                yield Static("📋 AVAILABLE PLATFORMS", classes="section_header")
                
                # Use pre-loaded manufacturing platforms
                if self.platform_names:
                    platform_list = ListView(*[ListItem(Label(f"🏭 {name}")) for name in self.platform_names])
                else:
                    platform_list = ListView(ListItem(Label("❌ No platforms available - Check manufacturing.py")))
                
                yield platform_list
                
            # Platform details and purchase
            with Vertical(id="platform_details"):
                yield Static("🏗️ PLATFORM DETAILS", classes="section_header")
                
                # Show details of first platform
                details = "No platform data available"
                try:
                    if self.selected_platform:
                        from manufacturing import industrial_platforms
                        platform_data = industrial_platforms.get(self.selected_platform, {})
                        owned_count = 0
                        if self.game_instance and hasattr(self.game_instance, 'owned_platforms'):
                            owned_count = len(self.game_instance.owned_platforms)
                        elif self.game_instance and hasattr(self.game_instance, 'manufacturing'):
                            owned_count = len(getattr(self.game_instance.manufacturing, 'owned_platforms', []))
                        
                        details = f"""{self.selected_platform}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Category: {platform_data.get('category', 'Unknown')}
Type: {platform_data.get('type', 'Unknown')}
Cost: 2,500,000 credits

Description: 
{platform_data.get('description', 'No description available')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Your Owned Platforms: {owned_count}
Daily Income: +{owned_count * 50000:,} credits"""
                    else:
                        details = """No Platform Selected
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Select a platform from the list to:
• View detailed specifications
• Purchase manufacturing rights  
• Manage existing platforms
• View income projections

Manufacturing platforms generate
passive income and resources for
your galactic empire."""
                        
                except Exception as e:
                    details = f"Error loading platform data: {str(e)}"
                    
                yield Static(details, id="platform_info")
                
                yield Static("─" * 40, classes="rule")
                yield Button("💳 Purchase Platform", id="buy_platform", variant="success")
                yield Button("📊 View Platform Stats", id="view_platform_stats", variant="primary")
                yield Button("🔧 Manage Platforms", id="manage_platforms", variant="primary")

class StationScreen(Static):
    """Space station management interface"""
    
    def __init__(self, game_instance=None, **kwargs):
        super().__init__(**kwargs)
        self.game_instance = game_instance
    
    def compose(self) -> ComposeResult:
        yield Static("🏗️ SPACE STATION MANAGEMENT", classes="screen_title")
        
        with Horizontal():
            # Station list
            with Vertical(id="station_list"):
                yield Static("🗺️ GALAXY STATIONS", classes="section_header")
                
                # Get real station data
                if self.game_instance and hasattr(self.game_instance, 'space_stations'):
                    stations = []
                    for station_id, station in self.game_instance.space_stations.stations.items():
                        name = getattr(station, 'name', f'Station-{station_id}')
                        station_type = getattr(station, 'station_type', 'Unknown')
                        owner = getattr(station, 'owner', None)
                        
                        status_icon = "🏗️" if owner == self.game_instance.character.name else "🔒"
                        ownership = "OWNED" if owner == self.game_instance.character.name else "AVAILABLE"
                        
                        stations.append(f"{status_icon} {name} [{station_type}] - {ownership}")
                    
                    if not stations:
                        stations = ["No stations discovered yet", "Explore systems to find stations"]
                else:
                    stations = [
                        "🏗️ Orbital Shipyard Alpha - AVAILABLE",
                        "🔬 Research Station Beta - AVAILABLE", 
                        "⛽ Fuel Depot Gamma - AVAILABLE",
                        "🛡️ Defense Platform Delta - AVAILABLE",
                        "🏪 Trading Post Epsilon - AVAILABLE"
                    ]
                
                station_list = ListView(*[ListItem(Label(station)) for station in stations])
                yield station_list
                
            # Station management
            with Vertical(id="station_controls"):
                yield Static("⚙️ STATION CONTROL", classes="section_header")
                
                # Get detailed station info
                if self.game_instance and hasattr(self.game_instance, 'space_stations') and self.game_instance.space_stations.stations:
                    # Get first station for details
                    first_station = list(self.game_instance.space_stations.stations.values())[0]
                    name = getattr(first_station, 'name', 'Unknown Station')
                    status = getattr(first_station, 'status', 'Unknown')
                    owner = getattr(first_station, 'owner', 'Available')
                    cost = getattr(first_station, 'cost', 1000000)
                    services = getattr(first_station, 'services', ['Unknown'])
                    income = getattr(first_station, 'daily_income', 0)
                    
                    station_info = f"""{name}
Status: {status}
Owner: {owner}
Cost: {cost:,} credits
Services: {', '.join(services) if isinstance(services, list) else services}
Income: +{income:,} credits/day"""
                else:
                    station_info = """No Station Data Available

Space stations provide:
• Passive income generation
• Ship construction services
• Trade route endpoints
• Defensive capabilities
• Research facilities

Explore systems to discover
available stations for purchase."""
                
                yield Static(station_info, id="station_info")
                
                yield Static("─" * 30, classes="rule")
                yield Button("💰 Purchase Station", id="buy_station", variant="success")
                yield Button("🔧 Upgrade Station", id="upgrade_station", variant="primary")
                yield Button("💵 Collect Income", id="collect_income", variant="warning")

class BotsScreen(Static):
    """AI Bots status and interaction interface"""
    
    def __init__(self, game_instance=None, **kwargs):
        super().__init__(**kwargs)
        self.game_instance = game_instance
    
    def compose(self) -> ComposeResult:
        yield Static("🤖 AI BOT MANAGEMENT", classes="screen_title")
        
        with Horizontal():
            # Bot list
            with Vertical(id="bot_list"):
                yield Static("🤖 ACTIVE BOTS", classes="section_header")
                
                # Get real bot data from game instance
                if self.game_instance and hasattr(self.game_instance, 'ai_bots') and self.game_instance.ai_bots.active_bots:
                    bots = []
                    for bot_id, bot in self.game_instance.ai_bots.active_bots.items():
                        name = getattr(bot, 'name', f"Bot-{bot_id}")
                        bot_type = getattr(bot, 'bot_type', 'Unknown')
                        status = getattr(bot, 'status', 'IDLE')
                        bots.append(f"🤖 {name} - {bot_type} [{status}]")
                else:
                    bots = [
                        "No active AI bots deployed",
                        "Deploy bots to automate tasks:",
                        "• Trading routes",
                        "• Mining operations", 
                        "• System exploration",
                        "• Station management"
                    ]
                
                bot_list = ListView(*[ListItem(Label(bot)) for bot in bots])
                yield bot_list
                
            # Bot interaction
            with Vertical(id="bot_interaction"):
                yield Static("💬 BOT INTERACTION", classes="section_header")
                
                # Get detailed bot information
                if self.game_instance and hasattr(self.game_instance, 'ai_bots') and self.game_instance.ai_bots.active_bots:
                    # Get first bot for details
                    first_bot = list(self.game_instance.ai_bots.active_bots.values())[0]
                    name = getattr(first_bot, 'name', 'Unknown Bot')
                    bot_type = getattr(first_bot, 'bot_type', 'Unknown Type')
                    status = getattr(first_bot, 'status', 'UNKNOWN')
                    location = getattr(first_bot, 'location', 'Unknown Location')
                    task = getattr(first_bot, 'current_task', 'No current task')
                    reputation = getattr(first_bot, 'reputation', 0)
                    last_action = getattr(first_bot, 'last_action', 'No recent activity')
                    
                    bot_info = f"""{name}
Type: {bot_type}
Status: {status}
Location: {location}
Current Task: {task}
Reputation: {reputation:+d}
Last Activity: {last_action}"""
                else:
                    bot_info = """No Active Bots

Deploy AI bots to automate:
• Trading between systems
• Mining resource deposits  
• Exploring uncharted space
• Managing space stations
• Diplomatic missions

Bots work independently and
generate passive income while
you focus on strategic goals."""
                
                yield Static(bot_info, id="bot_info")
                
                yield Static("─" * 30, classes="rule")
                yield Button("💬 Talk to Bot", id="talk_bot", variant="primary")
                yield Button("🤝 Trade with Bot", id="trade_bot", variant="success")
                yield Button("📍 Track Bot", id="track_bot", variant="primary")

class GalacticEmpireApp(App):
    """Main application class"""
    
    CSS = """
    Screen {
        background: black;
        color: green;
    }
    
    .screen_title {
        dock: top;
        height: 3;
        content-align: center middle;
        text-style: bold;
        color: cyan;
        background: blue 10%;
    }
    
    .section_header {
        height: 2;
        text-style: bold;
        color: yellow;
        background: blue 20%;
        content-align: center middle;
    }
    
    #menu_grid {
        grid-size: 3 4;
        grid-gutter: 1 2;
        margin: 1;
        padding: 1;
        height: auto;
        width: 100%;
    }
    
    #header {
        dock: top;
        height: 12;
        color: cyan;
        text-style: bold;
        content-align: center middle;
    }
    
    StatusBar {
        dock: top;
        height: 1;
        background: blue;
        color: white;
    }
    
    Button {
        min-height: 3;
        height: 3;
        min-width: 20;
        width: 100%;
        margin: 0 1;
        content-align: center middle;
    }
    
    Button:focus {
        text-style: none;
        background: $primary;
        color: white;
    }
    
    Button:hover {
        text-style: none;
        background: $primary;
        color: white;
    }
    
    Button.-primary {
        background: $primary;
        color: white;
        text-style: none;
    }
    
    DataTable {
        height: 15;
    }
    
    ListView {
        height: 20;
    }
    
    #nav_left {
        width: 30%;
        padding: 1;
        border: solid green;
    }
    
    #nav_right {
        width: 70%;
        padding: 1;
        border: solid cyan;  
    }
    
    #space_map {
        height: 18;
        color: white;
        background: black;
    }

    #nav_left Button {
        width: 100%;
        min-width: 15;
        height: 3;
        margin: 1 0;
    }

    #trade_controls Button {
        width: 100%;
        height: 3;
        margin: 1 0;
    }

    #excavation_panel Button {
        width: 100%;
        height: 3;
        margin: 1 0;
    }

    #platform_categories {
        width: 40%;
        padding: 1;
        border: solid yellow;
    }

    #platform_details {
        width: 60%;
        padding: 1; 
        border: solid green;
    }

    #platform_details Button {
        width: 100%;
        height: 3;
        margin: 1 0;
    }

    #station_list {
        width: 40%;
        padding: 1;
        border: solid cyan;
    }

    #station_controls {
        width: 60%;
        padding: 1;
        border: solid blue;
    }

    #station_controls Button {
        width: 100%;
        height: 3;
        margin: 1 0;
    }

    #bot_list {
        width: 40%;
        padding: 1;
        border: solid magenta;
    }

    #bot_interaction {
        width: 60%;
        padding: 1;
        border: solid red;
    }

    #bot_interaction Button {
        width: 100%;
        height: 3;
        margin: 1 0;
    }

    #character_grid {
        grid-size: 2 1;
        grid-gutter: 1 1;
        margin: 1;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("m", "show_main_menu", "Main Menu"),
        Binding("n", "show_navigation", "Navigation"),
        Binding("t", "show_trading", "Trading"),
        Binding("a", "show_archaeology", "Archaeology"),
        Binding("c", "show_character", "Character"),
        Binding("f", "show_manufacturing", "Manufacturing"),
        Binding("s", "show_stations", "Stations"),
        Binding("b", "show_bots", "AI Bots"),
        Binding("f1", "show_help", "Help"),
    ]
    
    def __init__(self):
        super().__init__()
        self.current_content = "main_menu"
        if GAME_AVAILABLE:
            self.game_instance = Game()
            # Initialize game if not already done
            if not hasattr(self.game_instance, 'player_name') or not self.game_instance.player_name:
                self.initialize_game()
        else:
            self.game_instance = None
            
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)
        yield StatusBar()
        # Create a container that will hold the main content
        with Container(id="main_container"):
            yield MainMenu(id="main_menu_initial")
        yield Footer()
        
    def on_mount(self) -> None:
        """App startup"""
        self.title = "Galactic Empire Management System"
        self.sub_title = "4X Space Strategy Game"
        self.update_status_bar()
        
    def initialize_game(self):
        """Initialize the game with default settings for interface mode"""
        if not self.game_instance:
            return
            
        # Set up basic game state for interface
        self.game_instance.player_name = "Commander"
        self.game_instance.character_class = "Explorer"
        self.game_instance.character_background = "Frontier Survivor"
        self.game_instance.credits = 15000
        
        # Initialize character stats
        self.game_instance.character_stats = {
            "leadership": 7,
            "technical": 8,
            "combat": 6,
            "diplomacy": 7,
            "exploration": 9,
            "trade": 6
        }
        
        # Initialize profession system if available
        if hasattr(self.game_instance, 'profession_system'):
            self.game_instance.profession_system.character_profession = "Galactic Historian"
            
    def update_status_bar(self):
        """Update the status bar with current game state"""
        if self.game_instance:
            credits = getattr(self.game_instance, 'credits', 0)
            location = "Deep Space"
            ship_name = "Aurora Ascendant"
            
            # Try to get real location data
            if hasattr(self.game_instance, 'navigation') and self.game_instance.navigation.current_ship:
                ship_name = self.game_instance.navigation.current_ship.name
                coords = self.game_instance.navigation.current_ship.coordinates
                location = f"({coords[0]}, {coords[1]}, {coords[2]})"
                
            try:
                status_bar = self.query_one(StatusBar)
                status_bar.update_status(credits=credits, location=location, ship=ship_name)
            except:
                pass
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks"""
        button_id = event.button.id
        
        if button_id == "manufacturing":
            self.action_show_manufacturing()
        elif button_id == "trading":
            self.action_show_trading()
        elif button_id == "navigation": 
            self.action_show_navigation()
        elif button_id == "stations":
            self.action_show_stations()
        elif button_id == "bots":
            self.action_show_bots()
        elif button_id == "factions":
            self.show_notification("⚔️ Faction relations coming soon!")
        elif button_id == "professions":
            self.show_notification("🎓 Profession system coming soon!")
        elif button_id == "archaeology":
            self.action_show_archaeology()
        elif button_id == "news":
            self.show_notification("📰 Galactic news coming soon!")
        elif button_id == "shipbuilder":
            self.show_notification("⚙️ Ship builder coming soon!")
        elif button_id == "character":
            self.action_show_character()
        elif button_id == "exit":
            self.exit()
            
        # Navigation screen buttons
        elif button_id == "local_map":
            self.handle_local_map()
        elif button_id == "galaxy_map":
            self.handle_galaxy_map()
        elif button_id == "refuel":
            self.handle_refuel()
        elif button_id == "jump":
            self.handle_jump()
            
        # Trading buttons
        elif button_id == "buy_btn":
            self.handle_buy_commodity()
        elif button_id == "sell_btn":
            self.handle_sell_commodity()
            
        # Archaeology buttons
        elif button_id == "scan_sites":
            self.handle_archaeological_scan()
        elif button_id == "excavate":
            self.handle_excavation()
            
        # Manufacturing buttons
        elif button_id == "buy_platform":
            self.handle_buy_platform()
        elif button_id == "view_platform_stats":
            self.show_notification("� Displaying platform statistics...")
        elif button_id == "manage_platforms":
            self.show_notification("🔧 Opening platform management console...")
            
        # Station management buttons  
        elif button_id == "buy_station":
            self.handle_buy_station()
        elif button_id == "upgrade_station":
            self.show_notification("🔧 Station upgrade initiated...")
        elif button_id == "collect_income":
            self.handle_collect_income()
            
        # Bot interaction buttons
        elif button_id == "talk_bot":
            self.handle_talk_to_bot()
        elif button_id == "trade_bot":
            self.show_notification("🤝 Opening trade interface with bot...")
        elif button_id == "track_bot":
            self.show_notification("📍 Tracking bot location...")
    
    def _switch_to_screen(self, new_screen_widget, screen_name):
        """Safely switch to a new screen using container replacement"""
        try:
            # Get the main container
            container = self.query_one("#main_container")
            
            # Remove all existing content from the container
            container.remove_children()
            
            # Use unique ID based on screen name to avoid conflicts
            import time
            unique_id = f"{screen_name}_{int(time.time() * 1000000) % 1000000}"
            new_screen_widget.id = unique_id
            
            # Mount the new screen in the container
            container.mount(new_screen_widget)
            self.current_content = screen_name
            
        except Exception as e:
            # Show error and fall back to main menu
            self.show_notification(f"Screen error: {str(e)[:40]}...")
            try:
                # Get container and reset to main menu
                container = self.query_one("#main_container")
                container.remove_children()
                unique_fallback_id = f"main_menu_{int(time.time() * 1000000) % 1000000}"
                fallback = MainMenu(id=unique_fallback_id)
                container.mount(fallback)
                self.current_content = "main_menu"
            except Exception:
                pass
        
    def action_show_main_menu(self) -> None:
        """Show main menu"""
        self._switch_to_screen(MainMenu(), "main_menu")
        
    def action_show_navigation(self) -> None:
        """Show navigation screen"""
        self._switch_to_screen(NavigationScreen(game_instance=self.game_instance), "navigation")
        
    def action_show_trading(self) -> None:
        """Show trading screen"""
        self._switch_to_screen(TradingScreen(game_instance=self.game_instance), "trading")
        
    def action_show_archaeology(self) -> None:
        """Show archaeology screen"""
        self._switch_to_screen(ArchaeologyScreen(game_instance=self.game_instance), "archaeology")
        
    def action_show_manufacturing(self) -> None:
        """Show manufacturing screen"""
        self._switch_to_screen(ManufacturingScreen(game_instance=self.game_instance), "manufacturing")
        
    def action_show_stations(self) -> None:
        """Show station management screen"""
        self._switch_to_screen(StationScreen(game_instance=self.game_instance), "stations")
        
    def action_show_bots(self) -> None:
        """Show AI bots screen"""
        self._switch_to_screen(BotsScreen(game_instance=self.game_instance), "bots")
        
    def action_show_character(self) -> None:
        """Show character screen"""
        self._switch_to_screen(CharacterScreen(game_instance=self.game_instance), "character")
        
    def action_show_help(self) -> None:
        """Show help information"""
        help_text = """
# Galactic Empire Management System - Help

## Mouse Controls
- Click buttons to navigate
- Drag to scroll content
- Right-click for context menus

## Keyboard Shortcuts  
- **Q**: Quit application
- **M**: Main Menu
- **N**: Navigation
- **T**: Trading
- **A**: Archaeology
- **C**: Character Profile
- **F1**: This help screen

## Game Features
- Build and manage your galactic empire
- Explore 30+ star systems
- Trade exotic commodities
- Discover ancient civilizations
- Interact with AI bots and factions
        """
        self.push_screen(HelpModal(help_text))
        
    def show_notification(self, message: str) -> None:
        """Show a temporary notification"""
        self.notify(message, title="System Message", timeout=3)
        
    def handle_archaeological_scan(self):
        """Handle archaeological site scanning"""
        if not self.game_instance or not hasattr(self.game_instance, 'galactic_history'):
            self.show_notification("🔍 Archaeological scanner offline")
            return
            
        # Simulate scanning with real game data if available
        self.show_notification("🔍 Scanning... Found 3 potential archaeological sites nearby!")
        
    def handle_excavation(self):
        """Handle archaeological excavation"""
        if not self.game_instance:
            self.show_notification("⛏️ Excavation equipment not available")
            return
            
        # Simulate excavation
        import random
        success = random.choice([True, False])
        if success:
            artifacts = ["Ancient Crystal Matrix", "Temporal Resonator", "Quantum Data Core"]
            artifact = random.choice(artifacts)
            self.show_notification(f"⛏️ Excavation successful! Discovered: {artifact}")
        else:
            self.show_notification("⛏️ Excavation incomplete. Continue digging...")
            
    def handle_buy_platform(self):
        """Handle manufacturing platform purchase"""
        if not self.game_instance:
            self.show_notification("💳 Transaction system offline")
            return
            
        cost = 2500000
        if self.game_instance.credits >= cost:
            self.game_instance.credits -= cost
            self.show_notification(f"🏭 Platform purchased! Remaining credits: {self.game_instance.credits:,}")
            self.update_status_bar()
        else:
            needed = cost - self.game_instance.credits
            self.show_notification(f"💳 Insufficient credits! Need {needed:,} more credits")
            
    def handle_buy_station(self):
        """Handle space station purchase"""
        if not self.game_instance:
            self.show_notification("💰 Transaction system offline")
            return
            
        cost = 5000000
        if self.game_instance.credits >= cost:
            self.game_instance.credits -= cost
            self.show_notification(f"🏗️ Station purchased! Remaining credits: {self.game_instance.credits:,}")
            self.update_status_bar()
        else:
            needed = cost - self.game_instance.credits
            self.show_notification(f"💰 Insufficient credits! Need {needed:,} more credits")
            
    def handle_collect_income(self):
        """Handle station income collection"""
        if not self.game_instance:
            self.show_notification("💵 Income system offline")
            return
            
        income = 50000
        self.game_instance.credits += income
        self.show_notification(f"💵 Collected {income:,} credits! Total: {self.game_instance.credits:,}")
        self.update_status_bar()
        
    def handle_talk_to_bot(self):
        """Handle bot conversation"""
        conversations = [
            "Captain Vex: 'Commander! I've found some excellent trading opportunities in the Vega system.'",
            "Dr. Cosmos: 'My research indicates unusual quantum fluctuations in nearby systems.'",
            "Explorer Zara: 'I've mapped three new systems with potential archaeological sites!'",
            "Industrialist Kane: 'Production efficiency is up 15% since last week, Commander.'",
            "Ambassador Nova: 'Diplomatic relations with the Centauri Alliance are improving.'"
        ]
        
        import random
        message = random.choice(conversations)
        self.show_notification(f"💬 {message}")
        
    def handle_local_map(self):
        """Handle local space map display"""
        if not self.game_instance:
            self.show_notification("🗺️ Navigation system offline")
            return
            
        nearby_systems = [
            "⭐ Proxima Alpha [2.3u]",
            "🏗️ Centauri Beta [4.1u]", 
            "🤖 Delta Vega [3.8u]",
            "🏛️ Ancient Ruins [5.2u]"
        ]
        self.show_notification(f"🗺️ Local scan complete! Found {len(nearby_systems)} systems nearby")
        
    def handle_galaxy_map(self):
        """Handle galaxy overview display"""
        if not self.game_instance:
            self.show_notification("🌌 Galaxy map offline")
            return
            
        self.show_notification("🌌 Galaxy Map: 30+ systems discovered, 15 visited, 8 with stations")
        
    def handle_refuel(self):
        """Handle ship refueling"""
        if not self.game_instance:
            self.show_notification("⛽ Fuel system offline")
            return
            
        fuel_cost = 500
        if self.game_instance.credits >= fuel_cost:
            self.game_instance.credits -= fuel_cost
            self.show_notification(f"⛽ Ship refueled! Cost: {fuel_cost} credits")
            self.update_status_bar()
        else:
            needed = fuel_cost - self.game_instance.credits
            self.show_notification(f"⛽ Insufficient credits for fuel! Need {needed} more credits")
            
    def handle_jump(self):
        """Handle hyperspace jump"""
        if not self.game_instance:
            self.show_notification("🎯 Jump drive offline")
            return
            
        jump_systems = ["Proxima Alpha", "Centauri Beta", "Vega Prime", "Wolf 359"]
        import random
        destination = random.choice(jump_systems)
        self.show_notification(f"🎯 Hyperspace jump initiated! Destination: {destination}")
        
        # Update location in status bar
        try:
            status_bar = self.query_one(StatusBar)
            status_bar.update_status(location=destination)
        except:
            pass
        
    def handle_buy_commodity(self):
        """Handle commodity purchase"""
        if not self.game_instance:
            self.show_notification("💳 Trading system offline")
            return
            
        # Get quantity from input if available
        try:
            quantity_input = self.query_one("#quantity_input", Input)
            quantity_str = quantity_input.value.strip()
            quantity = int(quantity_str) if quantity_str else 1
        except:
            quantity = 1
            
        # Sample commodity prices
        commodity = "Zerite Crystals"
        price_per_unit = 5234
        total_cost = price_per_unit * quantity
        
        if self.game_instance.credits >= total_cost:
            self.game_instance.credits -= total_cost
            self.show_notification(f"💳 Purchased {quantity} {commodity} for {total_cost:,} credits!")
            self.update_status_bar()
        else:
            needed = total_cost - self.game_instance.credits  
            self.show_notification(f"💳 Insufficient credits! Need {needed:,} more credits")
            
    def handle_sell_commodity(self):
        """Handle commodity sale"""
        if not self.game_instance:
            self.show_notification("💰 Trading system offline")
            return
            
        # Get quantity from input if available
        try:
            quantity_input = self.query_one("#quantity_input", Input)
            quantity_str = quantity_input.value.strip()
            quantity = int(quantity_str) if quantity_str else 1
        except:
            quantity = 1
            
        # Sample commodity sale
        commodity = "Quantum Sand"
        price_per_unit = 892
        total_income = price_per_unit * quantity
        
        self.game_instance.credits += total_income
        self.show_notification(f"💰 Sold {quantity} {commodity} for {total_income:,} credits!")
        self.update_status_bar()

class HelpModal(ModalScreen):
    """Help screen modal"""
    
    def __init__(self, help_text: str):
        super().__init__()
        self.help_text = help_text
        
    def compose(self) -> ComposeResult:
        yield Container(
            Markdown(self.help_text),
            Button("Close", variant="primary", id="close"),
            id="help_dialog"
        )
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close":
            self.app.pop_screen()

if __name__ == "__main__":
    app = GalacticEmpireApp()
    app.run()