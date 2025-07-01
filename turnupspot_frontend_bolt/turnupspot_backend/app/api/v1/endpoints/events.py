from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.database import get_db
from app.api.deps import get_current_user, get_optional_current_user
from app.models.user import User
from app.models.event import Event, EventAttendee, EventType, EventStatus, AttendeeStatus
from app.schemas.event import (
    EventCreate, EventUpdate, EventResponse, 
    EventRegistration, EventAttendeeResponse
)
from app.core.exceptions import EventNotFoundException, ForbiddenException

router = APIRouter()


@router.post("/", response_model=EventResponse)
def create_event(
    event_data: EventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new event"""
    db_event = Event(
        **event_data.dict(exclude={"additional_images"}),
        creator_id=current_user.id,
        additional_images=",".join(event_data.additional_images) if event_data.additional_images else None
    )
    
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    
    # Add attendee count
    db_event.attendee_count = 0
    
    return db_event


@router.get("/", response_model=List[EventResponse])
def get_events(
    skip: int = 0,
    limit: int = 100,
    event_type: Optional[EventType] = None,
    search: Optional[str] = None,
    upcoming_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """Get all events with optional filtering"""
    query = db.query(Event).filter(Event.status == EventStatus.PUBLISHED)
    
    if not current_user:
        query = query.filter(Event.is_public == True)
    
    if event_type:
        query = query.filter(Event.event_type == event_type)
    
    if search:
        query = query.filter(
            or_(
                Event.title.ilike(f"%{search}%"),
                Event.description.ilike(f"%{search}%"),
                Event.venue_name.ilike(f"%{search}%")
            )
        )
    
    if upcoming_only:
        from datetime import datetime
        query = query.filter(Event.start_datetime > datetime.utcnow())
    
    events = query.offset(skip).limit(limit).all()
    
    # Add attendee count to each event
    for event in events:
        event.attendee_count = len([a for a in event.attendees if a.status in [
            AttendeeStatus.REGISTERED, AttendeeStatus.CONFIRMED, AttendeeStatus.ATTENDED
        ]])
    
    return events


@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """Get event by ID"""
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise EventNotFoundException()
    
    # Check if event is public or user has access
    if not event.is_public and (not current_user or event.creator_id != current_user.id):
        raise ForbiddenException("Event is private")
    
    # Add attendee count
    event.attendee_count = len([a for a in event.attendees if a.status in [
        AttendeeStatus.REGISTERED, AttendeeStatus.CONFIRMED, AttendeeStatus.ATTENDED
    ]])
    
    return event


@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    event_update: EventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update event (creator only)"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise EventNotFoundException()
    
    # Check if user is creator or admin
    if event.creator_id != current_user.id and current_user.role != "admin":
        raise ForbiddenException("Only event creator can update the event")
    
    # Update event
    update_data = event_update.dict(exclude_unset=True)
    if "additional_images" in update_data:
        update_data["additional_images"] = ",".join(update_data["additional_images"]) if update_data["additional_images"] else None
    
    for field, value in update_data.items():
        setattr(event, field, value)
    
    db.commit()
    db.refresh(event)
    
    # Add attendee count
    event.attendee_count = len([a for a in event.attendees if a.status in [
        AttendeeStatus.REGISTERED, AttendeeStatus.CONFIRMED, AttendeeStatus.ATTENDED
    ]])
    
    return event


@router.delete("/{event_id}")
def delete_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete event (creator only)"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise EventNotFoundException()
    
    # Check if user is creator or admin
    if event.creator_id != current_user.id and current_user.role != "admin":
        raise ForbiddenException("Only event creator can delete the event")
    
    # Soft delete by changing status
    event.status = EventStatus.CANCELLED
    db.commit()
    
    return {"message": "Event cancelled successfully"}


@router.post("/{event_id}/register")
def register_for_event(
    event_id: int,
    registration: EventRegistration,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Register for an event"""
    event = db.query(Event).filter(
        and_(Event.id == event_id, Event.status == EventStatus.PUBLISHED)
    ).first()
    
    if not event:
        raise EventNotFoundException()
    
    # Check if registration is still open
    from datetime import datetime
    if event.registration_deadline and datetime.utcnow() > event.registration_deadline:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration deadline has passed"
        )
    
    # Check if user is already registered
    existing_registration = db.query(EventAttendee).filter(
        and_(
            EventAttendee.event_id == event_id,
            EventAttendee.user_id == current_user.id
        )
    ).first()
    
    if existing_registration:
        if existing_registration.status == AttendeeStatus.CANCELLED:
            # Reactivate registration
            existing_registration.status = AttendeeStatus.REGISTERED
            db.commit()
            return {"message": "Registration reactivated successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already registered for this event"
            )
    
    # Check if event is full
    if event.max_attendees:
        current_attendees = len([a for a in event.attendees if a.status in [
            AttendeeStatus.REGISTERED, AttendeeStatus.CONFIRMED, AttendeeStatus.ATTENDED
        ]])
        if current_attendees >= event.max_attendees:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Event is full"
            )
    
    # Create registration
    attendee = EventAttendee(
        event_id=event_id,
        user_id=current_user.id,
        status=AttendeeStatus.REGISTERED,
        amount_paid=event.ticket_price if not event.is_free else 0.0
    )
    
    db.add(attendee)
    db.commit()
    
    return {"message": "Registered successfully"}


@router.post("/{event_id}/unregister")
def unregister_from_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unregister from an event"""
    attendee = db.query(EventAttendee).filter(
        and_(
            EventAttendee.event_id == event_id,
            EventAttendee.user_id == current_user.id
        )
    ).first()
    
    if not attendee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not registered for this event"
        )
    
    attendee.status = AttendeeStatus.CANCELLED
    db.commit()
    
    return {"message": "Unregistered successfully"}


@router.get("/{event_id}/attendees", response_model=List[EventAttendeeResponse])
def get_event_attendees(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get event attendees (creator only)"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise EventNotFoundException()
    
    # Check if user is creator or admin
    if event.creator_id != current_user.id and current_user.role != "admin":
        raise ForbiddenException("Only event creator can view attendees")
    
    attendees = db.query(EventAttendee).filter(
        and_(
            EventAttendee.event_id == event_id,
            EventAttendee.status.in_([
                AttendeeStatus.REGISTERED, 
                AttendeeStatus.CONFIRMED, 
                AttendeeStatus.ATTENDED
            ])
        )
    ).all()
    
    return attendees


@router.post("/{event_id}/check-in/{attendee_id}")
def check_in_attendee(
    event_id: int,
    attendee_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check in an attendee (creator only)"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise EventNotFoundException()
    
    # Check if user is creator or admin
    if event.creator_id != current_user.id and current_user.role != "admin":
        raise ForbiddenException("Only event creator can check in attendees")
    
    attendee = db.query(EventAttendee).filter(
        and_(
            EventAttendee.id == attendee_id,
            EventAttendee.event_id == event_id
        )
    ).first()
    
    if not attendee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendee not found"
        )
    
    from datetime import datetime
    attendee.status = AttendeeStatus.ATTENDED
    attendee.check_in_time = datetime.utcnow()
    db.commit()
    
    return {"message": "Attendee checked in successfully"}