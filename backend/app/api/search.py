from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_optional_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.ai import AISearchRequest, AISearchResponse
from app.services.ai_provider import AIProvider, get_ai_provider
from app.services.search_service import search_movies_with_ai

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/ai", response_model=AISearchResponse)
def search_with_ai(
    payload: AISearchRequest,
    db: Session = Depends(get_db),
    provider: AIProvider = Depends(get_ai_provider),
    current_user: User | None = Depends(get_optional_current_user),
) -> AISearchResponse:
    return search_movies_with_ai(db, provider, payload.query, current_user=current_user)
