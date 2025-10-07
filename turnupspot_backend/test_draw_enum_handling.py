#!/usr/bin/env python3
"""
Test script to verify that draw handling correctly sets coin_toss_type enum to 'draw_decider'
"""

import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timezone

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.models.game import Match, GameTeam, CoinTossType, MatchStatus
from app.api.v1.endpoints.games import end_current_match
from app.core.database import get_db
from sqlalchemy.orm import Session

def test_draw_enum_handling():
    """Test that when a match ends in a draw, coin_toss_type is set to DRAW_DECIDER"""

    print("Testing draw enum handling...")

    # Mock the database session
    mock_db = Mock(spec=Session)

    # Create mock teams
    team_a = Mock(spec=GameTeam)
    team_a.id = "team_a_id"
    team_a.team_name = "Team A"

    team_b = Mock(spec=GameTeam)
    team_b.id = "team_b_id"
    team_b.team_name = "Team B"

    # Create mock match that ends in a draw
    mock_match = Mock(spec=Match)
    mock_match.id = "match_id"
    mock_match.team_a_id = "team_a_id"
    mock_match.team_b_id = "team_b_id"
    mock_match.team_a_score = 1
    mock_match.team_b_score = 1
    mock_match.is_draw = False  # Will be set to True
    mock_match.status = MatchStatus.IN_PROGRESS
    mock_match.requires_coin_toss = False  # Will be set to True
    mock_match.coin_toss_type = None  # Will be set to DRAW_DECIDER

    # Mock the query results
    mock_db.query.return_value.filter.return_value.first.return_value = mock_match
    mock_db.query.return_value.filter.return_value.all.return_value = []  # No previous draws

    # Mock the team queries
    mock_db.query.side_effect = lambda cls: Mock() if cls == GameTeam else Mock()

    # Mock team query results
    team_query_mock = Mock()
    team_query_mock.filter.return_value.first.side_effect = [team_a, team_b]
    mock_db.query.side_effect = lambda cls: team_query_mock if cls == GameTeam else Mock()

    # Mock the game
    mock_game = Mock()
    mock_game.id = "game_id"
    mock_game.sport_group_id = "group_id"
    mock_game.timer_is_running = True
    mock_game.timer_started_at = None
    mock_game.timer_remaining_seconds = 420

    # Mock the current user membership
    mock_membership = Mock()
    mock_membership.id = 1
    mock_membership.role.value = "admin"

    # Mock the sport group
    mock_sport_group = Mock()
    mock_sport_group.id = "group_id"

    try:
        # Call the end_current_match function
        result = end_current_match("game_id", mock_membership, mock_db)

        # Verify that the match was marked as a draw
        assert mock_match.is_draw == True, f"Expected is_draw=True, got {mock_match.is_draw}"

        # Verify that requires_coin_toss was set
        assert mock_match.requires_coin_toss == True, f"Expected requires_coin_toss=True, got {mock_match.requires_coin_toss}"

        # Verify that coin_toss_type was set to DRAW_DECIDER
        assert mock_match.coin_toss_type == CoinTossType.DRAW_DECIDER, f"Expected coin_toss_type=DRAW_DECIDER, got {mock_match.coin_toss_type}"

        # Verify the enum value is correct
        assert mock_match.coin_toss_type.value == "draw_decider", f"Expected enum value 'draw_decider', got '{mock_match.coin_toss_type.value}'"

        print("✓ Match correctly marked as draw")
        print("✓ requires_coin_toss set to True")
        print(f"✓ coin_toss_type set to: {mock_match.coin_toss_type}")
        print(f"✓ coin_toss_type.value: '{mock_match.coin_toss_type.value}'")

        # Check the result message
        assert "Match ended" in result["message"]
        assert result["match_result"]["is_draw"] == True
        assert result["match_result"]["requires_coin_toss"] == True

        print("✓ Result message indicates draw and coin toss requirement")

        return True

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enum_serialization():
    """Test that CoinTossType enum serializes correctly"""
    print("\nTesting enum serialization...")

    # Test DRAW_DECIDER
    draw_decider = CoinTossType.DRAW_DECIDER
    assert str(draw_decider) == "draw_decider", f"Expected 'draw_decider', got '{str(draw_decider)}'"
    assert draw_decider.value == "draw_decider", f"Expected value 'draw_decider', got '{draw_decider.value}'"

    # Test STARTING_TEAM
    starting_team = CoinTossType.STARTING_TEAM
    assert str(starting_team) == "starting_team", f"Expected 'starting_team', got '{str(starting_team)}'"
    assert starting_team.value == "starting_team", f"Expected value 'starting_team', got '{starting_team.value}'"

    print("✓ Enum serialization works correctly")
    return True

if __name__ == "__main__":
    print("Running draw enum handling tests...")
    print("=" * 50)

    try:
        # Test enum serialization first
        enum_ok = test_enum_serialization()

        # Test draw handling
        draw_ok = test_draw_enum_handling()

        if enum_ok and draw_ok:
            print("\n" + "=" * 50)
            print("✅ ALL TESTS PASSED - Draw handling correctly sets coin_toss_type to 'draw_decider'")
        else:
            print("\n❌ SOME TESTS FAILED")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)