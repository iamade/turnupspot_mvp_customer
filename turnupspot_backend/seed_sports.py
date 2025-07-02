#!/usr/bin/env python3
"""
Script to seed default sports into the database.
Run this after your database is set up and migrations are applied.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.sport import Sport

def seed_sports():
    """Seed default sports into the database."""
    db = SessionLocal()
    
    try:
        # Check if sports already exist
        existing_sports = db.query(Sport).count()
        if existing_sports > 0:
            print(f"Found {existing_sports} existing sports. Skipping seeding.")
            return
        
        # Default sports data
        default_sports = [
            {
                "name": "Football",
                "type": "Team",
                "max_players_per_team": 5,
                "min_teams": 2,
                "requires_referee": True,
                "rules": {
                    "description": "5-a-side football rules",
                    "duration": "2 x 25 minutes",
                    "substitutions": "Unlimited",
                    "fouls": "Standard football rules apply"
                }
            },
            {
                "name": "Basketball",
                "type": "Team",
                "max_players_per_team": 3,
                "min_teams": 2,
                "requires_referee": True,
                "rules": {
                    "description": "3-on-3 basketball rules",
                    "duration": "First to 21 points or 10 minutes",
                    "scoring": "1 point for free throws, 2 points for field goals",
                    "fouls": "Standard basketball rules apply"
                }
            },
            {
                "name": "Tennis",
                "type": "Individual",
                "players_per_match": 2,
                "requires_referee": True,
                "rules": {
                    "description": "Singles tennis rules",
                    "scoring": "Best of 3 sets",
                    "serving": "Alternate serves every 2 points",
                    "court": "Standard tennis court"
                }
            },
            {
                "name": "Table Tennis",
                "type": "Individual",
                "players_per_match": 2,
                "requires_referee": False,
                "rules": {
                    "description": "Singles table tennis rules",
                    "scoring": "Best of 5 games to 11 points",
                    "serving": "2 serves per player",
                    "equipment": "Standard table tennis table and paddles"
                }
            },
            {
                "name": "Volleyball",
                "type": "Team",
                "max_players_per_team": 6,
                "min_teams": 2,
                "requires_referee": True,
                "rules": {
                    "description": "6-on-6 volleyball rules",
                    "scoring": "Best of 3 sets to 25 points",
                    "rotation": "Clockwise rotation after winning serve",
                    "hits": "Maximum 3 hits per side"
                }
            },
            {
                "name": "Badminton",
                "type": "Individual",
                "players_per_match": 2,
                "requires_referee": False,
                "rules": {
                    "description": "Singles badminton rules",
                    "scoring": "Best of 3 games to 21 points",
                    "serving": "Alternate serves",
                    "court": "Standard badminton court"
                }
            },
            {
                "name": "Cricket",
                "type": "Team",
                "max_players_per_team": 11,
                "min_teams": 2,
                "requires_referee": True,
                "rules": {
                    "description": "Limited overs cricket rules",
                    "overs": "20 overs per team",
                    "format": "T20 style",
                    "equipment": "Standard cricket equipment"
                }
            }
        ]
        
        # Create sport objects
        sports_to_add = []
        for sport_data in default_sports:
            sport = Sport(
                name=sport_data["name"],
                type=sport_data["type"],
                max_players_per_team=sport_data.get("max_players_per_team"),
                min_teams=sport_data.get("min_teams"),
                players_per_match=sport_data.get("players_per_match"),
                requires_referee=sport_data["requires_referee"],
                rules=sport_data.get("rules"),
                is_default=True,
                created_by=None  # System-created
            )
            sports_to_add.append(sport)
        
        # Add to database
        db.add_all(sports_to_add)
        db.commit()
        
        print(f"Successfully seeded {len(sports_to_add)} default sports:")
        for sport in sports_to_add:
            print(f"  - {sport.name} ({sport.type})")
            
    except Exception as e:
        print(f"Error seeding sports: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Seeding default sports...")
    seed_sports()
    print("Done!") 