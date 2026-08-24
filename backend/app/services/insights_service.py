from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.models.activity_event import ActivityEvent
from app.models.favorite import Favorite
from app.models.genre import Genre
from app.models.movie_genre import MovieGenre
from app.models.rating import Rating
from app.models.review import Review
from app.models.user import User
from app.models.watch_progress import WatchProgress
from app.models.watchlist import Watchlist
from app.schemas.platform import (
    ActivityEventResponse,
    GenreInsightResponse,
    ProfileInsightsResponse,
)


def build_profile_insights(db: Session, current_user: User) -> ProfileInsightsResponse:
    favorite_genres = db.execute(
        select(Genre.name, func.count(Favorite.id).label("count"))
        .join(MovieGenre, MovieGenre.genre_id == Genre.id)
        .join(Favorite, Favorite.movie_id == MovieGenre.movie_id)
        .where(Favorite.user_id == current_user.id)
        .group_by(Genre.id, Genre.name)
        .order_by(desc("count"), Genre.name.asc())
        .limit(5)
    ).all()
    viewed_genres = db.execute(
        select(Genre.name, func.count(ActivityEvent.id).label("count"))
        .join(MovieGenre, MovieGenre.movie_id == ActivityEvent.movie_id)
        .join(Genre, Genre.id == MovieGenre.genre_id)
        .where(
            ActivityEvent.user_id == current_user.id,
            ActivityEvent.event_type == "movie_view",
        )
        .group_by(Genre.id, Genre.name)
        .order_by(desc("count"), Genre.name.asc())
        .limit(5)
    ).all()
    ratings_average = db.scalar(
        select(func.avg(Rating.rating)).where(Rating.user_id == current_user.id)
    )
    movies_completed = int(
        db.scalar(
            select(func.count(WatchProgress.id)).where(
                WatchProgress.user_id == current_user.id,
                WatchProgress.completed.is_(True),
            )
        )
        or 0
    )
    movies_in_progress = int(
        db.scalar(
            select(func.count(WatchProgress.id)).where(
                WatchProgress.user_id == current_user.id,
                WatchProgress.completed.is_(False),
            )
        )
        or 0
    )
    watchlist_count = int(
        db.scalar(select(func.count(Watchlist.id)).where(Watchlist.user_id == current_user.id)) or 0
    )
    review_count = int(
        db.scalar(select(func.count(Review.id)).where(Review.user_id == current_user.id)) or 0
    )
    recent_events = list(
        db.scalars(
            select(ActivityEvent)
            .where(ActivityEvent.user_id == current_user.id)
            .order_by(ActivityEvent.created_at.desc(), ActivityEvent.id.desc())
            .limit(20)
        ).all()
    )

    return ProfileInsightsResponse(
        favorite_genres=[GenreInsightResponse(name=name, count=count) for name, count in favorite_genres],
        most_viewed_genres=[GenreInsightResponse(name=name, count=count) for name, count in viewed_genres],
        average_rating_given=round(float(ratings_average or 0.0), 2),
        movies_completed=movies_completed,
        movies_in_progress=movies_in_progress,
        total_watchlist_entries=watchlist_count,
        total_reviews=review_count,
        recent_activity=[
            ActivityEventResponse(
                id=event.id,
                event_type=event.event_type,
                movie_id=event.movie_id,
                metadata=event.event_metadata,
                created_at=event.created_at,
            )
            for event in recent_events
        ],
    )
