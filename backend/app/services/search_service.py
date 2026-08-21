from app.core.config import get_settings
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.movie import Movie
from app.models.user import User
from app.schemas.ai import AISearchResponse
from app.services.activity_service import record_activity
from app.services.ai_provider import AIProvider
from app.services.cache import get_cache_service, stable_cache_key
from app.services.movie_views import build_movie_select, movie_response_list_from_rows


def search_movies_with_ai(
    db: Session,
    provider: AIProvider,
    query: str,
    *,
    current_user: User | None = None,
) -> AISearchResponse:
    cache_key = stable_cache_key("ai-search", query)
    cached = get_cache_service().get_json(cache_key)
    if cached is not None:
        return AISearchResponse.model_validate(cached)

    movies = list(db.scalars(select(Movie).order_by(Movie.release_year.desc(), Movie.id.desc())).all())
    result = provider.search_movies(query, movies)
    rows = []
    if result.matching_movie_ids:
        row_by_id = {
            row[0].id: row
            for row in db.execute(build_movie_select().where(Movie.id.in_(result.matching_movie_ids))).all()
        }
        rows = [row_by_id[movie_id] for movie_id in result.matching_movie_ids if movie_id in row_by_id]
    payload = AISearchResponse(
        matching_movies=movie_response_list_from_rows(rows),
        reasoning=result.reasoning,
        confidence=result.confidence,
    )
    if current_user is not None:
        record_activity(
            db,
            user_id=current_user.id,
            event_type="ai_search",
            metadata={"query": query[:120], "match_count": len(payload.matching_movies)},
            commit=True,
        )
    get_cache_service().set_json(
        cache_key,
        payload.model_dump(mode="json"),
        get_settings().ai_search_cache_ttl_seconds,
    )
    return payload
