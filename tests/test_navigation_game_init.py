"""
Tier-2 tests: fuel consumption, jump validation, game initialization,
and fleet mutation (create / delete / rename).

Run with:
    cd 4x_game
    python -m pytest tests/test_navigation_game_init.py -v
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import math
import pytest
import unittest.mock as mock
from navigation import Ship, calculate_fuel_consumption
from game import Game


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_ship(efficiency=30.0, output=30.0, crew=30.0, coords=(50, 50, 25), fuel=200):
    """Return a Ship whose attribute_profile is fully under test control."""
    ship = Ship("TestShip")
    ship.attribute_profile = {
        "engine_efficiency": efficiency,
        "engine_output": output,
        "crew_efficiency": crew,
    }
    ship.coordinates = coords
    ship.fuel = fuel
    return ship


def _game_no_ether(dangerous=False):
    """Minimal game mock: ether disabled, danger flag controllable."""
    g = mock.MagicMock()
    g.navigation.galaxy.ether_energy = None       # skip ether path entirely
    g.event_system.is_location_dangerous.return_value = dangerous
    return g


def _game_with_ether(friction, dangerous=False):
    """Minimal game mock: ether friction at a fixed uniform value."""
    g = mock.MagicMock()
    g.navigation.galaxy.ether_energy.get_friction_at.return_value = float(friction)
    g.event_system.is_location_dangerous.return_value = dangerous
    return g


# ---------------------------------------------------------------------------
# calculate_fuel_consumption — formula verification
# ---------------------------------------------------------------------------

class TestCalculateFuelConsumption:

    # ── baseline ─────────────────────────────────────────────────────────────

    def test_baseline_distance_5(self):
        """dist=5, all defaults (efficiency=30): base_fuel=10, all mults=1.0 → 10."""
        ship = _make_ship()
        assert calculate_fuel_consumption(ship, 5.0) == 10

    def test_baseline_scales_linearly_with_distance(self):
        """Doubling distance doubles fuel at baseline."""
        ship = _make_ship()
        assert calculate_fuel_consumption(ship, 10.0) == calculate_fuel_consumption(ship, 5.0) * 2

    def test_minimum_result_is_one(self):
        """Even a tiny distance returns at least 1 fuel."""
        ship = _make_ship()
        assert calculate_fuel_consumption(ship, 0.001) >= 1

    # ── engine efficiency multiplier ─────────────────────────────────────────

    def test_high_efficiency_reduces_fuel(self):
        """efficiency=80 → multiplier 0.5x  →  5 fuel for dist=5."""
        ship = _make_ship(efficiency=80.0)
        # eff_mult = clamp(1 - (80-30)/100) = clamp(0.5) = 0.5
        # fuel = 5*2 * 0.5 * crew_1.0 * out_1.0 = 5
        assert calculate_fuel_consumption(ship, 5.0) == 5

    def test_low_efficiency_increases_fuel(self):
        """efficiency=10 → multiplier 1.2x  →  12 fuel for dist=5."""
        ship = _make_ship(efficiency=10.0)
        # eff_mult = clamp(1 - (10-30)/100) = clamp(1.2) = 1.2
        assert calculate_fuel_consumption(ship, 5.0) == 12

    def test_efficiency_clamped_at_max_1_5(self):
        """Efficiency below -20 clamps the multiplier at 1.5×; both -20 and -100 give same result.

        Formula: mult = 1.0 - ((e-30)/100).  At e=-20: mult = 1.5 (ceiling).
        At e=-100: unclamped mult would be 2.3, clamped to 1.5.
        """
        ship_at_ceil  = _make_ship(efficiency=-20.0)  # exactly at ceiling
        ship_way_low  = _make_ship(efficiency=-100.0) # would be 2.3 unclamped
        assert calculate_fuel_consumption(ship_at_ceil, 5.0) == calculate_fuel_consumption(ship_way_low, 5.0)

    def test_efficiency_clamped_at_50_percent_upper(self):
        """Even 100 efficiency can't go below 0.5× (ceiling clamped)."""
        ship_max  = _make_ship(efficiency=100.0)
        ship_over = _make_ship(efficiency=200.0)
        assert calculate_fuel_consumption(ship_max, 5.0) == calculate_fuel_consumption(ship_over, 5.0)

    # ── engine output modifier ───────────────────────────────────────────────

    def test_high_output_adds_10pct_penalty(self):
        """output>50 adds a 1.1× multiplier: dist=5, eff=30 → 10 * 1.1 = 11."""
        ship = _make_ship(output=60.0)
        assert calculate_fuel_consumption(ship, 5.0) == 11

    def test_low_output_gives_10pct_bonus(self):
        """output<10 applies a 0.9× multiplier: dist=5, eff=30 → 10 * 0.9 = 9."""
        ship = _make_ship(output=5.0)
        assert calculate_fuel_consumption(ship, 5.0) == 9

    def test_mid_output_no_modifier(self):
        """10 ≤ output ≤ 50 → output_multiplier = 1.0 (no change)."""
        base = calculate_fuel_consumption(_make_ship(output=30.0), 5.0)
        for out in (10.0, 30.0, 50.0):
            assert calculate_fuel_consumption(_make_ship(output=out), 5.0) == base

    # ── ether coefficient ────────────────────────────────────────────────────

    def test_ether_friction_2_doubles_fuel(self):
        """Uniform friction=2.0 → ether_coefficient=2.0 → fuel doubled."""
        ship = _make_ship(coords=(50, 50, 25))
        target = (55, 50, 25)
        base   = calculate_fuel_consumption(ship, 5.0)
        ether  = calculate_fuel_consumption(ship, 5.0, target, _game_with_ether(2.0))
        assert ether == base * 2

    def test_ether_friction_1_no_change(self):
        """Friction=1.0 is neutral; result equals no-ether baseline."""
        ship = _make_ship(coords=(50, 50, 25))
        target = (55, 50, 25)
        base  = calculate_fuel_consumption(ship, 5.0)
        same  = calculate_fuel_consumption(ship, 5.0, target, _game_with_ether(1.0))
        assert same == base

    def test_no_ether_when_ether_energy_is_none(self):
        """ether_energy=None skips the ether path; result equals baseline."""
        ship = _make_ship(coords=(50, 50, 25))
        target = (55, 50, 25)
        base = calculate_fuel_consumption(ship, 5.0)
        same = calculate_fuel_consumption(ship, 5.0, target, _game_no_ether())
        assert same == base

    # ── dangerous region penalty ─────────────────────────────────────────────

    def test_dangerous_region_adds_50pct_penalty(self):
        """is_location_dangerous=True → fuel *= 1.5."""
        ship = _make_ship(coords=(50, 50, 25))
        target = (55, 50, 25)
        safe    = calculate_fuel_consumption(ship, 5.0, target, _game_no_ether(dangerous=False))
        danger  = calculate_fuel_consumption(ship, 5.0, target, _game_no_ether(dangerous=True))
        assert danger == pytest.approx(safe * 1.5, abs=1)

    def test_no_penalty_when_safe(self):
        """is_location_dangerous=False → same result as no game mock."""
        ship = _make_ship(coords=(50, 50, 25))
        target = (55, 50, 25)
        base = calculate_fuel_consumption(ship, 5.0)
        safe = calculate_fuel_consumption(ship, 5.0, target, _game_no_ether(dangerous=False))
        assert safe == base

    # ── combined modifiers ───────────────────────────────────────────────────

    def test_ether_and_danger_stack_multiplicatively(self):
        """friction=2.0 + danger → base * 2.0 * 1.5 = base * 3."""
        ship = _make_ship(coords=(50, 50, 25))
        target = (55, 50, 25)
        base  = calculate_fuel_consumption(ship, 5.0)
        combo = calculate_fuel_consumption(ship, 5.0, target, _game_with_ether(2.0, dangerous=True))
        assert combo == pytest.approx(base * 3, abs=1)

    def test_no_crash_without_game(self):
        """calculate_fuel_consumption(ship, dist) with no game/target must not raise."""
        ship = _make_ship()
        result = calculate_fuel_consumption(ship, 10.0)
        assert isinstance(result, int)


# ---------------------------------------------------------------------------
# Ship.can_jump_to / Ship.jump_to
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def galaxy():
    """Shared real galaxy (expensive to build — create once per module)."""
    return Game().navigation.galaxy


class TestCanJumpTo:

    def test_returns_true_within_range_with_fuel(self, galaxy):
        ship = _make_ship(coords=(50, 50, 25), fuel=200)
        ship.jump_range = 15
        target = (55, 50, 25)   # 5-unit jump
        assert ship.can_jump_to(target, galaxy) is True

    def test_returns_false_when_target_beyond_jump_range(self, galaxy):
        ship = _make_ship(coords=(50, 50, 25), fuel=200)
        ship.jump_range = 15
        target = (100, 50, 25)   # 50-unit jump
        assert ship.can_jump_to(target, galaxy) is False

    def test_returns_false_when_fuel_too_low(self, galaxy):
        ship = _make_ship(coords=(50, 50, 25), fuel=0)
        ship.jump_range = 15
        target = (55, 50, 25)
        assert ship.can_jump_to(target, galaxy) is False

    def test_returns_false_when_exactly_one_fuel_short(self, galaxy):
        ship = _make_ship(coords=(50, 50, 25))
        ship.jump_range = 15
        target = (55, 50, 25)
        fuel_needed = calculate_fuel_consumption(ship, 5.0)
        ship.fuel = fuel_needed - 1
        assert ship.can_jump_to(target, galaxy) is False

    def test_returns_true_with_exact_fuel_needed(self, galaxy):
        ship = _make_ship(coords=(50, 50, 25))
        ship.jump_range = 15
        target = (55, 50, 25)
        fuel_needed = calculate_fuel_consumption(ship, 5.0)
        ship.fuel = fuel_needed
        assert ship.can_jump_to(target, galaxy) is True


class TestJumpTo:

    def test_successful_jump_updates_coordinates(self, galaxy):
        ship = _make_ship(coords=(50, 50, 25), fuel=200)
        ship.jump_range = 15
        target = (55, 50, 25)
        success, _ = ship.jump_to(target, galaxy)
        assert success is True
        assert ship.coordinates == target

    def test_successful_jump_deducts_correct_fuel(self, galaxy):
        ship = _make_ship(coords=(50, 50, 25), fuel=200)
        ship.jump_range = 15
        target = (55, 50, 25)
        expected_cost = calculate_fuel_consumption(ship, 5.0)
        ship.jump_to(target, galaxy)
        assert ship.fuel == 200 - expected_cost

    def test_failed_jump_does_not_change_coordinates(self, galaxy):
        ship = _make_ship(coords=(50, 50, 25), fuel=200)
        ship.jump_range = 15
        target = (100, 50, 25)  # out of range
        ship.jump_to(target, galaxy)
        assert ship.coordinates == (50, 50, 25)

    def test_failed_jump_does_not_deduct_fuel(self, galaxy):
        ship = _make_ship(coords=(50, 50, 25), fuel=200)
        ship.jump_range = 15
        target = (100, 50, 25)
        ship.jump_to(target, galaxy)
        assert ship.fuel == 200

    def test_jump_returns_false_out_of_range(self, galaxy):
        ship = _make_ship(coords=(50, 50, 25), fuel=200)
        ship.jump_range = 15
        success, msg = ship.jump_to((100, 50, 25), galaxy)
        assert success is False

    def test_jump_returns_false_no_fuel(self, galaxy):
        ship = _make_ship(coords=(50, 50, 25), fuel=0)
        ship.jump_range = 15
        success, _ = ship.jump_to((55, 50, 25), galaxy)
        assert success is False

    def test_success_message_contains_fuel_used(self, galaxy):
        ship = _make_ship(coords=(50, 50, 25), fuel=200)
        ship.jump_range = 15
        _, msg = ship.jump_to((55, 50, 25), galaxy)
        assert "fuel" in msg.lower()

    def test_sequential_jumps_accumulate_fuel_cost(self, galaxy):
        ship = _make_ship(coords=(50, 50, 25), fuel=200)
        ship.jump_range = 20
        ship.jump_to((55, 50, 25), galaxy)
        fuel_after_first = ship.fuel
        ship.jump_to((60, 50, 25), galaxy)
        assert ship.fuel < fuel_after_first

    def test_fuel_never_goes_negative(self, galaxy):
        """Last successful jump must leave fuel ≥ 0."""
        ship = _make_ship(coords=(50, 50, 25), fuel=200)
        ship.jump_range = 20
        for _ in range(30):
            result, _ = ship.jump_to((55, 50, 25), galaxy)
            if not result:
                break
            ship.coordinates = (50, 50, 25)  # reset for next hop
        assert ship.fuel >= 0


# ---------------------------------------------------------------------------
# initialize_new_game — character and faction setup
# ---------------------------------------------------------------------------

@pytest.fixture()
def game():
    g = Game()
    return g


class TestInitializeNewGame:

    def _char(self, **overrides):
        base = {
            "name": "Commander Test",
            "character_class": "Explorer",
            "background": "Frontier Survivor",
            "species": "Terran",
            "faction": "",
            "research_paths": [],
        }
        base.update(overrides)
        return base

    def test_returns_true_on_success(self, game):
        assert game.initialize_new_game(self._char()) is True

    def test_sets_player_name(self, game):
        game.initialize_new_game(self._char(name="Alice"))
        assert game.player_name == "Alice"

    def test_sets_character_class(self, game):
        game.initialize_new_game(self._char(character_class="Scientist"))
        assert game.character_class == "Scientist"

    def test_sets_character_species(self, game):
        game.initialize_new_game(self._char(species="Silvan"))
        assert game.character_species == "Silvan"

    def test_sets_character_faction(self, game):
        game.initialize_new_game(self._char(faction="The Veritas Covenant"))
        assert game.character_faction == "The Veritas Covenant"

    def test_marks_character_as_created(self, game):
        game.initialize_new_game(self._char())
        assert game.character_created is True

    def test_faction_reputation_boosted_by_25(self, game):
        faction = "The Veritas Covenant"
        before = game.faction_system.player_relations.get(faction, 0)
        game.initialize_new_game(self._char(faction=faction))
        after = game.faction_system.player_relations.get(faction, 0)
        assert after == before + 25

    def test_only_chosen_faction_gets_reputation_boost(self, game):
        """Other factions must not receive the +25 starting bonus."""
        chosen = "The Veritas Covenant"
        other  = "Stellar Nexus Guild"
        before_other = game.faction_system.player_relations.get(other, 0)
        game.initialize_new_game(self._char(faction=chosen))
        after_other = game.faction_system.player_relations.get(other, 0)
        assert after_other == before_other

    def test_no_faction_boost_when_faction_empty(self, game):
        """Empty-string faction must not raise and must not modify any rep."""
        relations_before = dict(game.faction_system.player_relations)
        game.initialize_new_game(self._char(faction=""))
        assert game.faction_system.player_relations == relations_before

    def test_provided_stats_used_verbatim(self, game):
        stats = {"STR": 45, "INT": 60, "VIT": 25}
        game.initialize_new_game(self._char(stats=stats))
        assert game.character_stats == stats

    def test_default_stats_created_when_none_provided(self, game):
        game.initialize_new_game(self._char())
        assert isinstance(game.character_stats, dict)
        assert len(game.character_stats) > 0

    def test_research_paths_stored(self, game):
        paths = ["Quantum", "Engineering"]
        game.initialize_new_game(self._char(research_paths=paths))
        assert game.character_research_paths == paths

    def test_reinit_overwrites_previous_data(self, game):
        game.initialize_new_game(self._char(name="First"))
        game.initialize_new_game(self._char(name="Second"))
        assert game.player_name == "Second"


# ---------------------------------------------------------------------------
# create_custom_ship / delete_ship / rename_ship — fleet mutation atomicity
# ---------------------------------------------------------------------------

class TestCreateCustomShip:

    def test_ship_added_to_fleet(self, game):
        game.create_custom_ship("Pioneer")
        assert "Pioneer" in game.fleet

    def test_returns_success_true(self, game):
        success, _ = game.create_custom_ship("Voyager")
        assert success is True

    def test_ship_is_ship_instance(self, game):
        game.create_custom_ship("Titan")
        assert isinstance(game.fleet["Titan"], Ship)

    def test_ship_name_attribute_matches_key(self, game):
        game.create_custom_ship("Atlas")
        assert game.fleet["Atlas"].name == "Atlas"

    def test_blocks_duplicate_name(self, game):
        game.create_custom_ship("Nomad")
        success, msg = game.create_custom_ship("Nomad")
        assert success is False
        assert "exists" in msg.lower() or "already" in msg.lower()

    def test_blocks_empty_name(self, game):
        success, _ = game.create_custom_ship("")
        assert success is False

    def test_blocks_whitespace_only_name(self, game):
        success, _ = game.create_custom_ship("   ")
        assert success is False

    def test_role_passed_as_ship_class(self, game):
        game.create_custom_ship("Freighter", ship_role="Heavy Hauler")
        assert game.fleet["Freighter"].ship_class == "Heavy Hauler"

    def test_multiple_ships_can_be_created(self, game):
        game.create_custom_ship("Alpha")
        game.create_custom_ship("Beta")
        assert "Alpha" in game.fleet and "Beta" in game.fleet


class TestDeleteShip:

    def test_ship_removed_from_fleet(self, game):
        game.create_custom_ship("Doomed")
        game.delete_ship("Doomed")
        assert "Doomed" not in game.fleet

    def test_returns_success_true(self, game):
        game.create_custom_ship("ToBe")
        success, _ = game.delete_ship("ToBe")
        assert success is True

    def test_blocks_nonexistent_ship(self, game):
        success, msg = game.delete_ship("Phantom")
        assert success is False
        assert "not found" in msg.lower() or "Phantom" in msg

    def test_current_ship_cleared_when_active_ship_deleted(self, game):
        game.create_custom_ship("Active")
        game.set_active_ship("Active")
        assert game.navigation.current_ship is not None
        game.delete_ship("Active")
        assert game.navigation.current_ship is None

    def test_current_ship_unchanged_when_different_ship_deleted(self, game):
        game.create_custom_ship("Keep")
        game.create_custom_ship("Remove")
        game.set_active_ship("Keep")
        game.delete_ship("Remove")
        assert game.navigation.current_ship is not None
        assert game.navigation.current_ship.name == "Keep"

    def test_other_ships_unaffected(self, game):
        game.create_custom_ship("Survivor")
        game.create_custom_ship("Sacrificed")
        game.delete_ship("Sacrificed")
        assert "Survivor" in game.fleet


class TestRenameShip:

    def test_new_name_present_in_fleet(self, game):
        game.create_custom_ship("OldName")
        game.rename_ship("OldName", "NewName")
        assert "NewName" in game.fleet

    def test_old_name_absent_from_fleet(self, game):
        game.create_custom_ship("Original")
        game.rename_ship("Original", "Updated")
        assert "Original" not in game.fleet

    def test_ship_name_attribute_updated(self, game):
        game.create_custom_ship("Before")
        game.rename_ship("Before", "After")
        assert game.fleet["After"].name == "After"

    def test_returns_success_true(self, game):
        game.create_custom_ship("Alpha")
        success, _ = game.rename_ship("Alpha", "Omega")
        assert success is True

    def test_blocks_rename_to_existing_name(self, game):
        game.create_custom_ship("ShipA")
        game.create_custom_ship("ShipB")
        success, msg = game.rename_ship("ShipA", "ShipB")
        assert success is False
        assert "exists" in msg.lower() or "already" in msg.lower()

    def test_blocks_rename_nonexistent_ship(self, game):
        success, _ = game.rename_ship("Ghost", "NewGhost")
        assert success is False

    def test_blocks_empty_new_name(self, game):
        game.create_custom_ship("SomeName")
        success, _ = game.rename_ship("SomeName", "")
        assert success is False

    def test_current_ship_reference_updated_after_rename(self, game):
        """If the active ship is renamed, navigation.current_ship must reflect the rename."""
        game.create_custom_ship("ActiveShip")
        game.set_active_ship("ActiveShip")
        game.rename_ship("ActiveShip", "RenamedActive")
        current = game.navigation.current_ship
        assert current is not None
        assert current.name == "RenamedActive"

    def test_inactive_ship_rename_does_not_disturb_current_ship(self, game):
        game.create_custom_ship("Active2")
        game.create_custom_ship("Background")
        game.set_active_ship("Active2")
        game.rename_ship("Background", "NewBackground")
        assert game.navigation.current_ship.name == "Active2"

    def test_same_object_identity_preserved_after_rename(self, game):
        """The Ship object in the fleet after rename must be the original object."""
        game.create_custom_ship("SameObj")
        original = game.fleet["SameObj"]
        game.rename_ship("SameObj", "RenamedObj")
        assert game.fleet["RenamedObj"] is original
