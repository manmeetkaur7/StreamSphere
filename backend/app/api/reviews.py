from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db
from app.models.review import Review
from app.models.user import User
from app.schemas.engagement import ReviewResponse, ReviewUpdateRequest
from app.services.background_jobs import background_job_dispatcher
from app.services.recommendation_service import invalidate_user_recommendation_cache

router = APIRouter(prefix="/reviews", tags=["reviews"])


def _serialize_review(review: Review) -> ReviewResponse:
    return ReviewResponse(
        id=review.id,
        movie_id=review.movie_id,
        user_id=review.user_id,
        username=review.user.username,
        title=review.title,
        body=review.body,
        rating=review.rating,
        created_at=review.created_at,
        updated_at=review.updated_at,
    )


@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    payload: ReviewUpdateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReviewResponse:
    review = db.scalar(select(Review).where(Review.id == review_id))
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")
    if review.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to edit this review.")

    updates = payload.model_dump(exclude_unset=True)
    if "title" in updates:
        review.title = updates["title"].strip()
    if "body" in updates:
        review.body = updates["body"].strip()
    if "rating" in updates:
        review.rating = updates["rating"]

    db.commit()
    db.refresh(review)
    invalidate_user_recommendation_cache(current_user.id)
    background_job_dispatcher.queue_recommendation_refresh(background_tasks, user_id=current_user.id)
    return _serialize_review(review)


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    review = db.scalar(select(Review).where(Review.id == review_id))
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")
    if review.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to delete this review.")

    db.delete(review)
    db.commit()
    invalidate_user_recommendation_cache(current_user.id)
    background_job_dispatcher.queue_recommendation_refresh(background_tasks, user_id=current_user.id)
