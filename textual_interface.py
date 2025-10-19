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
        self.credits = 0
        self.location = "Unknown"
        self.ship_name = "No Ship"
        
    def compose(self) -> ComposeResult:
        yield Label("🎭 Welcome to 7019! Create a character to begin...")
        
    def update_status(self, credits: int = None, location: str = None, ship: str = None, turn_info: dict = None):
        """Update with normal game status (character + ship active)"""
        if credits is not None:
            self.credits = credits
        if location is not None:
            self.location = location
        if ship is not None:
            self.ship_name = ship
        
        # Build status string with turn information
        status_parts = []
        if turn_info:
            status_parts.append(f"Turn: {turn_info['current_turn']}/{turn_info['max_turns']}")
            status_parts.append(f"Actions: {turn_info['actions_remaining']}/{turn_info['max_actions']}")
        
        status_parts.extend([
            f"Credits: {self.credits:,}",
            f"Location: {self.location}",
            f"Ship: {self.ship_name}"
        ])
        
        self.query_one(Label).update(" | ".join(status_parts))
    
    def update_message(self, message: str):
        """Update with a custom message"""
        self.query_one(Label).update(message)

# Character Creation Step Classes
class CharacterCreationCoordinator(Static):
    """Coordinates the multi-step character creation process"""
    
    def __init__(self, game_instance=None, **kwargs):
        super().__init__(**kwargs)
        self.game_instance = game_instance
        self.current_step = 0
        self.character_data = {
            'name': '',
            'species': '',
            'background': '', 
            'faction': '',
            'character_class': '',
            'research_paths': [],
            'stats': None
        }
        self.steps = [
            ('species', '🧬 Choose Species'),
            ('background', '🏛️ Choose Background'),
            ('faction', '⚔️ Choose Faction'),
            ('class', '🎯 Choose Class'),
            ('research', '🔬 Select Research Paths'),
            ('stats', '🎲 Roll Stats'),
            ('name', '📝 Enter Name'),
            ('confirm', '✅ Confirm Character')
        ]
    
    def compose(self) -> ComposeResult:
        yield Static("🎭 CHARACTER CREATION", classes="screen_title")
        
        # Progress indicator
        with Horizontal(id="progress_bar"):
            for i, (step_id, step_name) in enumerate(self.steps):
                status = "✅" if i < self.current_step else "⏳" if i == self.current_step else "⭕"
                yield Static(f"{status} {step_name}", classes="progress_step")
        
        # Current step content area
        with ScrollableContainer(id="step_content_area"):
            yield Static("", id="step_content")
            # Container for interactive elements
            with Vertical(id="interactive_content"):
                # Name input
                yield Input(placeholder="Enter your character name...", id="name_input", classes="hidden")
                # Stats buttons
                yield Button("🎲 Generate Stats", id="generate_stats_step", variant="primary", classes="hidden")
                yield Button("🔄 Reroll Stats", id="reroll_stats_step", variant="warning", classes="hidden")
                # Selection buttons (will be populated dynamically)
                with Vertical(id="selection_buttons", classes="hidden"):
                    pass
        
        # Navigation buttons
        with Horizontal(id="nav_buttons"):
            yield Button("⬅️ Back", id="step_back", variant="warning")
            yield Button("➡️ Next", id="step_next", variant="primary")
            yield Button("🏠 Cancel", id="cancel_creation", variant="error")
    
    def on_mount(self):
        """Initialize the display when mounted"""
        self.update_step_display()
    
    def update_step_display(self):
        """Update the display for the current step"""
        if self.current_step >= len(self.steps):
            return
            
        step_id, step_name = self.steps[self.current_step]
        content_widget = self.query_one("#step_content")
        
        # Hide all special widgets first
        try:
            self.query_one("#name_input").add_class("hidden")
            self.query_one("#generate_stats_step").add_class("hidden") 
            self.query_one("#reroll_stats_step").add_class("hidden")
            self.query_one("#selection_buttons").add_class("hidden")
        except:
            pass
        
        # Clear any existing selection buttons
        try:
            selection_container = self.query_one("#selection_buttons")
            selection_container.remove_children()
        except:
            pass
        
        if step_id == 'species':
            content_widget.update("🧬 Choose your species:")
            self.create_species_buttons()
        elif step_id == 'background':
            content_widget.update("🏛️ Choose your character background:")
            self.create_background_buttons()
        elif step_id == 'faction':
            content_widget.update("⚔️ Choose your starting faction allegiance:")
            self.create_faction_buttons()
        elif step_id == 'class':
            content_widget.update("🎯 Choose your character class:")
            self.create_class_buttons()
        elif step_id == 'research':
            content_widget.update("🔬 Select starting research interests (choose up to 3):")
            self.create_research_buttons()
        elif step_id == 'stats':
            content_widget.update(self.get_stats_content())
            # Show stats generation buttons
            try:
                self.query_one("#generate_stats_step").remove_class("hidden")
                if self.character_data['stats']:
                    self.query_one("#reroll_stats_step").remove_class("hidden")
            except:
                pass
        elif step_id == 'name':
            content_widget.update(self.get_name_content())
            # Show name input
            try:
                name_input = self.query_one("#name_input")
                name_input.remove_class("hidden")
                name_input.value = self.character_data['name']
            except:
                pass
        elif step_id == 'confirm':
            content_widget.update(self.get_confirm_content())
    
    def create_species_buttons(self):
        """Create buttons for species selection"""
        if not GAME_AVAILABLE:
            return
        
        try:
            from species import species_database, get_playable_species
            playable_species = get_playable_species()
            
            selection_container = self.query_one("#selection_buttons")
            selection_container.remove_class("hidden")
            
            for species_name in playable_species.keys():
                variant = "success" if species_name == self.character_data['species'] else "primary"
                btn = Button(f"🧬 {species_name}", id=f"select_species_{species_name}", variant=variant)
                selection_container.mount(btn)
        except Exception as e:
            pass
    
    def create_background_buttons(self):
        """Create buttons for background selection"""
        if not GAME_AVAILABLE:
            return
        
        try:
            from characters import character_backgrounds
            
            selection_container = self.query_one("#selection_buttons")
            selection_container.remove_class("hidden")
            
            for bg_name in character_backgrounds.keys():
                variant = "success" if bg_name == self.character_data['background'] else "primary"
                btn = Button(f"🏛️ {bg_name}", id=f"select_background_{bg_name}", variant=variant)
                selection_container.mount(btn)
        except Exception as e:
            pass
    
    def create_faction_buttons(self):
        """Create buttons for faction selection"""
        if not GAME_AVAILABLE:
            return
        
        try:
            from factions import factions
            
            selection_container = self.query_one("#selection_buttons")
            selection_container.remove_class("hidden")
            
            # Show first 6 factions
            for faction_name in list(factions.keys())[:6]:
                variant = "success" if faction_name == self.character_data['faction'] else "primary"
                btn = Button(f"⚔️ {faction_name}", id=f"select_faction_{faction_name}", variant=variant)
                selection_container.mount(btn)
        except Exception as e:
            pass
    
    def create_class_buttons(self):
        """Create buttons for class selection"""
        if not GAME_AVAILABLE:
            return
        
        try:
            from characters import character_classes
            
            selection_container = self.query_one("#selection_buttons")
            selection_container.remove_class("hidden")
            
            for class_name in character_classes.keys():
                variant = "success" if class_name == self.character_data['character_class'] else "primary"
                btn = Button(f"🎯 {class_name}", id=f"select_class_{class_name}", variant=variant)
                selection_container.mount(btn)
        except Exception as e:
            pass
    
    def create_research_buttons(self):
        """Create buttons for research path selection"""
        if not GAME_AVAILABLE:
            return
        
        try:
            from research import research_categories
            
            selection_container = self.query_one("#selection_buttons")
            selection_container.remove_class("hidden")
            
            # Show first 6 research categories
            for category in list(research_categories.keys())[:6]:
                selected = category in self.character_data['research_paths']
                variant = "success" if selected else "primary"
                icon = "✅" if selected else "⭕"
                btn = Button(f"{icon} {category}", id=f"toggle_research_{category}", variant=variant)
                selection_container.mount(btn)
                
            # Add status display
            status_text = f"Selected: {len(self.character_data['research_paths'])}/3"
            status_label = Static(status_text, id="research_status")
            selection_container.mount(status_label)
        except Exception as e:
            pass
    
    def get_species_content(self):
        if not GAME_AVAILABLE:
            return "Demo mode - species selection unavailable"
        
        from species import species_database, get_playable_species
        playable_species = get_playable_species()
        
        content = "🧬 Choose your species:\n\n"
        for species_name, species_data in playable_species.items():
            selected = "👉 " if species_name == self.character_data['species'] else "   "
            content += f"{selected}{species_name}: {species_data['description'][:60]}...\n"
        
        content += "\n💡 Click a species name to select it"
        return content
    
    def get_background_content(self):
        if not GAME_AVAILABLE:
            return "Demo mode - background selection unavailable"
        
        content = "🏛️ Choose your character background:\n\n"
        for bg_name, bg_data in character_backgrounds.items():
            selected = "👉 " if bg_name == self.character_data['background'] else "   "
            content += f"{selected}{bg_name}: {bg_data['description'][:60]}...\n"
        
        content += "\n💡 Click a background name to select it"
        return content
    
    def get_faction_content(self):
        if not GAME_AVAILABLE:
            return "Demo mode - faction selection unavailable"
        
        from factions import factions
        content = "⚔️ Choose your starting faction allegiance:\n\n"
        
        for faction_name, faction_data in list(factions.items())[:6]:  # Show first 6
            selected = "👉 " if faction_name == self.character_data['faction'] else "   "
            content += f"{selected}{faction_name}: {faction_data['description'][:50]}...\n"
        
        content += "\n💡 Click a faction name to select it"
        return content
    
    def get_class_content(self):
        if not GAME_AVAILABLE:
            return "Demo mode - class selection unavailable"
        
        content = "🎯 Choose your character class:\n\n"
        for class_name, class_data in character_classes.items():
            selected = "👉 " if class_name == self.character_data['character_class'] else "   "
            content += f"{selected}{class_name}: {class_data['description'][:60]}...\n"
        
        content += "\n💡 Click a class name to select it"
        return content
    
    def get_research_content(self):
        if not GAME_AVAILABLE:
            return "Demo mode - research selection unavailable"
        
        from research import research_categories
        content = "🔬 Select starting research interests (choose up to 3):\n\n"
        
        for category in list(research_categories.keys())[:6]:  # Show first 6 categories
            selected = "✅ " if category in self.character_data['research_paths'] else "☐ "
            content += f"{selected}{category}\n"
        
        content += f"\nSelected: {len(self.character_data['research_paths'])}/3"
        content += "\n💡 Click categories to toggle selection"
        return content
    
    def get_stats_content(self):
        content = "🎲 Generate your character stats:\n\n"
        
        if self.character_data['stats']:
            content += "Current stats:\n"
            for stat, value in self.character_data['stats'].items():
                content += f"{stat}: {value}\n"
            content += "\n🔄 Click 'Reroll' to generate new stats"
        else:
            content += "Click 'Generate Stats' to create your character's attributes"
        
        return content
    
    def get_name_content(self):
        content = "📝 Enter your character name:\n\n"
        if self.character_data['name']:
            content += f"Current name: {self.character_data['name']}\n\n"
        content += "� Enter your name in the input field below"
        return content
    
    def get_confirm_content(self):
        content = "✅ Confirm your character:\n\n"
        content += f"Name: {self.character_data['name']}\n"
        content += f"Species: {self.character_data['species']}\n"
        content += f"Background: {self.character_data['background']}\n"
        content += f"Faction: {self.character_data['faction']}\n"
        content += f"Class: {self.character_data['character_class']}\n"
        content += f"Research Paths: {', '.join(self.character_data['research_paths'])}\n\n"
        
        if self.character_data['stats']:
            content += "Stats:\n"
            for stat, value in self.character_data['stats'].items():
                content += f"  {stat}: {value}\n"
        
        content += "\n🎉 Ready to create your character!"
        return content
    
    def on_click(self, event):
        """Handle clicks on text content for selections"""
        # This is a simplified approach - in a full implementation, you'd use 
        # more sophisticated widgets like ListView or custom clickable widgets
        pass
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks within the coordinator"""
        button_id = event.button.id
        
        if button_id == "generate_stats_step":
            self.generate_character_stats()
        elif button_id == "reroll_stats_step":
            self.generate_character_stats()
        elif button_id.startswith("select_species_"):
            species_name = button_id.replace("select_species_", "")
            self.select_species(species_name)
        elif button_id.startswith("select_background_"):
            background_name = button_id.replace("select_background_", "")
            self.select_background(background_name)
        elif button_id.startswith("select_faction_"):
            faction_name = button_id.replace("select_faction_", "")
            self.select_faction(faction_name)
        elif button_id.startswith("select_class_"):
            class_name = button_id.replace("select_class_", "")
            self.select_class(class_name)
        elif button_id.startswith("toggle_research_"):
            research_path = button_id.replace("toggle_research_", "")
            self.toggle_research_path(research_path)
    
    def on_input_changed(self, event) -> None:
        """Handle input changes within the coordinator"""
        if event.input.id == "name_input":
            self.character_data['name'] = event.value
            self.update_step_display()
    
    def generate_character_stats(self):
        """Generate character stats"""
        if GAME_AVAILABLE:
            from characters import create_character_stats
            self.character_data['stats'] = create_character_stats()
            self.update_step_display()
    
    def select_species(self, species_name):
        """Select a species"""
        self.character_data['species'] = species_name
        self.update_step_display()
    
    def select_background(self, background_name):
        """Select a background"""
        self.character_data['background'] = background_name  
        self.update_step_display()
    
    def select_faction(self, faction_name):
        """Select a faction"""
        self.character_data['faction'] = faction_name
        self.update_step_display()
    
    def select_class(self, class_name):
        """Select a character class"""
        self.character_data['character_class'] = class_name
        self.update_step_display()
    
    def toggle_research_path(self, research_path):
        """Toggle a research path selection"""
        if research_path in self.character_data['research_paths']:
            self.character_data['research_paths'].remove(research_path)
        else:
            if len(self.character_data['research_paths']) < 3:
                self.character_data['research_paths'].append(research_path)
        self.update_step_display()

class CharacterCreationScreen(Static):
    """Legacy character creation interface - now redirects to new system"""
    
    def __init__(self, game_instance=None, **kwargs):
        super().__init__(**kwargs)
        self.game_instance = game_instance
        
    def compose(self) -> ComposeResult:
        yield CharacterCreationCoordinator(game_instance=self.game_instance)

class MainMenu(Static):
    """Main menu with ASCII art header and navigation buttons"""
    
    def __init__(self, game_instance=None, **kwargs):
        super().__init__(**kwargs)
        self.game_instance = game_instance
    
    def compose(self) -> ComposeResult:
        # ASCII Art Header
        header_text = """
╔════════════════════════════════════════════════════════════════════════════════╗
║                              7019 MANAGEMENT SYSTEM                            ║
║                                                                                ║
║    ░.    ███████╗ ██████╗  ██╗ █████╗                                          ║
║    ░.    ╚════██║██╔═████╗███║██╔══██╗                                         ║
║    ░         ██╔╝██║██╔██║╚██║╚██████║                                         ║
║    ░        ██╔╝ ████╔╝██║ ██║ ╚═══██║                                         ║
║    ░        ██║  ╚██████╔╝ ██║ █████╔╝                                         ║
║    ░        ╚═╝   ╚═════╝  ╚═╝ ╚════╝                                          ║
╚════════════════════════════════════════════════════════════════════════════════╝"""
        
        yield Static(header_text, id="header")
        yield Static("═" * 80, classes="rule")
        
        # Core Game Actions
        yield Static("CORE SYSTEMS", classes="section_header")
        with Grid(id="core_grid"):
            yield Button("🚀 Navigation", id="navigation", variant="primary")
            yield Button("📈 Trading", id="trading", variant="primary")
            yield Button("🏭 Manufacturing", id="manufacturing", variant="primary")
            yield Button("🏗️ Stations", id="stations", variant="primary")
            yield Button("🛸 Ships", id="ship_manager", variant="primary")
            yield Button("🏛️ Archaeology", id="archaeology", variant="primary")
        
        # Management & Information
        yield Static("MANAGEMENT", classes="section_header")
        with Grid(id="management_grid"):
            yield Button("🤖 AI Bots", id="bots", variant="primary")
            yield Button("⚔️ Factions", id="factions", variant="primary")
            yield Button("🎓 Professions", id="professions", variant="primary")
            yield Button("� News", id="news", variant="primary")
            yield Button("📊 Character", id="character", variant="primary")
            yield Button("� Activity Log", id="player_log", variant="primary")
        
        # Character & Game Control
        yield Static("GAME CONTROL", classes="section_header")
        with Grid(id="control_grid"):
            # Check if character already exists
            if self.game_instance and getattr(self.game_instance, 'character_created', False):
                yield Button("👤 Character Created", id="new_character", variant="default")
            else:
                yield Button("🎭 New Character", id="new_character", variant="success")
            yield Button("⏭️ End Turn", id="end_turn", variant="warning")
            yield Button("⚙️ Settings", id="game_settings", variant="default")
            yield Button("💾 Save & Exit", id="exit", variant="error")

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
                
                progress_bar = ProgressBar(total=100, id="excavation_progress")
                yield progress_bar
                yield Static(f"Excavation Progress: {progress}%", id="progress_text")
    
    def on_mount(self) -> None:
        """Update progress bar after mounting"""
        progress = 0
        if (self.game_instance and 
            hasattr(self.game_instance, 'character') and 
            hasattr(self.game_instance.character, 'excavation_progress')):
            progress = self.game_instance.character.excavation_progress
        
        try:
            progress_bar = self.query_one("#excavation_progress", ProgressBar)
            progress_bar.update(progress=progress)
        except Exception:
            pass  # Progress bar not found or other error

class CharacterScreen(Static):
    """Character profile and progression"""
    
    def __init__(self, game_instance=None, **kwargs):
        super().__init__(**kwargs)
        self.game_instance = game_instance
    
    def on_mount(self) -> None:
        """Called when the screen is mounted"""
        self.refresh_character_data()
        
    def refresh_character_data(self) -> None:
        """Update character data display"""
        try:
            # Update wealth info
            if self.game_instance:
                credits = getattr(self.game_instance, 'credits', 0)
                ships = len(getattr(self.game_instance, 'owned_ships', []))
                stations = len(getattr(self.game_instance, 'owned_stations', []))
                platforms = len(getattr(self.game_instance, 'owned_platforms', []))
                
                wealth_info = f"""[green]Credits:[/green] [bold]{credits:,}[/bold] ¤
                        
[blue]Fleet:[/blue] {ships} ship{'s' if ships != 1 else ''}
[purple]Stations:[/purple] {stations} station{'s' if stations != 1 else ''}
[orange3]Platforms:[/orange3] {platforms} platform{'s' if platforms != 1 else ''}"""
                
                try:
                    wealth_widget = self.query_one("#wealth_info")
                    wealth_widget.update(wealth_info)
                except:
                    pass
        except Exception as e:
            pass
    
    def compose(self) -> ComposeResult:
        yield Static("👤 CHARACTER PROFILE", classes="screen_title")
        
        with Horizontal():
            # Left column - Character Info
            with Vertical(id="char_info_column"):
                # Character Portrait & Basic Info
                with Container(id="character_portrait", classes="profile_section"):
                    yield Static("🧑‍� COMMANDER PROFILE ", classes="section_header")
                    
                    if self.game_instance and self.game_instance.player_name:
                        commander_name = self.game_instance.player_name
                        char_class = self.game_instance.character_class or "Unassigned"
                        char_background = self.game_instance.character_background or "Unknown"
                        
                        # Get class and background descriptions
                        class_desc = ""
                        bg_desc = ""
                        if GAME_AVAILABLE:
                            try:
                                from characters import character_classes, character_backgrounds
                                if char_class in character_classes:
                                    class_desc = character_classes[char_class].get('description', '')
                                if char_background in character_backgrounds:
                                    bg_desc = character_backgrounds[char_background].get('description', '')
                            except:
                                pass
                        
                        profile_info = f"""[bold cyan]═══ {commander_name} ═══[/bold cyan]
                        
[yellow]Class:[/yellow] [bold]{char_class}[/bold]
{class_desc}

[yellow]Background:[/yellow] [bold]{char_background}[/bold] 
{bg_desc}"""
                        
                        yield Static(profile_info, id="profile_info")
                    else:
                        yield Static("[red]No character data available[/red]\n[dim]Create a character first[/dim]", id="profile_info")
                
                # Wealth & Assets
                with Container(id="wealth_section", classes="profile_section"):
                    yield Static("💰 WEALTH & ASSETS", classes="section_header")
                    
                    if self.game_instance:
                        credits = self.game_instance.credits or 0
                        ships = len(self.game_instance.owned_ships)
                        stations = len(self.game_instance.owned_stations)
                        platforms = len(self.game_instance.owned_platforms)
                        
                        wealth_info = f"""[green]Credits:[/green] [bold]{credits:,}[/bold] ¤
                        
[blue]Fleet:[/blue] {ships} ship{'s' if ships != 1 else ''}
[purple]Stations:[/purple] {stations} station{'s' if stations != 1 else ''}
[orange3]Platforms:[/orange3] {platforms} platform{'s' if platforms != 1 else ''}"""
                        
                        yield Static(wealth_info, id="wealth_info")
                    else:
                        yield Static("[red]Financial data unavailable[/red]", id="wealth_info")
            
            # Right column - Stats & Skills
            with Vertical(id="stats_column"):
                # Character Stats
                with Container(id="stats_section", classes="profile_section"):
                    yield Static("⚡ CHARACTER ATTRIBUTES", classes="section_header")
                    
                    if self.game_instance and self.game_instance.character_stats:
                        stats_display = ""
                        
                        # Organize stats into categories
                        stat_categories = {
                            "🎖️ Command": ['leadership', 'charisma', 'strategy'],
                            "⚔️ Military": ['combat', 'tactics', 'piloting'],
                            "🔧 Technical": ['engineering', 'research', 'hacking'],
                            "🤝 Social": ['diplomacy', 'trading', 'espionage'],
                            "🗺️ Frontier": ['navigation', 'survival', 'archaeology']
                        }
                        
                        for category, stat_names in stat_categories.items():
                            stats_display += f"[bold cyan]{category}[/bold cyan]\n"
                            
                            for stat_name in stat_names:
                                if stat_name in self.game_instance.character_stats:
                                    value = self.game_instance.character_stats[stat_name]
                                    # Create visual bar with colors based on value
                                    filled = "█" * value
                                    empty = "░" * (10 - value)
                                    
                                    # Color coding for stats
                                    if value >= 8:
                                        color = "bright_green"
                                    elif value >= 6:
                                        color = "green"  
                                    elif value >= 4:
                                        color = "yellow"
                                    else:
                                        color = "red"
                                    
                                    # Pad stat name to 12 characters for alignment
                                    padded_name = f"{stat_name.title()}:".ljust(12)
                                    stats_display += f"  [white]{padded_name}[/white] [{color}]{filled}[/{color}][dim]{empty}[/dim] [{color}]{value}[/{color}]/10\n"
                            
                            stats_display += "\n"
                        
                        # Add any remaining stats not in categories
                        all_categorized_stats = []
                        for stat_list in stat_categories.values():
                            all_categorized_stats.extend(stat_list)
                        
                        uncategorized_stats = []
                        for stat_name, value in self.game_instance.character_stats.items():
                            if stat_name not in all_categorized_stats:
                                uncategorized_stats.append((stat_name, value))
                        
                        if uncategorized_stats:
                            stats_display += "[bold cyan]📊 Other[/bold cyan]\n"
                            for stat_name, value in uncategorized_stats:
                                filled = "█" * value
                                empty = "░" * (10 - value)
                                if value >= 6:
                                    color = "green"
                                elif value >= 4:
                                    color = "yellow"
                                else:
                                    color = "red"
                                
                                # Pad stat name to 12 characters for alignment
                                padded_name = f"{stat_name.title()}:".ljust(12)
                                stats_display += f"  [white]{padded_name}[/white] [{color}]{filled}[/{color}][dim]{empty}[/dim] [{color}]{value}[/{color}]/10\n"
                        
                        yield Static(stats_display.rstrip(), id="stats_display")
                    else:
                        yield Static("[red]Character stats not available[/red]\n[dim]Generate stats in character creation[/dim]", id="stats_display")
                
                # Profession & Progress
                with Container(id="profession_section", classes="profile_section"):
                    yield Static("🎓 PROFESSION & PROGRESSION", classes="section_header")
                    
                    if self.game_instance and hasattr(self.game_instance, 'profession_system'):
                        prof_system = self.game_instance.profession_system
                        
                        if hasattr(prof_system, 'character_profession') and prof_system.character_profession:
                            profession = prof_system.character_profession
                            level = prof_system.profession_levels.get(profession, 1)
                            xp = prof_system.profession_experience.get(profession, 0)
                            
                            # Calculate XP to next level (simplified)
                            next_level_xp = level * 100
                            xp_progress = min(xp / next_level_xp, 1.0) if next_level_xp > 0 else 0
                            progress_bar_length = 20
                            filled_bars = int(xp_progress * progress_bar_length)
                            
                            progress_bar = "█" * filled_bars + "░" * (progress_bar_length - filled_bars)
                            
                            prof_info = f"""[bold cyan]Current Profession:[/bold cyan]
[green]{profession}[/green] - Level [yellow]{level}[/yellow]

[cyan]Experience:[/cyan] [green]{progress_bar}[/green] 
{xp}/{next_level_xp} XP"""
                            
                            yield Static(prof_info, id="profession_info")
                        else:
                            yield Static("[yellow]No active profession[/yellow]\n[dim]Visit the profession system to choose[/dim]", id="profession_info")
                    else:
                        yield Static("[red]Profession system unavailable[/red]", id="profession_info")

class ShipManagerScreen(Static):
    """Comprehensive ship management interface"""
    
    def __init__(self, game_instance=None, **kwargs):
        super().__init__(**kwargs)
        self.game_instance = game_instance
        self.selected_ship = None
        
    def compose(self) -> ComposeResult:
        yield Static("🛸 SHIP MANAGEMENT CENTER", classes="screen_title")
        
        with Horizontal():
            # Left panel - Ship list and actions
            with Vertical(id="ship_list_panel"):
                yield Static("🚀 FLEET OVERVIEW", classes="section_header")
                
                # Ship list
                with Container(id="ship_list_container"):
                    ship_items = []
                    
                    if self.game_instance:
                        # Add owned ships (predefined ships)
                        for ship_name in getattr(self.game_instance, 'owned_ships', []):
                            ship_items.append(ListItem(Label(f"🚢 {ship_name}")))
                        
                        # Add custom ships (player-built)
                        for ship in getattr(self.game_instance, 'custom_ships', []):
                            ship_name = ship.get('name', 'Unnamed Ship')
                            ship_items.append(ListItem(Label(f"🛠️ {ship_name}")))
                    
                    if not ship_items:
                        ship_items.append(ListItem(Label("📭 No ships available")))
                    
                    yield ListView(*ship_items, id="ship_list")
                
                # Ship action buttons
                yield Static("⚙️ SHIP ACTIONS", classes="section_header")
                with Vertical(id="ship_actions"):
                    yield Button("🔧 Create New Ship", id="btn_create_ship", variant="success")
                    yield Button("✏️ Edit Selected Ship", id="btn_edit_ship", variant="primary")
                    yield Button("🗑️ Delete Selected Ship", id="btn_delete_ship", variant="error")
                    yield Button("⭐ Set as Active Ship", id="btn_set_active", variant="warning")
                    yield Button("🔄 Refresh Fleet", id="btn_refresh_fleet", variant="default")
            
            # Right panel - Ship details
            with Vertical(id="ship_details_panel"):
                yield Static("📋 SHIP DETAILS", classes="section_header")
                
                with Container(id="ship_info_display"):
                    if self.game_instance and hasattr(self.game_instance.navigation, 'current_ship') and self.game_instance.navigation.current_ship:
                        current_ship = self.game_instance.navigation.current_ship
                        ship_info = f"""[bold cyan]═══ ACTIVE SHIP ═══[/bold cyan]
                        
[yellow]Name:[/yellow] [bold]{current_ship.name}[/bold]
[yellow]Class:[/yellow] {getattr(current_ship, 'ship_class', 'Unknown')}
[yellow]Location:[/yellow] ({current_ship.coordinates[0]}, {current_ship.coordinates[1]}, {current_ship.coordinates[2]})

[green]Status:[/green] [bold]Active[/bold]"""
                    else:
                        ship_info = """[red]No active ship selected[/red]
                        
[dim]Select a ship from the fleet list to view details[/dim]"""
                    
                    yield Static(ship_info, id="active_ship_info")
                
                # Ship creation form (hidden by default)
                with Container(id="ship_creation_form", classes="hidden"):
                    yield Static("🔧 CREATE NEW SHIP", classes="section_header")
                    yield Input(placeholder="Enter ship name...", id="new_ship_name")
                    with Horizontal():
                        yield Button("✅ Create", id="btn_confirm_create", variant="success")
                        yield Button("❌ Cancel", id="btn_cancel_create", variant="error")

    def on_mount(self) -> None:
        """Bind events and ensure UI reflects current game state"""
        # Ensure list and active ship display are up-to-date
        self.refresh_ship_list()
        self.refresh_active_ship_display()

    def refresh_ship_list(self) -> None:
        """Rebuild the ship list from game instance"""
        try:
            list_view = self.query_one("#ship_list", ListView)
        except Exception:
            return

        list_view.clear()
        items = []
        
        if self.game_instance:
            ships = self.game_instance.get_all_ships()
            for ship in ships:
                items.append(ListItem(Label(ship['display'])))

        if not items:
            items = [ListItem(Label("📭 No ships available"))]

        for it in items:
            list_view.append(it)

    def refresh_active_ship_display(self) -> None:
        """Update the active ship details panel"""
        try:
            widget = self.query_one("#active_ship_info", Static)
        except Exception:
            return

        if self.game_instance:
            ship_info = self.game_instance.get_active_ship_info()
            if ship_info:
                info = f"""[bold cyan]═══ ACTIVE SHIP ═══[/bold cyan]

[yellow]Name:[/yellow] [bold]{ship_info['name']}[/bold]
[yellow]Class:[/yellow] {ship_info['class']}
[yellow]Location:[/yellow] ({ship_info['coordinates'][0]}, {ship_info['coordinates'][1]}, {ship_info['coordinates'][2]})
[yellow]Fuel:[/yellow] {ship_info['fuel']}/{ship_info['max_fuel']}
[yellow]Cargo:[/yellow] {ship_info['cargo_used']}/{ship_info['cargo_max']}

[green]Status:[/green] [bold]Active[/bold]"""
            else:
                info = """[red]No active ship selected[/red]

[dim]Select a ship from the fleet list to view details[/dim]"""
        else:
            info = """[red]Game not available[/red]"""

        try:
            widget.update(info)
        except Exception:
            pass

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Store the name of the selected ship"""
        try:
            lv = event.list_view
            idx = lv.index
            
            if self.game_instance and idx is not None:
                ships = self.game_instance.get_all_ships()
                if 0 <= idx < len(ships):
                    self.selected_ship = ships[idx]['name']
                else:
                    self.selected_ship = None
            else:
                self.selected_ship = None
        except Exception:
            self.selected_ship = None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle ship manager button presses"""
        btn_id = event.button.id

        if btn_id == "btn_refresh_fleet":
            self.refresh_ship_list()
            self.refresh_active_ship_display()
            return

        if btn_id == "btn_create_ship":
            # Show creation form
            try:
                form = self.query_one("#ship_creation_form")
                form.remove_class("hidden")
            except Exception:
                pass
            return

        if btn_id == "btn_cancel_create":
            try:
                form = self.query_one("#ship_creation_form")
                form.add_class("hidden")
            except Exception:
                pass
            return

        if btn_id == "btn_confirm_create":
            try:
                name_input = self.query_one("#new_ship_name", Input)
                ship_name = name_input.value.strip()
                
                if self.game_instance:
                    success, message = self.game_instance.create_custom_ship(ship_name, "Custom")
                    if success:
                        self.app.show_notification(f"✅ {message}")
                        # Hide form and refresh
                        form = self.query_one("#ship_creation_form")
                        form.add_class("hidden")
                        name_input.value = ""
                        self.refresh_ship_list()
                    else:
                        self.app.show_notification(f"❌ {message}")
                else:
                    self.app.show_notification("❌ Game not available")
            except Exception as e:
                self.app.show_notification(f"❌ Error: {str(e)[:30]}...")
            return

        if btn_id == "btn_set_active":
            if not self.selected_ship:
                self.app.show_notification("❌ No ship selected to activate")
                return

            if self.game_instance:
                success, message = self.game_instance.set_active_ship(self.selected_ship)
                if success:
                    self.app.show_notification(f"⭐ {message}")
                    self.refresh_active_ship_display()
                else:
                    self.app.show_notification(f"❌ {message}")
            else:
                self.app.show_notification("❌ Game not available")
            return

        if btn_id == "btn_delete_ship":
            if not self.selected_ship:
                self.app.show_notification("❌ No ship selected to delete")
                return

            if self.game_instance:
                success, message = self.game_instance.delete_ship(self.selected_ship)
                if success:
                    self.app.show_notification(f"🗑️ {message}")
                    self.selected_ship = None
                    self.refresh_ship_list()
                    self.refresh_active_ship_display()
                else:
                    self.app.show_notification(f"❌ {message}")
            else:
                self.app.show_notification("❌ Game not available")
            return

        if btn_id == "btn_edit_ship":
            if not self.selected_ship:
                self.app.show_notification("❌ No ship selected to edit")
                return

            if self.game_instance:
                # Simple demo rename - add " Mk2" suffix
                new_name = self.selected_ship + " Mk2"
                success, message = self.game_instance.rename_ship(self.selected_ship, new_name)
                if success:
                    self.app.show_notification(f"✏️ {message}")
                    self.selected_ship = new_name  # Update selected ship name
                    self.refresh_ship_list()
                else:
                    self.app.show_notification(f"❌ {message}")
            else:
                self.app.show_notification("❌ Game not available")
            return

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

class PlayerLogScreen(Static):
    """Player log and activity history"""
    
    def __init__(self, game_instance=None, **kwargs):
        super().__init__(**kwargs)
        self.game_instance = game_instance
    
    def compose(self) -> ComposeResult:
        """Create child widgets"""
        yield Static("📜 PLAYER ACTIVITY LOG", classes="screen_title")
        yield Static("─" * 80, classes="rule")
        
        if not self.game_instance:
            yield Static("[red]No game instance available[/red]", id="log_content")
            return
            
        # Log controls
        with Container(id="log_controls"):
            yield Static("Filter by:", classes="section_header")
            with Grid(id="filter_grid"):
                yield Button("All Entries", id="filter_all", variant="primary")
                yield Button("Actions", id="filter_actions", variant="primary") 
                yield Button("System", id="filter_system", variant="primary")
                yield Button("Events", id="filter_events", variant="primary")
                yield Button("Current Turn", id="filter_current", variant="success")
                yield Button("Clear Log", id="clear_log", variant="warning")
        
        yield Static("─" * 80, classes="rule")
        
        # Log content
        with Container(id="log_container"):
            yield Static("Loading log...", id="log_content")
    
    def on_mount(self) -> None:
        """Called when the screen is mounted"""
        self.refresh_log()
    
    def refresh_log(self, entry_type=None):
        """Update log display"""
        try:
            if not self.game_instance:
                return
                
            # Get log entries
            if entry_type == "current":
                entries = self.game_instance.get_current_turn_log()
                header = f"Turn {self.game_instance.current_turn} Activity:"
            elif entry_type:
                entries = self.game_instance.get_log_entries(entry_type=entry_type, limit=50)
                header = f"{entry_type.title()} Log:"
            else:
                entries = self.game_instance.get_log_entries(limit=50)
                header = "Complete Activity Log:"
            
            if not entries:
                log_text = f"{header}\n\n[dim]No entries found[/dim]"
            else:
                log_lines = [header, ""]
                
                # Group entries by turn for better readability
                current_turn = None
                for entry in reversed(entries):  # Most recent first
                    if entry['turn'] != current_turn:
                        current_turn = entry['turn']
                        log_lines.append(f"[bold cyan]═══ Turn {current_turn} ═══[/bold cyan]")
                    
                    # Format entry based on type
                    time_str = entry['timestamp']
                    msg = entry['message']
                    entry_type_str = entry['type'].upper()
                    
                    # Color code by type
                    if entry['type'] == 'action':
                        color = "green"
                        icon = "▶"
                    elif entry['type'] == 'system':
                        color = "blue" 
                        icon = "ⓘ"
                    elif entry['type'] == 'event':
                        color = "yellow"
                        icon = "!"
                    elif entry['type'] == 'combat':
                        color = "red"
                        icon = "⚔"
                    elif entry['type'] == 'trade':
                        color = "cyan"
                        icon = "💰"
                    else:
                        color = "white"
                        icon = "•"
                    
                    log_lines.append(f"[{color}]{icon} [{time_str}] {msg}[/{color}]")
                
                log_text = "\n".join(log_lines)
            
            # Update display
            try:
                log_widget = self.query_one("#log_content")
                log_widget.update(log_text)
            except:
                pass
                
        except Exception as e:
            try:
                log_widget = self.query_one("#log_content")
                log_widget.update(f"[red]Error loading log: {str(e)}[/red]")
            except:
                pass

class Game7019App(App):
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
        height: 1;
        text-style: bold;
        color: yellow;
        background: blue 20%;
        content-align: center middle;
        margin: 0;
        padding: 0;
    }
    
    #core_grid {
        grid-size: 3 2;
        grid-gutter: 1 1;
        margin: 1 0;
        padding: 0 1;
        height: auto;
        width: 100%;
    }
    
    #management_grid {
        grid-size: 3 2;
        grid-gutter: 1 1;
        margin: 1 0;
        padding: 1;
        height: auto;
        width: 100%;
    }
    
    #control_grid {
        grid-size: 4 1;
        grid-gutter: 1 1;
        margin: 1 0;
        padding: 1;
        height: auto;
        width: 100%;
    }
    

    
    #filter_grid {
        grid-size: 3 2;
        grid-gutter: 1 1;
        margin: 1;
        padding: 1;
        height: auto;
        width: 100%;
    }
    
    #log_container {
        height: auto;
        max-height: 80%;
        overflow-y: auto;
        padding: 1;
        border: solid green;
    }
    
    #log_content {
        padding: 1;
        color: green;
        background: black;
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
        min-width: 15;
        width: 100%;
        margin: 0 1;
        padding: 0 1;
        content-align: center middle;
        text-style: none;
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
    
    /* Notification styling - make it more readable and closable */
    Notification {
        background: $primary;
        color: white;
        text-style: bold;
        border: thick white;
        padding: 1;
        margin: 0 1;
    }
    
    Notification:hover {
        background: $accent;
        border: thick $accent;
    }
    
    .notification {
        background: $primary;
        color: white;
        text-style: bold;
        border: solid white;
        padding: 1;
        margin: 0 1;
    }
    
    .notification:hover {
        background: $accent;
        border: solid $accent;
    }
    
    Toast {
        background: $primary;
        color: white;
        text-style: bold;
        border: solid white;
        padding: 1;
        margin: 0 1;
    }
    
    Toast:hover {
        background: $accent;
        border: solid $accent;
    }
    
    /* Additional notification system styling */
    #notifications {
        color: white;
        background: $primary;
    }
    
    .toast {
        color: white;
        background: $primary;
        text-style: bold;
        border: solid white;
        padding: 1;
        margin: 0 1;
    }
    
    .toast:hover {
        background: $accent;
        border: solid $accent;
    }
    
    /* Textual's notification widget styling */
    NotificationGroup {
        color: white;
        background: $primary;
    }
    
    NotificationGroup > Static {
        color: white;
        text-style: bold;
    }
    
    /* Custom notification close button styling */
    .notification-close {
        dock: right;
        width: 3;
        height: 1;
        content-align: center middle;
        background: red;
        color: white;
        text-style: bold;
    }
    
    .notification-close:hover {
        background: ansi_bright_red;
        text-style: bold;
    }
    
    /* Character Profile Styling */
    #char_info_column {
        width: 1fr;
        padding: 0 1 0 0;
        margin: 0;
    }
    
    #stats_column {
        width: 1fr;
        padding: 0 0 0 1;
        margin: 0;
    }
    
    .profile_section {
        background: $boost;
        border: thick $primary;
        padding: 1;
        margin: 1;
        min-height: 10;
        box-sizing: border-box;
    }
    
    #character_portrait {
        background: $panel;
        border: thick cyan;
        margin: 1 1 0 1;
    }
    
    #wealth_section {
        background: $panel;
        border: thick green;
        margin: 1;
    }
    
    #stats_section {
        background: $panel;
        border: thick yellow;
        margin: 1 1 0 1;
    }
    
    #profession_section {
        background: $panel;  
        border: thick purple;
        margin: 1;
    }
    
    #profile_info {
        text-align: center;
        padding: 0;
        margin: 0;
    }
    
    #wealth_info {
        text-align: left;
        padding: 0;
        margin: 0;
    }
    
    #stats_display {
        text-align: left;
        padding: 0;
        margin: 0;
    }
    
    #profession_info {
        text-align: left;
        padding: 0;
        margin: 0;
    }
    
    /* Ship Manager Styling */
    #ship_list_panel {
        width: 1fr;
        padding: 1;
    }
    
    #ship_details_panel {
        width: 2fr;
        padding: 1;
    }
    
    #ship_list_container {
        background: $panel;
        border: solid cyan;
        padding: 1;
        margin: 1 0;
        height: 15;
    }
    
    #ship_info_display {
        background: $panel;
        border: solid green;
        padding: 2;
        margin: 1 0;
        height: 15;
    }
    
    #ship_actions {
        margin: 1 0;
    }
    
    #ship_creation_form {
        background: $panel;
        border: solid yellow;
        padding: 2;
        margin: 1 0;
    }
    
    .hidden {
        display: none;
    }
    
    #active_ship_info {
        text-align: left;
        padding: 1;
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
        Binding("escape", "dismiss_notifications", "Dismiss Messages"),
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
            yield MainMenu(game_instance=self.game_instance, id="main_menu_initial")
        yield Footer()
        
    def on_mount(self) -> None:
        """App startup"""
        self.title = "7019 Management System"
        self.sub_title = "4X Space Strategy Game"
        self.update_status_bar()
        
    def on_click(self, event) -> None:
        """Handle click events, including notification dismissal"""
        try:
            # Check if the click was on a notification
            if hasattr(event, 'widget') and event.widget:
                widget = event.widget
                # Check for notification-related widgets
                if (hasattr(widget, 'classes') and 
                    ('notification' in str(widget.classes) or 
                     'toast' in str(widget.classes) or
                     widget.__class__.__name__ in ['Notification', 'Toast'])):
                    # Dismiss the notification
                    try:
                        widget.remove()
                    except:
                        pass
                    event.stop()
        except Exception:
            pass
        
    def initialize_game(self):
        """Initialize the game with default settings for interface mode"""
        if not self.game_instance:
            return
            
        # Set up basic game state for interface
        self.game_instance.player_name = "Commander"
        self.game_instance.character_class = "Explorer"
        self.game_instance.character_background = "Frontier Survivor"
        self.game_instance.credits = 15000
        
        # Initialize character stats with all new attributes
        self.game_instance.character_stats = {
            # Core Command Attributes
            "leadership": 7,
            "charisma": 6,
            "strategy": 8,
            
            # Combat & Military
            "combat": 6,
            "tactics": 7,
            "piloting": 8,
            
            # Technical & Science
            "engineering": 8,
            "research": 9,
            "hacking": 5,
            
            # Social & Economic
            "diplomacy": 7,
            "trading": 6,
            "espionage": 4,
            
            # Exploration & Survival
            "navigation": 9,
            "survival": 8,
            "archaeology": 7
        }
        
        # Initialize profession system if available
        if hasattr(self.game_instance, 'profession_system'):
            self.game_instance.profession_system.character_profession = "Galactic Historian"
        
        # Initialize default ships
        if not self.game_instance.owned_ships:
            self.game_instance.owned_ships = ["Basic Transport", "Aurora Ascendant"]
        
        # Set up default active ship in navigation system
        if hasattr(self.game_instance, 'navigation') and self.game_instance.navigation:
            from navigation import Ship
            if not self.game_instance.navigation.current_ship:
                # Create the default ship instance
                default_ship = Ship("Basic Transport", "Basic Transport")
                self.game_instance.navigation.current_ship = default_ship
                print(f"Initialized default ship: {default_ship.name}")
            
    def update_status_bar(self):
        """Update the status bar with current game state"""
        if self.game_instance:
            # Check if we have a real character (created through character creation)
            has_character = (
                self.game_instance.player_name and 
                self.game_instance.character_stats and
                getattr(self.game_instance, 'character_created', False)
            )
            
            # Check if we have an active ship
            has_ship = (
                hasattr(self.game_instance, 'navigation') and 
                self.game_instance.navigation and
                self.game_instance.navigation.current_ship
            )
            
            if not has_character and not has_ship:
                # No character or ship - show helpful message
                try:
                    status_bar = self.query_one(StatusBar)
                    status_bar.update_message("🎭 Create a character and board a ship to begin your galactic journey!")
                except:
                    pass
            elif not has_character:
                # Has ship but no character
                try:
                    status_bar = self.query_one(StatusBar)
                    status_bar.update_message("🎭 Create a character to begin commanding your fleet!")
                except:
                    pass
            elif not has_ship:
                # Has character but no ship
                credits = getattr(self.game_instance, 'credits', 0)
                turn_info = self.game_instance.get_turn_info()
                try:
                    status_bar = self.query_one(StatusBar)
                    status_parts = [
                        f"Turn: {turn_info['current_turn']}/{turn_info['max_turns']}",
                        f"Actions: {turn_info['actions_remaining']}/{turn_info['max_actions']}",
                        f"Credits: {credits:,}",
                        "🚀 Select or create a ship from Ship Manager!"
                    ]
                    status_bar.update_message(" | ".join(status_parts))
                except:
                    pass
            else:
                # Has both character and ship - show normal status
                credits = getattr(self.game_instance, 'credits', 0)
                ship_name = self.game_instance.navigation.current_ship.name
                coords = self.game_instance.navigation.current_ship.coordinates
                location = f"({coords[0]}, {coords[1]}, {coords[2]})"
                turn_info = self.game_instance.get_turn_info()
                
                try:
                    status_bar = self.query_one(StatusBar)
                    status_bar.update_status(credits=credits, location=location, ship=ship_name, turn_info=turn_info)
                except:
                    pass
            
            # Also try to update character screen if it's currently displayed
            if self.current_content == "character":
                try:
                    char_screen = self.query_one(CharacterScreen)
                    char_screen.refresh_character_data()
                except:
                    pass
        
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle list view selections"""
        list_id = event.list_view.id
        
        if list_id == "class_list" and GAME_AVAILABLE:
            try:
                # Get the index of the selected item
                selected_index = event.list_view.index
                if selected_index is not None and selected_index >= 0:
                    # Get class name from the list of classes
                    class_names = list(character_classes.keys())
                    if selected_index < len(class_names):
                        class_name = class_names[selected_index]
                        self.char_selected_class = class_name
                        self.update_character_preview_from_app()
                        self.show_notification(f"✅ Selected class: {class_name}")
                        print(f"DEBUG: Selected class: {class_name}")
                        print(f"DEBUG: App now has char_selected_class: {self.char_selected_class}")
            except Exception as e:
                print(f"Error getting class selection: {e}")
                self.show_notification(f"Error selecting class: {str(e)[:20]}...")
                    
        elif list_id == "background_list" and GAME_AVAILABLE:
            try:
                # Get the index of the selected item
                selected_index = event.list_view.index
                if selected_index is not None and selected_index >= 0:
                    # Get background name from the list of backgrounds
                    bg_names = list(character_backgrounds.keys())
                    if selected_index < len(bg_names):
                        bg_name = bg_names[selected_index]
                        self.char_selected_background = bg_name
                        self.update_character_preview_from_app()
                        self.show_notification(f"✅ Selected background: {bg_name}")
                        print(f"DEBUG: Selected background: {bg_name}")
                        print(f"DEBUG: App now has char_selected_background: {self.char_selected_background}")
            except Exception as e:
                print(f"Error getting background selection: {e}")
                self.show_notification(f"Error selecting background: {str(e)[:20]}...")
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input field changes"""
        if event.input.id == "char_name_input":
            self.char_character_name = event.value
            self.update_character_preview_from_app()

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
        elif button_id == "player_log":
            self.action_show_player_log()
        elif button_id == "new_character":
            self.action_show_character_creation()
        elif button_id == "generate_stats":
            self.handle_generate_stats()
        elif button_id == "reroll_stats":
            self.handle_reroll_stats()
        elif button_id == "exit":
            self.exit()
            
        # Character creation buttons
        elif button_id == "create_character":
            self.handle_create_character()
        elif button_id == "step_next":
            self.handle_step_next()
        elif button_id == "step_back":
            self.handle_step_back()
        elif button_id == "cancel_creation":
            self.action_show_main_menu()
        # Handle character creation coordinator buttons
        elif (button_id.startswith("select_") or button_id.startswith("toggle_") or 
              button_id == "generate_stats_step" or button_id == "reroll_stats_step"):
            # Let the coordinator handle these
            try:
                coordinator = self.query_one(CharacterCreationCoordinator)
                # The coordinator's on_button_pressed will handle this
                coordinator.on_button_pressed(event)
            except:
                pass
        elif button_id == "back_to_menu":
            self.action_show_main_menu()
        
        # Turn management buttons
        elif button_id == "end_turn":
            self.handle_end_turn()
        elif button_id == "game_settings":
            self.handle_game_settings()
            
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
            
        # Ship management buttons
        elif button_id == "ship_manager":
            self.action_show_ship_manager()
        elif button_id == "create_ship":
            self.action_show_ship_manager()  # Will open to creation mode
        elif button_id == "list_ships":
            self.action_show_ship_manager()  # Will show ship list
        elif button_id == "edit_ship":
            self.show_notification("✏️ Edit ship functionality coming soon!")
        elif button_id == "delete_ship":
            self.show_notification("🗑️ Delete ship functionality coming soon!")
        elif button_id == "set_active_ship":
            self.show_notification("⭐ Set active ship functionality coming soon!")
            
        # Ship manager screen buttons
        elif button_id == "btn_create_ship":
            self.handle_show_ship_creation()
        elif button_id == "btn_edit_ship":
            self.handle_edit_selected_ship()
        elif button_id == "btn_delete_ship":
            self.handle_delete_selected_ship()
        elif button_id == "btn_set_active":
            self.handle_set_active_ship()
        elif button_id == "btn_refresh_fleet":
            self.handle_refresh_fleet()
        elif button_id == "btn_confirm_create":
            self.handle_confirm_ship_creation()
        elif button_id == "btn_cancel_create":
            self.handle_cancel_ship_creation()
            
        # Player log filter buttons
        elif button_id == "filter_all":
            self.handle_log_filter(None)
        elif button_id == "filter_actions":
            self.handle_log_filter("action")
        elif button_id == "filter_system":
            self.handle_log_filter("system")
        elif button_id == "filter_events":
            self.handle_log_filter("event")
        elif button_id == "filter_current":
            self.handle_log_filter("current")
        elif button_id == "clear_log":
            self.handle_clear_log()
    
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
                fallback = MainMenu(game_instance=self.game_instance, id=unique_fallback_id)
                container.mount(fallback)
                self.current_content = "main_menu"
            except Exception:
                pass
        
    def action_show_main_menu(self) -> None:
        """Show main menu"""
        self._switch_to_screen(MainMenu(game_instance=self.game_instance), "main_menu")
        # Update status bar when returning to main menu
        self.update_status_bar()
        
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
        
    def action_show_character_creation(self) -> None:
        """Show character creation screen"""
        # Check if a character has already been created
        if self.game_instance and getattr(self.game_instance, 'character_created', False):
            self.show_notification("❌ A character has already been created! Use Character Profile to view details.")
            return
        
        # Reset character creation variables for a fresh start
        if hasattr(self, 'char_selected_class'):
            delattr(self, 'char_selected_class')
        if hasattr(self, 'char_selected_background'):
            delattr(self, 'char_selected_background')
        if hasattr(self, 'char_generated_stats'):
            delattr(self, 'char_generated_stats')
        if hasattr(self, 'char_character_name'):
            delattr(self, 'char_character_name')
        
        self._switch_to_screen(CharacterCreationScreen(game_instance=self.game_instance), "character_creation")
    
    def action_show_player_log(self) -> None:
        """Show player log screen"""
        self._switch_to_screen(PlayerLogScreen(game_instance=self.game_instance), "player_log")
    
    def action_show_ship_manager(self) -> None:
        """Show ship manager screen"""
        self._switch_to_screen(ShipManagerScreen(game_instance=self.game_instance), "ship_manager")
        
    def action_show_help(self) -> None:
        """Show help information"""
        help_text = """
# 7019 Management System - Help

## Mouse Controls
- Click buttons to navigate
- Drag to scroll content
- Right-click for context menus
- Click notifications to dismiss them

## Keyboard Shortcuts  
- **Q**: Quit application
- **M**: Main Menu
- **N**: Navigation
- **T**: Trading
- **A**: Archaeology
- **C**: Character Profile
- **ESC**: Dismiss all notifications
- **F1**: This help screen

## Game Features
- Build and manage your interstellar corporation
- Explore 30+ star systems
- Trade exotic commodities
- Discover ancient civilizations
- Interact with AI bots and factions
        """
        self.push_screen(HelpModal(help_text))
        
    def action_dismiss_notifications(self) -> None:
        """Dismiss all notifications"""
        try:
            # Clear all existing notifications
            self.clear_notifications()
            self.show_notification("✅ All messages dismissed", timeout=2.0)
        except Exception as e:
            pass
        
    def show_notification(self, message: str, timeout: float = 5.0) -> None:
        """Show a dismissable notification with close hint"""
        # Add close instructions and visual styling
        enhanced_message = f"[bold]{message}[/bold]\n[dim italic]💡 Click to dismiss • ESC to clear all[/dim italic]"
        self.notify(enhanced_message, title="📢 System Message", timeout=timeout)
        
    def show_persistent_notification(self, message: str) -> None:
        """Show a notification that doesn't auto-dismiss"""
        enhanced_message = f"[bold]{message}[/bold]\n[dim italic]💡 Click to dismiss • ESC to clear all[/dim italic]"
        self.notify(enhanced_message, title="📢 System Message", timeout=0)
        
    def show_error_notification(self, message: str) -> None:
        """Show an error notification"""
        enhanced_message = f"[red bold]{message}[/red bold]\n[dim italic]💡 Click to dismiss • ESC to clear all[/dim italic]"
        self.notify(enhanced_message, title="⚠️ Error", timeout=8.0)
        
    def show_success_notification(self, message: str) -> None:
        """Show a success notification"""
        enhanced_message = f"[green bold]{message}[/green bold]\n[dim italic]💡 Click to dismiss • ESC to clear all[/dim italic]"
        self.notify(enhanced_message, title="✅ Success", timeout=4.0)
        
    # Character creation handlers - store state in app
    def handle_generate_stats(self):
        """Generate random character stats"""
        if GAME_AVAILABLE:
            # Store stats on the app instance for now
            self.char_generated_stats = create_character_stats()
            self.update_character_preview_from_app()
            self.show_notification("📊 Character stats generated!")
        else:
            self.show_notification("⚠️ Stats generation unavailable in demo mode")
    
    def handle_reroll_stats(self):
        """Reroll character stats"""
        if GAME_AVAILABLE and hasattr(self, 'char_generated_stats') and self.char_generated_stats:
            self.char_generated_stats = create_character_stats()
            self.update_character_preview_from_app()
            self.show_notification("🎲 Stats rerolled!")
        else:
            self.show_notification("⚠️ Generate stats first")
    
    def handle_step_next(self):
        """Handle next step in character creation"""
        try:
            coordinator = self.query_one(CharacterCreationCoordinator)
            
            # Validate current step before proceeding
            step_id, step_name = coordinator.steps[coordinator.current_step]
            
            if step_id == 'species' and not coordinator.character_data['species']:
                self.show_notification("❌ Please select a species")
                return
            elif step_id == 'background' and not coordinator.character_data['background']:
                self.show_notification("❌ Please select a background")
                return
            elif step_id == 'faction' and not coordinator.character_data['faction']:
                self.show_notification("❌ Please select a faction")
                return
            elif step_id == 'class' and not coordinator.character_data['character_class']:
                self.show_notification("❌ Please select a character class")
                return
            elif step_id == 'research' and len(coordinator.character_data['research_paths']) == 0:
                self.show_notification("❌ Please select at least one research path")
                return
            elif step_id == 'stats' and not coordinator.character_data['stats']:
                self.show_notification("❌ Please generate character stats")
                return
            elif step_id == 'name' and not coordinator.character_data['name']:
                self.show_notification("❌ Please enter a character name")
                return
            elif step_id == 'confirm':
                self.handle_create_character_from_coordinator(coordinator)
                return
            
            # Move to next step
            coordinator.current_step += 1
            coordinator.update_step_display()
            
            # Update button states
            self.update_navigation_buttons(coordinator)
            
        except Exception as e:
            self.show_notification(f"Error: {str(e)}")
    
    def handle_step_back(self):
        """Handle previous step in character creation"""
        try:
            coordinator = self.query_one(CharacterCreationCoordinator)
            
            if coordinator.current_step > 0:
                coordinator.current_step -= 1
                coordinator.update_step_display()
                self.update_navigation_buttons(coordinator)
            else:
                self.action_show_main_menu()
                
        except Exception as e:
            self.show_notification(f"Error: {str(e)}")
    
    def update_navigation_buttons(self, coordinator):
        """Update navigation button states"""
        try:
            back_btn = self.query_one("#step_back")
            next_btn = self.query_one("#step_next")
            
            # Update button text based on current step
            if coordinator.current_step == 0:
                back_btn.label = "🏠 Main Menu"
            else:
                back_btn.label = "⬅️ Back"
                
            if coordinator.current_step == len(coordinator.steps) - 1:
                next_btn.label = "🎉 Create!"
            else:
                next_btn.label = "➡️ Next"
                
        except Exception as e:
            pass
    
    def handle_create_character_from_coordinator(self, coordinator):
        """Create character from the coordinator's data"""
        if GAME_AVAILABLE and self.game_instance:
            try:
                # Apply character data to game
                char_data = coordinator.character_data
                self.game_instance.player_name = char_data['name']
                self.game_instance.character_species = char_data['species']
                self.game_instance.character_background = char_data['background']
                self.game_instance.character_class = char_data['character_class']
                self.game_instance.character_stats = char_data['stats']
                
                # Set starting faction reputation bonus
                if hasattr(self.game_instance, 'faction_system') and char_data['faction']:
                    self.game_instance.faction_system.modify_reputation(
                        char_data['faction'], 25, "Starting faction allegiance"
                    )
                
                # Mark character as created
                self.game_instance.character_created = True
                
                # Update status bar
                self.update_status_bar()
                
                self.show_notification(f"✅ Character '{char_data['name']}' created successfully!")
                self.set_timer(2.0, self.action_show_main_menu)
                
            except Exception as e:
                self.show_notification(f"❌ Error creating character: {str(e)[:50]}...")
        else:
            self.show_notification("✅ Character created (demo mode)")
            self.action_show_main_menu()
    
    def handle_create_character(self):
        """Legacy character creation handler - now handles coordinator workflow"""
        try:
            coordinator = self.query_one(CharacterCreationCoordinator)
            self.handle_create_character_from_coordinator(coordinator)
        except:
            # Fallback to old system if coordinator not found
            self.show_notification("❌ Character creation error - please try again")
            self.action_show_main_menu()
    
    def update_character_preview_from_app(self):
        """Update the character preview display from app-level variables"""
        try:
            preview_widget = self.query_one("#char_preview")
            
            # Check if any selections have been made
            has_class = hasattr(self, 'char_selected_class') and self.char_selected_class
            has_background = hasattr(self, 'char_selected_background') and self.char_selected_background
            has_stats = hasattr(self, 'char_generated_stats') and self.char_generated_stats
            
            # If no selections made, show placeholder message
            if not has_class and not has_background and not has_stats:
                placeholder_text = """[dim]👤 CHARACTER PREVIEW[/dim]

🎯 [yellow]Start making some choices![/yellow]

1️⃣ Select a character class
2️⃣ Choose a background
3️⃣ Generate your stats
4️⃣ Enter a name

Your character preview will appear here
as you make your selections."""
                
                preview_widget.update(placeholder_text)
                return
            
            # Calculate starting credits
            base_credits = 10000
            class_credits = 0
            bg_credits = 0
            class_data = {}  # Initialize class_data to prevent undefined reference
            
            if GAME_AVAILABLE and has_class:
                class_data = character_classes.get(self.char_selected_class, {})
                class_credits = class_data.get("starting_credits", 0)
                
            if GAME_AVAILABLE and has_background:
                bg_data = character_backgrounds.get(self.char_selected_background, {})
                bg_credits = bg_data.get("credit_bonus", 0) + bg_data.get("credit_penalty", 0)
            
            total_credits = base_credits + class_credits + bg_credits
            
            # Build stats text
            stats_text = ""
            
            if has_stats:
                stats_lines = []
                for stat, value in self.char_generated_stats.items():
                    stats_lines.append(f"{stat.title()}: {value}")
                stats_text = "\n".join(stats_lines)
            
            char_name = getattr(self, 'char_character_name', '[Not Set]')
            selected_class = getattr(self, 'char_selected_class', '[None Selected]')
            selected_bg = getattr(self, 'char_selected_background', '[None Selected]')
            
            preview_text = f"""Name: {char_name}
Class: {selected_class}
Background: {selected_bg}

📊 STATS:
{stats_text}

💰 STARTING RESOURCES:
Credits: {total_credits:,}
Ships: {class_data.get('starting_ships', ['TBD'])[0] if has_class and GAME_AVAILABLE else '[Based on class]'}

🎯 CLASS BONUSES:
{self.get_class_bonuses_text_from_app()}

🌟 BACKGROUND TRAITS:
{self.get_background_traits_text_from_app()}"""
            
            preview_widget.update(preview_text)
        except Exception as e:
            print(f"Error updating preview: {e}")
    
    def get_class_bonuses_text_from_app(self):
        """Get formatted class bonuses text from app variables"""
        if not GAME_AVAILABLE or not hasattr(self, 'char_selected_class') or not self.char_selected_class:
            return "Select a class to see bonuses"
            
        class_data = character_classes.get(self.char_selected_class, {})
        bonuses = class_data.get("bonuses", {})
        
        if not bonuses:
            return "No special bonuses"
            
        bonus_lines = []
        for bonus, value in bonuses.items():
            if isinstance(value, float):
                bonus_lines.append(f"• {bonus.replace('_', ' ').title()}: +{int(value*100)}%")
            else:
                bonus_lines.append(f"• {bonus.replace('_', ' ').title()}: {value}")
        
        return "\n".join(bonus_lines)
    
    def get_background_traits_text_from_app(self):
        """Get formatted background traits text from app variables"""
        if not GAME_AVAILABLE or not hasattr(self, 'char_selected_background') or not self.char_selected_background:
            return "Select a background to see traits"
            
        bg_data = character_backgrounds.get(self.char_selected_background, {})
        traits = bg_data.get("traits", [])
        
        if not traits:
            return "No special traits"
            
        return "\n".join([f"• {trait}" for trait in traits])
    
    def apply_character_to_game_direct(self):
        """Apply the created character directly from app variables to the game instance"""
        if not self.game_instance:
            return
            
        # Set basic character info
        self.game_instance.player_name = self.char_character_name
        self.game_instance.character_class = self.char_selected_class
        self.game_instance.character_background = self.char_selected_background
        self.game_instance.character_stats = self.char_generated_stats
        
        # Apply starting credits
        class_data = character_classes.get(self.char_selected_class, {})
        bg_data = character_backgrounds.get(self.char_selected_background, {})
        
        base_credits = 10000
        class_credits = class_data.get("starting_credits", 0)
        bg_credits = bg_data.get("credit_bonus", 0) + bg_data.get("credit_penalty", 0)
        
        self.game_instance.credits = base_credits + class_credits + bg_credits
        
        # Initialize profession system if available
        if hasattr(self.game_instance, 'profession_system'):
            self.game_instance.profession_system.character_profession = "Galactic " + self.char_selected_class
    
    def update_character_preview(self):
        """Update the character preview display"""
        try:
            preview_widget = self.query_one("#char_preview")
            
            # Calculate starting credits
            base_credits = 10000
            class_credits = 0
            bg_credits = 0
            
            if GAME_AVAILABLE and self.selected_class:
                class_data = character_classes.get(self.selected_class, {})
                class_credits = class_data.get("starting_credits", 0)
                
            if GAME_AVAILABLE and self.selected_background:
                bg_data = character_backgrounds.get(self.selected_background, {})
                bg_credits = bg_data.get("credit_bonus", 0) + bg_data.get("credit_penalty", 0)
            
            total_credits = base_credits + class_credits + bg_credits
            
            # Build preview text
            stats_text = "?\n".join(["Leadership: ?", "Technical: ?", "Combat: ?", 
                                   "Diplomacy: ?", "Exploration: ?", "Trade: ?"])
            
            if self.generated_stats:
                stats_lines = []
                for stat, value in self.generated_stats.items():
                    stats_lines.append(f"{stat.title()}: {value}")
                stats_text = "\n".join(stats_lines)
            
            preview_text = f"""Name: {self.character_name or '[Not Set]'}
Class: {self.selected_class or '[None Selected]'}
Background: {self.selected_background or '[None Selected]'}

📊 STATS:
{stats_text}

💰 STARTING RESOURCES:
Credits: {total_credits:,}
Ships: {class_data.get('starting_ships', ['TBD'])[0] if self.selected_class and GAME_AVAILABLE else '[Based on class]'}

🎯 CLASS BONUSES:
{self.get_class_bonuses_text()}

🌟 BACKGROUND TRAITS:
{self.get_background_traits_text()}"""
            
            preview_widget.update(preview_text)
        except Exception as e:
            print(f"Error updating preview: {e}")
    
    def get_class_bonuses_text(self):
        """Get formatted class bonuses text"""
        if not GAME_AVAILABLE or not self.selected_class:
            return "Select a class to see bonuses"
            
        class_data = character_classes.get(self.selected_class, {})
        bonuses = class_data.get("bonuses", {})
        
        if not bonuses:
            return "No special bonuses"
            
        bonus_lines = []
        for bonus, value in bonuses.items():
            if isinstance(value, float):
                bonus_lines.append(f"• {bonus.replace('_', ' ').title()}: +{int(value*100)}%")
            else:
                bonus_lines.append(f"• {bonus.replace('_', ' ').title()}: {value}")
        
        return "\n".join(bonus_lines)
    
    def get_background_traits_text(self):
        """Get formatted background traits text"""
        if not GAME_AVAILABLE or not self.selected_background:
            return "Select a background to see traits"
            
        bg_data = character_backgrounds.get(self.selected_background, {})
        traits = bg_data.get("traits", [])
        
        if not traits:
            return "No special traits"
            
        return "\n".join([f"• {trait}" for trait in traits])
    


    def handle_archaeological_scan(self):
        """Handle archaeological site scanning"""
        if not self.game_instance or not hasattr(self.game_instance, 'galactic_history'):
            self.show_notification("🔍 Archaeological scanner offline")
            return
        
        # Check if we can take an action
        if not self.game_instance.can_take_action():
            turn_info = self.game_instance.get_turn_info()
            self.show_notification(f"⏰ No actions remaining this turn ({turn_info['actions_remaining']}/{turn_info['actions_per_turn']})")
            return
            
        # Consume action point
        self.game_instance.consume_action("Archaeological Site Scanning")
        
        # Simulate scanning with real game data if available
        self.show_notification("🔍 Scanning... Found 3 potential archaeological sites nearby!")
        
        # Update status bar to show remaining actions
        self.update_status_bar()
        
    def handle_excavation(self):
        """Handle archaeological excavation"""
        if not self.game_instance:
            self.show_notification("⛏️ Excavation equipment not available")
            return
        
        # Check if we can take an action
        if not self.game_instance.can_take_action():
            turn_info = self.game_instance.get_turn_info()
            self.show_notification(f"⏰ No actions remaining this turn ({turn_info['actions_remaining']}/{turn_info['actions_per_turn']})")
            return
            
        # Consume action point
        self.game_instance.consume_action("Archaeological Excavation")
        
        # Simulate excavation
        import random
        success = random.choice([True, False])
        if success:
            artifacts = ["Ancient Crystal Matrix", "Temporal Resonator", "Quantum Data Core"]
            artifact = random.choice(artifacts)
            # Log the discovery as an event
            self.game_instance.add_log_entry('event', f"Discovered artifact: {artifact}", {'artifact': artifact})
            self.show_notification(f"⛏️ Excavation successful! Discovered: {artifact}")
        else:
            self.show_notification("⛏️ Excavation incomplete. Continue digging...")
            
        # Update status bar to show remaining actions
        self.update_status_bar()
            
    def handle_buy_platform(self):
        """Handle manufacturing platform purchase"""
        if not self.game_instance:
            self.show_notification("💳 Transaction system offline")
            return
        
        # Check if we can take an action
        if not self.game_instance.can_take_action():
            turn_info = self.game_instance.get_turn_info()
            self.show_notification(f"⏰ No actions remaining this turn ({turn_info['actions_remaining']}/{turn_info['actions_per_turn']})")
            return
            
        cost = 2500000
        if self.game_instance.credits >= cost:
            # Consume action point
            self.game_instance.consume_action("Manufacturing Platform Purchase")
            
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
        
        # Check if we can take an action
        if not self.game_instance.can_take_action():
            turn_info = self.game_instance.get_turn_info()
            self.show_notification(f"⏰ No actions remaining this turn ({turn_info['actions_remaining']}/{turn_info['actions_per_turn']})")
            return
            
        jump_systems = ["Proxima Alpha", "Centauri Beta", "Vega Prime", "Wolf 359"]
        import random
        destination = random.choice(jump_systems)
        
        # Consume action point
        self.game_instance.consume_action(f"Hyperspace Jump to {destination}")
        
        self.show_notification(f"🎯 Hyperspace jump initiated! Destination: {destination}")
        
        # Update location in status bar
        try:
            status_bar = self.query_one(StatusBar)
            status_bar.update_status(location=destination)
        except:
            pass
            
        # Update status bar to show remaining actions
        self.update_status_bar()
        
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
    
    # Ship Management Handlers
    def handle_show_ship_creation(self):
        """Show ship creation form"""
        try:
            creation_form = self.query_one("#ship_creation_form")
            creation_form.remove_class("hidden")
            self.show_notification("🔧 Enter ship name and click Create")
        except:
            self.show_notification("❌ Could not open ship creation form")
    
    def handle_cancel_ship_creation(self):
        """Cancel ship creation"""
        try:
            creation_form = self.query_one("#ship_creation_form")
            creation_form.add_class("hidden")
            name_input = self.query_one("#new_ship_name")
            name_input.value = ""
            self.show_notification("❌ Ship creation cancelled")
        except:
            pass
    
    def handle_confirm_ship_creation(self):
        """Create a new ship"""
        try:
            name_input = self.query_one("#new_ship_name")
            ship_name = name_input.value.strip()
            
            if not ship_name:
                self.show_notification("❌ Please enter a ship name")
                return
                
            if self.game_instance:
                # Create a new custom ship
                new_ship = {
                    'name': ship_name,
                    'type': 'Custom Ship',
                    'health': 100,
                    'fuel': 100,
                    'components': []
                }
                
                # Add to custom ships
                if not hasattr(self.game_instance, 'custom_ships'):
                    self.game_instance.custom_ships = []
                
                self.game_instance.custom_ships.append(new_ship)
                
                # Hide form and refresh display
                self.handle_cancel_ship_creation()
                self.handle_refresh_fleet()
                
                self.show_notification(f"✅ Ship '{ship_name}' created successfully!")
            else:
                self.show_notification("❌ Game instance not available")
                
        except Exception as e:
            self.show_notification(f"❌ Error creating ship: {str(e)[:30]}...")
    
    def handle_edit_selected_ship(self):
        """Edit the selected ship"""
        self.show_notification("✏️ Ship editing coming soon!")
    
    def handle_delete_selected_ship(self):
        """Delete the selected ship"""
        self.show_notification("🗑️ Ship deletion coming soon!")
    
    def handle_set_active_ship(self):
        """Set the selected ship as active"""
        self.show_notification("⭐ Set active ship coming soon!")
    
    def handle_refresh_fleet(self):
        """Refresh the fleet display"""
        try:
            # Get the ship list
            ship_list = self.query_one("#ship_list")
            ship_list.clear()
            
            if self.game_instance:
                # Add owned ships
                for ship_name in getattr(self.game_instance, 'owned_ships', []):
                    ship_list.append(ListItem(Label(f"🚢 {ship_name}")))
                
                # Add custom ships
                for ship in getattr(self.game_instance, 'custom_ships', []):
                    ship_name = ship.get('name', 'Unnamed Ship')
                    ship_list.append(ListItem(Label(f"🛠️ {ship_name}")))
            
            self.show_notification("🔄 Fleet list refreshed!")
            
        except Exception as e:
            self.show_notification(f"❌ Error refreshing fleet: {str(e)[:30]}...")
    
    def handle_end_turn(self):
        """End the current turn and advance to next turn"""
        if not GAME_AVAILABLE or not self.game_instance:
            self.show_notification("❌ Game not available")
            return
            
        try:
            # Check if we can end the turn
            turn_info = self.game_instance.get_turn_info()
            
            # End the turn in the game logic
            self.game_instance.end_turn()
            
            # Update the status bar to reflect the new turn
            self.update_status_bar()
            
            # Show notification about turn advancement
            new_turn_info = self.game_instance.get_turn_info()
            self.show_notification(f"⏰ Turn {new_turn_info['current_turn']} begins!")
            
        except Exception as e:
            self.show_notification(f"❌ Error ending turn: {str(e)[:30]}...")
    
    def handle_game_settings(self):
        """Show game settings dialog"""
        self.show_notification("⚙️ Game settings coming soon!")
    
    def handle_log_filter(self, entry_type):
        """Handle log filtering"""
        try:
            # Find the current screen
            current_screen = self.query_one("#main_container").children[0]
            if isinstance(current_screen, PlayerLogScreen):
                current_screen.refresh_log(entry_type)
                
                # Show notification about filter
                if entry_type:
                    if entry_type == "current":
                        self.show_notification(f"📜 Showing current turn activity")
                    else:
                        self.show_notification(f"📜 Filtering by: {entry_type}")
                else:
                    self.show_notification("📜 Showing all log entries")
        except Exception as e:
            self.show_notification(f"❌ Error filtering log: {str(e)[:30]}...")
    
    def handle_clear_log(self):
        """Handle clearing the log"""
        if not GAME_AVAILABLE or not self.game_instance:
            self.show_notification("❌ Game not available")
            return
            
        try:
            self.game_instance.clear_log()
            self.show_notification("🗑️ Player log cleared")
            
            # Refresh the log display if we're on the log screen
            try:
                current_screen = self.query_one("#main_container").children[0]
                if isinstance(current_screen, PlayerLogScreen):
                    current_screen.refresh_log()
            except:
                pass
        except Exception as e:
            self.show_notification(f"❌ Error clearing log: {str(e)[:30]}...")

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
    app = Game7019App()
    app.run()