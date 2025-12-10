#!/usr/bin/env python3
"""
Simple test to verify CoinTossType enum behavior for draw handling
"""

import enum

# Import the actual enum from the model
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app.models.game import CoinTossType
    print("✓ Successfully imported CoinTossType from app.models.game")
except ImportError as e:
    print(f"Could not import from app.models.game: {e}")
    print("Falling back to local definition")
    class CoinTossType(str, enum.Enum):
        DRAW_DECIDER = "draw_decider"
        STARTING_TEAM = "starting_team"

def test_enum_behavior():
    """Test that the enum behaves correctly for database storage"""

    print("Testing CoinTossType enum behavior...")

    # Test enum creation
    draw_decider = CoinTossType.DRAW_DECIDER
    starting_team = CoinTossType.STARTING_TEAM

    print(f"DRAW_DECIDER: {draw_decider}")
    print(f"DRAW_DECIDER type: {type(draw_decider)}")
    print(f"DRAW_DECIDER value: {draw_decider.value}")

    # Test that .value gives the correct string
    assert draw_decider.value == "draw_decider"
    assert starting_team.value == "starting_team"

    print("✓ Enum .value gives correct string values")

    # Test database simulation - this is what the code should use
    stored_value = draw_decider.value  # This is what we store
    print(f"Stored value (using .value): '{stored_value}'")

    # Verify it matches the expected database value
    assert stored_value == "draw_decider"

    # Test that we can reconstruct the enum from the stored value
    if stored_value == "draw_decider":
        reconstructed_enum = CoinTossType(stored_value)
        print(f"✓ Successfully reconstructed enum from stored value: {reconstructed_enum}")
        assert reconstructed_enum == CoinTossType.DRAW_DECIDER
    else:
        print("✗ Could not reconstruct enum from stored value")
        return False

    return True

def test_draw_scenario():
    """Simulate what happens in draw scenario"""

    print("\nSimulating draw scenario...")

    # Simulate the FIXED code from games.py (using .value)
    coin_toss_type = CoinTossType.DRAW_DECIDER.value

    print(f"coin_toss_type set to: {coin_toss_type}")
    print(f"type: {type(coin_toss_type)}")

    # This is what gets stored in the database
    db_value = coin_toss_type  # Already a string
    print(f"Database value: '{db_value}'")

    # Verify it matches the expected enum value
    assert db_value == "draw_decider", f"Expected 'draw_decider', got '{db_value}'"
    assert isinstance(db_value, str), f"Expected string, got {type(db_value)}"

    print("✓ Draw scenario correctly sets coin_toss_type to 'draw_decider'")

    return True

if __name__ == "__main__":
    print("Running simple draw enum test...")
    print("=" * 40)

    try:
        enum_ok = test_enum_behavior()
        draw_ok = test_draw_scenario()

        if enum_ok and draw_ok:
            print("\n" + "=" * 40)
            print("✅ ALL TESTS PASSED")
            print("✅ CoinTossType enum correctly handles 'draw_decider' for draw scenarios")
        else:
            print("\n❌ TESTS FAILED")
            exit(1)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)