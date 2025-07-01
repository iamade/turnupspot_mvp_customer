from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Sport(Base):
    __tablename__ = "sports"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    type = Column(String, nullable=False)  # 'Team' or 'Individual'
    max_players_per_team = Column(Integer, nullable=True)
    min_teams = Column(Integer, nullable=True)
    players_per_match = Column(Integer, nullable=True)
    requires_referee = Column(Boolean, default=False)
    rules = Column(JSON, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null if default
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    creator = relationship("User")

    def __repr__(self):
        return f"<Sport(id={self.id}, name='{self.name}', type='{self.type}')>" 