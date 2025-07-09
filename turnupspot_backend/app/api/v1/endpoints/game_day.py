# turnupspot_backend/app/api/v1/endpoints/game_day.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
import calendar
import logging

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.sport_group import SportGroupMember, MemberRole, SportGroup
from app.models.game import Game, GameTeam, GamePlayer, GameStatus, PlayerStatus
from app.core.exceptions import ForbiddenException

router = APIRouter()


@router.get("/{sport_group_id}")
def get_game_day_info(
    sport_group_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get game day information for a sport group"""
    # Check if user is member of the sport group
    membership = db.query(SportGroupMember).filter(
        and_(
            SportGroupMember.sport_group_id == sport_group_id,
            SportGroupMember.user_id == current_user.id,
            SportGroupMember.is_approved == True
        )
    ).first()
    
    if not membership:
        raise ForbiddenException("Only group members can view game day info")
    
    # Get sport group
    sport_group = db.query(SportGroup).filter(SportGroup.id == sport_group_id).first()
    if not sport_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sport group not found"
        )
    
    # Check if today is a playing day
    today = datetime.now()
    today_num = today.weekday()  
    playing_days = [int(day.strip()) for day in sport_group.playing_days.split(",") if day.strip().isdigit()]
    is_playing_day = today_num in playing_days
    
    # Get current game if exists
    current_game = db.query(Game).filter(
        and_(
            Game.sport_group_id == sport_group_id,
            Game.game_date == today.date(),
            Game.status.in_([GameStatus.SCHEDULED, GameStatus.IN_PROGRESS])
        )
    ).first()
    
    # Check if check-in should be enabled (1 hour before game start)
    game_start_time = sport_group.game_start_time
    check_in_start_time = datetime.combine(today.date(), game_start_time.time()) - timedelta(hours=1)
    check_in_enabled = today >= check_in_start_time
    
    # Get game day info
    game_day_info = {
        "is_playing_day": is_playing_day,
        "day": today.strftime("%A"),
        "date": today.strftime("%B %d, %Y"),
        "game_start_time": game_start_time.strftime("%I:%M %p"),
        "game_end_time": sport_group.game_end_time.strftime("%I:%M %p"),
        "max_teams": sport_group.max_teams,
        "max_players_per_team": sport_group.max_players_per_team,
        "check_in_enabled": check_in_enabled,
        "current_game_id": current_game.id if current_game else None,
        "game_status": current_game.status if current_game else None,
        "venue_latitude": sport_group.venue_latitude,
        "venue_longitude": sport_group.venue_longitude,
        "venue_radius": 100  # Default radius in meters
    }
    
    return game_day_info


@router.get("/{sport_group_id}/players")
def get_game_day_players(
    sport_group_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all players for game day with their check-in status"""
    # Check if user is member of the sport group
    membership = db.query(SportGroupMember).filter(
        and_(
            SportGroupMember.sport_group_id == sport_group_id,
            SportGroupMember.user_id == current_user.id,
            SportGroupMember.is_approved == True
        )
    ).first()
    
    if not membership:
        raise ForbiddenException("Only group members can view game day players")
    
    # Get all approved members
    members = db.query(SportGroupMember).filter(
        and_(
            SportGroupMember.sport_group_id == sport_group_id,
            SportGroupMember.is_approved == True
        )
    ).all()
    
    # Get current game if exists
    today = datetime.now()
    current_game = db.query(Game).filter(
        and_(
            Game.sport_group_id == sport_group_id,
            Game.game_date == today.date(),
            Game.status.in_([GameStatus.SCHEDULED, GameStatus.IN_PROGRESS])
        )
    ).first()
    
    print(f"Current game found: {current_game.id if current_game else 'None'}")
    
    players = []
    for member in members:
        player_info = {
            "id": member.id,
            "user_id": member.user.id,
            "name": member.user.full_name,
            "status": "expected",
            "arrival_time": None,
            "is_captain": False,
            "team": None
        }
        
        # If there's a current game, get player status from game
        if current_game:
            game_player = db.query(GamePlayer).filter(
                and_(
                    GamePlayer.game_id == current_game.id,
                    GamePlayer.member_id == member.id
                )
            ).first()
            
            if game_player:
                player_info["status"] = game_player.status.value
                player_info["arrival_time"] = game_player.arrival_time.strftime("%H:%M") if game_player.arrival_time else None
                player_info["team"] = game_player.team.team_number if game_player.team else None
                player_info["is_captain"] = (game_player.team and game_player.team.captain_id == member.id)
                
            else:
                print(f"No game player record found for {member.user.full_name}")
        
        players.append(player_info)
    
    return players


@router.post("/{sport_group_id}/check-in")
def check_in_player_game_day(
    sport_group_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check in a player for game day"""
    # Check if user is member of the sport group
    membership = db.query(SportGroupMember).filter(
        and_(
            SportGroupMember.sport_group_id == sport_group_id,
            SportGroupMember.user_id == current_user.id,
            SportGroupMember.is_approved == True
        )
    ).first()
    
    if not membership:
        raise ForbiddenException("Only group members can check in")
    
    # Get sport group
    sport_group = db.query(SportGroup).filter(SportGroup.id == sport_group_id).first()
    if not sport_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sport group not found"
        )
    
    # Check if check-in is enabled (1 hour before game start)
    today = datetime.now()
    game_start_time = sport_group.game_start_time
    check_in_start_time = datetime.combine(today.date(), game_start_time.time()) - timedelta(hours=1)
    
    if today < check_in_start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-in is not enabled yet. It opens 1 hour before game start."
        )
    
    # Get or create current game
    current_game = db.query(Game).filter(
        and_(
            Game.sport_group_id == sport_group_id,
            Game.game_date == today.date(),
            Game.status.in_([GameStatus.SCHEDULED, GameStatus.IN_PROGRESS])
        )
    ).first()
    
    if not current_game:
        # Create new game
        current_game = Game(
            sport_group_id=sport_group_id,
            game_date=today.date(),
            start_time=datetime.combine(today.date(), game_start_time.time()),
            end_time=datetime.combine(today.date(), sport_group.game_end_time.time()),
            status=GameStatus.SCHEDULED
        )
        db.add(current_game)
        db.flush()
        print(f"Created new game with ID: {current_game.id}")
    else:
        print(f"Using existing game with ID: {current_game.id}")
    
    # Check if player already checked in
    existing_player = db.query(GamePlayer).filter(
        and_(
            GamePlayer.game_id == current_game.id,
            GamePlayer.member_id == membership.id
        )
    ).first()
    
    if existing_player and existing_player.status == PlayerStatus.ARRIVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player already checked in"
        )
    
    # Create or update game player
    if existing_player:
        existing_player.status = PlayerStatus.ARRIVED
        existing_player.arrival_time = datetime.utcnow()
        game_player = existing_player
        print(f"Updated existing player {membership.user.full_name} to ARRIVED")
    else:
        game_player = GamePlayer(
            game_id=current_game.id,
            member_id=membership.id,
            status=PlayerStatus.ARRIVED,
            arrival_time=datetime.utcnow()
        )
        db.add(game_player)
        print(f"Created new player record for {membership.user.full_name} with status ARRIVED")
    
    db.commit()
    db.refresh(game_player)
    
    # Verify the player was saved correctly
    saved_player = db.query(GamePlayer).filter(
        and_(
            GamePlayer.game_id == current_game.id,
            GamePlayer.member_id == membership.id
        )
    ).first()
    
    if saved_player:
        print(f"Verified: Player {saved_player.member.user.full_name} has status {saved_player.status.value}")
    else:
        print("ERROR: Could not find saved player record")
    
    # Handle team formation logic
    arrived_players = db.query(GamePlayer).filter(
        and_(
            GamePlayer.game_id == current_game.id,
            GamePlayer.status == PlayerStatus.ARRIVED
        )
    ).all()
    
    # If this is the 11th player or later, add to team 3
    if len(arrived_players) >= 11:
        team_number = 3
        # Find or create team 3
        team = db.query(GameTeam).filter(
            and_(
                GameTeam.game_id == current_game.id,
                GameTeam.team_number == team_number
            )
        ).first()
        
        if not team:
            team = GameTeam(
                game_id=current_game.id,
                team_name=f"Team {team_number}",
                team_number=team_number
            )
            db.add(team)
            db.flush()
        
        # Add player to team if team is not full
        team_players = db.query(GamePlayer).filter(
            and_(
                GamePlayer.game_id == current_game.id,
                GamePlayer.team_id == team.id
            )
        ).count()
        
        if team_players < sport_group.max_players_per_team:
            game_player.team_id = team.id
            db.commit()
    
    return {"message": "Player checked in successfully", "player_id": game_player.id}


@router.post("/{sport_group_id}/teams/assign-captains")
def assign_captains(
    sport_group_id: str,
    captain_assignments: dict,  # {player_id: team_number}
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Assign captains to teams (first 10 players only)"""
    # Check if user is admin of the sport group
    admin_membership = db.query(SportGroupMember).filter(
        and_(
            SportGroupMember.sport_group_id == sport_group_id,
            SportGroupMember.user_id == current_user.id,
            SportGroupMember.role == MemberRole.ADMIN
        )
    ).first()

    # Get current game
    today = datetime.now()
    current_game = db.query(Game).filter(
        and_(
            Game.sport_group_id == sport_group_id,
            Game.game_date == today.date(),
            Game.status.in_([GameStatus.SCHEDULED, GameStatus.IN_PROGRESS])
        )
    ).first()

    if not current_game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active game found"
        )

    # Get first 10 arrived players
    arrived_players = db.query(GamePlayer).filter(
        and_(
            GamePlayer.game_id == current_game.id,
            GamePlayer.status == PlayerStatus.ARRIVED
        )
    ).order_by(GamePlayer.arrival_time.asc()).limit(10).all()

    # Get the current user's membership record
    membership = db.query(SportGroupMember).filter(
        and_(
            SportGroupMember.sport_group_id == sport_group_id,
            SportGroupMember.user_id == current_user.id
        )
    ).first()

    # Now compare membership.id to GamePlayer.member_id
    is_first_ten = any(p.member_id == membership.id for p in arrived_players)

    if not admin_membership and not is_first_ten:
        raise ForbiddenException("Only admins or the first 10 arrived players can assign captains")

    if len(arrived_players) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Need at least 10 players to assign captains"
        )

    # Assign captains
    for player_id, team_number in captain_assignments.items():
        if team_number not in [1, 2]:
            continue
        # Find or create team
        team = db.query(GameTeam).filter(
            and_(
                GameTeam.game_id == current_game.id,
                GameTeam.team_number == team_number
            )
        ).first()
        if not team:
            team = GameTeam(
                game_id=current_game.id,
                team_name=f"Team {team_number}",
                team_number=team_number
            )
            db.add(team)
            db.flush()  # Assigns team.id
            print(f"Created new team: {team.team_name} with id {team.id}")
        # Find player
        player = db.query(GamePlayer).filter(
            and_(
                GamePlayer.game_id == current_game.id,
                GamePlayer.member_id == player_id
            )
        ).first()
        print(f"Assigning captain: player_id={player_id}, team_id={team.id}, player={player}")
        if player:
            team.captain_id = player.member_id
            player.team_id = team.id
            player.is_captain = True
            db.flush()  # Ensure changes are staged for commit
            print(f"After assignment: team.captain_id={team.captain_id}, player.team_id={player.team_id}, player.is_captain={player.is_captain}")
        else:
            print(f"No GamePlayer found for player_id={player_id} in game_id={current_game.id}")
    db.commit()
    return {"message": "Captains assigned successfully"}


@router.post("/{sport_group_id}/teams/select-players")
def select_team_players(
    sport_group_id: str,
    selections: dict,  # {team_number: [player_ids]}
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Captains select players for their teams"""
    # Get current game
    today = datetime.now()
    current_game = db.query(Game).filter(
        and_(
            Game.sport_group_id == sport_group_id,
            Game.game_date == today.date(),
            Game.status.in_([GameStatus.SCHEDULED, GameStatus.IN_PROGRESS])
        )
    ).first()
    
    if not current_game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active game found"
        )
    
    # Get sport group for max players per team
    sport_group = db.query(SportGroup).filter(SportGroup.id == sport_group_id).first()
    
    # Process selections
    for team_number, player_ids in selections.items():
        # Find team
        team = db.query(GameTeam).filter(
            and_(
                GameTeam.game_id == current_game.id,
                GameTeam.team_number == team_number
            )
        ).first()
        
        if not team:
            continue
        
        # Check if current user is captain of this team
        if team.captain_id != current_user.id:
            # Check if user is admin
            membership = db.query(SportGroupMember).filter(
                and_(
                    SportGroupMember.sport_group_id == sport_group_id,
                    SportGroupMember.user_id == current_user.id,
                    SportGroupMember.role == MemberRole.ADMIN
                )
            ).first()
            
            if not membership:
                raise ForbiddenException("Only team captains or admins can select players")
        
        # Add players to team (respecting max players per team)
        current_team_players = db.query(GamePlayer).filter(
            and_(
                GamePlayer.game_id == current_game.id,
                GamePlayer.team_id == team.id
            )
        ).count()
        
        for player_id in player_ids:
            if current_team_players >= sport_group.max_players_per_team:
                break
                
            player = db.query(GamePlayer).filter(
                and_(
                    GamePlayer.game_id == current_game.id,
                    GamePlayer.member_id == player_id,
                    GamePlayer.status == PlayerStatus.ARRIVED,
                    GamePlayer.team_id.is_(None)  # Not already assigned
                )
            ).first()
            
            if player:
                player.team_id = team.id
                current_team_players += 1
    
    db.commit()
    
    return {"message": "Players selected for teams successfully"}