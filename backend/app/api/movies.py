from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, selectinload

from app.core.auth import get_current_user
from app.db.session import get_db
from app.models.genre import Genre
from app.models.movie import Movie
from app.models.user import User
from app.schemas.content import (
    CreateMovie,
    MovieListResponse,
    MovieResponse,
    SortBy,
    SortOrder,
    UpdateMovie,
)

router = APIRouter(prefix="/movies", tags=["movies"])


def _movie_detail_query() -> Select[tuple[Movie]]:
    return select(Movie).options(selectinload(Movie.genres))


def _resolve_genres(db: Session, genre_ids: list[int]) -> list[Genre]:
    genres = list(
        db.scalars(select(Genre).where(Genre.id.in_(genre_ids)).order_by(Genre.name.asc())).all()
    )
    found_ids = {genre.id for genre in genres}
    missing_ids = [genre_id for genre_id in genre_ids if genre_id not in found_ids]
    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown genre ids: {', '.join(str(genre_id) for genre_id in missing_ids)}.",
        )
    genres_by_id = {genre.id: genre for genre in genres}
    return [genres_by_id[genre_id] for genre_id in genre_ids]


def _apply_movie_filters(
    statement: Select[tuple[Movie]],
    *,
    search: str | None,
    genre: str | None,
    language: str | None,
) -> Select[tuple[Movie]]:
    if genre:
        statement = statement.join(Movie.genres).where(func.lower(Genre.name) == genre.lower())
    if search:
        statement = statement.where(Movie.title.ilike(f"%{search.strip()}%"))
    if language:
        statement = statement.where(func.lower(Movie.language) == language.lower())
    return statement


def _apply_movie_sort(
    statement: Select[tuple[Movie]],
    *,
    sort_by: SortBy,
    sort_order: SortOrder,
) -> Select[tuple[Movie]]:
    sort_column = Movie.title if sort_by == "title" else Movie.release_year
    sort_expression = sort_column.asc() if sort_order == "asc" else sort_column.desc()
    return statement.order_by(sort_expression, Movie.id.asc())


@router.get("", response_model=MovieListResponse)
def list_movies(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=8, ge=1, le=50),
    search: str | None = Query(default=None),
    sort_by: SortBy = Query(default="title"),
    sort_order: SortOrder = Query(default="asc"),
    genre: str | None = Query(default=None),
    language: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> MovieListResponse:
    filtered_query = _apply_movie_filters(
        _movie_detail_query(),
        search=search,
        genre=genre,
        language=language,
    )
    count_query = select(func.count(func.distinct(Movie.id))).select_from(Movie)
    count_query = _apply_movie_filters(
        count_query,
        search=search,
        genre=genre,
        language=language,
    )
    total = db.scalar(count_query) or 0

    statement = _apply_movie_sort(
        filtered_query.distinct(),
        sort_by=sort_by,
        sort_order=sort_order,
    ).offset((page - 1) * page_size).limit(page_size)
    items = list(db.scalars(statement).all())

    return MovieListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size) if total else 0,
    )


@router.get("/{movie_id}", response_model=MovieResponse)
def get_movie(movie_id: int, db: Session = Depends(get_db)) -> Movie:
    movie = db.scalar(_movie_detail_query().where(Movie.id == movie_id))
    if movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found.")
    return movie


@router.post("", response_model=MovieResponse, status_code=status.HTTP_201_CREATED)
def create_movie(
    payload: CreateMovie,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Movie:
    movie = Movie(
        title=payload.title.strip(),
        description=payload.description.strip(),
        release_year=payload.release_year,
        duration_minutes=payload.duration_minutes,
        poster_url=str(payload.poster_url),
        trailer_url=str(payload.trailer_url),
        maturity_rating=payload.maturity_rating.strip(),
        language=payload.language.strip(),
    )
    movie.genres = _resolve_genres(db, payload.genre_ids)
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return db.scalar(_movie_detail_query().where(Movie.id == movie.id)) or movie


@router.put("/{movie_id}", response_model=MovieResponse)
def update_movie(
    movie_id: int,
    payload: UpdateMovie,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Movie:
    movie = db.scalar(_movie_detail_query().where(Movie.id == movie_id))
    if movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found.")

    updates = payload.model_dump(exclude_unset=True)
    if "title" in updates:
        movie.title = updates["title"].strip()
    if "description" in updates:
        movie.description = updates["description"].strip()
    if "release_year" in updates:
        movie.release_year = updates["release_year"]
    if "duration_minutes" in updates:
        movie.duration_minutes = updates["duration_minutes"]
    if "poster_url" in updates:
        movie.poster_url = str(updates["poster_url"])
    if "trailer_url" in updates:
        movie.trailer_url = str(updates["trailer_url"])
    if "maturity_rating" in updates:
        movie.maturity_rating = updates["maturity_rating"].strip()
    if "language" in updates:
        movie.language = updates["language"].strip()
    if "genre_ids" in updates:
        movie.genres = _resolve_genres(db, updates["genre_ids"])

    db.commit()
    db.refresh(movie)
    return movie


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> None:
    movie = db.get(Movie, movie_id)
    if movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found.")

    db.delete(movie)
    db.commit()
