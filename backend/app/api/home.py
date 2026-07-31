from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.ai import HomeResponse
from app.services.home_service import build_home_response

router = APIRouter(tags=["home"])


@router.get("/home", response_model=HomeResponse)
def get_home(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HomeResponse:
    return build_home_response(db, current_user)
