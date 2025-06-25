from fastapi import APIRouter, Depends, HTTPException
from app.services.notification_service import publish_notification, cache_notification_count, get_cached_notification_count
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.post("/send")
async def send_notification(message: str, current_user: User = Depends(get_current_user)):
    await publish_notification(str(current_user.id), message)
    return {"ok": True}

@router.post("/count/{count}")
async def set_notification_count(count: int, current_user: User = Depends(get_current_user)):
    await cache_notification_count(str(current_user.id), count)
    return {"ok": True}

@router.get("/count")
async def get_notification_count(current_user: User = Depends(get_current_user)):
    count = await get_cached_notification_count(str(current_user.id))
    return {"count": count} 