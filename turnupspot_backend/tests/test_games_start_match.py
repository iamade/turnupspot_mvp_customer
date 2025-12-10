import pytest
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import uuid

from app.models.user import User
from app.models.sport_group import SportGroup, SportGroupMember, MemberRole
from app.models.game import Game, GameTeam, GamePlayer, Match, MatchStatus, GameStatus


def create_test_game_with_teams(db: Session, user: User, sport_group: SportGroup) -> tuple[Game, list[GameTeam]]:
    """Helper to create a test game with teams and players"""
    # Create game
    game = Game(
        id=str(uuid.uuid4()),
        sport_group_id=sport_group.id,
        game_date=datetime.now(timezone.utc),
        start_time=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc),
        status=GameStatus.SCHEDULED,
        timer_is_running=True,
        timer_started_at=datetime.now(timezone.utc),
        timer_remaining_seconds=420
    )
    db.add(game)
    db.flush()

    # Create teams
    teams = []
    for i in range(1, 6):  # Teams 1-5
        team = GameTeam(
            id=str(uuid.uuid4()),
            game_id=game.id,
            team_name=f"Team {i}",
            team_number=i,
            captain_id=user.id if i == 1 else None
        )
        db.add(team)
        teams.append(team)

    db.flush()

    # Add players to teams (so they have players)
    for team in teams:
        player = GamePlayer(
            game_id=game.id,
            team_id=team.id,
            member_id=user.id,
            status="arrived"
        )
        db.add(player)

    db.commit()
    db.refresh(game)
    return game, teams


def test_start_match_respects_rotation_priority(db_session: Session):
    """Test that start-match respects rotation priority over coin-toss priority"""
    # Arrange: Create user, sport group, and game
    user = User(
        email="test@example.com",
        hashed_password="hashed",
        first_name="Test",
        last_name="User",
        phone_number="+1234567890",
        is_active=True
    )
    db_session.add(user)
    db_session.flush()

    sport_group = SportGroup(
        name="Test Group",
        description="Test",
        sport_type="football",
        venue_name="Test Venue",
        venue_address="Test Address",
        venue_latitude=0.0,
        venue_longitude=0.0,
        max_teams=8,
        max_players_per_team=11,
        playing_days=["monday"],
        game_start_time="18:00",
        game_end_time="20:00",
        creator_id=user.id
    )
    db_session.add(sport_group)
    db_session.flush()

    # Add user as admin to sport group
    membership = SportGroupMember(
        sport_group_id=sport_group.id,
        user_id=user.id,
        role=MemberRole.ADMIN,
        is_approved=True
    )
    db_session.add(membership)
    db_session.flush()

    # Create game with teams
    game, teams = create_test_game_with_teams(db_session, user, sport_group)

    # Set up completed matches so rotation dictates team 4 vs 5 next
    # Simulate previous matches: team 1 beat team 2, team 3 beat team 1, team 2 beat team 3
    # This makes team 4 and 5 the next in rotation (never played)
    completed_matches = [
        Match(
            id=str(uuid.uuid4()),
            game_id=game.id,
            team_a_id=teams[0].id,  # team 1
            team_b_id=teams[1].id,  # team 2
            team_a_score=2,
            team_b_score=1,
            winner_id=teams[0].id,
            status=MatchStatus.COMPLETED,
            completed_at=datetime.now(timezone.utc)
        ),
        Match(
            id=str(uuid.uuid4()),
            game_id=game.id,
            team_a_id=teams[2].id,  # team 3
            team_b_id=teams[0].id,  # team 1
            team_a_score=2,
            team_b_score=1,
            winner_id=teams[2].id,
            status=MatchStatus.COMPLETED,
            completed_at=datetime.now(timezone.utc)
        ),
        Match(
            id=str(uuid.uuid4()),
            game_id=game.id,
            team_a_id=teams[1].id,  # team 2
            team_b_id=teams[2].id,  # team 3
            team_a_score=2,
            team_b_score=1,
            winner_id=teams[1].id,
            status=MatchStatus.COMPLETED,
            completed_at=datetime.now(timezone.utc)
        )
    ]

    for match in completed_matches:
        db_session.add(match)
    db_session.commit()

    # Set referee
    game.referee_id = membership.id
    db_session.commit()

    # Act: Call start_match with team 4 and 5 (which should be allowed by rotation)
    from app.api.v1.endpoints.games import start_match

    match_data = {
        "team_a_id": teams[3].id,  # team 4
        "team_b_id": teams[4].id   # team 5
    }

    result = start_match(game.id, match_data, user, db_session)

    # Assert: response and DB show game.current_match persisted as 4 vs 5
    # Check that a Match record was created
    current_match = db_session.query(Match).filter(
        Match.game_id == game.id,
        Match.status == MatchStatus.IN_PROGRESS
    ).first()

    assert current_match is not None, "No IN_PROGRESS match found in DB"
    assert current_match.team_a_id in [teams[3].id, teams[4].id], f"Team A should be team 4 or 5, got {current_match.team_a_id}"
    assert current_match.team_b_id in [teams[3].id, teams[4].id], f"Team B should be team 4 or 5, got {current_match.team_b_id}"
    assert current_match.team_a_id != current_match.team_b_id, "Team A and B should be different"

    # Check that result contains the current match
    assert result is not None, "Result should not be None"
    assert "current_match" in result, "Response should contain current_match"
    if result["current_match"] is not None:
        assert result["current_match"]["team_a_id"] in [teams[3].id, teams[4].id]
        assert result["current_match"]["team_b_id"] in [teams[3].id, teams[4].id]


def test_start_match_selects_highest_never_played_teams(db_session: Session):
    """Test that when teams 4 and 5 have played, next suggested are teams 6 and 7 (highest never played)"""
    # Arrange: Create user, sport group, and game with 7 teams
    user = User(
        email="test@example.com",
        hashed_password="hashed",
        first_name="Test",
        last_name="User",
        phone_number="+1234567890",
        is_active=True
    )
    db_session.add(user)
    db_session.flush()

    sport_group = SportGroup(
        name="Test Group",
        description="Test",
        sport_type="football",
        venue_name="Test Venue",
        venue_address="Test Address",
        venue_latitude=0.0,
        venue_longitude=0.0,
        max_teams=8,
        max_players_per_team=11,
        playing_days=["monday"],
        game_start_time="18:00",
        game_end_time="20:00",
        creator_id=user.id
    )
    db_session.add(sport_group)
    db_session.flush()

    # Add user as admin to sport group
    membership = SportGroupMember(
        sport_group_id=sport_group.id,
        user_id=user.id,
        role=MemberRole.ADMIN,
        is_approved=True
    )
    db_session.add(membership)
    db_session.flush()

    # Create game with teams 1-7
    game = Game(
        id=str(uuid.uuid4()),
        sport_group_id=sport_group.id,
        game_date=datetime.now(timezone.utc),
        start_time=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc),
        status=GameStatus.SCHEDULED,
        timer_is_running=True,
        timer_started_at=datetime.now(timezone.utc),
        timer_remaining_seconds=420
    )
    db_session.add(game)
    db_session.flush()

    teams = []
    for i in range(1, 8):  # Teams 1-7
        team = GameTeam(
            id=str(uuid.uuid4()),
            game_id=game.id,
            team_name=f"Team {i}",
            team_number=i,
            captain_id=user.id if i == 1 else None
        )
        db_session.add(team)
        teams.append(team)

    db_session.flush()

    # Add players to teams
    for team in teams:
        player = GamePlayer(
            game_id=game.id,
            team_id=team.id,
            member_id=user.id,
            status="arrived"
        )
        db_session.add(player)

    # Simulate completed match: team 4 beat team 5
    completed_match = Match(
        id=str(uuid.uuid4()),
        game_id=game.id,
        team_a_id=teams[3].id,  # team 4
        team_b_id=teams[4].id,  # team 5
        team_a_score=2,
        team_b_score=1,
        winner_id=teams[3].id,
        status=MatchStatus.COMPLETED,
        completed_at=datetime.now(timezone.utc)
    )
    db_session.add(completed_match)
    db_session.commit()

    # Act: Call get_suggested_teams_for_match
    from app.api.v1.endpoints.games import get_suggested_teams_for_match

    result = get_suggested_teams_for_match(game.id, user, db_session)

    # Assert: suggested teams should be 6 and 7
    assert result["suggested_teams"] is not None
    suggested_team_numbers = sorted([t["team_number"] for t in result["suggested_teams"]])
    assert suggested_team_numbers == [6, 7], f"Expected teams 6 and 7, got {suggested_team_numbers}"