from typing import List, Optional
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Query,
    File,
    UploadFile,
    Form,
)
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import uuid
from io import BytesIO
from fastapi.responses import StreamingResponse
import os
from datetime import datetime
from sqlalchemy.orm import Session, selectinload
from uuid import uuid4
import logging

from app.core.database import get_db
from app.api.deps import get_current_user, get_optional_current_user
from app.models.user import User
from app.models.sport_group import (
    SportGroup,
    SportGroupMember,
    MemberRole,
    SportsType,
    PlayingDay,
    Day,
    Team,
    TeamMember,
)
from app.models.chat import ChatRoom, ChatRoomType, ChatMessage
from app.models.game import Game, GameTeam, GamePlayer, Match
from app.models.manual_checkin import GameDayParticipant
from app.schemas.sport_group import (
    SportGroupCreate,
    SportGroupUpdate,
    SportGroupResponse,
    SportGroupJoinRequest,
    SportGroupMemberResponse,
)
from app.core.exceptions import (
    GroupNotFoundException,
    ForbiddenException,
    UnauthorizedException,
)
from app.services.geocoding import geocoding_service
from app.services.qr_code import generate_qr_code
from app.services.team_formation import (
    form_teams_first_come,
    form_teams_random,
    rotate_teams_winner_stays,
)
from app.services.tournament_service import (
    create_tournament,
    add_tournament_result,
    get_tournament_results,
)
from app.services.stats import submit_stat, approve_stat, reject_stat, get_pending_stats

router = APIRouter()


@router.get("/my", response_model=List[SportGroupResponse])
def get_my_sport_groups(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    # Groups created by user
    created = db.query(SportGroup).filter(SportGroup.created_by == current_user.email)
    # Groups where user is a member
    member = (
        db.query(SportGroup)
        .join(SportGroupMember)
        .filter(SportGroupMember.user_id == current_user.id)
    )
    groups = (
        db.query(SportGroup)
        .join(SportGroupMember, SportGroupMember.sport_group_id == SportGroup.id)
        .options(
            selectinload(SportGroup.playing_days)  # Explicitly load the relationship
        )
        .filter(SportGroupMember.user_id == current_user.id)
        .all()
    )

    return groups

    # # Union and remove duplicates
    # groups = {g.id: g for g in created.all()}
    # for g in member.all():
    #     groups[g.id] = g
    # # Add member count to each group
    # for group in groups.values():
    #     group.member_count = len([m for m in group.members if m.is_approved])
    # return list(groups.values())


@router.post("/", response_model=SportGroupResponse)
async def create_sport_group(
    name: str = Form(...),
    description: str = Form(...),
    venue_name: str = Form(...),
    venue_address: str = Form(...),
    venue_latitude: float = Form(...),
    venue_longitude: float = Form(...),
    playing_days: str = Form(...),
    game_start_time: str = Form(...),
    game_end_time: str = Form(...),
    max_teams: int = Form(...),
    max_players_per_team: int = Form(...),
    rules: Optional[str] = Form(None),
    game_config: Optional[str] = Form(None),
    min_players_per_team: int = Form(3),
    referee_required: bool = Form(False),
    sports_type: str = Form(...),
    venue_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new sport group with file upload support"""

    # Validate coordinates
    if not venue_latitude or not venue_longitude:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Latitude and longitude are required",
        )

    # Handle venue image upload
    venue_image_url = None
    if venue_image:
        # Create uploads directory if it doesn't exist
        upload_dir = "static/uploads"
        os.makedirs(upload_dir, exist_ok=True)

        # Generate unique filename
        file_extension = (
            os.path.splitext(venue_image.filename)[1]
            if venue_image.filename
            else ".jpg"
        )
        filename = f"venue_{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, filename)

        # Save file
        with open(file_path, "wb") as buffer:
            content = await venue_image.read()
            buffer.write(content)

        venue_image_url = f"/static/uploads/{filename}"

    # Parse game times
    try:
        game_start_datetime = datetime.strptime(game_start_time, "%H:%M")
        game_end_datetime = datetime.strptime(game_end_time, "%H:%M")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid time format. Use HH:MM format",
        )

    try:
        # Parse the JSON string to get list of day objects
        import json

        playing_days_data = json.loads(playing_days)

        # Convert to PlayingDay model instances
        playing_days_objects = []
        for day_data in playing_days_data:
            playing_day = PlayingDay(
                id=str(uuid4()),
                day=Day(day_data["day"]),  # Convert string to Day enum
                sport_group_id=None,  # Will be set when SportGroup is created
            )
            playing_days_objects.append(playing_day)

        # Create new sport group
        db_sport_group = SportGroup(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            venue_name=venue_name,
            venue_address=venue_address,
            venue_latitude=venue_latitude,
            venue_longitude=venue_longitude,
            venue_image_url=venue_image_url,
            game_start_time=game_start_datetime,
            game_end_time=game_end_datetime,
            max_teams=max_teams,
            max_players_per_team=max_players_per_team,
            rules=rules,
            game_config=game_config,
            min_players_per_team=min_players_per_team,
            referee_required=referee_required,
            sports_type=SportsType(sports_type),
            created_by=current_user.email,
            creator_id=current_user.id,
        )

        db.add(db_sport_group)
        db.flush()

        # Now set the sport_group_id for playing_days and add them
        for playing_day in playing_days_objects:
            playing_day.sport_group_id = db_sport_group.id
            db.add(playing_day)

        # Automatically add creator as a member (admin, approved)
        creator_membership = SportGroupMember(
            sport_group_id=db_sport_group.id,
            user_id=current_user.id,
            role=MemberRole.ADMIN,
            is_approved=True,
        )
        db.add(creator_membership)

        db.commit()
        db.refresh(db_sport_group)

        return db_sport_group

    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid playing_days format: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error creating sport group: {str(e)}"
        )


@router.get("/", response_model=List[SportGroupResponse])
def get_sport_groups(
    skip: int = 0,
    limit: int = 100,
    sport_type: Optional[SportsType] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    # current_user: Optional[User] = Depends(get_current_user)  # Removed for public access
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
                SportGroup.venue_name.ilike(f"%{search}%"),
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
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Get a specific sport group by ID"""
    sport_group = db.query(SportGroup).filter(SportGroup.id == sport_group_id).first()
    if not sport_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sport group not found"
        )

    # Add member count
    sport_group.member_count = len([m for m in sport_group.members if m.is_approved])

    # Add current user's membership status if authenticated
    if current_user:
        user_membership = (
            db.query(SportGroupMember)
            .filter(
                and_(
                    SportGroupMember.sport_group_id == sport_group_id,
                    SportGroupMember.user_id == current_user.id,
                )
            )
            .first()
        )

        if user_membership:
            sport_group.current_user_membership = {
                "is_member": user_membership.is_approved,
                "is_pending": not user_membership.is_approved,
                "role": user_membership.role,
                "is_creator": sport_group.creator_id == current_user.id,
            }
        else:
            sport_group.current_user_membership = {
                "is_member": False,
                "is_pending": False,
                "role": None,
                "is_creator": False,
            }
    else:
        sport_group.current_user_membership = None

    return sport_group


@router.put("/{sport_group_id}", response_model=SportGroupResponse)
def update_sport_group(
    sport_group_id: str,
    sport_group_update: SportGroupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a sport group"""
    db_sport_group = (
        db.query(SportGroup).filter(SportGroup.id == sport_group_id).first()
    )
    if not db_sport_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sport group not found"
        )

    if db_sport_group.created_by != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this sport group",
        )

    # If venue address is being updated, get new coordinates
    update_data = sport_group_update.dict(exclude_unset=True)
    if "venue_address" in update_data:
        latitude, longitude = geocoding_service.get_coordinates(
            update_data["venue_address"]
        )
        if not latitude or not longitude:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not geocode the new venue address",
            )
        update_data["venue_latitude"] = latitude
        update_data["venue_longitude"] = longitude

    # Handle playing_days separately
    playing_days_update = update_data.pop("playing_days", None)

    # Update other fields
    for field, value in update_data.items():
        setattr(db_sport_group, field, value)

    # Handle playing days update
    if playing_days_update is not None:
        # Delete existing playing days
        db.query(PlayingDay).filter(
            PlayingDay.sport_group_id == sport_group_id
        ).delete()
        db.flush()
        # Create new playing days
        for day_string in playing_days_update:
            # Convert string to Day enum
            if day_string in [d.value for d in Day]:
                day_enum = Day(day_string)
                playing_day = PlayingDay(
                    id=str(uuid.uuid4()),  # Generate UUID for the playing day
                    sport_group_id=sport_group_id,
                    day=day_enum,
                )
                db.add(playing_day)

    db.commit()
    db.refresh(db_sport_group)

    return db_sport_group


@router.delete("/{sport_group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sport_group(
    sport_group_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a sport group and all related records"""
    logger = logging.getLogger(__name__)

    db_sport_group = (
        db.query(SportGroup).filter(SportGroup.id == sport_group_id).first()
    )
    if not db_sport_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sport group not found"
        )

    if db_sport_group.created_by != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this sport group",
        )

    try:
        logger.info(f"Starting deletion of sport group {sport_group_id}")

        # Check what related records exist before deletion
        members_count = (
            db.query(SportGroupMember)
            .filter(SportGroupMember.sport_group_id == sport_group_id)
            .count()
        )
        games_count = (
            db.query(Game).filter(Game.sport_group_id == sport_group_id).count()
        )
        teams_count = (
            db.query(Team).filter(Team.sport_group_id == sport_group_id).count()
        )
        chat_rooms_count = (
            db.query(ChatRoom).filter(ChatRoom.sport_group_id == sport_group_id).count()
        )
        chat_messages_count = (
            db.query(ChatMessage)
            .filter(
                ChatMessage.chat_room_id.in_(
                    db.query(ChatRoom.id).filter(
                        ChatRoom.sport_group_id == sport_group_id
                    )
                )
            )
            .count()
        )
        game_teams_count = (
            db.query(GameTeam)
            .filter(
                GameTeam.game_id.in_(
                    db.query(Game.id).filter(Game.sport_group_id == sport_group_id)
                )
            )
            .count()
        )
        game_players_count = (
            db.query(GamePlayer)
            .filter(
                GamePlayer.game_id.in_(
                    db.query(Game.id).filter(Game.sport_group_id == sport_group_id)
                )
            )
            .count()
        )
        matches_count = (
            db.query(Match)
            .filter(
                Match.game_id.in_(
                    db.query(Game.id).filter(Game.sport_group_id == sport_group_id)
                )
            )
            .count()
        )
        team_members_count = (
            db.query(TeamMember)
            .filter(
                TeamMember.team_id.in_(
                    db.query(Team.id).filter(Team.sport_group_id == sport_group_id)
                )
            )
            .count()
        )
        game_day_participants_count = (
            db.query(GameDayParticipant)
            .filter(
                GameDayParticipant.game_id.in_(
                    db.query(Game.id).filter(Game.sport_group_id == sport_group_id)
                )
            )
            .count()
        )
        logger.info(
            f"Before deletion: {members_count} members, {games_count} games, {teams_count} teams, {chat_rooms_count} chat rooms, {chat_messages_count} chat messages, {game_teams_count} game teams, {game_players_count} game players, {matches_count} matches, {team_members_count} team members, {game_day_participants_count} game day participants"
        )

        # Delete in correct order to avoid foreign key violations

        # 1. Delete chat messages first
        chat_messages_deleted = (
            db.query(ChatMessage)
            .filter(
                ChatMessage.chat_room_id.in_(
                    db.query(ChatRoom.id).filter(
                        ChatRoom.sport_group_id == sport_group_id
                    )
                )
            )
            .delete(synchronize_session=False)
        )
        logger.info(f"Deleted {chat_messages_deleted} chat messages")

        # 2. Delete chat rooms
        chat_rooms_deleted = (
            db.query(ChatRoom)
            .filter(ChatRoom.sport_group_id == sport_group_id)
            .delete()
        )
        logger.info(f"Deleted {chat_rooms_deleted} chat rooms")

        # 3. Delete matches first (they reference game_teams)
        matches_deleted = (
            db.query(Match)
            .filter(
                Match.game_id.in_(
                    db.query(Game.id).filter(Game.sport_group_id == sport_group_id)
                )
            )
            .delete(synchronize_session=False)
        )
        logger.info(f"Deleted {matches_deleted} matches")

        # 4. Delete game players
        game_players_deleted = (
            db.query(GamePlayer)
            .filter(
                GamePlayer.game_id.in_(
                    db.query(Game.id).filter(Game.sport_group_id == sport_group_id)
                )
            )
            .delete(synchronize_session=False)
        )
        logger.info(f"Deleted {game_players_deleted} game players")

        # 5. Delete game teams
        game_teams_deleted = (
            db.query(GameTeam)
            .filter(
                GameTeam.game_id.in_(
                    db.query(Game.id).filter(Game.sport_group_id == sport_group_id)
                )
            )
            .delete(synchronize_session=False)
        )
        logger.info(f"Deleted {game_teams_deleted} game teams")

        # 6. Delete game day participants
        game_day_participants_deleted = (
            db.query(GameDayParticipant)
            .filter(
                GameDayParticipant.game_id.in_(
                    db.query(Game.id).filter(Game.sport_group_id == sport_group_id)
                )
            )
            .delete(synchronize_session=False)
        )
        logger.info(f"Deleted {game_day_participants_deleted} game day participants")

        # 7. Delete games
        games_deleted = (
            db.query(Game).filter(Game.sport_group_id == sport_group_id).delete()
        )
        logger.info(f"Deleted {games_deleted} games")

        # 7. Delete team members
        team_members_deleted = (
            db.query(TeamMember)
            .filter(
                TeamMember.team_id.in_(
                    db.query(Team.id).filter(Team.sport_group_id == sport_group_id)
                )
            )
            .delete(synchronize_session=False)
        )
        logger.info(f"Deleted {team_members_deleted} team members")

        # 8. Delete teams
        teams_deleted = (
            db.query(Team).filter(Team.sport_group_id == sport_group_id).delete()
        )
        logger.info(f"Deleted {teams_deleted} teams")

        # 9. Delete sport group members
        members_deleted = (
            db.query(SportGroupMember)
            .filter(SportGroupMember.sport_group_id == sport_group_id)
            .delete()
        )
        logger.info(f"Deleted {members_deleted} sport group members")

        # Finally delete the sport group (playing days will be deleted via cascade)
        db.delete(db_sport_group)
        logger.info(f"Deleted sport group {sport_group_id}")

        db.commit()

    except Exception as e:
        logger.error(f"Error deleting sport group {sport_group_id}: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete sport group: {str(e)}",
        )

    return None


@router.post("/{group_id}/join")
def join_sport_group(
    group_id: str,
    join_request: SportGroupJoinRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Join a sport group"""
    group = (
        db.query(SportGroup)
        .filter(and_(SportGroup.id == group_id, SportGroup.is_active == True))
        .first()
    )

    if not group:
        raise GroupNotFoundException()

    # Check if user is already a member
    existing_membership = (
        db.query(SportGroupMember)
        .filter(
            and_(
                SportGroupMember.sport_group_id == group_id,
                SportGroupMember.user_id == current_user.id,
            )
        )
        .first()
    )

    if existing_membership:
        if existing_membership.is_approved:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already a member of this group",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Your join request is pending approval",
            )

    # Create membership request
    membership = SportGroupMember(
        sport_group_id=group_id,
        user_id=current_user.id,
        role=MemberRole.MEMBER,
        is_approved=False,  # Requires approval
    )

    db.add(membership)
    db.commit()

    return {"message": "Join request submitted successfully"}


@router.post("/{group_id}/leave")
def leave_sport_group(
    group_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Leave a sport group"""
    membership = (
        db.query(SportGroupMember)
        .filter(
            and_(
                SportGroupMember.sport_group_id == group_id,
                SportGroupMember.user_id == current_user.id,
            )
        )
        .first()
    )

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not a member of this group",
        )

    # Check if user is the creator
    group = db.query(SportGroup).filter(SportGroup.id == group_id).first()
    if group and group.creator_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group creator cannot leave the group. Transfer ownership or delete the group.",
        )

    db.delete(membership)
    db.commit()

    return {"message": "Left group successfully"}


@router.get("/{group_id}/members", response_model=List[SportGroupMemberResponse])
def get_group_members(
    group_id: str,
    include_pending: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get group members"""
    group = db.query(SportGroup).filter(SportGroup.id == group_id).first()
    if not group:
        raise GroupNotFoundException()

    # Check if user is a member of the group
    membership = (
        db.query(SportGroupMember)
        .filter(
            and_(
                SportGroupMember.sport_group_id == group_id,
                SportGroupMember.user_id == current_user.id,
            )
        )
        .first()
    )

    if not membership:
        raise ForbiddenException("Only group members can view member list")

    query = db.query(SportGroupMember).filter(
        SportGroupMember.sport_group_id == group_id
    )

    if include_pending:
        query = query.filter(SportGroupMember.is_approved == False)
    else:
        query = query.filter(SportGroupMember.is_approved == True)

    members = query.all()
    return members


@router.post("/{group_id}/members/{member_id}/approve")
def approve_member(
    group_id: str,
    member_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Approve a member join request (admin only)"""
    # Check if current user is admin of the group
    admin_membership = (
        db.query(SportGroupMember)
        .filter(
            and_(
                SportGroupMember.sport_group_id == group_id,
                SportGroupMember.user_id == current_user.id,
                SportGroupMember.role == MemberRole.ADMIN,
            )
        )
        .first()
    )

    if not admin_membership:
        raise ForbiddenException("Only group admins can approve members")

    # Get the membership to approve
    membership = (
        db.query(SportGroupMember)
        .filter(
            and_(
                SportGroupMember.sport_group_id == group_id,
                SportGroupMember.id == member_id,
            )
        )
        .first()
    )

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Member not found"
        )

    membership.is_approved = True
    db.commit()

    return {"message": "Member approved successfully"}


@router.delete("/{group_id}/members/{member_id}")
def remove_member(
    group_id: str,
    member_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a member from the group (admin only)"""
    # Check if current user is admin of the group
    admin_membership = (
        db.query(SportGroupMember)
        .filter(
            and_(
                SportGroupMember.sport_group_id == group_id,
                SportGroupMember.user_id == current_user.id,
                SportGroupMember.role == MemberRole.ADMIN,
            )
        )
        .first()
    )

    if not admin_membership:
        raise ForbiddenException("Only group admins can remove members")

    # Get the membership to remove
    membership = (
        db.query(SportGroupMember)
        .filter(
            and_(
                SportGroupMember.sport_group_id == group_id,
                SportGroupMember.id == member_id,
            )
        )
        .first()
    )

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Member not found"
        )

    # Check if trying to remove the group creator
    group = db.query(SportGroup).filter(SportGroup.id == group_id).first()
    if group and group.creator_id == membership.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove group creator",
        )

    db.delete(membership)
    db.commit()

    return {"message": "Member removed successfully"}


@router.post("/{group_id}/members/{member_id}/make-admin")
def make_member_admin(
    group_id: str,
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check if current_user is admin of the group
    membership = (
        db.query(SportGroupMember)
        .filter(
            SportGroupMember.sport_group_id == group_id,
            SportGroupMember.user_id == current_user.id,
            SportGroupMember.role == MemberRole.ADMIN,
        )
        .first()
    )
    if not membership:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Find the member to promote
    member = (
        db.query(SportGroupMember)
        .filter(
            SportGroupMember.sport_group_id == group_id,
            SportGroupMember.id == member_id,
        )
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    member.role = MemberRole.ADMIN
    db.commit()
    db.refresh(member)
    return {"message": "Member promoted to admin"}


# QR Code Invite Endpoint
@router.get("/{group_id}/invite/qr")
def get_group_invite_qr(group_id: str):
    invite_url = f"https://yourapp.com/join/{group_id}"
    qr_bytes = generate_qr_code(invite_url)
    return StreamingResponse(BytesIO(qr_bytes), media_type="image/png")


# Team Formation Endpoint
@router.post("/{group_id}/form-teams")
def form_teams(
    group_id: str,
    method: str = "first_come",
    team_size: int = 5,
    db: Session = Depends(get_db),
):
    group = db.query(SportGroup).filter(SportGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    players = [dict(user_id=m.user_id) for m in group.members if m.is_approved]
    if method == "random":
        teams = form_teams_random(players, team_size)
    else:
        teams = form_teams_first_come(players, team_size)
    return {"teams": teams}


# Tournament Management Endpoints
@router.post("/{group_id}/tournament")
def create_group_tournament(
    group_id: str, name: str, teams: list, prize: float = None, escrow: float = None
):
    tournament = create_tournament(group_id, name, teams, prize, escrow)
    return {"tournament_id": tournament.id}


@router.post("/{group_id}/tournament/result")
def add_group_tournament_result(group_id: str, result: dict):
    success = add_tournament_result(group_id, result)
    return {"ok": success}


@router.get("/{group_id}/tournament/results")
def get_group_tournament_results(group_id: str):
    results = get_tournament_results(group_id)
    return {"results": results}


# Stats Approval Endpoints
@router.post("/stats/submit")
def submit_game_stat(stat: dict):
    submit_stat(stat)
    return {"ok": True}


@router.get("/stats/pending")
def get_pending_game_stats():
    return {"pending": get_pending_stats()}


@router.post("/stats/approve/{stat_idx}")
def approve_game_stat(stat_idx: int):
    ok = approve_stat(stat_idx)
    return {"ok": ok}


@router.post("/stats/reject/{stat_idx}")
def reject_game_stat(stat_idx: int):
    ok = reject_stat(stat_idx)
    return {"ok": ok}
