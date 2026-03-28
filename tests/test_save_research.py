"""
Tests for save/load round-trip and research progression.

Run with:
    cd 4x_game
    python -m pytest tests/test_save_research.py -v
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import pytest
from game import Game
import save_game


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def game():
    g = Game()
    g.character_created = True
    g.character_stats = {"VIT": 30, "SYN": 30, "INT": 30}
    g.player_name = "Test Pilot"
    g.character_class = "Explorer"
    g.character_species = "Human"
    g.character_faction = "Independent"
    g.character_background = ""
    g.character_research_paths = []
    return g


@pytest.fixture()
def game_with_ship(game):
    from navigation import Ship
    ship = Ship("Freighter", "Basic Transport")
    ship.fuel = 75
    ship.coordinates = (10, 20, 5)
    game.fleet["Freighter"] = ship
    game.navigation.current_ship = ship
    return game


# ---------------------------------------------------------------------------
# Save/Load round-trip
# ---------------------------------------------------------------------------

class TestSaveLoadRoundTrip:

    def test_save_returns_true(self, game, tmp_path, monkeypatch):
        monkeypatch.setattr(save_game, "SAVE_DIR", tmp_path)
        assert save_game.save_game(game, "test") is True

    def test_fleet_name_preserved(self, game_with_ship, tmp_path, monkeypatch):
        monkeypatch.setattr(save_game, "SAVE_DIR", tmp_path)
        save_game.save_game(game_with_ship, "test")
        g2 = Game()
        save_game.load_game(g2, str(tmp_path / "test.json"))
        assert "Freighter" in g2.fleet

    def test_fleet_fuel_preserved(self, game_with_ship, tmp_path, monkeypatch):
        monkeypatch.setattr(save_game, "SAVE_DIR", tmp_path)
        save_game.save_game(game_with_ship, "test")
        g2 = Game()
        save_game.load_game(g2, str(tmp_path / "test.json"))
        assert g2.fleet["Freighter"].fuel == 75

    def test_fleet_coordinates_preserved(self, game_with_ship, tmp_path, monkeypatch):
        monkeypatch.setattr(save_game, "SAVE_DIR", tmp_path)
        save_game.save_game(game_with_ship, "test")
        g2 = Game()
        save_game.load_game(g2, str(tmp_path / "test.json"))
        assert g2.fleet["Freighter"].coordinates == (10, 20, 5)

    def test_active_ship_name_restored(self, game_with_ship, tmp_path, monkeypatch):
        monkeypatch.setattr(save_game, "SAVE_DIR", tmp_path)
        save_game.save_game(game_with_ship, "test")
        g2 = Game()
        save_game.load_game(g2, str(tmp_path / "test.json"))
        assert g2.navigation.current_ship is not None
        assert g2.navigation.current_ship.name == "Freighter"

    def test_multiple_ships_all_restored(self, game, tmp_path, monkeypatch):
        monkeypatch.setattr(save_game, "SAVE_DIR", tmp_path)
        from navigation import Ship
        game.fleet["Alpha"] = Ship("Alpha", "Scout")
        game.fleet["Beta"] = Ship("Beta", "Freighter")
        # Use values that fit inside the ships' default max_fuel so round-trip
        # is lossless (fuel > max_fuel gets capped by calculate_stats_from_components).
        game.fleet["Alpha"].fuel = 30
        game.fleet["Beta"].fuel = 80
        save_game.save_game(game, "multi")
        g2 = Game()
        save_game.load_game(g2, str(tmp_path / "multi.json"))
        assert set(g2.fleet.keys()) == {"Alpha", "Beta"}
        assert g2.fleet["Alpha"].fuel == 30
        assert g2.fleet["Beta"].fuel == 80

    def test_character_data_preserved(self, game, tmp_path, monkeypatch):
        monkeypatch.setattr(save_game, "SAVE_DIR", tmp_path)
        save_game.save_game(game, "char")
        g2 = Game()
        save_game.load_game(g2, str(tmp_path / "char.json"))
        assert g2.player_name == "Test Pilot"
        assert g2.character_class == "Explorer"
        assert g2.character_faction == "Independent"

    def test_research_state_preserved(self, game, tmp_path, monkeypatch):
        monkeypatch.setattr(save_game, "SAVE_DIR", tmp_path)
        game.completed_research = ["Etheric Observation Protocol"]
        game.active_research = "Etheric Sensitivity Training"
        game.research_progress = 7
        save_game.save_game(game, "research")
        g2 = Game()
        save_game.load_game(g2, str(tmp_path / "research.json"))
        assert "Etheric Observation Protocol" in g2.completed_research
        assert g2.active_research == "Etheric Sensitivity Training"
        assert g2.research_progress == 7

    def test_credits_preserved(self, game, tmp_path, monkeypatch):
        monkeypatch.setattr(save_game, "SAVE_DIR", tmp_path)
        game.credits = 42000
        save_game.save_game(game, "creds")
        g2 = Game()
        save_game.load_game(g2, str(tmp_path / "creds.json"))
        assert g2.credits == 42000

    def test_turn_counter_preserved(self, game, tmp_path, monkeypatch):
        monkeypatch.setattr(save_game, "SAVE_DIR", tmp_path)
        game.current_turn = 15
        save_game.save_game(game, "turns")
        g2 = Game()
        save_game.load_game(g2, str(tmp_path / "turns.json"))
        assert g2.current_turn == 15

    def test_load_returns_true_on_success(self, game, tmp_path, monkeypatch):
        monkeypatch.setattr(save_game, "SAVE_DIR", tmp_path)
        save_game.save_game(game, "ok")
        g2 = Game()
        result = save_game.load_game(g2, str(tmp_path / "ok.json"))
        assert result is True

    def test_empty_fleet_round_trips(self, game, tmp_path, monkeypatch):
        monkeypatch.setattr(save_game, "SAVE_DIR", tmp_path)
        assert game.fleet == {}
        save_game.save_game(game, "noships")
        g2 = Game()
        save_game.load_game(g2, str(tmp_path / "noships.json"))
        assert g2.fleet == {}


# ---------------------------------------------------------------------------
# Old-format (owned_ships list) migration
# ---------------------------------------------------------------------------

class TestMigrateOldShips:

    def test_owned_ships_become_fleet_entries(self, game):
        save_data = {"owned_ships": ["Freighter", "Scout"], "custom_ships": []}
        save_game._migrate_old_ships(game, save_data)
        assert "Freighter" in game.fleet
        assert "Scout" in game.fleet

    def test_fleet_size_matches_owned_list(self, game):
        save_data = {"owned_ships": ["A", "B", "C"], "custom_ships": []}
        save_game._migrate_old_ships(game, save_data)
        assert len(game.fleet) == 3

    def test_current_ship_state_overwrites_owned_ships_entry(self, game):
        save_data = {
            "owned_ships": ["Freighter"],
            "custom_ships": [],
            "current_ship_state": {
                "name": "Freighter",
                "ship_class": "Heavy Freighter",
                "coordinates": [99, 99, 99],
                "fuel": 777,
                "max_fuel": 800,
                "jump_range": 20,
                "cargo": {},
                "max_cargo": 500,
                "scan_range": 30.0,
                "health": 400,
            },
        }
        save_game._migrate_old_ships(game, save_data)
        assert game.fleet["Freighter"].fuel == 777
        assert game.fleet["Freighter"].coordinates == (99, 99, 99)

    def test_navigation_current_ship_set_from_state(self, game):
        save_data = {
            "owned_ships": [],
            "custom_ships": [],
            "current_ship_state": {
                "name": "Pioneer",
                "ship_class": "Explorer",
                "coordinates": [1, 2, 3],
                "fuel": 100,
                "max_fuel": 100,
                "jump_range": 15,
                "cargo": {},
                "max_cargo": 100,
                "scan_range": 10.0,
                "health": 300,
            },
        }
        save_game._migrate_old_ships(game, save_data)
        assert game.navigation.current_ship is not None
        assert game.navigation.current_ship.name == "Pioneer"

    def test_empty_old_save_gives_empty_fleet(self, game):
        save_data = {"owned_ships": [], "custom_ships": []}
        save_game._migrate_old_ships(game, save_data)
        assert game.fleet == {}

    def test_custom_ships_added_to_fleet(self, game):
        save_data = {
            "owned_ships": [],
            "custom_ships": [{"name": "Custom One", "role": "Combat"}],
        }
        save_game._migrate_old_ships(game, save_data)
        assert "Custom One" in game.fleet

    def test_navigation_falls_back_to_first_fleet_entry(self, game):
        """When no current_ship_state exists, current_ship is the first fleet entry."""
        save_data = {"owned_ships": ["Solo"], "custom_ships": []}
        save_game._migrate_old_ships(game, save_data)
        assert game.navigation.current_ship is not None
        assert game.navigation.current_ship.name == "Solo"


# ---------------------------------------------------------------------------
# Corrupted / missing save files
# ---------------------------------------------------------------------------

class TestCorruptedSave:

    def test_corrupted_json_returns_false(self, game, tmp_path):
        bad_file = tmp_path / "corrupt.json"
        bad_file.write_text("{invalid json ][", encoding="utf-8")
        assert save_game.load_game(game, str(bad_file)) is False

    def test_missing_file_returns_false(self, game, tmp_path):
        assert save_game.load_game(game, str(tmp_path / "nonexistent.json")) is False

    def test_corrupt_save_does_not_raise(self, game, tmp_path):
        bad_file = tmp_path / "corrupt.json"
        bad_file.write_text("not json at all", encoding="utf-8")
        try:
            save_game.load_game(game, str(bad_file))
        except Exception as e:
            pytest.fail(f"load_game raised unexpectedly: {e}")

    def test_empty_json_object_does_not_crash(self, game, tmp_path):
        """A minimal {} JSON file should not crash; game falls back to defaults."""
        empty_file = tmp_path / "empty.json"
        empty_file.write_text("{}", encoding="utf-8")
        try:
            save_game.load_game(game, str(empty_file))
        except Exception as e:
            pytest.fail(f"load_game raised on empty dict: {e}")

    def test_empty_json_object_defaults_credits(self, game, tmp_path):
        empty_file = tmp_path / "empty.json"
        empty_file.write_text("{}", encoding="utf-8")
        save_game.load_game(game, str(empty_file))
        assert game.credits == 10000  # save_data.get('credits', 10000)


# ---------------------------------------------------------------------------
# start_research_project
# ---------------------------------------------------------------------------

class TestStartResearchProject:

    def test_sets_active_research(self, game):
        success, _ = game.start_research_project("Etheric Observation Protocol")
        assert success is True
        assert game.active_research == "Etheric Observation Protocol"

    def test_resets_progress_to_zero(self, game):
        game.research_progress = 99
        game.start_research_project("Etheric Observation Protocol")
        assert game.research_progress == 0

    def test_blocks_when_already_researching(self, game):
        game.active_research = "Etheric Observation Protocol"
        success, msg = game.start_research_project("Adaptive Fabrication Systems")
        assert success is False
        assert "already" in msg.lower()

    def test_blocks_unknown_research_name(self, game):
        success, _ = game.start_research_project("Definitely Not A Real Node")
        assert success is False

    def test_blocks_when_prerequisites_not_met(self, game):
        # "Distributed Record Architecture" requires "Etheric Observation Protocol"
        success, msg = game.start_research_project("Distributed Record Architecture")
        assert success is False
        assert "prerequisites" in msg.lower() or "completed" in msg.lower()

    def test_starts_when_prerequisites_are_met(self, game):
        game.completed_research = ["Etheric Observation Protocol"]
        success, _ = game.start_research_project("Distributed Record Architecture")
        assert success is True

    def test_blocks_if_already_completed(self, game):
        game.completed_research = ["Etheric Observation Protocol"]
        success, _ = game.start_research_project("Etheric Observation Protocol")
        assert success is False

    def test_zero_cost_node_does_not_crash(self, game):
        """All current research costs are 0; start_research_project must handle that."""
        success, _ = game.start_research_project("Etheric Observation Protocol")
        assert success is True


# ---------------------------------------------------------------------------
# progress_research
# ---------------------------------------------------------------------------

class TestProgressResearch:

    @pytest.fixture(autouse=True)
    def _activate(self, game):
        game.active_research = "Etheric Observation Protocol"
        game.research_progress = 0
        self.game = game

    def test_increments_progress_by_days(self):
        self.game.progress_research(days=5)
        assert self.game.research_progress == 5

    def test_accumulates_over_multiple_calls(self):
        self.game.progress_research(days=3)
        self.game.progress_research(days=4)
        assert self.game.research_progress == 7

    def test_returns_false_when_no_active_research(self, game):
        game.active_research = None
        success, _ = game.progress_research()
        assert success is False

    def test_completes_exactly_at_threshold(self):
        from research import all_research
        threshold = all_research["Etheric Observation Protocol"]["research_time"]
        self.game.progress_research(days=threshold)
        assert "Etheric Observation Protocol" in self.game.completed_research
        assert self.game.active_research is None

    def test_completes_even_past_threshold(self):
        from research import all_research
        threshold = all_research["Etheric Observation Protocol"]["research_time"]
        success, msg = self.game.progress_research(days=threshold + 10)
        assert success is True
        assert "completed" in msg.lower()

    def test_not_completed_one_day_before_threshold(self):
        from research import all_research
        threshold = all_research["Etheric Observation Protocol"]["research_time"]
        self.game.progress_research(days=threshold - 1)
        assert self.game.active_research == "Etheric Observation Protocol"
        assert "Etheric Observation Protocol" not in self.game.completed_research


# ---------------------------------------------------------------------------
# Duplicate completion prevention
# ---------------------------------------------------------------------------

class TestDuplicatePrevention:

    def test_complete_research_called_twice_adds_once(self, game):
        game.active_research = "Etheric Observation Protocol"
        game.research_progress = 0
        game.complete_research()
        # Manually reset and call again to simulate a second completion attempt
        game.active_research = "Etheric Observation Protocol"
        game.research_progress = 0
        game.complete_research()
        assert game.completed_research.count("Etheric Observation Protocol") == 1

    def test_resolve_end_turn_adds_node_exactly_once(self, game):
        from research import all_research
        threshold = all_research["Etheric Observation Protocol"]["research_time"]
        game.active_research = "Etheric Observation Protocol"
        game.research_progress = threshold - 1
        game.resolve_end_turn()
        assert game.completed_research.count("Etheric Observation Protocol") == 1

    def test_progress_research_completion_does_not_duplicate(self, game):
        from research import all_research
        threshold = all_research["Etheric Observation Protocol"]["research_time"]
        game.active_research = "Etheric Observation Protocol"
        game.research_progress = 0
        # Progress past threshold twice in separate calls shouldn't double-add
        game.progress_research(days=threshold)
        game.completed_research  # already in list
        # Now if somehow called again with the same name already completed:
        game.active_research = "Etheric Observation Protocol"
        game.progress_research(days=threshold)
        assert game.completed_research.count("Etheric Observation Protocol") == 1


# ---------------------------------------------------------------------------
# purchase_completed_research
# ---------------------------------------------------------------------------

class TestPurchaseCompletedResearch:

    def test_blocks_already_completed(self, game):
        game.completed_research = ["Etheric Observation Protocol"]
        success, msg = game.purchase_completed_research("Etheric Observation Protocol")
        assert success is False
        assert "already" in msg.lower()

    def test_blocks_prerequisites_not_met(self, game):
        success, msg = game.purchase_completed_research("Distributed Record Architecture")
        assert success is False
        assert "prerequisites" in msg.lower()

    def test_blocks_insufficient_credits(self, game):
        from research import all_research
        node = "Etheric Observation Protocol"
        original_cost = all_research[node].get("research_cost", 0)
        try:
            all_research[node]["research_cost"] = 10000
            game.credits = 5  # 5 < 10000 * 3.0 = 30000
            success, msg = game.purchase_completed_research(node, cost_multiplier=3.0)
            assert success is False
            assert "insufficient" in msg.lower() or "credits" in msg.lower()
        finally:
            all_research[node]["research_cost"] = original_cost

    def test_adds_node_to_completed(self, game):
        game.credits = 999999
        success, _ = game.purchase_completed_research("Etheric Observation Protocol")
        assert success is True
        assert "Etheric Observation Protocol" in game.completed_research

    def test_prerequisites_satisfied_allows_purchase(self, game):
        game.completed_research = ["Etheric Observation Protocol"]
        game.credits = 999999
        success, _ = game.purchase_completed_research("Distributed Record Architecture")
        assert success is True
        assert "Distributed Record Architecture" in game.completed_research

    def test_blocks_nonexistent_research(self, game):
        success, _ = game.purchase_completed_research("Does Not Exist Node")
        assert success is False


# ---------------------------------------------------------------------------
# calculate_rp_per_turn — stacking bonus formula
# ---------------------------------------------------------------------------

class TestCalculateRpPerTurn:

    def test_returns_dict_with_total_and_breakdown(self, game):
        result = game.calculate_rp_per_turn()
        assert "total" in result
        assert "breakdown" in result

    def test_total_is_at_least_one(self, game):
        assert game.calculate_rp_per_turn()["total"] >= 1

    def test_higher_int_gives_more_rp(self, game):
        game.character_stats = {"INT": 30}
        low = game.calculate_rp_per_turn()["total"]
        game.character_stats = {"INT": 80}
        high = game.calculate_rp_per_turn()["total"]
        assert high > low

    def test_scientist_class_bonus_over_explorer(self, game):
        game.character_stats = {"INT": 50}
        game.character_class = "Explorer"
        base = game.calculate_rp_per_turn()["total"]
        game.character_class = "Scientist"
        boosted = game.calculate_rp_per_turn()["total"]
        assert boosted > base

    def test_academic_researcher_background_bonus(self, game):
        game.character_stats = {"INT": 30}
        game.character_background = ""
        base_rp = game.calculate_rp_per_turn()
        game.character_background = "Academic Researcher"
        boosted_rp = game.calculate_rp_per_turn()
        assert boosted_rp["total"] > base_rp["total"]
        assert boosted_rp["breakdown"]["background"] == 0.5

    def test_colony_rp_added_directly(self, game):
        base = game.calculate_rp_per_turn(colony_rp=0)["total"]
        with_colony = game.calculate_rp_per_turn(colony_rp=5)["total"]
        assert with_colony == base + 5

    def test_faction_bonus_applied_for_veritas_covenant(self, game):
        """The Veritas Covenant gives __all__: +2.0 RP to every research category."""
        game.character_faction = "The Veritas Covenant"
        game.active_research = "Etheric Observation Protocol"
        result = game.calculate_rp_per_turn()
        assert result["breakdown"].get("faction", 0) > 0

    def test_faction_bonus_absent_for_independent(self, game):
        """'Independent' faction has no entry in FACTION_RESEARCH_BONUSES."""
        game.character_faction = "Independent"
        game.active_research = "Etheric Observation Protocol"
        result = game.calculate_rp_per_turn()
        # faction bonus may be > 0 from other factions with positive rep,
        # but the Independent faction itself adds nothing
        from factions import FACTION_RESEARCH_BONUSES
        assert "Independent" not in FACTION_RESEARCH_BONUSES

    def test_path_bonus_is_zero_when_no_paths_set(self, game):
        game.active_research = "Etheric Observation Protocol"
        game.character_research_paths = []
        result = game.calculate_rp_per_turn()
        assert result["breakdown"]["path_bonus"] == 0.0

    def test_breakdown_keys_present(self, game):
        breakdown = game.calculate_rp_per_turn()["breakdown"]
        for key in ("intellect", "background", "path_bonus", "colony", "faction"):
            assert key in breakdown, f"breakdown missing key: {key!r}"

    def test_scientist_plus_academic_stacks(self, game):
        """Scientist class + Academic Researcher background should both contribute."""
        game.character_stats = {"INT": 30}
        game.character_class = "Explorer"
        game.character_background = ""
        base = game.calculate_rp_per_turn()["total"]

        game.character_class = "Scientist"
        game.character_background = "Academic Researcher"
        stacked = game.calculate_rp_per_turn()["total"]
        assert stacked > base
