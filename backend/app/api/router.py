from fastapi import APIRouter

from app.api.admin import router as admin_dashboard_router
from app.api.ai_movies import router as ai_movies_router
from app.api.auth import router as auth_router
from app.api.favorites import router as favorites_router
from app.api.genres import router as genres_router
from app.api.health import router as health_router
from app.api.home import router as home_router
from app.api.metrics import router as metrics_router
from app.api.movies import router as movies_router
from app.api.notifications import router as notifications_router
from app.api.notifications import websocket_router as notification_websocket_router
from app.api.progress import router as progress_router
from app.api.profile import router as profile_router
from app.api.recommendations import admin_router as admin_router
from app.api.recommendations import router as recommendations_router
from app.api.reviews import router as reviews_router
from app.api.search import router as search_router
from app.api.watchlist import router as watchlist_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(metrics_router)
api_router.include_router(auth_router)
api_router.include_router(genres_router)
api_router.include_router(ai_movies_router)
api_router.include_router(movies_router)
api_router.include_router(notifications_router)
api_router.include_router(notification_websocket_router)
api_router.include_router(search_router)
api_router.include_router(reviews_router)
api_router.include_router(watchlist_router)
api_router.include_router(favorites_router)
api_router.include_router(progress_router)
api_router.include_router(recommendations_router)
api_router.include_router(home_router)
api_router.include_router(profile_router)
api_router.include_router(admin_router)
api_router.include_router(admin_dashboard_router)
