from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db
from app.models.favorite import Favorite
from app.models.movie import Movie
from app.models.user import User
from app.schemas.engagement import FavoriteItemResponse
from app.services.movie_views import build_movie_select, movie_response_from_row
from app.services.recommendation_service import invalidate_user_recommendation_cache

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("", response_model=list[FavoriteItemResponse])
def list_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[FavoriteItemResponse]:
    entries = list(
        db.scalars(
            select(Favorite)
            .where(Favorite.user_id == current_user.id)
            .order_by(Favorite.created_at.desc(), Favorite.id.desc())
        ).all()
    )
    if not entries:
        return []

    movie_rows = db.execute(
        build_movie_select().where(Movie.id.in_([entry.movie_id for entry in entries]))
    ).all()
    movies_by_id = {row[0].id: movie_response_from_row(row) for row in movie_rows}
    return [
        FavoriteItemResponse(id=entry.id, created_at=entry.created_at, movie=movies_by_id[entry.movie_id])
        for entry in entries
    ]


@router.post("/{movie_id}", response_model=FavoriteItemResponse, status_code=status.HTTP_201_CREATED)
def add_favorite(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FavoriteItemResponse:
    if db.get(Movie, movie_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found.")

    existing_entry = db.scalar(
        select(Favorite).where(Favorite.user_id == current_user.id, Favorite.movie_id == movie_id)
    )
    if existing_entry is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Movie already favorited.")

    entry = Favorite(user_id=current_user.id, movie_id=movie_id)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    invalidate_user_recommendation_cache(current_user.id)
    movie_row = db.execute(build_movie_select().where(Movie.id == movie_id)).one()
    return FavoriteItemResponse(
        id=entry.id,
        created_at=entry.created_at,
        movie=movie_response_from_row(movie_row),
    )


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    entry = db.scalar(
        select(Favorite).where(Favorite.user_id == current_user.id, Favorite.movie_id == movie_id)
    )
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite entry not found.")

    db.delete(entry)
    db.commit()
    invalidate_user_recommendation_cache(current_user.id)
