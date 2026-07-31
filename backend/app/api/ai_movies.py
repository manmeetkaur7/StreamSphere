from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_admin, get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.ai import MovieSummaryResponse, ProgressResponse, ProgressUpsertRequest
from app.schemas.content import MovieResponse
from app.services.ai_provider import AIProvider, get_ai_provider
from app.services.movie_views import movie_response_list_from_rows
from app.services.progress_service import upsert_progress
from app.services.summary_service import get_or_generate_summary
from app.services.trending_service import get_trending_movie_rows

router = APIRouter(prefix="/movies", tags=["movies"])


def _completed_progress_response(movie_id: int) -> ProgressResponse:
    return ProgressResponse(
        id=0,
        movie_id=movie_id,
        progress_percentage=100,
        last_watched=datetime.now(timezone.utc),
        completed=True,
    )


@router.get("/trending", response_model=list[MovieResponse])
def list_trending_movies(db: Session = Depends(get_db)) -> list[MovieResponse]:
    return movie_response_list_from_rows(get_trending_movie_rows(db, limit=20))


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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProgressResponse:
    try:
        progress = upsert_progress(db, current_user, movie_id, payload.progress_percentage)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    if progress is None:
        response.status_code = status.HTTP_200_OK
        return _completed_progress_response(movie_id)
    return progress


@router.put("/{movie_id}/progress", response_model=ProgressResponse)
def update_movie_progress(
    movie_id: int,
    payload: ProgressUpsertRequest,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProgressResponse:
    try:
        progress = upsert_progress(db, current_user, movie_id, payload.progress_percentage)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    if progress is None:
        response.status_code = status.HTTP_200_OK
        return _completed_progress_response(movie_id)
    return progress


@router.post(
    "/{movie_id}/summary/regenerate",
    response_model=MovieSummaryResponse,
    dependencies=[Depends(get_current_admin)],
)
def regenerate_movie_summary(
    movie_id: int,
    db: Session = Depends(get_db),
    provider: AIProvider = Depends(get_ai_provider),
) -> MovieSummaryResponse:
    try:
        return get_or_generate_summary(db, provider, movie_id, force=True)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
