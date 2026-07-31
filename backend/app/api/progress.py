from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.ai import ContinueWatchingItemResponse
from app.services.progress_service import list_continue_watching

router = APIRouter(tags=["progress"])


@router.get("/continue-watching", response_model=list[ContinueWatchingItemResponse])
def get_continue_watching(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ContinueWatchingItemResponse]:
    return list_continue_watching(db, current_user)
