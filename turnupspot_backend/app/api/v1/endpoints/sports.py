from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User, UserRole
from app.models.sport import Sport
from app.schemas.sport import SportCreate, SportUpdate, SportResponse

router = APIRouter()

@router.get("/", response_model=List[SportResponse])
def list_sports(db: Session = Depends(get_db)):
    return db.query(Sport).all()

@router.post("/", response_model=SportResponse)
def create_sport(sport: SportCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_sport = Sport(
        name=sport.name,
        type=sport.type,
        max_players_per_team=sport.max_players_per_team,
        min_teams=sport.min_teams,
        players_per_match=sport.players_per_match,
        requires_referee=sport.requires_referee,
        rules=sport.rules,
        created_by=current_user.id,
        is_default=False
    )
    db.add(db_sport)
    db.commit()
    db.refresh(db_sport)
    return db_sport

@router.put("/{sport_id}", response_model=SportResponse)
def update_sport(sport_id: int, sport: SportUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_sport = db.query(Sport).filter(Sport.id == sport_id).first()
    if not db_sport:
        raise HTTPException(status_code=404, detail="Sport not found")
    if db_sport.created_by != current_user.id and current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to edit this sport")
    update_data = sport.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_sport, field, value)
    db.commit()
    db.refresh(db_sport)
    return db_sport

@router.delete("/{sport_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sport(sport_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_sport = db.query(Sport).filter(Sport.id == sport_id).first()
    if not db_sport:
        raise HTTPException(status_code=404, detail="Sport not found")
    if db_sport.created_by != current_user.id and current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to delete this sport")
    db.delete(db_sport)
    db.commit()
    return None 