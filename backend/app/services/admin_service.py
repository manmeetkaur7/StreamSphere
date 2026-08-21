from collections.abc import Sequence

from sqlalchemy import cast, desc, func, select, String
from sqlalchemy.orm import Session

from app.models.activity_event import ActivityEvent
from app.models.favorite import Favorite
from app.models.genre import Genre
from app.models.movie import Movie
from app.models.movie_genre import MovieGenre
from app.models.rating import Rating
from app.models.review import Review
from app.models.user import User
from app.models.watchlist import Watchlist
from app.schemas.content import MovieResponse
from app.schemas.platform import (
    AdminReviewResponse,
    AdminStatsResponse,
    AdminUserResponse,
    AnalyticsGenreMetricResponse,
    AnalyticsMovieMetricResponse,
    DailyActiveUserResponse,
    PlatformAnalyticsResponse,
)
from app.services.movie_views import build_movie_select, movie_response_from_row


def build_admin_stats(db: Session) -> AdminStatsResponse:
    return AdminStatsResponse(
        total_users=int(db.scalar(select(func.count(User.id))) or 0),
        total_movies=int(db.scalar(select(func.count(Movie.id))) or 0),
        total_reviews=int(db.scalar(select(func.count(Review.id))) or 0),
        total_ratings=int(db.scalar(select(func.count(Rating.id))) or 0),
        total_watchlist_entries=int(db.scalar(select(func.count(Watchlist.id))) or 0),
        total_favorites=int(db.scalar(select(func.count(Favorite.id))) or 0),
        total_ai_searches=int(
            db.scalar(select(func.count(ActivityEvent.id)).where(ActivityEvent.event_type == "ai_search")) or 0
        ),
        total_recommendations_generated=int(
            db.scalar(
                select(func.count(ActivityEvent.id)).where(
                    ActivityEvent.event_type == "recommendation_generated"
                )
            )
            or 0
        ),
    )


def list_admin_users(db: Session) -> list[AdminUserResponse]:
    users = list(db.scalars(select(User).order_by(User.created_at.desc(), User.id.desc()).limit(25)).all())
    return [AdminUserResponse.model_validate(user, from_attributes=True) for user in users]


def list_admin_movies(db: Session) -> list[MovieResponse]:
    rows = db.execute(build_movie_select().order_by(Movie.created_at.desc(), Movie.id.desc()).limit(25)).all()
    return [movie_response_from_row(row) for row in rows]


def list_admin_reviews(db: Session) -> list[AdminReviewResponse]:
    reviews = list(
        db.scalars(select(Review).order_by(Review.created_at.desc(), Review.id.desc()).limit(25)).all()
    )
    if not reviews:
        return []
    movie_titles = {
        movie_id: title
        for movie_id, title in db.execute(
            select(Movie.id, Movie.title).where(Movie.id.in_([review.movie_id for review in reviews]))
        ).all()
    }
    return [
        AdminReviewResponse(
            id=review.id,
            movie_id=review.movie_id,
            movie_title=movie_titles.get(review.movie_id, "Unknown movie"),
            user_id=review.user_id,
            username=review.user.username,
            title=review.title,
            body=review.body,
            rating=review.rating,
            created_at=review.created_at,
            updated_at=review.updated_at,
        )
        for review in reviews
    ]


def _movie_metric_rows_to_payload(
    db: Session,
    rows: Sequence[tuple[int, float | int]],
) -> list[AnalyticsMovieMetricResponse]:
    movie_ids = [movie_id for movie_id, _ in rows]
    if not movie_ids:
        return []
    movie_rows = db.execute(build_movie_select().where(Movie.id.in_(movie_ids))).all()
    movies_by_id = {row[0].id: movie_response_from_row(row) for row in movie_rows}
    return [
        AnalyticsMovieMetricResponse(movie=movies_by_id[movie_id], count=float(count))
        for movie_id, count in rows
        if movie_id in movies_by_id
    ]


def build_platform_analytics(db: Session) -> PlatformAnalyticsResponse:
    most_viewed = db.execute(
        select(ActivityEvent.movie_id, func.count(ActivityEvent.id).label("count"))
        .where(ActivityEvent.event_type == "movie_view", ActivityEvent.movie_id.is_not(None))
        .group_by(ActivityEvent.movie_id)
        .order_by(desc("count"))
        .limit(10)
    ).all()
    most_favorited = db.execute(
        select(Favorite.movie_id, func.count(Favorite.id).label("count"))
        .group_by(Favorite.movie_id)
        .order_by(desc("count"))
        .limit(10)
    ).all()
    most_watchlisted = db.execute(
        select(Watchlist.movie_id, func.count(Watchlist.id).label("count"))
        .group_by(Watchlist.movie_id)
        .order_by(desc("count"))
        .limit(10)
    ).all()
    top_rated = db.execute(
        select(Rating.movie_id, cast(func.avg(Rating.rating), String).label("count"))
        .group_by(Rating.movie_id)
        .order_by(desc(func.avg(Rating.rating)), desc(func.count(Rating.id)))
        .limit(10)
    ).all()
    most_reviewed = db.execute(
        select(Review.movie_id, func.count(Review.id).label("count"))
        .group_by(Review.movie_id)
        .order_by(desc("count"))
        .limit(10)
    ).all()
    popular_genres = db.execute(
        select(Genre.name, func.count(MovieGenre.movie_id).label("count"))
        .join(MovieGenre, MovieGenre.genre_id == Genre.id)
        .group_by(Genre.id, Genre.name)
        .order_by(desc("count"), Genre.name.asc())
        .limit(10)
    ).all()
    ai_search_volume = int(
        db.scalar(select(func.count(ActivityEvent.id)).where(ActivityEvent.event_type == "ai_search")) or 0
    )
    dau_rows = db.execute(
        select(
            func.date(ActivityEvent.created_at).label("day"),
            func.count(func.distinct(ActivityEvent.user_id)).label("active_users"),
        )
        .group_by(func.date(ActivityEvent.created_at))
        .order_by(desc("day"))
        .limit(7)
    ).all()

    return PlatformAnalyticsResponse(
        most_viewed_movies=_movie_metric_rows_to_payload(db, most_viewed),
        most_favorited_movies=_movie_metric_rows_to_payload(db, most_favorited),
        most_watchlisted_movies=_movie_metric_rows_to_payload(db, most_watchlisted),
        top_rated_movies=_movie_metric_rows_to_payload(
            db,
            [(movie_id, float(count)) for movie_id, count in top_rated],
        ),
        most_reviewed_movies=_movie_metric_rows_to_payload(db, most_reviewed),
        popular_genres=[
            AnalyticsGenreMetricResponse(name=name, count=count)
            for name, count in popular_genres
        ],
        ai_search_volume=ai_search_volume,
        daily_active_users=[
            DailyActiveUserResponse(day=str(day), active_users=active_users)
            for day, active_users in reversed(dau_rows)
        ],
    )
