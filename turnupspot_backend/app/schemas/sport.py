from typing import Optional, Any
from pydantic import BaseModel
from datetime import datetime

class SportBase(BaseModel):
    name: str
    type: str  # 'Team' or 'Individual'
    max_players_per_team: Optional[int] = None
    min_teams: Optional[int] = None
    players_per_match: Optional[int] = None
    requires_referee: bool = False
    rules: Optional[Any] = None

class SportCreate(SportBase):
    pass

class SportUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    max_players_per_team: Optional[int] = None
    min_teams: Optional[int] = None
    players_per_match: Optional[int] = None
    requires_referee: Optional[bool] = None
    rules: Optional[Any] = None

class SportResponse(SportBase):
    id: int
    is_default: bool
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 