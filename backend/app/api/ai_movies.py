from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_admin, get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.ai import MovieSummaryResponse, ProgressResponse, ProgressUpsertRequest
from app.services.activity_service import record_activity
from app.services.ai_provider import AIProvider, get_ai_provider
from app.services.background_jobs import background_job_dispatcher
from app.services.progress_service import upsert_progress
from app.services.summary_service import get_or_generate_summary

router = APIRouter(prefix="/movies", tags=["movies"])


def _completed_progress_response(movie_id: int) -> ProgressResponse:
    return ProgressResponse(
        id=0,
        movie_id=movie_id,
        progress_percentage=100,
        last_watched=datetime.now(timezone.utc),
        completed=True,
    )


@router.get("/{movie_id}/summary", response_model=MovieSummaryResponse)
def get_movie_summary(
    movie_id: int,
    db: Session = Depends(get_db),
    provider: AIProvider = Depends(get_ai_provider),
) -> MovieSummaryResponse:
    try:
        return get_or_generate_summary(db, provider, movie_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{movie_id}/progress", response_model=ProgressResponse, status_code=status.HTTP_201_CREATED)
def create_movie_progress(
    movie_id: int,
    payload: ProgressUpsertRequest,
    response: Response,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProgressResponse:
    try:
        progress = upsert_progress(db, current_user, movie_id, payload.progress_percentage)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    if progress is None:
        record_activity(
            db,
            user_id=current_user.id,
            event_type="progress_update",
            movie_id=movie_id,
            metadata={"progress_percentage": 100, "completed": True},
            commit=True,
        )
        background_job_dispatcher.queue_notification(
            background_tasks,
            user_id=current_user.id,
            notification_type="system_notification",
            title="Movie completed",
            message="You completed a movie from your continue watching list.",
        )
        response.status_code = status.HTTP_200_OK
        return _completed_progress_response(movie_id)
    record_activity(
        db,
        user_id=current_user.id,
        event_type="progress_update",
        movie_id=movie_id,
        metadata={"progress_percentage": progress.progress_percentage, "completed": progress.completed},
        commit=True,
    )
    return progress


@router.put("/{movie_id}/progress", response_model=ProgressResponse)
def update_movie_progress(
    movie_id: int,
    payload: ProgressUpsertRequest,
    response: Response,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProgressResponse:
    try:
        progress = upsert_progress(db, current_user, movie_id, payload.progress_percentage)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    if progress is None:
        record_activity(
            db,
            user_id=current_user.id,
            event_type="progress_update",
            movie_id=movie_id,
            metadata={"progress_percentage": 100, "completed": True},
            commit=True,
        )
        background_job_dispatcher.queue_notification(
            background_tasks,
            user_id=current_user.id,
            notification_type="system_notification",
            title="Movie completed",
            message="You completed a movie from your continue watching list.",
        )
        response.status_code = status.HTTP_200_OK
        return _completed_progress_response(movie_id)
    record_activity(
        db,
        user_id=current_user.id,
        event_type="progress_update",
        movie_id=movie_id,
        metadata={"progress_percentage": progress.progress_percentage, "completed": progress.completed},
        commit=True,
    )
    return progress


@router.post(
    "/{movie_id}/summary/regenerate",
    response_model=MovieSummaryResponse,
    dependencies=[Depends(get_current_admin)],
)
def regenerate_movie_summary(
    movie_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    provider: AIProvider = Depends(get_ai_provider),
) -> MovieSummaryResponse:
    try:
        background_job_dispatcher.queue_summary_generation(background_tasks, movie_id=movie_id)
        return get_or_generate_summary(db, provider, movie_id, force=True)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
