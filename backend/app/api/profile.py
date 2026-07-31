from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db
from app.models.favorite import Favorite
from app.models.movie import Movie
from app.models.rating import Rating
from app.models.review import Review
from app.models.user import User
from app.models.watchlist import Watchlist
from app.schemas.engagement import ProfileResponse, ProfileReviewResponse
from app.services.movie_views import build_movie_select, movie_response_from_row

router = APIRouter(tags=["profile"])


@router.get("/profile", response_model=ProfileResponse)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProfileResponse:
    favorite_entries = list(
        db.scalars(
            select(Favorite)
            .where(Favorite.user_id == current_user.id)
            .order_by(Favorite.created_at.desc(), Favorite.id.desc())
        ).all()
    )
    watchlist_entries = list(
        db.scalars(
            select(Watchlist)
            .where(Watchlist.user_id == current_user.id)
            .order_by(Watchlist.created_at.desc(), Watchlist.id.desc())
        ).all()
    )
    reviews = list(
        db.scalars(
            select(Review)
            .where(Review.user_id == current_user.id)
            .order_by(Review.created_at.desc(), Review.id.desc())
        ).all()
    )
    ratings_average = db.scalar(
        select(func.avg(Rating.rating)).where(Rating.user_id == current_user.id)
    )

    movie_ids = {entry.movie_id for entry in favorite_entries + watchlist_entries}
    movie_ids.update(review.movie_id for review in reviews[:5])
    movie_rows = db.execute(build_movie_select().where(Movie.id.in_(movie_ids))).all() if movie_ids else []
    movies_by_id = {row[0].id: movie_response_from_row(row) for row in movie_rows}

    recent_reviews = [
        ProfileReviewResponse(
            id=review.id,
            movie_id=review.movie_id,
            movie_title=movies_by_id[review.movie_id].title,
            user_id=review.user_id,
            username=review.user.username,
            title=review.title,
            body=review.body,
            rating=review.rating,
            created_at=review.created_at,
            updated_at=review.updated_at,
        )
        for review in reviews[:5]
    ]

    return ProfileResponse(
        username=current_user.username,
        email=current_user.email,
        account_creation_date=current_user.created_at,
        favorite_count=len(favorite_entries),
        watchlist_count=len(watchlist_entries),
        review_count=len(reviews),
        average_rating_given=round(float(ratings_average or 0.0), 2),
        recent_reviews=recent_reviews,
        favorite_movies=[movies_by_id[entry.movie_id] for entry in favorite_entries if entry.movie_id in movies_by_id],
        watchlist_movies=[movies_by_id[entry.movie_id] for entry in watchlist_entries if entry.movie_id in movies_by_id],
    )
