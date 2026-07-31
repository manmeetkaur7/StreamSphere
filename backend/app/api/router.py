from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.genres import router as genres_router
from app.api.health import router as health_router
from app.api.movies import router as movies_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(genres_router)
api_router.include_router(movies_router)
