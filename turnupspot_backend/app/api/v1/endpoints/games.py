from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from uuid import UUID
import uuid 

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.sport_group import SportGroup, SportGroupMember, MemberRole
from app.models.game import Game, GameTeam, GamePlayer, GameStatus, PlayerStatus, Match, MatchStatus, CoinTossType
from app.schemas.game import (
    GameCreate, GameUpdate, GameResponse, GameTimerUpdate, GameScoreUpdate,
    GamePlayerUpdate, GamePlayerResponse
)
from app.core.exceptions import ForbiddenException
from datetime import datetime, timezone
import random

from app.models.manual_checkin import GameDayParticipant
try:
    from zoneinfo import ZoneInfo
    MOUNTAIN_TZ = ZoneInfo("America/Denver")
except ImportError:
    import pytz
    MOUNTAIN_TZ = pytz.timezone("America/Denver")

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
    game_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get game by ID"""
    game = db.query(Game).filter(Game.id == str(game_id)).first()
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
    game_id: UUID,
    game_update: GameUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update game (admin only)"""
    game = db.query(Game).filter(Game.id == str(game_id)).first()
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
    game_id: UUID,
    timer_update: GameTimerUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update game timer (referee only)"""
    game = db.query(Game).filter(Game.id == str(game_id)).first()
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
        game.timer_is_running = True
        if game.status == GameStatus.SCHEDULED:
            game.status = GameStatus.IN_PROGRESS
    elif timer_update.action == "pause":
        # Store current remaining time and stop the timer
        remaining_time = game.get_remaining_time()
        game.timer_remaining_seconds = remaining_time
        game.timer_is_running = False
        game.timer_started_at = None
    elif timer_update.action == "resume":
        # Start the timer again from current remaining time
        game.timer_is_running = True
        game.timer_started_at = datetime.now(timezone.utc)
    elif timer_update.action == "stop":
        game.timer_is_running = False
        if game.current_time <= 0:
            game.status = GameStatus.COMPLETED
    elif timer_update.action == "reset":
        game.current_time = timer_update.time or 0
        game.timer_is_running = False
    
    if timer_update.time is not None:
        game.current_time = timer_update.time
    
    db.commit()
    
    return {"message": "Timer updated successfully", "current_time": game.current_time, "is_running": game.is_timer_running}

@router.get("/{game_id}/teams")
def get_game_teams(
    game_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all teams for a game with their details"""
    # Get all teams for this game
    teams = db.query(GameTeam).filter(GameTeam.game_id == game_id).all()
    
    team_data = []
    for team in teams:
        # Count players in this team (both registered and manual participants)
        registered_players = db.query(GamePlayer).filter(
            and_(GamePlayer.game_id == game_id, GamePlayer.team_id == team.id)
        ).count()
        
        manual_players = db.query(GameDayParticipant).filter(
            and_(GameDayParticipant.game_id == game_id, GameDayParticipant.team == team.team_number)
        ).count()
        
        team_info = {
            "id": team.id,
            "name": team.team_name,
            "team_number": team.team_number,
            "captain_id": team.captain_id,
            "player_count": registered_players + manual_players,
            "registered_players": registered_players,
            "manual_players": manual_players
        }
        team_data.append(team_info)
    
    return {"teams": team_data}

@router.get("/{game_id}/state")
def get_game_state(
    game_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current game state including matches and teams"""
    # Get the game first to check timer status
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    # Check if timer has expired and handle automatic match completion
    if game.is_timer_expired() and game.status == GameStatus.IN_PROGRESS:
        current_match = db.query(Match).filter(
            and_(
                Match.game_id == game_id,
                Match.status == MatchStatus.IN_PROGRESS
            )
        ).first()

        # If there's a current match, automatically complete it
        if current_match:
            # Complete the match
            current_match.status = MatchStatus.COMPLETED
            current_match.completed_at = datetime.now(timezone.utc)

            # Determine winner or draw
            if current_match.team_a_score > current_match.team_b_score:
                current_match.winner_id = current_match.team_a_id
                current_match.is_draw = False
            elif current_match.team_b_score > current_match.team_a_score:
                current_match.winner_id = current_match.team_b_id
                current_match.is_draw = False
            else:
                # It's a draw
                current_match.is_draw = True
                current_match.winner_id = None

                # Determine draw state using unified function
                # Note: We need to determine if we're in knockout stage for the draw logic
                # For timer expiration, we'll assume first rotation for simplicity
                draw_state = _determine_draw_state(current_match, is_knockout_stage=False, db=db)

                if draw_state["requires_coin_toss"]:
                    current_match.requires_coin_toss = True
                    current_match.coin_toss_type = draw_state["coin_toss_type"].value

                    # Set coin toss state for the game
                    game.coin_toss_state = {
                        "pending": True,
                        "team_a_id": current_match.team_a_id,
                        "team_b_id": current_match.team_b_id,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "stage": "first_rotation",
                        "draw_type": draw_state["draw_type"],
                        "purpose": draw_state["purpose"]
                    }

                    # Stop the timer when coin toss is required - game pauses until coin toss is completed
                    game.timer_is_running = False
                    game.timer_started_at = None
                    game.timer_remaining_seconds = 420

            db.commit()

    # Get current match (may have been updated above)
    current_match = db.query(Match).filter(
        and_(
            Match.game_id == game_id,
            Match.status == MatchStatus.IN_PROGRESS
        )
    ).first()
    
    # Get completed matches
    completed_matches = db.query(Match).filter(
        and_(
            Match.game_id == game_id,
            Match.status == MatchStatus.COMPLETED
        )
    ).order_by(Match.completed_at.desc()).all()
    
    # Get scheduled match (next match)
    scheduled_match = db.query(Match).filter(
        and_(
            Match.game_id == game_id,
            Match.status == MatchStatus.SCHEDULED
        )
    ).first()
    
    
    # Get all teams for this game
    teams = db.query(GameTeam).filter(GameTeam.game_id == game_id).all()
    
    # Create team info mapping
    team_info = {}
    teams_with_players = []
    
    for team in teams:
        # Count registered players
        registered_players = db.query(GamePlayer).filter(
            and_(GamePlayer.game_id == game_id, GamePlayer.team_id == team.id)
        ).count()
        
        # Count manual participants
        manual_players = db.query(GameDayParticipant).filter(
            and_(GameDayParticipant.game_id == game_id, GameDayParticipant.team == team.team_number)
        ).count()
        
        total_players = registered_players + manual_players
        
        team_info[team.id] = {
            "id": team.id,
            "name": team.team_name,
            "team_number": team.team_number,
            "captain_id": team.captain_id,
            "player_count": total_players,
            "registered_players": registered_players,
            "manual_players": manual_players
        }
        
         # Only include teams with players
        if total_players > 0:
            teams_with_players.append(team)
        
     # Determine available teams (teams not currently playing AND have players)
    currently_playing_team_ids = set()
    if current_match:
        currently_playing_team_ids.add(current_match.team_a_id)
        currently_playing_team_ids.add(current_match.team_b_id)
    
    available_teams = []
    for team in teams_with_players:
        if team.id not in currently_playing_team_ids:
            available_teams.append({
                "id": team.id,
                "name": team.team_name,
                "team_number": team.team_number,
                "captain_id": team.captain_id,
                "player_count": team_info[team.id]["player_count"]
            })
    
    # Sort available teams by team number for consistent ordering
    available_teams.sort(key=lambda x: x["team_number"])
    
    
    # Check if all teams have played at least once
    teams_that_played = set()
    for match in completed_matches:
        if match.team_a_id in team_info and team_info[match.team_a_id]["player_count"] > 0:
            teams_that_played.add(match.team_a_id)
        if match.team_b_id in team_info and team_info[match.team_b_id]["player_count"] > 0:
            teams_that_played.add(match.team_b_id)
    
    # Determine if we're in knockout stage
    total_teams_with_players = len(teams_with_players)
    is_knockout_stage = len(teams_that_played) >= total_teams_with_players and total_teams_with_players > 0
    
    # Check for coin toss requirement
    game = db.query(Game).filter(Game.id == game_id).first()
    coin_toss_state = None

    # Check if we need coin toss (from game or based on scheduled matches)
    if hasattr(game, 'coin_toss_state') and game.coin_toss_state:
        coin_toss_state = game.coin_toss_state
    else:
        # Check if any scheduled match requires coin toss
        scheduled_match_requiring_toss = db.query(Match).filter(
            and_(
                Match.game_id == game_id,
                Match.status == MatchStatus.SCHEDULED,
                Match.requires_coin_toss == True
            )
        ).first()

        if scheduled_match_requiring_toss:
            coin_toss_type = scheduled_match_requiring_toss.coin_toss_type or CoinTossType.DRAW_DECIDER
            coin_toss_state = {
                "pending": True,
                "team_a_id": scheduled_match_requiring_toss.team_a_id,
                "team_b_id": scheduled_match_requiring_toss.team_b_id,
                "match_id": scheduled_match_requiring_toss.id,
                "coin_toss_type": coin_toss_type if isinstance(coin_toss_type, str) else coin_toss_type.value,
                "reason": "rematch_after_draw" if coin_toss_type == CoinTossType.DRAW_DECIDER else "starting_team"
            }
    
    
    # Determine upcoming match based on available teams
    # Only show upcoming match if no coin toss is pending
    upcoming_match = None
    if coin_toss_state and coin_toss_state.get("pending"):
        # Coin toss is pending - do not show upcoming match until coin toss is completed
        upcoming_match = None
    elif scheduled_match:
        # There's a scheduled match - use it
        upcoming_match = {
            "team_a_id": scheduled_match.team_a_id,
            "team_b_id": scheduled_match.team_b_id,
            "team_a_name": team_info.get(scheduled_match.team_a_id, {}).get("name", "Unknown Team"),
            "team_b_name": team_info.get(scheduled_match.team_b_id, {}).get("name", "Unknown Team"),
            "is_knockout_stage": is_knockout_stage,
            "win_condition": "First to 1 goal" if is_knockout_stage else "2-goal lead (min 2 goals)",
            "match_id": scheduled_match.id
        }
    elif current_match and current_match.status == MatchStatus.IN_PROGRESS:
        # Predict next match based on current score and game state
        upcoming_match = _predict_next_match(
            current_match,
            available_teams,
            team_info,
            completed_matches,
            is_knockout_stage
        )
    elif not current_match and len(available_teams) >= 2:
        # No current match, show next two available teams based on rotation
        next_teams = _get_next_teams_for_match(
            db.query(Match).filter(
                and_(
                    Match.game_id == game_id,
                    Match.status == MatchStatus.COMPLETED
                )
            ).order_by(Match.completed_at.desc()).all(),
            available_teams,
            team_info,
            is_knockout_stage
        )
        if next_teams:
            upcoming_match = {
                "team_a_id": next_teams[0]["id"],
                "team_b_id": next_teams[1]["id"],
                "team_a_name": next_teams[0]["name"],
                "team_b_name": next_teams[1]["name"],
                "is_knockout_stage": is_knockout_stage,
                "win_condition": "First to 1 goal" if is_knockout_stage else "2-goal lead (min 2 goals)"
            }
        
    # Get the sport group to check if user is admin
    game = db.query(Game).filter(Game.id == game_id).first()
    sport_group = db.query(SportGroup).filter(SportGroup.id == game.sport_group_id).first()
    membership = db.query(SportGroupMember).filter(
        and_(
            SportGroupMember.sport_group_id == game.sport_group_id,
            SportGroupMember.user_id == current_user.id
        )
    ).first()
    
    # Determine if user can control the match
    can_control_match = False
    referee_info = {"name": "No referee assigned", "team": "", "user_id": None}
    
    if membership:
        # Check if user is admin
        is_admin = (membership.role == MemberRole.ADMIN or 
                   sport_group.creator_id == current_user.id)
        
        can_control_match = is_admin
        
        if is_admin:
            referee_info = {
                "name": "Admin Referee",
                "team": "Administrator",
                "user_id": membership.user_id
            }
            
        return {
        "current_match": {
            "team_a_id": current_match.team_a_id,
            "team_b_id": current_match.team_b_id,
            "team_a_name": team_info.get(current_match.team_a_id, {}).get("name", "Unknown Team"),
            "team_b_name": team_info.get(current_match.team_b_id, {}).get("name", "Unknown Team"),
            "team_a_score": current_match.team_a_score,
            "team_b_score": current_match.team_b_score,
            "started_at": current_match.started_at.isoformat() if current_match.started_at else None,
            "status": current_match.status.value,
            "is_knockout_stage": is_knockout_stage,
            "win_condition": "First to 1 goal" if is_knockout_stage else "2-goal lead (min 2 goals)",
            "match_id": current_match.id
        } if current_match else None,
        "coin_toss_state": coin_toss_state,
        "completed_matches": [
            {
                "team_a_id": match.team_a_id,
                "team_b_id": match.team_b_id,
                "team_a_name": team_info.get(match.team_a_id, {}).get("name", "Unknown Team"),
                "team_b_name": team_info.get(match.team_b_id, {}).get("name", "Unknown Team"),
                "team_a_score": match.team_a_score,
                "team_b_score": match.team_b_score,
                "winner_id": match.winner_id,
                "is_draw": match.is_draw,
                "completed_at": match.completed_at.isoformat() if match.completed_at else None,
                "referee_id": match.referee_id
            }
            for match in completed_matches
        ],
        "teams": [team.id for team in teams_with_players],
        "team_details": team_info,
        "available_teams": available_teams,
        "players": [],
        "can_control_match": can_control_match,
        "referee_info": referee_info,
        "is_knockout_stage": is_knockout_stage,
        "total_teams_with_players": total_teams_with_players,
        "has_active_match": current_match is not None
    }
        
def _create_next_match_after_coin_toss(game_id: str, winner_id: str, loser_id: str, db: Session) -> dict:
            """Create next match after coin toss - winner gets priority in rotation"""
            # Get all teams with players (NO elimination - all teams continue playing)
            all_teams = db.query(GameTeam).filter(GameTeam.game_id == game_id).order_by(GameTeam.team_number).all()
            
            teams_with_players = []
            for team in all_teams:
                # Count registered players
                registered_players = db.query(GamePlayer).filter(
                    and_(GamePlayer.game_id == game_id, GamePlayer.team_id == team.id)
                ).count()
                
                # Count manual participants
                manual_players = db.query(GameDayParticipant).filter(
                    and_(GameDayParticipant.game_id == game_id, GameDayParticipant.team == team.team_number)
                ).count()
                
                if registered_players + manual_players > 0:
                    teams_with_players.append(team)
            
            if len(teams_with_players) < 2:
                return {"message": "Not enough teams with players for next match", "created": False}
            
            # Get completed matches to track team usage
            completed_matches = db.query(Match).filter(
                and_(
                    Match.game_id == game_id,
                    Match.status == MatchStatus.COMPLETED
                )
            ).all()
            
            # Build team statistics - NO elimination tracking since all teams continue
            team_stats = {}
            for team in teams_with_players:
                team_stats[team.id] = {
                    "team": team,
                    "has_played": False,
                    "wins": 0,
                    "losses": 0,
                    "draws": 0
                }
            
            # Track stats for rotation priority (but no elimination)
            for match in completed_matches:
                if match.team_a_id in team_stats:
                    team_stats[match.team_a_id]["has_played"] = True
                if match.team_b_id in team_stats:
                    team_stats[match.team_b_id]["has_played"] = True
                
                if match.is_draw:
                    if match.team_a_id in team_stats:
                        team_stats[match.team_a_id]["draws"] += 1
                    if match.team_b_id in team_stats:
                        team_stats[match.team_b_id]["draws"] += 1
                elif match.winner_id:
                    if match.winner_id in team_stats:
                        team_stats[match.winner_id]["wins"] += 1
                    # Track losses for rotation priority, but don't eliminate
                    loser_id_match = match.team_a_id if match.winner_id == match.team_b_id else match.team_b_id
                    if loser_id_match in team_stats:
                        team_stats[loser_id_match]["losses"] += 1
            
            # Winner of coin toss plays next
            winner_team = team_stats.get(winner_id, {}).get("team")
            if not winner_team:
                return {"message": "Winner team not found", "created": False}
            
            # Find next opponent (exclude only the two teams that just played, not permanently)
            exclude_teams = {winner_id, loser_id}
            available_opponents = _get_next_available_teams_with_players(team_stats, exclude_teams)
            
            if not available_opponents:
                return {"message": "No available opponents", "created": False}
            
            next_opponent = available_opponents[0]
            
            # Create the next match
            new_match = Match(
                id=str(uuid.uuid4()),
                game_id=game_id,
                team_a_id=winner_id,
                team_b_id=next_opponent.id,
                team_a_score=0,
                team_b_score=0,
                status=MatchStatus.SCHEDULED,
                created_at=datetime.now(timezone.utc)
            )
            
            db.add(new_match)
            db.flush()
            
            return {
                "match_id": new_match.id,
                "team_a_id": winner_id,
                "team_b_id": next_opponent.id,
                "team_a_name": winner_team.team_name,
                "team_b_name": next_opponent.team_name,
                "created": True,
                "message": f"Next match: {winner_team.team_name} vs {next_opponent.team_name}"
            }        
        
def _get_next_teams_for_match(completed_matches, available_teams, team_info, is_knockout_stage):
    print(f"DEBUG: Type of completed_matches[0]: {type(completed_matches[0]) if completed_matches else 'No matches'}")
    """Get the next two teams that should play based on rotation priority"""
    if len(available_teams) < 2:
        return None
    
    # Build team statistics
    team_stats = {}
    for team in available_teams:
        team_stats[team["id"]] = {
            "team_data": team,
            "has_played": False,
            "wins": 0,
            "losses": 0,
            "draws": 0
        }
        
     # Analyze completed matches - only count matches that include teams with players
    for match in completed_matches:
        # Only process matches where both teams are in our available teams list
        # FIX: Use object attributes instead of dictionary keys
        team_a_in_available = any(t["id"] == match.team_a_id for t in available_teams)
        team_b_in_available = any(t["id"] == match.team_b_id for t in available_teams)
        
        if team_a_in_available and team_b_in_available:
            if match.team_a_id in team_stats:
                team_stats[match.team_a_id]["has_played"] = True
            if match.team_b_id in team_stats:
                team_stats[match.team_b_id]["has_played"] = True
            
            if match.is_draw:
                if match.team_a_id in team_stats:
                    team_stats[match.team_a_id]["draws"] += 1
                if match.team_b_id in team_stats:
                    team_stats[match.team_b_id]["draws"] += 1
            elif match.winner_id == match.team_a_id and match.team_a_id in team_stats:
                team_stats[match.team_a_id]["wins"] += 1
                if match.team_b_id in team_stats:
                    team_stats[match.team_b_id]["losses"] += 1
            elif match.winner_id == match.team_b_id and match.team_b_id in team_stats:
                team_stats[match.team_b_id]["wins"] += 1
                if match.team_a_id in team_stats:
                    team_stats[match.team_a_id]["losses"] += 1
    
    # # Analyze completed matches
    # for match in completed_matches:
    #     if match.team_a_id in team_stats:
    #         team_stats[match.team_a_id]["has_played"] = True
    #     if match.team_b_id in team_stats:
    #         team_stats[match.team_b_id]["has_played"] = True
        
    #     if match.is_draw:
    #         if match.team_a_id in team_stats:
    #             team_stats[match.team_a_id]["draws"] += 1
    #         if match.team_b_id in team_stats:
    #             team_stats[match.team_b_id]["draws"] += 1
    #     elif match.winner_id == match.team_a_id and match.team_a_id in team_stats:
    #         team_stats[match.team_a_id]["wins"] += 1
    #         if match.team_b_id in team_stats:
    #             team_stats[match.team_b_id]["losses"] += 1
    #     elif match.winner_id == match.team_b_id and match.team_b_id in team_stats:
    #         team_stats[match.team_b_id]["wins"] += 1
    #         if match.team_a_id in team_stats:
    #             team_stats[match.team_a_id]["losses"] += 1
    
    # Get teams by priority: never played > lost > drawn > won
    never_played = []
    lost_teams = []
    drawn_teams = []
    won_teams = []
    
    for team_id, stats in team_stats.items():
        team_data = stats["team_data"]
        
        if not stats["has_played"]:
            never_played.append(team_data)
        elif stats["losses"] > 0 and stats["wins"] == 0:
            lost_teams.append(team_data)
        elif stats["draws"] > 0 and stats["wins"] == 0 and stats["losses"] == 0:
            drawn_teams.append(team_data)
        elif stats["wins"] > 0:
            won_teams.append(team_data)
    
    # Sort each category by team number
    never_played.sort(key=lambda t: t["team_number"])
    lost_teams.sort(key=lambda t: t["team_number"])
    drawn_teams.sort(key=lambda t: t["team_number"])
    won_teams.sort(key=lambda t: t["team_number"])
    
    # Get priority list
    priority_teams = never_played + lost_teams + drawn_teams + won_teams
    
    if len(priority_teams) >= 2:
        return [priority_teams[0], priority_teams[1]]
    
    return None
        
def _predict_next_match(current_match, available_teams, team_info, completed_matches, is_knockout_stage):
    """Predict the next match based on current match state"""
    team_a_score = current_match.team_a_score
    team_b_score = current_match.team_b_score
    score_diff = abs(team_a_score - team_b_score)
    max_score = max(team_a_score, team_b_score)
    
    # Determine if current match could end soon
    match_could_end = False
    potential_winner = None
    
    if is_knockout_stage:
        # Knockout: first to 1 goal
        if team_a_score >= 1 and team_a_score > team_b_score:
            match_could_end = True
            potential_winner = current_match.team_a_id
        elif team_b_score >= 1 and team_b_score > team_a_score:
            match_could_end = True
            potential_winner = current_match.team_b_id
    else:
        # First rotation: 2-goal lead with minimum 2 goals
        if score_diff >= 2 and max_score >= 2:
            match_could_end = True
            potential_winner = current_match.team_a_id if team_a_score > team_b_score else current_match.team_b_id
    
    if match_could_end and potential_winner:
        # Winner stays, find next opponent
        winner_team_info = team_info.get(potential_winner)
        if winner_team_info and available_teams:
            return {
                "team_a_id": potential_winner,
                "team_b_id": available_teams[0]["id"],
                "team_a_name": winner_team_info["name"],
                "team_b_name": available_teams[0]["name"],
                "is_knockout_stage": is_knockout_stage,
                "win_condition": "First to 1 goal" if is_knockout_stage else "2-goal lead (min 2 goals)",
                "prediction": True
            }
    elif team_a_score == team_b_score:
        # Currently tied - if draw, both teams exit
        if len(available_teams) >= 2:
            return {
                "team_a_id": available_teams[0]["id"],
                "team_b_id": available_teams[1]["id"],
                "team_a_name": available_teams[0]["name"],
                "team_b_name": available_teams[1]["name"],
                "is_knockout_stage": is_knockout_stage,
                "win_condition": "First to 1 goal" if is_knockout_stage else "2-goal lead (min 2 goals)",
                "prediction": True,
                "scenario": "if_draw"
            }
    
    return None


@router.get("/{game_id}/suggested-teams")
def get_suggested_teams_for_match(
    game_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get suggested teams for the next match based on rotation logic"""
    # Get game state
    game_state = get_game_state(game_id, current_user, db)
    
    if game_state:
        available_teams = game_state.get("available_teams", [])
        completed_matches = game_state.get("completed_matches", [])
        team_info = game_state.get("team_details", {})
        is_knockout_stage = game_state.get("is_knockout_stage", False)
    else:
        available_teams, completed_matches, team_info, is_knockout_stage = [], [], {}, False
    
    if len(available_teams) < 2:
        return {
            "suggested_teams": [],
            "message": "Not enough available teams"
        }
    
    # Get next teams based on rotation
    next_teams = _get_next_teams_for_match(completed_matches, available_teams, team_info, is_knockout_stage)
    
    if next_teams:
        return {
            "suggested_teams": next_teams,
            "team_a": next_teams[0],
            "team_b": next_teams[1],
            "reason": "Based on rotation priority",
            "is_knockout_stage": is_knockout_stage
        }
    
    return {
        "suggested_teams": available_teams[:2],
        "team_a": available_teams[0],
        "team_b": available_teams[1],
        "reason": "Default selection",
        "is_knockout_stage": is_knockout_stage
    }
    
@router.post("/{game_id}/match/create")
def create_manual_match(
    game_id: UUID,
    match_data: dict = Body(...),  # {team_a_id: str, team_b_id: str}
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new match manually (admin only)"""
    game_id_str = str(game_id)
    game = db.query(Game).filter(Game.id == game_id_str).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Check permissions
    membership = db.query(SportGroupMember).filter(
        and_(
            SportGroupMember.sport_group_id == game.sport_group_id,
            SportGroupMember.user_id == current_user.id
        )
    ).first()
    
    sport_group = db.query(SportGroup).filter(SportGroup.id == game.sport_group_id).first()
    is_admin = (membership and membership.role == MemberRole.ADMIN) or sport_group.creator_id == current_user.id
    
    if not is_admin:
        raise HTTPException(status_code=403, detail="Only admins can create matches")
    
    # Check if there's already an active match
    existing_match = db.query(Match).filter(
        and_(
            Match.game_id == game_id_str,
            Match.status.in_([MatchStatus.IN_PROGRESS, MatchStatus.SCHEDULED])
        )
    ).first()
    
    if existing_match:
        raise HTTPException(status_code=400, detail="There is already an active or scheduled match")
    
    # Validate teams
    team_a_id = match_data.get("team_a_id")
    team_b_id = match_data.get("team_b_id")
    
    if not team_a_id or not team_b_id:
        raise HTTPException(status_code=400, detail="Both team_a_id and team_b_id are required")
    
    team_a = db.query(GameTeam).filter(GameTeam.id == team_a_id).first()
    team_b = db.query(GameTeam).filter(GameTeam.id == team_b_id).first()
    
    if not team_a or not team_b:
        raise HTTPException(status_code=404, detail="One or both teams not found")
    
    # Create new match
    new_match = Match(
        id=str(uuid.uuid4()),
        game_id=game_id_str,
        team_a_id=team_a_id,
        team_b_id=team_b_id,
        team_a_score=0,
        team_b_score=0,
        status=MatchStatus.SCHEDULED,
        created_at=datetime.now(timezone.utc)
    )
    
    db.add(new_match)
    db.commit()
    
    return {
        "message": "Match created successfully",
        "match_id": new_match.id,
        "team_a_id": team_a_id,
        "team_b_id": team_b_id,
        "team_a_name": team_a.team_name,
        "team_b_name": team_b.team_name,
        "status": "scheduled"
    }


# Update the coin toss endpoint to handle the rotation properly
# Update the coin toss endpoint to call the correct function:

def _validate_coin_toss_type(coin_toss_type_str: str) -> CoinTossType:
    """Validate and convert coin_toss_type string to enum"""
    try:
        # Try to match the string to enum values (case-insensitive)
        for enum_member in CoinTossType:
            if enum_member.value.lower() == coin_toss_type_str.lower():
                return enum_member
        # If no match found, raise ValueError
        raise ValueError(f"Invalid coin toss type: {coin_toss_type_str}")
    except ValueError:
        valid_types = [e.value for e in CoinTossType]
        raise HTTPException(
            status_code=400,
            detail=f"Invalid coin toss type '{coin_toss_type_str}'. Valid types are: {', '.join(valid_types)}"
        )


@router.post("/{game_id}/coin-toss")
def coin_toss(
    game_id: UUID,
    data: dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Perform a coin toss for a draw or starting team determination"""
    game = db.query(Game).filter(Game.id == str(game_id)).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    # Check permissions
    membership = db.query(SportGroupMember).filter(
        and_(
            SportGroupMember.sport_group_id == game.sport_group_id,
            SportGroupMember.user_id == current_user.id,
            SportGroupMember.is_approved == True
        )
    ).first()

    sport_group = db.query(SportGroup).filter(SportGroup.id == game.sport_group_id).first()
    is_admin = (membership and membership.role == MemberRole.ADMIN) or sport_group.creator_id == current_user.id

    if not is_admin:
        raise ForbiddenException("Only admin can perform coin toss")

    # Validate that both teams made choices
    team_a_choice = data.get("team_a_choice")
    team_b_choice = data.get("team_b_choice")

    if not team_a_choice or not team_b_choice:
        raise HTTPException(status_code=400, detail="Both teams must choose heads or tails")

    if team_a_choice == team_b_choice:
        raise HTTPException(status_code=400, detail="Teams cannot choose the same side")

    # Simulate coin toss
    result = random.choice(["heads", "tails"])

    # Determine winner and loser
    if team_a_choice == result:
        coin_toss_winner_id = data["team_a_id"]
        coin_toss_loser_id = data["team_b_id"]
    else:
        coin_toss_winner_id = data["team_b_id"]
        coin_toss_loser_id = data["team_a_id"]

    # Get team names for response
    winner_team = db.query(GameTeam).filter(GameTeam.id == coin_toss_winner_id).first()
    loser_team = db.query(GameTeam).filter(GameTeam.id == coin_toss_loser_id).first()

    # Validate and convert coin toss type to enum
    coin_toss_type_str = data.get("coin_toss_type", "draw_decider")
    coin_toss_type = _validate_coin_toss_type(coin_toss_type_str)

    if coin_toss_type == CoinTossType.DRAW_DECIDER:
        # For draw decider: winner gets priority in rotation
        next_match_result = _create_next_match_after_coin_toss(
            str(game_id),
            coin_toss_winner_id,
            coin_toss_loser_id,
            db
        )
        message = f"Coin landed on {result}! {winner_team.team_name if winner_team else 'Winner'} gets priority in next rotation."
    elif coin_toss_type == CoinTossType.STARTING_TEAM:
        # For starting team: winner starts the match
        # Find the match that requires this coin toss
        pending_match = db.query(Match).filter(
            and_(
                Match.game_id == str(game_id),
                Match.requires_coin_toss == True,
                Match.coin_toss_type == CoinTossType.STARTING_TEAM,
                or_(
                    and_(Match.team_a_id == data["team_a_id"], Match.team_b_id == data["team_b_id"]),
                    and_(Match.team_a_id == data["team_b_id"], Match.team_b_id == data["team_a_id"])
                )
            )
        ).first()

        if pending_match:
            # Update the match with coin toss results
            pending_match.coin_toss_result = result
            pending_match.coin_toss_winner_id = coin_toss_winner_id
            pending_match.requires_coin_toss = False

            # Set the winner as team_a for starting purposes
            if coin_toss_winner_id != pending_match.team_a_id:
                # Swap teams so winner starts
                temp = pending_match.team_a_id
                pending_match.team_a_id = pending_match.team_b_id
                pending_match.team_b_id = temp

        next_match_result = {"created": False, "message": "Coin toss completed for starting team"}
        message = f"Coin landed on {result}! {winner_team.team_name if winner_team else 'Winner'} starts the match."
    else:
        # This should never happen due to validation, but just in case
        raise HTTPException(status_code=400, detail=f"Unsupported coin toss type: {coin_toss_type}")

    # Clear coin toss state after processing is complete
    game.coin_toss_state = None

    db.commit()

    return {
        "result": result,
        "winner_id": coin_toss_winner_id,
        "loser_id": coin_toss_loser_id,
        "winner_name": winner_team.team_name if winner_team else "Unknown",
        "loser_name": loser_team.team_name if loser_team else "Unknown",
        "coin_result": result,
        "coin_toss_type": coin_toss_type.value,
        "message": message,
        "next_match": next_match_result if next_match_result.get("created") else None
    }
@router.post("/{game_id}/referee")
def assign_referee(
    game_id: UUID,
    data: dict = Body(...),  # {referee_id: int}
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Assign a referee for the current or upcoming match (admin only)."""
    game = db.query(Game).filter(Game.id == str(game_id)).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    membership = db.query(SportGroupMember).filter(
        and_(
            SportGroupMember.sport_group_id == game.sport_group_id,
            SportGroupMember.user_id == current_user.id,
            SportGroupMember.is_approved == True
        )
    ).first()
    if not membership or membership.role != MemberRole.ADMIN:
        raise ForbiddenException("Only admin can assign referee")
    game.referee_id = data["referee_id"]
    db.commit()
    return {"referee_id": game.referee_id}

# Update POST /{game_id}/score to handle winner/draw/next match/referee
@router.post("/{game_id}/score")
def update_team_score(
    game_id: UUID,
    score_update: GameScoreUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update team score (referee or admin only). After score submission, determine winner/draw, update next match and referee. If draw, require coin toss before next match is set."""
    game = db.query(Game).filter(Game.id == str(game_id)).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
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
        and_(GameTeam.id == score_update.team_id, GameTeam.game_id == str(game_id))
    ).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Update score
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
    
    # --- Winner/Draw/Next Match Logic ---
    # Get all teams for this game
    all_teams = db.query(GameTeam).filter(GameTeam.game_id == str(game_id)).all()
    
    # Check if we have a current match
    current_match = getattr(game, "current_match", None)
    if not current_match:
        # No current match, nothing to process
        return {"message": "Score updated successfully", "team_score": team.score}
    
    # Get the two teams in the current match
    team_a_id = current_match.get("team_a_id")
    team_b_id = current_match.get("team_b_id")
    
    if not team_a_id or not team_b_id:
        return {"message": "Score updated successfully", "team_score": team.score}
    
    team_a = db.query(GameTeam).filter(GameTeam.id == team_a_id).first()
    team_b = db.query(GameTeam).filter(GameTeam.id == team_b_id).first()
    
    if not team_a or not team_b:
        return {"message": "Score updated successfully", "team_score": team.score}
    
    # Determine match outcome
    team_a_score = team_a.score
    team_b_score = team_b.score
    
    # Check if match is complete (both teams have played)
    # For now, assume match is complete when both teams have scores
    # You might want to add a match status field to track this more precisely
    
    if team_a_score > team_b_score:
        # Team A wins
        winner_id = team_a_id
        loser_id = team_b_id
        is_draw = False
    elif team_b_score > team_a_score:
        # Team B wins
        winner_id = team_b_id
        loser_id = team_a_id
        is_draw = False
    else:
        # Draw
        winner_id = None
        loser_id = None
        is_draw = True
    
    # Update completed matches
    completed_matches = getattr(game, "completed_matches", [])
    match_result = {
        "team_a_id": team_a_id,
        "team_b_id": team_b_id,
        "team_a_score": team_a_score,
        "team_b_score": team_b_score,
        "winner_id": winner_id,
        "is_draw": is_draw,
        "referee_id": game.referee_id,
        "completed_at": datetime.utcnow().isoformat()
    }
    completed_matches.append(match_result)
    game.completed_matches = completed_matches
    
    # Clear current match
    game.current_match = None
    
    # Set upcoming match based on outcome
    if is_draw:
        # Draw - require coin toss before setting next match
        game.coin_toss_state = {
            "team_a_id": team_a_id,
            "team_b_id": team_b_id,
            "pending": True,
            "timestamp": datetime.utcnow().isoformat()
        }
        game.upcoming_match = None
    else:
        # Winner stays, loser leaves
        # Find next available team to play against winner
        next_opponent = _find_next_opponent(str(game_id), winner_id, completed_matches, db)
        if next_opponent:
            game.upcoming_match = {
                "team_a_id": winner_id,
                "team_b_id": next_opponent,
                "created_at": datetime.utcnow().isoformat()
            }
            # Auto-assign referee from non-playing teams
            new_referee_id = _assign_referee_from_non_playing_teams(
                str(game_id), winner_id, next_opponent, db
            )
            if new_referee_id:
                game.referee_id = new_referee_id
        else:
            # No more teams to play
            game.upcoming_match = None
    
    db.commit()
    
    return {
        "message": "Score updated successfully", 
        "team_score": team.score,
        "match_completed": True,
        "is_draw": is_draw,
        "winner_id": winner_id,
        "requires_coin_toss": is_draw
    }
    
@router.post("/{game_id}/match/start-scheduled")
def start_scheduled_match(
    game_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a scheduled match"""
    game_id_str = str(game_id)
    game = db.query(Game).filter(Game.id == game_id_str).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Get scheduled match
    scheduled_match = db.query(Match).filter(
        and_(
            Match.game_id == game_id_str,
            Match.status == MatchStatus.SCHEDULED
        )
    ).first()
    
    if not scheduled_match:
        raise HTTPException(status_code=404, detail="No scheduled match found")

    # Check if this match requires a coin toss before it can start
    if scheduled_match.requires_coin_toss:
        raise HTTPException(
            status_code=400,
            detail="This match requires a coin toss before it can start. Teams that previously drew must perform a coin toss to determine play order."
        )

    # Check permissions
    membership = db.query(SportGroupMember).filter(
        and_(
            SportGroupMember.sport_group_id == game.sport_group_id,
            SportGroupMember.user_id == current_user.id
        )
    ).first()

    sport_group = db.query(SportGroup).filter(SportGroup.id == game.sport_group_id).first()
    is_admin = (membership and membership.role == MemberRole.ADMIN) or sport_group.creator_id == current_user.id

    if not is_admin:
        raise HTTPException(status_code=403, detail="Only admins can start matches")
    
    # Start the match
    scheduled_match.status = MatchStatus.IN_PROGRESS
    scheduled_match.started_at = datetime.now(timezone.utc)
    
    # Reset and start game timer
    game.timer_started_at = datetime.now(timezone.utc)
    game.timer_remaining_seconds = 420
    game.timer_is_running = True
    game.status = GameStatus.IN_PROGRESS
    
    db.commit()
    
    return {
        "message": "Match started successfully",
        "match_id": scheduled_match.id,
        "team_a_id": scheduled_match.team_a_id,
        "team_b_id": scheduled_match.team_b_id
    }


@router.post("/{game_id}/match/score")
def update_match_score(
    game_id: UUID,
    score_update: GameScoreUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update match score directly and handle win conditions"""
    game_id_str = str(game_id)
    game = db.query(Game).filter(Game.id == game_id_str).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Get current match
    current_match = db.query(Match).filter(
        and_(
            Match.game_id == game_id_str,
            Match.status == MatchStatus.IN_PROGRESS
        )
    ).first()
    
    if not current_match:
        raise HTTPException(status_code=404, detail="No active match found")
    
    # Check permissions
    membership = db.query(SportGroupMember).filter(
        and_(
            SportGroupMember.sport_group_id == game.sport_group_id,
            SportGroupMember.user_id == current_user.id
        )
    ).first()
    
    # Check if user can control match (admin or referee)
    sport_group = db.query(SportGroup).filter(SportGroup.id == game.sport_group_id).first()
    is_admin = (membership and membership.role == MemberRole.ADMIN) or sport_group.creator_id == current_user.id
    
    if not is_admin:
        raise HTTPException(status_code=403, detail="Only admins can update scores")
    
    # Update the correct team score in the match
    if score_update.team_id == current_match.team_a_id:
        if score_update.action == "increment":
            current_match.team_a_score += 1
        elif score_update.action == "decrement":
            current_match.team_a_score = max(0, current_match.team_a_score - 1)
        elif score_update.action == "set" and score_update.value is not None:
            current_match.team_a_score = score_update.value
        new_score = current_match.team_a_score
    elif score_update.team_id == current_match.team_b_id:
        if score_update.action == "increment":
            current_match.team_b_score += 1
        elif score_update.action == "decrement":
            current_match.team_b_score = max(0, current_match.team_b_score - 1)
        elif score_update.action == "set" and score_update.value is not None:
            current_match.team_b_score = score_update.value
        new_score = current_match.team_b_score
    else:
        raise HTTPException(status_code=400, detail="Team not in current match")
    
    # Determine if we're in knockout stage
    all_teams = db.query(GameTeam).filter(GameTeam.game_id == game_id_str).all()
    
    # Count teams with players
    teams_with_players = []
    for team in all_teams:
        registered_players = db.query(GamePlayer).filter(
            and_(GamePlayer.game_id == game_id_str, GamePlayer.team_id == team.id)
        ).count()
        manual_players = db.query(GameDayParticipant).filter(
            and_(GameDayParticipant.game_id == game_id_str, GameDayParticipant.team == team.team_number)
        ).count()
        
        if registered_players + manual_players > 0:
            teams_with_players.append(team)
    
    total_teams_with_players = len(teams_with_players)
    
    # Get completed matches to see which teams have played
    completed_matches = db.query(Match).filter(
        and_(
            Match.game_id == game_id_str,
            Match.status == MatchStatus.COMPLETED
        )
    ).all()
    
    teams_that_played = set()
    for match in completed_matches:
        teams_that_played.add(match.team_a_id)
        teams_that_played.add(match.team_b_id)
    
    # Determine if we're in knockout stage (all teams have played at least once)
    is_knockout_stage = len(teams_that_played) >= total_teams_with_players and total_teams_with_players > 0
    
    # Check win conditions based on stage
    match_ended = False
    next_match_info = None
    
    if is_knockout_stage:
        # Knockout stage: first to 1 goal wins
        if current_match.team_a_score >= 1 and current_match.team_a_score > current_match.team_b_score:
            match_ended = True
            current_match.winner_id = current_match.team_a_id
            current_match.is_draw = False
        elif current_match.team_b_score >= 1 and current_match.team_b_score > current_match.team_a_score:
            match_ended = True
            current_match.winner_id = current_match.team_b_id
            current_match.is_draw = False
    else:
        # First rotation: 2-goal lead wins (minimum 2 goals)
        score_diff = abs(current_match.team_a_score - current_match.team_b_score)
        max_score = max(current_match.team_a_score, current_match.team_b_score)
        
        if score_diff >= 2 and max_score >= 2:
            match_ended = True
            if current_match.team_a_score > current_match.team_b_score:
                current_match.winner_id = current_match.team_a_id
            else:
                current_match.winner_id = current_match.team_b_id
            current_match.is_draw = False
    
    if match_ended:
        # Complete the current match
        current_match.status = MatchStatus.COMPLETED
        current_match.completed_at = datetime.now(timezone.utc)
        
        # Reset game timer
        game.timer_is_running = False
        game.timer_started_at = None
        game.timer_remaining_seconds = 420
        
        # Create next match based on outcome
        next_match_info = _create_next_match_with_rotation(
            game_id_str, 
            current_match, 
            winner_id=current_match.winner_id if current_match.winner_id else "unknown",  # Use match winner
            loser_id=loser_id if 'loser_id' in locals() else "unknown",  # Ensure loser_id is defined
            db=db
        )
    
    db.commit()
    
    stage_info = "Knockout Stage (First to 1 goal)" if is_knockout_stage else "First Rotation (2-goal lead/minimum)"
    
    
    return {
        "message": "Score updated successfully",
        "team_score": new_score,
        "team_a_score": current_match.team_a_score,
        "team_b_score": current_match.team_b_score,
        "match_ended": match_ended,
        "winner_id": current_match.winner_id if match_ended else None,
        "next_match": next_match_info if match_ended else None,
        "timer_reset": match_ended,
        "stage": stage_info,
        "is_knockout_stage": is_knockout_stage
    }
    

def _create_next_match_with_rotation(game_id: str, completed_match: Match, winner_id: str, loser_id: str, db: Session) -> dict:
    """Create the next match based on rotation rules and available teams with players"""
    # Get all teams with players
    all_teams = db.query(GameTeam).filter(GameTeam.game_id == game_id).order_by(GameTeam.team_number).all()
    
    teams_with_players = []
    for team in all_teams:
        # Count registered players
        registered_players = db.query(GamePlayer).filter(
            and_(GamePlayer.game_id == game_id, GamePlayer.team_id == team.id)
        ).count()
        
        # Count manual participants
        manual_players = db.query(GameDayParticipant).filter(
            and_(GameDayParticipant.game_id == game_id, GameDayParticipant.team == team.team_number)
        ).count()
        
        if registered_players + manual_players > 0:
            teams_with_players.append(team)
    
    if len(teams_with_players) < 2:
        return {"message": "Not enough teams with players for next match", "created": False}
    
    # Get all completed matches to track team usage
    completed_matches = db.query(Match).filter(
        and_(
            Match.game_id == game_id,
            Match.status == MatchStatus.COMPLETED
        )
    ).all()
    
    # Build team statistics for teams with players only
    team_stats = {}
    for team in teams_with_players:
        team_stats[team.id] = {
            "team": team,
            "has_played": False,
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "is_currently_playing": False
        }
        
    # Analyze completed matches
    for match in completed_matches:
        if match.team_a_id in team_stats:
            team_stats[match.team_a_id]["has_played"] = True
        if match.team_b_id in team_stats:
            team_stats[match.team_b_id]["has_played"] = True
        
        if match.is_draw:
            if match.team_a_id in team_stats:
                team_stats[match.team_a_id]["draws"] += 1
            if match.team_b_id in team_stats:
                team_stats[match.team_b_id]["draws"] += 1
        elif match.winner_id == match.team_a_id and match.team_a_id in team_stats:
            team_stats[match.team_a_id]["wins"] += 1
            if match.team_b_id in team_stats:
                team_stats[match.team_b_id]["losses"] += 1
        elif match.winner_id == match.team_b_id and match.team_b_id in team_stats:
            team_stats[match.team_b_id]["wins"] += 1
            if match.team_a_id in team_stats:
                team_stats[match.team_a_id]["losses"] += 1
    
    next_team_a = None
    next_team_b = None
    
    # Handle different match outcomes
    if completed_match.is_draw:
        # Determine draw state using unified function
        # We need to determine if we're in knockout stage
        # For this function, we'll check based on team stats (if all teams have played, we're in knockout)
        total_teams = len(team_stats)
        teams_that_played = sum(1 for stats in team_stats.values() if stats["has_played"])
        is_knockout_stage = teams_that_played >= total_teams

        draw_state = _determine_draw_state(completed_match, is_knockout_stage, db)

        if draw_state["requires_coin_toss"]:
            # Coin toss needed for this draw
            return {
                "message": draw_state["purpose"],
                "requires_coin_toss": True,
                "team_a_id": completed_match.team_a_id,
                "team_b_id": completed_match.team_b_id,
                "created": False
            }
        elif draw_state["draw_type"] == "0-0":
            # 0-0 draw: both teams out, next two available teams play
            available_teams = _get_next_available_teams_with_players(team_stats, exclude_teams=set())
            if len(available_teams) >= 2:
                next_team_a = available_teams[0]
                next_team_b = available_teams[1]
        # For draws with goals in knockout stage, both teams continue - handled by the normal winner/loser logic below
    elif winner_id and winner_id in team_stats:
        # Winner stays, find next opponent based on priority
        winner_team = team_stats[winner_id]["team"]
        next_team_a = winner_team
        
        # Get next opponent based on rotation priority
        exclude_teams = {winner_id, completed_match.team_a_id, completed_match.team_b_id}
        available_opponents = _get_next_available_teams_with_players(team_stats, exclude_teams)
        
        if available_opponents:
            next_team_b = available_opponents[0]
    
    # Create the next match if we have teams
    if next_team_a and next_team_b:
        # Check if this match pairing requires a coin toss (rematch between previously drawn teams)
        requires_coin_toss = _check_if_match_requires_coin_toss(
            game_id, next_team_a.id, next_team_b.id, db
        )

        new_match = Match(
            id=str(uuid.uuid4()),
            game_id=game_id,
            team_a_id=next_team_a.id,
            team_b_id=next_team_b.id,
            team_a_score=0,
            team_b_score=0,
            status=MatchStatus.SCHEDULED,
            requires_coin_toss=requires_coin_toss,
            coin_toss_type=CoinTossType.DRAW_DECIDER.value if requires_coin_toss else None,
            created_at=datetime.now(timezone.utc)
        )
        db.add(new_match)
        db.flush()

        return {
            "match_id": new_match.id,
            "team_a_id": next_team_a.id,
            "team_b_id": next_team_b.id,
            "team_a_name": next_team_a.team_name,
            "team_b_name": next_team_b.team_name,
            "created": True,
            "requires_coin_toss": requires_coin_toss
        }
    
    return {"message": "No more matches possible", "created": False}


def _determine_draw_state(current_match: Match, is_knockout_stage: bool, db: Session) -> dict:
    """
    Determine the draw state for a match.
    Args:
        current_match (Match): The match object.
        is_knockout_stage (bool): Whether the match is in the knockout stage.
        db (Session): The database session.

    Returns:
        dict: A dictionary containing the draw state.
    """
    if not current_match or not isinstance(current_match, Match):
        raise ValueError("Invalid match object provided.")

    if current_match.team_a_score is None or current_match.team_b_score is None:
        raise ValueError("Match scores must be defined.")

    team_a_score = current_match.team_a_score
    team_b_score = current_match.team_b_score

    if team_a_score == 0 and team_b_score == 0:
        # 0-0 draw: Coin toss required to determine play order
        return {
            "requires_coin_toss": True,
            "coin_toss_type": CoinTossType.STARTING_TEAM,
            "draw_type": "0-0",
            "purpose": "0-0 draw - coin toss to determine who plays first in next rotation"
        }
    elif is_knockout_stage and team_a_score == team_b_score:
        # Draw with goals in knockout stage: No coin toss needed
        return {
            "requires_coin_toss": False,
            "coin_toss_type": None,
            "draw_type": "with_goals",
            "purpose": "Draw with goals in knockout stage - both teams continue in rotation"
        }
    elif team_a_score == team_b_score:
        # Draw with goals in first rotation: Coin toss required
        return {
            "requires_coin_toss": True,
            "coin_toss_type": CoinTossType.DRAW_DECIDER,
            "draw_type": "with_goals",
            "purpose": "Draw with goals - coin toss to determine who gets priority in next rotation"
        }
    else:
        raise ValueError("Unexpected match state encountered.")
    print(f"DEBUG: Evaluating draw state for match {current_match.id}")
    print(f"DEBUG: Scores - Team A: {current_match.team_a_score}, Team B: {current_match.team_b_score}")
    print(f"DEBUG: Knockout stage: {is_knockout_stage}")
    """
    Unified function to determine draw state and coin toss requirements.

    Returns:
        {
            "requires_coin_toss": bool,
            "coin_toss_type": CoinTossType or None,
            "draw_type": "0-0" or "with_goals",
            "purpose": str describing the purpose
        }
    """
    game_id = current_match.game_id
    team_a_id = current_match.team_a_id
    team_b_id = current_match.team_b_id
    team_a_score = current_match.team_a_score
    team_b_score = current_match.team_b_score

    # Determine draw type
    draw_type = "0-0" if (team_a_score == 0 and team_b_score == 0) else "with_goals"

    # Check if this is a rematch between previously drawn teams
    previous_draws = db.query(Match).filter(
        and_(
            Match.game_id == game_id,
            Match.is_draw == True,
            or_(
                and_(Match.team_a_id == team_a_id, Match.team_b_id == team_b_id),
                and_(Match.team_a_id == team_b_id, Match.team_b_id == team_a_id)
            )
        )
    ).all()

    if previous_draws:
        # Rematch between teams that previously drew - coin toss required
        return {
            "requires_coin_toss": True,
            "coin_toss_type": CoinTossType.DRAW_DECIDER,
            "draw_type": draw_type,
            "purpose": "Rematch after previous draw - coin toss to determine who gets priority in next rotation"
        }
    elif team_a_score == 0 and team_b_score == 0:
        # 0-0 draw: Coin toss required to determine play order
        print("DEBUG: Handling 0-0 draw scenario.")
        return {
            "requires_coin_toss": True,
            "coin_toss_type": CoinTossType.STARTING_TEAM,
            "draw_type": "0-0",
            "purpose": "0-0 draw - coin toss to determine who plays first in next rotation"
        }
    elif is_knockout_stage and draw_type == "with_goals":
        # Draw with goals in knockout stage: No coin toss needed
        print("DEBUG: Handling draw with goals in knockout stage.")
        return {
            "requires_coin_toss": False,
            "coin_toss_type": None,
            "draw_type": "with_goals",
            "purpose": "Draw with goals in knockout stage - both teams continue in rotation"
        }
    elif draw_type == "with_goals":
        # Draw with goals in first rotation: Coin toss required
        print("DEBUG: Handling draw with goals in first rotation.")
        return {
            "requires_coin_toss": True,
            "coin_toss_type": CoinTossType.DRAW_DECIDER,
            "draw_type": "with_goals",
            "purpose": "Draw with goals - coin toss to determine who gets priority in next rotation"
        }


def _check_if_match_requires_coin_toss(game_id: str, team_a_id: str, team_b_id: str, db: Session) -> bool:
    """Check if a match between two teams requires a coin toss (rematch after draw)"""
    # Check if these two teams have previously drawn against each other
    previous_draws = db.query(Match).filter(
        and_(
            Match.game_id == game_id,
            Match.is_draw == True,
            or_(
                and_(Match.team_a_id == team_a_id, Match.team_b_id == team_b_id),
                and_(Match.team_a_id == team_b_id, Match.team_b_id == team_a_id)
            )
        )
    ).all()

    return len(previous_draws) > 0


def _get_next_available_teams_with_players(team_stats: dict, exclude_teams: set) -> list:
    """
    Get next available teams that have players based on rotation priority:
    1. Teams that have never played (by team number order)
    2. Teams that have lost (by team number order) 
    3. Teams that have drawn (by team number order)
    4. Teams that have won (by team number order)
    
    NOTE: In knockout stage, teams are NOT eliminated - they continue in rotation.
    Knockout stage only changes the win condition to "first to 1 goal".
    """
    # Separate teams by status for rotation priority
    never_played = []
    lost_teams = []
    drawn_teams = []
    won_teams = []
    
    for team_id, stats in team_stats.items():
        if team_id in exclude_teams:
            continue
            
        team = stats["team"]
        
        if not stats["has_played"]:
            never_played.append(team)
        elif stats["losses"] > 0 and stats["wins"] == 0:
            # Teams that have only lost (no wins) - higher priority for next match
            lost_teams.append(team)
        elif stats["draws"] > 0 and stats["wins"] == 0 and stats["losses"] == 0:
            # Teams that have only drawn
            drawn_teams.append(team)
        elif stats["wins"] > 0:
            # Teams that have won at least once - lower priority
            won_teams.append(team)
    
    # Sort each category by team number for consistent ordering
    never_played.sort(key=lambda t: t.team_number)
    lost_teams.sort(key=lambda t: t.team_number)
    drawn_teams.sort(key=lambda t: t.team_number)
    won_teams.sort(key=lambda t: t.team_number)
    
    # Return in rotation priority order (not elimination order)
    return never_played + lost_teams + drawn_teams + won_teams

# Update the match end handler to properly detect draws that need coin toss
@router.post("/{game_id}/match/end")
def end_current_match(
    game_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """End current match and determine next match based on rotation rules"""
    game_id_str = str(game_id)
    game = db.query(Game).filter(Game.id == game_id_str).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Get current match
    current_match = db.query(Match).filter(
        and_(
            Match.game_id == game_id_str,
            Match.status == MatchStatus.IN_PROGRESS
        )
    ).first()
    
    if not current_match:
        raise HTTPException(status_code=404, detail="No active match found")
    
    # Check if we're in knockout stage first
    all_teams = db.query(GameTeam).filter(GameTeam.game_id == game_id_str).all()
    teams_with_players = []
    for team in all_teams:
        registered_players = db.query(GamePlayer).filter(
            and_(GamePlayer.game_id == game_id_str, GamePlayer.team_id == team.id)
        ).count()
        manual_players = db.query(GameDayParticipant).filter(
            and_(GameDayParticipant.game_id == game_id_str, GameDayParticipant.team == team.team_number)
        ).count()
        if registered_players + manual_players > 0:
            teams_with_players.append(team)
    
    completed_matches = db.query(Match).filter(
        and_(
            Match.game_id == game_id_str,
            Match.status == MatchStatus.COMPLETED
        )
    ).all()
    
    teams_that_played = set()
    for match in completed_matches:
        teams_that_played.add(match.team_a_id)
        teams_that_played.add(match.team_b_id)
    
    is_knockout_stage = len(teams_that_played) >= len(teams_with_players) and len(teams_with_players) > 0
    
    
    # Complete the current match
    current_match.status = MatchStatus.COMPLETED
    current_match.completed_at = datetime.now(timezone.utc)
    
    winner_team_id = None
    loser_team_id = None
    requires_coin_toss = False

    # Determine winner or draw
    if current_match.team_a_score > current_match.team_b_score:
        current_match.winner_id = current_match.team_a_id
        current_match.is_draw = False
        winner_team_id = current_match.team_a_id
        loser_team_id = current_match.team_b_id
    elif current_match.team_b_score > current_match.team_a_score:
        current_match.winner_id = current_match.team_b_id
        current_match.is_draw = False
        winner_team_id = current_match.team_b_id
        loser_team_id = current_match.team_a_id
    else:
        # Draw - both teams return to rotation
        current_match.is_draw = True
        current_match.winner_id = None

        # Determine draw state using unified function
        draw_state = _determine_draw_state(current_match, is_knockout_stage, db)
        requires_coin_toss = draw_state["requires_coin_toss"]

        if requires_coin_toss:
            current_match.requires_coin_toss = True
            current_match.coin_toss_type = draw_state["coin_toss_type"].value
    
    # Reset game timer
    game.timer_is_running = False
    game.timer_started_at = None
    game.timer_remaining_seconds = 420
    
    next_match_info = None
    
    if requires_coin_toss:
        # Store coin toss state for frontend to handle
        game.coin_toss_state = {
            "pending": True,
            "team_a_id": current_match.team_a_id,
            "team_b_id": current_match.team_b_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "stage": "knockout_stage" if is_knockout_stage else "first_rotation",
            "draw_type": draw_state["draw_type"],
            "purpose": draw_state["purpose"]
       }
        
        team_a = db.query(GameTeam).filter(GameTeam.id == current_match.team_a_id).first()
        team_b = db.query(GameTeam).filter(GameTeam.id == current_match.team_b_id).first()
        
        next_match_info = {
                "requires_coin_toss": True,
                "team_a_id": current_match.team_a_id,
                "team_b_id": current_match.team_b_id,
                "team_a_name": team_a.team_name if team_a else "Unknown",
                "team_b_name": team_b.team_name if team_b else "Unknown",
                "message": draw_state["purpose"],
                "stage": "knockout_stage" if is_knockout_stage else "first_rotation",
                "draw_type": draw_state["draw_type"]
            }
    else:
        # Create next match based on outcome

            # Normal winner/loser scenario
            next_match_info = _create_next_match_with_rotation(
                game_id_str, 
                current_match, 
                winner_team_id or "unknown_winner",
                loser_team_id or "unknown_loser",
                db
            )    
    db.commit()
    
    stage_info = "Knockout Stage (First to 1 goal)" if is_knockout_stage else "First Rotation (2-goal lead/minimum)"
    draw_info = ""
    if current_match.is_draw:
        if current_match.team_a_score == 0 and current_match.team_b_score == 0:
            draw_info = " - 0-0 draw: Coin toss for next rotation priority"
        elif is_knockout_stage:
            draw_info = " - Draw with goals: Coin toss for next rotation priority"
        else:
            draw_info = " - Draw with goals: Coin toss for next rotation priority"
    
    return {
        "message": "Match ended",
        "match_result": {
            "winner_id": current_match.winner_id,
            "is_draw": current_match.is_draw,
            "team_a_score": current_match.team_a_score,
            "team_b_score": current_match.team_b_score,
            "requires_coin_toss": requires_coin_toss,
            "stage": stage_info + draw_info,
            "draw_type": draw_state["draw_type"] if current_match.is_draw else None
        },
        "next_match": next_match_info,
        "timer_reset": True,
        "is_knockout_stage": is_knockout_stage
    }
    
    
def _create_next_match(game_id: str, completed_match: Match, winner_id: str, loser_id: str, db: Session) -> dict:
    """Create the next match based on rotation rules and return match info"""
    # Get all teams for this game ordered by team number
    all_teams = db.query(GameTeam).filter(GameTeam.game_id == game_id).order_by(GameTeam.team_number).all()
    
    if len(all_teams) < 3:
        return {"message": "Not enough teams for rotation"}
    
    # Get all completed matches to track team usage
    completed_matches = db.query(Match).filter(
        and_(
            Match.game_id == game_id,
            Match.status == MatchStatus.COMPLETED
        )
    ).all()
    
    # Track team statistics
    team_stats = {}
    for team in all_teams:
        team_stats[team.id] = {
            "team": team,
            "has_played": False,
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "is_currently_playing": False
        }
        
    # Analyze completed matches
    for match in completed_matches:
        # Mark teams as having played
        team_stats[match.team_a_id]["has_played"] = True
        team_stats[match.team_b_id]["has_played"] = True
        
        if match.is_draw:
            team_stats[match.team_a_id]["draws"] += 1
            team_stats[match.team_b_id]["draws"] += 1
        elif match.winner_id == match.team_a_id:
            team_stats[match.team_a_id]["wins"] += 1
            team_stats[match.team_b_id]["losses"] += 1
        elif match.winner_id == match.team_b_id:
            team_stats[match.team_b_id]["wins"] += 1
            team_stats[match.team_a_id]["losses"] += 1
    
    # Mark currently playing teams
    if completed_match:
        team_stats[completed_match.team_a_id]["is_currently_playing"] = True
        team_stats[completed_match.team_b_id]["is_currently_playing"] = True
    
    next_team_a = None
    next_team_b = None
    
    # Handle different match outcomes
    if completed_match.is_draw and completed_match.team_a_score == 0 and completed_match.team_b_score == 0:
        # 0-0 draw: both teams out, next two available teams play
        available_teams = _get_next_available_teams(team_stats, exclude_teams=set())
        if len(available_teams) >= 2:
            next_team_a = available_teams[0]
            next_team_b = available_teams[1]
    elif completed_match.is_draw:
        # Draw with goals: coin toss needed - this should be handled separately
        return {
            "message": "Coin toss required for draw",
            "requires_coin_toss": True,
            "team_a_id": completed_match.team_a_id,
            "team_b_id": completed_match.team_b_id,
            "created": False
        }
    elif winner_id:
        # Winner stays, find next opponent based on priority
        winner_team = team_stats[winner_id]["team"]
        next_team_a = winner_team
        
        # Get next opponent based on rotation priority
        exclude_teams = {winner_id}  # Exclude the winner
        available_opponents = _get_next_available_teams(team_stats, exclude_teams)
        
        if available_opponents:
            next_team_b = available_opponents[0]
    
    # Create the next match if we have teams
    if next_team_a and next_team_b:
        new_match = Match(
            id=str(uuid.uuid4()),
            game_id=game_id,
            team_a_id=next_team_a.id,
            team_b_id=next_team_b.id,
            team_a_score=0,
            team_b_score=0,
            status=MatchStatus.SCHEDULED,
            created_at=datetime.now(timezone.utc)
        )
        db.add(new_match)
        db.flush()
        
        return {
            "match_id": new_match.id,
            "team_a_id": next_team_a.id,
            "team_b_id": next_team_b.id,
            "team_a_name": next_team_a.team_name,
            "team_b_name": next_team_b.team_name,
            "created": True
        }
    
    return {"message": "No more matches possible", "created": False}

def _get_next_available_teams(team_stats: dict, exclude_teams: set) -> list:
    """
    Get next available teams based on priority:
    1. Teams that have never played (by team number order)
    2. Teams that have lost (by team number order)
    3. Teams that have drawn (by team number order)
    4. Teams that have won (by team number order)
    """
    # Separate teams by status
    never_played = []
    lost_teams = []
    drawn_teams = []
    won_teams = []
    
    for team_id, stats in team_stats.items():
        if team_id in exclude_teams or stats["is_currently_playing"]:
            continue
            
        team = stats["team"]
        
        if not stats["has_played"]:
            never_played.append(team)
        elif stats["losses"] > 0 and stats["wins"] == 0:
            # Teams that have only lost (no wins)
            lost_teams.append(team)
        elif stats["draws"] > 0 and stats["wins"] == 0 and stats["losses"] == 0:
            # Teams that have only drawn
            drawn_teams.append(team)
        elif stats["wins"] > 0:
            # Teams that have won at least once
            won_teams.append(team)
    
    # Sort each category by team number for consistent ordering
    never_played.sort(key=lambda t: t.team_number)
    lost_teams.sort(key=lambda t: t.team_number)
    drawn_teams.sort(key=lambda t: t.team_number)
    won_teams.sort(key=lambda t: t.team_number)
    
    # Return in priority order
    return never_played + lost_teams + drawn_teams + won_teams


def _determine_next_match(game_id: str, completed_match: Match, winner_id: str, loser_id: str, db: Session) -> dict:
    """Determine next match based on rotation rules"""
    # Get all teams for this game
    all_teams = db.query(GameTeam).filter(GameTeam.game_id == game_id).order_by(GameTeam.team_number).all()
    
    # Get all completed matches
    completed_matches = db.query(Match).filter(
        and_(
            Match.game_id == game_id,
            Match.status == MatchStatus.COMPLETED
        )
    ).all()
    
    # Track which teams have played recently
    recent_players = set()
    if completed_match:
        recent_players.add(completed_match.team_a_id)
        recent_players.add(completed_match.team_b_id)
    
    # If draw (0-0 after time), both teams are out - next two teams play
    if completed_match.is_draw and completed_match.team_a_score == 0 and completed_match.team_b_score == 0:
        available_teams = [team for team in all_teams if team.id not in recent_players]
        if len(available_teams) >= 2:
            return {
                "team_a_id": available_teams[0].id,
                "team_b_id": available_teams[1].id,
                "team_a_name": available_teams[0].team_name,
                "team_b_name": available_teams[1].team_name
            }
    
    # If there's a winner, winner stays and plays next available team
    elif winner_id:
        available_teams = [team for team in all_teams if team.id not in recent_players and team.id != winner_id]
        if len(available_teams) >= 1:
            winner_team = db.query(GameTeam).filter(GameTeam.id == winner_id).first()
            return {
                "team_a_id": winner_id,
                "team_b_id": available_teams[0].id,
                "team_a_name": winner_team.team_name if winner_team else "Unknown",
                "team_b_name": available_teams[0].team_name
            }
    
    return {}

@router.get("/{game_id}/next-match")
def get_next_match(
    game_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get details of the next match to be played"""
    game_id_str = str(game_id)
    
    # Get current match to determine what's next
    current_match = db.query(Match).filter(
        and_(
            Match.game_id == game_id_str,
            Match.status == MatchStatus.IN_PROGRESS
        )
    ).first()
    
    if current_match:
        # Current match is ongoing - next match depends on result
        current_scores = {
            "team_a_score": current_match.team_a_score,
            "team_b_score": current_match.team_b_score
        }
        
        # Simulate what next match would be based on current state
        if current_match.team_a_score == 0 and current_match.team_b_score == 0:
            # If still 0-0, show that next two teams would play if it ends in draw
            all_teams = db.query(GameTeam).filter(GameTeam.game_id == game_id_str).order_by(GameTeam.team_number).all()
            current_players = {current_match.team_a_id, current_match.team_b_id}
            available_teams = [team for team in all_teams if team.id not in current_players]
            
            if len(available_teams) >= 2:
                return {
                    "conditional": True,
                    "condition": "if_draw",
                    "team_a_id": available_teams[0].id,
                    "team_b_id": available_teams[1].id,
                    "team_a_name": available_teams[0].team_name,
                    "team_b_name": available_teams[1].team_name,
                    "message": "If current match ends 0-0, these teams play next"
                }
        else:
            # Determine likely winner and show next opponent
            likely_winner_id = current_match.team_a_id if current_match.team_a_score > current_match.team_b_score else current_match.team_b_id
            winner_team = db.query(GameTeam).filter(GameTeam.id == likely_winner_id).first()
            
            all_teams = db.query(GameTeam).filter(GameTeam.game_id == game_id_str).order_by(GameTeam.team_number).all()
            current_players = {current_match.team_a_id, current_match.team_b_id}
            available_teams = [team for team in all_teams if team.id not in current_players]
            
            if len(available_teams) >= 1:
                return {
                    "conditional": True,
                    "condition": "if_current_winner_wins",
                    "team_a_id": likely_winner_id,
                    "team_b_id": available_teams[0].id,
                    "team_a_name": winner_team.team_name if winner_team else "Current Winner",
                    "team_b_name": available_teams[0].team_name,
                    "message": f"If {winner_team.team_name if winner_team else 'current leader'} wins, they play {available_teams[0].team_name} next"
                }
    
    # Check if there's a scheduled next match
    next_match = db.query(Match).filter(
        and_(
            Match.game_id == game_id_str,
            Match.status == MatchStatus.SCHEDULED
        )
    ).first()
    
    if next_match:
        team_a = db.query(GameTeam).filter(GameTeam.id == next_match.team_a_id).first()
        team_b = db.query(GameTeam).filter(GameTeam.id == next_match.team_b_id).first()
        
        return {
            "conditional": False,
            "team_a_id": next_match.team_a_id,
            "team_b_id": next_match.team_b_id,
            "team_a_name": team_a.team_name if team_a else "Unknown",
            "team_b_name": team_b.team_name if team_b else "Unknown",
            "message": "Next confirmed match"
        }
    
    return {"message": "No next match determined yet"}

def _find_next_opponent(game_id: str, winner_id: str, completed_matches: list, db: Session) -> str:
    """Find the next team to play against the winner."""
    # Get all teams for this game
    all_teams = db.query(GameTeam).filter(GameTeam.game_id == game_id).all()
    all_team_ids = [team.id for team in all_teams]
    
    # Get teams that have already played in this match
    played_teams = set()
    for match in completed_matches:
        played_teams.add(match["team_a_id"])
        played_teams.add(match["team_b_id"])
    
    # Find teams that haven't played yet
    available_teams = [tid for tid in all_team_ids if tid not in played_teams and tid != winner_id]
    
    if available_teams:
        # Return the first available team (you could implement more sophisticated selection)
        return available_teams[0]
    
    return "unknown"


def _assign_referee_from_non_playing_teams(game_id: str, team_a_id: str, team_b_id: str, db: Session) -> str:
    """Assign a referee from teams that are not playing in the current match."""
    # Get all teams for this game
    all_teams = db.query(GameTeam).filter(GameTeam.game_id == game_id).all()
    
    # Find teams that are not playing in the current match
    non_playing_teams = [team for team in all_teams if team.id not in [team_a_id, team_b_id]]
    
    if non_playing_teams:
        # Get the first non-playing team and assign its captain as referee
        # You could implement more sophisticated referee selection logic
        referee_team = non_playing_teams[0]
        if referee_team.captain_id:
            return referee_team.captain_id
    
    return "unknown"


@router.post("/{game_id}/start-match")
def start_match(
    game_id: UUID,
    match_data: dict = Body(...),  # {team_a_id: int, team_b_id: int}
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a match between two teams (admin or referee only)."""
    game = db.query(Game).filter(Game.id == str(game_id)).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    membership = db.query(SportGroupMember).filter(
        and_(
            SportGroupMember.sport_group_id == game.sport_group_id,
            SportGroupMember.user_id == current_user.id
        )
    ).first()
    is_referee = (game.referee_id == membership.id if membership else False)
    is_admin = (membership.role == MemberRole.ADMIN if membership else False)
    if not (is_referee or is_admin):
        raise ForbiddenException("Only referee or admin can start matches")

    # Check if timer is running before allowing match to start
    if not game.timer_is_running:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Timer must be started before the match can begin. Please start the timer first."
        )

    team_a_id = match_data.get("team_a_id")
    team_b_id = match_data.get("team_b_id")
    
    if not team_a_id or not team_b_id:
        raise HTTPException(status_code=400, detail="Both team_a_id and team_b_id are required")
    
    # Verify teams exist and belong to this game
    team_a = db.query(GameTeam).filter(
        and_(GameTeam.id == team_a_id, GameTeam.game_id == str(game_id))
    ).first()
    team_b = db.query(GameTeam).filter(
        and_(GameTeam.id == team_b_id, GameTeam.game_id == str(game_id))
    ).first()
    
    if not team_a or not team_b:
        raise HTTPException(status_code=404, detail="One or both teams not found")
    
    # Set current match
    game.current_match = {
        "team_a_id": team_a_id,
        "team_b_id": team_b_id,
        "started_at": datetime.utcnow().isoformat(),
        "referee_id": game.referee_id
    }
    
    # Clear upcoming match since it's now current
    game.upcoming_match = None
    
    # Start the game timer
    game.status = GameStatus.IN_PROGRESS
    game.is_timer_running = True
    
    db.commit()
    
    return {
        "message": "Match started successfully",
        "current_match": game.current_match,
        "game_status": game.status.value
    }


@router.post("/{game_id}/end-match")
def end_match(
    game_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """End the current match (admin or referee only)."""
    game = db.query(Game).filter(Game.id == str(game_id)).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    membership = db.query(SportGroupMember).filter(
        and_(
            SportGroupMember.sport_group_id == game.sport_group_id,
            SportGroupMember.user_id == current_user.id
        )
    ).first()
    is_referee = (game.referee_id == membership.id if membership else False)
    is_admin = (membership.role == MemberRole.ADMIN if membership else False)
    if not (is_referee or is_admin):
        raise ForbiddenException("Only referee or admin can end matches")
    
    if not game.current_match:
        raise HTTPException(status_code=400, detail="No current match to end")
    
    # Stop the timer
    game.is_timer_running = False
    
    # Clear current match (this will be processed by the score update logic)
    # The score update endpoint will handle the winner/draw logic
    game.current_match = None
    
    db.commit()
    
    return {"message": "Match ended successfully"}


@router.post("/{game_id}/players/{player_id}/check-in")
def check_in_player(
    game_id: UUID,
    player_id: int,
    player_update: GamePlayerUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check in a player for the game"""
    game = db.query(Game).filter(Game.id == str(game_id)).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # Get player
    player = db.query(GamePlayer).filter(
        and_(GamePlayer.id == player_id, GamePlayer.game_id == str(game_id))
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
    game_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all players for a game"""
    game = db.query(Game).filter(Game.id == str(game_id)).first()
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
    
    players = db.query(GamePlayer).filter(GamePlayer.game_id == str(game_id)).all()
    return players


@router.put("/{game_id}/players/{player_id}/stats")
def update_player_stats(
    game_id: UUID,
    player_id: int,
    player_update: GamePlayerUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update player game stats (referee only)"""
    game = db.query(Game).filter(Game.id == str(game_id)).first()
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
        and_(GamePlayer.id == player_id, GamePlayer.game_id == str(game_id))
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

@router.get("/{game_id}/available-teams")
def get_available_teams(
    game_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get teams available for the next match."""
    game = db.query(Game).filter(Game.id == str(game_id)).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    membership = db.query(SportGroupMember).filter(
        and_(
            SportGroupMember.sport_group_id == game.sport_group_id,
            SportGroupMember.user_id == current_user.id,
            SportGroupMember.is_approved == True
        )
    ).first()
    if not membership:
        raise ForbiddenException("Only group members can view available teams")
    
    # Get all teams for this game
    all_teams = db.query(GameTeam).filter(GameTeam.game_id == str(game_id)).all()
    all_team_ids = [team.id for team in all_teams]
    
    # Get completed matches to see which teams have played
    completed_matches = getattr(game, "completed_matches", [])
    played_teams = set()
    for match in completed_matches:
        played_teams.add(match["team_a_id"])
        played_teams.add(match["team_b_id"])
    
    # Add teams from current match if it exists
    current_match = getattr(game, "current_match", None)
    if current_match:
        played_teams.add(current_match["team_a_id"])
        played_teams.add(current_match["team_b_id"])
    
    # Find available teams
    available_teams = [team for team in all_teams if team.id not in played_teams]
    
    return {
        "available_teams": [
            {
                "id": team.id,
                "name": team.team_name,
                "team_number": team.team_number,
                "captain_id": team.captain_id
            }
            for team in available_teams
        ],
        "total_teams": len(all_teams),
        "played_teams": len(played_teams),
        "available_count": len(available_teams)
    }
    

@router.post("/{game_id}/timer/start")
def start_match_timer(
    game_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start the match timer (admin or referee only)"""
    
    # Convert UUID to string for database query
    game_id_str = str(game_id)
    print(f"Looking for game with ID: {game_id_str}")  # Debug log
    
    
    # First, get the game
    game = db.query(Game).filter(Game.id == game_id_str).first()
    print(f"Game found: {game is not None}")  # Debug log
    if not game:
         # Let's see what games exist
        # all_games = db.query(Game).all()
        # print(f"All games in DB: {[g.id for g in all_games]}")  # Debug log
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Check if timer is already running
    if game.timer_is_running and not game.is_timer_expired():
        return {
            "message": "Timer already running",
            "remaining_seconds": game.get_remaining_time(),
            "started_at": game.timer_started_at.isoformat() if game.timer_started_at else None
        }
    
    # Look for ANY active match (IN_PROGRESS or SCHEDULED)
    current_match = db.query(Match).filter(
        and_(
            Match.game_id == game_id_str,
            Match.status.in_([MatchStatus.IN_PROGRESS, MatchStatus.SCHEDULED])
        )
    ).first()
    
    # If no match found, check if game is in progress and create a basic match
    if not current_match and game.status == GameStatus.IN_PROGRESS:
        # Get Team 1 and Team 2 to create a basic match
        team1 = db.query(GameTeam).filter(
            and_(GameTeam.game_id == game_id_str, GameTeam.team_number == 1)
        ).first()
        team2 = db.query(GameTeam).filter(
            and_(GameTeam.game_id == game_id_str, GameTeam.team_number == 2)
        ).first()
        
        if team1 and team2:
            # Create a match between Team 1 and Team 2
            current_match = Match(
                id=str(uuid.uuid4()),
                game_id=game_id_str,
                team_a_id=team1.id,
                team_b_id=team2.id,
                team_a_score=0,
                team_b_score=0,
                status=MatchStatus.IN_PROGRESS,
                started_at=datetime.now(MOUNTAIN_TZ)
            )
            db.add(current_match)
            db.flush()
        else:
            raise HTTPException(status_code=404, detail="No teams found to create a match")
    
    # Only start timer if it's not already running or has expired
    if not game.timer_is_running or game.is_timer_expired():
        # game.timer_started_at = datetime.now(MOUNTAIN_TZ)
        game.timer_started_at = datetime.now(timezone.utc)
        game.timer_remaining_seconds = 420  # 7 minutes
        game.timer_is_running = True
        game.status = GameStatus.IN_PROGRESS
        
    # Update match status to IN_PROGRESS if it was SCHEDULED
    if current_match.status == MatchStatus.SCHEDULED:
        current_match.status = MatchStatus.IN_PROGRESS
        
    # Update match with timer start if not already started
    if not current_match.started_at:
        current_match.started_at = datetime.now(timezone.utc)
        # current_match.started_at = datetime.now(MOUNTAIN_TZ)
    
    
    db.commit()
    
    return {
        "message": "Match timer started",
        "remaining_seconds": game.get_remaining_time(),
        "started_at": current_match.started_at.isoformat(),
        "match_id": current_match.id,
        "team_a_id": current_match.team_a_id,
        "team_b_id": current_match.team_b_id
    }

@router.get("/{game_id}/timer")
def get_match_timer(
    game_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current timer status"""
    game = db.query(Game).filter(Game.id == str(game_id)).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    remaining_seconds = game.get_remaining_time()
    
    return {
        "is_running": game.timer_is_running,
        "remaining_seconds": remaining_seconds,
        "total_seconds": game.match_duration_seconds,
        "started_at": game.timer_started_at.isoformat() if game.timer_started_at else None,
        "timer_expired": game.is_timer_expired()
    }