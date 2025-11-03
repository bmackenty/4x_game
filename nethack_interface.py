#!/usr/bin/env python3
"""
NetHack-Style Interface for 4X Game
Pure keyboard control, ASCII-based UI inspired by NetHack/Roguelikes
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
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
    from navigation import Ship
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
        
    def add_message(self, msg: str, color: str = "white"):
        """Add a message to the log with optional color"""
        self.messages.append((msg, color))
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
        self.update_display()
    
    def update_display(self):
        """Update the message display with colors"""
        text = Text()
        for msg, color in self.messages[-self.max_messages:]:
            text.append(msg + "\n", style=color)
        self.update(text if text else " ")


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

            # Ensure player starts with a ship, based on class defaults
            try:
                cls = self.game.character_class
                if cls and cls in character_classes:
                    class_info = character_classes[cls]
                    # Add any class-defined starting ships
                    if 'starting_ships' in class_info:
                        for ship_name in class_info['starting_ships']:
                            if ship_name not in self.game.owned_ships:
                                self.game.owned_ships.append(ship_name)
                # Fallback: always grant a Basic Transport if still no ships
                if not self.game.owned_ships:
                    self.game.owned_ships.append("Basic Transport")
            except Exception:
                # Conservative fallback if anything goes wrong
                if not self.game.owned_ships:
                    self.game.owned_ships.append("Basic Transport")

            # Ensure navigation has a current ship to use on the map
            try:
                if hasattr(self.game, 'navigation') and self.game.navigation and not self.game.navigation.current_ship:
                    first_ship = self.game.owned_ships[0] if self.game.owned_ships else "Basic Transport"
                    # Use the ship name as class for standard ships to match Navigation expectations
                    self.game.navigation.current_ship = Ship(first_ship, first_ship)
            except Exception:
                pass
        
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
        if self.game and self.game.owned_ships:
            starter = ", ".join(self.game.owned_ships)
            self.query_one(MessageLog).add_message(f"Starter ship(s): {starter}")
        
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
        lines.append("[i: Inventory] [m: Map] [r: Research] [s: Status] [q: Menu]")
        
        self.query_one("#main_area", Static).update("\n".join(lines))
        
    def action_inventory(self):
        """Show inventory screen"""
        self.query_one(MessageLog).add_message("Opening inventory...")
        self.app.push_screen(InventoryScreen(self.game))
        
    def action_map(self):
        """Show map screen"""
        self.query_one(MessageLog).add_message("Opening galactic map...")
        self.app.push_screen(MapScreen(self.game))
        
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


class MapScreen(Screen):
    """Galaxy map screen (NetHack-style ASCII map)"""
    
    BINDINGS = [
        Binding("escape,q", "pop_screen", "Back", show=True),
    ]
    
    def __init__(self, game):
        super().__init__()
        self.game = game
        # Viewport size (visible area)
        self.viewport_width = 78
        self.viewport_height = 20
        # Virtual map size (much larger than viewport)
        self.virtual_width = 200
        self.virtual_height = 60
        # Viewport offset (camera position in virtual coordinates)
        self.viewport_x = 0
        self.viewport_y = 0
        # Scroll margin (distance from edge before scrolling)
        self.scroll_margin = 3
    
    def compose(self) -> ComposeResult:
        yield Static(id="map_display")
        yield MessageLog()
    
    def on_mount(self):
        # Ensure a current ship exists for positioning
        try:
            if hasattr(self.game, 'navigation') and self.game.navigation and not self.game.navigation.current_ship:
                first_ship = self.game.owned_ships[0] if self.game.owned_ships else "Basic Transport"
                self.game.navigation.current_ship = Ship(first_ship, first_ship)
        except Exception:
            pass

        self.update_map()
        msg_log = self.query_one(MessageLog)
        msg_log.add_message("Map displayed!", "cyan")
        msg_log.add_message("@ = Your ship | * = Visited | + = Unvisited | ◈/◆ = Stations", "white")
    
    def update_map(self):
        nav = getattr(self.game, 'navigation', None)
        if not nav or not nav.galaxy:
            self.query_one("#map_display", Static).update("Galaxy data unavailable")
            return
        galaxy = nav.galaxy
        ship = nav.current_ship
        
        # Initialize virtual buffer - store (char, system_data) tuples
        virtual_buf = [[(" ", None)] * self.virtual_width for _ in range(self.virtual_height)]
        
        def project(x, y):
            # Scale galaxy coordinates to virtual map coordinates
            px = int((x / galaxy.size_x) * (self.virtual_width - 1))
            py = int((y / galaxy.size_y) * (self.virtual_height - 1))
            # Clamp
            px = max(0, min(self.virtual_width - 1, px))
            py = max(0, min(self.virtual_height - 1, py))
            return px, py
        
        # Plot systems on virtual buffer with system data
        for sys in galaxy.systems.values():
            x, y, _ = sys["coordinates"]
            px, py = project(x, y)
            # Different symbols for systems with stations
            has_stations = sys.get("stations") and len(sys.get("stations", [])) > 0
            if has_stations:
                ch = "◈" if sys.get("visited") else "◆"  # Diamond for stations
            else:
                ch = "*" if sys.get("visited") else "+"
            virtual_buf[py][px] = (ch, sys)
        
        # Plot ship last
        ship_vx = ship_vy = 0
        if ship:
            sx, sy, _ = ship.coordinates
            ship_vx, ship_vy = project(sx, sy)
            virtual_buf[ship_vy][ship_vx] = ("@", None)
            
            # Center viewport on ship
            self.center_viewport_on(ship_vx, ship_vy)
        
        # Build Rich Text with colors
        text = Text()
        
        # Header
        text.append("═" * self.viewport_width + "\n", style="bold cyan")
        text.append("GALAXY MAP".center(self.viewport_width) + "\n", style="bold yellow")
        text.append("═" * self.viewport_width + "\n", style="bold cyan")
        
        # Render viewport with colors
        for y in range(self.viewport_height):
            virtual_y = self.viewport_y + y
            if 0 <= virtual_y < self.virtual_height:
                for x in range(self.viewport_width):
                    virtual_x = self.viewport_x + x
                    if 0 <= virtual_x < self.virtual_width:
                        char, sys_data = virtual_buf[virtual_y][virtual_x]
                        
                        # Color based on character type
                        if char == "@":
                            text.append(char, style="bold bright_white on blue")
                        elif char in ["◈", "◆"]:
                            # Stations - cyan/bright_cyan
                            if char == "◈":
                                text.append(char, style="bright_cyan")
                            else:
                                text.append(char, style="cyan")
                        elif char == "*":
                            # Visited system - green
                            text.append(char, style="green")
                        elif char == "+":
                            # Unvisited system - yellow
                            text.append(char, style="yellow")
                        else:
                            text.append(char)
                    else:
                        text.append(" ")
                text.append("\n")
            else:
                text.append(" " * self.viewport_width + "\n")
        
        # HUD
        text.append("─" * self.viewport_width + "\n", style="bold white")
        if ship:
            sx, sy, sz = ship.coordinates
            text.append(f"Ship: ", style="white")
            text.append(f"{ship.name}", style="bold cyan")
            text.append(f" ({ship.ship_class})  Pos: ({sx},{sy},{sz})\n", style="white")
            text.append(f"Fuel: ", style="white")
            fuel_pct = ship.fuel / ship.max_fuel if ship.max_fuel > 0 else 0
            fuel_color = "green" if fuel_pct > 0.5 else "yellow" if fuel_pct > 0.25 else "red"
            text.append(f"{ship.fuel}/{ship.max_fuel}", style=fuel_color)
            text.append(f"  Range: {ship.jump_range}\n", style="white")
        
        visited_count = sum(1 for s in galaxy.systems.values() if s.get("visited"))
        text.append(f"Systems: ", style="white")
        text.append(f"{len(galaxy.systems)}", style="bold yellow")
        text.append(f" | Visited: ", style="white")
        text.append(f"{visited_count}", style="bold green")
        text.append("\n", style="white")
        
        # Legend
        text.append("Legend: ", style="white")
        text.append("@ ", style="bold bright_white on blue")
        text.append("You  ", style="white")
        text.append("* ", style="green")
        text.append("Visited  ", style="white")
        text.append("+ ", style="yellow")
        text.append("Unvisited  ", style="white")
        text.append("◈ ", style="bright_cyan")
        text.append("Station(Vis)  ", style="white")
        text.append("◆ ", style="cyan")
        text.append("Station\n", style="white")
        
        text.append("[q/ESC: Back | Arrow/hjkl: Move]\n", style="dim white")
        
        self.query_one("#map_display", Static).update(text)
    
    def center_viewport_on(self, vx, vy):
        """Center the viewport on the given virtual coordinates"""
        # Calculate desired top-left corner
        target_x = vx - self.viewport_width // 2
        target_y = vy - self.viewport_height // 2
        
        # Clamp to valid range
        self.viewport_x = max(0, min(self.virtual_width - self.viewport_width, target_x))
        self.viewport_y = max(0, min(self.virtual_height - self.viewport_height, target_y))
    
    def action_pop_screen(self):
        self.app.pop_screen()

    def on_key(self, event) -> None:
        """Arrow/HJKL movement on the map; entering a system opens interaction screen"""
        key = event.key
        dx = dy = 0
        if key in ["left", "h"]:
            dx = -1
        elif key in ["right", "l"]:
            dx = 1
        elif key in ["up", "k"]:
            dy = -1
        elif key in ["down", "j"]:
            dy = 1
        else:
            return

        nav = getattr(self.game, 'navigation', None)
        if not nav or not nav.galaxy or not nav.current_ship:
            return
        galaxy = nav.galaxy
        ship = nav.current_ship

        # Movement step - based on virtual map for smoother scrolling
        step_x = max(1, round(galaxy.size_x / self.virtual_width))
        step_y = max(1, round(galaxy.size_y / self.virtual_height))

        # Move within galaxy bounds
        x, y, z = ship.coordinates
        x = max(0, min(galaxy.size_x, x + dx * step_x))
        y = max(0, min(galaxy.size_y, y + dy * step_y))
        ship.coordinates = (x, y, z)

        # Check if we're on a system
        def project(px, py):
            sx = int((px / galaxy.size_x) * (self.virtual_width - 1))
            sy = int((py / galaxy.size_y) * (self.virtual_height - 1))
            sx = max(0, min(self.virtual_width - 1, sx))
            sy = max(0, min(self.virtual_height - 1, sy))
            return sx, sy

        ship_cell = project(x, y)
        overlapping = []
        for sys in galaxy.systems.values():
            cx, cy, cz = sys["coordinates"]
            if project(cx, cy) == ship_cell:
                overlapping.append(sys)

        entered_system = None
        if overlapping:
            # Snap to the nearest system in this cell and mark visited
            def dist(a, b):
                ax, ay, az = a; bx, by, bz = b
                return ((ax-bx)**2 + (ay-by)**2 + (az-bz)**2) ** 0.5
            entered_system = min(overlapping, key=lambda s: dist((x, y, z), s["coordinates"]))
            ship.coordinates = entered_system["coordinates"]
            entered_system["visited"] = True

        self.update_map()

        if entered_system:
            # Determine what objects are present
            msg_log = self.query_one(MessageLog)
            msg_log.add_message(f"Arrived at {entered_system['name']}", "bright_cyan")
            
            # Show what celestial bodies are here
            bodies = entered_system.get('celestial_bodies', [])
            if bodies:
                # Identify primary object type
                planets = [b for b in bodies if b['object_type'] == 'Planet']
                moons = [b for b in bodies if b['object_type'] == 'Moon']
                asteroids = [b for b in bodies if b['object_type'] == 'Asteroid Belt']
                nebulae = [b for b in bodies if b['object_type'] == 'Nebula']
                stations = entered_system.get('stations', [])
                
                # Build description of what's here
                primary_objects = []
                
                if planets:
                    # Mention habitable planets specifically
                    habitable = [p for p in planets if p.get('habitable')]
                    if habitable:
                        primary_objects.append(f"{len(habitable)} habitable planet{'s' if len(habitable) > 1 else ''}")
                    elif len(planets) == 1:
                        primary_objects.append(f"1 {planets[0]['subtype'].lower()}")
                    else:
                        primary_objects.append(f"{len(planets)} planets")
                
                if moons:
                    primary_objects.append(f"{len(moons)} moon{'s' if len(moons) > 1 else ''}")
                
                if asteroids:
                    mineral_rich = [a for a in asteroids if a.get('mineral_rich')]
                    if mineral_rich:
                        primary_objects.append("mineral-rich asteroid belt")
                    else:
                        primary_objects.append("asteroid belt")
                
                if nebulae:
                    hazardous = [n for n in nebulae if n.get('hazardous')]
                    if hazardous:
                        primary_objects.append(f"hazardous {nebulae[0]['name'].lower()}")
                    else:
                        primary_objects.append(nebulae[0]['name'].lower())
                
                if stations:
                    primary_objects.append(f"{len(stations)} space station{'s' if len(stations) > 1 else ''}")
                
                if primary_objects:
                    msg_log.add_message(f"System contains: {', '.join(primary_objects)}", "yellow")
            
            self.app.push_screen(SystemInteractionScreen(self.game, entered_system))


class SystemInteractionScreen(Screen):
    """Interaction screen when entering a star system: trade/repair/refuel/etc."""

    BINDINGS = [
        Binding("escape,q", "pop_screen", "Back", show=True),
    ]

    def __init__(self, game, system):
        super().__init__()
        self.game = game
        self.system = system
        self.available_actions = []  # Will store (number, name, handler, description)

    def compose(self) -> ComposeResult:
        yield Static(id="system_display")
        yield MessageLog()

    def on_key(self, event):
        """Handle key presses directly"""
        # Check for number keys
        if event.character and event.character.isdigit():
            num = int(event.character)
            if num >= 1 and num <= 9:
                self._dispatch_action(num)
                event.prevent_default()
                return
        # Let other keys propagate normally

    def on_mount(self):
        self.build_available_actions()
        self.render_system()
        if self.available_actions:
            action_list = ", ".join([f"[{a[0]}] {a[1]}" for a in self.available_actions[:5]])
            self.query_one(MessageLog).add_message(f"Available: {action_list}...", "cyan")
    
    def build_available_actions(self):
        """Build list of available actions based on system contents"""
        self.available_actions = []
        action_num = 1
        
        # Basic actions always available
        self.available_actions.append((action_num, "Refuel", self.do_refuel, "Refuel your ship (10 cr/unit)"))
        action_num += 1
        
        self.available_actions.append((action_num, "Trade", self.do_trade, "Access commodity markets"))
        action_num += 1
        
        # Check for space stations with specific capabilities
        stations = self.system.get('stations', [])
        for station in stations:
            station_type = station.get('type', '')
            
            # Shipyard stations
            if 'Shipwright' in station.get('name', '') or 'Shipbuilding' in station.get('category', '') or 'Construction Yard' in station_type:
                self.available_actions.append((
                    action_num, 
                    f"Shipyard ({station.get('name', 'Unknown')})", 
                    lambda s=station: self.do_shipyard(s),
                    "Build or upgrade ships"
                ))
                action_num += 1
            
            # Trading Hub stations (enhanced trading)
            if 'Trade' in station.get('category', '') or 'Trade Hub' in station_type or 'Market' in station.get('name', ''):
                self.available_actions.append((
                    action_num,
                    f"Market ({station.get('name', 'Unknown')})",
                    lambda s=station: self.do_station_market(s),
                    "Access enhanced station markets"
                ))
                action_num += 1
            
            # Research stations
            if 'Research' in station.get('category', '') or 'Lab' in station_type:
                self.available_actions.append((
                    action_num,
                    f"Research ({station.get('name', 'Unknown')})",
                    lambda s=station: self.do_research(s),
                    "Access research facilities"
                ))
                action_num += 1
        
        # Check for habitable planets - species interaction
        bodies = self.system.get('celestial_bodies', [])
        habitable_planets = [b for b in bodies if b.get('object_type') == 'Planet' and b.get('habitable')]
        if habitable_planets:
            self.available_actions.append((
                action_num,
                "Visit Colony",
                lambda: self.do_visit_colony(habitable_planets[0]),
                "Interact with planetary inhabitants"
            ))
            action_num += 1
        
        # Check for asteroid belts - mining
        asteroid_belts = [b for b in bodies if b.get('object_type') == 'Asteroid Belt']
        if asteroid_belts:
            # Check if ship has mining capability (placeholder - you'd check ship equipment)
            can_mine = True  # TODO: Check ship has mining equipment
            if can_mine:
                self.available_actions.append((
                    action_num,
                    "Mine Asteroids",
                    lambda: self.do_mining(asteroid_belts[0]),
                    "Extract minerals from asteroid belt"
                ))
                action_num += 1
        
        # Repair option
        self.available_actions.append((action_num, "Repair", self.do_repair, "Repair ship damage"))
        action_num += 1

    def render_system(self):
        text = Text()
        
        # Header
        text.append("═" * 80 + "\n", style="bold cyan")
        text.append(f"{self.system['name']}".center(80) + "\n", style="bold yellow")
        text.append("═" * 80 + "\n", style="bold cyan")
        text.append("\n")
        
        # System info with colors
        text.append(f"Type: ", style="white")
        sys_type = self.system.get('type', 'Unknown')
        type_colors = {
            'Core World': 'bright_cyan',
            'Industrial': 'yellow',
            'Military': 'red',
            'Research': 'magenta',
            'Trading Hub': 'green',
            'Mining': 'bright_yellow',
            'Agricultural': 'bright_green',
            'Frontier': 'white'
        }
        text.append(f"{sys_type}\n", style=type_colors.get(sys_type, 'white'))
        
        text.append(f"Population: ", style="white")
        text.append(f"{self.system.get('population',0):,}\n", style="cyan")
        
        text.append(f"Resources: ", style="white")
        resources = self.system.get('resources', 'Unknown')
        res_colors = {'Rich': 'green', 'Abundant': 'bright_green', 'Moderate': 'yellow', 'Poor': 'red', 'Depleted': 'bright_red'}
        text.append(f"{resources}\n", style=res_colors.get(resources, 'white'))
        
        text.append(f"Threat: ", style="white")
        threat = self.system.get('threat_level', 0)
        threat_color = 'green' if threat <= 3 else 'yellow' if threat <= 6 else 'red'
        text.append(f"{threat}/10\n", style=threat_color)
        text.append("\n")
        
        # Description
        if self.system.get('description'):
            text.append(self.system['description'] + "\n\n", style="italic white")
        
        # Celestial Bodies
        celestial_bodies = self.system.get('celestial_bodies', [])
        if celestial_bodies:
            text.append("━" * 80 + "\n", style="blue")
            text.append("CELESTIAL BODIES:\n", style="bold bright_blue")
            text.append("━" * 80 + "\n", style="blue")
            
            # Group by type for better display
            planets = [b for b in celestial_bodies if b['object_type'] == 'Planet']
            moons = [b for b in celestial_bodies if b['object_type'] == 'Moon']
            asteroids = [b for b in celestial_bodies if b['object_type'] == 'Asteroid Belt']
            nebulae = [b for b in celestial_bodies if b['object_type'] == 'Nebula']
            comets = [b for b in celestial_bodies if b['object_type'] == 'Comet']
            
            # Display planets
            if planets:
                text.append("Planets:\n", style="bold yellow")
                for planet in planets:
                    text.append(f"  • ", style="yellow")
                    text.append(f"{planet['name']}", style="bright_yellow")
                    text.append(f" - {planet['subtype']}", style="yellow")
                    if planet.get('habitable'):
                        text.append(" [HABITABLE]", style="bright_green")
                    if planet.get('has_atmosphere'):
                        text.append(" [Atmosphere]", style="cyan")
                    text.append("\n")
            
            # Display moons
            if moons:
                text.append("Moons:\n", style="bold white")
                for moon in moons:
                    text.append(f"  • ", style="white")
                    text.append(f"{moon['name']}", style="bright_white")
                    text.append(f" (orbits {moon['orbits']})", style="dim white")
                    if moon.get('has_resources'):
                        text.append(" [Rich Resources]", style="green")
                    text.append("\n")
            
            # Display asteroid belts
            if asteroids:
                for belt in asteroids:
                    text.append(f"  • ", style="white")
                    text.append(f"{belt['name']}", style="yellow")
                    text.append(f" - {belt['density']} density", style="white")
                    if belt.get('mineral_rich'):
                        text.append(" [Mineral Rich]", style="bright_green")
                    text.append("\n")
            
            # Display nebulae
            if nebulae:
                for nebula in nebulae:
                    text.append(f"  • ", style="magenta")
                    text.append(f"{nebula['name']}", style="bright_magenta")
                    if nebula.get('hazardous'):
                        text.append(" [HAZARDOUS]", style="red")
                    text.append("\n")
            
            # Display comets
            if comets:
                for comet in comets:
                    text.append(f"  • ", style="cyan")
                    text.append(f"{comet['name']}", style="bright_cyan")
                    if comet.get('active'):
                        text.append(" [Active]", style="yellow")
                    text.append("\n")
            
            text.append("\n")
        
        # Space Stations
        stations = self.system.get('stations', [])
        if stations:
            text.append("━" * 80 + "\n", style="cyan")
            text.append("SPACE STATIONS:\n", style="bold bright_cyan")
            text.append("━" * 80 + "\n", style="cyan")
            for i, station in enumerate(stations, 1):
                text.append(f"{i}. ", style="white")
                text.append(f"{station.get('name', 'Unknown Station')}", style="bold bright_cyan")
                text.append(f" [{station.get('category', 'Unknown')}]\n", style="cyan")
                text.append(f"   Type: ", style="white")
                text.append(f"{station.get('type', 'Unknown')}\n", style="yellow")
                text.append(f"   ", style="white")
                text.append(f"{station.get('description', 'No description available.')}\n", style="dim white")
            text.append("\n")
        
        # Old station manager system (if still used)
        try:
            coords = self.system['coordinates']
            # Station
            station = None
            if hasattr(self.game, 'station_manager') and self.game.station_manager:
                station = self.game.station_manager.get_station_at_location(coords)
            if station:
                owner_status = "YOUR STATION" if station['owner'] == "Player" else "Available for Purchase"
                text.append(f"Station: {station['name']} ({station['type']}) - {owner_status}\n", style="bright_cyan")
            # Faction
            if hasattr(self.game, 'faction_system') and self.game.faction_system:
                fac = self.game.faction_system.get_system_faction(coords)
                if fac:
                    rep = self.game.faction_system.get_reputation_status(fac)
                    rep_colors = {'Revered': 'bright_green', 'Honored': 'green', 'Friendly': 'cyan', 
                                  'Neutral': 'white', 'Unfriendly': 'yellow', 'Hostile': 'red', 'Hated': 'bright_red'}
                    text.append(f"Control: ", style="white")
                    text.append(f"{fac}", style="yellow")
                    text.append(f" | Your Standing: ", style="white")
                    text.append(f"{rep}\n", style=rep_colors.get(rep, 'white'))
        except Exception:
            pass

        text.append("\n")
        
        # Ship status
        nav = getattr(self.game, 'navigation', None)
        ship = nav.current_ship if nav else None
        if ship:
            sx, sy, sz = ship.coordinates
            text.append(f"Ship: ", style="white")
            text.append(f"{ship.name}", style="bold cyan")
            text.append(f"  Fuel: ", style="white")
            fuel_pct = ship.fuel / ship.max_fuel if ship.max_fuel > 0 else 0
            fuel_color = "green" if fuel_pct > 0.5 else "yellow" if fuel_pct > 0.25 else "red"
            text.append(f"{ship.fuel}/{ship.max_fuel}", style=fuel_color)
            cargo_used = sum(ship.cargo.values()) if ship.cargo else 0
            text.append(f"  Cargo: ", style="white")
            cargo_pct = cargo_used / ship.max_cargo if ship.max_cargo > 0 else 0
            cargo_color = "green" if cargo_pct < 0.5 else "yellow" if cargo_pct < 0.8 else "red"
            text.append(f"{cargo_used}/{ship.max_cargo}\n", style=cargo_color)
        
        text.append("\n")
        
        # Dynamic Actions Menu
        text.append("━" * 80 + "\n", style="green")
        text.append("AVAILABLE ACTIONS:\n", style="bold bright_green")
        text.append("━" * 80 + "\n", style="green")
        
        for num, name, handler, description in self.available_actions:
            text.append(f"[", style="white")
            text.append(f"{num}", style="bold yellow")
            text.append(f"] ", style="white")
            text.append(f"{name}", style="bright_white")
            text.append(f" - {description}\n", style="dim white")
        
        text.append("\n")
        text.append("[", style="white")
        text.append("1-9", style="bold cyan")
        text.append("] Select action  [", style="white")
        text.append("q/ESC", style="bold cyan")
        text.append("] Back\n", style="white")
        
        self.query_one("#system_display", Static).update(text)

    def action_pop_screen(self):
        self.app.pop_screen()
    
    def _dispatch_action(self, num):
        """Dispatch to the appropriate action handler"""
        for action_num, name, handler, desc in self.available_actions:
            if action_num == num:
                self.query_one(MessageLog).add_message(f"Accessing: {name}", "cyan")
                handler()
                return
        self.query_one(MessageLog).add_message(f"No action {num} available", "red")
    
    # Action Handlers
    def do_refuel(self):
        """Refuel current ship if at a system and with enough credits"""
        nav = getattr(self.game, 'navigation', None)
        ship = nav.current_ship if nav else None
        if not ship:
            self.query_one(MessageLog).add_message("No ship to refuel.", "red")
            return
        fuel_needed = ship.max_fuel - ship.fuel
        if fuel_needed <= 0:
            self.query_one(MessageLog).add_message("Ship already fully fueled.", "yellow")
            return
        cost = fuel_needed * 10
        if cost > self.game.credits:
            self.query_one(MessageLog).add_message(f"Insufficient credits ({cost} needed).", "red")
            return
        self.game.credits -= cost
        ship.fuel = ship.max_fuel
        self.query_one(MessageLog).add_message(f"Refueled for {cost} credits.", "green")
        self.render_system()

    def do_trade(self):
        """Open trading interface"""
        self.app.push_screen(TradingScreen(self.game))
    
    def do_repair(self):
        """Repair ship"""
        self.app.push_screen(RepairScreen(self.game, self.system))
    
    def do_shipyard(self, station):
        """Access shipyard at a station"""
        self.query_one(MessageLog).add_message(f"Accessing shipyard at {station.get('name')}...", "cyan")
        self.app.push_screen(ShipyardScreen(self.game, self.system, station))
    
    def do_station_market(self, station):
        """Access enhanced station market"""
        self.query_one(MessageLog).add_message(f"Accessing markets at {station.get('name')}...", "cyan")
        # Use regular trading screen for now, could be enhanced later
        self.app.push_screen(TradingScreen(self.game))
    
    def do_research(self, station):
        """Access research station"""
        self.query_one(MessageLog).add_message(f"Accessing research at {station.get('name')}...", "cyan")
        self.app.push_screen(ResearchScreen(self.game, self.system, station))
    
    def do_visit_colony(self, planet):
        """Visit habitable planet for species interaction"""
        self.query_one(MessageLog).add_message(f"Landing on {planet.get('name')} ({planet.get('subtype')})...", "cyan")
        self.app.push_screen(ColonyInteractionScreen(self.game, self.system, planet))
    
    def do_mining(self, asteroid_belt):
        """Mine asteroid belt"""
        self.query_one(MessageLog).add_message(f"Initiating mining operations...", "cyan")
        self.app.push_screen(MiningScreen(self.game, self.system, asteroid_belt))


class TradingScreen(Screen):
    """Trading interface screen (buy/sell commodities)"""

    BINDINGS = [
        Binding("escape,q", "pop_screen", "Back", show=True),
        Binding("tab", "toggle_mode", "Toggle Buy/Sell", show=True),
        Binding("enter", "confirm", "Confirm", show=True),
        Binding("j,down", "cursor_down", "Down", show=False),
        Binding("k,up", "cursor_up", "Up", show=False),
        Binding("+", "inc_qty", "+", show=False),
        Binding("-", "dec_qty", "-", show=False),
        Binding("b", "confirm_buy", "Buy", show=True),
        Binding("s", "confirm_sell", "Sell", show=True),
        Binding("g", "refresh", "Refresh", show=False),
        Binding("m", "toggle_analysis", "Market", show=True),
        Binding("o", "show_opportunities", "Opportunities", show=True),
    ]

    def __init__(self, game):
        super().__init__()
        self.game = game
        self.mode = "buy"  # or "sell" or "analysis" or "opportunities"
        self.system_name = None
        self.buy_items = []   # list of (name, price, supply)
        self.sell_items = []  # list of (name, owned_qty, price, demand)
        self.selected_index = 0
        self.quantity = 1
        self.trade_scroll_offset = 0  # For scrolling long lists

    def compose(self) -> ComposeResult:
        yield Static(id="trade_display")
        yield MessageLog()

    def on_mount(self):
        self.system_name = self._get_system_name()
        if not self.system_name:
            self.query_one("#trade_display", Static).update("Not at a star system. Navigate to a system to trade.")
            self.query_one(MessageLog).add_message("No market here.", "red")
            return
        self.refresh_lists()
        self.update_display()
        self.query_one(MessageLog).add_message(f"Trading at {self.system_name}. Tab toggles Buy/Sell.", "green")

    def _get_system_name(self):
        try:
            nav = getattr(self.game, 'navigation', None)
            if not nav or not nav.current_ship:
                return None
            x, y, z = nav.current_ship.coordinates
            system = nav.galaxy.get_system_at(x, y, z)
            return system['name'] if system else None
        except Exception:
            return None

    def refresh_lists(self):
        self.buy_items = []
        self.sell_items = []
        try:
            info = self.game.economy.get_market_info(self.system_name) if self.system_name else None
            if not info:
                return
            market = info['market']
            
            # Buy list: commodities with supply > 0
            for commodity, supply in market['supply'].items():
                if supply > 0:
                    price = market['prices'][commodity]
                    self.buy_items.append((commodity, price, supply))
            self.buy_items.sort(key=lambda x: x[1])
            
            # Sell list: inventory items with market demand > 0
            inv = getattr(self.game, 'inventory', {}) or {}
            for commodity, owned_qty in inv.items():
                if owned_qty > 0 and commodity in market['demand'] and market['demand'][commodity] > 0:
                    price = market['prices'][commodity]
                    demand = market['demand'][commodity]
                    self.sell_items.append((commodity, owned_qty, price, demand))
            self.sell_items.sort(key=lambda x: x[2], reverse=True)
        finally:
            # Clamp selection index
            items = self.buy_items if self.mode == "buy" else self.sell_items
            if not items:
                self.selected_index = 0
            else:
                self.selected_index = max(0, min(self.selected_index, len(items) - 1))
            # Reset quantity to sane default
            if self.quantity <= 0:
                self.quantity = 1

    def update_display(self):
        lines = []
        lines.append("═" * 80)
        title = f"TRADING - {self.system_name or 'No Market'}"
        lines.append(title.center(80))
        lines.append("═" * 80)
        lines.append("")

        # Status bar
        credits = getattr(self.game, 'credits', 0)
        lines.append(f"Credits: {credits:,}")
        
        # Cargo status
        cargo = self.game.get_cargo_status()
        cargo_bar_width = 20
        cargo_filled = int(cargo['percentage'] / 100 * cargo_bar_width) if cargo['max'] > 0 else 0
        cargo_bar = "[" + ("█" * cargo_filled) + ("·" * (cargo_bar_width - cargo_filled)) + "]"
        lines.append(f"Cargo: {cargo['used']}/{cargo['max']} {cargo_bar} {cargo['percentage']:.0f}%")
        
        # Mode display
        if self.mode == "analysis":
            lines.append(f"Mode: MARKET ANALYSIS    [M to return to trading]")
        elif self.mode == "opportunities":
            lines.append(f"Mode: TRADE OPPORTUNITIES    [O to return to trading]")
        else:
            lines.append(f"Mode: {'BUY' if self.mode == 'buy' else 'SELL'}    [Tab: toggle | M: analysis | O: routes]")
        lines.append("")
        lines.append("─" * 80)
        lines.append("")

        # Display based on mode
        if self.mode == "analysis":
            self._display_market_analysis(lines)
        elif self.mode == "opportunities":
            self._display_trade_opportunities(lines)
        else:
            self._display_trade_list(lines)

        lines.append("")
        lines.append("─" * 80)
        if self.mode in ["analysis", "opportunities"]:
            lines.append("[M/O: Toggle view] [q/ESC: Back]")
        else:
            lines.append("[Tab: Toggle] [Enter: Confirm] [+/−: Qty] [j/k/↑/↓: Move] [M: Analysis] [O: Routes] [q/ESC: Back]")
        self.query_one("#trade_display", Static).update("\n".join(lines))

    def _display_market_analysis(self, lines):
        """Display market analysis with best buys and sells"""
        deals = self.game.get_market_best_deals(self.system_name)
        
        lines.append("MARKET ANALYSIS - BEST BUYING OPPORTUNITIES:")
        lines.append("")
        if deals['best_buys']:
            lines.append(f"{'Commodity':<25} {'Price':>10} {'Supply':>10}")
            lines.append("-" * 50)
            for commodity, price, supply in deals['best_buys']:
                lines.append(f"{commodity:<25} {price:>10,} cr {supply:>10}")
        else:
            lines.append("  No good buying opportunities")
        
        lines.append("")
        lines.append("BEST SELLING OPPORTUNITIES:")
        lines.append("")
        if deals['best_sells']:
            lines.append(f"{'Commodity':<25} {'Price':>10} {'Demand':>10}")
            lines.append("-" * 50)
            for commodity, price, demand in deals['best_sells']:
                lines.append(f"{commodity:<25} {price:>10,} cr {demand:>10}")
        else:
            lines.append("  No good selling opportunities")

    def _display_trade_opportunities(self, lines):
        """Display profitable trade routes"""
        routes = self.game.get_trade_routes()
        
        lines.append("PROFITABLE TRADE ROUTES:")
        lines.append("")
        if routes:
            lines.append(f"{'Commodity':<20} {'From':<15} {'To':<15} {'Buy':>8} {'Sell':>8} {'Profit':>8}")
            lines.append("-" * 80)
            for route in routes:
                lines.append(
                    f"{route['commodity'][:19]:<20} "
                    f"{route['source'][:14]:<15} "
                    f"{route['destination'][:14]:<15} "
                    f"{route['buy_price']:>8,} "
                    f"{route['sell_price']:>8,} "
                    f"{route['profit_margin']:>7.1f}%"
                )
        else:
            lines.append("  No profitable trade routes found")
        lines.append("")
        lines.append("Note: Prices change with supply/demand. Routes may shift before arrival.")

    def _display_trade_list(self, lines):
        """Display buy or sell list with scrolling support"""
        # List items
        items = self.buy_items if self.mode == "buy" else self.sell_items
        if not items:
            if self.mode == "buy":
                lines.append("No commodities available to buy here.")
            else:
                lines.append("No sellable inventory here (or no market demand).")
        else:
            # Calculate visible window (show max 20 items at a time)
            max_visible = 20
            total_items = len(items)
            
            # Adjust scroll offset to keep selected item visible
            if self.selected_index < self.trade_scroll_offset:
                self.trade_scroll_offset = self.selected_index
            elif self.selected_index >= self.trade_scroll_offset + max_visible:
                self.trade_scroll_offset = self.selected_index - max_visible + 1
            
            # Clamp scroll offset
            self.trade_scroll_offset = max(0, min(self.trade_scroll_offset, max(0, total_items - max_visible)))
            
            # Display header
            header = ("#  Commodity                     Price        Avail/Demand")
            lines.append(header)
            lines.append("-" * len(header))
            
            # Show scroll indicator if needed
            if self.trade_scroll_offset > 0:
                lines.append(f"  ▲ ({self.trade_scroll_offset} items above)")
            
            # Display visible items
            end_idx = min(self.trade_scroll_offset + max_visible, total_items)
            for i in range(self.trade_scroll_offset, end_idx):
                entry = items[i]
                cursor = ">" if i == self.selected_index else " "
                if self.mode == "buy":
                    name, price, supply = entry
                    lines.append(f" {cursor} {i+1:2d}. {name:<28} {price:>8,} cr     {supply:>6}")
                else:
                    name, owned, price, demand = entry
                    lines.append(f" {cursor} {i+1:2d}. {name:<28} {price:>8,} cr     {owned:>3}/{demand:<3}")
            
            # Show scroll indicator if more items below
            if end_idx < total_items:
                lines.append(f"  ▼ ({total_items - end_idx} items below)")

            # Selected item details
            sel = items[self.selected_index]
            lines.append("")
            if self.mode == "buy":
                name, price, supply = sel
                credits = getattr(self.game, 'credits', 0)
                max_afford = credits // price if price > 0 else 0
                cargo = self.game.get_cargo_status()
                max_cargo_space = cargo['available']
                max_buy = max(0, min(supply, max_afford, max_cargo_space))
                total = self.quantity * price
                lines.append(f"Selected: {name} | Price: {price:,} | Supply: {supply}")
                lines.append(f"Qty: {self.quantity} (max {max_buy}: credits={max_afford}, cargo={max_cargo_space})   Total: {total:,}  [+/- to adjust, Enter/B to buy]")
            else:
                name, owned, price, demand = sel
                max_sell = max(0, min(owned, demand))
                total = self.quantity * price
                lines.append(f"Selected: {name} | Price: {price:,} | You: {owned} | Demand: {demand}")
                lines.append(f"Qty: {self.quantity} (max {max_sell})  Value: {total:,}  [+/- to adjust, Enter/S to sell]")

    def action_pop_screen(self):
        self.app.pop_screen()

    def action_toggle_mode(self):
        if self.mode in ["analysis", "opportunities"]:
            self.mode = "buy"
        else:
            self.mode = "sell" if self.mode == "buy" else "buy"
        self.quantity = 1
        self.selected_index = 0
        self.trade_scroll_offset = 0
        self.refresh_lists()
        self.update_display()

    def action_toggle_analysis(self):
        if self.mode == "analysis":
            self.mode = "buy"
        else:
            self.mode = "analysis"
        self.trade_scroll_offset = 0
        self.update_display()

    def action_show_opportunities(self):
        if self.mode == "opportunities":
            self.mode = "buy"
        else:
            self.mode = "opportunities"
        self.trade_scroll_offset = 0
        self.update_display()

    def action_cursor_down(self):
        if self.mode in ["analysis", "opportunities"]:
            return  # No cursor in analysis/opportunities mode
        items = self.buy_items if self.mode == "buy" else self.sell_items
        if items:
            self.selected_index = (self.selected_index + 1) % len(items)
            self.update_display()

    def action_cursor_up(self):
        if self.mode in ["analysis", "opportunities"]:
            return  # No cursor in analysis/opportunities mode
        items = self.buy_items if self.mode == "buy" else self.sell_items
        if items:
            self.selected_index = (self.selected_index - 1) % len(items)
            self.update_display()

    def action_inc_qty(self):
        self.quantity += 1
        self.update_display()

    def action_dec_qty(self):
        if self.quantity > 1:
            self.quantity -= 1
            self.update_display()

    def action_refresh(self):
        self.refresh_lists()
        self.update_display()

    def action_confirm_buy(self):
        if self.mode != "buy":
            return
        self.action_confirm()

    def action_confirm_sell(self):
        if self.mode != "sell":
            return
        self.action_confirm()

    def action_confirm(self):
        # Perform trade based on mode (only if in buy/sell mode)
        if self.mode in ["analysis", "opportunities"]:
            return  # No confirm action in analysis/opportunities
        if not self.system_name:
            return
        items = self.buy_items if self.mode == "buy" else self.sell_items
        if not items:
            return
        sel = items[self.selected_index]
        try:
            if self.mode == "buy":
                name, price, supply = sel
                max_afford = (self.game.credits // price) if price > 0 else 0
                cargo = self.game.get_cargo_status()
                max_cargo_space = cargo['available']
                qty = max(0, min(self.quantity, supply, max_afford, max_cargo_space))
                if qty <= 0:
                    self.query_one(MessageLog).add_message("Cannot buy: adjust quantity, credits, or cargo space.")
                    return
                ok, msg = self.game.perform_trade_buy(self.system_name, name, qty)
                self.query_one(MessageLog).add_message(msg)
            else:
                name, owned, price, demand = sel
                qty = max(0, min(self.quantity, owned, demand))
                if qty <= 0:
                    self.query_one(MessageLog).add_message("Cannot sell: adjust quantity or demand.")
                    return
                ok, msg = self.game.perform_trade_sell(self.system_name, name, qty)
                self.query_one(MessageLog).add_message(msg)
        finally:
            self.quantity = 1
            self.refresh_lists()
            self.update_display()


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

    def action_pop_screen(self):
        """Handle 'q' or ESC to go back to previous screen"""
        self.app.pop_screen()


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
        # Economy and progression
        if self.game:
            try:
                lines.append(f"Credits:    {self.game.credits:,}")
            except Exception:
                pass
            try:
                lines.append(f"Level:      {self.game.level}")
            except Exception:
                pass
            try:
                lines.append(f"Experience: {self.game.xp}")
            except Exception:
                pass
        
        # Divider
        lines.append("")
        lines.append("─" * 80)
        lines.append("ASSETS")
        lines.append("")
        
        # Ships
        if self.game:
            ship_names = []
            try:
                ship_names.extend(self.game.owned_ships)
            except Exception:
                pass
            try:
                # custom_ships may be dicts with 'name'
                ship_names.extend([s.get('name', 'Unnamed Custom Ship') for s in getattr(self.game, 'custom_ships', [])])
            except Exception:
                pass
            if ship_names:
                lines.append("Ships:")
                for s in ship_names:
                    lines.append(f"  • {s}")
            else:
                lines.append("Ships:  None")
            lines.append("")
        
        # Bases: Stations and Platforms
        if self.game:
            stations = getattr(self.game, 'owned_stations', []) or []
            platforms = getattr(self.game, 'owned_platforms', []) or []
            lines.append("Stations:")
            if stations:
                for st in stations:
                    lines.append(f"  • {st}")
            else:
                lines.append("  None")
            lines.append("")
            lines.append("Platforms:")
            if platforms:
                for pf in platforms:
                    lines.append(f"  • {pf}")
            else:
                lines.append("  None")
            lines.append("")
        
        # Goods / Inventory
        if self.game:
            inv = getattr(self.game, 'inventory', {}) or {}
            lines.append("Inventory:")
            if inv:
                for item, qty in inv.items():
                    lines.append(f"  {item}: {qty}")
            else:
                lines.append("  Empty")
            lines.append("")
            
        lines.append("")
        lines.append("─" * 80)
        lines.append("[q/ESC: Back]")
        
        self.query_one("#status_display", Static).update("\n".join(lines))
        self.query_one(MessageLog).add_message("Status displayed. Press 'q' to return.")

    def action_pop_screen(self):
        """Handle 'q' or ESC to go back to previous screen"""
        self.app.pop_screen()


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
    
    #main_display, #main_area, #inventory_display, #status_display, #map_display {
        height: 1fr;
    }
    """
    
    TITLE = "Galactic Empire 4X"
    
    def on_mount(self):
        """Start with character creation"""
        self.push_screen(CharacterCreationScreen())


class RepairScreen(Screen):
    """Screen for repairing ship damage"""
    
    BINDINGS = [
        Binding("escape,q", "pop_screen", "Back", show=True),
        Binding("1", "repair_hull", "Repair Hull", show=False),
        Binding("2", "repair_systems", "Repair Systems", show=False),
        Binding("3", "repair_all", "Repair All", show=False),
    ]
    
    def __init__(self, game, system):
        super().__init__()
        self.game = game
        self.system = system
    
    def compose(self) -> ComposeResult:
        yield Static(id="repair_display")
        yield MessageLog()
    
    def on_mount(self):
        self.render_repair()
        self.query_one(MessageLog).add_message("Repair bay accessed", "green")
    
    def render_repair(self):
        text = Text()
        
        # Header
        text.append("═" * 80 + "\n", style="bold yellow")
        text.append(f"REPAIR BAY - {self.system['name']}".center(80) + "\n", style="bold yellow")
        text.append("═" * 80 + "\n", style="bold yellow")
        text.append("\n")
        
        # Ship status
        nav = getattr(self.game, 'navigation', None)
        ship = nav.current_ship if nav else None
        
        if ship:
            text.append(f"Ship: ", style="white")
            text.append(f"{ship.name} ({ship.ship_class})\n", style="bright_cyan")
            text.append("\n")
            
            # Hull integrity (placeholder - would track actual damage)
            hull_integrity = 100  # TODO: Track actual ship damage
            text.append(f"Hull Integrity: ", style="white")
            hull_color = "green" if hull_integrity > 75 else "yellow" if hull_integrity > 40 else "red"
            text.append(f"{hull_integrity}%\n", style=hull_color)
            
            # Systems status (placeholder)
            text.append(f"Systems Status: ", style="white")
            text.append(f"Operational\n", style="green")
            text.append("\n")
        
        # Repair costs
        text.append("━" * 80 + "\n", style="cyan")
        text.append("REPAIR OPTIONS:\n", style="bold bright_cyan")
        text.append("━" * 80 + "\n", style="cyan")
        
        hull_cost = 500
        systems_cost = 300
        total_cost = hull_cost + systems_cost
        
        text.append("[", style="white")
        text.append("1", style="bold yellow")
        text.append("] Repair Hull - ", style="white")
        text.append(f"{hull_cost} credits\n", style="green")
        
        text.append("[", style="white")
        text.append("2", style="bold yellow")
        text.append("] Repair Systems - ", style="white")
        text.append(f"{systems_cost} credits\n", style="green")
        
        text.append("[", style="white")
        text.append("3", style="bold yellow")
        text.append("] Full Repair - ", style="white")
        text.append(f"{total_cost} credits ", style="green")
        text.append("(10% discount)\n", style="dim white")
        
        text.append("\n")
        text.append(f"Your Credits: ", style="white")
        text.append(f"{self.game.credits:,}\n", style="yellow")
        text.append("\n")
        
        text.append("[", style="white")
        text.append("q/ESC", style="bold cyan")
        text.append("] Back\n", style="white")
        
        self.query_one("#repair_display", Static).update(text)
    
    def action_pop_screen(self):
        self.app.pop_screen()
    
    def repair_hull(self):
        cost = 500
        if self.game.credits >= cost:
            self.game.credits -= cost
            self.query_one(MessageLog).add_message(f"Hull repaired for {cost} credits!", "green")
            self.render_repair()
        else:
            self.query_one(MessageLog).add_message("Insufficient credits!", "red")
    
    def repair_systems(self):
        cost = 300
        if self.game.credits >= cost:
            self.game.credits -= cost
            self.query_one(MessageLog).add_message(f"Systems repaired for {cost} credits!", "green")
            self.render_repair()
        else:
            self.query_one(MessageLog).add_message("Insufficient credits!", "red")
    
    def repair_all(self):
        cost = 720  # 10% discount
        if self.game.credits >= cost:
            self.game.credits -= cost
            self.query_one(MessageLog).add_message(f"Full repair completed for {cost} credits!", "green")
            self.render_repair()
        else:
            self.query_one(MessageLog).add_message("Insufficient credits!", "red")


class ShipyardScreen(Screen):
    """Screen for shipyard operations - building and upgrading ships"""
    
    BINDINGS = [
        Binding("escape,q", "pop_screen", "Back", show=True),
        Binding("1", "view_ships", "View Ships", show=False),
        Binding("2", "upgrade_ship", "Upgrade", show=False),
        Binding("3", "build_ship", "Build Ship", show=False),
    ]
    
    def __init__(self, game, system, station):
        super().__init__()
        self.game = game
        self.system = system
        self.station = station
    
    def compose(self) -> ComposeResult:
        yield Static(id="shipyard_display")
        yield MessageLog()
    
    def on_mount(self):
        self.render_shipyard()
        self.query_one(MessageLog).add_message(f"Connected to {self.station.get('name')}", "green")
    
    def render_shipyard(self):
        text = Text()
        
        # Header
        text.append("═" * 80 + "\n", style="bold cyan")
        text.append(f"SHIPYARD - {self.station.get('name', 'Unknown Station')}".center(80) + "\n", style="bold yellow")
        text.append("═" * 80 + "\n", style="bold cyan")
        text.append("\n")
        
        # Station info
        text.append(f"Type: ", style="white")
        text.append(f"{self.station.get('type', 'Unknown')}\n", style="cyan")
        text.append(f"Location: ", style="white")
        text.append(f"{self.system['name']}\n", style="yellow")
        text.append("\n")
        text.append(f"{self.station.get('description', 'A shipbuilding facility.')}\n", style="italic dim white")
        text.append("\n")
        
        # Current ship
        nav = getattr(self.game, 'navigation', None)
        ship = nav.current_ship if nav else None
        
        if ship:
            text.append("━" * 80 + "\n", style="green")
            text.append("YOUR CURRENT SHIP:\n", style="bold bright_green")
            text.append("━" * 80 + "\n", style="green")
            text.append(f"  Name: ", style="white")
            text.append(f"{ship.name}\n", style="bright_cyan")
            text.append(f"  Class: ", style="white")
            text.append(f"{ship.ship_class}\n", style="cyan")
            text.append(f"  Cargo: ", style="white")
            text.append(f"{ship.max_cargo} units\n", style="yellow")
            text.append(f"  Fuel: ", style="white")
            text.append(f"{ship.max_fuel} units\n", style="yellow")
            text.append(f"  Jump Range: ", style="white")
            text.append(f"{ship.jump_range}\n", style="yellow")
            text.append("\n")
        
        # Services
        text.append("━" * 80 + "\n", style="cyan")
        text.append("SHIPYARD SERVICES:\n", style="bold bright_cyan")
        text.append("━" * 80 + "\n", style="cyan")
        
        text.append("[", style="white")
        text.append("1", style="bold yellow")
        text.append("] View Available Ships", style="white")
        text.append(" - Browse ship catalog\n", style="dim white")
        
        text.append("[", style="white")
        text.append("2", style="bold yellow")
        text.append("] Upgrade Current Ship", style="white")
        text.append(" - Enhance capabilities\n", style="dim white")
        
        text.append("[", style="white")
        text.append("3", style="bold yellow")
        text.append("] Build New Ship", style="white")
        text.append(" - Commission new vessel\n", style="dim white")
        
        text.append("\n")
        text.append(f"Your Credits: ", style="white")
        text.append(f"{self.game.credits:,}\n", style="yellow")
        text.append("\n")
        
        text.append("[", style="white")
        text.append("q/ESC", style="bold cyan")
        text.append("] Back\n", style="white")
        
        self.query_one("#shipyard_display", Static).update(text)
    
    def action_pop_screen(self):
        self.app.pop_screen()
    
    def view_ships(self):
        self.query_one(MessageLog).add_message("Browsing ship catalog...", "cyan")
        self.query_one(MessageLog).add_message("Ship catalog display coming soon!", "yellow")
    
    def upgrade_ship(self):
        self.query_one(MessageLog).add_message("Accessing upgrade options...", "cyan")
        self.query_one(MessageLog).add_message("Ship upgrade system coming soon!", "yellow")
    
    def build_ship(self):
        self.query_one(MessageLog).add_message("Opening ship builder...", "cyan")
        self.query_one(MessageLog).add_message("Ship construction coming soon!", "yellow")


class ResearchScreen(Screen):
    """Screen for research station operations"""
    
    BINDINGS = [
        Binding("escape,q", "pop_screen", "Back", show=True),
        Binding("1", "view_research", "View Research", show=False),
        Binding("2", "start_research", "Start Research", show=False),
        Binding("3", "buy_data", "Buy Data", show=False),
    ]
    
    def __init__(self, game, system, station):
        super().__init__()
        self.game = game
        self.system = system
        self.station = station
    
    def compose(self) -> ComposeResult:
        yield Static(id="research_display")
        yield MessageLog()
    
    def on_mount(self):
        self.render_research()
        self.query_one(MessageLog).add_message(f"Connected to {self.station.get('name')}", "green")
    
    def render_research(self):
        text = Text()
        
        # Header
        text.append("═" * 80 + "\n", style="bold magenta")
        text.append(f"RESEARCH STATION - {self.station.get('name', 'Unknown Station')}".center(80) + "\n", style="bold yellow")
        text.append("═" * 80 + "\n", style="bold magenta")
        text.append("\n")
        
        # Station info
        text.append(f"Type: ", style="white")
        text.append(f"{self.station.get('type', 'Unknown')}\n", style="magenta")
        text.append(f"Location: ", style="white")
        text.append(f"{self.system['name']}\n", style="yellow")
        text.append("\n")
        text.append(f"{self.station.get('description', 'A research facility.')}\n", style="italic dim white")
        text.append("\n")
        
        # Current research
        text.append("━" * 80 + "\n", style="cyan")
        text.append("CURRENT RESEARCH:\n", style="bold bright_cyan")
        text.append("━" * 80 + "\n", style="cyan")
        
        active_research = getattr(self.game, 'active_research', None)
        if active_research:
            text.append(f"  Project: ", style="white")
            text.append(f"{active_research}\n", style="bright_magenta")
            progress = getattr(self.game, 'research_progress', 0)
            text.append(f"  Progress: ", style="white")
            text.append(f"{progress}%\n", style="cyan")
        else:
            text.append("  No active research\n", style="dim white")
        text.append("\n")
        
        # Completed research
        completed = getattr(self.game, 'completed_research', [])
        if completed:
            text.append(f"Completed Technologies: ", style="white")
            text.append(f"{len(completed)}\n", style="green")
            text.append("\n")
        
        # Services
        text.append("━" * 80 + "\n", style="magenta")
        text.append("RESEARCH SERVICES:\n", style="bold bright_magenta")
        text.append("━" * 80 + "\n", style="magenta")
        
        text.append("[", style="white")
        text.append("1", style="bold yellow")
        text.append("] View Research Tree", style="white")
        text.append(" - Browse available technologies\n", style="dim white")
        
        text.append("[", style="white")
        text.append("2", style="bold yellow")
        text.append("] Start New Research", style="white")
        text.append(" - Begin technology project\n", style="dim white")
        
        text.append("[", style="white")
        text.append("3", style="bold yellow")
        text.append("] Purchase Data", style="white")
        text.append(" - Buy completed research\n", style="dim white")
        
        text.append("\n")
        text.append(f"Your Credits: ", style="white")
        text.append(f"{self.game.credits:,}\n", style="yellow")
        text.append("\n")
        
        text.append("[", style="white")
        text.append("q/ESC", style="bold cyan")
        text.append("] Back\n", style="white")
        
        self.query_one("#research_display", Static).update(text)
    
    def action_pop_screen(self):
        self.app.pop_screen()
    
    def view_research(self):
        self.query_one(MessageLog).add_message("Accessing research database...", "cyan")
        self.query_one(MessageLog).add_message("Research tree viewer coming soon!", "yellow")
    
    def start_research(self):
        self.query_one(MessageLog).add_message("Selecting research project...", "cyan")
        self.query_one(MessageLog).add_message("Research project selector coming soon!", "yellow")
    
    def buy_data(self):
        self.query_one(MessageLog).add_message("Browsing available data...", "cyan")
        self.query_one(MessageLog).add_message("Data marketplace coming soon!", "yellow")


class ColonyInteractionScreen(Screen):
    """Screen for interacting with inhabited planets"""
    
    BINDINGS = [
        Binding("escape,q", "pop_screen", "Back", show=True),
        Binding("1", "action_1", "Trade", show=False),
        Binding("2", "action_2", "Recruit", show=False),
        Binding("3", "action_3", "Diplomacy", show=False),
    ]
    
    def __init__(self, game, system, planet):
        super().__init__()
        self.game = game
        self.system = system
        self.planet = planet
    
    def compose(self) -> ComposeResult:
        yield Static(id="colony_display")
        yield MessageLog()
    
    def on_mount(self):
        self.render_colony()
        self.query_one(MessageLog).add_message("Landed on inhabited world", "green")
    
    def render_colony(self):
        text = Text()
        
        # Header
        text.append("═" * 80 + "\n", style="bold green")
        text.append(f"COLONY - {self.planet.get('name', 'Unknown')} ({self.system['name']})".center(80) + "\n", style="bold yellow")
        text.append("═" * 80 + "\n", style="bold green")
        text.append("\n")
        
        # Planet info
        text.append(f"Planet Type: ", style="white")
        text.append(f"{self.planet.get('subtype', 'Unknown')}\n", style="cyan")
        text.append(f"Atmosphere: ", style="white")
        text.append(f"{'Breathable' if self.planet.get('has_atmosphere') else 'None'}\n", 
                   style="green" if self.planet.get('has_atmosphere') else "red")
        text.append(f"Population: ", style="white")
        text.append(f"{self.system.get('population', 0):,}\n", style="cyan")
        text.append("\n")
        
        # Species info (placeholder - would be generated based on system)
        text.append("━" * 80 + "\n", style="magenta")
        text.append("INHABITANTS:\n", style="bold bright_magenta")
        text.append("━" * 80 + "\n", style="magenta")
        
        # Generate random species for now
        import random
        species_types = ["Terran", "Aetheri", "Silvan", "Quarrellian", "Luminaut"]
        local_species = random.choice(species_types)
        
        text.append(f"Primary Species: ", style="white")
        text.append(f"{local_species}\n", style="bright_cyan")
        text.append(f"Culture: ", style="white")
        cultures = ["Mercantile", "Militaristic", "Scientific", "Spiritual", "Agrarian"]
        text.append(f"{random.choice(cultures)}\n", style="yellow")
        text.append(f"Attitude: ", style="white")
        attitudes = ["Welcoming", "Neutral", "Cautious", "Suspicious"]
        attitude = random.choice(attitudes)
        attitude_color = {"Welcoming": "green", "Neutral": "white", "Cautious": "yellow", "Suspicious": "red"}
        text.append(f"{attitude}\n", style=attitude_color.get(attitude, "white"))
        text.append("\n")
        
        # Available actions
        text.append("━" * 80 + "\n", style="green")
        text.append("AVAILABLE INTERACTIONS:\n", style="bold bright_green")
        text.append("━" * 80 + "\n", style="green")
        
        text.append("[", style="white")
        text.append("1", style="bold yellow")
        text.append("] ", style="white")
        text.append("Trade with Locals", style="bright_white")
        text.append(" - Exchange goods and information\n", style="dim white")
        
        text.append("[", style="white")
        text.append("2", style="bold yellow")
        text.append("] ", style="white")
        text.append("Recruit Crew/Specialists", style="bright_white")
        text.append(" - Hire local talent for your ship\n", style="dim white")
        
        text.append("[", style="white")
        text.append("3", style="bold yellow")
        text.append("] ", style="white")
        text.append("Diplomatic Mission", style="bright_white")
        text.append(" - Establish relations and alliances\n", style="dim white")
        
        text.append("\n")
        text.append("[", style="white")
        text.append("q/ESC", style="bold cyan")
        text.append("] Return to orbit\n", style="white")
        
        self.query_one("#colony_display", Static).update(text)
    
    def action_pop_screen(self):
        self.app.pop_screen()
    
    def action_1(self):
        self.query_one(MessageLog).add_message("Opening local trade markets...", "cyan")
        # Could open a special trading screen with local goods
        self.query_one(MessageLog).add_message("Local trade interface coming soon!", "yellow")
    
    def action_2(self):
        self.query_one(MessageLog).add_message("Accessing recruitment office...", "cyan")
        self.query_one(MessageLog).add_message("Crew recruitment coming soon!", "yellow")
    
    def action_3(self):
        self.query_one(MessageLog).add_message("Initiating diplomatic protocols...", "cyan")
        self.query_one(MessageLog).add_message("Diplomacy system coming soon!", "yellow")


class MiningScreen(Screen):
    """Screen for mining asteroids"""
    
    BINDINGS = [
        Binding("escape,q", "pop_screen", "Back", show=True),
        Binding("space", "mine_cycle", "Mine", show=True),
    ]
    
    def __init__(self, game, system, asteroid_belt):
        super().__init__()
        self.game = game
        self.system = system
        self.asteroid_belt = asteroid_belt
        self.mining_progress = 0
        self.resources_collected = {}
    
    def compose(self) -> ComposeResult:
        yield Static(id="mining_display")
        yield MessageLog()
    
    def on_mount(self):
        self.render_mining()
        self.query_one(MessageLog).add_message("Mining operations initialized", "green")
    
    def render_mining(self):
        text = Text()
        
        # Header
        text.append("═" * 80 + "\n", style="bold yellow")
        text.append(f"MINING OPERATIONS - {self.system['name']}".center(80) + "\n", style="bold yellow")
        text.append("═" * 80 + "\n", style="bold yellow")
        text.append("\n")
        
        # Asteroid belt info
        text.append(f"Target: ", style="white")
        text.append(f"{self.asteroid_belt.get('name', 'Asteroid Belt')}\n", style="bright_yellow")
        text.append(f"Density: ", style="white")
        density = self.asteroid_belt.get('density', 'Moderate')
        density_color = {"Sparse": "yellow", "Moderate": "white", "Dense": "green"}
        text.append(f"{density}\n", style=density_color.get(density, "white"))
        text.append(f"Mineral Content: ", style="white")
        if self.asteroid_belt.get('mineral_rich'):
            text.append("Rich\n", style="bright_green")
        else:
            text.append("Standard\n", style="white")
        text.append("\n")
        
        # Mining progress
        text.append("━" * 80 + "\n", style="cyan")
        text.append("MINING PROGRESS:\n", style="bold bright_cyan")
        text.append("━" * 80 + "\n", style="cyan")
        
        progress_bar_width = 40
        filled = int(self.mining_progress / 100 * progress_bar_width)
        bar = "[" + ("█" * filled) + ("·" * (progress_bar_width - filled)) + "]"
        text.append(f"Progress: {bar} {self.mining_progress}%\n", style="cyan")
        text.append("\n")
        
        # Resources collected
        if self.resources_collected:
            text.append("Resources Collected:\n", style="bold green")
            for resource, amount in self.resources_collected.items():
                text.append(f"  • {resource}: ", style="white")
                text.append(f"{amount} units\n", style="green")
            text.append("\n")
        
        # Ship cargo status
        nav = getattr(self.game, 'navigation', None)
        ship = nav.current_ship if nav else None
        if ship:
            cargo_used = sum(ship.cargo.values()) if ship.cargo else 0
            text.append(f"Cargo Hold: ", style="white")
            cargo_pct = cargo_used / ship.max_cargo if ship.max_cargo > 0 else 0
            cargo_color = "green" if cargo_pct < 0.7 else "yellow" if cargo_pct < 0.9 else "red"
            text.append(f"{cargo_used}/{ship.max_cargo} ", style=cargo_color)
            text.append(f"({cargo_pct*100:.0f}% full)\n", style=cargo_color)
            text.append("\n")
        
        # Instructions
        text.append("[", style="white")
        text.append("SPACE", style="bold yellow")
        text.append("] Mine (hold to continue)  [", style="white")
        text.append("q/ESC", style="bold cyan")
        text.append("] Finish mining and return\n", style="white")
        
        self.query_one("#mining_display", Static).update(text)
    
    def action_pop_screen(self):
        self.app.pop_screen()
    
    def action_mine_cycle(self):
        """Perform one mining cycle"""
        import random
        
        # Check cargo space
        nav = getattr(self.game, 'navigation', None)
        ship = nav.current_ship if nav else None
        if ship:
            cargo_used = sum(ship.cargo.values()) if ship.cargo else 0
            if cargo_used >= ship.max_cargo:
                self.query_one(MessageLog).add_message("Cargo hold full! Return to station.", "red")
                return
        
        # Mine resources
        self.mining_progress = min(100, self.mining_progress + random.randint(5, 15))
        
        # Determine what was found
        possible_resources = [
            "Zerite Crystals", "Crythium Ore", "Phasemetal", "Quantum Sand",
            "Gravite", "Nullstone", "Carboxite Slabs", "Living Ore"
        ]
        
        if random.random() < 0.7:  # 70% chance to find something
            resource = random.choice(possible_resources)
            amount = random.randint(1, 5)
            
            # Bonus for mineral-rich belts
            if self.asteroid_belt.get('mineral_rich'):
                amount *= 2
            
            self.resources_collected[resource] = self.resources_collected.get(resource, 0) + amount
            
            # Add to ship cargo
            if ship and hasattr(ship, 'cargo'):
                ship.cargo[resource] = ship.cargo.get(resource, 0) + amount
            
            # Also add to game inventory
            self.game.inventory[resource] = self.game.inventory.get(resource, 0) + amount
            
            self.query_one(MessageLog).add_message(f"Extracted {amount} units of {resource}!", "green")
        else:
            self.query_one(MessageLog).add_message("Mining... no valuable ore in this batch", "dim white")
        
        self.render_mining()


def main():
    """Run the NetHack-style interface"""
    app = NetHackInterface()
    app.run()


if __name__ == "__main__":
    main()
