from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.favorite import Favorite
from app.models.genre import Genre
from app.models.movie import Movie
from app.models.user import User
from app.schemas.ai import HomeResponse
from app.schemas.content import GenreResponse
from app.services.movie_views import build_movie_select, movie_response_list_from_rows
from app.services.progress_service import list_continue_watching
from app.services.recommendation_service import get_recommendations
from app.services.trending_service import get_top_rated_movie_rows, get_trending_movie_rows


def _rows_to_movies(db: Session, statement) -> list:
    return movie_response_list_from_rows(db.execute(statement).all())


def build_home_response(db: Session, current_user: User) -> HomeResponse:
    recommendations = get_recommendations(db, current_user)
    continue_watching = list_continue_watching(db, current_user)
    trending = movie_response_list_from_rows(get_trending_movie_rows(db, limit=20))
    favorites_rows = db.execute(
        build_movie_select().where(
            Movie.id.in_(
                select(Favorite.movie_id).where(Favorite.user_id == current_user.id)
            )
        )
    ).all()
    favorites = movie_response_list_from_rows(favorites_rows)
    recently_added = _rows_to_movies(
        db,
        build_movie_select().order_by(Movie.created_at.desc(), Movie.id.desc()).limit(10),
    )
    top_rated = movie_response_list_from_rows(get_top_rated_movie_rows(db, limit=10))
    popular_genres = db.scalars(
        select(Genre)
        .join(Movie.genres)
        .group_by(Genre.id)
        .order_by(func.count(Movie.id).desc(), Genre.name.asc())
        .limit(8)
    ).all()
    return HomeResponse(
        continue_watching=continue_watching,
        recommended=recommendations.recommended_movies,
        trending=trending,
        favorites=favorites,
        recently_added=recently_added,
        top_rated=top_rated,
        popular_genres=[GenreResponse.model_validate(genre) for genre in popular_genres],
    )
