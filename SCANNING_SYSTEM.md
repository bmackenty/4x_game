# Ship Scanning Range System

## Overview
A ship scanning range system that allows players to detect nearby celestial objects and space stations. When a ship gets close to a planet or station, small information icons appear under the space object on the galaxy map.

## Features Implemented

### 1. Ship Scan Range Property
- Added `scan_range` attribute to Ship class (navigation.py)
- Default scan range: 5.0 map units
- Scan range upgrades via special components

### 2. Scanning Detection Logic
- New method: `Ship.get_objects_in_scan_range(galaxy)`
- Returns list of tuples: (object_type, object_data, distance)
- Detects: systems, stations, planets, moons, asteroids, nebulae, comets
- Results sorted by distance from ship

### 3. Scanner Component Upgrades (ship_builder.py)

| Component | Scan Range | Cost | Power | Tech Required |
|-----------|------------|------|-------|---------------|
| Scanner Array | 8.0 | 12,000 | 20 | None |
| Advanced Scanner Array | 15.0 | 30,000 | 35 | Advanced Research |
| Quantum Scanner | 25.0 | 50,000 | 50 | Quantum Mechanics |

### 4. Map Display Features (nethack_interface.py)

#### Icon System
When objects are within scan range, small icons appear beneath the system symbol:
- **P** = Habitable planet (bright green)
- **p** = Regular planet (dim green)
- **S** = Space station (bright cyan)
- **M** = Mineral-rich asteroids (yellow)
- **a** = Regular asteroids (dim white)

#### HUD Display
Ship status now shows:
```
Ship: Test Scout (Scout Ship)  Pos: (50,50,25)
Fuel: 100/100  Range: 15  Scan: 8.0
```

#### Updated Legend
```
Legend: @ You  * Visited  + Unvisited  ◈ Station(Vis)  ◆ Station
Scan: P Habitable  p Planet  S Station  M Minerals  a Asteroids
```

## Usage Example

```python
# Create ship with default scan range (5.0)
ship = Ship("Explorer", "Scout Ship")

# Upgrade with Scanner Array (8.0 range)
ship.components['special'] = ['Scanner Array']
ship.calculate_stats_from_components()

# Get all objects in range
scan_results = ship.get_objects_in_scan_range(galaxy)

# Results format: [(type, data, distance), ...]
# Example: ('planet', {planet_data}, 7.2)
```

## Gameplay Benefits

1. **Strategic Exploration**: Players can see what's nearby before committing to a jump
2. **Resource Planning**: Detect mineral-rich asteroids and habitable planets from distance
3. **Station Finding**: Quickly locate nearby stations for repairs/upgrades
4. **Ship Specialization**: Scout ships with advanced scanners excel at exploration
5. **Upgrade Path**: Clear progression from basic → advanced → quantum scanners

## Technical Details

### Scan Range Calculation
- Based on 2D distance (X,Y coordinates) on galaxy map
- Z-axis currently ignored for simplicity
- Distance formula: `sqrt((x2-x1)² + (y2-y1)²)`

### Component Integration
- Scan range stored in ship_components["Special Systems"]
- Applied during `calculate_stats_from_components()`
- Multiple special systems: only one scanner can be active

### Map Rendering
1. Ship scans for nearby objects
2. Systems within range marked as "scanned"
3. Icons placed one row below system symbol
4. Only one icon per system (prioritizes most important)
5. Icons only placed in empty cells

## Test Results

The `test_scanning.py` script confirms:
- ✅ Default scan range: 5.0 units
- ✅ Scanner Array: 8.0 units → 13 objects detected
- ✅ Advanced Scanner: 15.0 units → 78 objects detected
- ✅ Quantum Scanner: 25.0 units → 157 objects detected
- ✅ Detects all object types: planets, moons, stations, asteroids, nebulae, comets
- ✅ Results sorted by distance
- ✅ Component upgrades properly applied

## Future Enhancements

Potential improvements:
- Show scan range circle/radius on map
- Detailed scan info popup when hovering over scanned objects
- Active scanning vs. passive scanning (energy cost)
- Scan quality/detail levels (basic scan vs. deep scan)
- Cloaked/hidden objects requiring better scanners
- Scan interference from nebulae or other phenomena
- 3D scanning (incorporate Z-axis distance)
