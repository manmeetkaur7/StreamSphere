from collections import Counter

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.favorite import Favorite
from app.models.genre import Genre
from app.models.movie import Movie
from app.models.rating import Rating
from app.models.recommendation_cache import RecommendationCache
from app.models.review import Review
from app.models.user import User
from app.models.watchlist import Watchlist
from app.services.activity_service import record_activity
from app.core.config import get_settings
from app.schemas.ai import RecommendationResponse
from app.schemas.content import GenreResponse
from app.services.cache import get_cache_service
from app.services.movie_views import (
    build_movie_select,
    movie_response_from_row,
    movie_response_list_from_rows,
)
from app.services.trending_service import get_top_rated_movie_rows


def _csv_to_ints(value: str) -> list[int]:
    if not value.strip():
        return []
    return [int(part) for part in value.split(",") if part]


def _csv_to_strings(value: str) -> list[str]:
    return [part for part in value.split(",") if part]


def _movie_rows_by_ids(db: Session, movie_ids: list[int]):
    if not movie_ids:
        return []
    rows = db.execute(build_movie_select().where(Movie.id.in_(movie_ids))).all()
    rows_by_id = {row[0].id: row for row in rows}
    return [rows_by_id[movie_id] for movie_id in movie_ids if movie_id in rows_by_id]


def _top_genres_for_user(db: Session, current_user: User) -> list[Genre]:
    genre_counter: Counter[int] = Counter()

    favorite_movie_ids = db.scalars(
        select(Favorite.movie_id).where(Favorite.user_id == current_user.id)
    ).all()
    watchlist_movie_ids = db.scalars(
        select(Watchlist.movie_id).where(Watchlist.user_id == current_user.id)
    ).all()
    highly_rated_movie_ids = db.scalars(
        select(Rating.movie_id).where(Rating.user_id == current_user.id, Rating.rating >= 4)
    ).all()

    movie_ids = set(favorite_movie_ids) | set(watchlist_movie_ids) | set(highly_rated_movie_ids)
    if not movie_ids:
        return []

    movies = db.scalars(select(Movie).where(Movie.id.in_(movie_ids))).all()
    for movie in movies:
        for genre in movie.genres:
            genre_counter[genre.id] += 1

    ranked_ids = [genre_id for genre_id, _ in genre_counter.most_common(4)]
    if not ranked_ids:
        return []
    genres = db.scalars(select(Genre).where(Genre.id.in_(ranked_ids))).all()
    genres_by_id = {genre.id: genre for genre in genres}
    return [genres_by_id[genre_id] for genre_id in ranked_ids if genre_id in genres_by_id]


def _recommendation_candidates(db: Session, current_user: User) -> list[int]:
    top_genres = _top_genres_for_user(db, current_user)
    seen_movie_ids = set(
        db.scalars(
            select(Favorite.movie_id).where(Favorite.user_id == current_user.id)
        ).all()
    )
    seen_movie_ids.update(
        db.scalars(select(Watchlist.movie_id).where(Watchlist.user_id == current_user.id)).all()
    )
    seen_movie_ids.update(
        db.scalars(select(Rating.movie_id).where(Rating.user_id == current_user.id)).all()
    )
    seen_movie_ids.update(
        db.scalars(select(Review.movie_id).where(Review.user_id == current_user.id)).all()
    )

    recommended_ids: list[int] = []
    if top_genres:
        genre_ids = [genre.id for genre in top_genres]
        preferred_movies = db.scalars(
            select(Movie)
            .join(Movie.genres)
            .where(Genre.id.in_(genre_ids))
            .order_by(Movie.release_year.desc(), Movie.id.desc())
        ).all()
        for movie in preferred_movies:
            if movie.id not in seen_movie_ids and movie.id not in recommended_ids:
                recommended_ids.append(movie.id)

    highest_rated_rows = get_top_rated_movie_rows(db, limit=20)
    for row in highest_rated_rows:
        movie_id = row[0].id
        if movie_id not in seen_movie_ids and movie_id not in recommended_ids:
            recommended_ids.append(movie_id)

    recent_movies = db.scalars(select(Movie).order_by(Movie.created_at.desc(), Movie.id.desc())).all()
    for movie in recent_movies:
        if movie.id not in seen_movie_ids and movie.id not in recommended_ids:
            recommended_ids.append(movie.id)

    return recommended_ids[:20]


def _recommendation_cache_key(user_id: object) -> str:
    return f"recommendations:user:{user_id}"


def compute_recommendations(db: Session, current_user: User, *, persist: bool = True) -> RecommendationResponse:
    settings = get_settings()
    top_genres = _top_genres_for_user(db, current_user)
    movie_ids = _recommendation_candidates(db, current_user)
    movie_rows = _movie_rows_by_ids(db, movie_ids)
    recommended_movies = movie_response_list_from_rows(movie_rows)
    genre_labels = [genre.name for genre in top_genres]
    reason = (
        "Recommendations blend your favorite genres, strong personal ratings, watchlist activity, and high-performing recent catalog additions."
        if genre_labels
        else "Recommendations are based on top-rated and recently added movies until more personal taste data is available."
    )

    payload = RecommendationResponse(
        recommended_movies=recommended_movies,
        recommended_genres=[GenreResponse.model_validate(genre) for genre in top_genres],
        reason_for_recommendation=reason,
    )

    if persist:
        cache = db.scalar(
            select(RecommendationCache).where(RecommendationCache.user_id == current_user.id)
        )
        if cache is None:
            cache = RecommendationCache(
                user_id=current_user.id,
                recommended_movie_ids="",
                recommended_genres="",
                reason_for_recommendation=reason,
            )
            db.add(cache)

        cache.recommended_movie_ids = ",".join(str(movie.id) for movie in recommended_movies)
        cache.recommended_genres = ",".join(genre_labels)
        cache.reason_for_recommendation = reason
        record_activity(
            db,
            user_id=current_user.id,
            event_type="recommendation_generated",
            metadata={"recommended_count": len(recommended_movies)},
        )
        db.commit()
        get_cache_service().set_json(
            _recommendation_cache_key(current_user.id),
            payload.model_dump(mode="json"),
            settings.recommendation_cache_ttl_seconds,
        )

    return payload


def get_recommendations(db: Session, current_user: User) -> RecommendationResponse:
    cache_service = get_cache_service()
    cached = cache_service.get_json(_recommendation_cache_key(current_user.id))
    if cached is not None:
        return RecommendationResponse.model_validate(cached)

    cache = db.scalar(
        select(RecommendationCache).where(RecommendationCache.user_id == current_user.id)
    )
    if cache is None:
        return compute_recommendations(db, current_user)

    movie_rows = _movie_rows_by_ids(db, _csv_to_ints(cache.recommended_movie_ids))
    recommended_movies = [movie_response_from_row(row) for row in movie_rows]
    genres = db.scalars(
        select(Genre).where(Genre.name.in_(_csv_to_strings(cache.recommended_genres)))
    ).all()
    genres_by_name = {genre.name: genre for genre in genres}
    ordered_genres = [
        GenreResponse.model_validate(genres_by_name[name])
        for name in _csv_to_strings(cache.recommended_genres)
        if name in genres_by_name
    ]
    payload = RecommendationResponse(
        recommended_movies=recommended_movies,
        recommended_genres=ordered_genres,
        reason_for_recommendation=cache.reason_for_recommendation,
    )
    cache_service.set_json(
        _recommendation_cache_key(current_user.id),
        payload.model_dump(mode="json"),
        get_settings().recommendation_cache_ttl_seconds,
    )
    return payload


def invalidate_user_recommendation_cache(user_id: object) -> None:
    get_cache_service().delete(_recommendation_cache_key(user_id))


def clear_recommendation_cache(db: Session) -> int:
    caches = db.scalars(select(RecommendationCache)).all()
    count = len(list(caches))
    for cache in list(caches):
        invalidate_user_recommendation_cache(cache.user_id)
        db.delete(cache)
    db.commit()
    return count
