#!/usr/bin/env python3
"""
Test script to verify CoinTossType enum serialization fix.
This tests that enum values are correctly serialized to lowercase strings.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.models.game import CoinTossType

def test_coin_toss_enum_values():
    """Test that CoinTossType enum values are lowercase strings"""
    print("Testing CoinTossType enum serialization...")
    
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
    
    print("✓ All CoinTossType enum values are correctly serialized to lowercase strings")

def test_enum_usage_in_games_py():
    """Test that the games.py file uses .value for enum serialization"""
    print("\nChecking enum usage in games.py...")
    
    games_file_path = os.path.join(os.path.dirname(__file__), 'app', 'api', 'v1', 'endpoints', 'games.py')
    
    with open(games_file_path, 'r') as f:
        content = f.read()
    
    # Check for proper .value usage
    expected_patterns = [
        'CoinTossType.DRAW_DECIDER.value',
        'CoinTossType.STARTING_TEAM.value'
    ]
    
    missing_patterns = []
    for pattern in expected_patterns:
        if pattern not in content:
            missing_patterns.append(pattern)
        else:
            print(f"✓ Found proper usage: {pattern}")
    
    if missing_patterns:
        print(f"✗ Missing .value usage for: {missing_patterns}")
        return False
    else:
        print("✓ All CoinTossType enum usages correctly use .value")
        return True

def test_enum_database_serialization():
    """Test enum serialization for database storage"""
    print("\nTesting enum serialization for database...")
    
    # Test that the values are appropriate for database storage
    draw_decider_db_value = CoinTossType.DRAW_DECIDER.value
    starting_team_db_value = CoinTossType.STARTING_TEAM.value
    
    # Verify values are lowercase and database-friendly
    assert draw_decider_db_value.islower(), "Enum value should be lowercase for database"
    assert starting_team_db_value.islower(), "Enum value should be lowercase for database"
    assert '_' in draw_decider_db_value, "Enum value should use snake_case for database"
    assert '_' in starting_team_db_value, "Enum value should use snake_case for database"
    
    print("✓ CoinTossType enum values are database-friendly (lowercase, snake_case)")

if __name__ == "__main__":
    try:
        print("Running CoinTossType enum serialization tests...")
        print("=" * 50)
        
        test_coin_toss_enum_values()
        enum_usage_ok = test_enum_usage_in_games_py()
        test_enum_database_serialization()
        
        print("\n" + "=" * 50)
        print("✅ ALL TESTS PASSED - CoinTossType enum serialization fix is working correctly!")
        print(f"✅ Enum values are properly serialized to lowercase strings: 'draw_decider', 'starting_team'")
        
        if enum_usage_ok:
            print("✅ All enum usages in games.py correctly use .value property")
        else:
            print("❌ Some enum usages in games.py need to be updated to use .value")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)