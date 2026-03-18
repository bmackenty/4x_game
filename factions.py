"""
Faction System for 4X Game
Diplomatic relations, faction benefits, and political gameplay

All faction data is stored in lore/factions.json.
This module loads that file and exposes the same public API as before,
so all existing callers (game.py, backend/main.py, etc.) are unaffected.
"""

import json
import pathlib
import random

# ── Load raw data from lore/factions.json ─────────────────────────────────────
_LORE_PATH = pathlib.Path(__file__).parent / "lore" / "factions.json"

with _LORE_PATH.open(encoding="utf-8") as _f:
    _data = json.load(_f)

# ── Public data ────────────────────────────────────────────────────────────────

factions: dict = _data["factions"]

# Maps faction name → research category → bonus multiplier
FACTION_RESEARCH_BONUSES: dict = _data["faction_research_bonuses"]


# ── FactionSystem class ────────────────────────────────────────────────────────

class FactionSystem:
    def __init__(self):
        self.player_relations = {}     # faction_name: reputation_value
        self.faction_relations = {}    # faction_name: {other_faction: relationship}
        self.faction_territories = {}  # faction_name: [system_coordinates]
        self.faction_activities = {}   # faction_name: current_activity

        self.initialize_factions()
        self.initialize_relationships()

    def initialize_factions(self):
        """Initialize all faction data and player relations"""
        for faction_name in factions.keys():
            self.player_relations[faction_name] = random.randint(-10, 10)  # Neutral start
            self.faction_activities[faction_name] = self.get_random_activity(faction_name)

    def initialize_relationships(self):
        """Initialize inter-faction relationships"""
        faction_names = list(factions.keys())

        for faction in faction_names:
            self.faction_relations[faction] = {}
            for other_faction in faction_names:
                if faction != other_faction:
                    relationship = self.calculate_base_relationship(faction, other_faction)
                    self.faction_relations[faction][other_faction] = relationship

    def calculate_base_relationship(self, faction1, faction2):
        """Calculate base relationship between two factions"""
        faction1_data = factions[faction1]
        faction2_data = factions[faction2]

        # Similar philosophies create better relationships
        if faction1_data['philosophy'] == faction2_data['philosophy']:
            return random.randint(20, 50)

        # Compatible focuses
        compatible_focuses = {
            'Technology': ['Research', 'Industry'],
            'Research':   ['Technology', 'Exploration'],
            'Trade':      ['Diplomacy', 'Industry'],
            'Exploration':['Research', 'Mysticism'],
            'Industry':   ['Technology', 'Trade'],
            'Diplomacy':  ['Trade', 'Cultural'],
            'Cultural':   ['Diplomacy', 'Mysticism'],
            'Mysticism':  ['Cultural', 'Exploration']
        }

        faction1_focus = faction1_data['primary_focus']
        faction2_focus = faction2_data['primary_focus']

        if faction2_focus in compatible_focuses.get(faction1_focus, []):
            return random.randint(10, 30)
        elif faction1_focus == faction2_focus:
            return random.randint(-10, 20)  # Competition but understanding
        else:
            return random.randint(-20, 10)  # Neutral to mild dislike

    def get_random_activity(self, faction_name):
        """Get a random activity for a faction based on their focus"""
        faction_data = factions[faction_name]
        activities = faction_data['typical_activities']
        return random.choice(activities)

    def get_faction_info(self, faction_name):
        """Get complete information about a faction"""
        if faction_name not in factions:
            return None

        faction_data = factions[faction_name].copy()
        faction_data['player_reputation'] = self.player_relations.get(faction_name, 0)
        faction_data['current_activity']  = self.faction_activities.get(faction_name, "Unknown")
        faction_data['territory_count']   = len(self.faction_territories.get(faction_name, []))

        return faction_data

    def modify_reputation(self, faction_name, change, reason=""):
        """Modify player reputation with a faction"""
        if faction_name in self.player_relations:
            old_rep = self.player_relations[faction_name]
            self.player_relations[faction_name] = max(-100, min(100, old_rep + change))
            new_rep = self.player_relations[faction_name]
            return f"Reputation with {faction_name}: {old_rep} -> {new_rep} ({reason})"
        return f"Unknown faction: {faction_name}"

    def get_reputation_status(self, faction_name):
        """Get reputation status string"""
        rep = self.player_relations.get(faction_name, 0)

        if rep >= 75:
            return "Allied"
        elif rep >= 50:
            return "Friendly"
        elif rep >= 25:
            return "Cordial"
        elif rep >= -25:
            return "Neutral"
        elif rep >= -50:
            return "Unfriendly"
        elif rep >= -75:
            return "Hostile"
        else:
            return "Enemy"

    def get_faction_benefits(self, faction_name):
        """Get benefits available from a faction based on reputation"""
        rep = self.player_relations.get(faction_name, 0)
        faction_data = factions.get(faction_name, {})
        benefits = []

        if rep >= 25:  # Cordial or better
            benefits.extend(faction_data.get('low_rep_benefits', []))

        if rep >= 50:  # Friendly or better
            benefits.extend(faction_data.get('mid_rep_benefits', []))

        if rep >= 75:  # Allied
            benefits.extend(faction_data.get('high_rep_benefits', []))

        return benefits

    def get_faction_zone_benefits(self, faction_name, location_type='system'):
        """Get benefits for being in a faction's controlled space

        Args:
            faction_name:  Name of the controlling faction
            location_type: 'system', 'station', 'planet', or 'shipyard'

        Returns:
            dict with benefit descriptions and modifiers
        """
        rep = self.player_relations.get(faction_name, 0)
        faction_data = factions.get(faction_name, {})
        benefits = {
            'trade_discount':   0,
            'repair_discount':  0,
            'refuel_discount':  0,
            'research_bonus':   0,
            'shipyard_discount':0,
            'description':      []
        }

        # Base benefits for being in faction space (even with neutral rep)
        if rep >= -25:  # Neutral or better
            benefits['description'].append(f"You are in {faction_name} space")

            focus = faction_data.get('primary_focus', '')
            if focus == 'Trade':
                benefits['trade_discount'] = 5
                benefits['description'].append("Trade goods: -5% prices")
            elif focus in ('Technology', 'Industry'):
                benefits['repair_discount']   = 10
                benefits['shipyard_discount'] = 5
                benefits['description'].append("Repair: -10%, Shipyard: -5%")
            elif focus == 'Research':
                benefits['research_bonus'] = 10
                benefits['description'].append("Research speed: +10%")

        # Enhanced benefits for cordial relations
        if rep >= 25:
            benefits['trade_discount']  += 5
            benefits['refuel_discount']  = 10
            benefits['description'].append("Cordial status: Additional discounts")

        # Strong benefits for friendly relations
        if rep >= 50:
            benefits['trade_discount']    += 10
            benefits['repair_discount']   += 15
            benefits['refuel_discount']   += 10
            benefits['shipyard_discount'] += 10
            benefits['research_bonus']    += 15
            benefits['description'].append("Friendly status: Major discounts and bonuses")

        # Maximum benefits for allied status
        if rep >= 75:
            benefits['trade_discount']    += 15
            benefits['repair_discount']   += 20
            benefits['refuel_discount']   += 20
            benefits['shipyard_discount'] += 20
            benefits['research_bonus']    += 25
            benefits['description'].append("Allied status: Maximum benefits")

        # Location-specific bonuses
        if location_type == 'station' and rep >= 25:
            benefits['description'].append("Station access granted")
        elif location_type == 'shipyard' and rep >= 50:
            benefits['description'].append("Advanced ship modifications available")
        elif location_type == 'planet' and rep >= 50:
            benefits['description'].append("Colony support and trade privileges")

        return benefits

    def assign_faction_territories(self, galaxy):
        """Assign territories to factions across the galaxy"""
        systems = list(galaxy.systems.values())
        faction_names = list(factions.keys())

        # Clear existing territories
        self.faction_territories = {name: [] for name in faction_names}

        # Assign 1-3 systems to each faction randomly
        for faction_name in faction_names:
            num_systems = random.randint(1, 3)
            available_systems = [
                s for s in systems
                if not any(s['coordinates'] in territories
                           for territories in self.faction_territories.values())
            ]
            if available_systems:
                assigned = random.sample(available_systems, min(num_systems, len(available_systems)))
                self.faction_territories[faction_name] = [s['coordinates'] for s in assigned]

    def get_system_faction(self, coordinates):
        """Get the faction that controls a system"""
        for faction_name, territories in self.faction_territories.items():
            if coordinates in territories:
                return faction_name
        return None

    def update_faction_activities(self):
        """Update faction activities periodically"""
        for faction_name in factions.keys():
            if random.random() < 0.1:  # 10% chance to change activity
                self.faction_activities[faction_name] = self.get_random_activity(faction_name)

    def set_player_home_faction(self, faction_name, reputation=80):
        """
        Mark a faction as the player's home faction by setting their starting
        reputation to a strongly positive value (default 80 = Allied).

        Called once during new-game setup after the character is created.
        Future systems (quests, trades, missions) can call modify_reputation()
        to nudge this value up or down from here.

        Args:
            faction_name: The faction the player belongs to.
            reputation:   Starting reputation score (clamped to -100…100).
        """
        if faction_name not in self.player_relations:
            return
        self.player_relations[faction_name] = max(-100, min(100, reputation))
