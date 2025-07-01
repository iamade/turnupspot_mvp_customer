from typing import List, Dict, Optional

tournaments = {}

class Tournament:
    def __init__(self, id: str, name: str, teams: List[str], prize: Optional[float] = None, escrow: Optional[float] = None):
        self.id = id
        self.name = name
        self.teams = teams
        self.prize = prize
        self.escrow = escrow
        self.results = []

    def add_result(self, result: Dict):
        self.results.append(result)

    def get_results(self):
        return self.results

# Example functions

def create_tournament(id: str, name: str, teams: List[str], prize: Optional[float] = None, escrow: Optional[float] = None):
    tournaments[id] = Tournament(id, name, teams, prize, escrow)
    return tournaments[id]

def add_tournament_result(tournament_id: str, result: Dict):
    if tournament_id in tournaments:
        tournaments[tournament_id].add_result(result)
        return True
    return False

def get_tournament_results(tournament_id: str):
    if tournament_id in tournaments:
        return tournaments[tournament_id].get_results()
    return [] 