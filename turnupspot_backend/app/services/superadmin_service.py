from app.schemas.superadmin import SuperAdminStats
from app.models.user import User, UserRole
from app.models.event import Event
from app.models.vendor import Vendor
from app.core.database import get_db
from sqlalchemy.orm import Session
from typing import List

def get_app_stats(db: Session) -> SuperAdminStats:
    total_users = db.query(User).count()
    total_events = db.query(Event).count()
    total_vendors = db.query(Vendor).count()
    return SuperAdminStats(total_users=total_users, total_events=total_events, total_vendors=total_vendors)

def list_users(db: Session) -> List[User]:
    return db.query(User).all()

def change_user_role(user_id: int, new_role: UserRole, db: Session) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    user.role = new_role
    db.commit()
    db.refresh(user)
    return user

def ban_user(user_id: int, db: Session) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    user.is_active = False
    db.commit()
    return True 