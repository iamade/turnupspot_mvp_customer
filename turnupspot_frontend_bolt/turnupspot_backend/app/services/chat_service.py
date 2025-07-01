from app.core.nosql import mongo_db
from app.nosql_models.chat import ChatMessage
from typing import List, Optional
from bson import ObjectId

CHAT_COLLECTION = "chat_messages"

async def create_chat_message(message_data: dict) -> ChatMessage:
    result = await mongo_db[CHAT_COLLECTION].insert_one(message_data)
    message_data["_id"] = result.inserted_id
    return ChatMessage(**message_data)

async def get_chat_messages(chat_id: str, skip: int = 0, limit: int = 50) -> List[ChatMessage]:
    cursor = mongo_db[CHAT_COLLECTION].find({"chat_id": chat_id}).sort("timestamp", -1).skip(skip).limit(limit)
    messages = [ChatMessage(**msg) async for msg in cursor]
    return list(reversed(messages))

async def update_chat_message(message_id: str, update_data: dict) -> Optional[ChatMessage]:
    result = await mongo_db[CHAT_COLLECTION].find_one_and_update(
        {"_id": ObjectId(message_id)},
        {"$set": update_data},
        return_document=True
    )
    if result:
        return ChatMessage(**result)
    return None

async def delete_chat_message(message_id: str) -> bool:
    result = await mongo_db[CHAT_COLLECTION].delete_one({"_id": ObjectId(message_id)})
    return result.deleted_count == 1 