from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.favorites import router as favorites_router
from app.api.genres import router as genres_router
from app.api.health import router as health_router
from app.api.movies import router as movies_router
from app.api.profile import router as profile_router
from app.api.reviews import router as reviews_router
from app.api.watchlist import router as watchlist_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(genres_router)
api_router.include_router(movies_router)
api_router.include_router(reviews_router)
api_router.include_router(watchlist_router)
api_router.include_router(favorites_router)
api_router.include_router(profile_router)
