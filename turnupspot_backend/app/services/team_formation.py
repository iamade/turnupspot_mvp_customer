import random
from typing import List, Dict
from datetime import datetime, timedelta
import calendar
from app.models.sport_group import SportGroup

def form_teams_first_come(players: List[Dict], team_size: int) -> List[List[Dict]]:
    return [players[i:i+team_size] for i in range(0, len(players), team_size)]

def form_teams_random(players: List[Dict], team_size: int) -> List[List[Dict]]:
    shuffled = players[:]
    random.shuffle(shuffled)
    return [shuffled[i:i+team_size] for i in range(0, len(shuffled), team_size)]

def rotate_teams_winner_stays(teams: List[List[Dict]], last_winner_idx: int) -> List[List[Dict]]:
    # Winner stays, others rotate
    if not teams:
        return []
    winner = teams[last_winner_idx]
    others = [team for idx, team in enumerate(teams) if idx != last_winner_idx]
    return [winner] + others 