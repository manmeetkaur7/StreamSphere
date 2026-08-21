from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, require_admin
from app.db.session import get_db
from app.models.review import Review
from app.models.user import User
from app.schemas.ai import AdminActionResponse
from app.schemas.content import MovieResponse
from app.schemas.platform import (
    AdminReviewResponse,
    AdminStatsResponse,
    AdminUserResponse,
    AdminUserStatusUpdateRequest,
    PlatformAnalyticsResponse,
)
from app.services.admin_service import (
    build_admin_stats,
    build_platform_analytics,
    list_admin_movies,
    list_admin_reviews,
    list_admin_users,
)

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/stats", response_model=AdminStatsResponse)
def get_admin_stats(db: Session = Depends(get_db)) -> AdminStatsResponse:
    return build_admin_stats(db)


@router.get("/users", response_model=list[AdminUserResponse])
def get_admin_users(db: Session = Depends(get_db)) -> list[AdminUserResponse]:
    return list_admin_users(db)


@router.get("/movies", response_model=list[MovieResponse])
def get_admin_movies(db: Session = Depends(get_db)) -> list[MovieResponse]:
    return list_admin_movies(db)


@router.get("/reviews", response_model=list[AdminReviewResponse])
def get_admin_reviews(db: Session = Depends(get_db)) -> list[AdminReviewResponse]:
    return list_admin_reviews(db)


@router.delete("/reviews/{review_id}", response_model=AdminActionResponse)
def admin_delete_review(review_id: int, db: Session = Depends(get_db)) -> AdminActionResponse:
    review = db.scalar(select(Review).where(Review.id == review_id))
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")
    db.delete(review)
    db.commit()
    return AdminActionResponse(detail="Review deleted.")


@router.put("/users/{user_id}/status", response_model=AdminUserResponse)
def admin_update_user_status(
    user_id: UUID,
    payload: AdminUserStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AdminUserResponse:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if user.id == current_user.id and not payload.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot deactivate your own account.")
    user.is_active = payload.is_active
    db.commit()
    db.refresh(user)
    return AdminUserResponse.model_validate(user, from_attributes=True)


@router.get("/analytics", response_model=PlatformAnalyticsResponse)
def get_admin_analytics(db: Session = Depends(get_db)) -> PlatformAnalyticsResponse:
    return build_platform_analytics(db)
