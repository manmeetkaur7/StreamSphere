from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models.favorite import Favorite
from app.models.movie import Movie
from app.models.rating import Rating
from app.models.review import Review
from app.models.watchlist import Watchlist
from app.services.movie_views import build_movie_select


def get_trending_movie_rows(db: Session, *, limit: int = 20):
    favorite_counts = (
        select(Favorite.movie_id.label("movie_id"), func.count(Favorite.id).label("favorite_count"))
        .group_by(Favorite.movie_id)
        .subquery()
    )
    watchlist_counts = (
        select(Watchlist.movie_id.label("movie_id"), func.count(Watchlist.id).label("watchlist_count"))
        .group_by(Watchlist.movie_id)
        .subquery()
    )
    review_counts = (
        select(Review.movie_id.label("movie_id"), func.count(Review.id).label("review_count"))
        .group_by(Review.movie_id)
        .subquery()
    )
    ratings_avg = (
        select(Rating.movie_id.label("movie_id"), func.avg(Rating.rating).label("average_rating"))
        .group_by(Rating.movie_id)
        .subquery()
    )
    statement: Select = (
        build_movie_select()
        .outerjoin(favorite_counts, favorite_counts.c.movie_id == Movie.id)
        .outerjoin(watchlist_counts, watchlist_counts.c.movie_id == Movie.id)
        .outerjoin(review_counts, review_counts.c.movie_id == Movie.id)
        .outerjoin(ratings_avg, ratings_avg.c.movie_id == Movie.id)
        .order_by(
            func.coalesce(favorite_counts.c.favorite_count, 0).desc(),
            func.coalesce(watchlist_counts.c.watchlist_count, 0).desc(),
            func.coalesce(ratings_avg.c.average_rating, 0.0).desc(),
            func.coalesce(review_counts.c.review_count, 0).desc(),
            Movie.release_year.desc(),
            Movie.id.desc(),
        )
        .limit(limit)
    )
    return db.execute(statement).all()


def get_top_rated_movie_rows(db: Session, *, limit: int = 10):
    statement = build_movie_select()
    statement = (
        statement
        .order_by(
            func.coalesce(statement.selected_columns.average_rating, 0.0).desc(),
            func.coalesce(statement.selected_columns.total_ratings, 0).desc(),
            Movie.release_year.desc(),
            Movie.id.desc(),
        )
        .limit(limit)
    )
    return db.execute(statement).all()
