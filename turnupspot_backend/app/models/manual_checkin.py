from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class GameDayParticipant(Base):
    __tablename__ = "game_day_participants"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    team = Column(Integer, nullable=True)
    is_registered_user = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    game = relationship("Game", back_populates="manual_participants") 