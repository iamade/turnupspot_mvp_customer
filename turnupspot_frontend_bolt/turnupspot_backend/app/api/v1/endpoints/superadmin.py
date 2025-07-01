from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserResponse
from app.schemas.superadmin import SuperAdminStats
from app.services.superadmin_service import get_app_stats, list_users, change_user_role, ban_user
from app.api.deps import get_current_user
from typing import List

router = APIRouter(prefix="/superadmin", tags=["superadmin"])

@router.get("/stats", response_model=SuperAdminStats)
def get_stats():
    return get_app_stats()

def require_superadmin(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Superadmin only")
    return current_user

@router.get("/users", response_model=List[UserResponse])
async def superadmin_list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    return list_users(db)

@router.post("/users/{user_id}/role")
async def superadmin_change_user_role(
    user_id: int,
    new_role: UserRole,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    user = change_user_role(user_id, new_role, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"ok": True}

@router.post("/users/{user_id}/ban")
async def superadmin_ban_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    success = ban_user(user_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"ok": True} 