from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    Enum as SQLEnum,
    Float,
    Time,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum
from datetime import datetime, date

from app.core.database import Base


class SportsType(str, Enum):
    FOOTBALL = "football"
    BASKETBALL = "basketball"
    TENNIS = "tennis"
    VOLLEYBALL = "volleyball"
    CRICKET = "cricket"
    BASEBALL = "baseball"
    RUGBY = "rugby"
    HOCKEY = "hockey"
    BADMINTON = "badminton"
    TABLE_TENNIS = "table_tennis"
    SWIMMING = "swimming"
    ATHLETICS = "athletics"
    OTHER = "other"


class SkillLevel(str, Enum):
    ALL = "all"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    PROFESSIONAL = "professional"


class AgeGroup(str, Enum):
    ALL = "all"
    UNDER_18 = "under18"
    EIGHTEEN_TO_TWENTY_FIVE = "18-25"
    TWENTY_SIX_TO_THIRTY_FIVE = "26-35"
    OVER_35 = "over35"


class MemberRole(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"


class Day(str, Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"


class PlayingDay(Base):
    __tablename__ = "playing_days"

    id = Column(String, primary_key=True)
    sport_group_id = Column(String, ForeignKey("sport_groups.id", ondelete="CASCADE"))
    day = Column(SQLEnum(Day))

    # Relationship
    sport_group = relationship("SportGroup", back_populates="playing_days")


class SportGroup(Base):
    __tablename__ = "sport_groups"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    venue_name = Column(String, nullable=False)
    venue_address = Column(String, nullable=False)
    venue_image_url = Column(String)
    venue_latitude = Column(Float)
    venue_longitude = Column(Float)
    # playing_days = Column(String, default="0,2,4")  # e.g., "0,2,4" for Mon, Wed, Fri
    game_start_time = Column(Time, nullable=False)
    game_end_time = Column(Time, nullable=False)
    max_teams = Column(Integer, nullable=False)
    max_players_per_team = Column(Integer, nullable=False)
    rules = Column(String)
    game_config = Column(Text, nullable=True)  # JSON string for game rules
    min_players_per_team = Column(Integer, default=3)
    referee_required = Column(Boolean, default=False)
    created_by = Column(String, ForeignKey("users.email"), nullable=False)
    sports_type = Column(SQLEnum(SportsType), nullable=False)

    # Meta
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    creator = relationship(
        "User", back_populates="created_sport_groups", foreign_keys=[creator_id]
    )
    teams = relationship("Team", back_populates="sport_group")
    members = relationship("SportGroupMember", back_populates="sport_group")
    games = relationship("Game", back_populates="sport_group")
    chat_room = relationship("ChatRoom", back_populates="sport_group", uselist=False)
    playing_days = relationship(
        "PlayingDay", back_populates="sport_group", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<SportGroup(id={self.id}, name='{self.name}', sport='{self.sports_type}')>"

    def is_playing_day(self, today: date) -> bool:
        if not self.playing_days:
            return False  # or True if you want every day to be a playing day by default
        # playing_days = [int(d) for d in self.playing_days.split(",") if d.strip().isdigit()]
        playing_days = [pd.day.value for pd in self.playing_days]
        weekday_name = today.strftime("%A")
        return weekday_name in playing_days
        # return today.weekday() in playing_days


class SportGroupMember(Base):
    __tablename__ = "sport_group_members"

    id = Column(Integer, primary_key=True, index=True)
    sport_group_id = Column(String, ForeignKey("sport_groups.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(SQLEnum(MemberRole), default=MemberRole.MEMBER)
    is_approved = Column(Boolean, default=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    sport_group = relationship("SportGroup", back_populates="members")
    user = relationship("User", back_populates="sport_group_memberships")
    game_participations = relationship("GamePlayer", back_populates="member")

    def __repr__(self):
        return f"<SportGroupMember(group_id={self.sport_group_id}, user_id={self.user_id}, role='{self.role}')>"


class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    arrival_time = Column(DateTime, nullable=True)

    # Relationships
    team = relationship("Team", back_populates="members")
    user = relationship("User")

    def __repr__(self):
        return f"<TeamMember(team_id={self.team_id}, user_id={self.user_id})>"


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    sport_group_id = Column(String, ForeignKey("sport_groups.id"), nullable=False)

    # Relationships
    sport_group = relationship("SportGroup", back_populates="teams")
    members = relationship("TeamMember", back_populates="team")

    def __repr__(self):
        return f"<Team(id={self.id}, name='{self.name}', sport_group_id='{self.sport_group_id}')>"
