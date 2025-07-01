from typing import Optional, List
from pydantic import BaseModel, validator
from datetime import datetime

from app.models.event import EventType, EventStatus, AttendeeStatus


class EventBase(BaseModel):
    title: str
    description: str
    event_type: EventType
    start_datetime: datetime
    end_datetime: datetime
    venue_name: str
    venue_address: str
    venue_latitude: Optional[float] = None
    venue_longitude: Optional[float] = None
    max_attendees: Optional[int] = None
    ticket_price: float = 0.0
    is_free: bool = True
    registration_deadline: Optional[datetime] = None
    is_public: bool = True

    @validator('end_datetime')
    def validate_end_datetime(cls, v, values):
        if 'start_datetime' in values and v <= values['start_datetime']:
            raise ValueError('End datetime must be after start datetime')
        return v

    @validator('ticket_price')
    def validate_ticket_price(cls, v, values):
        if 'is_free' in values and not values['is_free'] and v <= 0:
            raise ValueError('Paid events must have a positive ticket price')
        return v


class EventCreate(EventBase):
    cover_image_url: Optional[str] = None
    additional_images: Optional[List[str]] = []


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    event_type: Optional[EventType] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    venue_name: Optional[str] = None
    venue_address: Optional[str] = None
    venue_latitude: Optional[float] = None
    venue_longitude: Optional[float] = None
    max_attendees: Optional[int] = None
    ticket_price: Optional[float] = None
    is_free: Optional[bool] = None
    registration_deadline: Optional[datetime] = None
    cover_image_url: Optional[str] = None
    additional_images: Optional[List[str]] = None
    status: Optional[EventStatus] = None
    is_public: Optional[bool] = None


class EventAttendeeResponse(BaseModel):
    id: int
    user_id: int
    status: AttendeeStatus
    registration_date: datetime
    check_in_time: Optional[datetime] = None
    amount_paid: Optional[float] = None
    user: "UserResponse"

    class Config:
        from_attributes = True


class EventResponse(EventBase):
    id: int
    creator_id: int
    cover_image_url: Optional[str] = None
    additional_images: Optional[List[str]] = []
    status: EventStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    attendee_count: int = 0
    attendees: Optional[List[EventAttendeeResponse]] = []

    class Config:
        from_attributes = True


class EventRegistration(BaseModel):
    message: Optional[str] = None


# Import here to avoid circular imports
from app.schemas.user import UserResponse
EventAttendeeResponse.model_rebuild()