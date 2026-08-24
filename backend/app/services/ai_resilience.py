from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from dataclasses import dataclass
from typing import Generic, TypeVar

from app.core.config import get_settings
from app.models.movie import Movie
from app.services.ai_provider import AISearchResult, AIProvider, MovieSummaryResult
from app.services.metrics import get_metrics_registry

T = TypeVar("T")

_EXECUTOR = ThreadPoolExecutor(max_workers=4, thread_name_prefix="streamsphere-ai")


@dataclass(slots=True)
class AIExecutionResult(Generic[T]):
    payload: T
    degraded: bool = False
    reason: str | None = None


def _run_with_retries(operation_name: str, callback) -> AIExecutionResult[T]:
    settings = get_settings()
    last_error: Exception | None = None
    attempts = max(settings.ai_request_retries, 0) + 1

    for _ in range(attempts):
        future = _EXECUTOR.submit(callback)
        try:
            return AIExecutionResult(payload=future.result(timeout=settings.ai_request_timeout_seconds))
        except FutureTimeoutError as exc:
            future.cancel()
            last_error = TimeoutError(f"{operation_name} timed out.")
        except Exception as exc:  # pragma: no cover - exercised through callers
            last_error = exc

    get_metrics_registry().increment("ai.requests.failures")
    message = str(last_error) if last_error else f"{operation_name} failed."
    raise RuntimeError(message) from last_error


def fallback_search_result(query: str) -> AIExecutionResult[AISearchResult]:
    return AIExecutionResult(
        payload=AISearchResult(
            matching_movie_ids=[],
            reasoning=f"AI search is temporarily unavailable for '{query[:80]}'. Showing no AI matches right now.",
            confidence=0.2,
        ),
        degraded=True,
        reason="ai_unavailable",
    )


def fallback_summary_result(movie: Movie) -> AIExecutionResult[MovieSummaryResult]:
    themes = [genre.name for genre in movie.genres[:3]] or ["Drama"]
    return AIExecutionResult(
        payload=MovieSummaryResult(
            short_summary=f"{movie.title} is a {movie.language.lower()} story set in {movie.release_year}.",
            long_summary=(
                f"{movie.title} follows {movie.description.strip()} "
                f"It runs for {movie.duration_minutes} minutes and carries a {movie.maturity_rating} rating."
            ),
            main_themes=themes,
            viewer_type="Best for viewers who want the core catalog details while AI summaries are unavailable.",
        ),
        degraded=True,
        reason="ai_unavailable",
    )


def run_ai_search(provider: AIProvider, query: str, movies: list[Movie]) -> AIExecutionResult[AISearchResult]:
    try:
        return _run_with_retries("AI search", lambda: provider.search_movies(query, movies))
    except RuntimeError:
        return fallback_search_result(query)


def run_ai_summary(provider: AIProvider, movie: Movie) -> AIExecutionResult[MovieSummaryResult]:
    try:
        return _run_with_retries("AI summary", lambda: provider.summarize_movie(movie))
    except RuntimeError:
        return fallback_summary_result(movie)
