from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_admin, get_current_user
from app.core.demo import require_demo_write_access
from app.db.session import get_db
from app.models.user import User
from app.schemas.ai import AdminActionResponse, RecommendationResponse
from app.services.recommendation_service import clear_recommendation_cache, compute_recommendations, get_recommendations

router = APIRouter(tags=["recommendations"])
admin_router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/recommendations", response_model=RecommendationResponse)
def list_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RecommendationResponse:
    require_demo_write_access()
    return get_recommendations(db, current_user)


@admin_router.post(
    "/recommendations/recompute",
    response_model=RecommendationResponse,
    dependencies=[Depends(get_current_admin)],
)
def recompute_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RecommendationResponse:
    return compute_recommendations(db, current_user, persist=True)


@admin_router.delete(
    "/recommendations/cache",
    response_model=AdminActionResponse,
    dependencies=[Depends(get_current_admin)],
)
def clear_recommendations_cache(db: Session = Depends(get_db)) -> AdminActionResponse:
    require_demo_write_access()
    cleared = clear_recommendation_cache(db)
    return AdminActionResponse(detail=f"Cleared {cleared} cached recommendation entries.")
