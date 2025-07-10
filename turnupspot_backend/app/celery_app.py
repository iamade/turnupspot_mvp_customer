from celery import Celery
from celery.schedules import crontab
from app.tasks import scheduled 

celery_app = Celery(
    "turnupspot_backend",
    broker="redis://localhost:6379/0",  # Change if your Redis is elsewhere
    backend="redis://localhost:6379/0"
)

celery_app.conf.timezone = "UTC"
celery_app.conf.beat_schedule = {
    "create-games-every-day": {
        "task": "app.tasks.scheduled.create_games_for_today",
        #  "schedule": crontab(hour=0, minute=1),  # Runs every day at 00:01 UTC
        "schedule": crontab(),  # every minute
        # "schedule":  crontab(minute=0)	#Every hour at :00
    },
}