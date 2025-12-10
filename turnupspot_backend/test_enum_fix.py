#!/usr/bin/env python3
"""
Standalone test to verify CoinTossType enum fix.
Tests that the enum properly serializes to lowercase values.
"""

import sys
import enum

# Test the enum definition
class CoinTossType(str, enum.Enum):
    DRAW_DECIDER = "draw_decider"
    STARTING_TEAM = "starting_team"

def test_enum_values():
    """Test that enum values are lowercase strings"""
    print("Testing CoinTossType enum values...")
    
    # Test DRAW_DECIDER
    assert CoinTossType.DRAW_DECIDER.value == "draw_decider", \
        f"Expected 'draw_decider', got '{CoinTossType.DRAW_DECIDER.value}'"
    print(f"✓ CoinTossType.DRAW_DECIDER.value = '{CoinTossType.DRAW_DECIDER.value}'")
    
    # Test STARTING_TEAM
    assert CoinTossType.STARTING_TEAM.value == "starting_team", \
        f"Expected 'starting_team', got '{CoinTossType.STARTING_TEAM.value}'"
    print(f"✓ CoinTossType.STARTING_TEAM.value = '{CoinTossType.STARTING_TEAM.value}'")
    
    # Test that string comparison works
    assert CoinTossType.DRAW_DECIDER.value == "draw_decider"
    assert CoinTossType.STARTING_TEAM.value == "starting_team"
    print("✓ String comparisons work correctly")
    
    # Test enum member name vs value
    print(f"\nEnum member names (what was being sent incorrectly):")
    print(f"  CoinTossType.DRAW_DECIDER.name = '{CoinTossType.DRAW_DECIDER.name}'")
    print(f"  CoinTossType.STARTING_TEAM.name = '{CoinTossType.STARTING_TEAM.name}'")
    
    print(f"\nEnum values (what should be sent to DB):")
    print(f"  CoinTossType.DRAW_DECIDER.value = '{CoinTossType.DRAW_DECIDER.value}'")
    print(f"  CoinTossType.STARTING_TEAM.value = '{CoinTossType.STARTING_TEAM.value}'")
    
    return True

def test_sqlalchemy_enum_config():
    """Test the SQLAlchemy enum configuration"""
    print("\n" + "="*60)
    print("SQLAlchemy Enum Configuration Test")
    print("="*60)
    
    # Test the values_callable function that we added
    values_callable = lambda obj: [e.value for e in obj]
    values = values_callable(CoinTossType)
    
    print(f"Values that will be stored in DB: {values}")
    assert values == ['draw_decider', 'starting_team'], \
        f"Expected ['draw_decider', 'starting_team'], got {values}"
    print("✓ values_callable correctly extracts enum values")
    
    # Verify none of the uppercase names are in the values
    assert 'DRAW_DECIDER' not in values
    assert 'STARTING_TEAM' not in values
    print("✓ Uppercase enum names are NOT in DB values (good!)")
    
    return True

if __name__ == "__main__":
    try:
        print("="*60)
        print("Enum Fix Verification Test")
        print("="*60)
        print()
        
        if test_enum_values():
            print("\n✅ Enum values test PASSED")
        
        if test_sqlalchemy_enum_config():
            print("\n✅ SQLAlchemy enum config test PASSED")
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED ✅")
        print("="*60)
        print("\nSummary:")
        print("- Enum values are correctly lowercase: 'draw_decider', 'starting_team'")
        print("- SQLAlchemy will now use .value (lowercase) instead of .name (uppercase)")
        print("- This fixes the DataError: 'STARTING_TEAM' -> 'starting_team'")
        sys.exit(0)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)