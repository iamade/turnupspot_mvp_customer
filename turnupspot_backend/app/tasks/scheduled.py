from datetime import datetime
from celery import shared_task
from ..core.database import SessionLocal
from ..models.sport_group import SportGroup
from ..models.game import Game, GameStatus

@shared_task
def create_games_for_today():
    db = SessionLocal()
    today = datetime.utcnow().date()
    print(f"[CELERY] Running create_games_for_today for {today}")

    sport_groups = db.query(SportGroup).all()
    for group in sport_groups:
        if not group.is_playing_day(today):
            print(f"[CELERY] Skipping group {group.id} (not a playing day)")
            continue

        existing_game = db.query(Game).filter(
            Game.sport_group_id == group.id,
            Game.game_date == today
        ).first()
        if not existing_game:
            new_game = Game(
                sport_group_id=group.id,
                game_date=today,
                start_time=datetime.combine(today, group.game_start_time),
                end_time=datetime.combine(today, group.game_end_time),
                status=GameStatus.SCHEDULED
            )
            db.add(new_game)
            print(f"[CELERY] Created game for group {group.id} on {today}")
        else:
            print(f"[CELERY] Game already exists for group {group.id} on {today}")
    db.commit()
    db.close()