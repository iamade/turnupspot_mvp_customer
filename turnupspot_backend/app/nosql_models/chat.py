from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ChatMessage(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    chat_id: str
    sender_id: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    attachments: Optional[List[str]] = None 