from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from app.models.chat import MessageType


class ChatMessageBase(BaseModel):
    content: str
    message_type: MessageType = MessageType.TEXT
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None


class ChatMessageCreate(ChatMessageBase):
    chat_room_id: int


class ChatMessageUpdate(BaseModel):
    content: Optional[str] = None
    is_edited: bool = True


class ChatMessageResponse(ChatMessageBase):
    id: int
    chat_room_id: int
    sender_id: int
    is_edited: bool
    edited_at: Optional[datetime] = None
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    sender: "UserResponse"

    class Config:
        from_attributes = True


class ChatRoomResponse(BaseModel):
    id: int
    name: Optional[str] = None
    room_type: str
    sport_group_id: Optional[int] = None
    event_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    recent_messages: Optional[list[ChatMessageResponse]] = []

    class Config:
        from_attributes = True


# Import here to avoid circular imports
from app.schemas.user import UserResponse
ChatMessageResponse.model_rebuild()