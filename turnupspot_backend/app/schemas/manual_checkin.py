from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime

class GameDayParticipantCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    team: Optional[int] = None

    @validator('email', pre=True, always=True)
    def empty_string_to_none(cls, v):
        if v == '':
            return None
        return v

class GameDayParticipantOut(BaseModel):
    id: int
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    is_registered_user: bool
    created_at: datetime
    team: Optional[int] = None

    class Config:
        orm_mode = True 