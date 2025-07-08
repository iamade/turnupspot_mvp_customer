from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, sport_groups, events, vendors, games, chat, superadmin, notifications, sports, game_day


api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(sport_groups.router, prefix="/sport-groups", tags=["sport-groups"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(vendors.router, prefix="/vendors", tags=["vendors"])
api_router.include_router(games.router, prefix="/games", tags=["games"])
api_router.include_router(game_day.router, prefix="/games/game-day", tags=["game-day"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(sports.router, prefix="/sports", tags=["sports"])
api_router.include_router(superadmin.router)
api_router.include_router(notifications.router)