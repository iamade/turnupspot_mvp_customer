from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import uuid

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.sport_group import SportGroup, SportGroupMember, MemberRole, SportsType
from app.models.chat import ChatRoom, ChatRoomType
from app.schemas.sport_group import (
    SportGroupCreate, SportGroupUpdate, SportGroupResponse, 
    SportGroupJoinRequest, SportGroupMemberResponse
)
from app.core.exceptions import GroupNotFoundException, ForbiddenException, UnauthorizedException
from app.services.geocoding import geocoding_service

router = APIRouter()


@router.post("/", response_model=SportGroupResponse)
def create_sport_group(
    sport_group: SportGroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new sport group"""
    # Get coordinates from Google Maps
    latitude, longitude = geocoding_service.get_coordinates(sport_group.venue_address)
    if not latitude or not longitude:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not geocode the venue address"
        )
    
    # Create new sport group
    db_sport_group = SportGroup(
        id=str(uuid.uuid4()),
        **sport_group.dict(),
        venue_latitude=latitude,
        venue_longitude=longitude,
        created_by=current_user.email
    )
    
    db.add(db_sport_group)
    db.commit()
    db.refresh(db_sport_group)
    
    return db_sport_group


@router.get("/", response_model=List[SportGroupResponse])
def get_sport_groups(
    skip: int = 0,
    limit: int = 100,
    sport_type: Optional[SportsType] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get all sport groups with optional filtering"""
    query = db.query(SportGroup).filter(SportGroup.is_active == True)
    
    if sport_type:
        query = query.filter(SportGroup.sport_type == sport_type)
    
    if search:
        query = query.filter(
            or_(
                SportGroup.name.ilike(f"%{search}%"),
                SportGroup.description.ilike(f"%{search}%"),
                SportGroup.venue_name.ilike(f"%{search}%")
            )
        )
    
    groups = query.offset(skip).limit(limit).all()
    
    # Add member count to each group
    for group in groups:
        group.member_count = len([m for m in group.members if m.is_approved])
    
    return groups


@router.get("/{sport_group_id}", response_model=SportGroupResponse)
def get_sport_group(
    sport_group_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific sport group by ID"""
    sport_group = db.query(SportGroup).filter(SportGroup.id == sport_group_id).first()
    if not sport_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sport group not found"
        )
    return sport_group


@router.put("/{sport_group_id}", response_model=SportGroupResponse)
def update_sport_group(
    sport_group_id: str,
    sport_group_update: SportGroupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a sport group"""
    db_sport_group = db.query(SportGroup).filter(SportGroup.id == sport_group_id).first()
    if not db_sport_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sport group not found"
        )
    
    if db_sport_group.created_by != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this sport group"
        )
    
    # If venue address is being updated, get new coordinates
    update_data = sport_group_update.dict(exclude_unset=True)
    if "venue_address" in update_data:
        latitude, longitude = geocoding_service.get_coordinates(update_data["venue_address"])
        if not latitude or not longitude:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not geocode the new venue address"
            )
        update_data["venue_latitude"] = latitude
        update_data["venue_longitude"] = longitude
    
    for field, value in update_data.items():
        setattr(db_sport_group, field, value)
    
    db.commit()
    db.refresh(db_sport_group)
    
    return db_sport_group


@router.delete("/{sport_group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sport_group(
    sport_group_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a sport group"""
    db_sport_group = db.query(SportGroup).filter(SportGroup.id == sport_group_id).first()
    if not db_sport_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sport group not found"
        )
    
    if db_sport_group.created_by != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this sport group"
        )
    
    db.delete(db_sport_group)
    db.commit()
    
    return None


@router.post("/{group_id}/join")
def join_sport_group(
    group_id: int,
    join_request: SportGroupJoinRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join a sport group"""
    group = db.query(SportGroup).filter(
        and_(SportGroup.id == group_id, SportGroup.is_active == True)
    ).first()
    
    if not group:
        raise GroupNotFoundException()
    
    # Check if user is already a member
    existing_membership = db.query(SportGroupMember).filter(
        and_(
            SportGroupMember.sport_group_id == group_id,
            SportGroupMember.user_id == current_user.id
        )
    ).first()
    
    if existing_membership:
        if existing_membership.is_approved:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already a member of this group"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Your join request is pending approval"
            )
    
    # Create membership request
    membership = SportGroupMember(
        sport_group_id=group_id,
        user_id=current_user.id,
        role=MemberRole.MEMBER,
        is_approved=False  # Requires approval
    )
    
    db.add(membership)
    db.commit()
    
    return {"message": "Join request submitted successfully"}


@router.post("/{group_id}/leave")
def leave_sport_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Leave a sport group"""
    membership = db.query(SportGroupMember).filter(
        and_(
            SportGroupMember.sport_group_id == group_id,
            SportGroupMember.user_id == current_user.id
        )
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not a member of this group"
        )
    
    # Check if user is the creator
    group = db.query(SportGroup).filter(SportGroup.id == group_id).first()
    if group and group.creator_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group creator cannot leave the group. Transfer ownership or delete the group."
        )
    
    db.delete(membership)
    db.commit()
    
    return {"message": "Left group successfully"}


@router.get("/{group_id}/members", response_model=List[SportGroupMemberResponse])
def get_group_members(
    group_id: int,
    include_pending: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get group members"""
    group = db.query(SportGroup).filter(SportGroup.id == group_id).first()
    if not group:
        raise GroupNotFoundException()
    
    # Check if user is a member of the group
    membership = db.query(SportGroupMember).filter(
        and_(
            SportGroupMember.sport_group_id == group_id,
            SportGroupMember.user_id == current_user.id
        )
    ).first()
    
    if not membership:
        raise ForbiddenException("Only group members can view member list")
    
    query = db.query(SportGroupMember).filter(SportGroupMember.sport_group_id == group_id)
    
    if not include_pending:
        query = query.filter(SportGroupMember.is_approved == True)
    
    members = query.all()
    return members


@router.post("/{group_id}/members/{member_id}/approve")
def approve_member(
    group_id: int,
    member_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve a member join request (admin only)"""
    # Check if current user is admin of the group
    admin_membership = db.query(SportGroupMember).filter(
        and_(
            SportGroupMember.sport_group_id == group_id,
            SportGroupMember.user_id == current_user.id,
            SportGroupMember.role == MemberRole.ADMIN
        )
    ).first()
    
    if not admin_membership:
        raise ForbiddenException("Only group admins can approve members")
    
    # Get the membership to approve
    membership = db.query(SportGroupMember).filter(
        and_(
            SportGroupMember.sport_group_id == group_id,
            SportGroupMember.id == member_id
        )
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    membership.is_approved = True
    db.commit()
    
    return {"message": "Member approved successfully"}


@router.delete("/{group_id}/members/{member_id}")
def remove_member(
    group_id: int,
    member_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a member from the group (admin only)"""
    # Check if current user is admin of the group
    admin_membership = db.query(SportGroupMember).filter(
        and_(
            SportGroupMember.sport_group_id == group_id,
            SportGroupMember.user_id == current_user.id,
            SportGroupMember.role == MemberRole.ADMIN
        )
    ).first()
    
    if not admin_membership:
        raise ForbiddenException("Only group admins can remove members")
    
    # Get the membership to remove
    membership = db.query(SportGroupMember).filter(
        and_(
            SportGroupMember.sport_group_id == group_id,
            SportGroupMember.id == member_id
        )
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    # Check if trying to remove the group creator
    group = db.query(SportGroup).filter(SportGroup.id == group_id).first()
    if group and group.creator_id == membership.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove group creator"
        )
    
    db.delete(membership)
    db.commit()
    
    return {"message": "Member removed successfully"}