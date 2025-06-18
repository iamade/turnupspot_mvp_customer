from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


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


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    sport_group_id = Column(Integer, ForeignKey("sport_groups.id"), nullable=False)
    
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
    
    # Meta
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    sport_group = relationship("SportGroup", back_populates="games")
    referee = relationship("SportGroupMember", foreign_keys=[referee_id])
    assistant_referee = relationship("SportGroupMember", foreign_keys=[assistant_referee_id])
    teams = relationship("GameTeam", back_populates="game")
    players = relationship("GamePlayer", back_populates="game")

    def __repr__(self):
        return f"<Game(id={self.id}, sport_group_id={self.sport_group_id}, status='{self.status}')>"


class GameTeam(Base):
    __tablename__ = "game_teams"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
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
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("game_teams.id"), nullable=True)
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