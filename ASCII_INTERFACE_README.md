# ASCII 4X Game Interface

This is an ASCII-based interface for the 4X Galactic Empire Management Game, designed to work on Windows, macOS, and Linux terminals with color support.

## Features

### 🎮 **Cross-Platform ASCII Interface**
- **Elastic screen sizing** - adapts to any terminal size
- **Full color support** - uses ANSI colors for enhanced visuals
- **Multiple input methods** - numbers, letters, arrow keys, coordinate input
- **Context-sensitive menus** - different options based on current screen/activity

### 🗺️ **ASCII Galaxy Map**
- **Visual 2D projection** of the 3D galaxy with ASCII symbols
- **Symbol legend** for different system types
- **Color-coded systems** based on resources, threat level, and visit status
- **Real-time navigation** with coordinate input

### 💰 **Split-Screen Trading Interface**
- **Buy opportunities** on the left with prices and supply
- **Sell opportunities** on the right with demand and player inventory
- **Color-coded affordability** - red for unaffordable, green for profitable
- **Real-time market data** from the dynamic economy system

### 🚀 **Ship Builder Interface**
- **Component list selection** with detailed stats and costs
- **Real-time cost calculation** as you build
- **Visual ship stats** display
- **Template and custom ship options**

### 🤖 **Bot Interaction System**
- **Menu-based dialogue** with AI bots
- **Personality-based responses** 
- **Trading and information exchange**
- **Reputation tracking**

### 📊 **Always-Visible Status Bar**
- **Player credits** and ship information
- **Current location** coordinates
- **Fuel levels** with color-coded warnings
- **Current screen** indicator

## How to Run

### Quick Start
```bash
python3 run_ascii_game.py
```

### Alternative Launch
```bash
python3 game_interface.py
```

## Controls

### General Controls
- **Numbers (1-9)**: Select menu options
- **Letters (a-z)**: Alternative shortcuts and trading commands
- **Arrow Keys**: Navigate menus (where supported)
- **Enter**: Confirm selection
- **ESC**: Go back/exit current screen

### Navigation
- **Coordinate Input**: Enter exact X,Y,Z coordinates for precise navigation
- **System Jump**: Select from nearby systems within jump range
- **Local Map**: View systems within current jump range

### Trading
- **1-8**: Buy commodity by number from buy opportunities list
- **a-h**: Sell commodity by letter from sell opportunities list
- **m**: View detailed market analysis
- **i**: View your inventory
- **r**: Return to ship status

### Ship Builder
- **1-5**: Select component categories (Hull, Engine, Weapons, Shields, Special)
- **6**: View current ship stats
- **7**: Purchase designed ship
- **8**: Return to main menu

## Game Screens

### 🏠 **Main Menu**
- Start new game
- Character creation
- Help system
- Quit

### 👤 **Character Creation**
- **6 Character Classes**: Each with unique bonuses and starting assets
- **6 Backgrounds**: Different starting resources and traits
- **Real-time stats** display as you select options

### 🗺️ **Galaxy Map**
- **ASCII visualization** of the galaxy with system symbols
- **Current location** display with system information
- **Navigation options** for jumping and coordinate input
- **Nearby systems** list with fuel costs

### 🚀 **Ship Status**
- **Current ship** information and location
- **System details** where you're currently located
- **Action menu** for trading, station visits, navigation

### 💰 **Trading Interface**
- **Split-screen layout** with buy/sell opportunities
- **Market analysis** with supply/demand information
- **Inventory management** with cargo tracking
- **Profit calculations** for trading decisions

### 🔧 **Ship Builder**
- **Component selection** from 5 categories
- **Cost tracking** and stat calculations
- **Template ships** for quick builds
- **Custom designs** with detailed specifications

### 🏗️ **Station Management**
- **Owned stations** with income and upgrade levels
- **Available stations** for purchase
- **Station services** and benefits
- **Upgrade options** for increased income

### 🤝 **Faction Relations**
- **Reputation tracking** with all 30 factions
- **Color-coded standings** (green=allied, red=enemy)
- **Faction benefits** based on reputation levels
- **Territory information** and diplomatic status

### 🔬 **Archaeology**
- **Discovery summary** with sites and artifacts found
- **Exploration options** for current location
- **Ancient civilization** information
- **Artifact collection** and research benefits

### 🤖 **Bot Interaction**
- **Bot information** including personality and current goals
- **Dialogue options** for greeting and information exchange
- **Trading opportunities** with AI bots
- **Reputation building** through interactions

## Technical Details

### Color Support
- **ANSI color codes** for cross-platform compatibility
- **Bright colors** for important information
- **Dim colors** for secondary information
- **Color-coded status** (green=good, red=warning, yellow=attention)

### Terminal Compatibility
- **Windows**: Uses `msvcrt` for input and `shutil` for terminal size
- **Unix/Linux/macOS**: Uses `termios`, `tty`, and `fcntl` for terminal control
- **Fallback support** for terminals without advanced features

### Performance
- **10 FPS refresh rate** for smooth interface updates
- **Background refresh thread** to prevent input blocking
- **Efficient screen clearing** and redrawing
- **Minimal CPU usage** during idle periods

## Troubleshooting

### Color Not Working
- Ensure your terminal supports ANSI colors
- Set `TERM` environment variable to a color-capable terminal type
- Try running with `TERM=xterm-256color python3 run_ascii_game.py`

### Input Not Responding
- Make sure you're in the correct input mode
- Try pressing Enter to confirm selections
- Use ESC to exit input modes

### Screen Layout Issues
- Resize your terminal window for better layout
- Minimum recommended size: 80x24 characters
- Optimal size: 120x40 characters or larger

### Game Not Starting
- Ensure all game files are in the same directory
- Check Python version (3.6+ required)
- Verify all dependencies are available

## Future Enhancements

- **Save/Load functionality** for game states
- **Multiplayer support** with shared galaxy
- **Advanced combat system** with ASCII battle displays
- **Technology research trees** with visual progression
- **Diplomatic negotiations** with interactive dialogue
- **Automated trading routes** and fleet management
- **Enhanced archaeology** with excavation mini-games
- **Custom key bindings** and interface preferences

---

**Enjoy exploring the galaxy with the ASCII interface!** 🌌
