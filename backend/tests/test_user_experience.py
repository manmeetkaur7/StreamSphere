import uuid
from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app import main
from app.core.auth import get_current_user
from app.db.base import Base, register_models
from app.db.database import engine
from app.db.session import SessionLocal
from app.models.favorite import Favorite
from app.models.activity_event import ActivityEvent
from app.models.genre import Genre
from app.models.movie import Movie
from app.models.movie_genre import MovieGenre
from app.models.notification import Notification
from app.models.rating import Rating
from app.models.recommendation_cache import RecommendationCache
from app.models.review import Review
from app.models.user import User
from app.models.watch_progress import WatchProgress
from app.models.watchlist import Watchlist


@contextmanager
def no_op_lifespan(_: object):
    yield


def setup_module() -> None:
    register_models()
    Base.metadata.create_all(bind=engine)


def _reset_tables() -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                "TRUNCATE TABLE activity_events, notifications, watch_progress, recommendation_cache, "
                "watchlists, favorites, ratings, reviews, movie_genres, movies, genres, users "
                "RESTART IDENTITY CASCADE"
            )
        )


def _create_user(username: str, email: str) -> User:
    with SessionLocal() as db:
        user = User(
            id=uuid.uuid4(),
            username=username,
            email=email,
            hashed_password="hashed-password",
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
    return TestClient(app)


def _create_movie(client: TestClient, genre_name: str = "Drama") -> dict:
    genre = client.post("/genres", json={"name": genre_name})
    assert genre.status_code == 201
    genre_id = genre.json()["id"]
    response = client.post(
        "/movies",
        json={
            "title": "Signal Harbor",
            "description": "A former coast guard navigator returns to her hometown and uncovers a conspiracy hidden inside the harbor traffic grid.",
            "release_year": 2026,
            "duration_minutes": 112,
            "poster_url": "https://example.com/posters/signal-harbor.jpg",
            "trailer_url": "https://example.com/trailers/signal-harbor",
            "maturity_rating": "PG-13",
            "language": "English",
            "genre_ids": [genre_id],
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def user_client(monkeypatch):
    _reset_tables()
    user = _create_user("tester", "tester@example.com")
    client = _build_client(monkeypatch, user)
    yield client, user
    client.close()
    _reset_tables()


@pytest.fixture
def secondary_user(monkeypatch):
    user = _create_user("reviewer", "reviewer@example.com")
    client = _build_client(monkeypatch, user)
    yield client, user
    client.close()


def test_watchlist_crud(user_client) -> None:
    client, _ = user_client
    movie = _create_movie(client)

    added = client.post(f"/watchlist/{movie['id']}")
    assert added.status_code == 201
    payload = added.json()
    assert payload["movie"]["id"] == movie["id"]

    duplicate = client.post(f"/watchlist/{movie['id']}")
    assert duplicate.status_code == 409

    listed = client.get("/watchlist")
    assert listed.status_code == 200
    items = listed.json()
    assert len(items) == 1
    assert items[0]["movie"]["title"] == movie["title"]

    deleted = client.delete(f"/watchlist/{movie['id']}")
    assert deleted.status_code == 204
    assert client.get("/watchlist").json() == []


def test_favorites_crud(user_client) -> None:
    client, _ = user_client
    movie = _create_movie(client)

    added = client.post(f"/favorites/{movie['id']}")
    assert added.status_code == 201
    assert added.json()["movie"]["id"] == movie["id"]

    duplicate = client.post(f"/favorites/{movie['id']}")
    assert duplicate.status_code == 409

    listed = client.get("/favorites")
    assert listed.status_code == 200
    assert listed.json()[0]["movie"]["title"] == movie["title"]

    deleted = client.delete(f"/favorites/{movie['id']}")
    assert deleted.status_code == 204
    assert client.get("/favorites").json() == []


def test_ratings_update_movie_aggregates(user_client) -> None:
    client, _ = user_client
    movie = _create_movie(client)

    created = client.post(f"/movies/{movie['id']}/rating", json={"rating": 4})
    assert created.status_code == 201
    assert created.json()["rating"] == 4

    movie_after_create = client.get(f"/movies/{movie['id']}")
    assert movie_after_create.status_code == 200
    assert movie_after_create.json()["average_rating"] == 4.0
    assert movie_after_create.json()["total_ratings"] == 1

    updated = client.put(f"/movies/{movie['id']}/rating", json={"rating": 5})
    assert updated.status_code == 200
    assert updated.json()["rating"] == 5

    movie_after_update = client.get(f"/movies/{movie['id']}")
    assert movie_after_update.json()["average_rating"] == 5.0
    assert movie_after_update.json()["total_ratings"] == 1

    deleted = client.delete(f"/movies/{movie['id']}/rating")
    assert deleted.status_code == 204
    movie_after_delete = client.get(f"/movies/{movie['id']}")
    assert movie_after_delete.json()["average_rating"] == 0.0
    assert movie_after_delete.json()["total_ratings"] == 0


def test_reviews_crud_and_listing(user_client) -> None:
    client, _ = user_client
    movie = _create_movie(client)

    created = client.post(
        f"/movies/{movie['id']}/reviews",
        json={
            "title": "Strong comeback story",
            "body": "The harbor setting and grounded pacing make the mystery feel lived in and personal throughout.",
            "rating": 4,
        },
    )
    assert created.status_code == 201
    review = created.json()
    assert review["movie_id"] == movie["id"]

    listed = client.get(f"/movies/{movie['id']}/reviews")
    assert listed.status_code == 200
    assert listed.json()[0]["title"] == "Strong comeback story"

    updated = client.put(
        f"/reviews/{review['id']}",
        json={"title": "Excellent comeback story", "rating": 5},
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Excellent comeback story"
    assert updated.json()["rating"] == 5

    movie_after_review = client.get(f"/movies/{movie['id']}")
    assert movie_after_review.json()["review_count"] == 1

    deleted = client.delete(f"/reviews/{review['id']}")
    assert deleted.status_code == 204
    assert client.get(f"/movies/{movie['id']}/reviews").json() == []


def test_profile_endpoint(user_client) -> None:
    client, user = user_client
    movie = _create_movie(client)

    assert client.post(f"/watchlist/{movie['id']}").status_code == 201
    assert client.post(f"/favorites/{movie['id']}").status_code == 201
    assert client.post(f"/movies/{movie['id']}/rating", json={"rating": 4}).status_code == 201
    assert (
        client.post(
            f"/movies/{movie['id']}/reviews",
            json={
                "title": "Thoughtful thriller",
                "body": "It keeps the personal stakes in focus while still delivering a satisfying conspiracy plot.",
                "rating": 4,
            },
        ).status_code
        == 201
    )

    response = client.get("/profile")
    assert response.status_code == 200
    payload = response.json()
    assert payload["username"] == user.username
    assert payload["email"] == user.email
    assert payload["favorite_count"] == 1
    assert payload["watchlist_count"] == 1
    assert payload["review_count"] == 1
    assert payload["average_rating_given"] == 4.0
    assert payload["favorite_movies"][0]["id"] == movie["id"]
    assert payload["watchlist_movies"][0]["id"] == movie["id"]
    assert payload["recent_reviews"][0]["movie_title"] == movie["title"]


def test_review_permission_checks(user_client, secondary_user) -> None:
    primary_client, _ = user_client
    secondary_client, _ = secondary_user
    movie = _create_movie(primary_client)

    review = primary_client.post(
        f"/movies/{movie['id']}/reviews",
        json={
            "title": "Owner review",
            "body": "This review should only be editable and removable by the user who created it.",
            "rating": 3,
        },
    ).json()

    forbidden_update = secondary_client.put(
        f"/reviews/{review['id']}",
        json={"title": "Hijacked review"},
    )
    assert forbidden_update.status_code == 403

    forbidden_delete = secondary_client.delete(f"/reviews/{review['id']}")
    assert forbidden_delete.status_code == 403
