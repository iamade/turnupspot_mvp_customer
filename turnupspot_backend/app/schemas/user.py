from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from enum import Enum

from app.models.user import UserRole


class UserRole(str, Enum):
    USER = "user"
    VENDOR = "vendor"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone_number: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    bio: Optional[str] = None


class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.USER
    interests: Optional[List[str]] = []

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    role: UserRole
    profile_image_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None