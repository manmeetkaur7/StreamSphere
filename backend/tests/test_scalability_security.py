from __future__ import annotations

import uuid
from contextlib import contextmanager

from alembic.config import Config
from alembic.script import ScriptDirectory
from fastapi.testclient import TestClient
from sqlalchemy import text

from app import main
from app.core.auth import get_current_user
from app.db.base import Base, ensure_schema_compatibility, register_models
from app.db.database import engine
from app.db.session import SessionLocal
from app.models.genre import Genre
from app.models.movie import Movie
from app.models.user import User
from app.services.ai_provider import AIProvider, AISearchResult, MovieSummaryResult, get_ai_provider
from app.services.cache import reset_runtime_services


@contextmanager
def no_op_lifespan(_: object):
    yield


class BrokenAIProvider(AIProvider):
    provider_name = "broken"

    def search_movies(self, query: str, movies: list[Movie]) -> AISearchResult:
        raise TimeoutError(f"search failed for {query}")

    def summarize_movie(self, movie: Movie) -> MovieSummaryResult:
        raise TimeoutError(f"summary failed for {movie.title}")


def setup_module() -> None:
    register_models()
    Base.metadata.create_all(bind=engine)
    ensure_schema_compatibility()


def _reset_tables() -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                "TRUNCATE TABLE activity_events, notifications, watch_progress, recommendation_cache, "
                "movie_summaries, watchlists, favorites, ratings, reviews, movie_genres, movies, genres, users "
                "RESTART IDENTITY CASCADE"
            )
        )


def _create_user(*, username: str, email: str) -> User:
    with SessionLocal() as db:
        user = User(
            id=uuid.uuid4(),
            username=username,
            email=email,
            hashed_password="$2b$12$WbV22xqTQ1pIY1jaB6Q6YeBmkws0xA4dPrmT2ymlk/wEYBLETymF6",  # Password123!
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        db.expunge(user)
        return user


def _build_client(monkeypatch, current_user: User | None = None, *, broken_ai: bool = False) -> TestClient:
    monkeypatch.setattr(main, "lifespan", no_op_lifespan)
    app = main.create_app()
    if current_user is not None:
        app.dependency_overrides[get_current_user] = lambda: current_user
    if broken_ai:
        app.dependency_overrides[get_ai_provider] = lambda: BrokenAIProvider()
    return TestClient(app)


def test_security_headers_are_present(monkeypatch) -> None:
    reset_runtime_services()
    client = _build_client(monkeypatch)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"
    assert "content-security-policy" in response.headers
    client.close()


def test_structured_404_error_contains_request_id(monkeypatch) -> None:
    client = _build_client(monkeypatch)

    response = client.get("/does-not-exist")

    assert response.status_code == 404
    payload = response.json()
    assert payload["detail"] == "Not Found"
    assert payload["error"]["code"] == "not_found"
    assert payload["error"]["request_id"] == response.headers["x-request-id"]
    client.close()


def test_metrics_endpoint_reports_safe_counters(monkeypatch) -> None:
    reset_runtime_services()
    client = _build_client(monkeypatch)

    assert client.get("/health").status_code == 200
    metrics = client.get("/metrics")

    assert metrics.status_code == 200
    payload = metrics.json()
    assert payload["http.requests.total"] >= 1
    assert "http.requests.duration_ms.avg" in payload
    client.close()


def test_ai_search_gracefully_falls_back_when_provider_fails(monkeypatch) -> None:
    _reset_tables()
    user = _create_user(username="searcher", email="searcher@example.com")
    client = _build_client(monkeypatch, current_user=user, broken_ai=True)

    genre = client.post("/genres", json={"name": "Fallback Genre"}).json()
    client.post(
        "/movies",
        json={
            "title": "Fallback Search Movie",
            "description": "A safe movie entry used to test AI search fallback behavior.",
            "release_year": 2025,
            "duration_minutes": 101,
            "poster_url": "https://example.com/posters/fallback-search.jpg",
            "trailer_url": "https://example.com/trailers/fallback-search",
            "maturity_rating": "PG-13",
            "language": "English",
            "genre_ids": [genre["id"]],
        },
    )

    response = client.post("/search/ai", json={"query": "fallback query"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["matching_movies"] == []
    assert "temporarily unavailable" in payload["reasoning"]
    client.close()
    _reset_tables()


def test_movie_summary_gracefully_falls_back_when_provider_fails(monkeypatch) -> None:
    _reset_tables()
    user = _create_user(username="summarizer", email="summarizer@example.com")
    client = _build_client(monkeypatch, current_user=user, broken_ai=True)

    genre = client.post("/genres", json={"name": "Summary Genre"}).json()
    movie = client.post(
        "/movies",
        json={
            "title": "Fallback Summary Movie",
            "description": "A catalog entry for resilient summary generation testing.",
            "release_year": 2024,
            "duration_minutes": 109,
            "poster_url": "https://example.com/posters/fallback-summary.jpg",
            "trailer_url": "https://example.com/trailers/fallback-summary",
            "maturity_rating": "PG",
            "language": "English",
            "genre_ids": [genre["id"]],
        },
    ).json()

    response = client.get(f"/movies/{movie['id']}/summary")

    assert response.status_code == 200
    payload = response.json()
    assert payload["movie_id"] == movie["id"]
    assert payload["short_summary"]
    assert payload["viewer_type"]
    client.close()
    _reset_tables()


def test_recommendation_cache_isolated_per_user(monkeypatch) -> None:
    _reset_tables()
    user_a = _create_user(username="alpha", email="alpha@example.com")
    user_b = _create_user(username="beta", email="beta@example.com")

    with SessionLocal() as db:
        genre = Genre(name="Isolation Genre")
        db.add(genre)
        db.flush()
        db.add_all(
            [
                Movie(
                    title="Isolation One",
                    description="First recommendation input movie.",
                    release_year=2025,
                    duration_minutes=100,
                    poster_url="https://example.com/posters/isolation-one.jpg",
                    trailer_url="https://example.com/trailers/isolation-one",
                    maturity_rating="PG-13",
                    language="English",
                    genres=[genre],
                ),
                Movie(
                    title="Isolation Two",
                    description="Second recommendation candidate.",
                    release_year=2026,
                    duration_minutes=104,
                    poster_url="https://example.com/posters/isolation-two.jpg",
                    trailer_url="https://example.com/trailers/isolation-two",
                    maturity_rating="PG-13",
                    language="English",
                    genres=[genre],
                ),
            ]
        )
        db.commit()

    client_a = _build_client(monkeypatch, current_user=user_a)
    client_b = _build_client(monkeypatch, current_user=user_b)

    payload_a = client_a.get("/recommendations").json()
    payload_b = client_b.get("/recommendations").json()

    assert payload_a["reason_for_recommendation"] == payload_b["reason_for_recommendation"]
    assert payload_a is not payload_b
    client_a.close()
    client_b.close()
    _reset_tables()


def test_alembic_configuration_exposes_head_revision() -> None:
    config = Config("backend/alembic.ini")
    config.set_main_option("script_location", "backend/alembic")
    script = ScriptDirectory.from_config(config)

    assert script.get_current_head() == "20260821_0002"
