from app.core.config import get_settings
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.movie import Movie
from app.models.movie_summary import MovieSummary
from app.schemas.ai import MovieSummaryResponse
from app.services.ai_provider import AIProvider
from app.services.cache import get_cache_service


def _summary_cache_key(movie_id: int) -> str:
    return f"movie-summary:{movie_id}"


def _summary_response(summary: MovieSummary) -> MovieSummaryResponse:
    themes = [theme for theme in summary.main_themes.split("|") if theme]
    return MovieSummaryResponse(
        movie_id=summary.movie_id,
        short_summary=summary.short_summary,
        long_summary=summary.long_summary,
        main_themes=themes,
        viewer_type=summary.viewer_type,
        provider_name=summary.provider_name,
        generated_at=summary.generated_at,
        updated_at=summary.updated_at,
    )


def get_or_generate_summary(
    db: Session,
    provider: AIProvider,
    movie_id: int,
    *,
    force: bool = False,
) -> MovieSummaryResponse:
    cache_service = get_cache_service()
    if not force:
        cached = cache_service.get_json(_summary_cache_key(movie_id))
        if cached is not None:
            return MovieSummaryResponse.model_validate(cached)

    movie = db.get(Movie, movie_id)
    if movie is None:
        raise ValueError("Movie not found.")

    summary = db.scalar(select(MovieSummary).where(MovieSummary.movie_id == movie_id))
    if summary is not None and not force:
        payload = _summary_response(summary)
        cache_service.set_json(
            _summary_cache_key(movie_id),
            payload.model_dump(mode="json"),
            get_settings().movie_summary_cache_ttl_seconds,
        )
        return payload

    generated = provider.summarize_movie(movie)
    if summary is None:
        summary = MovieSummary(
            movie_id=movie_id,
            short_summary=generated.short_summary,
            long_summary=generated.long_summary,
            main_themes="|".join(generated.main_themes),
            viewer_type=generated.viewer_type,
            provider_name=provider.provider_name,
        )
        db.add(summary)
    else:
        summary.short_summary = generated.short_summary
        summary.long_summary = generated.long_summary
        summary.main_themes = "|".join(generated.main_themes)
        summary.viewer_type = generated.viewer_type
        summary.provider_name = provider.provider_name

    db.commit()
    db.refresh(summary)
    payload = _summary_response(summary)
    cache_service.set_json(
        _summary_cache_key(movie_id),
        payload.model_dump(mode="json"),
        get_settings().movie_summary_cache_ttl_seconds,
    )
    return payload
