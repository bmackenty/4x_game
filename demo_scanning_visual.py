#!/usr/bin/env python3
"""
Visual demo of scanning range icons on the map
"""

print("=" * 70)
print(" " * 20 + "SCANNING SYSTEM VISUAL DEMO")
print("=" * 70)

print("""
When your ship approaches a star system, the scanning system reveals
information about celestial bodies and facilities beneath the system icon.

EXAMPLE GALAXY MAP VIEW:
""")

print("─" * 70)
print("                         GALAXY MAP")
print("═" * 70)
print()
print("       .   +       ◆       .    *      +     .     ◈      .    +")
print("           p      (S)            P           M            (S)")
print()
print("    .    +      .     *      .      @      .    +     .     *")
print("                                  (ship)")
print()
print("       *     .     +       .    ◈      *     .      +      .   *")
print("                                (S)")
print()
print("─" * 70)
print("Ship: Explorer (Scout Ship)  Pos: (50,50,25)")
print("Fuel: 100/100  Range: 15  Scan: 8.0")
print("─" * 70)

print("""
LEGEND:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

System Symbols:
  @  = Your ship (you are here)
  *  = Visited system
  +  = Unvisited system  
  ◈  = Station (visited)
  ◆  = Station (unvisited)

Scanned Object Icons (appear below systems within scan range):
  P  = Habitable planet (colonization opportunity!)
  p  = Regular planet
  S  = Space station (services available)
  M  = Mineral-rich asteroids (mining opportunity!)
  a  = Regular asteroid belt

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SCANNER UPGRADES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

╔════════════════════════╦═══════════╦═════════╦═══════╦═════════════════╗
║ Component              ║ Scan Range║  Cost   ║ Power ║ Tech Required   ║
╠════════════════════════╬═══════════╬═════════╬═══════╬═════════════════╣
║ Basic Ship             ║   5.0     ║    -    ║   -   ║ None            ║
║ Scanner Array          ║   8.0     ║ 12,000  ║  20   ║ None            ║
║ Advanced Scanner Array ║  15.0     ║ 30,000  ║  35   ║ Advanced Res.   ║
║ Quantum Scanner        ║  25.0     ║ 50,000  ║  50   ║ Quantum Mech.   ║
╚════════════════════════╩═══════════╩═════════╩═══════╩═════════════════╝

EXAMPLE SCENARIO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You're piloting an Explorer with a Quantum Scanner (25.0 range).

As you approach Rigel Station:
  ◆  <- Unvisited system icon
  S  <- Scanner detects: Space station present
  P  <- Scanner detects: Habitable planet in system
  M  <- Scanner detects: Mineral-rich asteroid belt

Decision Point:
• Visit the station for ship upgrades?
• Survey the habitable planet for colonization?
• Mine the asteroid belt for resources?
• Continue exploring to find better opportunities?

With a basic ship (5.0 range), you would only see:
  ◆  <- Unvisited system
     <- No scan data (too far away)

STRATEGIC BENEFITS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Plan routes more efficiently
✓ Identify valuable resources before committing fuel
✓ Find stations for repairs without trial and error
✓ Locate habitable planets for colonization missions
✓ Scout mineral deposits for mining operations
✓ Avoid empty systems when looking for specific services

Scout ships with advanced scanners make excellent exploration vessels!
""")

print("=" * 70)
print(" " * 15 + "INSTALL SCANNERS. EXPLORE SMARTER.")
print("=" * 70)
