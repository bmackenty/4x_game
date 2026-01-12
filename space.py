"""
Space Environment Module - Static Ether Energy Zones
Defines static ether energy zones throughout the galaxy that affect fuel efficiency.
These zones represent areas of space with different drag coefficients (friction).
Higher drag zones require more fuel to traverse, while lower drag zones enhance fuel efficiency.
"""

from typing import List, Tuple, Dict

# Static Ether Energy Zones
# Format: List of (center: (x, y, z), radius: float, friction: float, name: str)
# friction < 1.0 = enhances fuel efficiency (less fuel needed)
# friction = 1.0 = neutral (no effect)
# friction > 1.0 = reduces fuel efficiency (more fuel needed)

ETHER_ENERGY_ZONES: List[Tuple[Tuple[int, int, int], float, float, str]] = [
    # Low friction zones (enhance fuel efficiency) - positioned throughout the galaxy
    ((50, 50, 25), 40.0, 0.5, "Void Current Alpha"),
    ((100, 100, 25), 45.0, 0.6, "Ether Stream Beta"),
    ((150, 150, 30), 50.0, 0.55, "Void Current Beta"),
    ((200, 200, 25), 40.0, 0.65, "Ether Stream Gamma"),
    ((250, 250, 30), 45.0, 0.7, "Cosmic Breeze Alpha"),
    ((300, 300, 25), 50.0, 0.6, "Void Current Gamma"),
    ((350, 350, 30), 40.0, 0.55, "Ether Stream Delta"),
    ((400, 400, 25), 45.0, 0.65, "Cosmic Breeze Beta"),
    ((450, 450, 30), 50.0, 0.5, "Void Current Delta"),
    
    # High friction zones (reduce fuel efficiency) - positioned throughout
    ((75, 75, 25), 55.0, 1.4, "Flux Storm Prime"),
    ((125, 125, 30), 50.0, 1.5, "Etheric Turbulence Alpha"),
    ((175, 175, 25), 60.0, 1.6, "Void Rift Alpha"),
    ((225, 225, 30), 55.0, 1.3, "Flux Storm Beta"),
    ((275, 275, 25), 50.0, 1.45, "Etheric Turbulence Beta"),
    ((325, 325, 30), 60.0, 1.55, "Void Rift Beta"),
    ((375, 375, 25), 55.0, 1.4, "Flux Storm Gamma"),
    ((425, 425, 30), 50.0, 1.5, "Etheric Turbulence Gamma"),
    
    # Moderate enhancement zones - distributed
    ((60, 120, 25), 35.0, 0.8, "Stable Ether Current Alpha"),
    ((140, 180, 30), 40.0, 0.75, "Cosmic Breeze Gamma"),
    ((220, 240, 25), 45.0, 0.85, "Ether Stream Epsilon"),
    ((300, 360, 30), 35.0, 0.8, "Stable Ether Current Beta"),
    ((380, 420, 25), 40.0, 0.75, "Cosmic Breeze Delta"),
    
    # Moderate drag zones - distributed
    ((80, 160, 30), 50.0, 1.2, "Mild Flux Zone Alpha"),
    ((160, 240, 25), 45.0, 1.25, "Etheric Disturbance Alpha"),
    ((240, 320, 30), 55.0, 1.15, "Cosmic Turbulence Alpha"),
    ((320, 400, 25), 50.0, 1.2, "Mild Flux Zone Beta"),
    ((400, 80, 30), 45.0, 1.25, "Etheric Disturbance Beta"),
    
    # Additional zones for better coverage
    ((25, 25, 20), 30.0, 0.7, "Cosmic Breeze Epsilon"),
    ((475, 475, 30), 35.0, 1.4, "Flux Storm Delta"),
    ((50, 450, 25), 40.0, 0.6, "Void Current Epsilon"),
    ((450, 50, 30), 45.0, 1.5, "Etheric Turbulence Delta"),
]

# Color mapping for ether energy zones based on friction level
# Used by UI to display zones with appropriate colors
ETHER_ENERGY_COLORS = {
    "very_low_drag": "bright_green",      # friction < 0.7
    "low_drag": "green",                   # 0.7 <= friction < 0.85
    "mild_enhancement": "cyan",            # 0.85 <= friction < 0.95
    "neutral": "dim_white",                # 0.95 <= friction < 1.05
    "mild_drag": "yellow",                 # 1.05 <= friction < 1.3
    "moderate_drag": "bright_yellow",      # 1.3 <= friction < 1.6
    "high_drag": "red",                    # 1.6 <= friction < 2.0
    "very_high_drag": "bright_red",       # friction >= 2.0
}

def get_color_for_friction(friction: float) -> str:
    """
    Get the color name for a given friction value.
    
    Args:
        friction: Friction coefficient (drag)
        
    Returns:
        Color name string for UI display
    """
    if friction < 0.7:
        return ETHER_ENERGY_COLORS["very_low_drag"]
    elif friction < 0.85:
        return ETHER_ENERGY_COLORS["low_drag"]
    elif friction < 0.95:
        return ETHER_ENERGY_COLORS["mild_enhancement"]
    elif friction < 1.05:
        return ETHER_ENERGY_COLORS["neutral"]
    elif friction < 1.3:
        return ETHER_ENERGY_COLORS["mild_drag"]
    elif friction < 1.6:
        return ETHER_ENERGY_COLORS["moderate_drag"]
    elif friction < 2.0:
        return ETHER_ENERGY_COLORS["high_drag"]
    else:
        return ETHER_ENERGY_COLORS["very_high_drag"]
