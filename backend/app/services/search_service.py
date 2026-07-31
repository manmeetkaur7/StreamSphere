from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.movie import Movie
from app.schemas.ai import AISearchResponse
from app.services.ai_provider import AIProvider
from app.services.movie_views import build_movie_select, movie_response_list_from_rows


def search_movies_with_ai(db: Session, provider: AIProvider, query: str) -> AISearchResponse:
    movies = list(db.scalars(select(Movie).order_by(Movie.release_year.desc(), Movie.id.desc())).all())
    result = provider.search_movies(query, movies)
    rows = []
    if result.matching_movie_ids:
        row_by_id = {
            row[0].id: row
            for row in db.execute(build_movie_select().where(Movie.id.in_(result.matching_movie_ids))).all()
        }
        rows = [row_by_id[movie_id] for movie_id in result.matching_movie_ids if movie_id in row_by_id]
    return AISearchResponse(
        matching_movies=movie_response_list_from_rows(rows),
        reasoning=result.reasoning,
        confidence=result.confidence,
    )
