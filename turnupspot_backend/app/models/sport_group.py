from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from app.core.database import Base


class SportsType(str, enum.Enum):
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


class SkillLevel(str, enum.Enum):
    ALL = "all"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    PROFESSIONAL = "professional"


class AgeGroup(str, enum.Enum):
    ALL = "all"
    UNDER_18 = "under18"
    EIGHTEEN_TO_TWENTY_FIVE = "18-25"
    TWENTY_SIX_TO_THIRTY_FIVE = "26-35"
    OVER_35 = "over35"


class MemberRole(str, enum.Enum):
    ADMIN = "admin"
    MEMBER = "member"


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
    playing_days = Column(String, nullable=False)  # Comma-separated days
    game_start_time = Column(DateTime, nullable=False)
    game_end_time = Column(DateTime, nullable=False)
    max_teams = Column(Integer, nullable=False)
    max_players_per_team = Column(Integer, nullable=False)
    rules = Column(String)
    referee_required = Column(Boolean, default=False)
    created_by = Column(String, ForeignKey("users.email"), nullable=False)
    sports_type = Column(Enum(SportsType), nullable=False)
    
    # Meta
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    creator = relationship(
        "User",
        back_populates="created_sport_groups",
        foreign_keys=[creator_id]
    )
    teams = relationship("Team", back_populates="sport_group")
    members = relationship("SportGroupMember", back_populates="sport_group")
    games = relationship("Game", back_populates="sport_group")
    chat_room = relationship("ChatRoom", back_populates="sport_group", uselist=False)

    def __repr__(self):
        return f"<SportGroup(id={self.id}, name='{self.name}', sport='{self.sports_type}')>"


class SportGroupMember(Base):
    __tablename__ = "sport_group_members"

    id = Column(Integer, primary_key=True, index=True)
    sport_group_id = Column(String, ForeignKey("sport_groups.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(Enum(MemberRole), default=MemberRole.MEMBER)
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
    
    #Relationships
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