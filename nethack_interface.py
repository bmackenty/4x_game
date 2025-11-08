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
import math
import textwrap

# Import game modules
try:
    from game import Game
    from characters import character_classes, create_character_stats, calculate_derived_attributes, DERIVED_METRIC_INFO
    from backgrounds import backgrounds as background_data, get_background_list, apply_background_bonuses
    from species import species_database, get_playable_species
    from factions import factions
    from research import research_categories
    from navigation import Ship
    from galactic_history import generate_epoch_history
    GAME_AVAILABLE = True
except ImportError:
    GAME_AVAILABLE = False
    character_classes = {}
    background_data = {}
    get_background_list = lambda: []
    apply_background_bonuses = lambda stats, bg: stats
    species_database = {}
    factions = {}
    research_categories = {}
    generate_epoch_history = None


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


class GalacticHistoryScreen(Screen):
    """Display the galactic history - epochs, civilizations, cataclysms"""
    
    BINDINGS = [
        Binding("escape,q", "pop_screen", "Back", show=True),
        Binding("j,down", "scroll_down", "Scroll Down", show=True),
        Binding("k,up", "scroll_up", "Scroll Up", show=True),
    ]
    
    def __init__(self):
        super().__init__()
        self.history_scroll_offset = 0
        self.history_data = None
        self.history_lines = []  # Cache the built history lines
        
    def compose(self) -> ComposeResult:
        yield Static(id="history_display")
        yield MessageLog()
        
    def on_mount(self):
        """Generate and display galactic history"""
        # Generate history if available
        if generate_epoch_history:
            self.history_data = generate_epoch_history()
        else:
            # Fallback demo history when galactic_history module isn't available
            self.history_data = self._generate_demo_history()
        
        # Build history lines once
        self._build_history_lines()
        
        self.update_display()
        msg_log = self.query_one(MessageLog)
        msg_log.add_message("Galactic History - Use j/k or arrows to scroll, q to return", "cyan")
    
    def _build_history_lines(self):
        """Build the complete history lines list once"""
        self.history_lines = []
        
        if not self.history_data:
            return
        
        for epoch in self.history_data:
            # Epoch header
            self.history_lines.append(("═" * 120, "bold bright_cyan"))
            self.history_lines.append((f"{epoch['name']}", "bold bright_yellow"))
            self.history_lines.append((f"Years {epoch['start_year']:,} – {epoch['end_year']:,} (Duration: {epoch['end_year'] - epoch['start_year']:,} years)", "bright_white"))
            self.history_lines.append(("─" * 120, "dim white"))
            self.history_lines.append((f"Themes: {', '.join(epoch['themes'])}", "cyan"))
            self.history_lines.append(("", "white"))
            
            # Cataclysms
            if epoch.get('cataclysms'):
                self.history_lines.append(("⚠ Major Cataclysms:", "bold red"))
                for cataclysm in epoch['cataclysms']:
                    self.history_lines.append((f"  • {cataclysm}", "bright_red"))
                self.history_lines.append(("", "white"))
            
            # Faction Formations
            if epoch.get('faction_formations'):
                self.history_lines.append(("🏛️  Faction Formations:", "bold bright_green"))
                for faction in epoch['faction_formations']:
                    self.history_lines.append((f"  • Year {faction['year']:,}: {faction['event']}", "bright_white"))
                self.history_lines.append(("", "white"))
            
            # Mysteries
            if epoch.get('mysteries'):
                self.history_lines.append(("✦ Mysteries of This Age:", "bold magenta"))
                for mystery in epoch['mysteries']:
                    self.history_lines.append((f"  • {mystery}", "bright_magenta"))
                self.history_lines.append(("", "white"))
            
            # Civilizations
            self.history_lines.append(("Civilizations of This Epoch:", "bold green"))
            self.history_lines.append(("", "white"))
            
            for civ in epoch['civilizations']:
                self.history_lines.append((f"┌─ {civ['name']}", "bold bright_white"))
                self.history_lines.append((f"│  Species: {civ['species']}", "white"))
                self.history_lines.append((f"│  Traits: {', '.join(civ['traits'])}", "dim cyan"))
                self.history_lines.append((f"│  Founded: Year {civ['founded']:,} | Collapsed: Year {civ['collapsed']:,}", "yellow"))
                self.history_lines.append((f"│  Duration: {civ['collapsed'] - civ['founded']:,} years", "dim yellow"))
                self.history_lines.append((f"│", "white"))
                self.history_lines.append((f"│  Remnants:", "bright_blue"))
                self.history_lines.append((f"│    {civ['remnants']}", "dim blue"))
                
                if civ.get('notable_events'):
                    self.history_lines.append((f"│", "white"))
                    self.history_lines.append((f"│  Notable Events:", "bright_green"))
                    for event in civ['notable_events']:
                        year = event.get('year', '?')
                        desc = event.get('description', str(event))
                        self.history_lines.append((f"│    • Year {year}: {desc}", "dim green"))
                
                self.history_lines.append((f"└{'─' * 118}", "dim white"))
                self.history_lines.append(("", "white"))
            
            self.history_lines.append(("", "white"))
    
    def _generate_demo_history(self):
        """Generate simple demo history when galactic_history module is unavailable"""
        return [
            {
                "name": "The Dawn of Echoes",
                "start_year": 0,
                "end_year": 3000,
                "themes": ["emergence", "first contact"],
                "cataclysms": ["Etheric Resonance Collapse"],
                "mysteries": ["The Great Silence returns for 73 years"],
                "civilizations": [
                    {
                        "name": "Aethori Bio-Architects",
                        "type": "Bio-Architects",
                        "traits": ["organic cities", "living ships", "gene-forged citizens"],
                        "founded": 200,
                        "collapsed": 2800,
                        "remnants": "Overgrown megastructures pulsate faintly, still alive after millennia.",
                        "notable_events": [
                            "The Aethori Bio-Architects encountered a planet disappears and reappears inverted."
                        ]
                    }
                ]
            },
            {
                "name": "The Age of Expansion",
                "start_year": 3000,
                "end_year": 10000,
                "themes": ["colonization", "conflict"],
                "cataclysms": ["AI Schism of the Ascendant Mind", "Stellar Network Implosion"],
                "mysteries": [],
                "civilizations": [
                    {
                        "name": "Voryx Quantum Dynasties",
                        "type": "Quantum Dynasties",
                        "traits": ["temporal control", "superposition rulers", "probability warfare"],
                        "founded": 3500,
                        "collapsed": 9500,
                        "remnants": "Temporal scars linger, with entire regions flickering between timelines.",
                        "notable_events": [
                            "The Voryx Quantum Dynasties encountered a ship exits FTL before it departs."
                        ]
                    }
                ]
            }
        ]
        
    def update_display(self):
        """Render the galactic history"""
        text = Text()
        
        # Header
        text.append("═" * 120 + "\n", style="bold cyan")
        text.append("GALACTIC HISTORY".center(120) + "\n", style="bold yellow")
        text.append("The Ages of the Known Galaxy".center(120) + "\n", style="dim white")
        text.append("═" * 120 + "\n", style="bold cyan")
        text.append("\n")
        
        if not self.history_lines:
            text.append("History data unavailable.\n", style="red")
            text.append("\n")
            text.append("Press 'q' to return\n", style="dim white")
            self.query_one("#history_display", Static).update(text)
            return
        
        # Apply scroll offset and render visible lines
        visible_height = 35  # Number of lines visible
        start_line = self.history_scroll_offset
        end_line = start_line + visible_height
        
        visible_lines = self.history_lines[start_line:end_line]
        
        for line_text, line_style in visible_lines:
            text.append(line_text + "\n", style=line_style)
        
        # Scroll indicator
        text.append("\n")
        text.append("─" * 120 + "\n", style="bold white")
        total_lines = len(self.history_lines)
        scroll_pct = (self.history_scroll_offset / max(1, total_lines - visible_height)) * 100 if total_lines > visible_height else 100
        text.append(f"Scroll: {scroll_pct:.0f}% | Line {start_line + 1}/{total_lines} | [j/k or ↑/↓: scroll] [q: back]\n", style="dim white")
        
        self.query_one("#history_display", Static).update(text)
    
    def action_scroll_down(self):
        """Scroll down through history"""
        visible_height = 35
        total_lines = len(self.history_lines)
        max_scroll = max(0, total_lines - visible_height)
        
        if self.history_scroll_offset < max_scroll:
            self.history_scroll_offset += 3
            self.update_display()
    
    def action_scroll_up(self):
        """Scroll up through history"""
        if self.history_scroll_offset > 0:
            self.history_scroll_offset = max(0, self.history_scroll_offset - 3)
            self.update_display()
    
    def action_pop_screen(self):
        """Return to previous screen"""
        self.app.pop_screen()


class CharacterCreationScreen(Screen):
    """NetHack-style character creation - single screen with keyboard selection"""
    
    BINDINGS = [
        Binding("ctrl+c", "app.quit", "Quit", show=False),
        Binding("enter", "confirm", "Confirm", show=True),
        Binding("h,H", "show_history", "History", show=True),
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
        self.background_list = get_background_list() if GAME_AVAILABLE else ["Orbital Foundling"]
        self.faction_list = list(factions.keys()) if GAME_AVAILABLE else ["Independent"]
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
            if not self.species_list or len(self.species_list) == 0:
                lines.append("SELECT YOUR SPECIES:")
                lines.append("")
                lines.append("  ERROR: No species available!")
                lines.append("  Please confirm species.py defines playable species.")
                lines.append("")
            else:
                if self.current_index >= len(self.species_list):
                    self.current_index = 0
                if self.current_index < 0:
                    self.current_index = 0
                
                lines.append("SELECT YOUR SPECIES:")
                lines.append("")
                
                visible_count = 10
                scroll_offset = max(0, self.current_index - visible_count + 3)
                visible_species = self.species_list[scroll_offset:scroll_offset + visible_count]
                
                if self.species_list and 0 <= self.current_index < len(self.species_list):
                    current_species_name = self.species_list[self.current_index]
                    current_species = species_database.get(current_species_name, {}) if GAME_AVAILABLE else {}
                else:
                    current_species_name = ""
                    current_species = {}
                
                def wrap_detail(prefix: str, text: str):
                    if not text:
                        return []
                    wrapped = [prefix]
                    words = text.split()
                    line = ""
                    for word in words:
                        if len(line) + len(word) + 1 <= 36:
                            line += (word + " ")
                        else:
                            wrapped.append(f"│   {line.strip()}")
                            line = word + " "
                    if line:
                        wrapped.append(f"│   {line.strip()}")
                    return wrapped
                
                detail_lines = []
                if GAME_AVAILABLE and current_species:
                    detail_lines.append("│ SPECIES DETAILS")
                    detail_lines.append("│ " + "─" * 38)
                    
                    desc = current_species.get("description", "")
                    if desc:
                        detail_lines.extend(wrap_detail("│ Description:", desc))
                        detail_lines.append("│")
                    
                    category = current_species.get("category")
                    if category:
                        detail_lines.append(f"│ Category: {category}")
                    homeworld = current_species.get("homeworld")
                    if homeworld:
                        detail_lines.append(f"│ Homeworld: {homeworld}")
                    alliance = current_species.get("alliance_status")
                    if alliance:
                        detail_lines.append(f"│ Alliance Status: {alliance}")
                    population = current_species.get("population")
                    if population:
                        detail_lines.append(f"│ Population: {population}")
                    if len(detail_lines) > 2:
                        detail_lines.append("│")
                    
                    biology = current_species.get("biology", "")
                    if biology:
                        detail_lines.extend(wrap_detail("│ Biology:", biology))
                        detail_lines.append("│")
                    
                    cognition = current_species.get("cognition", "")
                    if cognition:
                        detail_lines.extend(wrap_detail("│ Cognition:", cognition))
                        detail_lines.append("│")
                    
                    culture = current_species.get("culture", "")
                    if culture:
                        detail_lines.extend(wrap_detail("│ Culture:", culture))
                        detail_lines.append("│")
                    
                    technology = current_species.get("technology", "")
                    if technology:
                        detail_lines.extend(wrap_detail("│ Technology:", technology))
                        detail_lines.append("│")
                    
                    traits = current_species.get("special_traits", [])
                    if traits:
                        detail_lines.append("│ Special Traits:")
                        for trait in traits:
                            detail_lines.append(f"│   - {trait}")
                        detail_lines.append("│")
                    
                    starting_bonuses = current_species.get("starting_bonuses", {})
                    if starting_bonuses:
                        detail_lines.append("│ Starting Bonuses:")
                        for bonus_name, bonus_value in starting_bonuses.items():
                            detail_lines.append(f"│   {bonus_name.replace('_', ' ').title()}: {bonus_value}")
                else:
                    detail_lines.append("│ SPECIES DETAILS")
                    detail_lines.append("│ " + "─" * 38)
                    detail_lines.append("│")
                    detail_lines.append("│ No additional information available.")
                
                for i, species in enumerate(visible_species):
                    actual_index = i + scroll_offset
                    cursor = ">" if actual_index == self.current_index else " "
                    letter = chr(97 + actual_index) if actual_index < 26 else " "
                    left_text = f"  {cursor} {letter}) {species}"[:38].ljust(38)
                    right_text = detail_lines[i] if i < len(detail_lines) else "│"
                    lines.append(left_text + "  " + right_text)
                
                if detail_lines and len(detail_lines) > len(visible_species):
                    for detail_line in detail_lines[len(visible_species):]:
                        left_text = " " * 38
                        lines.append(left_text + "  " + detail_line)
                
                if len(self.species_list) > visible_count:
                    lines.append("")
                    scroll_info = f"  [{self.current_index + 1}/{len(self.species_list)}] (Use j/k to scroll)"
                    lines.append(scroll_info)
                    
        elif self.stage == "background":
            # Ensure background list is populated
            if not self.background_list or len(self.background_list) == 0:
                try:
                    if GAME_AVAILABLE:
                        self.background_list = get_background_list()
                    else:
                        self.background_list = ["Orbital Foundling"]
                except Exception as e:
                    lines.append(f"ERROR loading backgrounds: {e}")
                    self.background_list = ["Orbital Foundling"]
            
            # Show error if still empty
            if not self.background_list or len(self.background_list) == 0:
                lines.append("SELECT YOUR BACKGROUND:")
                lines.append("")
                lines.append("  ERROR: No backgrounds available!")
                lines.append("  Please check that backgrounds.py exists and is valid.")
                lines.append("")
            else:
                # Ensure current_index is valid
                if self.current_index >= len(self.background_list):
                    self.current_index = 0
                if self.current_index < 0:
                    self.current_index = 0
                
                lines.append("SELECT YOUR BACKGROUND:")
                lines.append("")
                
                # Calculate scrolling window (show 10 items at a time for backgrounds)
                visible_count = 10
                scroll_offset = max(0, self.current_index - visible_count + 3)
                visible_backgrounds = self.background_list[scroll_offset:scroll_offset + visible_count] if self.background_list else []
                
                # Get current background details
                if self.background_list and len(self.background_list) > 0 and 0 <= self.current_index < len(self.background_list):
                    current_bg_name = self.background_list[self.current_index]
                    current_bg = background_data.get(current_bg_name, {}) if GAME_AVAILABLE else {}
                else:
                    current_bg_name = ""
                    current_bg = {}
            
                # Build the detail lines for the right panel
                detail_lines = []
                if GAME_AVAILABLE and current_bg:
                    detail_lines.append(f"│ BACKGROUND DETAILS")
                    detail_lines.append(f"│ " + "─" * 38)
                    
                    # Description
                    desc = current_bg.get('description', '')
                    if desc:
                        detail_lines.append(f"│ Description:")
                        words = desc.split()
                        line = ""
                        for word in words:
                            if len(line) + len(word) + 1 <= 36:
                                line += (word + " ")
                            else:
                                detail_lines.append(f"│   {line.strip()}")
                                line = word + " "
                        if line:
                            detail_lines.append(f"│   {line.strip()}")
                        detail_lines.append(f"│")
                    
                    # Stat Bonuses
                    bonuses = current_bg.get('stat_bonuses', {})
                    if bonuses:
                        detail_lines.append(f"│ Stat Bonuses:")
                        for stat, bonus in bonuses.items():
                            detail_lines.append(f"│   +{bonus} {stat}")
                        detail_lines.append(f"│")
                    
                    # Talent
                    talent = current_bg.get('talent', '')
                    if talent:
                        detail_lines.append(f"│ Talent:")
                        words = talent.split()
                        line = ""
                        for word in words:
                            if len(line) + len(word) + 1 <= 36:
                                line += (word + " ")
                            else:
                                detail_lines.append(f"│   {line.strip()}")
                                line = word + " "
                        if line:
                            detail_lines.append(f"│   {line.strip()}")
                
                # Build left column (background list) and combine with right column
                # Show backgrounds on left, details for selected on right (similar to faction display)
                for i, bg in enumerate(visible_backgrounds):
                    actual_index = i + scroll_offset
                    cursor = ">" if actual_index == self.current_index else " "
                    
                    # Left side: background name (40 chars wide)
                    left_text = f"  {cursor} {bg}"[:38].ljust(38)
                    
                    # Right side: show detail lines top-aligned (like faction panel)
                    if i < len(detail_lines):
                        right_text = detail_lines[i]
                    else:
                        right_text = "│"
                    
                    lines.append(left_text + "  " + right_text)
                
                # After the list, show remaining details for the selected background
                if detail_lines and len(detail_lines) > len(visible_backgrounds):
                    # Add remaining detail lines below the list
                    for detail_line in detail_lines[len(visible_backgrounds):]:
                        left_text = " " * 38
                        lines.append(left_text + "  " + detail_line)
                
                # Show scroll indicator if needed
                if self.background_list and len(self.background_list) > visible_count:
                    lines.append("")
                    scroll_info = f"  [{self.current_index + 1}/{len(self.background_list)}] (Use j/k to scroll)"
                    lines.append(scroll_info)
                    
        elif self.stage == "faction":
            # Two-column layout: faction list on left, details on right
            lines.append("SELECT YOUR FACTION:")
            lines.append("")
            
            # Calculate scrolling window (show 20 items at a time)
            visible_count = 20
            scroll_offset = max(0, self.current_index - visible_count + 5)  # Keep selection near middle
            visible_factions = self.faction_list[scroll_offset:scroll_offset + visible_count]
            
            # Get current faction details
            current_faction_name = self.faction_list[self.current_index]
            current_faction = factions.get(current_faction_name, {}) if GAME_AVAILABLE else {}
            
            # Build the detail lines for the right panel
            detail_lines = []
            if GAME_AVAILABLE and current_faction:
                detail_lines.append(f"│ FACTION DETAILS")
                detail_lines.append(f"│ " + "─" * 38)
                detail_lines.append(f"│ Philosophy: {current_faction.get('philosophy', 'Unknown')}")
                detail_lines.append(f"│ Focus: {current_faction.get('primary_focus', 'Unknown')}")
                detail_lines.append(f"│ Government: {current_faction.get('government_type', 'Unknown')}")
                detail_lines.append(f"│")
                
                # Description (word wrap)
                desc = current_faction.get('description', '')
                if desc:
                    detail_lines.append(f"│ Description:")
                    # Wrap description to 36 chars per line
                    words = desc.split()
                    line = ""
                    for word in words:
                        if len(line) + len(word) + 1 <= 36:
                            line += (word + " ")
                        else:
                            detail_lines.append(f"│   {line.strip()}")
                            line = word + " "
                    if line:
                        detail_lines.append(f"│   {line.strip()}")
                    detail_lines.append(f"│")
                
                # Origin story (word wrap)
                origin = current_faction.get('origin_story', '')
                if origin:
                    detail_lines.append(f"│ Origin:")
                    words = origin.split()
                    line = ""
                    for word in words:
                        if len(line) + len(word) + 1 <= 36:
                            line += (word + " ")
                        else:
                            detail_lines.append(f"│   {line.strip()}")
                            line = word + " "
                    if line:
                        detail_lines.append(f"│   {line.strip()}")
                    detail_lines.append(f"│")
                
                # Founding information
                epoch = current_faction.get('founding_epoch', 'Unknown')
                year = current_faction.get('founding_year', '?')
                detail_lines.append(f"│ Founded: {epoch}")
                detail_lines.append(f"│ Year: {year}")
            else:
                detail_lines.append("│")
            
            # Build left column (faction list) and combine with right column
            for i, faction in enumerate(visible_factions):
                actual_index = i + scroll_offset
                cursor = ">" if actual_index == self.current_index else " "
                
                # Left side: faction name (40 chars wide)
                left_text = f"  {cursor} {faction}"[:38].ljust(38)
                
                # Right side: get corresponding detail line
                if i < len(detail_lines):
                    right_text = detail_lines[i]
                else:
                    right_text = "│"
                
                lines.append(left_text + "  " + right_text)
            
            # Show scroll indicator if needed
            if len(self.faction_list) > visible_count:
                lines.append("")
                scroll_info = f"  [{self.current_index + 1}/{len(self.faction_list)}] (Use j/k to scroll)"
                lines.append(scroll_info)
                    
        elif self.stage == "class":
            if not self.class_list or len(self.class_list) == 0:
                lines.append("SELECT YOUR CLASS:")
                lines.append("")
                lines.append("  ERROR: No classes available!")
                lines.append("  Please check that characters.py defines character classes.")
                lines.append("")
            else:
                if self.current_index >= len(self.class_list):
                    self.current_index = 0
                if self.current_index < 0:
                    self.current_index = 0
                
                lines.append("SELECT YOUR CLASS:")
                lines.append("")
                
                visible_count = 10
                scroll_offset = max(0, self.current_index - visible_count + 3)
                visible_classes = self.class_list[scroll_offset:scroll_offset + visible_count]
                
                if self.class_list and 0 <= self.current_index < len(self.class_list):
                    current_class_name = self.class_list[self.current_index]
                    current_class = character_classes.get(current_class_name, {}) if GAME_AVAILABLE else {}
                else:
                    current_class_name = ""
                    current_class = {}
                
                detail_lines = []
                if GAME_AVAILABLE and current_class:
                    detail_lines.append("│ CLASS DETAILS")
                    detail_lines.append("│ " + "─" * 38)
                    
                    desc = current_class.get('description', '')
                    if desc:
                        detail_lines.append("│ Description:")
                        words = desc.split()
                        line = ""
                        for word in words:
                            if len(line) + len(word) + 1 <= 36:
                                line += (word + " ")
                            else:
                                detail_lines.append(f"│   {line.strip()}")
                                line = word + " "
                        if line:
                            detail_lines.append(f"│   {line.strip()}")
                        detail_lines.append("│")
                    
                    credits = current_class.get('starting_credits')
                    if credits is not None:
                        detail_lines.append(f"│ Starting Credits: {credits}")
                    
                    for key, label in [
                        ("starting_ships", "Starting Ships"),
                        ("starting_stations", "Starting Stations"),
                        ("starting_platforms", "Starting Platforms"),
                    ]:
                        items = current_class.get(key, [])
                        if items:
                            detail_lines.append(f"│ {label}:")
                            for item in items:
                                detail_lines.append(f"│   - {item}")
                            detail_lines.append("│")
                    
                    bonuses = current_class.get('bonuses', {})
                    if bonuses:
                        detail_lines.append("│ Bonuses:")
                        for bonus_name, bonus_value in bonuses.items():
                            percent = round(bonus_value * 100)
                            detail_lines.append(f"│   {bonus_name.replace('_', ' ').title()}: +{percent}%")
                        detail_lines.append("│")
                    
                    skills = current_class.get('skills', [])
                    if skills:
                        detail_lines.append("│ Skills:")
                        for skill in skills:
                            detail_lines.append(f"│   - {skill}")
                else:
                    detail_lines.append("│ CLASS DETAILS")
                    detail_lines.append("│ " + "─" * 38)
                    detail_lines.append("│")
                    detail_lines.append("│ No additional information available.")
                
                for i, cls in enumerate(visible_classes):
                    actual_index = i + scroll_offset
                    cursor = ">" if actual_index == self.current_index else " "
                    left_text = f"  {cursor} {chr(97 + actual_index)}) {cls}"[:38].ljust(38)
                    if i < len(detail_lines):
                        right_text = detail_lines[i]
                    else:
                        right_text = "│"
                    lines.append(left_text + "  " + right_text)
                
                if detail_lines and len(detail_lines) > len(visible_classes):
                    for detail_line in detail_lines[len(visible_classes):]:
                        left_text = " " * 38
                        lines.append(left_text + "  " + detail_line)
                
                if len(self.class_list) > visible_count:
                    lines.append("")
                    scroll_info = f"  [{self.current_index + 1}/{len(self.class_list)}] (Use j/k to scroll)"
                    lines.append(scroll_info)
                    
        elif self.stage == "stats":
            from characters import STAT_NAMES, STAT_DESCRIPTIONS, BASE_STAT_VALUE, POINT_BUY_POINTS, MAX_STAT_VALUE, validate_stat_allocation
            lines.append("YOUR CHARACTER STATS (Point-Buy System):")
            lines.append("")
            lines.append(f"  All stats start at {BASE_STAT_VALUE}. You may spend up to {POINT_BUY_POINTS} points.")
            lines.append(f"  Maximum {MAX_STAT_VALUE} per stat. Leaving points unspent is allowed.")
            lines.append("")
            if self.character_data['stats']:
                stats = self.character_data['stats']
                # Calculate base total (accounting for background bonuses)
                base_total = BASE_STAT_VALUE * len(STAT_NAMES)
                
                # Show background bonuses if applicable
                if self.character_data.get('background'):
                    bg = background_data.get(self.character_data['background'], {}) if GAME_AVAILABLE else {}
                    if bg:
                        bonuses = bg.get('stat_bonuses', {})
                        if bonuses:
                            # Subtract background bonuses from total to get allocated points correctly
                            bg_bonus_total = sum(bonuses.values())
                            base_total += bg_bonus_total
                
                current_total = sum(stats.values())
                allocated_points = current_total - base_total
                remaining_points = POINT_BUY_POINTS - allocated_points
                
                lines.append(f"  Points Remaining: {remaining_points}/{POINT_BUY_POINTS}")
                if self.character_data.get('background'):
                    bg = background_data.get(self.character_data['background'], {}) if GAME_AVAILABLE else {}
                    if bg:
                        bonuses = bg.get('stat_bonuses', {})
                        if bonuses:
                            bonus_str = ", ".join([f"+{v} {k}" for k, v in bonuses.items()])
                            lines.append(f"  Background Bonuses: {bonus_str}")
                lines.append("")
                
                # Get selected stat index (default to 0 if not set)
                selected_index = getattr(self, '_selected_stat_index', 0)
                stat_codes = list(STAT_NAMES.keys())
                
                for i, stat_code in enumerate(stat_codes):
                    value = stats.get(stat_code, BASE_STAT_VALUE)
                    stat_name = STAT_NAMES[stat_code]
                    
                    # Show cursor indicator for selected stat
                    cursor = ">" if i == selected_index else " "
                    
                    # Show if this stat has a background bonus
                    bg_bonus = ""
                    if self.character_data.get('background'):
                        bg = background_data.get(self.character_data['background'], {}) if GAME_AVAILABLE else {}
                        if bg:
                            bonuses = bg.get('stat_bonuses', {})
                            if stat_code in bonuses:
                                bg_bonus = f" (+{bonuses[stat_code]})"
                    
                    # Highlight selected stat
                    if i == selected_index:
                        lines.append(f"  {cursor} [{stat_code}] {stat_name}: {value}/{MAX_STAT_VALUE}{bg_bonus} ← →")
                    else:
                        lines.append(f"  {cursor}  {stat_code}  {stat_name}: {value}/{MAX_STAT_VALUE}{bg_bonus}")
                
                lines.append("")
                derived = calculate_derived_attributes(stats)
                if derived:
                    lines.append("  Derived Metrics:")
                    for name, value in derived.items():
                        info = DERIVED_METRIC_INFO.get(name, {})
                        formula = info.get("formula")
                        description = info.get("description")
                        metric_line = f"    {name}: {value}"
                        if formula:
                            metric_line += f"  [{formula}]"
                        if description:
                            metric_line += f" - {description}"
                        lines.append(metric_line)
                    lines.append("")

                is_valid, msg = validate_stat_allocation(stats, self.character_data.get('background'))
                if is_valid:
                    lines.append(f"  ✓ {msg}")
                else:
                    lines.append(f"  ⚠ {msg}")
            else:
                lines.append("  Press 'r' to initialize stats (all start at 30)")
            lines.append("")
            lines.append("  Controls:")
            lines.append("    ↑/↓ - Navigate between stats")
            lines.append("    ←/→ - Decrease/Increase selected stat")
            lines.append("    r - Initialize/Reset stats")
            lines.append("    Enter - Accept and continue")
            
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
                from characters import STAT_NAMES
                lines.append("  Stats:")
                for stat_code in STAT_NAMES.keys():
                    value = self.character_data['stats'].get(stat_code, 30)
                    stat_name = STAT_NAMES[stat_code]
                    lines.append(f"    {stat_code} ({stat_name}): {value}/100")
            lines.append("")
            lines.append("  Press Enter to start game, 'b' to go back")
        
        lines.append("")
        lines.append("─" * 80)
        if self.stage == "name":
            lines.append(f"[Type to enter name] [Backspace: delete] [Enter: confirm]")
        elif self.stage == "faction":
            lines.append(f"[j/k or ↑/↓: scroll] [Enter: confirm] [H: history] [q: quit]")
        elif self.stage == "background":
            lines.append(f"[j/k or ↑/↓: scroll] [Enter: confirm] [H: history] [q: quit]")
        else:
            lines.append(f"[j/k or ↑/↓: navigate] [a-z: quick select] [Enter: confirm] [H: history] [q: quit]")
        
        try:
            display_text = "\n".join(lines)
            self.query_one("#main_display", Static).update(display_text)
        except Exception as e:
            # Fallback display if there's an error
            try:
                error_msg = f"Display Error: {e}\nCurrent Stage: {self.stage}\nBackground List Length: {len(self.background_list) if self.background_list else 0}"
                self.query_one("#main_display", Static).update(error_msg)
                if hasattr(self, 'query_one'):
                    try:
                        self.query_one(MessageLog).add_message(f"Display error: {e}")
                    except:
                        pass
            except:
                pass
        
    def on_key(self, event) -> None:
        """Handle keyboard input"""
        key = event.key
        # Also check event.character for special keys like + and -
        char = getattr(event, 'character', None)
        
        
        # Quit with 'q' (except when typing name)
        if key == "q" and self.stage != "name":
            self.app.exit()
            return
        
        # Handle stats stage with arrow key navigation
        if self.stage == "stats":
            from characters import STAT_NAMES
            stat_codes = list(STAT_NAMES.keys())
            
            # Initialize selected stat index if not set
            if not hasattr(self, '_selected_stat_index'):
                self._selected_stat_index = 0
            
            # Reset stats
            if key == "r" or char == "r":
                self.roll_stats()
                return
            
            # Navigate between stats (up/down arrows)
            elif key in ["up", "k"]:
                self._selected_stat_index = (self._selected_stat_index - 1) % len(stat_codes)
                stat_code = stat_codes[self._selected_stat_index]
                self.query_one(MessageLog).add_message(f"Selected {STAT_NAMES[stat_code]}")
                self.update_display()
                event.prevent_default()
                event.stop()
                return
            elif key in ["down", "j"]:
                self._selected_stat_index = (self._selected_stat_index + 1) % len(stat_codes)
                stat_code = stat_codes[self._selected_stat_index]
                self.query_one(MessageLog).add_message(f"Selected {STAT_NAMES[stat_code]}")
                self.update_display()
                event.prevent_default()
                event.stop()
                return
            
            # Adjust selected stat (left/right arrows)
            elif key in ["left", "h"]:
                # Decrease stat
                self._selected_stat_code = stat_codes[self._selected_stat_index]
                event.prevent_default()
                event.stop()
                self.adjust_stat(-1)
                return
            elif key in ["right", "l"]:
                # Increase stat
                self._selected_stat_code = stat_codes[self._selected_stat_index]
                event.prevent_default()
                event.stop()
                self.adjust_stat(+1)
                return
            
            # Accept stats and continue
            elif key == "enter":
                self.action_confirm()
                return
        
        # Navigation keys (vim-style and arrows) - only when not in stats stage
        # Background stage also uses j/k navigation
        if self.stage not in ["stats", "name"]:
            if key in ["j", "down"]:
                self.move_cursor(1)
                event.stop()
                return
            elif key in ["k", "up"]:
                self.move_cursor(-1)
                event.stop()
                return
        
        # Enter key handling (stats stage handled above with return)
        # Handle Enter key for all stages except stats (which is handled above)
        if key == "enter" and self.stage != "stats":
            # Call action_confirm which handles stage transitions
            self.action_confirm()
            # CRITICAL: Stop event propagation to prevent double-processing
            event.stop()
            event.prevent_default()
            return
        elif key == "b" and self.stage == "confirm":
            self.stage = "name"
            self.current_index = 0
            self.update_display()
        # Quick letter selection (skip for faction since there are too many)
        elif len(key) == 1 and key.isalpha() and self.stage not in ["name", "stats", "confirm", "faction"]:
            idx = ord(key.lower()) - ord('a')
            if 0 <= idx < len(self.get_current_list()):
                self.current_index = idx
                self.action_confirm()
        # Name entry
        elif self.stage == "name":
            if key == "backspace" and len(self.character_data['name']) > 0:
                self.character_data['name'] = self.character_data['name'][:-1]
                self.update_display()
                event.stop()
                event.prevent_default()
            elif len(key) == 1 and (key.isalnum() or key == " "):
                if len(self.character_data['name']) < 20:
                    self.character_data['name'] += key
                    self.update_display()
                event.stop()
                event.prevent_default()
            return
                    
    def move_cursor(self, delta: int):
        """Move selection cursor"""
        if self.stage in ["stats", "name", "confirm"]:
            return
        
        # Get the current list for this stage
        current_list = self.get_current_list()
        if not current_list or len(current_list) == 0:
            # If list is empty, try to populate it
            if self.stage == "background" and (not self.background_list or len(self.background_list) == 0):
                try:
                    if GAME_AVAILABLE:
                        self.background_list = get_background_list()
                        current_list = self.background_list
                except Exception:
                    pass
            if not current_list or len(current_list) == 0:
                return  # Can't navigate if no list
        
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
            # Ensure background list is populated
            if not self.background_list or len(self.background_list) == 0:
                try:
                    if GAME_AVAILABLE:
                        self.background_list = get_background_list()
                    else:
                        self.background_list = ["Orbital Foundling"]
                except Exception as e:
                    self.query_one(MessageLog).add_message(f"Error loading backgrounds: {e}")
                    self.background_list = ["Orbital Foundling"]
            
            # Verify background list is populated before moving to background stage
            if not self.background_list or len(self.background_list) == 0:
                self.query_one(MessageLog).add_message(f"ERROR: Cannot load backgrounds! Please check backgrounds.py")
                return  # Don't proceed if we can't load backgrounds
            
            self.stage = "background"
            self.current_index = 0
            self.query_one(MessageLog).add_message(f"Selected species: {self.character_data['species']}")
            self.query_one(MessageLog).add_message(f"Now select your background ({len(self.background_list)} available)")
            self.update_display()
            return
            
        elif self.stage == "background":
            # Ensure background list is populated and current_index is valid
            if not self.background_list or len(self.background_list) == 0:
                try:
                    if GAME_AVAILABLE:
                        self.background_list = get_background_list()
                    else:
                        self.background_list = ["Orbital Foundling"]
                except Exception as e:
                    self.query_one(MessageLog).add_message(f"Error loading backgrounds: {e}")
                    self.background_list = ["Orbital Foundling"]
            
            if self.current_index >= len(self.background_list):
                self.current_index = 0
            
            if len(self.background_list) == 0:
                self.query_one(MessageLog).add_message("ERROR: No backgrounds available!")
                return
            
            self.character_data['background'] = self.background_list[self.current_index]
            self.stage = "faction"
            self.current_index = 0
            bg_name = self.character_data['background']
            bg = background_data.get(bg_name, {}) if GAME_AVAILABLE else {}
            if bg:
                bonuses = bg.get('stat_bonuses', {})
                if bonuses:
                    bonus_str = ", ".join([f"+{v} {k}" for k, v in bonuses.items()])
                    self.query_one(MessageLog).add_message(f"Selected background: {bg_name} ({bonus_str})")
                else:
                    self.query_one(MessageLog).add_message(f"Selected background: {bg_name}")
            else:
                self.query_one(MessageLog).add_message(f"Selected background: {bg_name}")
            self.update_display()
            return
            
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
                # Validate stats before proceeding
                from characters import validate_stat_allocation
                is_valid, msg = validate_stat_allocation(self.character_data['stats'])
                if is_valid:
                    self.stage = "name"
                    self.query_one(MessageLog).add_message("Stats accepted. Enter your name.")
                else:
                    self.query_one(MessageLog).add_message(f"Cannot proceed: {msg}")
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
            return  # Don't update display after starting game
            
        # Only update display if we didn't return early
        self.update_display()
        
    def roll_stats(self):
        """Initialize character stats with base values and apply background bonuses"""
        if GAME_AVAILABLE:
            from characters import create_base_character_stats
            base_stats = create_base_character_stats()
            
            # Apply background bonuses if a background was selected
            if self.character_data.get('background'):
                self.character_data['stats'] = apply_background_bonuses(
                    base_stats, 
                    self.character_data['background']
                )
                bg_name = self.character_data['background']
                bg = background_data.get(bg_name, {})
                if bg:
                    bonuses = bg.get('stat_bonuses', {})
                    if bonuses:
                        bonus_str = ", ".join([f"+{v} {k}" for k, v in bonuses.items()])
                        self.query_one(MessageLog).add_message(f"Stats initialized with background bonuses: {bonus_str}")
                    else:
                        self.query_one(MessageLog).add_message("Stats initialized! Use ↑/↓ to navigate, ←/→ to adjust.")
                else:
                    self.query_one(MessageLog).add_message("Stats initialized! Use ↑/↓ to navigate, ←/→ to adjust.")
            else:
                self.character_data['stats'] = base_stats
                self.query_one(MessageLog).add_message("Stats initialized! Use ↑/↓ to navigate, ←/→ to adjust.")
        else:
            from characters import create_base_character_stats
            self.character_data['stats'] = create_base_character_stats()
            self.query_one(MessageLog).add_message("Stats initialized! Use ↑/↓ to navigate, ←/→ to adjust.")
        # Always set default selected stat index
        self._selected_stat_index = 0
        self.update_display()
    
    def adjust_stat(self, direction):
        """Adjust the currently selected stat"""
        from characters import STAT_NAMES, BASE_STAT_VALUE, POINT_BUY_POINTS, MAX_STAT_VALUE
        
        if not self.character_data.get('stats'):
            self.roll_stats()
            return
        
        # Ensure we have a selected stat index
        if not hasattr(self, '_selected_stat_index'):
            self._selected_stat_index = 0
        
        stat_codes = list(STAT_NAMES.keys())
        if self._selected_stat_index < 0 or self._selected_stat_index >= len(stat_codes):
            self._selected_stat_index = 0
        
        stats = self.character_data['stats']
        stat_code = stat_codes[self._selected_stat_index]
        
        # Update the selected stat code for display purposes
        self._selected_stat_code = stat_code
        
        if stat_code not in stats:
            # Invalid stat code, reset to first
            self._selected_stat_index = 0
            stat_code = stat_codes[0]
            self._selected_stat_code = stat_code
        
        current_value = stats[stat_code]
        
        # Calculate base total (accounting for background bonuses)
        base_total = BASE_STAT_VALUE * len(STAT_NAMES)
        if self.character_data.get('background'):
            bg = background_data.get(self.character_data['background'], {}) if GAME_AVAILABLE else {}
            if bg:
                bonuses = bg.get('stat_bonuses', {})
                if bonuses:
                    bg_bonus_total = sum(bonuses.values())
                    base_total += bg_bonus_total
        
        # Calculate minimum value for this stat (including background bonus)
        base_value_for_stat = BASE_STAT_VALUE
        if self.character_data.get('background'):
            bg = background_data.get(self.character_data['background'], {}) if GAME_AVAILABLE else {}
            if bg:
                bonuses = bg.get('stat_bonuses', {})
                if stat_code in bonuses:
                    base_value_for_stat += bonuses[stat_code]
        
        current_total = sum(stats.values())
        allocated_points = current_total - base_total
        remaining_points = POINT_BUY_POINTS - allocated_points
        
        if direction > 0:  # Increase
            if current_value < MAX_STAT_VALUE and remaining_points > 0:
                # Directly modify the dictionary to ensure the change is made
                self.character_data['stats'][stat_code] = current_value + 1
                new_value = self.character_data['stats'][stat_code]
                # Recalculate remaining points with background bonuses
                new_total = sum(self.character_data['stats'].values())
                new_allocated = new_total - base_total
                new_remaining = POINT_BUY_POINTS - new_allocated
                self.query_one(MessageLog).add_message(f"Increased {STAT_NAMES[stat_code]} to {new_value} (Remaining: {new_remaining})")
            else:
                if current_value >= MAX_STAT_VALUE:
                    self.query_one(MessageLog).add_message(f"{STAT_NAMES[stat_code]} is at maximum ({MAX_STAT_VALUE})")
                elif remaining_points <= 0:
                    self.query_one(MessageLog).add_message(f"No points remaining to allocate")
        elif direction < 0:  # Decrease
            if current_value > base_value_for_stat:
                # Directly modify the dictionary to ensure the change is made
                self.character_data['stats'][stat_code] = current_value - 1
                new_value = self.character_data['stats'][stat_code]
                # Recalculate remaining points
                new_base_total = BASE_STAT_VALUE * len(STAT_NAMES)
                if self.character_data.get('background'):
                    bg = background_data.get(self.character_data['background'], {}) if GAME_AVAILABLE else {}
                    if bg:
                        bonuses = bg.get('stat_bonuses', {})
                        if bonuses:
                            new_base_total += sum(bonuses.values())
                new_remaining = POINT_BUY_POINTS - (sum(self.character_data['stats'].values()) - new_base_total)
                self.query_one(MessageLog).add_message(f"Decreased {STAT_NAMES[stat_code]} to {new_value} (Remaining: {new_remaining})")
            else:
                self.query_one(MessageLog).add_message(f"{STAT_NAMES[stat_code]} is at minimum ({base_value_for_stat})")
        
        # Force update the display to show changes
        self.update_display()
    
    def action_show_history(self):
        """Show the galactic history screen"""
        self.app.push_screen(GalacticHistoryScreen())


class MainGameScreen(Screen):
    """Main game screen - NetHack style with map and status"""
    
    BINDINGS = [
        Binding("q", "quit_game", "Quit", show=False),
        Binding("i", "inventory", "Inventory", show=True),
        Binding("m", "map", "Map", show=True),
        Binding("n", "news", "News", show=True),
        Binding("r", "research", "Research", show=True),
        Binding("s", "status", "Status", show=True),
        Binding("h,H", "history", "History", show=True),
    ]
    
    def __init__(self, character_data):
        super().__init__()
        self.character_data = character_data
        self.game = Game() if GAME_AVAILABLE else None
        self.turn_count = 0
        
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

    def action_history(self):
        """Open the Galactic History screen"""
        self.app.push_screen(GalacticHistoryScreen())
        
    def compose(self) -> ComposeResult:
        """Compose the main game screen"""
        yield Static(id="status_bar")
        yield Static(id="main_area")
        yield MessageLog()
        
    def on_mount(self):
        """Initialize the game screen"""
        self.update_display()
        self.query_one(MessageLog).add_message(f"Welcome, {self.character_data['name']}!")
        self.query_one(MessageLog).add_message("Press 'n' for news, 'm' for map, 'i' for inventory, 's' for status")
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
        lines.append("[i: Inventory] [m: Map] [n: News] [s: Status] [q: Menu]")
        
        self.query_one("#main_area", Static).update("\n".join(lines))
    
    def advance_turn(self):
        """Advance the game turn and update events"""
        self.turn_count += 1
        
        # Update events every 3 turns
        if self.game and hasattr(self.game, 'event_system') and self.turn_count % 3 == 0:
            self.game.event_system.update_events()
        
    def action_inventory(self):
        """Show inventory screen"""
        self.query_one(MessageLog).add_message("Opening inventory...")
        self.app.push_screen(InventoryScreen(self.game))
        self.advance_turn()
        
    def action_map(self):
        """Show map screen"""
        self.query_one(MessageLog).add_message("Opening galactic map...")
        self.app.push_screen(MapScreen(self.game))
        self.advance_turn()
    
    def action_news(self):
        """Show galactic news feed"""
        self.query_one(MessageLog).add_message("Opening galactic news feed...")
        self.app.push_screen(GalacticNewsScreen(self.game))
        self.advance_turn()
        
    def action_research(self):
        """Show research screen"""
        self.query_one(MessageLog).add_message("Opening research interface...")
        self.advance_turn()
        
    def action_status(self):
        """Show detailed status"""
        self.query_one(MessageLog).add_message("Opening status screen...")
        self.app.push_screen(StatusScreen(self.character_data, self.game))
        self.advance_turn()
        
    def action_quit_game(self):
        """Quit the game"""
        self.app.exit()


class MapScreen(Screen):
    """Galaxy map screen (NetHack-style ASCII map)"""
    
    BINDINGS = [
        Binding("escape,q", "pop_screen", "Back", show=True),
        Binding("n", "news", "News", show=True),
        Binding("f", "toggle_factions", "Toggle Factions", show=True),
        Binding("h,H", "history", "History", show=True),
    ]
    
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.move_count = 0  # Track moves for event updates
        # Viewport size (visible area) - expanded for larger screens
        self.viewport_width = 120
        self.viewport_height = 35
        # Virtual map size (much larger than viewport)
        self.virtual_width = 200
        self.virtual_height = 60
        # Viewport offset (camera position in virtual coordinates)
        self.viewport_x = 0
        self.viewport_y = 0
        # Scroll margin (distance from edge before scrolling)
        self.scroll_margin = 3
        # Faction zone display toggle
        self.show_faction_zones = False
        # Faction color mapping (persistent across updates)
        self.faction_colors = {}
    
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
        msg_log.add_message("@ = Your ship | & = NPC ships | * = Visited | + = Unvisited | ◈/◆ = Stations", "white")
        msg_log.add_message("Scanned objects: P/p = Planets | S = Stations | M/a = Asteroids", "bright_magenta")
        
        # Show NPC count
        nav = getattr(self.game, 'navigation', None)
        if nav and hasattr(nav, 'npc_ships'):
            msg_log.add_message(f"Active NPC ships in galaxy: {len(nav.npc_ships)}", "magenta")
    
    def update_map(self):
        nav = getattr(self.game, 'navigation', None)
        if not nav or not nav.galaxy:
            self.query_one("#map_display", Static).update("Galaxy data unavailable")
            return
        galaxy = nav.galaxy
        ship = nav.current_ship
        
        # Initialize virtual buffer - store (char, system_data, faction_name) tuples
        virtual_buf = [[(" ", None, None)] * self.virtual_width for _ in range(self.virtual_height)]
        
        def project(x, y):
            # Scale galaxy coordinates to virtual map coordinates
            px = int((x / galaxy.size_x) * (self.virtual_width - 1))
            py = int((y / galaxy.size_y) * (self.virtual_height - 1))
            # Clamp
            px = max(0, min(self.virtual_width - 1, px))
            py = max(0, min(self.virtual_height - 1, py))
            return px, py
        
        # If faction zones are enabled, draw faction backgrounds
        if self.show_faction_zones and hasattr(galaxy, 'faction_zones'):
            # Import deterministic faction color mapping
            from systems import FACTION_COLORS
            
            # Populate instance faction colors dictionary for consistent access
            available_colors = [
                "blue", "red", "green", "magenta", "cyan", 
                "yellow", "bright_blue", "bright_red", "bright_green",
                "bright_magenta", "bright_cyan"
            ]
            for idx, faction_name in enumerate(galaxy.faction_zones.keys()):
                if faction_name in FACTION_COLORS:
                    # Use predefined color for consistency
                    self.faction_colors[faction_name] = FACTION_COLORS[faction_name]
                else:
                    # Fallback for procedural factions
                    self.faction_colors[faction_name] = available_colors[idx % len(available_colors)]
            
            # Fill in faction zone backgrounds
            for py in range(self.virtual_height):
                for px in range(self.virtual_width):
                    # Convert virtual coords back to galaxy coords
                    gx = int((px / (self.virtual_width - 1)) * galaxy.size_x)
                    gy = int((py / (self.virtual_height - 1)) * galaxy.size_y)
                    gz = galaxy.size_z / 2  # Use middle z-plane for 2D visualization
                    
                    # Check which faction zone this point is in
                    faction = galaxy.get_faction_for_location(gx, gy, gz) if hasattr(galaxy, 'get_faction_for_location') else None
                    
                    if faction:
                        # Mark this cell as being in faction space with a subtle background character
                        virtual_buf[py][px] = ("░", None, faction)
        
        # Get objects in scan range if ship has scanning capability
        scanned_systems = set()
        if ship and hasattr(ship, 'get_objects_in_scan_range'):
            scan_results = ship.get_objects_in_scan_range(galaxy)
            for obj_type, obj_data, distance in scan_results:
                if obj_type == 'system':
                    # Mark system as scanned
                    scanned_systems.add(obj_data['name'])
        
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
            
            # Get faction for this system
            faction = sys.get('controlling_faction')
            virtual_buf[py][px] = (ch, sys, faction)
            
            # Add small icons below systems within scan range
            if sys['name'] in scanned_systems and py + 1 < self.virtual_height:
                # Determine what icons to show
                icons = []
                
                # Check for planets
                bodies = sys.get('celestial_bodies', [])
                planets = [b for b in bodies if b['object_type'] == 'Planet']
                if planets:
                    # Show P for habitable planets, p for regular planets
                    habitable = [p for p in planets if p.get('habitable')]
                    if habitable:
                        icons.append('P')  # Habitable planet
                    else:
                        icons.append('p')  # Regular planet
                
                # Check for stations
                if has_stations:
                    icons.append('S')  # Station
                
                # Check for special objects
                moons = [b for b in bodies if b['object_type'] == 'Moon']
                asteroids = [b for b in bodies if b['object_type'] == 'Asteroid Belt']
                
                if asteroids:
                    mineral_rich = [a for a in asteroids if a.get('mineral_rich')]
                    if mineral_rich:
                        icons.append('M')  # Mineral-rich asteroids
                    else:
                        icons.append('a')  # Regular asteroids
                
                # Place first icon below the system
                if icons and px < self.virtual_width:
                    current_char, current_data, current_faction = virtual_buf[py + 1][px]
                    # Only place if empty or space or faction background
                    if current_char == " " or current_char == "░":
                        virtual_buf[py + 1][px] = (icons[0], None, current_faction)
        
        # Plot NPC ships
        if nav and hasattr(nav, 'npc_ships'):
            for npc in nav.npc_ships:
                nx, ny, nz = npc.coordinates
                npx, npy = project(nx, ny)
                # Use '&' symbol for NPCs, preserve faction info
                _, _, faction = virtual_buf[npy][npx]
                virtual_buf[npy][npx] = ("&", npc, faction)
        
        # Plot player ship last (so it's on top)
        ship_vx = ship_vy = 0
        if ship:
            sx, sy, _ = ship.coordinates
            ship_vx, ship_vy = project(sx, sy)
            # Preserve faction info at player location
            _, _, faction = virtual_buf[ship_vy][ship_vx]
            virtual_buf[ship_vy][ship_vx] = ("@", None, faction)
            
            # Center viewport on ship
            self.center_viewport_on(ship_vx, ship_vy)
        
        # Build Rich Text with colors
        text = Text()
        
        # Header
        text.append("═" * self.viewport_width + "\n", style="bold cyan")
        header = "GALAXY MAP"
        if self.show_faction_zones:
            header += " - FACTION ZONES"
        text.append(header.center(self.viewport_width) + "\n", style="bold yellow")
        text.append("═" * self.viewport_width + "\n", style="bold cyan")
        
        # Render viewport with colors
        for y in range(self.viewport_height):
            virtual_y = self.viewport_y + y
            if 0 <= virtual_y < self.virtual_height:
                for x in range(self.viewport_width):
                    virtual_x = self.viewport_x + x
                    if 0 <= virtual_x < self.virtual_width:
                        char, sys_data, faction = virtual_buf[virtual_y][virtual_x]
                        
                        # Determine base style based on character type
                        base_style = None
                        
                        # Color based on character type
                        if char == "@":
                            base_style = "bold bright_white on blue"
                        elif char == "&":
                            # NPC ship
                            base_style = "bold magenta"
                        elif char in ["◈", "◆"]:
                            # Stations - cyan/bright_cyan, but may have faction background
                            if self.show_faction_zones and faction:
                                # Show in faction color
                                faction_color = self.faction_colors.get(faction, "cyan")
                                if char == "◈":
                                    base_style = f"bold bright_white on {faction_color}"
                                else:
                                    base_style = f"bold white on {faction_color}"
                            else:
                                if char == "◈":
                                    base_style = "bright_cyan"
                                else:
                                    base_style = "cyan"
                        elif char == "*":
                            # Visited system - green, but may have faction background
                            if self.show_faction_zones and faction:
                                faction_color = self.faction_colors.get(faction, "green")
                                base_style = f"bold white on {faction_color}"
                            else:
                                base_style = "green"
                        elif char == "+":
                            # Unvisited system - yellow, but may have faction background
                            if self.show_faction_zones and faction:
                                faction_color = self.faction_colors.get(faction, "yellow")
                                base_style = f"bold white on {faction_color}"
                            else:
                                base_style = "yellow"
                        elif char == "P":
                            # Habitable planet (scanned)
                            base_style = "bold bright_green"
                        elif char == "p":
                            # Regular planet (scanned)
                            base_style = "dim green"
                        elif char == "S":
                            # Station indicator (scanned)
                            base_style = "bold bright_cyan"
                        elif char == "M":
                            # Mineral-rich asteroids (scanned)
                            base_style = "bold yellow"
                        elif char == "a":
                            # Regular asteroids (scanned)
                            base_style = "dim white"
                        elif char == "░":
                            # Faction background
                            if self.show_faction_zones and faction:
                                faction_color = self.faction_colors.get(faction, "white")
                                base_style = f"dim {faction_color}"
                            else:
                                base_style = "dim white"
                        
                        if base_style:
                            text.append(char, style=base_style)
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
            text.append(f"  Range: {ship.jump_range}", style="white")
            # Show scan range
            scan_range = getattr(ship, 'scan_range', 5.0)
            text.append(f"  Scan: {scan_range:.1f}\n", style="bright_magenta")
        
        visited_count = sum(1 for s in galaxy.systems.values() if s.get("visited"))
        text.append(f"Systems: ", style="white")
        text.append(f"{len(galaxy.systems)}", style="bold yellow")
        text.append(f" | Visited: ", style="white")
        text.append(f"{visited_count}", style="bold green")
        
        # Show current faction zone if enabled
        if self.show_faction_zones and ship and hasattr(galaxy, 'get_faction_for_location'):
            sx, sy, sz = ship.coordinates
            current_faction = galaxy.get_faction_for_location(sx, sy, sz)
            if current_faction:
                text.append(f" | Zone: ", style="white")
                faction_color = self.faction_colors.get(current_faction, "white")
                text.append(f"{current_faction}", style=f"bold {faction_color}")
        
        # Show nearby NPCs
        if nav and hasattr(nav, 'npc_ships') and ship:
            nearby_npcs = []
            sx, sy, sz = ship.coordinates
            for npc in nav.npc_ships:
                nx, ny, nz = npc.coordinates
                distance = math.sqrt((sx-nx)**2 + (sy-ny)**2 + (sz-nz)**2)
                if distance <= 10:  # Within 10 units
                    nearby_npcs.append((npc, distance))
            
            if nearby_npcs:
                text.append(f" | NPCs nearby: ", style="white")
                text.append(f"{len(nearby_npcs)}", style="bold magenta")
        
        text.append("\n", style="white")
        
        # Legend
        if self.show_faction_zones:
            text.append("Faction Mode: ", style="bold bright_cyan")
            text.append("Colored backgrounds = faction zones  ", style="white")
            text.append("░ ", style="dim white")
            text.append("= faction space\n", style="white")
        
        text.append("Legend: ", style="white")
        text.append("@ ", style="bold bright_white on blue")
        text.append("You  ", style="white")
        text.append("& ", style="bold magenta")
        text.append("NPC  ", style="white")
        text.append("* ", style="green")
        text.append("Visited  ", style="white")
        text.append("+ ", style="yellow")
        text.append("Unvisited  ", style="white")
        text.append("◈ ", style="bright_cyan")
        text.append("Station(Vis)  ", style="white")
        text.append("◆ ", style="cyan")
        text.append("Station\n", style="white")
        
        text.append("Scan: ", style="white")
        text.append("P ", style="bold bright_green")
        text.append("Habitable  ", style="white")
        text.append("p ", style="dim green")
        text.append("Planet  ", style="white")
        text.append("S ", style="bold bright_cyan")
        text.append("Station  ", style="white")
        text.append("M ", style="bold yellow")
        text.append("Minerals  ", style="white")
        text.append("a ", style="dim white")
        text.append("Asteroids\n", style="white")
        
        text.append("[q/ESC: Back | Arrow/hjkl: Move | f: Toggle Factions | H: History]\n", style="dim white")
        
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
    
    def action_news(self):
        """Show galactic news feed from the map"""
        self.app.push_screen(GalacticNewsScreen(self.game))
    
    def action_history(self):
        """Show galactic history from the map"""
        self.app.push_screen(GalacticHistoryScreen())
    
    def action_toggle_factions(self):
        """Toggle faction zone visualization"""
        self.show_faction_zones = not self.show_faction_zones
        msg_log = self.query_one(MessageLog)
        if self.show_faction_zones:
            msg_log.add_message("Faction zones: ON", "bright_cyan")
        else:
            msg_log.add_message("Faction zones: OFF", "white")
        self.update_map()

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
        
        # Track moves and update events every 3 moves
        self.move_count += 1
        if self.move_count % 3 == 0 and hasattr(self.game, 'event_system'):
            self.game.event_system.update_events()
            # Show notification if new event occurred
            latest_news = self.game.event_system.get_news_feed(limit=1)
            if latest_news and self.move_count == 3:  # Only show first time
                msg_log = self.query_one(MessageLog)
                msg_log.add_message("⚡ New galactic event! Press 'n' for news", "bright_yellow")
        
        # Move NPC ships
        if hasattr(nav, 'update_npc_ships'):
            nav.update_npc_ships()
        
        # Check for NPC encounters
        if hasattr(nav, 'get_npc_at_location'):
            npc = nav.get_npc_at_location((x, y, z))
            if npc:
                try:
                    msg_log = self.query_one(MessageLog)
                    msg_log.add_message(f"Encountered {npc.name}!", "bright_magenta")
                    self.update_map()
                    self.app.push_screen(NPCEncounterScreen(self.game, npc, nav))
                    return
                except Exception as e:
                    msg_log = self.query_one(MessageLog)
                    msg_log.add_message(f"Error with NPC encounter: {e}", "red")
                    import traceback
                    traceback.print_exc()

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


class GalacticNewsScreen(Screen):
    """Galactic News Feed - displays recent events from the event system"""
    
    BINDINGS = [
        Binding("escape,q", "pop_screen", "Back", show=True),
        Binding("j,down", "scroll_down", "Down", show=False),
        Binding("k,up", "scroll_up", "Up", show=False),
    ]
    
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.news_scroll_offset = 0
        self.news_items = []
        self.max_display = 20
        
    def compose(self) -> ComposeResult:
        yield Static(id="news_display")
        yield MessageLog()
    
    def on_mount(self):
        self.load_news()
        self.render_news()
        msg_log = self.query_one(MessageLog)
        msg_log.add_message("Galactic News Network - Stay Informed", "bright_cyan")
        msg_log.add_message("Use j/k or arrows to scroll", "white")
    
    def load_news(self):
        """Load news from the event system"""
        self.news_items = []
        
        if not self.game or not hasattr(self.game, 'event_system'):
            # Generate some placeholder news if event system not available
            self.news_items = [
                {
                    'headline': 'Systems Online',
                    'description': 'All galactic communication systems are operational.',
                    'type': 'system',
                    'severity': 1
                }
            ]
            return
        
        # Get news from the event system
        news_feed = self.game.event_system.get_news_feed(limit=30)
        
        if news_feed:
            self.news_items = news_feed
        else:
            # No news yet, show a placeholder
            self.news_items = [
                {
                    'headline': 'Galaxy at Peace',
                    'description': 'No major events reported at this time. All systems nominal.',
                    'type': 'system',
                    'severity': 1
                }
            ]
    
    def render_news(self):
        """Render the news feed"""
        text = Text()
        
        # Header
        text.append("═" * 100 + "\n", style="bold cyan")
        text.append("GALACTIC NEWS NETWORK".center(100) + "\n", style="bold bright_cyan")
        text.append("Breaking News from Across the Galaxy".center(100) + "\n", style="cyan")
        text.append("═" * 100 + "\n", style="bold cyan")
        text.append("\n")
        
        # Show event count
        active_events = 0
        if self.game and hasattr(self.game, 'event_system'):
            active_events = len(self.game.event_system.get_active_events())
        
        text.append(f"Active Events: {active_events} | News Items: {len(self.news_items)}\n", style="yellow")
        text.append("─" * 100 + "\n", style="dim white")
        text.append("\n")
        
        # Display news items
        if not self.news_items:
            text.append("No news available.\n", style="dim white")
        else:
            # Show subset based on scroll offset
            start_idx = self.news_scroll_offset
            end_idx = min(start_idx + self.max_display, len(self.news_items))
            
            for i in range(start_idx, end_idx):
                item = self.news_items[i]
                
                # Color based on event type
                type_colors = {
                    'economic': 'green',
                    'political': 'blue',
                    'scientific': 'bright_cyan',
                    'military': 'red',
                    'natural': 'yellow',
                    'social': 'magenta',
                    'travel': 'cyan',
                    'scandal': 'bright_magenta',
                    'tabloid': 'bright_magenta',
                    'system': 'dim white'
                }
                
                event_type = item.get('type', 'system')
                color = type_colors.get(event_type, 'white')
                severity = item.get('severity', 1)
                
                # Severity indicator
                severity_mark = "!" * min(severity, 5)
                if severity >= 7:
                    severity_style = "bold red"
                elif severity >= 4:
                    severity_style = "yellow"
                else:
                    severity_style = "dim white"
                
                # Headline
                text.append(f"[{severity_mark:5}] ", style=severity_style)
                text.append(f"{item.get('headline', 'Unknown Event')}\n", style=f"bold {color}")
                
                # Description
                description = item.get('description', '')
                # Wrap description to fit screen
                if len(description) > 95:
                    description = description[:92] + "..."
                text.append(f"         {description}\n", style=color)
                
                # Event type and affected systems
                type_str = f"[{event_type.upper()}]"
                affected = item.get('affected_systems', [])
                if affected and len(affected) > 0:
                    systems_str = ", ".join(affected[:3])
                    if len(affected) > 3:
                        systems_str += f" (+{len(affected) - 3} more)"
                    text.append(f"         {type_str} Affected: {systems_str}\n", style="dim white")
                else:
                    text.append(f"         {type_str}\n", style="dim white")
                
                text.append("\n")
            
            # Scroll indicator
            if len(self.news_items) > self.max_display:
                text.append("─" * 100 + "\n", style="dim white")
                text.append(f"Showing {start_idx + 1}-{end_idx} of {len(self.news_items)} | ", style="dim cyan")
                text.append("Use j/k to scroll\n", style="dim cyan")
        
        self.query_one("#news_display", Static).update(text)
    
    def action_scroll_down(self):
        """Scroll down the news feed"""
        if self.news_scroll_offset + self.max_display < len(self.news_items):
            self.news_scroll_offset += 1
            self.render_news()
            self.query_one(MessageLog).add_message("Scrolled down", "dim white")
    
    def action_scroll_up(self):
        """Scroll up the news feed"""
        if self.news_scroll_offset > 0:
            self.news_scroll_offset -= 1
            self.render_news()
            self.query_one(MessageLog).add_message("Scrolled up", "dim white")
    
    def action_pop_screen(self):
        """Close the news screen"""
        self.app.pop_screen()


class NPCEncounterScreen(Screen):

    """Screen for interacting with NPC ships"""
    
    BINDINGS = [
        Binding("escape,q", "pop_screen", "Back", show=True),
    ]
    
    def __init__(self, game, npc, navigation):
        super().__init__()
        self.game = game
        self.npc = npc
        self.navigation = navigation
        self.mode = "main"  # main, trade, rumors
        self.selected_index = 0
        self.trade_mode = "buy"  # buy or sell
    
    def compose(self) -> ComposeResult:
        yield Static(id="npc_display")
        yield MessageLog()
    
    def on_mount(self):
        self.render_npc()
        msg_log = self.query_one(MessageLog)
        msg_log.add_message(f"Encountered {self.npc.name}", "bright_magenta")
        msg_log.add_message(self.npc.get_greeting(), "cyan")
    
    def on_key(self, event) -> None:
        key = event.key
        
        if self.mode == "main":
            if key in ["1"]:
                self.mode = "trade"
                self.selected_index = 0
                self.render_npc()
            elif key in ["2"]:
                self.show_rumors()
            elif key in ["3"]:
                self.chat()
            elif key in ["4", "q", "escape"]:
                self.app.pop_screen()
        
        elif self.mode == "trade":
            if key in ["1"]:
                self.trade_mode = "buy"
                self.selected_index = 0
                self.render_npc()
            elif key in ["2"]:
                self.trade_mode = "sell"
                self.selected_index = 0
                self.render_npc()
            elif key in ["escape", "q"]:
                self.mode = "main"
                self.render_npc()
            elif key == "j" or key == "down":
                items = list(self.npc.trade_goods.keys()) if self.trade_mode == "buy" else list(self.game.inventory.keys())
                if items:
                    self.selected_index = (self.selected_index + 1) % len(items)
                    self.render_npc()
            elif key == "k" or key == "up":
                items = list(self.npc.trade_goods.keys()) if self.trade_mode == "buy" else list(self.game.inventory.keys())
                if items:
                    self.selected_index = (self.selected_index - 1) % len(items)
                    self.render_npc()
            elif key == "enter":
                self.execute_trade()
    
    def render_npc(self):
        text = Text()
        
        # Header
        text.append("═" * 80 + "\n", style="bold cyan")
        text.append(f"NPC ENCOUNTER - {self.npc.name}".center(80) + "\n", style="bold yellow")
        text.append(f"Ship: {self.npc.ship_class} | Personality: {self.npc.personality}".center(80) + "\n", style="white")
        text.append("═" * 80 + "\n", style="bold cyan")
        text.append("\n")
        
        if self.mode == "main":
            text.append("What would you like to do?\n\n", style="bright_white")
            text.append("[1] Trade with them\n", style="cyan")
            text.append("[2] Ask about rumors\n", style="cyan")
            text.append("[3] Chat\n", style="cyan")
            text.append("[4] Leave\n", style="dim white")
            
            # Show NPC info
            text.append("\n" + "─" * 80 + "\n", style="white")
            text.append(f"NPC Credits: {self.npc.credits:,}\n", style="yellow")
            text.append(f"Cargo ({len(self.npc.trade_goods)} types): ", style="white")
            text.append(", ".join(self.npc.trade_goods.keys())[:60] + "\n", style="dim white")
        
        elif self.mode == "trade":
            text.append("TRADE MENU\n\n", style="bright_white")
            text.append("[1] Buy from NPC  ", style="cyan" if self.trade_mode == "buy" else "dim white")
            text.append("[2] Sell to NPC\n\n", style="cyan" if self.trade_mode == "sell" else "dim white")
            
            if self.trade_mode == "buy":
                text.append("Available from NPC:\n", style="bright_yellow")
                text.append("─" * 80 + "\n", style="white")
                
                if not self.npc.trade_goods:
                    text.append("Nothing available for trade.\n", style="dim white")
                else:
                    for i, (item, qty) in enumerate(self.npc.trade_goods.items()):
                        price = 10  # Base price
                        marker = "► " if i == self.selected_index else "  "
                        style = "bright_white" if i == self.selected_index else "white"
                        text.append(f"{marker}{item} x{qty} - {price} credits each\n", style=style)
            else:
                text.append("Your Inventory:\n", style="bright_yellow")
                text.append("─" * 80 + "\n", style="white")
                
                if not self.game.inventory:
                    text.append("Nothing to sell.\n", style="dim white")
                else:
                    for i, (item, qty) in enumerate(self.game.inventory.items()):
                        price = 8  # Sell price (lower than buy)
                        marker = "► " if i == self.selected_index else "  "
                        style = "bright_white" if i == self.selected_index else "white"
                        text.append(f"{marker}{item} x{qty} - {price} credits each\n", style=style)
            
            text.append("\n[j/k: navigate] [Enter: trade] [q: back]\n", style="dim white")
        
        text.append("\n" + "─" * 80 + "\n", style="white")
        text.append(f"Your Credits: {self.game.credits:,}\n", style="green")
        
        self.query_one("#npc_display", Static).update(text)
    
    def execute_trade(self):
        msg_log = self.query_one(MessageLog)
        
        if self.trade_mode == "buy":
            items = list(self.npc.trade_goods.keys())
            if not items or self.selected_index >= len(items):
                return
            
            item = items[self.selected_index]
            price = 10
            
            if self.game.credits >= price:
                # Buy one unit
                self.game.credits -= price
                self.npc.credits += price
                self.npc.trade_goods[item] -= 1
                
                if self.npc.trade_goods[item] <= 0:
                    del self.npc.trade_goods[item]
                    self.selected_index = max(0, self.selected_index - 1)
                
                # Add to player inventory
                self.game.inventory[item] = self.game.inventory.get(item, 0) + 1
                
                msg_log.add_message(f"Bought {item} for {price} credits", "green")
                self.render_npc()
            else:
                msg_log.add_message("Not enough credits!", "red")
        
        else:  # sell
            items = list(self.game.inventory.keys())
            if not items or self.selected_index >= len(items):
                return
            
            item = items[self.selected_index]
            price = 8
            
            if self.npc.credits >= price:
                # Sell one unit
                self.game.credits += price
                self.npc.credits -= price
                self.game.inventory[item] -= 1
                
                if self.game.inventory[item] <= 0:
                    del self.game.inventory[item]
                    self.selected_index = max(0, self.selected_index - 1)
                
                # Add to NPC inventory
                self.npc.trade_goods[item] = self.npc.trade_goods.get(item, 0) + 1
                
                msg_log.add_message(f"Sold {item} for {price} credits", "green")
                self.render_npc()
            else:
                msg_log.add_message("NPC doesn't have enough credits!", "red")
    
    def show_rumors(self):
        msg_log = self.query_one(MessageLog)
        
        # Generate 1-3 rumors
        num_rumors = random.randint(1, 3)
        for _ in range(num_rumors):
            rumor = self.npc.generate_rumor()
            msg_log.add_message(f"💬 {rumor}", "yellow")
        
        msg_log.add_message("Press any key to continue...", "dim white")
    
    def chat(self):
        msg_log = self.query_one(MessageLog)
        
        chat_responses = {
            "Friendly": [
                "It's a big galaxy out there. Stick to the trade routes if you're new.",
                "I've been doing this for years. Never gets old!",
                "Safe travels, friend. May the stars guide you."
            ],
            "Cautious": [
                "...Just passing through. Same as you, I assume.",
                "Keep your sensors sharp. Not everyone out here is friendly.",
                "I don't share my routes. Sorry."
            ],
            "Greedy": [
                "Credits make the galaxy go round, friend.",
                "Everything has a price. Everything.",
                "I didn't get rich by being generous."
            ],
            "Chatty": [
                "Oh, let me tell you about the time I nearly crashed into a comet!",
                "Have you been to the nebula sectors? Absolutely beautiful!",
                "I know someone who knows someone who found an ancient artifact..."
            ],
            "Mysterious": [
                "The void speaks to those who listen.",
                "Some paths are meant to be walked alone.",
                "You'll understand... in time."
            ],
            "Suspicious": [
                "Why so many questions? What are you really after?",
                "I don't know you. I don't trust you.",
                "This conversation is over."
            ]
        }
        
        response = random.choice(chat_responses.get(self.npc.personality, ["..."]))
        msg_log.add_message(f"{self.npc.name}: {response}", "cyan")
    
    def action_pop_screen(self):
        msg_log = self.query_one(MessageLog)
        msg_log.add_message(f"{self.npc.name} continues on their journey...", "dim white")
        self.app.pop_screen()


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
        
        # Faction control information
        controlling_faction = self.system.get('controlling_faction')
        if controlling_faction:
            text.append("⚑ Controlled by: ", style="white")
            text.append(f"{controlling_faction}\n", style="bold bright_magenta")
            
            # Show faction benefits if available
            if hasattr(self.game, 'faction_system'):
                benefits = self.game.faction_system.get_faction_zone_benefits(controlling_faction, 'system')
                rep = self.game.faction_system.player_relations.get(controlling_faction, 0)
                rep_status = self.game.faction_system.get_reputation_status(controlling_faction)
                
                text.append(f"  Your Reputation: ", style="white")
                rep_color = 'green' if rep >= 50 else 'yellow' if rep >= 0 else 'red'
                text.append(f"{rep_status} ({rep})\n", style=rep_color)
                
                # Show active benefits
                if benefits['description']:
                    text.append("  Active Benefits: ", style="white")
                    text.append(f"{', '.join(benefits['description'][:2])}\n", style="bright_green")
            
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
        character = self.character_data or {}
        game = self.game

        inner_width = 78
        left_width = 35
        right_width = 35

        def colorize(line: str, style: str) -> str:
            return f"[{style}]{line}[/{style}]"

        def fmt_line(text: str = "") -> str:
            trimmed = text[: inner_width - 2]
            return f"║ {trimmed.ljust(inner_width - 2)} ║"

        def fmt_center(text: str) -> str:
            trimmed = text[:inner_width]
            return f"║{trimmed.center(inner_width)}║"

        def fmt_two_col(left: str, right: str) -> str:
            left_trimmed = left[:left_width]
            right_trimmed = right[:right_width]
            content = f"{left_trimmed.ljust(left_width)} │ {right_trimmed.ljust(right_width)}"
            return f"║ {content.ljust(inner_width - 2)} ║"

        def wrap_column(text: str, width: int) -> list[str]:
            if not text:
                return [""]
            wrapped = textwrap.wrap(text, width=width, break_long_words=True, break_on_hyphens=False)
            return wrapped or [text[:width]]

        def render_two_col_pair(left_text: str, right_text: str) -> list[str]:
            left_chunks = wrap_column(left_text, left_width)
            right_chunks = wrap_column(right_text, right_width)
            rows = []
            for idx in range(max(len(left_chunks), len(right_chunks))):
                left_part = left_chunks[idx] if idx < len(left_chunks) else ""
                right_part = right_chunks[idx] if idx < len(right_chunks) else ""
                rows.append(fmt_two_col(left_part, right_part))
            return rows

        def render_two_col_block(left_lines: list[str], right_lines: list[str]) -> list[str]:
            rows = []
            for idx in range(max(len(left_lines), len(right_lines))):
                left_part = left_lines[idx] if idx < len(left_lines) else ""
                right_part = right_lines[idx] if idx < len(right_lines) else ""
                rows.append(fmt_two_col(left_part, right_part))
            return rows

        def render_bullets(entries: list[str]) -> list[str]:
            if not entries:
                return [fmt_line("• None recorded yet.")]
            bullet_lines = []
            for entry in entries:
                wrapped = textwrap.wrap(entry, width=inner_width - 4, break_long_words=True, break_on_hyphens=False)
                if not wrapped:
                    wrapped = [entry[: inner_width - 4]]
                for idx, chunk in enumerate(wrapped):
                    prefix = "• " if idx == 0 else "  "
                    bullet_lines.append(fmt_line(f"{prefix}{chunk}"))
            return bullet_lines

        def safe_attr(obj, attr):
            if not obj:
                return None
            try:
                return getattr(obj, attr)
            except Exception:
                return None

        def format_number(value):
            if value is None:
                return "—"
            if isinstance(value, (int, float)):
                if isinstance(value, float):
                    if value.is_integer():
                        return f"{int(value):,}"
                    return f"{value:,.2f}"
                return f"{value:,}"
            return str(value)

        name = character.get("name", "—")
        species_name = character.get("species", "—")
        class_name = character.get("class", "—")
        background_name = character.get("background", "—")
        faction_name = character.get("faction", "—")

        credits_val = format_number(safe_attr(game, "credits"))
        level_val = format_number(safe_attr(game, "level"))
        xp_val = format_number(safe_attr(game, "xp"))
        reputation_val = format_number(safe_attr(game, "reputation"))

        from characters import (
            STAT_NAMES,
            BASE_STAT_VALUE,
            calculate_derived_attributes,
            DERIVED_METRIC_INFO,
        )

        stats = character.get("stats", {})
        derived = calculate_derived_attributes(stats) if stats else {}

        species_info = species_database.get(species_name, {}) if GAME_AVAILABLE else {}
        background_info = background_data.get(background_name, {}) if GAME_AVAILABLE else {}
        class_info = character_classes.get(class_name, {}) if GAME_AVAILABLE else {}

        ships = []
        if game:
            try:
                ships.extend(getattr(game, "owned_ships", []) or [])
            except Exception:
                pass
            try:
                custom = getattr(game, "custom_ships", []) or []
                for ship in custom:
                    if isinstance(ship, dict):
                        ships.append(ship.get("name", "Custom Ship"))
                    else:
                        ships.append(str(ship))
            except Exception:
                pass

        stations = getattr(game, "owned_stations", []) or []
        platforms = getattr(game, "owned_platforms", []) or []
        inventory = getattr(game, "inventory", {}) or {}

        def gather_events() -> list[str]:
            if not game:
                return []
            for attr in ("recent_events", "event_log", "events", "history_log"):
                value = safe_attr(game, attr)
                if value:
                    if isinstance(value, list):
                        entries = []
                        for item in value[-6:]:
                            if isinstance(item, dict):
                                title = item.get("title") or item.get("name") or item.get("event")
                                desc = item.get("description") or item.get("summary")
                                if title and desc:
                                    entries.append(f"{title}: {desc}")
                                elif title:
                                    entries.append(str(title))
                                else:
                                    entries.append(str(item))
                            else:
                                entries.append(str(item))
                        return entries
                    return [str(value)]
            return []

        event_entries = gather_events()

        def gather_decorations() -> list[str]:
            decorations = []
            for source in (
                character.get("decorations"),
                character.get("awards"),
                safe_attr(game, "decorations"),
                safe_attr(game, "awards"),
                safe_attr(game, "commendations"),
            ):
                if not source:
                    continue
                if isinstance(source, list):
                    decorations.extend([str(item) for item in source])
                else:
                    decorations.append(str(source))
            return decorations

        decoration_entries = gather_decorations()

        talent_entries = []
        for talent in character.get("talents", []) or []:
            talent_entries.append(f"Personal Talent: {talent}")

        if background_info:
            talent = background_info.get("talent")
            if talent:
                talent_entries.append(f"Background Talent: {talent}")
            for trait in background_info.get("traits", []) or []:
                talent_entries.append(f"Background Trait: {trait}")
            bonuses = background_info.get("stat_bonuses", {})
            for stat_code, bonus_val in bonuses.items():
                talent_entries.append(f"Background Bonus: +{bonus_val} {stat_code}")

        if species_info:
            for trait in species_info.get("special_traits", []) or []:
                talent_entries.append(f"Species Trait: {trait}")

        if class_info:
            for skill in class_info.get("skills", []) or []:
                talent_entries.append(f"Class Skill: {skill}")
            bonuses = class_info.get("bonuses", {})
            for bonus_name, bonus_value in bonuses.items():
                percent = round(bonus_value * 100) if isinstance(bonus_value, (int, float)) else bonus_value
                if isinstance(percent, (int, float)):
                    talent_entries.append(f"Class Bonus: {bonus_name.replace('_', ' ').title()} +{percent}%")
                else:
                    talent_entries.append(f"Class Bonus: {bonus_name.replace('_', ' ').title()} {percent}")

        top_border = "╔" + "═" * inner_width + "╗"
        section_divider = "╠" + "═" * inner_width + "╣"
        sub_divider = "╟" + "─" * inner_width + "╢"
        bottom_border = "╚" + "═" * inner_width + "╝"

        lines = []
        lines.append(colorize(top_border, "bold cyan"))
        lines.append(colorize(fmt_center("CHARACTER SHEET"), "bold cyan"))
        lines.append(colorize(section_divider, "bold cyan"))
        lines.append(colorize(fmt_center("IDENTITY & ORIGINS"), "bold yellow"))
        lines.append(colorize(sub_divider, "bold cyan"))

        identity_pairs = [
            (f"Name: {name}", f"Species: {species_name}"),
            (f"Class: {class_name}", f"Background: {background_name}"),
            (f"Faction: {faction_name}", f"Level: {level_val}"),
            (f"Credits: {credits_val}", f"Experience: {xp_val}"),
        ]

        if reputation_val != "—":
            identity_pairs.append((f"Reputation: {reputation_val}", ""))

        for left_text, right_text in identity_pairs:
            lines.extend(render_two_col_pair(left_text, right_text))

        lines.append(fmt_line())
        lines.append(colorize(section_divider, "bold cyan"))
        lines.append(colorize(fmt_center("ATTRIBUTES"), "bold yellow"))
        lines.append(colorize(sub_divider, "bold cyan"))

        stat_lines = []
        if stats:
            for code, stat_name in STAT_NAMES.items():
                value = stats.get(code, BASE_STAT_VALUE)
                stat_lines.append(f"{code} {stat_name:<18} {value:>3}/100")
        else:
            stat_lines.append("No core attributes recorded.")

        derived_lines = []
        if derived:
            for metric_name, metric_value in derived.items():
                name_slice = metric_name[:20]
                value_str = format_number(metric_value)
                combined = f"{name_slice:<20}{value_str:>{right_width - 20}}"
                derived_lines.append(combined)
        else:
            derived_lines.append("No derived metrics calculated.")

        lines.extend(render_two_col_block(stat_lines, derived_lines))

        lines.append(fmt_line())
        lines.append(colorize(section_divider, "bold cyan"))
        lines.append(colorize(fmt_center("TALENTS & TRAINING"), "bold yellow"))
        lines.append(colorize(sub_divider, "bold cyan"))
        lines.extend(render_bullets(talent_entries))

        lines.append(fmt_line())
        lines.append(colorize(section_divider, "bold cyan"))
        lines.append(colorize(fmt_center("RECENT EVENTS"), "bold yellow"))
        lines.append(colorize(sub_divider, "bold cyan"))
        lines.extend(render_bullets(event_entries or ["No notable events logged yet."]))

        lines.append(fmt_line())
        lines.append(colorize(section_divider, "bold cyan"))
        lines.append(colorize(fmt_center("HONORS & DECORATIONS"), "bold yellow"))
        lines.append(colorize(sub_divider, "bold cyan"))
        lines.extend(render_bullets(decoration_entries))

        lines.append(fmt_line())
        lines.append(colorize(section_divider, "bold cyan"))
        lines.append(colorize(fmt_center("FLEET & HOLDINGS"), "bold yellow"))
        lines.append(colorize(sub_divider, "bold cyan"))

        fleet_left = ["Ships"]
        if ships:
            for ship in ships:
                chunks = wrap_column(ship, left_width - 2)
                for idx, chunk in enumerate(chunks):
                    prefix = "• " if idx == 0 else "  "
                    fleet_left.append(f"{prefix}{chunk}")
        else:
            fleet_left.append("• None")

        holdings = []
        if stations:
            holdings.append("Stations")
            for station in stations:
                chunks = wrap_column(station, right_width - 2)
                for idx, chunk in enumerate(chunks):
                    prefix = "• " if idx == 0 else "  "
                    holdings.append(f"{prefix}{chunk}")
        if platforms:
            holdings.append("Platforms")
            for platform in platforms:
                chunks = wrap_column(platform, right_width - 2)
                for idx, chunk in enumerate(chunks):
                    prefix = "• " if idx == 0 else "  "
                    holdings.append(f"{prefix}{chunk}")

        if not holdings:
            holdings = ["Installations", "• None"]

        lines.extend(render_two_col_block(fleet_left, holdings))

        lines.append(fmt_line())
        lines.append(colorize(section_divider, "bold cyan"))
        lines.append(colorize(fmt_center("CARGO MANIFEST"), "bold yellow"))
        lines.append(colorize(sub_divider, "bold cyan"))

        cargo_entries = []
        if inventory:
            items = list(inventory.items())
            overflow = 0
            max_entries = 8
            if len(items) > max_entries:
                overflow = len(items) - max_entries
                items = items[:max_entries]
            for item_name, quantity in items:
                cargo_entries.append(f"{item_name}: {quantity}")
            if overflow:
                cargo_entries.append(f"… plus {overflow} additional item(s)")
        else:
            cargo_entries.append("Cargo hold is currently empty.")

        lines.extend(render_bullets(cargo_entries))

        lines.append(colorize(bottom_border, "bold cyan"))
        lines.append("[dim white][q/ESC: Back][/dim white]")

        self.query_one("#status_display", Static).update("\n".join(lines))
        self.query_one(MessageLog).add_message("Status displayed. Press 'q' to return.", "cyan")

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
    ]
    
    def __init__(self, game, system, station):
        super().__init__()
        self.game = game
        self.system = system
        self.station = station
        self.mode = "main"  # main, upgrade_category, upgrade_component
        self.selected_category = None
        self.selected_index = 0
        self.component_list = []
    
    def compose(self) -> ComposeResult:
        yield Static(id="shipyard_display")
        yield MessageLog()
    
    def on_key(self, event):
        """Handle key presses"""
        if event.character and event.character.isdigit():
            num = int(event.character)
            if self.mode == "main" and 1 <= num <= 2:
                if num == 1:
                    self.action_upgrade_ship()
                elif num == 2:
                    self.action_build_ship()
                event.prevent_default()
            elif self.mode == "upgrade_category" and 1 <= num <= 5:
                self.select_category(num)
                event.prevent_default()
        elif event.key == "up" or event.key == "k":
            if self.mode == "upgrade_component":
                self.selected_index = max(0, self.selected_index - 1)
                self.render_shipyard()
        elif event.key == "down" or event.key == "j":
            if self.mode == "upgrade_component":
                self.selected_index = min(len(self.component_list) - 1, self.selected_index + 1)
                self.render_shipyard()
        elif event.key == "enter":
            if self.mode == "upgrade_component" and self.component_list:
                self.install_selected_component()
                event.prevent_default()
    
    def on_mount(self):
        self.render_shipyard()
        self.query_one(MessageLog).add_message(f"Connected to {self.station.get('name')}", "green")
    
    def render_shipyard(self):
        from ship_builder import ship_components
        text = Text()
        
        # Header
        text.append("═" * 80 + "\n", style="bold cyan")
        text.append(f"SHIPYARD - {self.station.get('name', 'Unknown Station')}".center(80) + "\n", style="bold yellow")
        text.append("═" * 80 + "\n", style="bold cyan")
        text.append("\n")
        
        # Current ship info
        nav = getattr(self.game, 'navigation', None)
        ship = nav.current_ship if nav else None
        
        if ship and hasattr(ship, 'components'):
            text.append("CURRENT SHIP: ", style="bold bright_green")
            text.append(f"{ship.name}\n", style="bright_cyan")
            
            # Show installed components
            text.append(f"  Hull: ", style="white")
            text.append(f"{ship.components.get('hull', 'Unknown')}\n", style="cyan")
            text.append(f"  Engine: ", style="white")
            text.append(f"{ship.components.get('engine', 'None')}\n", style="cyan")
            
            if ship.components.get('weapons'):
                text.append(f"  Weapons: ", style="white")
                text.append(f"{', '.join(ship.components['weapons'])}\n", style="cyan")
            
            if ship.components.get('shields'):
                text.append(f"  Shields: ", style="white")
                text.append(f"{', '.join(ship.components['shields'])}\n", style="cyan")
            
            if ship.components.get('special'):
                text.append(f"  Special: ", style="white")
                text.append(f"{', '.join(ship.components['special'])}\n", style="cyan")
            
            # Power info
            power_info = self.game.get_ship_power_info()
            if power_info:
                power_pct = power_info['power_percentage']
                power_color = "red" if power_pct > 90 else ("yellow" if power_pct > 70 else "green")
                text.append(f"  Power: ", style="white")
                text.append(f"{power_info['power_used']}W / {power_info['power_output']}W ", style=power_color)
                text.append(f"({power_pct:.0f}%)\n", style=power_color)
            
            text.append("\n")
        
        # Mode-specific content
        if self.mode == "main":
            self._render_main_menu(text)
        elif self.mode == "upgrade_category":
            self._render_category_menu(text)
        elif self.mode == "upgrade_component":
            self._render_component_list(text)
        
        self.query_one("#shipyard_display", Static).update(text)
    
    def _render_main_menu(self, text):
        text.append("━" * 80 + "\n", style="cyan")
        text.append("SHIPYARD SERVICES:\n", style="bold bright_cyan")
        text.append("━" * 80 + "\n", style="cyan")
        text.append("\n")
        
        text.append("[", style="white")
        text.append("1", style="bold yellow")
        text.append("] Upgrade Current Ship\n", style="white")
        
        text.append("[", style="white")
        text.append("2", style="bold yellow")
        text.append("] Build New Ship (Coming Soon)\n", style="dim white")
        
        text.append("\n")
        text.append(f"Your Credits: ", style="white")
        text.append(f"{self.game.credits:,}\n", style="yellow")
        text.append("\n")
        text.append("[", style="white")
        text.append("q/ESC", style="bold cyan")
        text.append("] Back\n", style="white")
    
    def _render_category_menu(self, text):
        text.append("━" * 80 + "\n", style="cyan")
        text.append("SELECT COMPONENT CATEGORY:\n", style="bold bright_cyan")
        text.append("━" * 80 + "\n", style="cyan")
        text.append("\n")
        
        text.append("[", style="white")
        text.append("1", style="bold yellow")
        text.append("] Engines\n", style="white")
        
        text.append("[", style="white")
        text.append("2", style="bold yellow")
        text.append("] Weapons\n", style="white")
        
        text.append("[", style="white")
        text.append("3", style="bold yellow")
        text.append("] Shields\n", style="white")
        
        text.append("[", style="white")
        text.append("4", style="bold yellow")
        text.append("] Special Systems\n", style="white")
        
        text.append("\n[", style="white")
        text.append("q/ESC", style="bold cyan")
        text.append("] Back\n", style="white")
    
    def _render_component_list(self, text):
        from ship_builder import ship_components
        
        text.append("━" * 80 + "\n", style="cyan")
        text.append(f"AVAILABLE {self.selected_category.upper()}:\n", style="bold bright_cyan")
        text.append("━" * 80 + "\n", style="cyan")
        text.append("\n")
        
        if not self.component_list:
            text.append("No components available.\n", style="yellow")
        else:
            for i, (comp_name, comp_data) in enumerate(self.component_list):
                cursor = ">" if i == self.selected_index else " "
                
                # Check compatibility
                can_install, reason = self.game.can_install_component(self.selected_category, comp_name)
                status_color = "green" if can_install else "red"
                status_icon = "✓" if can_install else "✗"
                
                text.append(f" {cursor} ", style="white")
                text.append(f"{comp_name:<30} ", style="bright_cyan")
                text.append(f"{comp_data.get('cost', 0):>8,} cr  ", style="yellow")
                text.append(f"{status_icon} ", style=status_color)
                
                # Show key stats
                if self.selected_category == "Engines":
                    text.append(f"Speed:{comp_data.get('speed', 1.0):.1f}x Power:{comp_data.get('power_output', 0)}W", style="white")
                elif self.selected_category == "Weapons":
                    text.append(f"Dmg:{comp_data.get('damage', 0)} Pwr:{comp_data.get('power_required', 0)}W", style="white")
                elif self.selected_category == "Shields":
                    text.append(f"Str:{comp_data.get('shield_strength', 0)} Pwr:{comp_data.get('power_required', 0)}W", style="white")
                elif self.selected_category == "Special Systems":
                    if 'cargo_bonus' in comp_data:
                        text.append(f"Cargo:+{comp_data['cargo_bonus']}", style="white")
                    text.append(f" Pwr:{comp_data.get('power_required', 0)}W", style="white")
                
                text.append("\n")
                
                # Show reason if can't install
                if not can_install and i == self.selected_index:
                    text.append(f"      {reason}\n", style="red italic")
        
        text.append("\n")
        if self.component_list:
            selected_comp_name, selected_comp = self.component_list[self.selected_index]
            text.append("DESCRIPTION: ", style="bold white")
            text.append(f"{selected_comp.get('description', 'No description')}\n", style="italic white")
            text.append("\n")
        
        text.append("[", style="white")
        text.append("↑/↓ or j/k", style="bold cyan")
        text.append("] Navigate  [", style="white")
        text.append("Enter", style="bold green")
        text.append("] Install  [", style="white")
        text.append("q/ESC", style="bold cyan")
        text.append("] Back\n", style="white")
    
    def action_pop_screen(self):
        if self.mode != "main":
            self.mode = "upgrade_category" if self.mode == "upgrade_component" else "main"
            self.selected_index = 0
            self.render_shipyard()
        else:
            self.app.pop_screen()
    
    def action_upgrade_ship(self):
        ship = self.game.navigation.current_ship if self.game.navigation else None
        if not ship:
            self.query_one(MessageLog).add_message("No active ship!", "red")
            return
        
        if not hasattr(ship, 'components'):
            self.query_one(MessageLog).add_message("This ship doesn't support upgrades", "red")
            return
        
        self.mode = "upgrade_category"
        self.render_shipyard()
        self.query_one(MessageLog).add_message("Select component category", "cyan")
    
    def action_build_ship(self):
        self.query_one(MessageLog).add_message("Ship construction coming soon!", "yellow")
    
    def select_category(self, num):
        from ship_builder import ship_components
        
        categories = ["Engines", "Weapons", "Shields", "Special Systems"]
        if 1 <= num <= len(categories):
            self.selected_category = categories[num - 1]
            self.component_list = list(ship_components[self.selected_category].items())
            self.selected_index = 0
            self.mode = "upgrade_component"
            self.render_shipyard()
            self.query_one(MessageLog).add_message(f"Browsing {self.selected_category}", "cyan")
    
    def install_selected_component(self):
        if not self.component_list:
            return
        
        comp_name, comp_data = self.component_list[self.selected_index]
        
        # Check if can install
        can_install, reason = self.game.can_install_component(self.selected_category, comp_name)
        if not can_install:
            self.query_one(MessageLog).add_message(reason, "red")
            return
        
        # Install component
        success, message = self.game.install_ship_component(self.selected_category, comp_name)
        
        if success:
            self.query_one(MessageLog).add_message(message, "green")
            self.render_shipyard()  # Refresh display with new stats
        else:
            self.query_one(MessageLog).add_message(message, "red")


class ResearchScreen(Screen):
    """Screen for research station operations"""
    
    BINDINGS = [
        Binding("escape,q", "pop_screen", "Back", show=True),
    ]
    
    def __init__(self, game, system, station):
        super().__init__()
        self.game = game
        self.system = system
        self.station = station
        self.mode = "main"  # main, browse, start, purchase
        self.selected_category = None
        self.selected_index = 0
        self.research_list = []
    
    def compose(self) -> ComposeResult:
        yield Static(id="research_display")
        yield MessageLog()
    
    def on_key(self, event):
        """Handle key presses"""
        if event.character and event.character.isdigit():
            num = int(event.character)
            if self.mode == "main" and 1 <= num <= 3:
                if num == 1:
                    self.action_browse_research()
                elif num == 2:
                    self.action_start_research()
                elif num == 3:
                    self.action_purchase_data()
                event.prevent_default()
            elif self.mode == "browse" and 1 <= num <= 9:
                self.select_category(num)
                event.prevent_default()
        elif event.key == "up" or event.key == "k":
            if self.mode in ["start", "purchase"]:
                self.selected_index = max(0, self.selected_index - 1)
                self.render_research()
        elif event.key == "down" or event.key == "j":
            if self.mode in ["start", "purchase"]:
                self.selected_index = min(len(self.research_list) - 1, self.selected_index + 1)
                self.render_research()
        elif event.key == "enter":
            if self.mode == "start" and self.research_list:
                self.start_selected_research()
                event.prevent_default()
            elif self.mode == "purchase" and self.research_list:
                self.purchase_selected_research()
                event.prevent_default()
        elif event.key == "c" and self.mode == "main":
            # Cancel current research
            self.cancel_current_research()
            event.prevent_default()
        elif event.key == "p" and self.mode == "main":
            # Progress research manually (for testing)
            self.progress_research_manually()
            event.prevent_default()
    
    def on_mount(self):
        self.render_research()
        self.query_one(MessageLog).add_message(f"Connected to {self.station.get('name')}", "green")
    
    def render_research(self):
        from research import all_research, research_categories
        text = Text()
        
        # Header
        text.append("═" * 80 + "\n", style="bold magenta")
        text.append(f"RESEARCH STATION - {self.station.get('name', 'Unknown Station')}".center(80) + "\n", style="bold yellow")
        text.append("═" * 80 + "\n", style="bold magenta")
        text.append("\n")
        
        # Active research status
        active_research = getattr(self.game, 'active_research', None)
        if active_research:
            research_data = all_research.get(active_research)
            if research_data:
                progress = getattr(self.game, 'research_progress', 0)
                total_time = research_data.get('research_time', 100)
                progress_pct = (progress / total_time) * 100 if total_time > 0 else 0
                
                text.append("ACTIVE RESEARCH: ", style="bold bright_magenta")
                text.append(f"{active_research}\n", style="bright_cyan")
                
                # Progress bar
                bar_width = 40
                filled = int(progress_pct / 100 * bar_width)
                bar = "[" + ("█" * filled) + ("·" * (bar_width - filled)) + "]"
                progress_color = "green" if progress_pct > 66 else ("yellow" if progress_pct > 33 else "red")
                text.append(f"  {bar} ", style=progress_color)
                text.append(f"{progress_pct:.1f}%\n", style=progress_color)
                text.append(f"  {progress}/{total_time} days\n", style="white")
                text.append("\n")
        
        # Completed research count
        completed = getattr(self.game, 'completed_research', [])
        if completed:
            text.append(f"Completed: ", style="white")
            text.append(f"{len(completed)} ", style="green")
            text.append(f"/ {len(all_research)} technologies\n", style="white")
            text.append("\n")
        
        # Mode-specific content
        if self.mode == "main":
            self._render_main_menu(text)
        elif self.mode == "browse":
            self._render_category_menu(text)
        elif self.mode == "start":
            self._render_research_list(text, for_purchase=False)
        elif self.mode == "purchase":
            self._render_research_list(text, for_purchase=True)
        
        self.query_one("#research_display", Static).update(text)
    
    def _render_main_menu(self, text):
        text.append("━" * 80 + "\n", style="magenta")
        text.append("RESEARCH SERVICES:\n", style="bold bright_magenta")
        text.append("━" * 80 + "\n", style="magenta")
        text.append("\n")
        
        text.append("[", style="white")
        text.append("1", style="bold yellow")
        text.append("] Browse Research Tree\n", style="white")
        
        text.append("[", style="white")
        text.append("2", style="bold yellow")
        text.append("] Start New Research\n", style="white")
        
        text.append("[", style="white")
        text.append("3", style="bold yellow")
        text.append("] Purchase Research Data (3x cost)\n", style="white")
        
        if self.game.active_research:
            text.append("\n[", style="white")
            text.append("c", style="bold red")
            text.append("] Cancel Active Research\n", style="white")
            
            text.append("[", style="white")
            text.append("p", style="bold cyan")
            text.append("] Progress Research (+10 days)\n", style="dim white")
        
        text.append("\n")
        text.append(f"Your Credits: ", style="white")
        text.append(f"{self.game.credits:,}\n", style="yellow")
        text.append("\n")
        text.append("[", style="white")
        text.append("q/ESC", style="bold cyan")
        text.append("] Back\n", style="white")
    
    def _render_category_menu(self, text):
        from research import research_categories
        
        text.append("━" * 80 + "\n", style="magenta")
        text.append("SELECT RESEARCH CATEGORY:\n", style="bold bright_magenta")
        text.append("━" * 80 + "\n", style="magenta")
        text.append("\n")
        
        categories = list(research_categories.keys())
        for i, category in enumerate(categories[:9], 1):  # Show first 9
            count = len(research_categories[category])
            completed_count = sum(1 for name in research_categories[category].keys() 
                                if name in self.game.completed_research)
            
            text.append("[", style="white")
            text.append(f"{i}", style="bold yellow")
            text.append(f"] {category} ", style="white")
            text.append(f"({completed_count}/{count})\n", style="cyan")
        
        text.append("\n[", style="white")
        text.append("q/ESC", style="bold cyan")
        text.append("] Back\n", style="white")
    
    def _render_research_list(self, text, for_purchase=False):
        from research import all_research
        
        title = "PURCHASE RESEARCH DATA" if for_purchase else "START NEW RESEARCH"
        text.append("━" * 80 + "\n", style="magenta")
        text.append(f"{title}:\n", style="bold bright_magenta")
        text.append("━" * 80 + "\n", style="magenta")
        text.append("\n")
        
        if not self.research_list:
            text.append("No research projects available.\n", style="yellow")
        else:
            # Show scrollable list
            max_visible = 15
            total_items = len(self.research_list)
            scroll_offset = max(0, min(self.selected_index - max_visible + 1, total_items - max_visible))
            scroll_offset = max(0, scroll_offset)
            
            if scroll_offset > 0:
                text.append(f"  ▲ ({scroll_offset} items above)\n", style="dim white")
            
            end_idx = min(scroll_offset + max_visible, total_items)
            for i in range(scroll_offset, end_idx):
                research_name, research_data = self.research_list[i]
                cursor = ">" if i == self.selected_index else " "
                
                # Check affordability
                cost = research_data.get('research_cost', 0)
                if for_purchase:
                    cost = int(cost * 3.0)  # 3x for purchase
                
                can_afford = cost <= self.game.credits
                cost_color = "yellow" if can_afford else "red"
                
                text.append(f" {cursor} ", style="white")
                text.append(f"{research_name:<40} ", style="bright_magenta")
                text.append(f"{cost:>10,} cr ", style=cost_color)
                text.append(f"[{research_data.get('difficulty', 0)}/10]", style="cyan")
                text.append(f" {research_data.get('research_time', 0)} days\n", style="white")
            
            if end_idx < total_items:
                text.append(f"  ▼ ({total_items - end_idx} items below)\n", style="dim white")
            
            # Show selected research details
            if self.research_list:
                selected_name, selected_data = self.research_list[self.selected_index]
                text.append("\n")
                text.append("━" * 80 + "\n", style="dim white")
                text.append(f"{selected_name}\n", style="bold bright_magenta")
                text.append(f"{selected_data.get('description', '')}\n", style="italic white")
                text.append(f"\nDifficulty: {selected_data.get('difficulty', 0)}/10  ", style="cyan")
                text.append(f"Time: {selected_data.get('research_time', 0)} days  ", style="white")
                text.append(f"Category: {selected_data.get('category', 'Unknown')}\n", style="yellow")
                
                if selected_data.get('prerequisites'):
                    text.append(f"Prerequisites: {', '.join(selected_data['prerequisites'])}\n", style="red")
                
                if selected_data.get('unlocks'):
                    text.append(f"Unlocks: {', '.join(selected_data['unlocks'])}\n", style="green")
        
        text.append("\n[", style="white")
        text.append("↑/↓ or j/k", style="bold cyan")
        text.append("] Navigate  [", style="white")
        text.append("Enter", style="bold green")
        action_text = "Purchase" if for_purchase else "Start"
        text.append(f"] {action_text}  [", style="white")
        text.append("q/ESC", style="bold cyan")
        text.append("] Back\n", style="white")
    
    def action_pop_screen(self):
        if self.mode != "main":
            self.mode = "main"
            self.selected_index = 0
            self.render_research()
        else:
            self.app.pop_screen()
    
    def action_browse_research(self):
        self.mode = "browse"
        self.render_research()
        self.query_one(MessageLog).add_message("Select research category", "cyan")
    
    def action_start_research(self):
        if self.game.active_research:
            self.query_one(MessageLog).add_message("Already researching something! Cancel first with 'c'", "red")
            return
        
        available = self.game.get_available_research_projects()
        if not available:
            self.query_one(MessageLog).add_message("No research available!", "red")
            return
        
        self.research_list = list(available.items())
        self.selected_index = 0
        self.mode = "start"
        self.render_research()
        self.query_one(MessageLog).add_message("Select research to start", "cyan")
    
    def action_purchase_data(self):
        available = self.game.get_available_research_projects()
        if not available:
            self.query_one(MessageLog).add_message("No research available to purchase!", "red")
            return
        
        self.research_list = list(available.items())
        self.selected_index = 0
        self.mode = "purchase"
        self.render_research()
        self.query_one(MessageLog).add_message("Select research to purchase (3x cost)", "cyan")
    
    def select_category(self, num):
        from research import research_categories, all_research
        
        categories = list(research_categories.keys())
        if 1 <= num <= len(categories):
            category = categories[num - 1]
            research_in_category = research_categories[category]
            
            # Show info about this category
            msg_log = self.query_one(MessageLog)
            msg_log.add_message(f"Category: {category}", "magenta")
            
            completed = [name for name in research_in_category.keys() if name in self.game.completed_research]
            available = [name for name in research_in_category.keys() 
                        if name in self.game.get_available_research_projects()]
            
            msg_log.add_message(f"Completed: {len(completed)}, Available: {len(available)}, Total: {len(research_in_category)}", "cyan")
            
            # List some examples
            if available:
                examples = list(available)[:3]
                msg_log.add_message(f"Examples: {', '.join(examples)}", "yellow")
    
    def start_selected_research(self):
        if not self.research_list:
            return
        
        research_name, research_data = self.research_list[self.selected_index]
        success, message = self.game.start_research_project(research_name)
        
        if success:
            self.query_one(MessageLog).add_message(message, "green")
            self.mode = "main"
            self.render_research()
        else:
            self.query_one(MessageLog).add_message(message, "red")
    
    def purchase_selected_research(self):
        if not self.research_list:
            return
        
        research_name, research_data = self.research_list[self.selected_index]
        success, message = self.game.purchase_completed_research(research_name, cost_multiplier=3.0)
        
        if success:
            self.query_one(MessageLog).add_message(message, "green")
            self.mode = "main"
            self.render_research()
        else:
            self.query_one(MessageLog).add_message(message, "red")
    
    def cancel_current_research(self):
        success, message = self.game.cancel_research()
        if success:
            self.query_one(MessageLog).add_message(message, "yellow")
        else:
            self.query_one(MessageLog).add_message(message, "red")
        self.render_research()
    
    def progress_research_manually(self):
        """Manually progress research by 10 days (for testing)"""
        success, message = self.game.progress_research(days=10)
        self.query_one(MessageLog).add_message(message, "cyan" if success else "red")
        self.render_research()


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
