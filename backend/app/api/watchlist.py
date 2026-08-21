from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db
from app.models.movie import Movie
from app.models.user import User
from app.models.watchlist import Watchlist
from app.schemas.engagement import WatchlistItemResponse
from app.services.activity_service import record_activity
from app.services.background_jobs import background_job_dispatcher
from app.services.movie_views import build_movie_select, movie_response_from_row
from app.services.recommendation_service import invalidate_user_recommendation_cache

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


@router.get("", response_model=list[WatchlistItemResponse])
def list_watchlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[WatchlistItemResponse]:
    entries = list(
        db.scalars(
            select(Watchlist)
            .where(Watchlist.user_id == current_user.id)
            .order_by(Watchlist.created_at.desc(), Watchlist.id.desc())
        ).all()
    )
    if not entries:
        return []

    movie_rows = db.execute(
        build_movie_select().where(Movie.id.in_([entry.movie_id for entry in entries]))
    ).all()
    movies_by_id = {row[0].id: movie_response_from_row(row) for row in movie_rows}
    return [
        WatchlistItemResponse(id=entry.id, created_at=entry.created_at, movie=movies_by_id[entry.movie_id])
        for entry in entries
    ]


@router.post("/{movie_id}", response_model=WatchlistItemResponse, status_code=status.HTTP_201_CREATED)
def add_to_watchlist(
    movie_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WatchlistItemResponse:
    if db.get(Movie, movie_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found.")

    existing_entry = db.scalar(
        select(Watchlist).where(Watchlist.user_id == current_user.id, Watchlist.movie_id == movie_id)
    )
    if existing_entry is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Movie already in watchlist.")

    entry = Watchlist(user_id=current_user.id, movie_id=movie_id)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    record_activity(db, user_id=current_user.id, event_type="watchlist_add", movie_id=movie_id, commit=True)
    invalidate_user_recommendation_cache(current_user.id)
    background_job_dispatcher.queue_recommendation_refresh(background_tasks, user_id=current_user.id)
    background_job_dispatcher.queue_notification(
        background_tasks,
        user_id=current_user.id,
        notification_type="watchlist_reminder",
        title="Added to watchlist",
        message="This movie is in your watchlist and ready for your next session.",
    )
    movie_row = db.execute(build_movie_select().where(Movie.id == movie_id)).one()
    return WatchlistItemResponse(
        id=entry.id,
        created_at=entry.created_at,
        movie=movie_response_from_row(movie_row),
    )


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_watchlist(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    entry = db.scalar(
        select(Watchlist).where(Watchlist.user_id == current_user.id, Watchlist.movie_id == movie_id)
    )
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watchlist entry not found.")

    db.delete(entry)
    db.commit()
    invalidate_user_recommendation_cache(current_user.id)
