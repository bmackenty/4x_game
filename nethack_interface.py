#!/usr/bin/env python3
"""
NetHack-Style Interface for 4X Game
Pure keyboard control, ASCII-based UI inspired by NetHack/Roguelikes
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Label
from textual.binding import Binding
from textual.screen import Screen
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
import random

# Import game modules
try:
    from game import Game
    from characters import character_classes, character_backgrounds, create_character_stats
    from species import species_database, get_playable_species
    from factions import factions
    from research import research_categories
    GAME_AVAILABLE = True
except ImportError:
    GAME_AVAILABLE = False
    character_classes = {}
    character_backgrounds = {}
    species_database = {}
    factions = {}
    research_categories = {}


class MessageLog(Static):
    """Bottom message log like NetHack's message area"""
    
    def __init__(self):
        super().__init__()
        self.messages = []
        self.max_messages = 3
        
    def add_message(self, msg: str):
        """Add a message to the log"""
        self.messages.append(msg)
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
        self.update_display()
    
    def update_display(self):
        """Update the message display"""
        content = "\n".join(self.messages[-self.max_messages:])
        self.update(content if content else " ")


class CharacterCreationScreen(Screen):
    """NetHack-style character creation - single screen with keyboard selection"""
    
    BINDINGS = [
        Binding("ctrl+c", "app.quit", "Quit", show=False),
        Binding("enter", "confirm", "Confirm", show=True),
    ]
    
    def __init__(self):
        super().__init__()
        self.stage = "species"  # species -> background -> faction -> class -> stats -> name
        self.character_data = {
            'species': None,
            'background': None,
            'faction': None,
            'class': None,
            'stats': None,
            'name': "",
        }
        
        # Selection lists
        self.species_list = list(get_playable_species().keys()) if GAME_AVAILABLE else ["Terran"]
        self.background_list = list(character_backgrounds.keys()) if GAME_AVAILABLE else ["Merchant"]
        self.faction_list = list(factions.keys())[:12] if GAME_AVAILABLE else ["Independent"]
        self.class_list = list(character_classes.keys()) if GAME_AVAILABLE else ["Explorer"]
        
        # Current selection index
        self.current_index = 0
        
    def compose(self) -> ComposeResult:
        """Compose the character creation screen"""
        yield Static(id="main_display")
        yield MessageLog()
        
    def on_mount(self):
        """Initialize the screen"""
        self.update_display()
        self.query_one(MessageLog).add_message("Welcome to the character creator!")
        self.query_one(MessageLog).add_message(f"Select your {self.stage}. Use j/k or arrows, Enter to confirm")
        
    def update_display(self):
        """Update the main display based on current stage"""
        lines = []
        lines.append("═" * 80)
        lines.append("CHARACTER CREATION".center(80))
        lines.append("═" * 80)
        lines.append("")
        
        # Show current selections
        lines.append(f"Species:    {self.character_data['species'] or '???'}")
        lines.append(f"Background: {self.character_data['background'] or '???'}")
        lines.append(f"Faction:    {self.character_data['faction'] or '???'}")
        lines.append(f"Class:      {self.character_data['class'] or '???'}")
        lines.append(f"Name:       {self.character_data['name'] or '???'}")
        lines.append("")
        lines.append("─" * 80)
        lines.append("")
        
        # Show current selection list
        if self.stage == "species":
            lines.append("SELECT YOUR SPECIES:")
            lines.append("")
            for i, species in enumerate(self.species_list):
                cursor = ">" if i == self.current_index else " "
                lines.append(f"  {cursor} {chr(97 + i)}) {species}")
                if GAME_AVAILABLE and species in species_database:
                    desc = species_database[species].get('description', '')[:60]
                    lines.append(f"      {desc}...")
                    
        elif self.stage == "background":
            lines.append("SELECT YOUR BACKGROUND:")
            lines.append("")
            for i, bg in enumerate(self.background_list):
                cursor = ">" if i == self.current_index else " "
                lines.append(f"  {cursor} {chr(97 + i)}) {bg}")
                if GAME_AVAILABLE and bg in character_backgrounds:
                    desc = character_backgrounds[bg].get('description', '')[:60]
                    lines.append(f"      {desc}...")
                    
        elif self.stage == "faction":
            lines.append("SELECT YOUR FACTION:")
            lines.append("")
            for i, faction in enumerate(self.faction_list):
                cursor = ">" if i == self.current_index else " "
                lines.append(f"  {cursor} {chr(97 + i)}) {faction}")
                if GAME_AVAILABLE and faction in factions:
                    desc = factions[faction].get('description', '')[:60]
                    lines.append(f"      {desc}...")
                    
        elif self.stage == "class":
            lines.append("SELECT YOUR CLASS:")
            lines.append("")
            for i, cls in enumerate(self.class_list):
                cursor = ">" if i == self.current_index else " "
                lines.append(f"  {cursor} {chr(97 + i)}) {cls}")
                if GAME_AVAILABLE and cls in character_classes:
                    desc = character_classes[cls].get('description', '')[:60]
                    lines.append(f"      {desc}...")
                    
        elif self.stage == "stats":
            lines.append("YOUR CHARACTER STATS:")
            lines.append("")
            if self.character_data['stats']:
                for stat, value in self.character_data['stats'].items():
                    lines.append(f"  {stat.ljust(15)}: {value}")
            else:
                lines.append("  Press 'r' to roll stats")
            lines.append("")
            lines.append("  Press Enter to accept, 'r' to reroll")
            
        elif self.stage == "name":
            lines.append("ENTER YOUR CHARACTER NAME:")
            lines.append("")
            lines.append(f"  Name: {self.character_data['name']}_")
            lines.append("")
            lines.append("  Type your name and press Enter")
            
        elif self.stage == "confirm":
            lines.append("CONFIRM YOUR CHARACTER:")
            lines.append("")
            lines.append(f"  Name:       {self.character_data['name']}")
            lines.append(f"  Species:    {self.character_data['species']}")
            lines.append(f"  Background: {self.character_data['background']}")
            lines.append(f"  Faction:    {self.character_data['faction']}")
            lines.append(f"  Class:      {self.character_data['class']}")
            lines.append("")
            if self.character_data['stats']:
                lines.append("  Stats:")
                for stat, value in self.character_data['stats'].items():
                    lines.append(f"    {stat.ljust(15)}: {value}")
            lines.append("")
            lines.append("  Press Enter to start game, 'b' to go back")
        
        lines.append("")
        lines.append("─" * 80)
        lines.append(f"[j/k or ↑/↓: navigate] [a-z: quick select] [Enter: confirm] [q: quit]")
        
        self.query_one("#main_display", Static).update("\n".join(lines))
        
    def on_key(self, event) -> None:
        """Handle keyboard input"""
        key = event.key
        
        # Quit with 'q' (except when typing name)
        if key == "q" and self.stage != "name":
            self.app.exit()
            return
        
        # Navigation keys (vim-style and arrows)
        if key in ["j", "down"]:
            self.move_cursor(1)
        elif key in ["k", "up"]:
            self.move_cursor(-1)
        elif key == "enter":
            self.action_confirm()
        elif key == "r" and self.stage == "stats":
            self.roll_stats()
        elif key == "b" and self.stage == "confirm":
            self.stage = "name"
            self.current_index = 0
            self.update_display()
        # Quick letter selection
        elif len(key) == 1 and key.isalpha() and self.stage not in ["name", "stats", "confirm"]:
            idx = ord(key.lower()) - ord('a')
            if 0 <= idx < len(self.get_current_list()):
                self.current_index = idx
                self.action_confirm()
        # Name entry
        elif self.stage == "name":
            if key == "backspace" and len(self.character_data['name']) > 0:
                self.character_data['name'] = self.character_data['name'][:-1]
                self.update_display()
            elif len(key) == 1 and (key.isalnum() or key == " "):
                if len(self.character_data['name']) < 20:
                    self.character_data['name'] += key
                    self.update_display()
                    
    def move_cursor(self, delta: int):
        """Move selection cursor"""
        if self.stage in ["stats", "name", "confirm"]:
            return
            
        current_list = self.get_current_list()
        self.current_index = (self.current_index + delta) % len(current_list)
        self.update_display()
        
    def get_current_list(self):
        """Get the current selection list"""
        if self.stage == "species":
            return self.species_list
        elif self.stage == "background":
            return self.background_list
        elif self.stage == "faction":
            return self.faction_list
        elif self.stage == "class":
            return self.class_list
        return []
        
    def action_confirm(self):
        """Confirm current selection and move to next stage"""
        if self.stage == "species":
            self.character_data['species'] = self.species_list[self.current_index]
            self.stage = "background"
            self.current_index = 0
            self.query_one(MessageLog).add_message(f"Selected species: {self.character_data['species']}")
            
        elif self.stage == "background":
            self.character_data['background'] = self.background_list[self.current_index]
            self.stage = "faction"
            self.current_index = 0
            self.query_one(MessageLog).add_message(f"Selected background: {self.character_data['background']}")
            
        elif self.stage == "faction":
            self.character_data['faction'] = self.faction_list[self.current_index]
            self.stage = "class"
            self.current_index = 0
            self.query_one(MessageLog).add_message(f"Selected faction: {self.character_data['faction']}")
            
        elif self.stage == "class":
            self.character_data['class'] = self.class_list[self.current_index]
            self.stage = "stats"
            self.current_index = 0
            self.roll_stats()
            self.query_one(MessageLog).add_message(f"Selected class: {self.character_data['class']}")
            
        elif self.stage == "stats":
            if self.character_data['stats']:
                self.stage = "name"
                self.query_one(MessageLog).add_message("Stats accepted. Enter your name.")
            else:
                self.roll_stats()
                
        elif self.stage == "name":
            if len(self.character_data['name'].strip()) > 0:
                self.stage = "confirm"
                self.query_one(MessageLog).add_message("Review your character.")
            else:
                self.query_one(MessageLog).add_message("You must enter a name!")
                
        elif self.stage == "confirm":
            # Start the game!
            self.app.push_screen(MainGameScreen(self.character_data))
            
        self.update_display()
        
    def roll_stats(self):
        """Roll character stats"""
        if GAME_AVAILABLE:
            self.character_data['stats'] = create_character_stats()
        else:
            self.character_data['stats'] = {
                'Strength': random.randint(3, 18),
                'Dexterity': random.randint(3, 18),
                'Intelligence': random.randint(3, 18),
                'Wisdom': random.randint(3, 18),
                'Charisma': random.randint(3, 18),
            }
        self.query_one(MessageLog).add_message("Stats rolled! Press 'r' to reroll or Enter to accept.")
        self.update_display()


class MainGameScreen(Screen):
    """Main game screen - NetHack style with map and status"""
    
    BINDINGS = [
        Binding("q", "quit_game", "Quit", show=False),
        Binding("i", "inventory", "Inventory", show=True),
        Binding("m", "map", "Map", show=True),
        Binding("t", "trade", "Trade", show=True),
        Binding("r", "research", "Research", show=True),
        Binding("s", "status", "Status", show=True),
    ]
    
    def __init__(self, character_data):
        super().__init__()
        self.character_data = character_data
        self.game = Game() if GAME_AVAILABLE else None
        
        # Initialize game with character
        if self.game:
            self.game.player_name = character_data['name']
            self.game.character_species = character_data['species']
            self.game.character_background = character_data['background']
            self.game.character_faction = character_data['faction']
            self.game.character_class = character_data['class']
            self.game.character_stats = character_data['stats']
            self.game.character_created = True
        
    def compose(self) -> ComposeResult:
        """Compose the main game screen"""
        yield Static(id="status_bar")
        yield Static(id="main_area")
        yield MessageLog()
        
    def on_mount(self):
        """Initialize the game screen"""
        self.update_display()
        self.query_one(MessageLog).add_message(f"Welcome, {self.character_data['name']}!")
        self.query_one(MessageLog).add_message("Press 'i' for inventory, 'm' for map, 't' for trade, 'r' for research")
        
    def update_display(self):
        """Update the main display"""
        # Status bar
        status = f"[{self.character_data['name']}] [{self.character_data['class']}] "
        if self.game:
            status += f"Credits: {self.game.credits:,} | "
            status += f"Location: {self.game.current_location.get('name', 'Unknown') if hasattr(self.game, 'current_location') and self.game.current_location else 'Space'}"
        
        self.query_one("#status_bar", Static).update(status)
        
        # Main area - show overview
        lines = []
        lines.append("═" * 80)
        lines.append("GALACTIC EMPIRE MANAGEMENT".center(80))
        lines.append("═" * 80)
        lines.append("")
        lines.append(f"Commander: {self.character_data['name']}")
        lines.append(f"Species: {self.character_data['species']} | Class: {self.character_data['class']}")
        lines.append(f"Faction: {self.character_data['faction']} | Background: {self.character_data['background']}")
        lines.append("")
        lines.append("─" * 80)
        lines.append("")
        
        if self.game:
            lines.append(f"Credits: {self.game.credits:,}")
            lines.append(f"Ships: {len(self.game.owned_ships)}")
            lines.append(f"Stations: {len(self.game.owned_stations)}")
            lines.append("")
            lines.append("Recent Activity:")
            lines.append("  • Character created successfully")
            lines.append("  • Ready to begin your journey")
        else:
            lines.append("Demo Mode - Game modules not loaded")
        
        lines.append("")
        lines.append("─" * 80)
        lines.append("[i: Inventory] [m: Map] [t: Trade] [r: Research] [s: Status] [q: Menu]")
        
        self.query_one("#main_area", Static).update("\n".join(lines))
        
    def action_inventory(self):
        """Show inventory screen"""
        self.query_one(MessageLog).add_message("Opening inventory...")
        self.app.push_screen(InventoryScreen(self.game))
        
    def action_map(self):
        """Show map screen"""
        self.query_one(MessageLog).add_message("Opening galactic map...")
        
    def action_trade(self):
        """Show trade screen"""
        self.query_one(MessageLog).add_message("Opening trade interface...")
        
    def action_research(self):
        """Show research screen"""
        self.query_one(MessageLog).add_message("Opening research interface...")
        
    def action_status(self):
        """Show detailed status"""
        self.query_one(MessageLog).add_message("Opening status screen...")
        self.app.push_screen(StatusScreen(self.character_data, self.game))
        
    def action_quit_game(self):
        """Quit the game"""
        self.app.exit()


class InventoryScreen(Screen):
    """Inventory management screen"""
    
    BINDINGS = [
        Binding("escape,q", "pop_screen", "Back", show=True),
    ]
    
    def __init__(self, game):
        super().__init__()
        self.game = game
        
    def compose(self) -> ComposeResult:
        yield Static(id="inventory_display")
        yield MessageLog()
        
    def on_mount(self):
        lines = []
        lines.append("═" * 80)
        lines.append("INVENTORY".center(80))
        lines.append("═" * 80)
        lines.append("")
        
        if self.game and self.game.inventory:
            for item, qty in self.game.inventory.items():
                lines.append(f"  {item}: {qty}")
        else:
            lines.append("  Your cargo hold is empty.")
            
        lines.append("")
        lines.append("─" * 80)
        lines.append("[q/ESC: Back]")
        
        self.query_one("#inventory_display", Static).update("\n".join(lines))
        self.query_one(MessageLog).add_message("Inventory displayed. Press 'q' to return.")


class StatusScreen(Screen):
    """Character status screen"""
    
    BINDINGS = [
        Binding("escape,q", "pop_screen", "Back", show=True),
    ]
    
    def __init__(self, character_data, game):
        super().__init__()
        self.character_data = character_data
        self.game = game
        
    def compose(self) -> ComposeResult:
        yield Static(id="status_display")
        yield MessageLog()
        
    def on_mount(self):
        lines = []
        lines.append("═" * 80)
        lines.append("CHARACTER STATUS".center(80))
        lines.append("═" * 80)
        lines.append("")
        lines.append(f"Name:       {self.character_data['name']}")
        lines.append(f"Species:    {self.character_data['species']}")
        lines.append(f"Class:      {self.character_data['class']}")
        lines.append(f"Background: {self.character_data['background']}")
        lines.append(f"Faction:    {self.character_data['faction']}")
        lines.append("")
        
        if self.character_data.get('stats'):
            lines.append("STATISTICS:")
            for stat, value in self.character_data['stats'].items():
                lines.append(f"  {stat.ljust(15)}: {value}")
        
        lines.append("")
        
        if self.game:
            lines.append(f"Credits:    {self.game.credits:,}")
            lines.append(f"Level:      {self.game.level}")
            lines.append(f"Experience: {self.game.xp}")
            
        lines.append("")
        lines.append("─" * 80)
        lines.append("[q/ESC: Back]")
        
        self.query_one("#status_display", Static).update("\n".join(lines))
        self.query_one(MessageLog).add_message("Status displayed. Press 'q' to return.")


class NetHackInterface(App):
    """Main NetHack-style application"""
    
    CSS = """
    Screen {
        background: black;
        color: white;
    }
    
    Static {
        background: black;
        color: white;
    }
    
    MessageLog {
        dock: bottom;
        height: 4;
        background: black;
        color: yellow;
        border: solid white;
    }
    
    #status_bar {
        dock: top;
        height: 1;
        background: blue;
        color: white;
    }
    
    #main_display, #main_area, #inventory_display, #status_display {
        height: 1fr;
    }
    """
    
    TITLE = "Galactic Empire 4X"
    
    def on_mount(self):
        """Start with character creation"""
        self.push_screen(CharacterCreationScreen())


def main():
    """Run the NetHack-style interface"""
    app = NetHackInterface()
    app.run()


if __name__ == "__main__":
    main()
