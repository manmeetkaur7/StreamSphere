from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.movie import Movie
from app.models.user import User
from app.models.watch_progress import WatchProgress
from app.schemas.ai import ContinueWatchingItemResponse, ProgressResponse
from app.services.movie_views import build_movie_select, movie_response_from_row


def upsert_progress(db: Session, current_user: User, movie_id: int, progress_percentage: int) -> ProgressResponse | None:
    if db.get(Movie, movie_id) is None:
        raise ValueError("Movie not found.")

    completed = progress_percentage >= 100
    entry = db.scalar(
        select(WatchProgress).where(
            WatchProgress.user_id == current_user.id,
            WatchProgress.movie_id == movie_id,
        )
    )

    if completed:
        if entry is not None:
            db.delete(entry)
            db.commit()
        return None

    if entry is None:
        entry = WatchProgress(
            user_id=current_user.id,
            movie_id=movie_id,
            progress_percentage=progress_percentage,
            completed=False,
        )
        db.add(entry)
    else:
        entry.progress_percentage = progress_percentage
        entry.completed = False

    db.commit()
    db.refresh(entry)
    return ProgressResponse(
        id=entry.id,
        movie_id=entry.movie_id,
        progress_percentage=entry.progress_percentage,
        last_watched=entry.last_watched,
        completed=entry.completed,
    )


def list_continue_watching(db: Session, current_user: User) -> list[ContinueWatchingItemResponse]:
    entries = list(
        db.scalars(
            select(WatchProgress)
            .where(WatchProgress.user_id == current_user.id, WatchProgress.completed.is_(False))
            .order_by(WatchProgress.last_watched.desc(), WatchProgress.id.desc())
        ).all()
    )
    if not entries:
        return []
    rows_by_id = {
        row[0].id: row
        for row in db.execute(build_movie_select().where(Movie.id.in_([entry.movie_id for entry in entries]))).all()
    }
    return [
        ContinueWatchingItemResponse(
            id=entry.id,
            progress_percentage=entry.progress_percentage,
            last_watched=entry.last_watched,
            completed=entry.completed,
            movie=movie_response_from_row(rows_by_id[entry.movie_id]),
        )
        for entry in entries
        if entry.movie_id in rows_by_id
    ]
