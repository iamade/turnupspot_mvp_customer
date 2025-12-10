from typing import Optional, List
from pydantic import BaseModel, field_validator, Field
from datetime import datetime, time
from enum import Enum

from app.models.sport_group import SportsType, MemberRole


class Day(str, Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"


class PlayingDayBase(BaseModel):
    day: Day


class PlayingDayCreate(PlayingDayBase):
    pass


class PlayingDay(PlayingDayBase):
    id: str
    sport_group_id: str

    class Config:
        from_attributes = True


class SportGroupBase(BaseModel):
    name: str
    description: Optional[str] = None
    venue_name: str
    venue_address: str
    venue_image_url: Optional[str] = None
    playing_days: List[PlayingDay] = []
    game_start_time: time
    game_end_time: time
    max_teams: int = Field(gt=0)
    max_players_per_team: int = Field(gt=0)
    rules: Optional[str] = None
    game_config: Optional[str] = None
    min_players_per_team: int = Field(default=3, gt=0)
    referee_required: bool = False
    sports_type: SportsType

    @field_validator("max_teams")
    def validate_max_teams(cls, v):
        if v < 2:
            raise ValueError("Must have at least 2 teams")
        return v

    @field_validator("max_players_per_team")
    def validate_max_players(cls, v):
        if v < 1:
            raise ValueError("Must have at least 1 player per team")
        return v

    class Config:
        from_attributes = True


class SportGroupCreate(SportGroupBase):
    playing_days: List[PlayingDayCreate]


class SportGroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    venue_name: Optional[str] = None
    venue_address: Optional[str] = None
    venue_image_url: Optional[str] = None
    playing_days: Optional[List[Day]] = None
    game_start_time: Optional[time] = None
    game_end_time: Optional[time] = None
    max_teams: Optional[int] = Field(None, gt=0)
    max_players_per_team: Optional[int] = Field(None, gt=0)
    rules: Optional[str] = None
    game_config: Optional[str] = None
    min_players_per_team: Optional[int] = Field(None, gt=0)
    referee_required: Optional[bool] = None
    sports_type: Optional[SportsType] = None

    @field_validator("playing_days", mode="before")
    @classmethod
    def normalize_playing_days(cls, v):
        if v is None:
            return v

        normalized = []
        for item in v:
            if isinstance(item, dict) and "day" in item:
                # Extract day from PlayingDay object
                day_value = item["day"]
                normalized.append(day_value)
            elif isinstance(item, str):
                # Handle string values - convert uppercase to title case if needed
                if item.isupper():
                    item = item.capitalize()
                normalized.append(item)
            else:
                # Handle other types (shouldn't happen but just in case)
                normalized.append(str(item))

        return normalized


class SportGroupMemberResponse(BaseModel):
    id: int
    user_id: int
    role: MemberRole
    is_approved: bool
    joined_at: datetime
    user: "UserResponse"

    class Config:
        from_attributes = True


class UserMembershipInfo(BaseModel):
    is_member: bool
    is_pending: bool
    role: Optional[MemberRole] = None
    is_creator: bool


class SportGroupResponse(SportGroupBase):
    id: str
    venue_latitude: Optional[float] = None
    venue_longitude: Optional[float] = None
    created_by: str
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    playing_days: List[PlayingDay]
    member_count: Optional[int] = None
    current_user_membership: Optional[UserMembershipInfo] = None

    class Config:
        from_attributes = True


class SportGroupJoinRequest(BaseModel):
    message: Optional[str] = None


# Import here to avoid circular imports
from app.schemas.user import UserResponse

SportGroupMemberResponse.model_rebuild()
