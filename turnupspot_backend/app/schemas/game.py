from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from app.models.game import GameStatus, PlayerStatus


class GameTeamBase(BaseModel):
    team_name: str
    team_number: int
    captain_id: Optional[int] = None


class GameTeamCreate(GameTeamBase):
    pass


class GameTeamResponse(GameTeamBase):
    id: int
    game_id: int
    score: int
    goals_scored: int
    goals_conceded: int
    created_at: datetime

    class Config:
        from_attributes = True


class GamePlayerBase(BaseModel):
    member_id: int
    team_id: Optional[int] = None
    status: PlayerStatus = PlayerStatus.EXPECTED


class GamePlayerCreate(GamePlayerBase):
    pass


class GamePlayerUpdate(BaseModel):
    status: Optional[PlayerStatus] = None
    team_id: Optional[int] = None
    arrival_time: Optional[datetime] = None
    check_in_location_lat: Optional[str] = None
    check_in_location_lng: Optional[str] = None
    goals_scored: Optional[int] = None
    assists: Optional[int] = None
    yellow_cards: Optional[int] = None
    red_cards: Optional[int] = None


class GamePlayerResponse(GamePlayerBase):
    id: int
    game_id: int
    arrival_time: Optional[datetime] = None
    check_in_location_lat: Optional[str] = None
    check_in_location_lng: Optional[str] = None
    goals_scored: int
    assists: int
    yellow_cards: int
    red_cards: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GameBase(BaseModel):
    game_date: datetime
    start_time: datetime
    end_time: Optional[datetime] = None
    referee_id: Optional[int] = None
    assistant_referee_id: Optional[int] = None
    notes: Optional[str] = None
    weather_conditions: Optional[str] = None


class GameCreate(GameBase):
    sport_group_id: int
    teams: Optional[List[GameTeamCreate]] = []
    players: Optional[List[GamePlayerCreate]] = []


class GameUpdate(BaseModel):
    game_date: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    referee_id: Optional[int] = None
    assistant_referee_id: Optional[int] = None
    status: Optional[GameStatus] = None
    current_time: Optional[int] = None
    is_timer_running: Optional[bool] = None
    notes: Optional[str] = None
    weather_conditions: Optional[str] = None


class GameResponse(BaseModel):
    id: int
    sport_group_id: int
    status: GameStatus
    current_time: int
    is_timer_running: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    teams: Optional[List[GameTeamResponse]] = []
    players: Optional[List[GamePlayerResponse]] = []
    completed_matches: Optional[List[Dict[str, Any]]] = None
    current_match: Optional[Dict[str, Any]] = None
    upcoming_match: Optional[Dict[str, Any]] = None
    coin_toss_state: Optional[Dict[str, Any]] = None
    referee_id: Optional[int] = None

    class Config:
        from_attributes = True


class GameTimerUpdate(BaseModel):
    action: str  # "start", "stop", "reset"
    time: Optional[int] = None  # For setting specific time


class GameScoreUpdate(BaseModel):
    team_id: int
    action: str  # "increment", "decrement", "set"
    value: Optional[int] = None  # For setting specific score