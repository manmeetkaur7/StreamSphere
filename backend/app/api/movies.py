from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db
from app.models.genre import Genre
from app.models.movie import Movie
from app.models.rating import Rating
from app.models.review import Review
from app.models.user import User
from app.schemas.content import (
    CreateMovie,
    MovieListResponse,
    MovieResponse,
    SortBy,
    SortOrder,
    UpdateMovie,
)
from app.schemas.engagement import RatingRequest, RatingResponse, ReviewCreateRequest, ReviewResponse
from app.services.movie_views import build_movie_select, movie_response_from_row, movie_response_list_from_rows
from app.services.recommendation_service import invalidate_user_recommendation_cache

router = APIRouter(prefix="/movies", tags=["movies"])


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
    statement: Select[tuple[object, ...]],
    *,
    search: str | None,
    genre: str | None,
    language: str | None,
) -> Select[tuple[object, ...]]:
    if genre:
        statement = statement.join(Movie.genres).where(func.lower(Genre.name) == genre.lower())
    if search:
        statement = statement.where(Movie.title.ilike(f"%{search.strip()}%"))
    if language:
        statement = statement.where(func.lower(Movie.language) == language.lower())
    return statement


def _apply_movie_sort(
    statement: Select[tuple[object, ...]],
    *,
    sort_by: SortBy,
    sort_order: SortOrder,
) -> Select[tuple[object, ...]]:
    sort_column = Movie.title if sort_by == "title" else Movie.release_year
    sort_expression = sort_column.asc() if sort_order == "asc" else sort_column.desc()
    return statement.order_by(sort_expression, Movie.id.asc())


def _movie_detail_row(db: Session, movie_id: int):
    row = db.execute(build_movie_select().where(Movie.id == movie_id)).one_or_none()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found.")
    return row


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
        build_movie_select(),
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
    items = movie_response_list_from_rows(db.execute(statement).all())

    return MovieListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size) if total else 0,
    )


@router.get("/{movie_id}", response_model=MovieResponse)
def get_movie(movie_id: int, db: Session = Depends(get_db)) -> MovieResponse:
    return movie_response_from_row(_movie_detail_row(db, movie_id))


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
    return movie_response_from_row(_movie_detail_row(db, movie.id))


@router.put("/{movie_id}", response_model=MovieResponse)
def update_movie(
    movie_id: int,
    payload: UpdateMovie,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Movie:
    movie = db.get(Movie, movie_id)
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
    return movie_response_from_row(_movie_detail_row(db, movie.id))


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


@router.post("/{movie_id}/rating", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
def create_rating(
    movie_id: int,
    payload: RatingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Rating:
    if db.get(Movie, movie_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found.")

    existing_rating = db.scalar(
        select(Rating).where(Rating.movie_id == movie_id, Rating.user_id == current_user.id)
    )
    if existing_rating is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already rated this movie.",
        )

    rating = Rating(movie_id=movie_id, user_id=current_user.id, rating=payload.rating)
    db.add(rating)
    db.commit()
    db.refresh(rating)
    invalidate_user_recommendation_cache(current_user.id)
    return rating


@router.put("/{movie_id}/rating", response_model=RatingResponse)
def update_rating(
    movie_id: int,
    payload: RatingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Rating:
    rating = db.scalar(
        select(Rating).where(Rating.movie_id == movie_id, Rating.user_id == current_user.id)
    )
    if rating is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found.")

    rating.rating = payload.rating
    db.commit()
    db.refresh(rating)
    invalidate_user_recommendation_cache(current_user.id)
    return rating


@router.delete("/{movie_id}/rating", status_code=status.HTTP_204_NO_CONTENT)
def delete_rating(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    rating = db.scalar(
        select(Rating).where(Rating.movie_id == movie_id, Rating.user_id == current_user.id)
    )
    if rating is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found.")

    db.delete(rating)
    db.commit()
    invalidate_user_recommendation_cache(current_user.id)


@router.get("/{movie_id}/reviews", response_model=list[ReviewResponse])
def list_reviews(movie_id: int, db: Session = Depends(get_db)) -> list[ReviewResponse]:
    if db.get(Movie, movie_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found.")

    reviews = list(
        db.scalars(
            select(Review)
            .where(Review.movie_id == movie_id)
            .order_by(Review.created_at.desc(), Review.id.desc())
        ).all()
    )
    return [_serialize_review(review) for review in reviews]


@router.post("/{movie_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    movie_id: int,
    payload: ReviewCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReviewResponse:
    if db.get(Movie, movie_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found.")

    review = Review(
        movie_id=movie_id,
        user_id=current_user.id,
        title=payload.title.strip(),
        body=payload.body.strip(),
        rating=payload.rating,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    invalidate_user_recommendation_cache(current_user.id)
    return _serialize_review(review)
