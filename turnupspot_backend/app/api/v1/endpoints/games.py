from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from uuid import UUID

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
from datetime import datetime
import random

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


@router.get("/{game_id}/state")
def get_game_state(
    game_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current match, upcoming match, completed matches, referee, and coin toss state."""
    game = db.query(Game).filter(Game.id == str(game_id)).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    # Check membership
    membership = db.query(SportGroupMember).filter(
        and_(
            SportGroupMember.sport_group_id == game.sport_group_id,
            SportGroupMember.user_id == current_user.id,
            SportGroupMember.is_approved == True
        )
    ).first()
    if not membership:
        raise ForbiddenException("Only group members can view game state")
    # Get teams, matches, referee, coin toss state
    teams = db.query(GameTeam).filter(GameTeam.game_id == str(game_id)).all()
    players = db.query(GamePlayer).filter(GamePlayer.game_id == str(game_id)).all()
    completed_matches = getattr(game, "completed_matches", [])
    current_match = getattr(game, "current_match", None)
    upcoming_match = getattr(game, "upcoming_match", None)
    referee = getattr(game, "referee_id", None)
    coin_toss_state = getattr(game, "coin_toss_state", None)
    return {
        "current_match": current_match,
        "upcoming_match": upcoming_match,
        "completed_matches": completed_matches,
        "referee": referee,
        "coin_toss_state": coin_toss_state,
        "teams": [t.id for t in teams],
        "players": [p.id for p in players]
    }

@router.post("/{game_id}/coin-toss")
def coin_toss(
    game_id: UUID,
    data: dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Perform a coin toss for a draw. Body: {team_a_id, team_b_id, team_a_choice, team_b_choice}"""
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
        raise ForbiddenException("Only admin can perform coin toss")
    
    # Simulate coin toss
    result = random.choice(["heads", "tails"])
    winner = data["team_a_id"] if data["team_a_choice"] == result else data["team_b_id"]
    loser = data["team_b_id"] if data["team_a_choice"] == result else data["team_a_id"]
    
    # Store coin toss state (for audit)
    game.coin_toss_state = {
        "team_a_id": data["team_a_id"],
        "team_b_id": data["team_b_id"],
        "team_a_choice": data["team_a_choice"],
        "team_b_choice": data["team_b_choice"],
        "result": result,
        "winner": winner,
        "loser": loser,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Set upcoming match based on coin toss result
    # Winner plays first, loser plays second
    completed_matches = getattr(game, "completed_matches", [])
    next_opponent = _find_next_opponent(str(game_id), winner, completed_matches, db)
    
    if next_opponent:
        game.upcoming_match = {
            "team_a_id": winner,
            "team_b_id": next_opponent,
            "created_at": datetime.utcnow().isoformat(),
            "coin_toss_winner": True
        }
        # Auto-assign referee from non-playing teams
        new_referee_id = _assign_referee_from_non_playing_teams(
            str(game_id), winner, next_opponent, db
        )
        if new_referee_id:
            game.referee_id = new_referee_id
    else:
        # No more teams to play
        game.upcoming_match = None
    
    db.commit()
    return {"result": result, "winner": winner, "upcoming_match": game.upcoming_match}

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
    
    return None


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
    
    return None


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