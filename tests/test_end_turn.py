"""
Characterization tests for end-turn behavior.

These tests instantiate Game directly and call the same sequence the backend
endpoint calls, asserting on the results that are currently observed to be
correct.  They serve as a safety net: if a future change breaks the turn
flow, at least one test here should catch it.

Run with:
    cd 4x_game
    python -m pytest tests/test_end_turn.py -v
"""

import sys
import os

# Make the project root importable regardless of where pytest is invoked from.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from game import Game, hull_auto_repair_rate


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def game():
    """Minimal Game ready for play: character created, default stats."""
    g = Game()
    g.character_created = True
    g.character_stats = {"VIT": 30, "SYN": 30}
    g.player_name = "Test Pilot"
    g.character_class = "Explorer"
    g.character_species = "Human"
    g.character_faction = "Independent"
    return g


@pytest.fixture()
def game_with_research(game):
    """Game with an active research project that takes 20 turns."""
    game.active_research = "Etheric Observation Protocol"
    game.research_progress = 0
    return game


# ---------------------------------------------------------------------------
# end_turn() — turn counter and action-point reset
# ---------------------------------------------------------------------------

class TestEndTurn:

    def test_turn_number_starts_at_one(self, game):
        assert game.current_turn == 1

    def test_end_turn_increments_turn_number(self, game):
        game.end_turn()
        assert game.current_turn == 2

    def test_end_turn_increments_each_call(self, game):
        for expected in range(2, 6):
            game.end_turn()
            assert game.current_turn == expected

    def test_end_turn_returns_success_true(self, game):
        success, _ = game.end_turn()
        assert success is True

    def test_end_turn_message_contains_new_turn(self, game):
        _, msg = game.end_turn()
        assert "2" in msg  # new turn number appears in message

    def test_end_turn_resets_action_points(self, game):
        game.turn_actions_remaining = 0
        game.end_turn()
        assert game.turn_actions_remaining == game.max_actions_per_turn

    def test_end_turn_when_already_ended_returns_false(self, game):
        game.game_ended = True
        success, msg = game.end_turn()
        assert success is False
        assert "ended" in msg.lower()

    def test_end_turn_does_not_increment_when_already_ended(self, game):
        game.game_ended = True
        game.end_turn()
        assert game.current_turn == 1  # unchanged

    def test_max_turns_zero_means_unlimited(self, game):
        game.max_turns = 0
        for _ in range(100):
            game.end_turn()
        assert game.game_ended is False

    def test_max_turns_reached_sets_game_ended(self, game):
        game.max_turns = 3
        game.end_turn()  # -> turn 2
        game.end_turn()  # -> turn 3
        game.end_turn()  # -> turn 4 > max_turns (3) → ended
        assert game.game_ended is True

    def test_max_turns_not_exceeded_game_continues(self, game):
        game.max_turns = 5
        game.end_turn()  # 2
        game.end_turn()  # 3
        assert game.game_ended is False


# ---------------------------------------------------------------------------
# advance_turn() — event list and research progression
# ---------------------------------------------------------------------------

class TestAdvanceTurn:

    def test_returns_a_list(self, game):
        events = game.advance_turn()
        assert isinstance(events, list)

    def test_each_event_has_channel_and_message(self, game):
        events = game.advance_turn()
        for ev in events:
            assert "channel" in ev, f"event missing 'channel': {ev}"
            assert "message" in ev, f"event missing 'message': {ev}"

    def test_first_event_is_turn_channel(self, game):
        events = game.advance_turn()
        assert events[0]["channel"] == "TURN"

    def test_turn_event_message_contains_turn_number(self, game):
        events = game.advance_turn()
        turn_events = [e for e in events if e["channel"] == "TURN"]
        assert any(str(game.current_turn) in e["message"] for e in turn_events)

    def test_no_research_event_when_none_active(self, game):
        game.active_research = None
        events = game.advance_turn()
        rnd_events = [e for e in events if e["channel"] == "R&D"]
        assert rnd_events == []

    def test_research_progress_increments_by_one(self, game_with_research):
        before = game_with_research.research_progress
        game_with_research.advance_turn()
        assert game_with_research.research_progress == before + 1

    def test_research_event_emitted_when_active(self, game_with_research):
        events = game_with_research.advance_turn()
        rnd = [e for e in events if e["channel"] == "R&D"]
        assert len(rnd) == 1
        assert game_with_research.active_research in rnd[0]["message"]

    def test_research_accumulates_over_multiple_advances(self, game_with_research):
        for _ in range(5):
            game_with_research.advance_turn()
        assert game_with_research.research_progress == 5

    def test_research_progress_not_reset_between_advances(self, game_with_research):
        game_with_research.advance_turn()
        game_with_research.advance_turn()
        assert game_with_research.research_progress == 2


# ---------------------------------------------------------------------------
# hull_auto_repair_rate — now imported from game.py engine
# ---------------------------------------------------------------------------

class TestHullAutoRepairRate:

    def test_default_stats_give_half_point(self):
        rate = hull_auto_repair_rate({"VIT": 30, "SYN": 30})
        assert rate == pytest.approx(0.5)

    def test_minimum_clamped_at_0_1(self):
        rate = hull_auto_repair_rate({"VIT": 0, "SYN": 0})
        assert rate >= 0.1

    def test_high_vit_increases_rate(self):
        base = hull_auto_repair_rate({"VIT": 30, "SYN": 30})
        high = hull_auto_repair_rate({"VIT": 60, "SYN": 30})
        assert high > base

    def test_high_syn_increases_rate(self):
        base = hull_auto_repair_rate({"VIT": 30, "SYN": 30})
        high = hull_auto_repair_rate({"VIT": 30, "SYN": 60})
        assert high > base

    def test_max_stats_formula(self):
        # VIT=100, SYN=100: 0.5 + (70*0.03) + (70*0.02) = 0.5 + 2.1 + 1.4 = 4.0
        rate = hull_auto_repair_rate({"VIT": 100, "SYN": 100})
        assert rate == pytest.approx(4.0)

    def test_missing_keys_use_defaults(self):
        assert hull_auto_repair_rate({}) == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# resolve_end_turn() — the consolidated engine entry point
# ---------------------------------------------------------------------------

class TestResolveEndTurn:

    def test_returns_dict_with_required_keys(self, game):
        result = game.resolve_end_turn()
        for key in ("success", "message", "new_turn", "events",
                    "game_ended", "newly_completed_research",
                    "financial_summary", "credits_before", "credits_after"):
            assert key in result, f"missing key: {key}"

    def test_success_is_true(self, game):
        assert game.resolve_end_turn()["success"] is True

    def test_increments_turn(self, game):
        result = game.resolve_end_turn()
        assert result["new_turn"] == 2
        assert game.current_turn == 2

    def test_events_is_a_list(self, game):
        assert isinstance(game.resolve_end_turn()["events"], list)

    def test_events_all_have_channel_and_message(self, game):
        for ev in game.resolve_end_turn()["events"]:
            assert "channel" in ev
            assert "message" in ev

    def test_game_ended_false_by_default(self, game):
        assert game.resolve_end_turn()["game_ended"] is False

    def test_returns_false_when_already_ended(self, game):
        game.game_ended = True
        result = game.resolve_end_turn()
        assert result["success"] is False

    def test_no_research_completion_when_none_active(self, game):
        game.active_research = None
        assert game.resolve_end_turn()["newly_completed_research"] is None

    def test_research_progresses_each_cycle(self, game_with_research):
        game_with_research.resolve_end_turn()
        # advance_turn adds +1; resolve_end_turn adds (rp-1) more → total == rp
        rp = game_with_research.calculate_rp_per_turn()["total"]
        assert game_with_research.research_progress == rp

    def test_research_completes_when_threshold_reached(self, game_with_research):
        from research import all_research
        rt = all_research["Etheric Observation Protocol"]["research_time"]
        # Force progress to just below the threshold
        game_with_research.research_progress = rt - 1
        result = game_with_research.resolve_end_turn()
        assert result["newly_completed_research"] is not None
        assert result["newly_completed_research"]["name"] == "Etheric Observation Protocol"
        assert game_with_research.active_research is None  # cleared after completion

    def test_completed_research_added_to_game(self, game_with_research):
        from research import all_research
        rt = all_research["Etheric Observation Protocol"]["research_time"]
        game_with_research.research_progress = rt - 1
        game_with_research.resolve_end_turn()
        assert "Etheric Observation Protocol" in game_with_research.completed_research

    def test_colony_advance_fn_called(self, game):
        called = []
        def fake_colony(_):
            called.append(True)
            return {"income": 500}
        game.resolve_end_turn(colony_advance_fn=fake_colony)
        assert called, "colony_advance_fn was not called"

    def test_colony_financial_summary_returned(self, game):
        result = game.resolve_end_turn(
            colony_advance_fn=lambda _: {"income": 999}
        )
        assert result["financial_summary"] == {"income": 999}

    def test_credits_before_and_after_captured(self, game):
        initial = game.credits
        result = game.resolve_end_turn()
        assert result["credits_before"] == initial

    def test_hull_repair_event_emitted_when_damaged(self, game):
        game.ship_hull_damage = 5.0
        events = game.resolve_end_turn()["events"]
        hull_events = [e for e in events if e["channel"] == "HULL"]
        assert any("repair" in e["message"].lower() for e in hull_events)

    def test_hull_damage_reduced_after_repair(self, game):
        # Patch random so the 5% hazard roll never fires; only the repair path runs.
        import unittest.mock as mock
        game.ship_hull_damage = 5.0
        with mock.patch("game.random") as mock_rnd:
            mock_rnd.random.return_value = 1.0   # > 0.05 → no hazard
            game.resolve_end_turn()
        assert game.ship_hull_damage < 5.0

    def test_multiple_cycles_accumulate_turns(self, game):
        for _ in range(5):
            game.resolve_end_turn()
        assert game.current_turn == 6

    def test_research_accumulates_over_cycles(self, game_with_research):
        rp = game_with_research.calculate_rp_per_turn()["total"]
        game_with_research.resolve_end_turn()
        game_with_research.resolve_end_turn()
        assert game_with_research.research_progress == rp * 2
