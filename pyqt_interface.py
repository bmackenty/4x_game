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

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QAction
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QDockWidget,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
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
    from galactic_history import generate_epoch_history
    from save_game import get_save_files, save_game, load_game
    GAME_AVAILABLE = True
except ImportError:
    # Fallback stubs so the UI can still be imported without the engine.
    GAME_AVAILABLE = False

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
        font = QFont("Courier")
        font.setStyleHint(QFont.StyleHint.TypeWriter)
        self.setFont(font)
        self.setMaximumHeight(120)  # keep it to roughly 6–8 lines
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        
        # Terminal-style black background with green text
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #000000;
                color: #00FF00;
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

        font = QFont("Courier")
        font.setStyleHint(QFont.StyleHint.TypeWriter)
        self.text_area.setFont(font)
        self.text_area.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        
        # Terminal-style black background with green text
        self.text_area.setStyleSheet("""
            QPlainTextEdit {
                background-color: #000000;
                color: #00FF00;
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

        for epoch in history_data:
            # Header for epoch.
            lines.append("═" * 120)
            lines.append(f" {epoch.get('name', 'Unnamed Epoch')}")
            start = epoch.get("start_year", 0)
            end = epoch.get("end_year", 0)
            duration = end - start
            lines.append(f" Years {start:,} – {end:,} (Duration: {duration:,} years)")
            lines.append("─" * 120)

            themes = epoch.get("themes", [])
            if themes:
                lines.append(f" Themes: {', '.join(themes)}")
            lines.append("")

            # Cataclysms.
            cataclysms = epoch.get("cataclysms", [])
            if cataclysms:
                lines.append(" ⚠ Major Cataclysms:")
                for c in cataclysms:
                    lines.append(f"   • {c}")
                lines.append("")

            # Faction formations.
            formations = epoch.get("faction_formations", [])
            if formations:
                lines.append(" Faction Formations:")
                for f in formations:
                    year = f.get("year", 0)
                    event = f.get("event", "")
                    lines.append(f"   • Year {year:,}: {event}")
                lines.append("")

            # Mysteries.
            mysteries = epoch.get("mysteries", [])
            if mysteries:
                lines.append(" ✦ Mysteries of This Age:")
                for m in mysteries:
                    lines.append(f"   • {m}")
                lines.append("")

            # Civilizations.
            civs = epoch.get("civilizations", [])
            lines.append(" Civilizations of This Epoch:")
            lines.append("")

            for civ in civs:
                lines.append(f" ┌─ {civ.get('name', 'Unknown Civilization')}")
                lines.append(f" │ Species: {civ.get('species', 'Unknown')}")
                traits = civ.get("traits", [])
                if traits:
                    lines.append(f" │ Traits: {', '.join(traits)}")
                founded = civ.get("founded", 0)
                collapsed = civ.get("collapsed", founded)
                duration_civ = collapsed - founded
                lines.append(
                    f" │ Founded: Year {founded:,} | Collapsed: Year {collapsed:,}"
                )
                lines.append(f" │ Duration: {duration_civ:,} years")
                lines.append(" │")
                lines.append(" │ Remnants:")
                lines.append(f" │ {civ.get('remnants', 'No data')}")
                lines.append(" │")

                events = civ.get("notable_events", [])
                if events:
                    lines.append(" │ Notable Events:")
                    for e in events:
                        lines.append(f" │  • {e}")

                lines.append(" └" + "─" * 118)
                lines.append("")

            lines.append("")
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

        self.setWindowTitle("4X Galactic Empire (PyQt6 Roguelike UI)")
        self.resize(1200, 800)

        # Reference to active game. None before starting or loading.
        self.game: Optional[Game] = None

        # ------------------------------------------------------------------
        # Central text area (ASCII main view)
        # ------------------------------------------------------------------
        self.main_view = QPlainTextEdit(self)
        self.main_view.setReadOnly(True)
        font = QFont("Courier")
        font.setStyleHint(QFont.StyleHint.TypeWriter)
        self.main_view.setFont(font)
        self.main_view.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        
        # Terminal-style black background with green text
        self.main_view.setStyleSheet("""
            QPlainTextEdit {
                background-color: #000000;
                color: #00FF00;
                border: none;
            }
        """)
        
        self.setCentralWidget(self.main_view)

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
        menu_view.addAction(self.action_view_history)

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
        self.action_view_history.setShortcut("H")
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
        lines: List[str] = []
        lines.append("═" * 80)
        lines.append(" GALACTIC EMPIRE 4X ".center(80, " "))
        lines.append("═" * 80)
        lines.append("")
        lines.append("  7019 • Mind Your Assumptions".center(80))
        lines.append("")
        lines.append("  MAIN MENU".center(80))
        lines.append("")
        lines.append("   [N] New Game")
        lines.append("   [L] Load Game")
        lines.append("   [S] Save Game (if a game is active)")
        lines.append("   [H] View Galactic History")
        lines.append("   [Q] Quit")
        lines.append("")
        lines.append("─" * 80)
        lines.append("Use menu entries or shortcuts: N, L, S, H, Q.".center(80))
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

        lines: List[str] = []
        lines.append("═" * 80)
        lines.append(f" COMMANDER OVERVIEW ".center(80))
        lines.append("═" * 80)
        lines.append("")
        lines.append(f" Name   : {player_name}")
        lines.append(f" Species: {player_species}")
        lines.append(f" Class  : {character_class}")
        lines.append("")
        lines.append(f" Credits: {credits:,}")
        lines.append(f" Turn   : {turn}")
        lines.append("")
        lines.append("─" * 80)
        lines.append(" (This is a minimal overview. Extend `render_game_overview`")
        lines.append("  to display ships, stations, inventory, navigation, etc.)")
        lines.append("─" * 80)
        lines.append("")
        lines.append("Use the Game menu or keyboard shortcuts to continue.".center(80))
        lines.append(" [N] New Game | [L] Load Game | [S] Save Game | [H] History ".center(80))
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
        - If the engine is available, instantiate a fresh `Game`.
        - For now, we do not run the full character creation pipeline here.
          Instead, we rely on the Game constructor, which in your project
          may trigger or encapsulate that flow (via other UI forms or
          procedural defaults).
        - After creating the game, we render an overview and log a message.
        """
        if not GAME_AVAILABLE:
            QMessageBox.critical(
                self,
                "Game Engine Not Available",
                "The game modules could not be imported. "
                "Make sure you run this inside the 4x_game project.",
            )
            return

        self.game = Game()
        self.message_log.add_message("New game started.", "[GAME]")
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
