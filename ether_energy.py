"""
Ether Energy System - Cosmic Friction Zones

Represents different types of ether energies and cosmic energies throughout space
that affect fuel efficiency. These zones create "friction" that either reduces
or enhances fuel efficiency during travel.
"""

import random
import math
from typing import Tuple, Optional, Dict, List


class EtherEnergyZone:
    """Represents a zone of ether energy with a friction coefficient"""
    
    def __init__(self, center: Tuple[int, int, int], radius: float, friction: float, name: str):
        """
        Args:
            center: (x, y, z) coordinates of zone center
            radius: Radius of the zone in units
            friction: Friction coefficient (0.5-2.0)
                     - < 1.0 = enhances fuel efficiency (less fuel needed)
                     - 1.0 = neutral (no effect)
                     - > 1.0 = reduces fuel efficiency (more fuel needed)
            name: Name/type of the ether energy zone
        """
        self.center = center
        self.radius = radius
        self.friction = friction
        self.name = name
        self.base_radius = radius  # Store original radius for stability
        self.base_center = center  # Store original center for stability
    
    def contains(self, x: int, y: int, z: int) -> bool:
        """Check if coordinates are within this zone"""
        cx, cy, cz = self.center
        distance = math.sqrt((x - cx)**2 + (y - cy)**2 + (z - cz)**2)
        return distance <= self.radius
    
    def get_friction_at(self, x: int, y: int, z: int) -> Optional[float]:
        """Get friction coefficient at given coordinates, or None if outside zone"""
        if self.contains(x, y, z):
            # Calculate distance from center for gradient effect
            cx, cy, cz = self.center
            distance = math.sqrt((x - cx)**2 + (y - cy)**2 + (z - cz)**2)
            
            # Stronger effect at center, weaker at edges
            if distance == 0:
                return self.friction
            else:
                # Linear falloff from center to edge
                intensity = 1.0 - (distance / self.radius)
                # Blend between friction and neutral (1.0)
                return 1.0 + (self.friction - 1.0) * intensity
        return None
    
    def drift(self, max_drift: float = 2.0):
        """Slightly move zone boundaries (for dynamic but stable zones)"""
        # Small random drift in center position
        cx, cy, cz = self.center
        drift_x = random.uniform(-max_drift, max_drift)
        drift_y = random.uniform(-max_drift, max_drift)
        drift_z = random.uniform(-max_drift * 0.5, max_drift * 0.5)
        
        # Keep within reasonable bounds of original center
        new_cx = max(self.base_center[0] - 5, min(self.base_center[0] + 5, cx + drift_x))
        new_cy = max(self.base_center[1] - 5, min(self.base_center[1] + 5, cy + drift_y))
        new_cz = max(self.base_center[2] - 2, min(self.base_center[2] + 2, cz + drift_z))
        
        self.center = (int(new_cx), int(new_cy), int(new_cz))
        
        # Small random variation in radius
        radius_drift = random.uniform(-1.0, 1.0)
        self.radius = max(self.base_radius * 0.9, min(self.base_radius * 1.1, self.radius + radius_drift))


class EtherEnergySystem:
    """Manages ether energy zones throughout the galaxy"""
    
    def __init__(self, galaxy_size_x: int, galaxy_size_y: int, galaxy_size_z: int):
        """
        Initialize ether energy system for a galaxy
        
        Args:
            galaxy_size_x: Width of galaxy
            galaxy_size_y: Height of galaxy
            galaxy_size_z: Depth of galaxy
        """
        self.galaxy_size_x = galaxy_size_x
        self.galaxy_size_y = galaxy_size_y
        self.galaxy_size_z = galaxy_size_z
        self.zones: List[EtherEnergyZone] = []
        self.drift_counter = 0
        self._generate_zones()
    
    def _generate_zones(self):
        """Generate ether energy zones throughout the galaxy"""
        # Zone types with their friction characteristics
        zone_types = [
            # Low friction zones (enhance fuel efficiency)
            ("Void Current", 0.6, 0.7),  # Strong enhancement
            ("Ether Stream", 0.75, 0.85),  # Moderate enhancement
            ("Cosmic Breeze", 0.85, 0.95),  # Mild enhancement
            
            # High friction zones (reduce fuel efficiency)
            ("Flux Storm", 1.3, 1.5),  # Moderate penalty
            ("Etheric Turbulence", 1.5, 1.8),  # Strong penalty
            ("Void Rift", 1.8, 2.2),  # Very strong penalty
            
            # Neutral zones (slight variation)
            ("Stable Ether", 0.95, 1.05),  # Nearly neutral
        ]
        
        # Generate 15-25 zones
        num_zones = random.randint(15, 25)
        
        for i in range(num_zones):
            # Random position in galaxy
            x = random.randint(50, self.galaxy_size_x - 50)
            y = random.randint(50, self.galaxy_size_y - 50)
            z = random.randint(10, self.galaxy_size_z - 10)
            
            # Random zone type
            name, min_friction, max_friction = random.choice(zone_types)
            friction = random.uniform(min_friction, max_friction)
            
            # Random radius (20-80 units)
            radius = random.uniform(20, 80)
            
            zone = EtherEnergyZone((x, y, z), radius, friction, name)
            self.zones.append(zone)
    
    def get_friction_at(self, x: int, y: int, z: int) -> float:
        """
        Get combined friction coefficient at given coordinates
        
        Returns:
            Friction coefficient (0.5-2.0)
            - < 1.0 = enhances fuel efficiency
            - 1.0 = neutral
            - > 1.0 = reduces fuel efficiency
        """
        # Check all zones and combine their effects
        frictions = []
        for zone in self.zones:
            friction = zone.get_friction_at(x, y, z)
            if friction is not None:
                frictions.append(friction)
        
        if not frictions:
            return 1.0  # Neutral if no zones overlap
        
        # Average overlapping zones (could use other combination methods)
        combined_friction = sum(frictions) / len(frictions)
        
        # Clamp to reasonable range
        return max(0.5, min(2.0, combined_friction))
    
    def get_zone_at(self, x: int, y: int, z: int) -> Optional[EtherEnergyZone]:
        """Get the primary zone at given coordinates (strongest effect)"""
        best_zone = None
        best_friction = 0.0
        
        for zone in self.zones:
            friction = zone.get_friction_at(x, y, z)
            if friction is not None and abs(friction - 1.0) > abs(best_friction - 1.0):
                best_zone = zone
                best_friction = friction
        
        return best_zone
    
    def get_friction_level(self, friction: float) -> str:
        """
        Get a human-readable description of friction level
        
        Returns:
            Description string like "Low Drag", "High Drag", etc.
        """
        if friction < 0.7:
            return "Very Low Drag"
        elif friction < 0.85:
            return "Low Drag"
        elif friction < 0.95:
            return "Mild Enhancement"
        elif friction < 1.05:
            return "Neutral"
        elif friction < 1.3:
            return "Mild Drag"
        elif friction < 1.6:
            return "Moderate Drag"
        elif friction < 2.0:
            return "High Drag"
        else:
            return "Very High Drag"
    
    def update(self):
        """Update zones (drift boundaries slightly)"""
        self.drift_counter += 1
        
        # Drift zones every 10 updates (keeps them relatively stable)
        if self.drift_counter % 10 == 0:
            for zone in self.zones:
                zone.drift(max_drift=2.0)
    
    def get_zones_in_region(self, min_x: int, min_y: int, min_z: int,
                            max_x: int, max_y: int, max_z: int) -> List[EtherEnergyZone]:
        """Get all zones that overlap with a region"""
        result = []
        for zone in self.zones:
            cx, cy, cz = zone.center
            # Check if zone center is in region or zone overlaps region
            if (min_x <= cx <= max_x and min_y <= cy <= max_y and min_z <= cz <= max_z):
                result.append(zone)
            # Also check if zone extends into region
            elif (cx - zone.radius <= max_x and cx + zone.radius >= min_x and
                  cy - zone.radius <= max_y and cy + zone.radius >= min_y and
                  cz - zone.radius <= max_z and cz + zone.radius >= min_z):
                result.append(zone)
        return result

