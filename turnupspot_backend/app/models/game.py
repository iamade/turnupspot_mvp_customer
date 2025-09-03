
from datetime import timezone, datetime as dt
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
import enum
import uuid
from uuid import uuid4

from app.core.database import Base
from app.models.manual_checkin import GameDayParticipant


class GameStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PlayerStatus(str, enum.Enum):
    EXPECTED = "expected"
    ARRIVED = "arrived"
    DELAYED = "delayed"
    ABSENT = "absent"
    
    
class MatchStatus(enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# Add the Match model
class Match(Base):
    __tablename__ = "matches"

    id = Column(String, primary_key=True, index=True)
    game_id = Column(String, ForeignKey("games.id"), nullable=False)
    team_a_id = Column(String, ForeignKey("game_teams.id"), nullable=False)
    team_b_id = Column(String, ForeignKey("game_teams.id"), nullable=False)
    team_a_score = Column(Integer, default=0)
    team_b_score = Column(Integer, default=0)
    winner_id = Column(String, ForeignKey("game_teams.id"), nullable=True)  # NULL for draws
    is_draw = Column(Boolean, default=False)
    status = Column(Enum(MatchStatus), default=MatchStatus.SCHEDULED)
    referee_id = Column(Integer, ForeignKey("sport_group_members.id"), nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    game = relationship("Game", back_populates="matches")
    team_a = relationship("GameTeam", foreign_keys=[team_a_id])
    team_b = relationship("GameTeam", foreign_keys=[team_b_id])
    winner = relationship("GameTeam", foreign_keys=[winner_id])
    referee = relationship("SportGroupMember", foreign_keys=[referee_id])


class Game(Base):
    __tablename__ = "games"

    id = Column(String, primary_key=True, index=True)
    sport_group_id = Column(String, ForeignKey("sport_groups.id"), nullable=False)
    # date = Column(DateTime, nullable=False)
    status = Column(String, default="scheduled")  # scheduled, active, completed
    
    # Game details
    game_date = Column(DateTime, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    
    # Officials
    referee_id = Column(Integer, ForeignKey("sport_group_members.id"), nullable=True)
    assistant_referee_id = Column(Integer, ForeignKey("sport_group_members.id"), nullable=True)
    
    # Game state
    status = Column(Enum(GameStatus), default=GameStatus.SCHEDULED)
    current_time = Column(Integer, default=0)  # Game time in seconds
    is_timer_running = Column(Boolean, default=False)
    
    # Notes
    notes = Column(Text, nullable=True)
    weather_conditions = Column(String, nullable=True)
    
      # Timer fields
    match_duration_seconds = Column(Integer, default=420)  # 7 minutes default
    timer_started_at = Column(DateTime, nullable=True)
    timer_remaining_seconds = Column(Integer, nullable=True)
    timer_is_running = Column(Boolean, default=False)
    
    # Current match info
    current_match_team_a = Column(String, nullable=True)
    current_match_team_b = Column(String, nullable=True)
    current_match_team_a_score = Column(Integer, default=0)
    current_match_team_b_score = Column(Integer, default=0)
    current_match_started_at = Column(DateTime, nullable=True)
    
    # Team rotation logic
    team_rotation_order = Column(Text, nullable=True)  # JSON string of team order
    current_rotation_index = Column(Integer, default=0)
    
    
    # Meta
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    sport_group = relationship("SportGroup", back_populates="games")
    referee = relationship("SportGroupMember", foreign_keys=[referee_id])
    assistant_referee = relationship("SportGroupMember", foreign_keys=[assistant_referee_id])
    teams = relationship("GameTeam", back_populates="game")
    players = relationship("GamePlayer", back_populates="game")
    manual_participants = relationship("GameDayParticipant", back_populates="game")
    completed_matches = Column(JSON, default=list)
    current_match = Column(JSON, nullable=True)
    upcoming_match = Column(JSON, nullable=True)
    coin_toss_state = Column(JSON, nullable=True)
    matches = relationship("Match", back_populates="game", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Game(id={self.id}, sport_group_id={self.sport_group_id}, status='{self.status}')>"
    
    def get_remaining_time(self) -> int:
        """Calculate remaining time in seconds"""
        if not self.timer_is_running or not self.timer_started_at:
            return self.timer_remaining_seconds or self.match_duration_seconds
        
        # Use timezone-aware datetime.now() instead of deprecated utcnow()
        now = dt.now(timezone.utc)
        
        # Ensure timer_started_at is timezone-aware
        if self.timer_started_at.tzinfo is None:
            timer_start = self.timer_started_at.replace(tzinfo=timezone.utc)
        else:
            timer_start = self.timer_started_at
        
        elapsed = (now - timer_start).total_seconds()
        remaining = max(0, (self.timer_remaining_seconds or self.match_duration_seconds) - int(elapsed))
        return remaining

    def is_timer_expired(self) -> bool:
        """Check if timer has expired"""
        return self.get_remaining_time() <= 0


class GameTeam(Base):
    __tablename__ = "game_teams"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4())) 
    game_id = Column(String, ForeignKey("games.id"), nullable=False)
    team_name = Column(String, nullable=False)
    team_number = Column(Integer, nullable=False)  # 1, 2, 3, etc.
    captain_id = Column(Integer, ForeignKey("sport_group_members.id"), nullable=True)
    score = Column(Integer, default=0)
    
    # Team stats
    goals_scored = Column(Integer, default=0)
    goals_conceded = Column(Integer, default=0)
    
    # Meta
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    game = relationship("Game", back_populates="teams")
    captain = relationship("SportGroupMember")
    players = relationship("GamePlayer", back_populates="team")

    def __repr__(self):
        return f"<GameTeam(id={self.id}, name='{self.team_name}', score={self.score})>"


class GamePlayer(Base):
    __tablename__ = "game_players"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(String, ForeignKey("games.id"), nullable=False)
    team_id = Column(String, ForeignKey("game_teams.id"), nullable=True)
    member_id = Column(Integer, ForeignKey("sport_group_members.id"), nullable=False)
    
    # Player status
    status = Column(Enum(PlayerStatus), default=PlayerStatus.EXPECTED)
    arrival_time = Column(DateTime, nullable=True)
    check_in_location_lat = Column(String, nullable=True)
    check_in_location_lng = Column(String, nullable=True)
    
    # Game stats
    goals_scored = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)
    
    # Meta
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    game = relationship("Game", back_populates="players")
    team = relationship("GameTeam", back_populates="players")
    member = relationship("SportGroupMember", back_populates="game_participations")

    def __repr__(self):
        return f"<GamePlayer(id={self.id}, member_id={self.member_id}, status='{self.status}')>"