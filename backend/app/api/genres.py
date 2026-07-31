from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db
from app.models.genre import Genre
from app.models.user import User
from app.schemas.content import GenreCreate, GenreResponse, GenreUpdate

router = APIRouter(prefix="/genres", tags=["genres"])


def _normalize_genre_name(name: str) -> str:
    return " ".join(name.strip().split())


def _get_existing_genre_by_name(db: Session, name: str) -> Genre | None:
    return db.scalar(select(Genre).where(func.lower(Genre.name) == name.lower()))


@router.get("", response_model=list[GenreResponse])
def list_genres(db: Session = Depends(get_db)) -> list[Genre]:
    return list(db.scalars(select(Genre).order_by(Genre.name.asc())).all())


@router.post("", response_model=GenreResponse, status_code=status.HTTP_201_CREATED)
def create_genre(
    payload: GenreCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Genre:
    normalized_name = _normalize_genre_name(payload.name)
    existing_genre = _get_existing_genre_by_name(db, normalized_name)
    if existing_genre is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A genre with this name already exists.",
        )

    genre = Genre(name=normalized_name)
    db.add(genre)
    db.commit()
    db.refresh(genre)
    return genre


@router.put("/{genre_id}", response_model=GenreResponse)
def update_genre(
    genre_id: int,
    payload: GenreUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Genre:
    genre = db.get(Genre, genre_id)
    if genre is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found.")

    normalized_name = _normalize_genre_name(payload.name)
    existing_genre = _get_existing_genre_by_name(db, normalized_name)
    if existing_genre is not None and existing_genre.id != genre.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A genre with this name already exists.",
        )

    genre.name = normalized_name
    db.commit()
    db.refresh(genre)
    return genre


@router.delete("/{genre_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_genre(
    genre_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> None:
    genre = db.get(Genre, genre_id)
    if genre is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found.")

    db.delete(genre)
    db.commit()
