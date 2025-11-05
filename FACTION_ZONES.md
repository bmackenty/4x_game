# Faction Zones System - Implementation Guide

## Overview
The faction zones system creates a living, politically-divided galaxy where different factions control specific regions of space. Systems, stations, and planets within faction-controlled zones provide unique benefits based on your reputation with that faction.

**NEW**: Visual faction zone display! Press **'f'** on the galaxy map to toggle faction zone visualization with color-coded territories.

## Key Features Implemented

### 1. Expanded Galaxy Size
- **Previous**: 100 x 100 x 50 (500,000 cubic units)
- **New**: 500 x 500 x 200 (50,000,000 cubic units)
- **100x larger volume** for more exploration and strategic depth
- **80-120 star systems** (up from 30-40)
- More diverse distribution and room for faction territories

### 2. Faction Zone Generation
Each faction zone consists of:
- **Center Point**: Random coordinates in galaxy space
- **Radius**: 40-100 units (varies by faction)
- **Systems List**: All star systems within the zone
- **15 active faction zones** out of 30+ available factions

#### Zone Distribution
- Approximately 35% of systems are faction-controlled
- 65% remain neutral/unclaimed space
- Zones can overlap, creating contested regions
- Systems are assigned to the first matching zone

### 2.5. Visual Faction Zone Display (NEW!)

Press **'f'** on the galaxy map to toggle between normal and faction visualization modes.

#### Faction Mode OFF (Default)
- Clean, minimal display
- Normal colored systems: `*` (visited) and `+` (unvisited)
- Stations: `◈` (visited) or `◆` (unvisited)
- Focus on navigation and exploration

#### Faction Mode ON (Press 'f')
- **Color-coded backgrounds** for each faction zone
- **11 distinct colors** for easy faction identification
- **`░` characters** fill faction-controlled space
- **Current zone displayed** in the HUD
- **Header changes** to "GALAXY MAP - FACTION ZONES"
- Systems in faction space show **colored backgrounds**

#### Available Faction Colors
- Blue, Red, Green, Magenta, Cyan, Yellow
- Bright variants: Bright Blue, Bright Red, Bright Green, Bright Magenta, Bright Cyan

#### Visual Benefits
✓ Instantly identify faction territories at a glance
✓ Plan optimal routes through friendly faction space
✓ Avoid hostile faction zones visually
✓ See your current location's faction affiliation
✓ Understand galactic political geography

### 3. System-Level Faction Control

#### Faction-Influenced System Types
When a system falls within faction space, its type is biased based on faction focus:

| Faction Focus | Preferred System Types |
|--------------|----------------------|
| Trade | Trading Hub, Core World, Industrial |
| Research | Research, Core World, Frontier |
| Technology | Industrial, Research, Core World |
| Industry | Industrial, Mining, Core World |
| Exploration | Frontier, Research, Trading Hub |
| Mysticism | Research, Frontier, Core World |
| Cultural | Core World, Trading Hub, Agricultural |

#### Station Distribution
- **Neutral systems**: 40% chance no stations, 35% one station, 20% two, 5% three
- **Faction systems**: 30% one station, 35% two, 25% three, 10% four stations
- All stations in faction space are marked with `controlling_faction`

#### Planetary Control
- Habitable planets in faction space are marked as faction-controlled
- Provides basis for colony interactions and trade privileges
- Future expansion: faction-specific colony types and governance

### 4. Faction Benefits System

Benefits are tiered based on reputation level:

#### Reputation Tiers
- **Enemy** (-100 to -75): Hostile, no benefits, may be attacked
- **Hostile** (-75 to -50): No benefits, restricted access
- **Unfriendly** (-50 to -25): No benefits
- **Neutral** (-25 to 25): Basic presence acknowledged
- **Cordial** (25 to 50): Minor benefits
- **Friendly** (50 to 75): Major benefits
- **Allied** (75 to 100): Maximum benefits

#### Benefit Categories

**Trade Discounts**
- Neutral: 0-5% (faction-specific)
- Cordial: +5% additional
- Friendly: +10% additional
- Allied: +15% additional
- Maximum: 30% trade discount when allied

**Repair Discounts**
- Neutral: 0-10% (Technology/Industry factions)
- Cordial: Same as neutral
- Friendly: +15% additional
- Allied: +20% additional
- Maximum: 35% repair discount

**Refuel Discounts**
- Cordial: 10%
- Friendly: +10% additional (20% total)
- Allied: +20% additional (40% total)

**Shipyard Discounts**
- Neutral: 0-5% (Technology/Industry factions)
- Cordial: Same as neutral
- Friendly: +10% additional
- Allied: +20% additional
- Maximum: 30% shipyard discount

**Research Bonuses**
- Neutral: 0-10% (Research factions)
- Friendly: +15% additional
- Allied: +25% additional
- Maximum: 40% research speed bonus

#### Faction-Specific Base Benefits (Neutral Reputation)

**Trade-Focused Factions**
- Stellar Nexus Guild
- Galactic Circus
- Benefits: -5% trade prices

**Technology/Industry Factions**
- The Icaron Collective
- Gearwrights Guild
- Quantum Artificers Guild
- Technomancers
- Benefits: -10% repair, -5% shipyard

**Research Factions**
- The Veritas Covenant
- Scholara Nexus
- Chemists' Concord
- Benefits: +10% research speed

### 5. Location-Specific Benefits

**At Stations** (Cordial+)
- Station access granted
- Docking privileges
- Information sharing

**At Shipyards** (Friendly+)
- Advanced ship modifications
- Faction-specific ship designs
- Priority service

**At Planets** (Friendly+)
- Colony support
- Trade privileges
- Resource access
- Cultural exchange

## Technical Implementation

### Galaxy Class Changes (navigation.py)

```python
class Galaxy:
    def __init__(self):
        self.size_x = 500  # Increased from 100
        self.size_y = 500  # Increased from 100
        self.size_z = 200  # Increased from 50
        self.faction_zones = {}  # NEW: Faction zone data
        
    def generate_faction_zones(self):
        # Creates 15 faction zones with random centers and radii
        
    def get_faction_for_location(self, x, y, z):
        # Returns controlling faction or None for a location
```

### System Data Structure

```python
system = {
    "name": "Alpha Centauri",
    "coordinates": (250, 300, 100),
    "type": "Research",  # Biased by faction focus
    "controlling_faction": "The Veritas Covenant",  # NEW
    "stations": [
        {
            "name": "Research Station Alpha",
            "controlling_faction": "The Veritas Covenant"  # NEW
        }
    ],
    "celestial_bodies": [
        {
            "object_type": "Planet",
            "habitable": True,
            "controlling_faction": "The Veritas Covenant"  # NEW
        }
    ]
}
```

### FactionSystem Class Changes (factions.py)

```python
def get_faction_zone_benefits(self, faction_name, location_type='system'):
    """
    Returns dict with:
    - trade_discount: Percentage discount
    - repair_discount: Percentage discount
    - refuel_discount: Percentage discount
    - research_bonus: Percentage bonus
    - shipyard_discount: Percentage discount
    - description: List of benefit descriptions
    """
```

## Gameplay Impact

### Strategic Considerations

1. **Route Planning**
   - Plan routes through friendly faction space for better prices
   - Avoid hostile faction zones if low reputation
   - Neutral space offers no benefits but no risks

2. **Reputation Management**
   - Build reputation with key factions to unlock benefits
   - Trade in faction space to gain reputation
   - Complete faction missions for reputation boosts

3. **Economic Optimization**
   - Allied status in Trade faction space = 30% savings
   - Research in friendly Research faction space = 40% faster
   - Repair in Technology faction space = 35% cheaper

4. **Exploration Rewards**
   - Larger galaxy means more to discover
   - Faction zones create natural exploration goals
   - Finding faction-controlled research stations = major benefits

### Future Expansion Possibilities

1. **Dynamic Faction Borders**
   - Zones expand/contract based on faction power
   - Player actions influence faction territory
   - Faction wars create contested zones

2. **Faction Missions**
   - Deliver goods to faction systems
   - Defend faction space from pirates
   - Explore for faction scientific interests

3. **Faction-Exclusive Content**
   - Unique ships available only to allies
   - Special technologies from Research factions
   - Cultural artifacts from Cultural factions

4. **Political Events**
   - Faction alliances and rivalries
   - Trade agreements between factions
   - Diplomatic incidents affecting reputation

## Usage in Game

### Map Controls

**Galaxy Map Keybindings:**
- **f** - Toggle faction zone visualization ON/OFF
- **n** - Open galactic news feed
- **q/ESC** - Return to main screen
- **hjkl** - Move ship (vim-style)
- **Arrow keys** - Move ship

### Viewing Faction Zones on Map

**Normal Mode** (faction toggle OFF):
```
GALAXY MAP
════════════════════════════════════════

      +    ◆        *      +
    +    @     +        ◈
      *        +    &
        +         +
```

**Faction Mode** (press 'f' to toggle ON):
```
GALAXY MAP - FACTION ZONES
════════════════════════════════════════

  ░░░░+░░░░◆░░░   *      +
 ░░░░░@░░░+░░░░   ◈      
  ░░░░*░░░░+░░░&          
   ░░░░░░░░░░░      +
   
Zone: The Veritas Covenant  [BLUE background]
```

Legend:
- `░` = Faction-controlled space
- Colored backgrounds = Different faction zones
- Your current zone shown in HUD

### Viewing Faction Information

When entering a faction-controlled system:
```
═══════════════════════════════════════
              ALPHA CENTAURI
═══════════════════════════════════════

⚑ Controlled by: The Veritas Covenant
  Your Reputation: Friendly (65)
  Active Benefits: +10% research, -10% trade

Type: Research
Population: 5,234,000
...
```

### Testing the System

Run the test scripts:

**Faction Zone Data:**
```bash
python3 test_faction_zones.py
```

This will show:
- Galaxy size and system count
- All faction zones with their properties
- System distribution by faction
- Sample faction-controlled systems
- Benefit calculations at different reputation levels
- Galaxy size analysis

**Faction Toggle Demo:**
```bash
python3 demo_faction_toggle.py
```

This will demonstrate:
- How the faction toggle works
- Visual features and colors
- Gameplay benefits
- Controls and keybindings
- Implementation details
- Faction zone coverage statistics

## Summary

The faction zones system adds:
- ✅ **100x larger galaxy** for exploration
- ✅ **15 faction-controlled zones** across the galaxy
- ✅ **Visual faction toggle** (press 'f' on map)
- ✅ **Color-coded territories** for easy identification
- ✅ **Dynamic benefits** based on reputation
- ✅ **Strategic depth** through faction relations
- ✅ **Economic gameplay** with discounts and bonuses
- ✅ **Visual feedback** showing faction control
- ✅ **Scalable system** for future expansion
- Benefit calculations at different reputation levels
- Galaxy size analysis

## Summary

The faction zones system adds:
- ✅ **100x larger galaxy** for exploration
- ✅ **15 faction-controlled zones** across the galaxy
- ✅ **Dynamic benefits** based on reputation
- ✅ **Strategic depth** through faction relations
- ✅ **Economic gameplay** with discounts and bonuses
- ✅ **Visual feedback** showing faction control
- ✅ **Scalable system** for future expansion

Players now have meaningful reasons to:
- Build relationships with specific factions
- Plan routes through friendly space
- Seek out faction-controlled research/trade hubs
- Explore the vastly expanded galaxy
