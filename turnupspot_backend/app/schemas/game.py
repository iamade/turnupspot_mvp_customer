from typing import Optional, List, Dict, Any
from pydantic import BaseModel, field_validator
from datetime import datetime

from app.models.game import GameStatus, PlayerStatus, CoinTossType


class GameTeamBase(BaseModel):
    team_name: str
    team_number: int
    captain_id: Optional[int] = None


class GameTeamCreate(GameTeamBase):
    pass


class GameTeamResponse(GameTeamBase):
    id: str
    game_id: str
    score: int
    goals_scored: int
    goals_conceded: int
    created_at: datetime

    class Config:
        from_attributes = True


class GamePlayerBase(BaseModel):
    member_id: int
    team_id: Optional[str] = None
    status: PlayerStatus = PlayerStatus.EXPECTED


class GamePlayerCreate(GamePlayerBase):
    pass


class GamePlayerUpdate(BaseModel):
    status: Optional[PlayerStatus] = None
    team_id: Optional[str] = None
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
    sport_group_id: str
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
    id: str
    sport_group_id: str
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
    action: str  # "start", "stop", "reset", "pause", "resume"
    time: Optional[int] = None  # For setting specific time


class GameScoreUpdate(BaseModel):
    team_id: str
    action: str  # "increment", "decrement", "set"
    value: Optional[int] = None  # For setting specific score


class CoinTossRequest(BaseModel):
    """Schema for coin toss request with validation"""
    team_a_id: str
    team_b_id: str
    team_a_choice: str  # "heads" or "tails"
    team_b_choice: str  # "heads" or "tails"
    coin_toss_type: str = "draw_decider"  # "draw_decider" or "starting_team"
    
    @field_validator('coin_toss_type')
    @classmethod
    def validate_coin_toss_type(cls, v: str) -> str:
        """Validate that coin_toss_type is a valid enum value"""
        valid_values = [e.value for e in CoinTossType]
        if v.lower() not in valid_values:
            raise ValueError(
                f"Invalid coin_toss_type '{v}'. Must be one of: {', '.join(valid_values)}"
            )
        return v.lower()  # Normalize to lowercase
    
    @field_validator('team_a_choice', 'team_b_choice')
    @classmethod
    def validate_choice(cls, v: str) -> str:
        """Validate that choice is heads or tails"""
        if v.lower() not in ['heads', 'tails']:
            raise ValueError("Choice must be 'heads' or 'tails'")
        return v.lower()