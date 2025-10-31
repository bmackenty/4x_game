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
        lines.append("[i: Inventory] [m: Map] [t: Trade] [r: Research] [s: Status] [q: Menu]")
        
        self.query_one("#main_area", Static).update("\n".join(lines))
        
    def action_inventory(self):
        """Show inventory screen"""
        self.query_one(MessageLog).add_message("Opening inventory...")
        self.app.push_screen(InventoryScreen(self.game))
        
    def action_map(self):
        """Show map screen"""
        self.query_one(MessageLog).add_message("Opening galactic map...")
        self.app.push_screen(MapScreen(self.game))
        
    def action_trade(self):
        """Show trade screen"""
        self.query_one(MessageLog).add_message("Opening trade interface...")
        self.app.push_screen(TradingScreen(self.game))
        
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
        # Fixed map render size
        self.map_width = 80
        self.map_height = 22
    
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
        self.query_one(MessageLog).add_message("Map displayed. '@' = your ship, '*' = visited, '+' = unvisited")
    
    def update_map(self):
        nav = getattr(self.game, 'navigation', None)
        if not nav or not nav.galaxy:
            self.query_one("#map_display", Static).update("Galaxy data unavailable")
            return
        galaxy = nav.galaxy
        ship = nav.current_ship
        # Initialize buffer
        buf = [[" "] * self.map_width for _ in range(self.map_height)]
        
        def project(x, y):
            # Scale 0..size to 0..width-1
            px = int((x / galaxy.size_x) * (self.map_width - 1))
            py = int((y / galaxy.size_y) * (self.map_height - 1))
            # Clamp
            px = max(0, min(self.map_width - 1, px))
            py = max(0, min(self.map_height - 1, py))
            return px, py
        
        # Plot systems
        for sys in galaxy.systems.values():
            x, y, _ = sys["coordinates"]
            px, py = project(x, y)
            ch = "*" if sys.get("visited") else "+"
            buf[py][px] = ch
        
        # Plot ship last
        if ship:
            sx, sy, _ = ship.coordinates
            px, py = project(sx, sy)
            buf[py][px] = "@"
        
        # Build legend and info
        lines = []
        lines.append("═" * self.map_width)
        lines.append("GALAXY MAP".center(self.map_width))
        lines.append("═" * self.map_width)
        
        # Render map area
        for row in buf:
            lines.append("".join(row))
        
        # HUD
        lines.append("─" * self.map_width)
        if ship:
            sx, sy, sz = ship.coordinates
            lines.append(f"Ship: {ship.name} ({ship.ship_class})  Pos: ({sx},{sy},{sz})  Fuel: {ship.fuel}/{ship.max_fuel}  Range: {ship.jump_range}")
        visited_count = sum(1 for s in galaxy.systems.values() if s.get("visited"))
        lines.append(f"Systems: {len(galaxy.systems)} | Visited: {visited_count}")
        lines.append("[q/ESC: Back]")
        
        self.query_one("#map_display", Static).update("\n".join(lines))
    
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

        # Choose movement step to make each keypress visible on the map
        step_x = max(1, round(galaxy.size_x / self.map_width))
        step_y = max(1, round(galaxy.size_y / self.map_height))

        # Move within galaxy bounds
        x, y, z = ship.coordinates
        x = max(0, min(galaxy.size_x, x + dx * step_x))
        y = max(0, min(galaxy.size_y, y + dy * step_y))
        ship.coordinates = (x, y, z)

        # After moving, check if we're on the same displayed cell as any star system
        def project(px, py):
            sx = int((px / galaxy.size_x) * (self.map_width - 1))
            sy = int((py / galaxy.size_y) * (self.map_height - 1))
            sx = max(0, min(self.map_width - 1, sx))
            sy = max(0, min(self.map_height - 1, sy))
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
            # Open interaction screen for trading/repairs/combat
            self.query_one(MessageLog).add_message(f"Arrived at {entered_system['name']}")
            self.app.push_screen(SystemInteractionScreen(self.game, entered_system))


class SystemInteractionScreen(Screen):
    """Interaction screen when entering a star system: trade/repair/refuel/etc."""

    BINDINGS = [
        Binding("escape,q", "pop_screen", "Back", show=True),
        Binding("r", "refuel", "Refuel", show=True),
        Binding("t", "trade", "Trade", show=True),
        Binding("f", "fight", "Fight", show=True),
        Binding("k", "repair", "Repair", show=True),
    ]

    def __init__(self, game, system):
        super().__init__()
        self.game = game
        self.system = system

    def compose(self) -> ComposeResult:
        yield Static(id="system_display")
        yield MessageLog()

    def on_mount(self):
        self.render_system()
        self.query_one(MessageLog).add_message("[r]efuel  [t]rade  [k]repair  [f]ight  [q] back")

    def render_system(self):
        lines = []
        lines.append("═" * 80)
        lines.append(f"{self.system['name']}".center(80))
        lines.append("═" * 80)
        lines.append("")
        lines.append(f"Type: {self.system.get('type','Unknown')}")
        lines.append(f"Population: {self.system.get('population',0):,}")
        lines.append(f"Resources: {self.system.get('resources','Unknown')}")
        lines.append(f"Threat: {self.system.get('threat_level',0)}/10")
        lines.append("")
        if self.system.get('description'):
            lines.append(self.system['description'])
            lines.append("")
        # Show station/bot/faction flags if available
        try:
            coords = self.system['coordinates']
            # Station
            station = None
            if hasattr(self.game, 'station_manager') and self.game.station_manager:
                station = self.game.station_manager.get_station_at_location(coords)
            if station:
                owner_status = "YOUR STATION" if station['owner'] == "Player" else "Available for Purchase"
                lines.append(f"Station: {station['name']} ({station['type']}) - {owner_status}")
            # Faction
            if hasattr(self.game, 'faction_system') and self.game.faction_system:
                fac = self.game.faction_system.get_system_faction(coords)
                if fac:
                    rep = self.game.faction_system.get_reputation_status(fac)
                    lines.append(f"Control: {fac} | Your Standing: {rep}")
        except Exception:
            pass

        lines.append("")
        # Ship status
        nav = getattr(self.game, 'navigation', None)
        ship = nav.current_ship if nav else None
        if ship:
            sx, sy, sz = ship.coordinates
            lines.append(f"Ship: {ship.name}  Fuel: {ship.fuel}/{ship.max_fuel}  Cargo: {sum(ship.cargo.values()) if ship.cargo else 0}/{ship.max_cargo}")
        lines.append("")
        lines.append("[r] Refuel (10 cr per fuel)  [t] Trade  [k] Repair  [f] Fight  [q/ESC] Back")
        self.query_one("#system_display", Static).update("\n".join(lines))

    def action_pop_screen(self):
        self.app.pop_screen()

    def action_refuel(self):
        """Refuel current ship if at a system and with enough credits"""
        nav = getattr(self.game, 'navigation', None)
        ship = nav.current_ship if nav else None
        if not ship:
            self.query_one(MessageLog).add_message("No ship to refuel.")
            return
        fuel_needed = ship.max_fuel - ship.fuel
        if fuel_needed <= 0:
            self.query_one(MessageLog).add_message("Ship already fully fueled.")
            return
        cost = fuel_needed * 10
        if cost > self.game.credits:
            self.query_one(MessageLog).add_message(f"Insufficient credits ({cost} needed).")
            return
        self.game.credits -= cost
        ship.fuel = ship.max_fuel
        self.query_one(MessageLog).add_message(f"Refueled for {cost} credits.")
        self.render_system()

    def action_trade(self):
        """Open trading interface"""
        self.app.push_screen(TradingScreen(self.game))

    def action_fight(self):
        # Placeholder for combat
        self.query_one(MessageLog).add_message("Combat not implemented yet.")

    def action_repair(self):
        # Placeholder for repairs
        self.query_one(MessageLog).add_message("Repairs not implemented yet.")


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

    def compose(self) -> ComposeResult:
        yield Static(id="trade_display")
        yield MessageLog()

    def on_mount(self):
        self.system_name = self._get_system_name()
        if not self.system_name:
            self.query_one("#trade_display", Static).update("Not at a star system. Navigate to a system to trade.")
            self.query_one(MessageLog).add_message("No market here.")
            return
        self.refresh_lists()
        self.update_display()
        self.query_one(MessageLog).add_message(f"Trading at {self.system_name}. Tab toggles Buy/Sell.")

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
        """Display buy or sell list"""
        # List items
        items = self.buy_items if self.mode == "buy" else self.sell_items
        if not items:
            if self.mode == "buy":
                lines.append("No commodities available to buy here.")
            else:
                lines.append("No sellable inventory here (or no market demand).")
        else:
            header = ("#  Commodity                     Price        Avail/Demand")
            lines.append(header)
            lines.append("-" * len(header))
            for i, entry in enumerate(items, 1):
                cursor = ">" if (i - 1) == self.selected_index else " "
                if self.mode == "buy":
                    name, price, supply = entry
                    lines.append(f" {cursor} {i:2d}. {name:<28} {price:>8,} cr     {supply:>6}")
                else:
                    name, owned, price, demand = entry
                    lines.append(f" {cursor} {i:2d}. {name:<28} {price:>8,} cr     {owned:>3}/{demand:<3}")

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
        self.refresh_lists()
        self.update_display()

    def action_toggle_analysis(self):
        if self.mode == "analysis":
            self.mode = "buy"
        else:
            self.mode = "analysis"
        self.update_display()

    def action_show_opportunities(self):
        if self.mode == "opportunities":
            self.mode = "buy"
        else:
            self.mode = "opportunities"
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


def main():
    """Run the NetHack-style interface"""
    app = NetHackInterface()
    app.run()


if __name__ == "__main__":
    main()
