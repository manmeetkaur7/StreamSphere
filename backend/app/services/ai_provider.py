from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.core.config import get_settings
from app.models.movie import Movie


@dataclass(slots=True)
class AISearchResult:
    matching_movie_ids: list[int]
    reasoning: str
    confidence: float


@dataclass(slots=True)
class MovieSummaryResult:
    short_summary: str
    long_summary: str
    main_themes: list[str]
    viewer_type: str


class AIProvider(ABC):
    provider_name: str

    @abstractmethod
    def search_movies(self, query: str, movies: list[Movie]) -> AISearchResult:
        raise NotImplementedError

    @abstractmethod
    def summarize_movie(self, movie: Movie) -> MovieSummaryResult:
        raise NotImplementedError


class MockAIProvider(AIProvider):
    provider_name = "mock"

    def search_movies(self, query: str, movies: list[Movie]) -> AISearchResult:
        query_lower = query.lower()
        genre_terms = {
            "funny": "Comedy",
            "comedy": "Comedy",
            "science fiction": "Sci-Fi",
            "sci-fi": "Sci-Fi",
            "horror": "Horror",
            "action": "Action",
            "drama": "Drama",
            "animation": "Animation",
            "documentary": "Documentary",
        }
        matched_genres = {
            genre_name
            for keyword, genre_name in genre_terms.items()
            if keyword in query_lower
        }
        decade = None
        if "2020" in query_lower:
            decade = (2020, 2029)

        scored: list[tuple[int, Movie]] = []
        for movie in movies:
            score = 0
            if matched_genres and any(genre.name in matched_genres for genre in movie.genres):
                score += 3
            if decade and decade[0] <= movie.release_year <= decade[1]:
                score += 2
            if movie.title.lower() in query_lower or any(token in movie.description.lower() for token in query_lower.split()):
                score += 1
            if score > 0:
                scored.append((score, movie))

        scored.sort(key=lambda item: (-item[0], -item[1].release_year, item[1].title))
        matching_movie_ids = [movie.id for _, movie in scored[:10]]
        matched_labels = ", ".join(sorted(matched_genres)) if matched_genres else "broad catalog signals"
        reasoning = (
            f"Matched movies using {matched_labels} and release-era cues from the request."
        )
        confidence = min(0.95, 0.45 + (0.1 * len(matching_movie_ids)))
        return AISearchResult(
            matching_movie_ids=matching_movie_ids,
            reasoning=reasoning,
            confidence=round(confidence if matching_movie_ids else 0.25, 2),
        )

    def summarize_movie(self, movie: Movie) -> MovieSummaryResult:
        theme_candidates = [genre.name for genre in movie.genres[:3]]
        short_summary = f"{movie.title} is a {movie.language.lower()} {', '.join(theme_candidates).lower()} story set around {movie.description.split('.')[0].lower()}."
        long_summary = (
            f"{movie.title} ({movie.release_year}) follows {movie.description.strip()} "
            f"It blends {', '.join(theme_candidates).lower()} elements with a {movie.maturity_rating} tone and runs for {movie.duration_minutes} minutes."
        )
        viewer_type = (
            f"Best for viewers who enjoy {theme_candidates[0].lower()}-leaning stories with strong character momentum."
            if theme_candidates
            else "Best for viewers who enjoy character-driven streaming picks."
        )
        return MovieSummaryResult(
            short_summary=short_summary,
            long_summary=long_summary,
            main_themes=theme_candidates or ["Character-driven storytelling"],
            viewer_type=viewer_type,
        )


class OpenAIProvider(AIProvider):
    provider_name = "openai"

    def __init__(self, api_key: str | None):
        self.api_key = api_key

    def search_movies(self, query: str, movies: list[Movie]) -> AISearchResult:
        raise NotImplementedError("OpenAIProvider is a placeholder. Configure implementation before use.")

    def summarize_movie(self, movie: Movie) -> MovieSummaryResult:
        raise NotImplementedError("OpenAIProvider is a placeholder. Configure implementation before use.")


def get_ai_provider() -> AIProvider:
    settings = get_settings()
    if settings.ai_provider_name == "openai":
        return OpenAIProvider(settings.openai_api_key)
    return MockAIProvider()
