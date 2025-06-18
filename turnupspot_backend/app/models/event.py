from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class EventType(str, enum.Enum):
    CONCERT = "concert"
    CONFERENCE = "conference"
    WORKSHOP = "workshop"
    PARTY = "party"
    SPORTS = "sports"
    EXHIBITION = "exhibition"
    FESTIVAL = "festival"
    OTHER = "other"


class EventStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class AttendeeStatus(str, enum.Enum):
    REGISTERED = "registered"
    CONFIRMED = "confirmed"
    ATTENDED = "attended"
    NO_SHOW = "no_show"
    CANCELLED = "cancelled"


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    event_type = Column(Enum(EventType), nullable=False)
    
    # Date and time
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    
    # Location
    venue_name = Column(String, nullable=False)
    venue_address = Column(String, nullable=False)
    venue_latitude = Column(Float, nullable=True)
    venue_longitude = Column(Float, nullable=True)
    
    # Event details
    max_attendees = Column(Integer, nullable=True)
    ticket_price = Column(Float, default=0.0)
    is_free = Column(Boolean, default=True)
    registration_deadline = Column(DateTime, nullable=True)
    
    # Media
    cover_image_url = Column(String, nullable=True)
    additional_images = Column(Text, nullable=True)  # JSON string of image URLs
    
    # Status and meta
    status = Column(Enum(EventStatus), default=EventStatus.DRAFT)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    creator = relationship("User", back_populates="created_events")
    attendees = relationship("EventAttendee", back_populates="event")

    @property
    def attendee_count(self):
        return len([a for a in self.attendees if a.status in [AttendeeStatus.REGISTERED, AttendeeStatus.CONFIRMED, AttendeeStatus.ATTENDED]])

    def __repr__(self):
        return f"<Event(id={self.id}, title='{self.title}', type='{self.event_type}')>"


class EventAttendee(Base):
    __tablename__ = "event_attendees"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(AttendeeStatus), default=AttendeeStatus.REGISTERED)
    registration_date = Column(DateTime(timezone=True), server_default=func.now())
    check_in_time = Column(DateTime, nullable=True)
    
    # Payment info (if applicable)
    payment_id = Column(String, nullable=True)
    amount_paid = Column(Float, nullable=True)

    # Relationships
    event = relationship("Event", back_populates="attendees")
    user = relationship("User", back_populates="event_attendances")

    def __repr__(self):
        return f"<EventAttendee(event_id={self.event_id}, user_id={self.user_id}, status='{self.status}')>"