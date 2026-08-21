import uuid
from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text

from app import main
from app.core.auth import get_current_user
from app.db.base import Base, ensure_schema_compatibility, register_models
from app.db.database import engine
from app.db.session import SessionLocal
from app.models.favorite import Favorite
from app.models.activity_event import ActivityEvent
from app.models.genre import Genre
from app.models.movie import Movie
from app.models.movie_genre import MovieGenre
from app.models.movie_summary import MovieSummary
from app.models.notification import Notification
from app.models.rating import Rating
from app.models.recommendation_cache import RecommendationCache
from app.models.review import Review
from app.models.user import User
from app.models.watch_progress import WatchProgress
from app.models.watchlist import Watchlist
from app.services.ai_provider import MockAIProvider, get_ai_provider


@contextmanager
def no_op_lifespan(_: object):
    yield


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


def _create_user(username: str, email: str, *, is_admin: bool = False) -> User:
    with SessionLocal() as db:
        user = User(
            id=uuid.uuid4(),
            username=username,
            email=email,
            hashed_password="hashed-password",
            is_admin=is_admin,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        db.expunge(user)
        return user


def _build_client(monkeypatch, current_user: User) -> TestClient:
    monkeypatch.setattr(main, "lifespan", no_op_lifespan)
    app = main.create_app()
    app.dependency_overrides[get_current_user] = lambda: current_user
    app.dependency_overrides[get_ai_provider] = lambda: MockAIProvider()
    return TestClient(app)


def _create_genre(client: TestClient, name: str) -> dict:
    response = client.post("/genres", json={"name": name})
    assert response.status_code == 201
    return response.json()


def _create_movie(
    client: TestClient,
    *,
    title: str,
    description: str,
    release_year: int,
    language: str,
    genre_ids: list[int],
) -> dict:
    response = client.post(
        "/movies",
        json={
            "title": title,
            "description": description,
            "release_year": release_year,
            "duration_minutes": 100,
            "poster_url": f"https://example.com/posters/{title.lower().replace(' ', '-')}.jpg",
            "trailer_url": f"https://example.com/trailers/{title.lower().replace(' ', '-')}",
            "maturity_rating": "PG-13",
            "language": language,
            "genre_ids": genre_ids,
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def reset_test_state():
    _reset_tables()
    yield
    _reset_tables()


@pytest.fixture
def user_client(monkeypatch, reset_test_state):
    user = _create_user("ai-user", "ai-user@example.com")
    client = _build_client(monkeypatch, user)
    yield client, user
    client.close()


@pytest.fixture
def admin_client(monkeypatch, reset_test_state):
    admin = _create_user("admin-user", "admin@example.com", is_admin=True)
    client = _build_client(monkeypatch, admin)
    yield client, admin
    client.close()


def test_recommendations_and_home(user_client) -> None:
    client, _ = user_client
    comedy = _create_genre(client, "Comedy")
    sci_fi = _create_genre(client, "Sci-Fi")
    drama = _create_genre(client, "Drama")

    favorite_movie = _create_movie(
        client,
        title="Orbital Mischief",
        description="A funny science fiction rescue mission spirals into a found-family adventure.",
        release_year=2024,
        language="English",
        genre_ids=[comedy["id"], sci_fi["id"]],
    )
    recommended_movie = _create_movie(
        client,
        title="Nebula Weekend",
        description="A group of engineers turns a stalled station into the galaxy's strangest comedy club.",
        release_year=2025,
        language="English",
        genre_ids=[comedy["id"], sci_fi["id"]],
    )
    _create_movie(
        client,
        title="Quiet Current",
        description="A grounded family drama about rebuilding trust after a coastal blackout.",
        release_year=2023,
        language="English",
        genre_ids=[drama["id"]],
    )

    assert client.post(f"/favorites/{favorite_movie['id']}").status_code == 201
    assert client.post(f"/movies/{favorite_movie['id']}/rating", json={"rating": 5}).status_code == 201
    assert client.post(f"/watchlist/{favorite_movie['id']}").status_code == 201

    recommendations = client.get("/recommendations")
    assert recommendations.status_code == 200
    payload = recommendations.json()
    assert payload["recommended_movies"]
    assert payload["recommended_movies"][0]["id"] == recommended_movie["id"]
    assert payload["recommended_genres"]
    assert payload["reason_for_recommendation"]

    home = client.get("/home")
    assert home.status_code == 200
    home_payload = home.json()
    assert home_payload["recommended"]
    assert home_payload["trending"]
    assert home_payload["popular_genres"]


def test_continue_watching_and_completion(user_client) -> None:
    client, _ = user_client
    action = _create_genre(client, "Action")
    movie = _create_movie(
        client,
        title="Redline Echo",
        description="An elite courier fights through a citywide lockdown to deliver evidence before dawn.",
        release_year=2026,
        language="English",
        genre_ids=[action["id"]],
    )

    created = client.post(f"/movies/{movie['id']}/progress", json={"progress_percentage": 35})
    assert created.status_code == 201
    assert created.json()["progress_percentage"] == 35

    listed = client.get("/continue-watching")
    assert listed.status_code == 200
    assert listed.json()[0]["movie"]["id"] == movie["id"]

    updated = client.put(f"/movies/{movie['id']}/progress", json={"progress_percentage": 82})
    assert updated.status_code == 200
    assert updated.json()["progress_percentage"] == 82

    completed = client.put(f"/movies/{movie['id']}/progress", json={"progress_percentage": 100})
    assert completed.status_code == 200
    assert completed.json()["completed"] is True
    assert client.get("/continue-watching").json() == []


def test_ai_search_and_summary_cache(user_client) -> None:
    client, _ = user_client
    comedy = _create_genre(client, "Comedy")
    sci_fi = _create_genre(client, "Sci-Fi")

    movie = _create_movie(
        client,
        title="Cosmic Punchline",
        description="A funny science fiction caper follows a washed-up pilot and an android comic on tour across the outer colonies.",
        release_year=2022,
        language="English",
        genre_ids=[comedy["id"], sci_fi["id"]],
    )

    search = client.post("/search/ai", json={"query": "Funny science fiction movies from the 2020s"})
    assert search.status_code == 200
    search_payload = search.json()
    assert search_payload["matching_movies"]
    assert search_payload["matching_movies"][0]["id"] == movie["id"]
    assert search_payload["reasoning"]
    assert search_payload["confidence"] > 0

    summary_first = client.get(f"/movies/{movie['id']}/summary")
    assert summary_first.status_code == 200
    first_payload = summary_first.json()
    assert first_payload["movie_id"] == movie["id"]
    assert first_payload["main_themes"]

    summary_second = client.get(f"/movies/{movie['id']}/summary")
    assert summary_second.status_code == 200
    second_payload = summary_second.json()
    assert second_payload["generated_at"] == first_payload["generated_at"]

    with SessionLocal() as db:
        summaries = db.scalars(select(MovieSummary).where(MovieSummary.movie_id == movie["id"])).all()
        assert len(summaries) == 1


def test_trending_endpoint(user_client) -> None:
    client, _ = user_client
    horror = _create_genre(client, "Horror")
    movie = _create_movie(
        client,
        title="Night Relay",
        description="A late-night radio host uncovers a pattern inside emergency broadcasts across the desert.",
        release_year=2025,
        language="English",
        genre_ids=[horror["id"]],
    )

    assert client.post(f"/favorites/{movie['id']}").status_code == 201
    assert client.post(f"/watchlist/{movie['id']}").status_code == 201
    assert client.post(f"/movies/{movie['id']}/rating", json={"rating": 5}).status_code == 201
    assert (
        client.post(
            f"/movies/{movie['id']}/reviews",
            json={
                "title": "Excellent tension",
                "body": "The radio format keeps the suspense tight while the mystery escalates with every call.",
                "rating": 5,
            },
        ).status_code
        == 201
    )

    trending = client.get("/movies/trending")
    assert trending.status_code == 200
    assert trending.json()[0]["id"] == movie["id"]


def test_admin_endpoints_and_permissions(user_client, admin_client) -> None:
    user_client_instance, _ = user_client
    admin_client_instance, _ = admin_client

    animation = _create_genre(user_client_instance, "Animation")
    movie = _create_movie(
        user_client_instance,
        title="Paper Satellites",
        description="Young inventors build a cardboard observatory and discover a pattern in the night sky.",
        release_year=2021,
        language="English",
        genre_ids=[animation["id"]],
    )

    forbidden = user_client_instance.delete("/admin/recommendations/cache")
    assert forbidden.status_code == 403

    assert admin_client_instance.post(f"/favorites/{movie['id']}").status_code == 201

    recompute = admin_client_instance.post("/admin/recommendations/recompute")
    assert recompute.status_code == 200

    regenerate = admin_client_instance.post(f"/movies/{movie['id']}/summary/regenerate")
    assert regenerate.status_code == 200
    assert regenerate.json()["movie_id"] == movie["id"]

    cleared = admin_client_instance.delete("/admin/recommendations/cache")
    assert cleared.status_code == 200
    assert "Cleared" in cleared.json()["detail"]
