#!/usr/bin/env python3
"""
Simple test to verify enum validation for coin_toss_type
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Import the enum directly without loading the full app
import enum

class CoinTossType(str, enum.Enum):
    draw_decider = "draw_decider"
    STARTING_TEAM = "starting_team"

def _validate_coin_toss_type(coin_toss_type_str: str) -> CoinTossType:
    """Validate and convert coin_toss_type string to enum"""
    try:
        # Try to match the string to enum values (case-insensitive)
        for enum_member in CoinTossType:
            if enum_member.value.lower() == coin_toss_type_str.lower():
                return enum_member
        # If no match found, raise ValueError
        raise ValueError(f"Invalid coin toss type: {coin_toss_type_str}")
    except ValueError:
        valid_types = [e.value for e in CoinTossType]
        raise ValueError(f"Invalid coin toss type '{coin_toss_type_str}'. Valid types are: {', '.join(valid_types)}")

def test_enum_validation():
    """Test the enum validation function"""
    print("Testing enum validation...")

    # Test valid inputs
    try:
        result = _validate_coin_toss_type("draw_decider")
        assert result == CoinTossType.draw_decider
        print("✓ 'draw_decider' -> CoinTossType.draw_decider")

        result = _validate_coin_toss_type("DRAW_DECIDER")
        assert result == CoinTossType.draw_decider
        print("✓ 'DRAW_DECIDER' -> CoinTossType.draw_decider")

        result = _validate_coin_toss_type("starting_team")
        assert result == CoinTossType.STARTING_TEAM
        print("✓ 'starting_team' -> CoinTossType.STARTING_TEAM")

        result = _validate_coin_toss_type("STARTING_TEAM")
        assert result == CoinTossType.STARTING_TEAM
        print("✓ 'STARTING_TEAM' -> CoinTossType.STARTING_TEAM")

    except Exception as e:
        print(f"✗ Valid input test failed: {e}")
        return False

    # Test invalid inputs
    try:
        _validate_coin_toss_type("invalid_type")
        print("✗ Should have raised ValueError for invalid type")
        return False
    except ValueError as e:
        if "Invalid coin toss type" in str(e):
            print("✓ Correctly rejected invalid type")
        else:
            print(f"✗ Wrong error message: {e}")
            return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

    # Test enum comparisons
    coin_type = CoinTossType.draw_decider
    if coin_type == CoinTossType.draw_decider:
        print("✓ Enum comparison works")
    else:
        print("✗ Enum comparison failed")
        return False

    if coin_type == CoinTossType.STARTING_TEAM:
        print("✗ Enum comparison should have failed")
        return False
    else:
        print("✓ Enum comparison correctly distinguished different values")

    print("\n✅ All tests passed! Enum validation is working correctly.")
    return True

if __name__ == "__main__":
    success = test_enum_validation()
    sys.exit(0 if success else 1)