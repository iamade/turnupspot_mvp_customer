from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class ChatRoomType(str, enum.Enum):
    SPORT_GROUP = "sport_group"
    EVENT = "event"
    DIRECT = "direct"


class MessageType(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    SYSTEM = "system"


class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    room_type = Column(Enum(ChatRoomType), nullable=False)
    
    # Related entity IDs
    sport_group_id = Column(String, ForeignKey("sport_groups.id"), nullable=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    
    # Room settings
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    sport_group = relationship("SportGroup", back_populates="chat_room")
    messages = relationship("ChatMessage", back_populates="chat_room")

    def __repr__(self):
        return f"<ChatRoom(id={self.id}, type='{self.room_type}', name='{self.name}')>"


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Message content
    message_type = Column(Enum(MessageType), default=MessageType.TEXT)
    content = Column(Text, nullable=False)
    file_url = Column(String, nullable=True)
    file_name = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    
    # Message metadata
    is_edited = Column(Boolean, default=False)
    edited_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    chat_room = relationship("ChatRoom", back_populates="messages")
    sender = relationship("User", back_populates="sent_messages")

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, sender_id={self.sender_id}, type='{self.message_type}')>"