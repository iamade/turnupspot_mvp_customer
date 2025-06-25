from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.sport_group import SportGroupMember
from app.models.chat import ChatRoom, ChatMessage, ChatRoomType, MessageType
from app.schemas.chat import ChatMessageCreate, ChatMessageUpdate, ChatMessageResponse, ChatRoomResponse
from app.core.exceptions import ForbiddenException
from app.services import chat_service
from bson import ObjectId
from fastapi import BackgroundTasks

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.room_connections: dict = {}

    async def connect(self, websocket: WebSocket, room_id: int, user_id: int):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if room_id not in self.room_connections:
            self.room_connections[room_id] = []
        
        self.room_connections[room_id].append({
            "websocket": websocket,
            "user_id": user_id
        })

    def disconnect(self, websocket: WebSocket, room_id: int):
        self.active_connections.remove(websocket)
        
        if room_id in self.room_connections:
            self.room_connections[room_id] = [
                conn for conn in self.room_connections[room_id] 
                if conn["websocket"] != websocket
            ]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast_to_room(self, message: str, room_id: int, exclude_user_id: Optional[int] = None):
        if room_id in self.room_connections:
            for connection in self.room_connections[room_id]:
                if exclude_user_id is None or connection["user_id"] != exclude_user_id:
                    try:
                        await connection["websocket"].send_text(message)
                    except:
                        # Connection is closed, remove it
                        self.room_connections[room_id].remove(connection)


manager = ConnectionManager()


@router.get("/rooms/{room_id}", response_model=ChatRoomResponse)
def get_chat_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat room details"""
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat room not found"
        )
    
    # Check if user has access to this room
    if room.room_type == ChatRoomType.SPORT_GROUP:
        membership = db.query(SportGroupMember).filter(
            and_(
                SportGroupMember.sport_group_id == room.sport_group_id,
                SportGroupMember.user_id == current_user.id,
                SportGroupMember.is_approved == True
            )
        ).first()
        
        if not membership:
            raise ForbiddenException("You don't have access to this chat room")
    
    # Get recent messages
    recent_messages = db.query(ChatMessage).filter(
        and_(
            ChatMessage.chat_room_id == room_id,
            ChatMessage.is_deleted == False
        )
    ).order_by(ChatMessage.created_at.desc()).limit(50).all()
    
    room.recent_messages = list(reversed(recent_messages))
    
    return room


@router.get("/rooms/{room_id}/messages", response_model=List[ChatMessageResponse])
async def get_chat_messages(
    room_id: int,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat messages for a room"""
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat room not found"
        )
    
    # Check if user has access to this room
    if room.room_type == ChatRoomType.SPORT_GROUP:
        membership = db.query(SportGroupMember).filter(
            and_(
                SportGroupMember.sport_group_id == room.sport_group_id,
                SportGroupMember.user_id == current_user.id,
                SportGroupMember.is_approved == True
            )
        ).first()
        
        if not membership:
            raise ForbiddenException("You don't have access to this chat room")
    
    messages = await chat_service.get_chat_messages(str(room_id), skip, limit)
    return messages


@router.post("/rooms/{room_id}/messages", response_model=ChatMessageResponse)
async def send_message(
    room_id: int,
    message_data: ChatMessageCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message to a chat room"""
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat room not found"
        )
    
    # Check if user has access to this room
    if room.room_type == ChatRoomType.SPORT_GROUP:
        membership = db.query(SportGroupMember).filter(
            and_(
                SportGroupMember.sport_group_id == room.sport_group_id,
                SportGroupMember.user_id == current_user.id,
                SportGroupMember.is_approved == True
            )
        ).first()
        
        if not membership:
            raise ForbiddenException("You don't have access to this chat room")
    
    message_dict = message_data.dict()
    message_dict["chat_id"] = str(room_id)
    message_dict["sender_id"] = str(current_user.id)
    chat_message = await chat_service.create_chat_message(message_dict)
    return chat_message


@router.put("/messages/{message_id}", response_model=ChatMessageResponse)
async def update_message(
    message_id: str,
    message_update: ChatMessageUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a chat message (sender only)"""
    update_data = message_update.dict(exclude_unset=True)
    chat_message = await chat_service.update_chat_message(message_id, update_data)
    if not chat_message:
        raise HTTPException(status_code=404, detail="Message not found")
    return chat_message


@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a chat message (sender only)"""
    deleted = await chat_service.delete_chat_message(message_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"ok": True}


@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time chat"""
    try:
        # Verify token and get user
        from app.core.security import verify_token
        payload = verify_token(token)
        email = payload.get("sub")
        
        user = db.query(User).filter(User.email == email).first()
        if not user:
            await websocket.close(code=1008, reason="Invalid user")
            return
        
        # Check room access
        room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
        if not room:
            await websocket.close(code=1008, reason="Room not found")
            return
        
        if room.room_type == ChatRoomType.SPORT_GROUP:
            membership = db.query(SportGroupMember).filter(
                and_(
                    SportGroupMember.sport_group_id == room.sport_group_id,
                    SportGroupMember.user_id == user.id,
                    SportGroupMember.is_approved == True
                )
            ).first()
            
            if not membership:
                await websocket.close(code=1008, reason="Access denied")
                return
        
        # Connect to room
        await manager.connect(websocket, room_id, user.id)
        
        try:
            while True:
                # Receive message from WebSocket
                data = await websocket.receive_text()
                
                # Create message in database
                db_message = ChatMessage(
                    chat_room_id=room_id,
                    sender_id=user.id,
                    content=data,
                    message_type=MessageType.TEXT
                )
                
                db.add(db_message)
                db.commit()
                db.refresh(db_message)
                
                # Broadcast to room
                import json
                message_data = {
                    "id": db_message.id,
                    "content": db_message.content,
                    "sender_id": db_message.sender_id,
                    "sender_name": user.full_name,
                    "created_at": db_message.created_at.isoformat(),
                    "message_type": db_message.message_type
                }
                
                await manager.broadcast_to_room(
                    json.dumps(message_data), 
                    room_id, 
                    exclude_user_id=user.id
                )
                
        except WebSocketDisconnect:
            manager.disconnect(websocket, room_id)
            
    except Exception as e:
        await websocket.close(code=1011, reason=str(e))