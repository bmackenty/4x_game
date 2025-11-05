# Faction Zone Visualization - Quick Reference

## Map Toggle Feature

Press **'f'** on the galaxy map to switch between modes.

### Normal Mode (Default)
```
═══════════════════════════════════════════════════════════
                        GALAXY MAP
═══════════════════════════════════════════════════════════

    +         ◆              *         +
      +    @      +              ◈         +
         *           +    &
    +         +              *
         *         +
              +         *         +

Ship: Wanderer (Scout)  Pos: (250,300,100)
Fuel: 45/50  Range: 10  Scan: 8.0
Systems: 89 | Visited: 12

Legend: @ You  & NPC  * Visited  + Unvisited  ◈ Station(Vis)  ◆ Station
[q/ESC: Back | Arrow/hjkl: Move | f: Toggle Factions]
```

**Features:**
- Clean, minimal display
- Focus on systems and stations
- Easy navigation
- Clear visited/unvisited distinction

---

### Faction Mode (Press 'f')
```
═══════════════════════════════════════════════════════════
                  GALAXY MAP - FACTION ZONES
═══════════════════════════════════════════════════════════

    +  ░░░░░◆░░░░░░░    *         +
      ░░░@░░░░+░░░░░        ◈         +
    ░░░░░*░░░░░░░+░░░&
    ░░░░░░+░░░░░░░░░      *
    ░░░░░*░░░░░+░░░
              +         *         +

Ship: Wanderer (Scout)  Pos: (250,300,100)
Fuel: 45/50  Range: 10  Scan: 8.0
Systems: 89 | Visited: 12 | Zone: The Veritas Covenant

Faction Mode: Colored backgrounds = faction zones  ░ = faction space

Legend: @ You  & NPC  * Visited  + Unvisited  ◈ Station(Vis)  ◆ Station
[q/ESC: Back | Arrow/hjkl: Move | f: Toggle Factions]
```

**Features:**
- **░ characters** fill faction-controlled space
- **Colored backgrounds** for each faction (11 unique colors)
- **Current zone** displayed in HUD ("Zone: The Veritas Covenant")
- **Header changes** to show "FACTION ZONES" mode
- Systems in faction space have **colored backgrounds**
- Same navigation controls

---

## Faction Colors

When faction mode is enabled, each faction zone appears in one of these colors:

| Color | Faction Example |
|-------|----------------|
| Blue | The Veritas Covenant |
| Red | The Harmonic Synaxis |
| Green | Keeper of the Keys |
| Magenta | The Galactic Salvage Guild |
| Cyan | Celestial Alliance |
| Yellow | The Scholara Nexus |
| Bright Blue | Technomancers |
| Bright Red | The Harmonic Resonance Collective |
| Bright Green | The Icaron Collective |
| Bright Magenta | Dreamwalker Collective |
| Bright Cyan | Quantum Artificers Guild |

*Colors are automatically assigned when the galaxy is generated.*

---

## Quick Tips

### When to Use Normal Mode
- ✓ General navigation and exploration
- ✓ Finding specific stations or systems
- ✓ When you want minimal visual clutter
- ✓ Scanning for planets and resources

### When to Use Faction Mode
- ✓ Planning routes through friendly faction space
- ✓ Avoiding hostile faction territories
- ✓ Finding faction-controlled research stations
- ✓ Understanding galactic political layout
- ✓ Locating specific faction zones quickly
- ✓ Strategic gameplay and route optimization

---

## Strategic Advantages

### With Faction Visualization Enabled:

**Route Planning**
- See at a glance which faction controls nearby systems
- Plan efficient routes through allied faction space for maximum benefits
- Avoid hostile zones that might attack or deny docking

**Resource Location**
- Quickly find Research faction zones for science bonuses
- Locate Trade faction hubs for better prices
- Identify Technology faction space for cheaper repairs

**Reputation Management**
- Visualize where your faction relationships matter most
- Focus trading and missions in specific faction zones
- Build strategic alliances in key areas of the galaxy

**Exploration Goals**
- See unexplored faction zones as targets
- Discover which factions control valuable systems
- Plan expansion into unclaimed neutral space

---

## Technical Details

### Implementation
- **Virtual buffer** stores (character, system_data, faction_name) tuples
- **Dynamic color mapping** assigns colors to factions on galaxy generation
- **Background rendering** fills faction space with ░ (light shade) character
- **Faction detection** uses distance calculation from zone centers
- **HUD updates** show current faction zone when in faction mode

### Performance
- Toggle is instant (no regeneration needed)
- Same map rendering pipeline
- Faction data cached in virtual buffer
- No performance impact on normal mode

---

## Examples by Reputation

### Neutral Territory (No Faction)
```
Normal Mode:  *    +    ◆    ◈
Faction Mode: *    +    ◆    ◈  (no background)
```

### Trade Faction Space (Allied - 30% trade discount)
```
Normal Mode:  *    +    ◆    ◈
Faction Mode: *░░░░+░░░░◆░░░░◈  (CYAN background)
HUD shows: "Zone: Stellar Nexus Guild"
```

### Research Faction Space (Friendly - 25% research bonus)
```
Normal Mode:  *    +    ◆    ◈
Faction Mode: *░░░░+░░░░◆░░░░◈  (BLUE background)
HUD shows: "Zone: The Veritas Covenant"
```

### Technology Faction Space (Allied - 35% repair discount)
```
Normal Mode:  *    +    ◆    ◈
Faction Mode: *░░░░+░░░░◆░░░░◈  (BRIGHT_GREEN background)
HUD shows: "Zone: The Icaron Collective"
```

---

## Keybindings Summary

| Key | Action |
|-----|--------|
| **f** | Toggle faction zones ON/OFF |
| **n** | Open galactic news feed |
| **q** or **ESC** | Return to main screen |
| **h/j/k/l** | Move ship (vim-style: left/down/up/right) |
| **Arrow keys** | Move ship (arrow keys) |

---

## See Also

- `FACTION_ZONES.md` - Complete faction zones documentation
- `test_faction_zones.py` - Test faction zone data and benefits
- `demo_faction_toggle.py` - Interactive demo of the toggle feature
- `factions.py` - Faction system and benefits implementation
- `navigation.py` - Galaxy generation and faction zone creation
