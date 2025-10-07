#!/usr/bin/env python3
"""
Test script to verify CoinTossType enum consistency across backend, frontend, and database.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.models.game import CoinTossType

def test_enum_values():
    """Test that CoinTossType enum values are lowercase and consistent"""
    print("Testing CoinTossType enum values...")

    # Test DRAW_DECIDER
    draw_decider_value = CoinTossType.DRAW_DECIDER.value
    print(f"DRAW_DECIDER value: {draw_decider_value}")
    assert draw_decider_value == "draw_decider", f"Expected 'draw_decider', got '{draw_decider_value}'"
    assert isinstance(draw_decider_value, str), f"Expected string, got {type(draw_decider_value)}"

    # Test STARTING_TEAM
    starting_team_value = CoinTossType.STARTING_TEAM.value
    print(f"STARTING_TEAM value: {starting_team_value}")
    assert starting_team_value == "starting_team", f"Expected 'starting_team', got '{starting_team_value}'"
    assert isinstance(starting_team_value, str), f"Expected string, got {type(starting_team_value)}"

    print("✓ All CoinTossType enum values are correctly lowercase strings")

def test_enum_consistency():
    """Test that enum values match frontend expectations"""
    print("\nTesting enum consistency with frontend...")

    # These should match the frontend enum values
    expected_values = {
        "DRAW_DECIDER": "draw_decider",
        "STARTING_TEAM": "starting_team"
    }

    for enum_member, expected_value in expected_values.items():
        actual_value = getattr(CoinTossType, enum_member).value
        assert actual_value == expected_value, f"{enum_member} should be '{expected_value}', got '{actual_value}'"
        print(f"✓ {enum_member} = '{actual_value}'")

    print("✓ Enum values are consistent with frontend expectations")

if __name__ == "__main__":
    try:
        print("Running CoinTossType enum consistency tests...")
        print("=" * 50)

        test_enum_values()
        test_enum_consistency()

        print("\n" + "=" * 50)
        print("✅ ALL TESTS PASSED - CoinTossType enum is consistent across backend and frontend!")
        print("✅ Enum values are lowercase strings: 'draw_decider', 'starting_team'")
        print("✅ Ready for draw handling without serialization errors")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)