from app.core.cache import redis
import json

NOTIFICATION_CHANNEL = "notifications"

async def publish_notification(user_id: str, message: str):
    notification = {"user_id": user_id, "message": message}
    await redis.publish(NOTIFICATION_CHANNEL, json.dumps(notification))

async def cache_notification_count(user_id: str, count: int):
    await redis.set(f"user:{user_id}:notification_count", count)

async def get_cached_notification_count(user_id: str) -> int:
    count = await redis.get(f"user:{user_id}:notification_count")
    return int(count) if count else 0 