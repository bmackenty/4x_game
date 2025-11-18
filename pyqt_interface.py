#!/usr/bin/env python3
"""
PyQt6-Based “NetHack-Style” Interface for 4X Game
=================================================

This module provides a desktop GUI interface for the 4X Galactic Empire game,
designed to preserve the “NetHack / roguelike / old-school” feel while moving
out of the terminal.

Key design goals:
-----------------
- Preserve the *ASCII / text-forward* presentation:
  - The main content area is a QPlainTextEdit using a monospace font.
  - Layout uses panels and a bottom message log reminiscent of NetHack.
- Keep the game engine **UI-agnostic**:
  - The interface constructs and manipulates a `Game` instance from `game.py`.
  - All game logic remains in the engine; this module only:
    - Instantiates `Game`
    - Calls high-level functions like `load_game`, `save_game`
    - Renders summaries of the current state for human consumption.
- Provide a **menu-driven desktop feel**:
  - Menus: Game (New, Load, Save, Quit), View (History), Help (About).
  - Dialogs for loading saves and viewing galactic history.
  - Keyboard shortcuts (N, L, Q, H, etc.) to keep the roguelike workflow.

This file is intentionally verbose with comments and docstrings to serve as
teaching material and to make future extensions easier.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import sys
import textwrap

from PyQt6.QtCore import Qt, QSize, QRegularExpression
from PyQt6.QtGui import QFont, QAction, QSyntaxHighlighter, QTextCharFormat, QColor, QPalette
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QDockWidget,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

# ---------------------------------------------------------------------------
# Import game modules
# ---------------------------------------------------------------------------

# We mirror the pattern used in nethack_interface.py:
# - Try to import the real modules.
# - If that fails (e.g., standalone import for docs), fall back to stubs.
try:
    from game import Game
    from characters import create_character_stats, calculate_derived_attributes, DERIVED_METRIC_INFO
    from backgrounds import backgrounds as background_data, get_background_list, apply_background_bonuses
    from species import species_database, get_playable_species
    from factions import factions
    from classes import classes, get_available_classes
    from research import research_categories
    from navigation import Ship
    from galactic_history import generate_epoch_history
    from ship_builder import (
        ship_components,
        calculate_power_usage,
        compute_ship_profile,
        aggregate_component_metadata,
        collect_component_entries,
        COMPONENT_CATEGORY_LABELS,
    )
    from ship_classes import ship_classes
    from ship_attributes import SHIP_ATTRIBUTE_CATEGORIES, SHIP_ATTRIBUTE_DEFINITIONS
    from save_game import get_save_files, save_game, load_game, delete_save_file
    GAME_AVAILABLE = True
    print(f"SUCCESS: Game modules loaded. Factions count: {len(factions)}")

except ImportError as e:
    # Fallback stubs so the UI can still be imported without the engine.
    GAME_AVAILABLE = False
    print(f"FAILED: Import error at module level: {e}")

    class Game:  # type: ignore[no-redef]
        """Minimal stub for Game when engine is unavailable."""

        def __init__(self) -> None:
            self.player_name = "Demo Commander"
            self.credits = 0
            self.turn = 0

        def __str__(self) -> str:
            return "Demo Game (engine not available)"

    def generate_epoch_history() -> List[Dict[str, Any]]:  # type: ignore[no-redef]
        """Demo galactic history (used only if real function is unavailable)."""
        return [
            {
                "name": "Demo Epoch",
                "start_year": 0,
                "end_year": 10_000,
                "themes": ["Exploration", "First Contact"],
                "cataclysms": ["The Great Silence: All FTL comms drop for 100 years."],
                "faction_formations": [
                    {
                        "year": 2500,
                        "name": "Demo Coalition",
                        "event": "Prototype interstellar alliance is formed.",
                    }
                ],
                "mysteries": ["Origin of the ancient gates"],
                "civilizations": [
                    {
                        "name": "Proto-Terrans",
                        "species": "Terran",
                        "traits": ["Exploratory", "Diplomatic"],
                        "founded": 1000,
                        "collapsed": 9000,
                        "remnants": "Forms the basis of the present demo government.",
                        "notable_events": [
                            "First successful FTL jump",
                            "Discovery of alien ruins",
                        ],
                    }
                ],
            }
        ]

    def get_save_files() -> List[Dict[str, Any]]:  # type: ignore[no-redef]
        return []

    def save_game(game: Game, name: Optional[str] = None) -> bool:  # type: ignore[no-redef]
        return False

    def load_game(game: Game, path: str) -> bool:  # type: ignore[no-redef]
        return False


# ---------------------------------------------------------------------------
# Utility dataclasses and helper functions
# ---------------------------------------------------------------------------


@dataclass
class SaveGameInfo:
    """
    Simple representation of a save game entry.

    The actual data structure returned by `get_save_files()` in your project
    is a list of dictionaries. Here we normalize it into a dataclass for
    easier handling within the PyQt layer.

    Expected keys (based on nethack_interface.py snippet):
    ------------------------------------------------------
    - 'path': str             -> full filesystem path to save file
    - 'name': str             -> user-facing save name
    - 'player_name': str      -> name of the commander
    - 'character_class': str  -> e.g., Merchant, Explorer, etc.
    - 'credits': int          -> player credits at save time
    - 'turn': int             -> turn number at save time
    - 'timestamp': str        -> ISO-ish timestamp
    """

    path: str
    name: str
    player_name: str
    character_class: str
    credits: int
    turn: int
    timestamp: str

    @classmethod
    def from_raw(cls, raw: Dict[str, Any]) -> "SaveGameInfo":
        """
        Factory method to construct SaveGameInfo safely from a raw dict
        returned by `get_save_files()`.
        """
        return cls(
            path=str(raw.get("path", "")),
            name=str(raw.get("name", "Unnamed Save")),
            player_name=str(raw.get("player_name", "Unknown")),
            character_class=str(raw.get("character_class", "Unknown")),
            credits=int(raw.get("credits", 0)),
            turn=int(raw.get("turn", 0)),
            timestamp=str(raw.get("timestamp", "")),
        )


# ---------------------------------------------------------------------------
# Message log widget
# ---------------------------------------------------------------------------


class MessageLogWidget(QPlainTextEdit):
    """
    Bottom-of-window message log, similar in spirit to NetHack's message area.

    Behaviour:
    ----------
    - Read-only text area.
    - Maintains an internal buffer of messages.
    - Allows appending colored / styled messages in a simple ASCII-friendly way.
    - The PyQt version does not use ANSI colors by default; instead it uses
      plain text and simple markers (e.g., [INFO], [WARN], [ERROR]) to keep
      the look old-school.
    """

    def __init__(self, parent: Optional[QWidget] = None, max_messages: int = 50) -> None:
        super().__init__(parent)

        self._max_messages = max_messages
        self._messages: List[str] = []

        # Configure widget appearance for an old-school text UI feel.
        self.setReadOnly(True)
        font = QFont("Menlo")
        font.setStyleHint(QFont.StyleHint.TypeWriter)
        self.setFont(font)
        self.setMaximumHeight(120)  # keep it to roughly 6–8 lines
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        
        # Terminal-style black background with white text
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #000000;
                color: #FFFFFF;
                border: 1px solid #00AA00;
            }
        """)

    def add_message(self, message: str, prefix: str = "[INFO]") -> None:
        """
        Append a line to the log.

        Parameters
        ----------
        message : str
            The log message content.
        prefix : str, optional
            A short prefix indicating type or severity, e.g. "[WARN]".
        """
        full_line = f"{prefix} {message}"
        self._messages.append(full_line)

        # Truncate buffer if necessary.
        if len(self._messages) > self._max_messages:
            self._messages = self._messages[-self._max_messages :]

        # Update the Qt widget text.
        self.setPlainText("\n".join(self._messages))
        # Ensure the view is scrolled to the bottom.
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())


# ---------------------------------------------------------------------------
# Syntax highlighter for ASCII character sheet
# ---------------------------------------------------------------------------

class ASCIISheetHighlighter(QSyntaxHighlighter):
    """Colorize ASCII character sheet lines in the main view.

    - Borders: cyan
    - Section headers: yellow
    - Numbers: green
    - Footer hint: gray
    """

    def __init__(self, parent_document):
        super().__init__(parent_document)

        # Define text formats
        self.cyan_fmt = QTextCharFormat()
        self.cyan_fmt.setForeground(QColor("#00FFFF"))

        self.yellow_fmt = QTextCharFormat()
        self.yellow_fmt.setForeground(QColor("#FFFF55"))

        self.green_fmt = QTextCharFormat()
        self.green_fmt.setForeground(QColor("#00FF00"))

        self.gray_fmt = QTextCharFormat()
        self.gray_fmt.setForeground(QColor("#808080"))

        # Precompiled patterns
        self.border_re = QRegularExpression(r"^[╔╚╠╟].*[╗╣╢]$")
        self.section_re = QRegularExpression(r"^║\s*(CHARACTER SHEET|IDENTITY & ORIGINS|ATTRIBUTES|BACKGROUND & CLASS|FLEET & HOLDINGS|EQUIPMENT)\s*║$")
        self.hint_re = QRegularExpression(r"^\[Press O to return to overview\]")
        self.number_re = QRegularExpression(r"\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\b")

    def highlightBlock(self, text: str) -> None:
        # Borders
        if self.border_re.match(text).hasMatch():
            self.setFormat(0, len(text), self.cyan_fmt)
            return

        # Section headers
        if self.section_re.match(text).hasMatch():
            self.setFormat(0, len(text), self.yellow_fmt)

        # Footer hint
        if self.hint_re.match(text).hasMatch():
            self.setFormat(0, len(text), self.gray_fmt)

        # Numbers anywhere in the line
        it = self.number_re.globalMatch(text)
        while it.hasNext():
            m = it.next()
            self.setFormat(m.capturedStart(), m.capturedLength(), self.green_fmt)


# ---------------------------------------------------------------------------
# Galactic history dialog
# ---------------------------------------------------------------------------


class GalacticHistoryDialog(QDialog):
    """
    Modal dialog for viewing the procedurally generated galactic history.

    This is a PyQt adaptation of the `GalacticHistoryScreen` from
    `nethack_interface.py`. It:
    - Calls `generate_epoch_history()` from `galactic_history.py`.
    - Formats the returned data into ASCII text.
    - Displays it in a scrollable QPlainTextEdit.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Galactic History")
        self.resize(1000, 700)

        # Main vertical layout for the dialog.
        layout = QVBoxLayout(self)

        # Title label hinting at how to close.
        title_label = QLabel("Galactic History (press Esc or click Close to return)")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Scrollable text area for the history content.
        self.text_area = QPlainTextEdit(self)
        self.text_area.setReadOnly(True)

        font = QFont("Menlo")
        font.setStyleHint(QFont.StyleHint.TypeWriter)
        self.text_area.setFont(font)
        self.text_area.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        
        # Terminal-style black background with white text
        self.text_area.setStyleSheet("""
            QPlainTextEdit {
                background-color: #000000;
                color: #FFFFFF;
                border: 1px solid #00AA00;
            }
        """)

        layout.addWidget(self.text_area)

        # Dialog buttons (Close only).
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close, parent=self)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Populate content.
        self._populate_history()

    def _populate_history(self) -> None:
        """
        Generate and render the full galactic history as ASCII text.
        """
        try:
            history_data = generate_epoch_history()
        except Exception:
            # If something goes wrong, show a minimal message instead of crashing.
            history_data = []

        if not history_data:
            self.text_area.setPlainText("No galactic history data available.")
            return

        lines: List[str] = []
        
        # Add introduction
        lines.append("")
        lines.append("═" * 120)
        lines.append("")
        lines.append("                    THE CHRONICLES OF THE GALACTIC AGE")
        lines.append("                      A History of Civilizations Lost and Found")
        lines.append("")
        lines.append("═" * 120)
        lines.append("")
        lines.append("")

        # Use narrative formatting
        try:
            from galactic_history import format_epoch_narrative
            for epoch in history_data:
                epoch_lines = format_epoch_narrative(epoch)
                lines.extend(epoch_lines)
        except ImportError:
            # Fallback to old format if import fails
            for epoch in history_data:
                lines.append("═" * 120)
                lines.append(f" {epoch.get('name', 'Unnamed Epoch')}")
                start = epoch.get("start_year", 0)
                end = epoch.get("end_year", 0)
                lines.append(f" Years {start:,} – {end:,}")
                lines.append("")

        self.text_area.setPlainText("\n".join(lines))


# ---------------------------------------------------------------------------
# Load game dialog
# ---------------------------------------------------------------------------


class LoadGameDialog(QDialog):
    """
    Modal dialog that lists available save games and returns the user’s choice.

    Flow:
    -----
    - Fetches raw list from `get_save_files()`.
    - Normalizes entries into SaveGameInfo objects.
    - Displays each save as a list item with a multi-line description.
    - When the user clicks OK or double-clicks an item, the dialog returns the
      selected SaveGameInfo (accessible via `selected_save` attribute).
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Load Game")
        self.resize(600, 400)

        self.selected_save: Optional[SaveGameInfo] = None
        self._save_entries: List[SaveGameInfo] = []

        layout = QVBoxLayout(self)

        # Instruction label.
        label = QLabel("Select a save to load:")
        layout.addWidget(label)

        # List widget to display available saves.
        self.list_widget = QListWidget(self)
        layout.addWidget(self.list_widget)

        # OK / Cancel buttons.
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)

        # Populate the list from the game’s save system.
        self._load_saves()

    def _load_saves(self) -> None:
        """
        Retrieve save game entries and populate the list widget.
        """
        try:
            raw_saves = get_save_files()
        except Exception:
            raw_saves = []

        self._save_entries = [SaveGameInfo.from_raw(raw) for raw in raw_saves]

        self.list_widget.clear()

        if not self._save_entries:
            # Show a friendly message when there are no saves.
            item = QListWidgetItem("No save files found.")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.list_widget.addItem(item)
            return

        # Create one list item per save entry.
        for entry in self._save_entries:
            description = textwrap.dedent(
                f"""
                {entry.name}
                Player: {entry.player_name} | Class: {entry.character_class}
                Credits: {entry.credits:,} | Turn: {entry.turn}
                Time: {entry.timestamp}
                """
            ).strip()
            item = QListWidgetItem(description)
            self.list_widget.addItem(item)

    def _on_accept(self) -> None:
        """
        Called when the user presses OK. Sets `selected_save` based on the
        current selection.
        """
        row = self.list_widget.currentRow()
        if 0 <= row < len(self._save_entries):
            self.selected_save = self._save_entries[row]
            self.accept()
        else:
            # No valid selection; keep dialog open but give feedback.
            QMessageBox.warning(self, "No Selection", "Please select a save to load.")

    def _on_item_double_clicked(self, _: QListWidgetItem) -> None:
        """
        When the user double-clicks a list item, treat it as accepting the dialog.
        """
        self._on_accept()


# ---------------------------------------------------------------------------
# Character creation dialog
# ---------------------------------------------------------------------------


class CharacterCreationDialog(QDialog):
    """
    Multi-stage character creation wizard dialog.
    
    Mimics the flow from nethack_interface.py:
    species -> background -> faction -> class -> stats -> name -> confirm
    """
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        
        self.setWindowTitle("Character Creation")
        self.resize(1000, 700)
        
        # Character data
        self.stage = "species"
        self.character_data = {
            'species': None,
            'background': None,
            'faction': None,
            'class': None,
            'stats': None,
            'name': "",
        }
        
        # Import game modules for data
        if GAME_AVAILABLE:
            # Use the already-imported module-level data
            self.species_list = list(species_database.keys())
            self.playable_species = set(get_playable_species().keys())
            self.background_list = get_background_list()
            self.faction_list = list(factions.keys())
            self.class_list = []  # Will be populated after background selection
            self.species_database = species_database
            self.background_data = background_data
            self.factions = factions
            self.character_classes = classes
            
            print(f"Loaded: {len(self.species_list)} species, {len(self.background_list)} backgrounds, {len(self.faction_list)} factions, {len(classes)} total classes")
        else:
            print("DEBUG: GAME_AVAILABLE is False")
            self._set_demo_data()
        
        self.current_index = 0
        # Start on first playable species
        for i, species in enumerate(self.species_list):
            if species in self.playable_species:
                self.current_index = i
                break
        
        # Layout
        layout = QVBoxLayout(self)
        
        # Text display area
        self.text_area = QPlainTextEdit(self)
        self.text_area.setReadOnly(True)
        font = QFont("Menlo")
        font.setStyleHint(QFont.StyleHint.TypeWriter)
        self.text_area.setFont(font)
        self.text_area.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.text_area.setStyleSheet("""
            QPlainTextEdit {
                background-color: #000000;
                color: #FFFFFF;
                border: 1px solid #00AA00;
            }
        """)
        layout.addWidget(self.text_area)
        
        # Input area for name entry
        self.name_input = QLineEdit(self)
        self.name_input.setFont(font)
        self.name_input.setMaxLength(50)
        self.name_input.setPlaceholderText("Enter your character name...")
        self.name_input.hide()
        self.name_input.returnPressed.connect(self._handle_name_entry)
        layout.addWidget(self.name_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.prev_button = QPushButton("← Previous", self)
        self.prev_button.clicked.connect(self._go_previous)
        self.prev_button.setEnabled(False)
        button_layout.addWidget(self.prev_button)
        
        button_layout.addStretch()
        
        self.next_button = QPushButton("Confirm Selection →", self)
        self.next_button.clicked.connect(self._go_next)
        button_layout.addWidget(self.next_button)
        
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Set focus policy to ensure keyboard events are received
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.text_area.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # Initial render
        self._update_display()
    
    def _set_demo_data(self) -> None:
        """Set demo data when game modules unavailable."""
        self.species_list = ["Terran"]
        self.playable_species = {"Terran"}
        self.background_list = ["Orbital Foundling"]
        self.faction_list = ["Independent"]
        self.class_list = ["Explorer"]
        self.species_database = {}
        self.background_data = {}
        self.factions = {}
        self.character_classes = {}
    
    def keyPressEvent(self, event) -> None:  # type: ignore[override]
        """Handle keyboard navigation."""
        key = event.key()
        
        # Don't intercept keys when name input has focus
        if self.name_input.hasFocus():
            super().keyPressEvent(event)
            return
        
        # Stats stage - handle up/down for stat selection and left/right for adjustment
        if self.stage == "stats":
            if GAME_AVAILABLE:
                from characters import STAT_NAMES
                stat_codes = list(STAT_NAMES.keys())
                
                # Initialize selected stat index if not set
                if not hasattr(self, '_selected_stat_index'):
                    self._selected_stat_index = 0
                
                if key in (Qt.Key.Key_Up, Qt.Key.Key_K):
                    self._selected_stat_index = (self._selected_stat_index - 1) % len(stat_codes)
                    self._update_display()
                    event.accept()
                    return
                elif key in (Qt.Key.Key_Down, Qt.Key.Key_J):
                    self._selected_stat_index = (self._selected_stat_index + 1) % len(stat_codes)
                    self._update_display()
                    event.accept()
                    return
                elif key in (Qt.Key.Key_Left, Qt.Key.Key_H):
                    self._adjust_stat(-1)
                    event.accept()
                    return
                elif key in (Qt.Key.Key_Right, Qt.Key.Key_L):
                    self._adjust_stat(1)
                    event.accept()
                    return
                elif key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
                    self._go_next()
                    event.accept()
                    return
        
        # Up/Down or J/K for navigation in selection stages
        if key in (Qt.Key.Key_Up, Qt.Key.Key_K):
            if self.stage not in ("name", "confirm", "stats"):
                self.current_index = max(0, self.current_index - 1)
                self._update_display()
                event.accept()
        elif key in (Qt.Key.Key_Down, Qt.Key.Key_J):
            if self.stage not in ("name", "confirm", "stats"):
                max_idx = self._get_current_list_length() - 1
                self.current_index = min(max_idx, self.current_index + 1)
                self._update_display()
                event.accept()
        elif key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
            if self.stage == "name":
                self._handle_name_entry()
            else:
                self._go_next()
            event.accept()
        elif key == Qt.Key.Key_Escape:
            self.reject()
            event.accept()
        else:
            super().keyPressEvent(event)
    
    def _get_current_list_length(self) -> int:
        """Get length of current selection list."""
        if self.stage == "species":
            return len(self.species_list)
        elif self.stage == "background":
            return len(self.background_list)
        elif self.stage == "faction":
            return len(self.faction_list)
        elif self.stage == "class":
            return len(self.class_list)
        return 0
    
    def _update_display(self) -> None:
        """Render the current stage."""
        lines = []
        lines.append("═" * 80)
        lines.append("CHARACTER CREATION".center(80))
        lines.append("═" * 80)
        lines.append("")
        
        # Show progress as a table
        lines.append("┌────────────┬──────────────────────────┬────────────┬──────────────────────────┐")
        lines.append(f"│ Species    │ {(self.character_data['species'] or '???')[:24]:<24} │ Background │ {(self.character_data['background'] or '???')[:24]:<24} │")
        lines.append("├────────────┼──────────────────────────┼────────────┼──────────────────────────┤")
        lines.append(f"│ Faction    │ {(self.character_data['faction'] or '???')[:24]:<24} │ Class      │ {(self.character_data['class'] or '???')[:24]:<24} │")
        lines.append("├────────────┴──────────────────────────┴────────────┴──────────────────────────┤")
        lines.append(f"│ Name: {(self.character_data['name'] or '???')[:71]:<71} │")
        lines.append("└───────────────────────────────────────────────────────────────────────────────┘")
        lines.append("")
        lines.append("─" * 80)
        lines.append("")
        
        if self.stage == "species":
            lines.extend(self._render_species_selection())
        elif self.stage == "background":
            lines.extend(self._render_background_selection())
        elif self.stage == "faction":
            lines.extend(self._render_faction_selection())
        elif self.stage == "class":
            lines.extend(self._render_class_selection())
        elif self.stage == "stats":
            lines.extend(self._render_stats_display())
        elif self.stage == "name":
            lines.extend(self._render_name_entry())
        elif self.stage == "confirm":
            lines.extend(self._render_confirmation())
        
        self.text_area.setPlainText("\n".join(lines))
        
        # Update button states
        self.prev_button.setEnabled(self.stage != "species")
        if self.stage == "confirm":
            self.next_button.setText("Create Character")
        else:
            self.next_button.setText("Confirm Selection →")
    
    def _render_species_selection(self) -> List[str]:
        """Render species selection screen."""
        lines = []
        lines.append("SELECT YOUR SPECIES:")
        lines.append("")
        
        # Get current species details
        if 0 <= self.current_index < len(self.species_list):
            current_species_name = self.species_list[self.current_index]
            current_species = self.species_database.get(current_species_name, {})
        else:
            current_species_name = ""
            current_species = {}
        
        # Build detail lines for right panel
        detail_lines = []
        if current_species:
            detail_lines.append("│ SPECIES DETAILS")
            detail_lines.append("│ " + "─" * 38)
            
            # Description
            desc = current_species.get("description", "")
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
            
            # Category, homeworld, etc.
            category = current_species.get("category")
            if category:
                detail_lines.append(f"│ Category: {category}")
            homeworld = current_species.get("homeworld")
            if homeworld:
                detail_lines.append(f"│ Homeworld: {homeworld}")
            
            # Special traits
            traits = current_species.get("special_traits", [])
            if traits:
                detail_lines.append("│")
                detail_lines.append("│ Special Traits:")
                for trait in traits:
                    detail_lines.append(f"│   - {trait}")
        
        # Two-column layout: species list on left, details on right
        visible_count = min(15, len(self.species_list))
        for i, species in enumerate(self.species_list[:visible_count]):
            is_playable = species in self.playable_species
            cursor = ">" if i == self.current_index else " "
            species_display = species if is_playable else f"{species} (not playable)"
            left_text = f"  {cursor} {species_display}"[:38].ljust(38)
            
            # Right side: detail lines
            if i < len(detail_lines):
                right_text = detail_lines[i]
            else:
                right_text = "│"
            
            lines.append(left_text + "  " + right_text)
        
        # Remaining detail lines
        if len(detail_lines) > visible_count:
            for detail_line in detail_lines[visible_count:]:
                left_text = " " * 38
                lines.append(left_text + "  " + detail_line)
        
        lines.append("")
        lines.append(f"[{self.current_index + 1}/{len(self.species_list)}]")
        
        return lines
    
    def _render_background_selection(self) -> List[str]:
        """Render background selection screen."""
        lines = []
        lines.append("SELECT YOUR BACKGROUND:")
        lines.append("")
        
        # Get current background details
        if 0 <= self.current_index < len(self.background_list):
            current_bg_name = self.background_list[self.current_index]
            current_bg = self.background_data.get(current_bg_name, {})
        else:
            current_bg = {}
        
        # Build detail lines for right panel
        detail_lines = []
        if current_bg:
            detail_lines.append("│ BACKGROUND DETAILS")
            detail_lines.append("│ " + "─" * 38)
            
            # Description
            desc = current_bg.get('description', '')
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
            
            # Stat bonuses
            bonuses = current_bg.get('stat_bonuses', {})
            if bonuses:
                detail_lines.append("│ Stat Bonuses:")
                for stat, bonus in bonuses.items():
                    detail_lines.append(f"│   +{bonus} {stat}")
                detail_lines.append("│")
            
            # Talent
            talent = current_bg.get('talent', '')
            if talent:
                detail_lines.append("│ Talent:")
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
        
        # Two-column layout with scrolling
        visible_count = 15
        scroll_offset = max(0, self.current_index - visible_count + 5)  # Keep selection visible
        visible_backgrounds = self.background_list[scroll_offset:scroll_offset + visible_count]
        
        for i, bg in enumerate(visible_backgrounds):
            actual_index = i + scroll_offset
            cursor = ">" if actual_index == self.current_index else " "
            left_text = f"  {cursor} {bg}"[:38].ljust(38)
            
            # Right side: detail lines
            if i < len(detail_lines):
                right_text = detail_lines[i]
            else:
                right_text = "│"
            
            lines.append(left_text + "  " + right_text)
        
        # Remaining detail lines below the background list
        if len(detail_lines) > len(visible_backgrounds):
            for detail_line in detail_lines[len(visible_backgrounds):]:
                left_text = " " * 38
                lines.append(left_text + "  " + detail_line)
        
        lines.append("")
        if len(self.background_list) > visible_count:
            lines.append(f"[{self.current_index + 1}/{len(self.background_list)}] (Use ↑/↓ to scroll)")
        else:
            lines.append(f"[{self.current_index + 1}/{len(self.background_list)}]")
        
        return lines
    
    def _render_faction_selection(self) -> List[str]:
        """Render faction selection screen."""
        lines = []
        lines.append("SELECT YOUR FACTION:")
        lines.append("")
        
        # Get current faction details
        if 0 <= self.current_index < len(self.faction_list):
            current_faction_name = self.faction_list[self.current_index]
            current_faction = self.factions.get(current_faction_name, {})
        else:
            current_faction = {}
        
        # Build detail lines for right panel
        detail_lines = []
        if current_faction:
            detail_lines.append("│ FACTION DETAILS")
            detail_lines.append("│ " + "─" * 38)
            detail_lines.append(f"│ Philosophy: {current_faction.get('philosophy', 'Unknown')}")
            detail_lines.append(f"│ Focus: {current_faction.get('primary_focus', 'Unknown')}")
            detail_lines.append(f"│ Government: {current_faction.get('government_type', 'Unknown')}")
            detail_lines.append("│")
            
            # Description
            desc = current_faction.get('description', '')
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
            
            # Origin story
            origin = current_faction.get('origin_story', '')
            if origin:
                detail_lines.append("│ Origin:")
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
                detail_lines.append("│")
            
            # Founding info
            epoch = current_faction.get('founding_epoch', 'Unknown')
            year = current_faction.get('founding_year', '?')
            detail_lines.append(f"│ Founded: {epoch}")
            detail_lines.append(f"│ Year: {year}")
        
        # Two-column layout with scrolling
        visible_count = 20
        scroll_offset = max(0, self.current_index - 10) if len(self.faction_list) > visible_count else 0
        end_index = min(scroll_offset + visible_count, len(self.faction_list))
        visible_factions = self.faction_list[scroll_offset:end_index]
        
        for i, faction in enumerate(visible_factions):
            actual_index = i + scroll_offset
            cursor = ">" if actual_index == self.current_index else " "
            left_text = f"  {cursor} {faction}"[:38].ljust(38)
            
            # Right side: detail lines
            if i < len(detail_lines):
                right_text = detail_lines[i]
            else:
                right_text = "│"
            
            lines.append(left_text + "  " + right_text)
        
        # Remaining detail lines below the faction list
        if len(detail_lines) > len(visible_factions):
            for detail_line in detail_lines[len(visible_factions):]:
                left_text = " " * 38
                lines.append(left_text + "  " + detail_line)
        
        lines.append("")
        if len(self.faction_list) > visible_count:
            lines.append(f"[{self.current_index + 1}/{len(self.faction_list)}] (Use ↑/↓ to scroll)")
        else:
            lines.append(f"[{self.current_index + 1}/{len(self.faction_list)}]")
        
        return lines
    
    def _render_class_selection(self) -> List[str]:
        """Render class selection screen."""
        lines = []
        lines.append("SELECT YOUR CLASS:")
        lines.append("filtered by background choice...")
        lines.append("")
        
        # Get current class details
        if 0 <= self.current_index < len(self.class_list):
            current_class_name = self.class_list[self.current_index]
            current_class = self.character_classes.get(current_class_name, {})
        else:
            current_class = {}
        
        # Build detail lines for right panel
        detail_lines = []
        if current_class:
            detail_lines.append("│ CLASS DETAILS")
            detail_lines.append("│ " + "─" * 38)
            
            # Description
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
            
            # Primary stats
            primary_stats = current_class.get('primary_stats', [])
            if primary_stats:
                detail_lines.append(f"│ Primary Stats: {', '.join(primary_stats)}")
                detail_lines.append("│")
            
            # Career path
            career = current_class.get('career_path', '')
            if career:
                detail_lines.append(f"│ Career: {career}")
                detail_lines.append("│")
            
            # Starting abilities
            abilities = current_class.get('starting_abilities', [])
            if abilities:
                detail_lines.append("│ Starting Abilities:")
                for ability in abilities[:3]:  # Show first 3
                    detail_lines.append(f"│   - {ability}")
                detail_lines.append("│")
            
            # Starting equipment
            equipment = current_class.get('starting_equipment', [])
            if equipment:
                detail_lines.append("│ Starting Equipment:")
                for item in equipment[:3]:  # Show first 3
                    detail_lines.append(f"│   - {item}")
        
        # Two-column layout with scrolling
        visible_count = 15
        scroll_offset = max(0, self.current_index - visible_count + 5)
        visible_classes = self.class_list[scroll_offset:scroll_offset + visible_count]
        
        for i, char_class in enumerate(visible_classes):
            actual_index = i + scroll_offset
            cursor = ">" if actual_index == self.current_index else " "
            left_text = f"  {cursor} {char_class}"[:38].ljust(38)
            
            # Right side: detail lines
            if i < len(detail_lines):
                right_text = detail_lines[i]
            else:
                right_text = "│"
            
            lines.append(left_text + "  " + right_text)
        
        # Remaining detail lines
        if len(detail_lines) > len(visible_classes):
            for detail_line in detail_lines[len(visible_classes):]:
                left_text = " " * 38
                lines.append(left_text + "  " + detail_line)
        
        lines.append("")
        if len(self.class_list) > visible_count:
            lines.append(f"[{self.current_index + 1}/{len(self.class_list)}] (Use ↑/↓ to scroll)")
        else:
            lines.append(f"[{self.current_index + 1}/{len(self.class_list)}]")
        
        return lines
    
    def _render_stats_display(self) -> List[str]:
        """Render interactive point-buy stat allocation screen."""
        lines = []
        
        if not GAME_AVAILABLE:
            lines.append("Stats calculation unavailable (game modules not loaded).")
            lines.append("")
            lines.append("Press Enter to continue...")
            return lines
        
        try:
            from characters import STAT_NAMES, STAT_DESCRIPTIONS, BASE_STAT_VALUE, POINT_BUY_POINTS, MAX_STAT_VALUE
            
            # Initialize stats if not already set
            if not self.character_data.get('stats'):
                base_stats = create_character_stats()
                # Apply background bonuses
                if self.character_data['background']:
                    bg = self.background_data.get(self.character_data['background'], {})
                    stat_bonuses = bg.get('stat_bonuses', {})
                    for stat, bonus in stat_bonuses.items():
                        if stat in base_stats:
                            base_stats[stat] += bonus
                self.character_data['stats'] = base_stats
                self._selected_stat_index = 0
            
            stats = self.character_data['stats']
            
            # Calculate points
            base_total = BASE_STAT_VALUE * len(STAT_NAMES)
            if self.character_data.get('background'):
                bg = self.background_data.get(self.character_data['background'], {})
                stat_bonuses = bg.get('stat_bonuses', {})
                if stat_bonuses:
                    bg_bonus_total = sum(stat_bonuses.values())
                    base_total += bg_bonus_total
            
            current_total = sum(stats.values())
            allocated_points = current_total - base_total
            remaining_points = POINT_BUY_POINTS - allocated_points
            
            lines.append(f"STATS: {BASE_STAT_VALUE} base + {POINT_BUY_POINTS} pts max | Remaining: {remaining_points} | ↑/↓ select ←/→ adjust")
            
            # Calculate derived stats once for display
            derived = calculate_derived_attributes(stats)
            derived_items = list(derived.items())
            
            # Get selected stat index
            selected_index = getattr(self, '_selected_stat_index', 0)
            stat_codes = list(STAT_NAMES.keys())
            
            # Two-column layout: Stats on left, Derived on right
            lines.append("BASE STATS".ljust(40) + " │ DERIVED METRICS")
            lines.append("─" * 40 + "─┼" + "─" * 38)
            
            # Display stats with derived stats in parallel columns
            max_rows = max(len(stat_codes), len(derived_items))
            
            for i in range(max_rows):
                # Left column: Base stat
                if i < len(stat_codes):
                    stat_code = stat_codes[i]
                    value = stats.get(stat_code, BASE_STAT_VALUE)
                    
                    # Show cursor indicator for selected stat
                    cursor = ">" if i == selected_index else " "
                    
                    # Show if this stat has a background bonus
                    bg_bonus = ""
                    if self.character_data.get('background'):
                        bg = self.background_data.get(self.character_data['background'], {})
                        stat_bonuses = bg.get('stat_bonuses', {})
                        if stat_code in stat_bonuses:
                            bg_bonus = f" (+{stat_bonuses[stat_code]})"
                    
                    # Create stat bar with ASCII characters
                    bar_length = 10
                    filled = min(int((value / MAX_STAT_VALUE) * bar_length), bar_length)
                    bar = "█" * filled + "░" * (bar_length - filled)
                    
                    # Build stat line: cursor + code + value + bar + bonus
                    stat_line = f" {cursor}{stat_code}:{value:3d} [{bar}]{bg_bonus}".ljust(40)
                else:
                    stat_line = " " * 40
                
                # Right column: Derived stat
                if i < len(derived_items):
                    metric_name, metric_value = derived_items[i]
                    metric_info = DERIVED_METRIC_INFO.get(metric_name, {})
                    display_name = metric_info.get('name', metric_name)
                    
                    if isinstance(metric_value, float):
                        if metric_value >= 1000:
                            value_str = f"{metric_value:,.0f}"
                        else:
                            value_str = f"{metric_value:.1f}"
                    else:
                        value_str = str(metric_value)
                    
                    derived_line = f" │ {display_name}: {value_str}"
                else:
                    derived_line = " │"
                
                lines.append(stat_line + derived_line)
            
            # Show description for selected stat (compact, one line)
            if 0 <= selected_index < len(stat_codes):
                stat_code = stat_codes[selected_index]
                stat_name = STAT_NAMES[stat_code]
                desc = STAT_DESCRIPTIONS.get(stat_code, '')
                if desc:
                    # Truncate description if too long
                    desc_short = desc[:75] + "..." if len(desc) > 75 else desc
                    lines.append("─" * 40 + "─┼" + "─" * 38)
                    lines.append(f"{stat_name}: {desc_short}")
            
        except Exception as e:
            import traceback
            lines.append(f"Error calculating stats: {e}")
            lines.append("")
            lines.append("Traceback:")
            for line in traceback.format_exc().split('\n'):
                if line:
                    lines.append(f"  {line}")
            lines.append("")
            print(f"Stats error: {e}")
            traceback.print_exc()
        
        lines.append("")
        lines.append("─" * 80)
        lines.append("Use ↑/↓ to select stat, ←/→ to adjust | Press Enter when done")
        
        return lines
    
    def _render_name_entry(self) -> List[str]:
        """Render name entry screen."""
        lines = []
        lines.append("ENTER YOUR CHARACTER NAME:")
        lines.append("")
        lines.append("Choose a name for your commander.")
        lines.append("")
        lines.append("(Type your name in the text field below and press Enter)")
        
        return lines
    
    def _render_confirmation(self) -> List[str]:
        """Render final confirmation screen."""
        lines = []
        lines.append("CONFIRM YOUR CHARACTER:")
        lines.append("")
        lines.append(f"Species:    {self.character_data['species']}")
        lines.append(f"Background: {self.character_data['background']}")
        lines.append(f"Faction:    {self.character_data['faction']}")
        lines.append(f"Class:      {self.character_data['class']}")
        lines.append(f"Name:       {self.character_data['name']}")
        lines.append("")
        
        # Show stats summary if available
        if self.character_data.get('stats'):
            lines.append("─" * 80)
            lines.append("FINAL STATS:")
            lines.append("")
            
            if GAME_AVAILABLE:
                from characters import STAT_NAMES
                stats = self.character_data['stats']
                stat_codes = list(STAT_NAMES.keys())
                
                # Show stats in two columns
                for i in range(0, len(stat_codes), 2):
                    left_stat = stat_codes[i]
                    left_value = stats.get(left_stat, 30)
                    left_name = STAT_NAMES[left_stat]
                    left_text = f"  {left_stat} ({left_name}): {left_value}".ljust(38)
                    
                    if i + 1 < len(stat_codes):
                        right_stat = stat_codes[i + 1]
                        right_value = stats.get(right_stat, 30)
                        right_name = STAT_NAMES[right_stat]
                        right_text = f"{right_stat} ({right_name}): {right_value}"
                    else:
                        right_text = ""
                    
                    lines.append(left_text + "  " + right_text)
                
                lines.append("")
                
                # Show a few key derived stats
                try:
                    derived = calculate_derived_attributes(stats)
                    lines.append("Key Derived Stats:")
                    lines.append(f"  Health: {derived.get('Health', 0)}")
                    lines.append(f"  Etheric Capacity: {derived.get('Etheric Capacity', 0)}")
                    lines.append(f"  Processing Speed: {derived.get('Processing Speed', 0)}")
                except:
                    pass
            lines.append("")
        
        lines.append("─" * 80)
        lines.append("Press 'Create Character' to begin your journey,")
        lines.append("or 'Previous' to make changes.")
        
        return lines
    
    def _go_next(self) -> None:
        """Advance to next stage."""
        if self.stage == "species":
            # Validate playable species
            selected_species = self.species_list[self.current_index]
            if selected_species not in self.playable_species:
                QMessageBox.warning(
                    self,
                    "Invalid Selection",
                    f"{selected_species} is not a playable species. Please select a playable species."
                )
                return
            
            self.character_data['species'] = selected_species
            self.stage = "background"
            self.current_index = 0
            
        elif self.stage == "background":
            self.character_data['background'] = self.background_list[self.current_index]
            self.stage = "faction"
            self.current_index = 0
            
        elif self.stage == "faction":
            self.character_data['faction'] = self.faction_list[self.current_index]
            # Populate class list based on selected background
            if self.character_data['background']:
                self.class_list = get_available_classes(self.character_data['background'])
                print(f"Filtered to {len(self.class_list)} classes for background: {self.character_data['background']}")
            else:
                self.class_list = list(self.character_classes.keys())
            self.stage = "class"
            self.current_index = 0
            
        elif self.stage == "class":
            self.character_data['class'] = self.class_list[self.current_index]
            self.stage = "stats"
            
        elif self.stage == "stats":
            self.stage = "name"
            self.name_input.show()
            self.name_input.setFocus()
            
        elif self.stage == "name":
            self._handle_name_entry()
            return
            
        elif self.stage == "confirm":
            # Create character and close dialog
            self.accept()
            return
        
        self._update_display()
    
    def _go_previous(self) -> None:
        """Go back to previous stage."""
        if self.stage == "confirm":
            self.stage = "name"
            self.name_input.show()
            self.name_input.setFocus()
        elif self.stage == "name":
            self.stage = "stats"
            self.name_input.hide()
        elif self.stage == "stats":
            self.stage = "class"
            self.current_index = self.class_list.index(self.character_data['class']) if self.character_data['class'] else 0
        elif self.stage == "class":
            self.stage = "faction"
            self.current_index = self.faction_list.index(self.character_data['faction']) if self.character_data['faction'] else 0
        elif self.stage == "faction":
            self.stage = "background"
            self.current_index = self.background_list.index(self.character_data['background']) if self.character_data['background'] else 0
        elif self.stage == "background":
            self.stage = "species"
            self.current_index = self.species_list.index(self.character_data['species']) if self.character_data['species'] else 0
        
        self._update_display()
    
    def _handle_name_entry(self) -> None:
        """Handle name input completion."""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(
                self,
                "Name Required",
                "Please enter a name for your character."
            )
            return
        
        self.character_data['name'] = name
        self.name_input.hide()
        self.stage = "confirm"
        self._update_display()
    
    def _adjust_stat(self, direction: int) -> None:
        """Adjust the currently selected stat by the given direction (+1 or -1)."""
        if not GAME_AVAILABLE:
            return
        
        from characters import STAT_NAMES, BASE_STAT_VALUE, POINT_BUY_POINTS, MAX_STAT_VALUE
        
        if not self.character_data.get('stats'):
            return
        
        # Ensure we have a selected stat index
        if not hasattr(self, '_selected_stat_index'):
            self._selected_stat_index = 0
        
        stats = self.character_data['stats']
        stat_codes = list(STAT_NAMES.keys())
        
        if self._selected_stat_index < 0 or self._selected_stat_index >= len(stat_codes):
            self._selected_stat_index = 0
        
        stat_code = stat_codes[self._selected_stat_index]
        current_value = stats.get(stat_code, BASE_STAT_VALUE)
        
        # Calculate base total (accounting for background bonuses)
        base_total = BASE_STAT_VALUE * len(STAT_NAMES)
        if self.character_data.get('background'):
            bg = self.background_data.get(self.character_data['background'], {})
            stat_bonuses = bg.get('stat_bonuses', {})
            if stat_bonuses:
                bg_bonus_total = sum(stat_bonuses.values())
                base_total += bg_bonus_total
        
        # Calculate minimum value for this stat (including background bonus)
        base_value_for_stat = BASE_STAT_VALUE
        if self.character_data.get('background'):
            bg = self.background_data.get(self.character_data['background'], {})
            stat_bonuses = bg.get('stat_bonuses', {})
            if stat_code in stat_bonuses:
                base_value_for_stat += stat_bonuses[stat_code]
        
        current_total = sum(stats.values())
        allocated_points = current_total - base_total
        remaining_points = POINT_BUY_POINTS - allocated_points
        
        if direction > 0:  # Increase
            if current_value < MAX_STAT_VALUE and remaining_points > 0:
                self.character_data['stats'][stat_code] = current_value + 1
                self._update_display()
            else:
                if current_value >= MAX_STAT_VALUE:
                    QMessageBox.information(self, "Maximum Reached", f"{STAT_NAMES[stat_code]} is at maximum ({MAX_STAT_VALUE})")
                elif remaining_points <= 0:
                    QMessageBox.information(self, "No Points", "No points remaining to allocate")
        elif direction < 0:  # Decrease
            if current_value > base_value_for_stat:
                self.character_data['stats'][stat_code] = current_value - 1
                self._update_display()
            else:
                QMessageBox.information(self, "Minimum Reached", f"{STAT_NAMES[stat_code]} is at minimum ({base_value_for_stat})")



# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------


class RoguelikeMainWindow(QMainWindow):
    """
    Primary application window for the PyQt6 interface.

    Layout:
    -------
    - Central Widget: QPlainTextEdit (ASCII main area: menus, game summaries, maps)
    - Bottom Dock: MessageLogWidget (NetHack-style short log of recent events)
    - Menus:
      * Game: New Game, Load Game, Save Game, Quit
      * View: Galactic History
      * Help: About

    Responsibilities:
    -----------------
    - Maintain a single `Game` instance (or None before a game starts).
    - Render text-based “screens” into the central area:
      - Main menu
      - Basic game overview (for now)
    - Route actions from menus / shortcuts to engine calls:
      - Create new game
      - Load existing game
      - Save current game
    """

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle(" -= 7019 =-")
        self.resize(1200, 800)

        # Reference to active game. None before starting or loading.
        self.game: Optional[Game] = None

        # ------------------------------------------------------------------
        # Central text area (ASCII main view)
        # ------------------------------------------------------------------
        self.main_view = QPlainTextEdit(self)
        self.main_view.setReadOnly(True)
        font = QFont("Menlo")
        font.setStyleHint(QFont.StyleHint.TypeWriter)
        self.main_view.setFont(font)
        self.main_view.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        
        # Terminal-style black background with white text
        self.main_view.setStyleSheet("""
            QPlainTextEdit {
                background-color: #000000;
                color: #FFFFFF;
                border: none;
            }
        """)
        
        self.setCentralWidget(self.main_view)

        # Attach syntax highlighter for colorized ASCII sheets
        try:
            self._sheet_highlighter = ASCIISheetHighlighter(self.main_view.document())
        except Exception:
            self._sheet_highlighter = None

        # ------------------------------------------------------------------
        # Message log dock at the bottom
        # ------------------------------------------------------------------
        self.message_log = MessageLogWidget(self)

        log_dock = QDockWidget("Message Log", self)
        log_dock.setWidget(self.message_log)
        log_dock.setFeatures(
            QDockWidget.DockWidgetFeature.NoDockWidgetFeatures
        )  # fixed position by default
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, log_dock)

        # ------------------------------------------------------------------
        # Status bar
        # ------------------------------------------------------------------
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # ------------------------------------------------------------------
        # Menus and actions
        # ------------------------------------------------------------------
        self._create_actions()
        self._create_menus()
        self._setup_shortcuts()

        # Render initial main menu.
        self.render_main_menu()

    # ------------------------------------------------------------------
    # Menu / action creation
    # ------------------------------------------------------------------

    def _create_actions(self) -> None:
        """Create QAction objects and connect them to handlers."""

        # Game menu actions.
        self.action_new_game = QAction("New Game", self)
        self.action_new_game.triggered.connect(self.on_new_game)

        self.action_load_game = QAction("Load Game", self)
        self.action_load_game.triggered.connect(self.on_load_game)

        self.action_save_game = QAction("Save Game", self)
        self.action_save_game.triggered.connect(self.on_save_game)

        self.action_quit = QAction("Quit", self)
        self.action_quit.triggered.connect(self.close)

        # View menu actions.
        self.action_view_history = QAction("Galactic History", self)
        self.action_view_history.triggered.connect(self.on_view_history)
        
        self.action_character_sheet = QAction("Character Sheet", self)
        self.action_character_sheet.triggered.connect(self.on_character_sheet)
        
        self.action_ship_status = QAction("Ship Status", self)
        self.action_ship_status.triggered.connect(self.on_ship_status)
        
        self.action_map = QAction("Galaxy Map", self)
        self.action_map.triggered.connect(self.on_map)
        
        self.action_overview = QAction("Overview", self)
        self.action_overview.triggered.connect(self.on_overview)

        # Help menu actions.
        self.action_about = QAction("About", self)
        self.action_about.triggered.connect(self.on_about)

    def _create_menus(self) -> None:
        """Wire actions into the menu bar structure."""

        menu_game = self.menuBar().addMenu("&Game")
        menu_game.addAction(self.action_new_game)
        menu_game.addAction(self.action_load_game)
        menu_game.addAction(self.action_save_game)
        menu_game.addSeparator()
        menu_game.addAction(self.action_quit)

        menu_view = self.menuBar().addMenu("&View")
        menu_view.addAction(self.action_overview)
        menu_view.addAction(self.action_view_history)
        menu_view.addAction(self.action_character_sheet)
        menu_view.addAction(self.action_ship_status)
        menu_view.addAction(self.action_map)

        menu_help = self.menuBar().addMenu("&Help")
        menu_help.addAction(self.action_about)

    def _setup_shortcuts(self) -> None:
        """
        Define keyboard shortcuts that mimic a roguelike-style workflow.

        Examples:
        ---------
        - N: New Game
        - L: Load Game
        - S: Save Game
        - H: View Galactic History
        - Q: Quit
        """
        self.action_new_game.setShortcut("N")
        self.action_load_game.setShortcut("L")
        self.action_save_game.setShortcut("S")
        self.action_overview.setShortcut("O")
        self.action_view_history.setShortcut("H")
        self.action_character_sheet.setShortcut("C")
        self.action_ship_status.setShortcut("V")
        self.action_map.setShortcut("M")
        self.action_quit.setShortcut("Q")

    # ------------------------------------------------------------------
    # Rendering helpers
    # ------------------------------------------------------------------

    def render_main_menu(self) -> None:
        """
        Render the ASCII main menu screen into the central text area.

        This is intentionally reminiscent of NetHack-style splash menus,
        with heavy box characters and a simple choices list. The actual
        interactions are handled via menus and shortcuts, not by typing
        letters at a prompt.
        """
        # Calculate width based on viewport and font metrics
        fm = self.main_view.fontMetrics()
        char_width = fm.horizontalAdvance('=')  # Use a typical character
        viewport_width = self.main_view.viewport().width()
        # Account for margins and scrollbar
        usable_width = viewport_width - 20  # Subtract some pixels for margins
        width = max(80, usable_width // char_width)
        
        lines: List[str] = []
        lines.append("═" * width)
        lines.append(" GALACTIC EMPIRE 4X ".center(width, " "))
        lines.append("═" * width)
        lines.append("")
        lines.append("  7019 • Mind Your Assumptions".center(width))
        lines.append("")
        lines.append("  MAIN MENU".center(width))
        lines.append("")
        lines.append("   [N] New Game")
        lines.append("   [L] Load Game")
        lines.append("   [S] Save Game (if a game is active)")
        lines.append("   [C] Character Sheet (if a game is active)")
        lines.append("   [V] Vessel Status (if a game is active)")
        lines.append("   [M] Galaxy Map (if a game is active)")
        lines.append("   [H] View Galactic History")
        lines.append("   [Q] Quit")
        lines.append("")
        lines.append("─" * width)
        lines.append("Use menu entries or shortcuts: N, L, S, C, V, H, Q.".center(width))
        lines.append("")

        self.main_view.setPlainText("\n".join(lines))
        self.status_bar.showMessage("Main menu")

    def render_game_overview(self) -> None:
        """
        Render a basic ASCII overview of the current game state.

        NOTE:
        -----
        This method is deliberately conservative because we do not introspect
        the full structure of `Game` here (and that structure may evolve).
        It uses `getattr` with sensible fallbacks to avoid breaking if
        attributes are absent.

        You can and *should* extend this to show:
        - Assets (ships, stations, platforms)
        - Current system, navigation data
        - Credits, turn, fuel, cargo, etc.
        - Any narrative / event hooks you care about

        The goal is to keep all layout and ASCII formatting here, and all
        data/logic inside the `Game` object.
        """
        if not self.game:
            self.main_view.setPlainText("No active game. Use New or Load to begin.")
            return

        # Safely extract a few often-used fields from the Game instance.
        player_name = getattr(self.game, "player_name", "Unknown Commander")
        player_species = getattr(self.game, "species", "Unknown Species")
        character_class = getattr(self.game, "character_class", "Unknown Class")
        credits = getattr(self.game, "credits", 0)
        turn = getattr(self.game, "turn", 0)

        # Calculate width based on viewport and font metrics
        fm = self.main_view.fontMetrics()
        char_width = fm.horizontalAdvance('=')  # Use a typical character
        viewport_width = self.main_view.viewport().width()
        # Account for margins and scrollbar
        usable_width = viewport_width - 20  # Subtract some pixels for margins
        width = max(80, usable_width // char_width)
        
        lines: List[str] = []
        lines.append("═" * width)
        lines.append(f" COMMANDER OVERVIEW ".center(width))
        lines.append("═" * width)
        lines.append("")
        lines.append(f" Name   : {player_name}")
        lines.append(f" Species: {player_species}")
        lines.append(f" Class  : {character_class}")
        lines.append("")
        lines.append(f" Credits: {credits:,}")
        lines.append(f" Turn   : {turn}")
        lines.append("")
        lines.append("─" * width)
        lines.append(" (This is a minimal overview. Extend `render_game_overview`")
        lines.append("  to display ships, stations, inventory, navigation, etc.)")
        lines.append("─" * width)
        lines.append("")
        lines.append("Use the Game menu or keyboard shortcuts to continue.".center(width))
        lines.append(" [N] New Game | [L] Load Game | [S] Save Game ".center(width))
        lines.append(" [C] Character Sheet | [V] Vessel Status | [H] History | [O] Overview ".center(width))
        lines.append("")

        self.main_view.setPlainText("\n".join(lines))
        self.status_bar.showMessage("Game overview")

    # ------------------------------------------------------------------
    # Menu action handlers
    # ------------------------------------------------------------------

    def on_new_game(self) -> None:
        """
        Handler for "New Game" action.

        Behaviour:
        ----------
        - Opens the character creation dialog
        - If user completes character creation, creates a new game with those choices
        - Renders the game overview
        """
        if not GAME_AVAILABLE:
            QMessageBox.critical(
                self,
                "Game Engine Not Available",
                "The game modules could not be imported. "
                "Make sure you run this inside the 4x_game project.",
            )
            return

        # Show character creation dialog
        dlg = CharacterCreationDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            # User cancelled
            return
        
        # Create game with character data
        self.game = Game()
        
        # Apply character choices to the game
        # (The Game class uses character_species, character_background, character_faction)
        self.game.character_species = dlg.character_data['species']
        self.game.character_background = dlg.character_data['background']
        self.game.character_faction = dlg.character_data['faction']
        self.game.character_class = dlg.character_data['class']
        self.game.player_name = dlg.character_data['name']
        # Persist allocated stats if available
        if dlg.character_data.get('stats'):
            self.game.character_stats = dlg.character_data['stats']
        
        self.message_log.add_message(
            f"New game started: {dlg.character_data['name']}, "
            f"{dlg.character_data['class']} ({dlg.character_data['species']})",
            "[GAME]"
        )
        self.render_game_overview()

    def on_load_game(self) -> None:
        """
        Handler for "Load Game" action.

        Behaviour:
        ----------
        - Open the LoadGameDialog.
        - If the user cancels, do nothing.
        - If the user selects a save:
          * Create a `Game` instance if none exists.
          * Call `load_game(self.game, selected.path)`.
          * On success: render overview and log success.
          * On failure: show error and keep old game (if any).
        """
        if not GAME_AVAILABLE:
            QMessageBox.critical(
                self,
                "Game Engine Not Available",
                "The game modules could not be imported; cannot load saves.",
            )
            return

        dlg = LoadGameDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted or dlg.selected_save is None:
            # User cancelled or no valid selection.
            return

        selected = dlg.selected_save
        # Ensure we have a Game instance to load into.
        if self.game is None:
            self.game = Game()

        loaded_ok = False
        try:
            loaded_ok = load_game(self.game, selected.path)
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Load Failed",
                f"An error occurred while loading the game:\n{exc}",
            )
            return

        if loaded_ok:
            self.message_log.add_message(
                f"Loaded save '{selected.name}' for player {selected.player_name}.",
                "[LOAD]",
            )
            self.render_game_overview()
        else:
            QMessageBox.warning(
                self,
                "Load Failed",
                "The save file could not be loaded. Please verify it is valid.",
            )

    def on_save_game(self) -> None:
        """
        Handler for "Save Game" action.

        Behaviour:
        ----------
        - If there is no active game, show a warning.
        - If the engine is unavailable, show an error.
        - Otherwise, call `save_game(self.game)` and log the result.
        - For now we do not ask for a custom save name in the GUI; we rely
          on the `save_game` function’s default naming behaviour. You can
          extend this by popping up a QInputDialog to capture a name.
        """
        if not GAME_AVAILABLE:
            QMessageBox.critical(
                self,
                "Game Engine Not Available",
                "The game modules could not be imported; cannot save.",
            )
            return

        if self.game is None:
            QMessageBox.warning(
                self,
                "No Active Game",
                "There is no active game to save. Start or load a game first.",
            )
            return

        try:
            ok = save_game(self.game)
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Save Failed",
                f"An error occurred while saving the game:\n{exc}",
            )
            return

        if ok:
            self.message_log.add_message("Game saved successfully.", "[SAVE]")
        else:
            QMessageBox.warning(
                self,
                "Save Failed",
                "The save operation did not report success. "
                "Check the save_game implementation.",
            )

    def on_view_history(self) -> None:
        """
        Handler for "Galactic History" action.

        Opens a modal dialog that shows the procedurally generated history.
        """
        dlg = GalacticHistoryDialog(self)
        dlg.exec()

    def on_character_sheet(self) -> None:
        """
        Handler for "Character Sheet" action.
        
        Shows detailed character information including stats, background, class, etc.
        """
        if not self.game:
            QMessageBox.warning(
                self,
                "No Active Game",
                "There is no active game. Start or load a game first.",
            )
            return
        
        self.render_character_sheet()
        self.message_log.add_message("Character sheet displayed. Press Overview (O) to return.", "[VIEW]")

    def on_overview(self) -> None:
        """Handler for returning to game overview."""
        if self.game:
            self.render_game_overview()
            self.message_log.add_message("Returned to overview.", "[VIEW]")
        else:
            self.render_main_menu()

    def render_character_sheet(self) -> None:
        """Render a detailed character sheet similar to nethack_interface style."""
        if not self.game:
            self.main_view.setPlainText("No active game.")
            return
        
        # Calculate width - use most of the available viewport width
        fm = self.main_view.fontMetrics()
        char_width = fm.horizontalAdvance('M')  # Use M for more accurate width
        viewport_width = self.main_view.viewport().width()
        usable_width = viewport_width - 40  # Leave some margin
        width = max(120, usable_width // char_width)  # Minimum 120 chars, expand to fit window
        
        inner_width = width - 4
        left_width = (inner_width - 3) // 2
        right_width = inner_width - left_width - 3
        
        def fmt_line(text: str = "") -> str:
            trimmed = text[:inner_width]
            return f"║ {trimmed.ljust(inner_width)} ║"
        
        def fmt_center(text: str) -> str:
            trimmed = text[:inner_width]
            return f"║{trimmed.center(inner_width + 2)}║"
        
        def fmt_two_col(left: str, right: str) -> str:
            left_trimmed = left[:left_width]
            right_trimmed = right[:right_width]
            content = f"{left_trimmed.ljust(left_width)} │ {right_trimmed.ljust(right_width)}"
            return f"║ {content} ║"
        
        # Gather character data
        name = getattr(self.game, 'player_name', '—')
        species_name = getattr(self.game, 'character_species', '—')
        class_name = getattr(self.game, 'character_class', '—')
        background_name = getattr(self.game, 'character_background', '—')
        faction_name = getattr(self.game, 'character_faction', '—')
        
        credits = getattr(self.game, 'credits', 0)
        turn = getattr(self.game, 'turn', 0)
        level = getattr(self.game, 'level', 1)
        
        # Get stats from game object (Game stores stats in character_stats)
        stats = getattr(self.game, 'character_stats', {}) or {}
        derived = {}
        
        # Build the sheet
        lines = []
        lines.append("╔" + "═" * (inner_width + 2) + "╗")
        lines.append(fmt_center("CHARACTER SHEET"))
        lines.append("╠" + "═" * (inner_width + 2) + "╣")
        lines.append(fmt_center("IDENTITY & ORIGINS"))
        lines.append("╟" + "─" * (inner_width + 2) + "╢")
        
        # Identity section
        identity_data = [
            (f"Name: {name}", f"Species: {species_name}"),
            (f"Class: {class_name}", f"Background: {background_name}"),
            (f"Faction: {faction_name}", f"Level: {level}"),
            (f"Credits: {credits:,}", f"Turn: {turn}"),
        ]
        
        for left, right in identity_data:
            lines.append(fmt_two_col(left, right))
        
        lines.append(fmt_line())
        lines.append("╠" + "═" * (inner_width + 2) + "╣")
        lines.append(fmt_center("ATTRIBUTES"))
        lines.append("╟" + "─" * (inner_width + 2) + "╢")
        
        # Stats section (two columns: base stats | derived stats)
        if GAME_AVAILABLE:
            from characters import STAT_NAMES, BASE_STAT_VALUE
            
            # Shorten stat names to fit better
            stat_name_map = {
                'VIT': 'Vitality',
                'KIN': 'Kinetics',
                'INT': 'Intellect',
                'AEF': 'Aetheric Aff',  # Shortened
                'COH': 'Coherence',
                'INF': 'Influence',
                'SYN': 'Synthesis'
            }
            
            # Use effective stats for display and derived calculations
            stat_codes = ['VIT', 'KIN', 'INT', 'AEF', 'COH', 'INF', 'SYN']
            effective_stats = stats if stats else {code: BASE_STAT_VALUE for code in stat_codes}

            stat_lines = []
            for code in stat_codes:
                stat_name = stat_name_map.get(code, STAT_NAMES.get(code, code))
                value = effective_stats.get(code, BASE_STAT_VALUE)
                stat_lines.append(f"{code} {stat_name:<13} {value:>3}")
            
            # Compute derived attributes from effective stats
            derived = calculate_derived_attributes(effective_stats)

            # Pair derived attributes with base stats on the same row using a fixed order
            derived_order = [
                "Health",
                "Etheric Capacity",
                "Processing Speed",
                "Adaptation Index",
                "Resilience Index",
                "Innovation Quotient",
                "Etheric Stability",
            ]

            def fmt_derived(name: str, value) -> str:
                if isinstance(value, float):
                    if value >= 1000:
                        value_str = f"{value:,.0f}"
                    else:
                        value_str = f"{value:.1f}"
                else:
                    value_str = str(value)
                name_short = name[:18]
                return f"{name_short:<18} {value_str}"

            # Build derived lines in desired order (pad/truncate to match base stats)
            ordered_values = [fmt_derived(n, derived.get(n, "")) for n in derived_order]
            # Ensure we have at least as many derived entries as base stats
            while len(ordered_values) < len(stat_lines):
                ordered_values.append("")

            for i in range(len(stat_lines)):
                left = stat_lines[i]
                right = ordered_values[i]
                lines.append(fmt_two_col(left, right))
        else:
            lines.append(fmt_line("Stats unavailable (game modules not loaded)"))
        
        # Background & Class info
        lines.append(fmt_line())
        lines.append("╠" + "═" * (inner_width + 2) + "╣")
        lines.append(fmt_center("BACKGROUND & CLASS"))
        lines.append("╟" + "─" * (inner_width + 2) + "╢")
        
        if GAME_AVAILABLE and background_name != '—':
            from backgrounds import backgrounds as background_data
            from classes import classes
            
            bg_info = background_data.get(background_name, {})
            class_info = classes.get(class_name, {})
            faction_info = factions.get(faction_name, {})
            
            if bg_info:
                bg_desc = bg_info.get('description', '')
                if bg_desc:
                    wrapped = textwrap.wrap(bg_desc, width=inner_width - 2)
                    lines.append(fmt_line(f"Background: {background_name}"))
                    for line in wrapped:
                        lines.append(fmt_line(f"  {line}"))
                    lines.append(fmt_line())
            
            if class_info:
                class_desc = class_info.get('description', '')
                career = class_info.get('career_path', '')
                if class_desc:
                    wrapped = textwrap.wrap(class_desc, width=inner_width - 2)
                    lines.append(fmt_line(f"Class: {class_name}"))
                    for line in wrapped:
                        lines.append(fmt_line(f"  {line}"))
                    if career:
                        lines.append(fmt_line(f"  Career: {career}"))
                    lines.append(fmt_line())
            
            if faction_info and faction_name != '—':
                faction_desc = faction_info.get('description', '')
                philosophy = faction_info.get('philosophy', '')
                gov_type = faction_info.get('government_type', '')
                primary_focus = faction_info.get('primary_focus', '')
                
                lines.append(fmt_line(f"Faction: {faction_name}"))
                if philosophy:
                    lines.append(fmt_line(f"  Philosophy: {philosophy}"))
                if gov_type:
                    lines.append(fmt_line(f"  Government: {gov_type}"))
                if primary_focus:
                    lines.append(fmt_line(f"  Focus: {primary_focus}"))
                if faction_desc:
                    wrapped = textwrap.wrap(faction_desc, width=inner_width - 2)
                    for line in wrapped:
                        lines.append(fmt_line(f"  {line}"))
        else:
            lines.append(fmt_line("No background/class information available"))
        
        # Assets section
        lines.append(fmt_line())
        lines.append("╠" + "═" * (inner_width + 2) + "╣")
        lines.append(fmt_center("FLEET & HOLDINGS"))
        lines.append("╟" + "─" * (inner_width + 2) + "╢")
        
        ships = []
        try:
            ships.extend(getattr(self.game, "owned_ships", []) or [])
            custom = getattr(self.game, "custom_ships", []) or []
            for ship in custom:
                if isinstance(ship, dict):
                    ships.append(ship.get("name", "Custom Ship"))
                else:
                    ships.append(str(ship))
        except:
            pass
        
        stations = getattr(self.game, "owned_stations", []) or []
        platforms = getattr(self.game, "owned_platforms", []) or []
        
        fleet_left = ["Ships:"]
        if ships:
            for ship in ships[:5]:  # Show first 5
                fleet_left.append(f"  • {ship}")
            if len(ships) > 5:
                fleet_left.append(f"  … plus {len(ships) - 5} more")
        else:
            fleet_left.append("  • None")
        
        holdings = ["Installations:"]
        if stations:
            for station in stations[:3]:
                holdings.append(f"  • {station}")
        if platforms:
            for platform in platforms[:2]:
                holdings.append(f"  • {platform}")
        if not stations and not platforms:
            holdings.append("  • None")
        
        max_rows = max(len(fleet_left), len(holdings))
        for i in range(max_rows):
            left = fleet_left[i] if i < len(fleet_left) else ""
            right = holdings[i] if i < len(holdings) else ""
            lines.append(fmt_two_col(left, right))
        
        # Equipment section
        lines.append(fmt_line())
        lines.append("╠" + "═" * (inner_width + 2) + "╣")
        lines.append(fmt_center("EQUIPMENT"))
        lines.append("╟" + "─" * (inner_width + 2) + "╢")
        
        equipment = getattr(self.game, "equipment", {}) or {}
        if equipment:
            for slot, item in list(equipment.items())[:6]:
                lines.append(fmt_line(f"  {slot}: {item}"))
        else:
            lines.append(fmt_line("  No equipment equipped (not yet implemented)"))
        
        lines.append("╚" + "═" * (inner_width + 2) + "╝")
        lines.append("")
        lines.append("[Press O to return to overview]".center(width))
        
        self.main_view.setPlainText("\n".join(lines))
        self.status_bar.showMessage("Character Sheet | Press O to return")

    def on_ship_status(self) -> None:
        """
        Handler for "Ship Status" action.
        
        Shows detailed ship information including components, cargo, fuel, crew, etc.
        """
        if not self.game:
            QMessageBox.warning(
                self,
                "No Active Game",
                "There is no active game. Start or load a game first.",
            )
            return
        
        self.render_ship_status()
        self.message_log.add_message("Ship status displayed. Press Overview (O) to return.", "[VIEW]")

    def render_ship_status(self) -> None:
        """Render a detailed ship status screen similar to character sheet style."""
        if not self.game:
            self.main_view.setPlainText("No active game.")
            return
        
        # Get navigation system and current ship
        nav = getattr(self.game, 'navigation', None)
        ship = nav.current_ship if nav else None
        
        if not ship:
            self.main_view.setPlainText("No active ship.")
            return
        
        # Calculate width - use most of the available viewport width
        fm = self.main_view.fontMetrics()
        char_width = fm.horizontalAdvance('M')
        viewport_width = self.main_view.viewport().width()
        usable_width = viewport_width - 40
        width = max(120, usable_width // char_width)
        
        inner_width = width - 4
        left_width = (inner_width - 3) // 2
        right_width = inner_width - left_width - 3
        
        def fmt_line(text: str = "") -> str:
            trimmed = text[:inner_width]
            return f"║ {trimmed.ljust(inner_width)} ║"
        
        def fmt_center(text: str) -> str:
            trimmed = text[:inner_width]
            return f"║{trimmed.center(inner_width + 2)}║"
        
        def fmt_two_col(left: str, right: str) -> str:
            left_trimmed = left[:left_width]
            right_trimmed = right[:right_width]
            content = f"{left_trimmed.ljust(left_width)} │ {right_trimmed.ljust(right_width)}"
            return f"║ {content} ║"
        
        # Build the sheet
        lines = []
        lines.append("╔" + "═" * (inner_width + 2) + "╗")
        lines.append(fmt_center("SHIP STATUS"))
        lines.append("╠" + "═" * (inner_width + 2) + "╣")
        lines.append(fmt_center("VESSEL IDENTIFICATION"))
        lines.append("╟" + "─" * (inner_width + 2) + "╢")
        
        # Ship identity
        ship_name = ship.name
        ship_class = ship.ship_class
        sx, sy, sz = ship.coordinates
        
        identity_data = [
            (f"Name: {ship_name}", f"Class: {ship_class}"),
            (f"Location: ({sx}, {sy}, {sz})", f"Scan Range: {ship.scan_range}"),
        ]
        
        for left, right in identity_data:
            lines.append(fmt_two_col(left, right))
        
        # Resources
        lines.append(fmt_line())
        lines.append("╠" + "═" * (inner_width + 2) + "╣")
        lines.append(fmt_center("RESOURCES"))
        lines.append("╟" + "─" * (inner_width + 2) + "╢")
        
        # Fuel status
        fuel_pct = (ship.fuel / ship.max_fuel * 100) if ship.max_fuel > 0 else 0
        fuel_bar_width = 30
        fuel_filled = int(fuel_bar_width * fuel_pct / 100)
        fuel_bar = "█" * fuel_filled + "░" * (fuel_bar_width - fuel_filled)
        
        lines.append(fmt_two_col(
            f"Fuel: {ship.fuel}/{ship.max_fuel} ({fuel_pct:.1f}%)",
            f"Range: {ship.jump_range} units"
        ))
        lines.append(fmt_line(f"  [{fuel_bar}]"))
        lines.append(fmt_line())
        
        # Cargo status
        cargo_used = sum(ship.cargo.values()) if ship.cargo else 0
        cargo_pct = (cargo_used / ship.max_cargo * 100) if ship.max_cargo > 0 else 0
        cargo_bar_width = 30
        cargo_filled = int(cargo_bar_width * cargo_pct / 100)
        cargo_bar = "█" * cargo_filled + "░" * (cargo_bar_width - cargo_filled)
        
        lines.append(fmt_two_col(
            f"Cargo: {cargo_used}/{ship.max_cargo} units ({cargo_pct:.1f}%)",
            f"Items: {len(ship.cargo)} types"
        ))
        lines.append(fmt_line(f"  [{cargo_bar}]"))
        
        # Cargo manifest
        if ship.cargo:
            lines.append(fmt_line())
            lines.append(fmt_line("Cargo Manifest:"))
            for item, qty in list(ship.cargo.items())[:10]:
                lines.append(fmt_line(f"  • {item}: {qty}"))
            if len(ship.cargo) > 10:
                lines.append(fmt_line(f"  ... and {len(ship.cargo) - 10} more items"))
        
        # Components
        lines.append(fmt_line())
        lines.append("╠" + "═" * (inner_width + 2) + "╣")
        lines.append(fmt_center("SHIP COMPONENTS"))
        lines.append("╟" + "─" * (inner_width + 2) + "╢")
        
        components = getattr(ship, 'components', {})
        if components:
            component_order = ['hull', 'engine', 'weapons', 'shields', 'sensors', 'support']
            for comp_type in component_order:
                comp_value = components.get(comp_type)
                if comp_value:
                    if isinstance(comp_value, list):
                        lines.append(fmt_line(f"{comp_type.capitalize()}:"))
                        for item in comp_value:
                            lines.append(fmt_line(f"  • {item}"))
                    else:
                        lines.append(fmt_line(f"{comp_type.capitalize()}: {comp_value}"))
        else:
            lines.append(fmt_line("No component data available"))
        
        # Crew
        lines.append(fmt_line())
        lines.append("╠" + "═" * (inner_width + 2) + "╣")
        lines.append(fmt_center("CREW COMPLEMENT"))
        lines.append("╟" + "─" * (inner_width + 2) + "╢")
        
        crew = getattr(ship, 'crew', [])
        max_crew = getattr(ship, 'max_crew', 10)
        
        lines.append(fmt_two_col(
            f"Crew: {len(crew)}/{max_crew}",
            f"Morale: Good"  # Placeholder
        ))
        
        if crew:
            lines.append(fmt_line())
            lines.append(fmt_line("Crew Roster:"))
            for member in crew[:15]:
                name = member.name if hasattr(member, 'name') else str(member)
                role = member.role if hasattr(member, 'role') else "Crew"
                lines.append(fmt_line(f"  • {name} - {role}"))
            if len(crew) > 15:
                lines.append(fmt_line(f"  ... and {len(crew) - 15} more crew members"))
        else:
            lines.append(fmt_line("  No crew assigned"))
        
        lines.append("")
        lines.append("╚" + "═" * (inner_width + 2) + "╝")
        lines.append("")
        lines.append("[Press O to return to overview]".center(width))
        
        self.main_view.setPlainText("\n".join(lines))
        self.status_bar.showMessage("Ship Status | Press O to return")

    def on_map(self) -> None:
        """
        Handler for "Galaxy Map" action.
        
        Opens the full-screen galaxy map with navigation capabilities.
        """
        if not self.game:
            QMessageBox.warning(
                self,
                "No Active Game",
                "There is no active game. Start or load a game first.",
            )
            return
        
        # Ensure navigation system is initialized
        if not hasattr(self.game, 'navigation') or not self.game.navigation:
            QMessageBox.warning(
                self,
                "Navigation Unavailable",
                "Navigation system not initialized.",
            )
            return
        
        # Open map screen
        map_screen = MapScreen(self.game, self)
        map_screen.exec()
        
        # Refresh overview after closing map
        if self.game:
            self.render_game_overview()
            self.message_log.add_message("Returned from galaxy map.", "[VIEW]")

    def on_about(self) -> None:
        """
        Show an About dialog with basic information.
        """
        text = textwrap.dedent(
            """
            4X Galactic Empire (PyQt6 Roguelike UI)
            ---------------------------------------
            This interface is designed to keep the feel of a classic
            ASCII roguelike while providing a modern desktop GUI.

            - Engine:  4x_game (Python)
            - UI:      PyQt6
            - Style:   NetHack-inspired, keyboard-friendly

            Controls:
              • N: New Game
              • L: Load Game
              • S: Save Game
              • O: Overview
              • C: Character Sheet
              • H: Galactic History
              • Q: Quit
            """
        ).strip()

        QMessageBox.information(self, "About", text)

    # ------------------------------------------------------------------
    # Optional: override sizeHint to suggest a good default size
    # ------------------------------------------------------------------

    def sizeHint(self) -> QSize:  # type: ignore[override]
        return QSize(1200, 800)

    def showEvent(self, event) -> None:  # type: ignore[override]
        """Re-render after window is shown to get accurate viewport size."""
        super().showEvent(event)
        # Render with correct viewport width now that window is visible
        if self.game is None:
            self.render_main_menu()
        else:
            self.render_game_overview()

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        """Re-render content when window is resized to adjust width."""
        super().resizeEvent(event)
        # Re-render the current view to adjust to new width
        if self.game is None:
            self.render_main_menu()
        else:
            self.render_game_overview()


# ---------------------------------------------------------------------------
# Galaxy Map Screen
# ---------------------------------------------------------------------------


class MapScreen(QDialog):
    """
    Full-screen Galaxy Map with ASCII visualization.
    
    Features:
    - Virtual map 200x60, viewport 120x35 with scrolling
    - Faction zone overlay (F key)
    - Ether energy visualization (E key)
    - HJKL/arrow navigation with fuel consumption
    - Scanning range for nearby objects
    - NPC ship movement and encounters
    """
    
    def __init__(self, game, parent=None):
        super().__init__(parent)
        self.game = game
        self.setWindowTitle("Galaxy Map")
        self.setModal(False)
        
        # Viewport and virtual map dimensions
        self.viewport_width = 120
        self.viewport_height = 35
        self.virtual_width = 200
        self.virtual_height = 60
        
        # Viewport offset (camera position)
        self.viewport_x = 0
        self.viewport_y = 0
        
        # Toggles
        self.show_faction_zones = False
        self.show_ether_energy = False
        
        # Faction color mapping
        self.faction_colors = {}
        
        # Fuel recharge tracking
        self.fuel_recharge_counter = 0
        self.fuel_recharge_target = 3
        
        # Move counter for events
        self.move_count = 0
        
        # Setup UI
        self.init_ui()
        
        # Ensure navigation system has a ship
        self.ensure_ship()
        
        # Initial render
        self.update_map()
        
    def init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout()
        
        # Map display
        self.map_display = QPlainTextEdit()
        self.map_display.setReadOnly(True)
        self.map_display.setFont(QFont("Menlo", 10))
        
        # Apply dark terminal styling
        palette = self.map_display.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor("#000000"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#FFFFFF"))
        self.map_display.setPalette(palette)
        
        # Install syntax highlighter for colors
        self.highlighter = MapHighlighter(self.map_display.document())
        
        layout.addWidget(self.map_display)
        
        # Status bar with instructions
        self.status_label = QLabel(
            "[HJKL/Arrows: Move] [F: Faction Zones] [E: Ether Energy] "
            "[N: News] [H: History] [Q/ESC: Close]"
        )
        self.status_label.setStyleSheet("color: #808080; padding: 5px;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # Make it large
        self.resize(1400, 900)
        
        # Ensure this dialog receives key events even if the text area is focused
        self.map_display.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
    def ensure_ship(self):
        """Ensure navigation system has a current ship."""
        try:
            if hasattr(self.game, 'navigation') and self.game.navigation:
                if not self.game.navigation.current_ship:
                    from navigation import Ship
                    first_ship = self.game.owned_ships[0] if self.game.owned_ships else "Basic Transport"
                    self.game.navigation.current_ship = Ship(first_ship, first_ship)
        except Exception as e:
            print(f"Error ensuring ship: {e}")
    
    def update_map(self):
        """Render the galaxy map."""
        nav = getattr(self.game, 'navigation', None)
        if not nav or not nav.galaxy:
            self.map_display.setPlainText("Galaxy data unavailable")
            return
        
        galaxy = nav.galaxy
        ship = nav.current_ship
        
        if not ship:
            self.map_display.setPlainText("No ship available")
            return
        
        # Initialize virtual buffer - store (char, system_data, faction_name) tuples
        virtual_buf = [[(" ", None, None) for _ in range(self.virtual_width)] 
                       for _ in range(self.virtual_height)]
        
        def project(x, y):
            """Scale galaxy coordinates to virtual map coordinates."""
            px = int((x / galaxy.size_x) * (self.virtual_width - 1))
            py = int((y / galaxy.size_y) * (self.virtual_height - 1))
            px = max(0, min(self.virtual_width - 1, px))
            py = max(0, min(self.virtual_height - 1, py))
            return px, py
        
        # Draw faction zone backgrounds if enabled
        if self.show_faction_zones and hasattr(galaxy, 'faction_zones'):
            from systems import FACTION_COLORS
            
            # Build faction color mapping
            available_colors = [
                "blue", "red", "green", "magenta", "cyan",
                "yellow", "bright_blue", "bright_red", "bright_green",
                "bright_magenta", "bright_cyan"
            ]
            for idx, faction_name in enumerate(galaxy.faction_zones.keys()):
                if faction_name in FACTION_COLORS:
                    self.faction_colors[faction_name] = FACTION_COLORS[faction_name]
                else:
                    self.faction_colors[faction_name] = available_colors[idx % len(available_colors)]
            
            # Fill faction backgrounds
            for py in range(self.virtual_height):
                for px in range(self.virtual_width):
                    gx = int((px / (self.virtual_width - 1)) * galaxy.size_x)
                    gy = int((py / (self.virtual_height - 1)) * galaxy.size_y)
                    gz = galaxy.size_z / 2
                    
                    faction = galaxy.get_faction_for_location(gx, gy, gz) if hasattr(galaxy, 'get_faction_for_location') else None
                    
                    if faction:
                        virtual_buf[py][px] = ("░", None, faction)
        
        # Draw ether energy overlay if enabled
        if self.show_ether_energy and hasattr(galaxy, 'ether_energy') and galaxy.ether_energy:
            for py in range(self.virtual_height):
                for px in range(self.virtual_width):
                    gx = int((px / (self.virtual_width - 1)) * galaxy.size_x)
                    gy = int((py / (self.virtual_height - 1)) * galaxy.size_y)
                    gz = int(galaxy.size_z / 2)
                    
                    friction = galaxy.ether_energy.get_friction_at(gx, gy, gz)
                    
                    # Determine symbol based on friction
                    if friction < 0.85:
                        dot_char = "·"
                        dot_color = "bright_green" if friction < 0.7 else "green"
                    elif friction < 0.95:
                        dot_char = "·"
                        dot_color = "cyan"
                    elif friction < 1.05:
                        dot_char = "·"
                        dot_color = "dim_white"
                    elif friction < 1.3:
                        dot_char = "·"
                        dot_color = "yellow"
                    elif friction < 1.6:
                        dot_char = "·"
                        dot_color = "bright_yellow"
                    else:
                        dot_char = "·"
                        dot_color = "red" if friction < 2.0 else "bright_red"
                    
                    current_char, current_data, current_faction = virtual_buf[py][px]
                    if current_char in (" ", ".", "░"):
                        virtual_buf[py][px] = (dot_char, {"ether_friction": friction, "ether_color": dot_color}, None)
        
        # Get scanned systems
        scanned_systems = set()
        if ship and hasattr(ship, 'get_objects_in_scan_range'):
            try:
                scan_results = ship.get_objects_in_scan_range(galaxy)
                for obj_type, obj_data, distance in scan_results:
                    if obj_type == 'system':
                        scanned_systems.add(obj_data['name'])
            except Exception:
                pass
        
        # Plot systems
        for sys in galaxy.systems.values():
            x, y, _ = sys["coordinates"]
            px, py = project(x, y)
            
            has_stations = sys.get("stations") and len(sys.get("stations", [])) > 0
            if has_stations:
                ch = "◈" if sys.get("visited") else "◆"
            else:
                ch = "*" if sys.get("visited") else "+"
            
            faction = sys.get('controlling_faction')
            virtual_buf[py][px] = (ch, sys, faction)
            
            # Add scan icons below systems
            if sys['name'] in scanned_systems and py + 1 < self.virtual_height:
                icons = []
                bodies = sys.get('celestial_bodies', [])
                planets = [b for b in bodies if b['object_type'] == 'Planet']
                
                if planets:
                    habitable = [p for p in planets if p.get('habitable')]
                    if habitable:
                        icons.append('P')
                    else:
                        icons.append('p')
                
                if has_stations:
                    icons.append('S')
                
                asteroids = [b for b in bodies if b['object_type'] == 'Asteroid Belt']
                if asteroids:
                    mineral_rich = [a for a in asteroids if a.get('mineral_rich')]
                    if mineral_rich:
                        icons.append('M')
                    else:
                        icons.append('a')
                
                if icons and px < self.virtual_width:
                    current_char, current_data, current_faction = virtual_buf[py + 1][px]
                    if current_char in (" ", "░"):
                        virtual_buf[py + 1][px] = (icons[0], None, current_faction)
        
        # Plot NPC ships
        if nav and hasattr(nav, 'npc_ships'):
            for npc in nav.npc_ships:
                nx, ny, nz = npc.coordinates
                npx, npy = project(nx, ny)
                _, _, faction = virtual_buf[npy][npx]
                virtual_buf[npy][npx] = ("&", npc, faction)
        
        # Plot player ship
        sx, sy, sz = ship.coordinates
        ship_vx, ship_vy = project(sx, sy)
        _, _, faction = virtual_buf[ship_vy][ship_vx]
        virtual_buf[ship_vy][ship_vx] = ("@", None, faction)
        
        # Center viewport on ship
        self.center_viewport_on(ship_vx, ship_vy)
        
        # Build display text
        lines = []
        
        # Header
        lines.append("═" * self.viewport_width)
        header = "GALAXY MAP"
        if self.show_faction_zones:
            header += " - FACTION ZONES"
        if self.show_ether_energy:
            header += " - ETHER ENERGY"
        lines.append(header.center(self.viewport_width))
        lines.append("═" * self.viewport_width)
        
        # Render viewport
        for y in range(self.viewport_height):
            virtual_y = self.viewport_y + y
            line = ""
            if 0 <= virtual_y < self.virtual_height:
                for x in range(self.viewport_width):
                    virtual_x = self.viewport_x + x
                    if 0 <= virtual_x < self.virtual_width:
                        char, sys_data, faction = virtual_buf[virtual_y][virtual_x]
                        line += char
                    else:
                        line += " "
            else:
                line = " " * self.viewport_width
            lines.append(line)
        
        # HUD
        lines.append("─" * self.viewport_width)
        
        # Ship info
        ship_info = f"Ship: {ship.name} ({ship.ship_class})  Pos: ({sx},{sy},{sz})"
        lines.append(ship_info)
        
        # Fuel and stats
        fuel_pct = ship.fuel / ship.max_fuel if ship.max_fuel > 0 else 0
        fuel_bar = self.make_bar(int(fuel_pct * 20), 20, "█", "░")
        scan_range = getattr(ship, 'scan_range', 5.0)
        fuel_line = f"Fuel: {fuel_bar} {ship.fuel}/{ship.max_fuel}  Range: {ship.jump_range}  Scan: {scan_range:.1f}"
        lines.append(fuel_line)
        
        # Systems visited
        visited_count = sum(1 for s in galaxy.systems.values() if s.get("visited"))
        stats_line = f"Systems: {len(galaxy.systems)} | Visited: {visited_count}"
        
        # Current faction zone
        if self.show_faction_zones and hasattr(galaxy, 'get_faction_for_location'):
            current_faction = galaxy.get_faction_for_location(sx, sy, sz)
            if current_faction:
                stats_line += f" | Zone: {current_faction}"
        
        # Current ether friction
        if self.show_ether_energy and hasattr(galaxy, 'ether_energy') and galaxy.ether_energy:
            friction = galaxy.ether_energy.get_friction_at(sx, sy, sz)
            friction_level = galaxy.ether_energy.get_friction_level(friction)
            stats_line += f" | Ether: {friction_level} ({friction:.2f}x)"
        
        # Nearby NPCs
        if nav and hasattr(nav, 'npc_ships'):
            import math
            nearby_npcs = []
            for npc in nav.npc_ships:
                nx, ny, nz = npc.coordinates
                distance = math.sqrt((sx-nx)**2 + (sy-ny)**2 + (sz-nz)**2)
                if distance <= 10:
                    nearby_npcs.append((npc, distance))
            if nearby_npcs:
                stats_line += f" | NPCs nearby: {len(nearby_npcs)}"
        
        lines.append(stats_line)
        lines.append("")
        
        # Legends
        if self.show_faction_zones:
            lines.append("Faction Mode: Colored backgrounds = faction zones  ░ = faction space")
        
        if self.show_ether_energy:
            lines.append("Ether Energy: · Low Drag(green) | Enhancement(cyan) | Mild Drag(yellow) | High Drag(red)")
        
        lines.append("Legend: @ You  & NPC  * Visited  + Unvisited  ◈ Station(Vis)  ◆ Station")
        lines.append("Scan: P Habitable  p Planet  S Station  M Minerals  a Asteroids")
        lines.append("[q/ESC: Back | Arrow/hjkl: Move | f: Toggle Factions | e: Toggle Ether | n: News | H: History]")
        
        # Set text
        self.map_display.setPlainText("\n".join(lines))
    
    def make_bar(self, filled, total, fill_char="█", empty_char="░"):
        """Create an ASCII bar."""
        return fill_char * filled + empty_char * (total - filled)
    
    def center_viewport_on(self, vx, vy):
        """Center the viewport on given virtual coordinates."""
        target_x = vx - self.viewport_width // 2
        target_y = vy - self.viewport_height // 2
        
        self.viewport_x = max(0, min(self.virtual_width - self.viewport_width, target_x))
        self.viewport_y = max(0, min(self.virtual_height - self.viewport_height, target_y))
    
    def keyPressEvent(self, event):
        """Handle keyboard input."""
        key = event.key()
        text = event.text().lower()
        
        # Close
        if key in (Qt.Key.Key_Escape, Qt.Key.Key_Q):
            self.accept()
            return
        
        # Toggle faction zones
        if text == 'f':
            self.show_faction_zones = not self.show_faction_zones
            status = "ON" if self.show_faction_zones else "OFF"
            self.status_label.setText(f"Faction zones: {status}")
            self.update_map()
            return
        
        # Toggle ether energy
        if text == 'e':
            self.show_ether_energy = not self.show_ether_energy
            status = "ON" if self.show_ether_energy else "OFF"
            self.status_label.setText(f"Ether energy overlay: {status}")
            self.update_map()
            return
        
        # Show news
        if text == 'n':
            from news_system import display_news
            # Open news dialog
            msg = QMessageBox(self)
            msg.setWindowTitle("Galactic News")
            
            if hasattr(self.game, 'event_system'):
                news_feed = self.game.event_system.get_news_feed(limit=10)
                if news_feed:
                    news_text = "\n\n".join([f"• {item['headline']}\n  {item['description']}" 
                                             for item in news_feed])
                else:
                    news_text = "No news available at this time."
            else:
                news_text = "News system unavailable."
            
            msg.setText(news_text)
            msg.exec()
            return
        
        # Show history
        if text == 'h':
            dlg = GalacticHistoryDialog(self)
            dlg.exec()
            return
        
        # Movement
        dx = dy = 0
        if key == Qt.Key.Key_Left or text == 'h':
            dx = -1
        elif key == Qt.Key.Key_Right or text == 'l':
            dx = 1
        elif key == Qt.Key.Key_Up or text == 'k':
            dy = -1
        elif key == Qt.Key.Key_Down or text == 'j':
            dy = 1
        else:
            super().keyPressEvent(event)
            return
        
        # Process movement
        self.move_ship(dx, dy)
    
    def move_ship(self, dx, dy):
        """Move the ship and handle fuel consumption."""
        import math
        import random
        
        nav = getattr(self.game, 'navigation', None)
        if not nav or not nav.galaxy or not nav.current_ship:
            return
        
        galaxy = nav.galaxy
        ship = nav.current_ship
        
        # Movement step
        step_x = max(1, round(galaxy.size_x / self.virtual_width))
        step_y = max(1, round(galaxy.size_y / self.virtual_height))
        
        # Calculate new position
        old_x, old_y, old_z = ship.coordinates
        new_x = max(0, min(galaxy.size_x, old_x + dx * step_x))
        new_y = max(0, min(galaxy.size_y, old_y + dy * step_y))
        
        # Calculate distance
        distance = math.sqrt((new_x - old_x)**2 + (new_y - old_y)**2)
        
        # Handle fuel consumption
        if distance > 0:
            try:
                from navigation import calculate_fuel_consumption
                target_coords = (new_x, new_y, old_z)
                fuel_needed = calculate_fuel_consumption(ship, distance, target_coords, self.game)
                
                if ship.fuel > 0:
                    if fuel_needed > ship.fuel:
                        ship.fuel = 0
                    else:
                        ship.fuel -= fuel_needed
                    
                    if ship.fuel <= 10 and ship.fuel > 0:
                        self.status_label.setText(f"⚠️ Low fuel warning: {ship.fuel}/{ship.max_fuel}")
                    elif ship.fuel <= 0:
                        self.status_label.setText("⚠️ Fuel depleted! Movement slowly recharges fuel.")
                        self.fuel_recharge_counter = 0
                        self.fuel_recharge_target = 3
                else:
                    # Recharge when out of fuel
                    self.fuel_recharge_counter += 1
                    
                    if self.fuel_recharge_counter >= self.fuel_recharge_target:
                        recharge_amount = random.randint(1, 2)
                        ship.fuel = min(ship.fuel + recharge_amount, ship.max_fuel)
                        self.fuel_recharge_counter = 0
                        self.fuel_recharge_target = 4 if self.fuel_recharge_target == 3 else 3
                        
                        if ship.fuel < ship.max_fuel:
                            self.status_label.setText(f"⚡ Emergency recharge: {ship.fuel}/{ship.max_fuel}")
                        else:
                            self.status_label.setText("⚡ Fuel fully recharged!")
            except ImportError:
                pass
        
        # Move ship
        ship.coordinates = (new_x, new_y, old_z)
        
        # Update map
        self.update_map()
        
        # Track moves and update events
        self.move_count += 1
        if self.move_count % 3 == 0 and hasattr(self.game, 'event_system'):
            self.game.event_system.update_events()
        
        # Move NPCs
        if hasattr(nav, 'update_npc_ships'):
            nav.update_npc_ships()
        
        # Check for NPC encounters
        if hasattr(nav, 'get_npc_at_location'):
            npc = nav.get_npc_at_location((new_x, new_y, old_z))
            if npc:
                msg = QMessageBox(self)
                msg.setWindowTitle("NPC Encounter")
                msg.setText(f"Encountered {npc.name}!")
                msg.exec()
                return
        
        # Check for system entry
        def project(px, py):
            sx = int((px / galaxy.size_x) * (self.virtual_width - 1))
            sy = int((py / galaxy.size_y) * (self.virtual_height - 1))
            return max(0, min(self.virtual_width - 1, sx)), max(0, min(self.virtual_height - 1, sy))
        
        ship_cell = project(new_x, new_y)
        overlapping = []
        for sys in galaxy.systems.values():
            cx, cy, cz = sys["coordinates"]
            if project(cx, cy) == ship_cell:
                overlapping.append(sys)
        
        if overlapping:
            # Find nearest system
            def dist(a, b):
                ax, ay, az = a
                bx, by, bz = b
                return math.sqrt((ax-bx)**2 + (ay-by)**2 + (az-bz)**2)
            
            entered_system = min(overlapping, key=lambda s: dist((new_x, new_y, old_z), s["coordinates"]))
            ship.coordinates = entered_system["coordinates"]
            entered_system["visited"] = True
            
            self.update_map()
            
            # Show system info
            bodies = entered_system.get('celestial_bodies', [])
            planets = [b for b in bodies if b['object_type'] == 'Planet']
            stations = entered_system.get('stations', [])
            
            info_parts = [f"Arrived at {entered_system['name']}"]
            
            if planets:
                habitable = [p for p in planets if p.get('habitable')]
                if habitable:
                    info_parts.append(f"{len(habitable)} habitable planet(s)")
            
            if stations:
                info_parts.append(f"{len(stations)} station(s)")
            
            msg = QMessageBox(self)
            msg.setWindowTitle("System Entry")
            msg.setText("\n".join(info_parts))
            msg.exec()


class MapHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for the map screen."""
    
    def __init__(self, parent_document):
        super().__init__(parent_document)
        
        # Define formats
        self.cyan_fmt = QTextCharFormat()
        self.cyan_fmt.setForeground(QColor("#00FFFF"))
        
        self.yellow_fmt = QTextCharFormat()
        self.yellow_fmt.setForeground(QColor("#FFFF55"))
        
        self.green_fmt = QTextCharFormat()
        self.green_fmt.setForeground(QColor("#00FF00"))
        
        self.magenta_fmt = QTextCharFormat()
        self.magenta_fmt.setForeground(QColor("#FF00FF"))
        
        self.red_fmt = QTextCharFormat()
        self.red_fmt.setForeground(QColor("#FF0000"))
        
        self.gray_fmt = QTextCharFormat()
        self.gray_fmt.setForeground(QColor("#808080"))
        
        # Patterns
        self.border_re = QRegularExpression(r"^[═─]+$")
        self.header_re = QRegularExpression(r"GALAXY MAP")
        self.player_re = QRegularExpression(r"@")
        self.npc_re = QRegularExpression(r"&")
        self.visited_re = QRegularExpression(r"\*")
        self.unvisited_re = QRegularExpression(r"\+")
        self.station_re = QRegularExpression(r"[◈◆]")
        self.legend_re = QRegularExpression(r"^\[.*\]$")
    
    def highlightBlock(self, text: str) -> None:
        # Borders
        if self.border_re.match(text).hasMatch():
            self.setFormat(0, len(text), self.cyan_fmt)
            return
        
        # Headers
        if self.header_re.match(text).hasMatch():
            self.setFormat(0, len(text), self.yellow_fmt)
            return
        
        # Legend
        if self.legend_re.match(text).hasMatch():
            self.setFormat(0, len(text), self.gray_fmt)
            return
        
        # Map symbols - use QRegularExpressionMatchIterator correctly
        it = self.player_re.globalMatch(text)
        while it.hasNext():
            m = it.next()
            self.setFormat(m.capturedStart(), m.capturedLength(), self.cyan_fmt)

        it = self.npc_re.globalMatch(text)
        while it.hasNext():
            m = it.next()
            self.setFormat(m.capturedStart(), m.capturedLength(), self.magenta_fmt)

        it = self.visited_re.globalMatch(text)
        while it.hasNext():
            m = it.next()
            self.setFormat(m.capturedStart(), m.capturedLength(), self.green_fmt)

        it = self.unvisited_re.globalMatch(text)
        while it.hasNext():
            m = it.next()
            self.setFormat(m.capturedStart(), m.capturedLength(), self.yellow_fmt)

        it = self.station_re.globalMatch(text)
        while it.hasNext():
            m = it.next()
            self.setFormat(m.capturedStart(), m.capturedLength(), self.cyan_fmt)


# ---------------------------------------------------------------------------
# Application entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """
    Entrypoint for launching the PyQt6 interface.

    Typical usage from the repository root:
    ---------------------------------------
    - Ensure you have installed the UI requirements:

        pip install -r requirements_ui.txt

      and that `requirements_ui.txt` includes `PyQt6`.

    - Then run:

        python3 pyqt_interface.py

    The window will open with the ASCII-style main menu.
    """
    app = QApplication(sys.argv)
    window = RoguelikeMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
