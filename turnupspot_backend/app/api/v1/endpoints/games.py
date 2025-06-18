from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.sport_group import SportGroupMember, MemberRole
from app.models.game import Game, GameTeam, GamePlayer, GameStatus, PlayerStatus
from app.schemas.game import (
    GameCreate, GameUpdate, GameResponse, GameTimerUpdate, GameScoreUpdate,
    GamePlayerUpdate, GamePlayerResponse
)
from app.core.exceptions import ForbiddenException

router = APIRouter()


@router.post("/", response_model=GameResponse)
def create_game(
    game_data: GameCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new game"""
    # Check if user is admin of the sport group
    membership = db.query(SportGroupMember).filter(
        and_(
            SportGroupMember.sport_group_id == game_data.sport_group_id,
            SportGroupMember.user_id == current_user.id,
            SportGroupMember.role == MemberRole.ADMIN
        )
    ).first()
    
    if not membership:
        raise ForbiddenException("Only group admins can create games")
    
    # Create game
    db_game = Game(
        **game_data.dict(exclude={"teams", "players"})
    )
    
    db.add(db_game)
    db.flush()  # Get the ID without committing
    
    # Create teams
    for team_data in game_data.teams:
        team = GameTeam(
            game_id=db_game.id,
            **team_data.dict()
        )
        db.add(team)
    
    # Create player assignments
    for player_data in game_data.players:
        player = GamePlayer(
            game_id=db_game.id,
            **player_data.dict()
        )
        db.add(player)
    
    db.commit()
    db.refresh(db_game)
    
    return db_game


@router.get("/sport-group/{group_id}", response_model=List[GameResponse])
def get_group_games(
    group_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get games for a sport group"""
    # Check if user is member of the sport group
    membership = db.query(SportGroupMember).filter(
        and_(
            SportGroupMember.sport_group_id == group_id,
            SportGroupMember.user_id == current_user.id,
            SportGroupMember.is_approved == True
        )
    ).first()
    
    if not membership:
        raise ForbiddenException("Only group members can view games")
    
    games = db.query(Game).filter(Game.sport_group_id == group_id).offset(skip).limit(limit).all()
    return games


@router.get("/{game_id}", response_model=GameResponse)
def get_game(
    game_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get game by ID"""
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # Check if user is member of the sport group
    membership = db.query(SportGroupMember).filter(
        and_(
            SportGroupMember.sport_group_id == game.sport_group_id,
            SportGroupMember.user_id == current_user.id,
            SportGroupMember.is_approved == True
        )
    ).first()
    
    if not membership:
        raise ForbiddenException("Only group members can view games")
    
    return game


@router.put("/{game_id}", response_model=GameResponse)
def update_game(
    game_id: int,
    game_update: GameUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update game (admin only)"""
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # Check if user is admin of the sport group
    membership = db.query(SportGroupMember).filter(
        and_(
            SportGroupMember.sport_group_id == game.sport_group_id,
            SportGroupMember.user_id == current_user.id,
            SportGroupMember.role == MemberRole.ADMIN
        )
    ).first()
    
    if not membership:
        raise ForbiddenException("Only group admins can update games")
    
    # Update game
    update_data = game_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(game, field, value)
    
    db.commit()
    db.refresh(game)
    
    return game


@router.post("/{game_id}/timer")
def update_game_timer(
    game_id: int,
    timer_update: GameTimerUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update game timer (referee only)"""
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # Check if user is referee or admin
    membership = db.query(SportGroupMember).filter(
        and_(
            SportGroupMember.sport_group_id == game.sport_group_id,
            SportGroupMember.user_id == current_user.id
        )
    ).first()
    
    is_referee = (game.referee_id == membership.id if membership else False)
    is_admin = (membership.role == MemberRole.ADMIN if membership else False)
    
    if not (is_referee or is_admin):
        raise ForbiddenException("Only referee or admin can control game timer")
    
    # Update timer based on action
    if timer_update.action == "start":
        game.is_timer_running = True
        if game.status == GameStatus.SCHEDULED:
            game.status = GameStatus.IN_PROGRESS
    elif timer_update.action == "stop":
        game.is_timer_running = False
        if game.current_time <= 0:
            game.status = GameStatus.COMPLETED
    elif timer_update.action == "reset":
        game.current_time = timer_update.time or 0
        game.is_timer_running = False
    
    if timer_update.time is not None:
        game.current_time = timer_update.time
    
    db.commit()
    
    return {"message": "Timer updated successfully", "current_time": game.current_time, "is_running": game.is_timer_running}


@router.post("/{game_id}/score")
def update_team_score(
    game_id: int,
    score_update: GameScoreUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update team score (referee only)"""
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # Check if user is referee or admin
    membership = db.query(SportGroupMember).filter(
        and_(
            SportGroupMember.sport_group_id == game.sport_group_id,
            SportGroupMember.user_id == current_user.id
        )
    ).first()
    
    is_referee = (game.referee_id == membership.id if membership else False)
    is_admin = (membership.role == MemberRole.ADMIN if membership else False)
    
    if not (is_referee or is_admin):
        raise ForbiddenException("Only referee or admin can update scores")
    
    # Get team
    team = db.query(GameTeam).filter(
        and_(GameTeam.id == score_update.team_id, GameTeam.game_id == game_id)
    ).first()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Update score based on action
    if score_update.action == "increment":
        team.score += 1
        team.goals_scored += 1
    elif score_update.action == "decrement":
        team.score = max(0, team.score - 1)
        team.goals_scored = max(0, team.goals_scored - 1)
    elif score_update.action == "set" and score_update.value is not None:
        team.score = score_update.value
        team.goals_scored = score_update.value
    
    db.commit()
    
    return {"message": "Score updated successfully", "team_score": team.score}


@router.post("/{game_id}/players/{player_id}/check-in")
def check_in_player(
    game_id: int,
    player_id: int,
    player_update: GamePlayerUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check in a player for the game"""
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # Get player
    player = db.query(GamePlayer).filter(
        and_(GamePlayer.id == player_id, GamePlayer.game_id == game_id)
    ).first()
    
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    # Check if current user is the player or admin
    membership = db.query(SportGroupMember).filter(
        and_(
            SportGroupMember.sport_group_id == game.sport_group_id,
            SportGroupMember.user_id == current_user.id
        )
    ).first()
    
    is_player = (player.member_id == membership.id if membership else False)
    is_admin = (membership.role == MemberRole.ADMIN if membership else False)
    
    if not (is_player or is_admin):
        raise ForbiddenException("Only the player or admin can check in")
    
    # Update player status
    from datetime import datetime
    player.status = PlayerStatus.ARRIVED
    player.arrival_time = datetime.utcnow()
    
    if player_update.check_in_location_lat:
        player.check_in_location_lat = player_update.check_in_location_lat
    if player_update.check_in_location_lng:
        player.check_in_location_lng = player_update.check_in_location_lng
    
    db.commit()
    
    return {"message": "Player checked in successfully"}


@router.get("/{game_id}/players", response_model=List[GamePlayerResponse])
def get_game_players(
    game_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all players for a game"""
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # Check if user is member of the sport group
    membership = db.query(SportGroupMember).filter(
        and_(
            SportGroupMember.sport_group_id == game.sport_group_id,
            SportGroupMember.user_id == current_user.id,
            SportGroupMember.is_approved == True
        )
    ).first()
    
    if not membership:
        raise ForbiddenException("Only group members can view game players")
    
    players = db.query(GamePlayer).filter(GamePlayer.game_id == game_id).all()
    return players


@router.put("/{game_id}/players/{player_id}/stats")
def update_player_stats(
    game_id: int,
    player_id: int,
    player_update: GamePlayerUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update player game stats (referee only)"""
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # Check if user is referee or admin
    membership = db.query(SportGroupMember).filter(
        and_(
            SportGroupMember.sport_group_id == game.sport_group_id,
            SportGroupMember.user_id == current_user.id
        )
    ).first()
    
    is_referee = (game.referee_id == membership.id if membership else False)
    is_admin = (membership.role == MemberRole.ADMIN if membership else False)
    
    if not (is_referee or is_admin):
        raise ForbiddenException("Only referee or admin can update player stats")
    
    # Get player
    player = db.query(GamePlayer).filter(
        and_(GamePlayer.id == player_id, GamePlayer.game_id == game_id)
    ).first()
    
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    # Update player stats
    update_data = player_update.dict(exclude_unset=True, exclude={"check_in_location_lat", "check_in_location_lng", "arrival_time"})
    for field, value in update_data.items():
        if hasattr(player, field):
            setattr(player, field, value)
    
    db.commit()
    db.refresh(player)
    
    return player