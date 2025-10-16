#!/usr/bin/env python3
"""
Quick test to verify uniform button sizing
"""

from textual.app import App, ComposeResult
from textual.containers import Grid, Vertical
from textual.widgets import Button, Static, Header, Footer

class ButtonTestApp(App):
    """Test app to verify button sizing"""
    
    CSS = """
    Screen {
        background: black;
        color: green;
    }
    
    Button {
        min-height: 3;
        height: 3;
        min-width: 20;
        width: 100%;
        margin: 0 1;
        content-align: center middle;
    }
    
    #test_grid {
        grid-size: 3 2;
        grid-gutter: 1 2;
        margin: 2;
        padding: 1;
        height: auto;
        width: 100%;
    }
    
    .title {
        dock: top;
        height: 3;
        content-align: center middle;
        text-style: bold;
        color: cyan;
        background: blue 20%;
    }
    """
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("BUTTON SIZE TEST - All buttons should be uniform", classes="title")
        
        with Grid(id="test_grid"):
            yield Button("🏭 Short", variant="primary")
            yield Button("📈 Market Trading - Long", variant="primary")
            yield Button("🚀 Nav", variant="primary")
            yield Button("🏗️ Station Management System", variant="primary")
            yield Button("🤖 AI", variant="primary")
            yield Button("⚔️ Faction Relations & Diplomacy", variant="primary")
        
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.notify(f"Clicked: {event.button.label}")

if __name__ == "__main__":
    app = ButtonTestApp()
    app.run()