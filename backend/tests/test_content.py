from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text

from app.core.auth import get_current_user
from app.db.base import Base, register_models
from app.db.database import engine
from app.db.session import SessionLocal
from app.models.activity_event import ActivityEvent
from app.models.genre import Genre
from app.models.movie import Movie
from app.models.movie_genre import MovieGenre
from app.models.notification import Notification
from app.models.user import User
from app import main
from app.services.content_seed import _replace_placeholder_playback_urls


@contextmanager
def no_op_lifespan(_: object):
    yield


def _reset_content_tables() -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                "TRUNCATE TABLE activity_events, notifications, movie_genres, movies, genres "
                "RESTART IDENTITY CASCADE"
            )
        )


def _build_client(monkeypatch) -> TestClient:
    monkeypatch.setattr(main, "lifespan", no_op_lifespan)
    app = main.create_app()
    app.dependency_overrides[get_current_user] = lambda: User(
        email="tester@example.com",
        username="tester",
        hashed_password="not-used",
    )
    return TestClient(app)


def setup_module() -> None:
    register_models()
    Base.metadata.create_all(bind=engine)


@pytest.fixture
def client(monkeypatch):
    _reset_content_tables()
    client = _build_client(monkeypatch)
    yield client
    client.close()
    _reset_content_tables()


def test_genre_crud(client: TestClient) -> None:
    created = client.post("/genres", json={"name": "Thriller"})
    assert created.status_code == 201
    genre = created.json()
    assert genre["name"] == "Thriller"

    listed = client.get("/genres")
    assert listed.status_code == 200
    assert listed.json() == [genre]

    updated = client.put(f"/genres/{genre['id']}", json={"name": "Mystery"})
    assert updated.status_code == 200
    assert updated.json()["name"] == "Mystery"

    deleted = client.delete(f"/genres/{genre['id']}")
    assert deleted.status_code == 204

    final_list = client.get("/genres")
    assert final_list.status_code == 200
    assert final_list.json() == []


def test_movie_crud(client: TestClient) -> None:
    action = client.post("/genres", json={"name": "Action CRUD"}).json()
    drama = client.post("/genres", json={"name": "Drama CRUD"}).json()

    payload = {
        "title": "Skyline Pursuit",
        "description": "An elite pilot and an investigative reporter race to expose a smuggling ring above the Pacific coast.",
        "release_year": 2026,
        "duration_minutes": 117,
        "poster_url": "https://example.com/posters/skyline-pursuit.jpg",
        "trailer_url": "https://example.com/trailers/skyline-pursuit",
        "maturity_rating": "PG-13",
        "language": "English",
        "genre_ids": [action["id"], drama["id"]],
    }
    created = client.post("/movies", json=payload)
    assert created.status_code == 201
    movie = created.json()
    assert movie["title"] == payload["title"]
    assert [genre["name"] for genre in movie["genres"]] == ["Action CRUD", "Drama CRUD"]

    fetched = client.get(f"/movies/{movie['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == movie["id"]

    updated = client.put(
        f"/movies/{movie['id']}",
        json={
            "language": "Spanish",
            "genre_ids": [drama["id"]],
            "duration_minutes": 120,
        },
    )
    assert updated.status_code == 200
    updated_movie = updated.json()
    assert updated_movie["language"] == "Spanish"
    assert updated_movie["duration_minutes"] == 120
    assert [genre["name"] for genre in updated_movie["genres"]] == ["Drama CRUD"]

    deleted = client.delete(f"/movies/{movie['id']}")
    assert deleted.status_code == 204
    assert client.get(f"/movies/{movie['id']}").status_code == 404


def test_movie_search_and_filters(client: TestClient) -> None:
    sci_fi_name = "Sci-Fi Search"
    comedy_name = "Comedy Search"
    sci_fi = client.post("/genres", json={"name": sci_fi_name}).json()
    comedy = client.post("/genres", json={"name": comedy_name}).json()

    movies = [
        {
            "title": "Solar Drift",
            "description": "A cargo crew on a failing solar sail finds a way home by trusting a disgraced navigator.",
            "release_year": 2025,
            "duration_minutes": 109,
            "poster_url": "https://example.com/posters/solar-drift.jpg",
            "trailer_url": "https://example.com/trailers/solar-drift",
            "maturity_rating": "PG-13",
            "language": "English",
            "genre_ids": [sci_fi["id"]],
        },
        {
            "title": "Lunar Laughs",
            "description": "A moon-base maintenance crew turns a catastrophic systems failure into the strangest comedy show in orbit.",
            "release_year": 2024,
            "duration_minutes": 101,
            "poster_url": "https://example.com/posters/lunar-laughs.jpg",
            "trailer_url": "https://example.com/trailers/lunar-laughs",
            "maturity_rating": "PG",
            "language": "English",
            "genre_ids": [comedy["id"], sci_fi["id"]],
        },
        {
            "title": "Harbor Lights",
            "description": "A struggling harbor musician reconnects with his family after an unexpected local radio hit.",
            "release_year": 2022,
            "duration_minutes": 97,
            "poster_url": "https://example.com/posters/harbor-lights.jpg",
            "trailer_url": "https://example.com/trailers/harbor-lights",
            "maturity_rating": "PG",
            "language": "Spanish",
            "genre_ids": [comedy["id"]],
        },
    ]
    for payload in movies:
        assert client.post("/movies", json=payload).status_code == 201

    searched = client.get("/movies", params={"search": "lunar"})
    assert searched.status_code == 200
    searched_items = searched.json()["items"]
    assert [movie["title"] for movie in searched_items] == ["Lunar Laughs"]

    filtered = client.get("/movies", params={"genre": sci_fi_name, "language": "English"})
    assert filtered.status_code == 200
    filtered_titles = [movie["title"] for movie in filtered.json()["items"]]
    assert filtered_titles == ["Lunar Laughs", "Solar Drift"]


def test_movie_pagination(client: TestClient) -> None:
    genre = client.post("/genres", json={"name": "Documentary"}).json()
    for index in range(12):
        response = client.post(
            "/movies",
            json={
                "title": f"Archive Story {index:02d}",
                "description": f"Documentary entry number {index:02d} follows a local archive as it preserves community memory for future generations.",
                "release_year": 2010 + index,
                "duration_minutes": 80 + index,
                "poster_url": f"https://example.com/posters/archive-story-{index:02d}.jpg",
                "trailer_url": f"https://example.com/trailers/archive-story-{index:02d}",
                "maturity_rating": "PG",
                "language": "English",
                "genre_ids": [genre["id"]],
            },
        )
        assert response.status_code == 201

    page_two = client.get(
        "/movies",
        params={"page": 2, "page_size": 5, "sort_by": "release_year", "sort_order": "desc"},
    )
    assert page_two.status_code == 200
    payload = page_two.json()
    assert payload["total"] == 12
    assert payload["page"] == 2
    assert payload["page_size"] == 5
    assert payload["total_pages"] == 3
    assert len(payload["items"]) == 5
    assert payload["items"][0]["release_year"] == 2016


def test_seed_playback_repair_updates_only_legacy_placeholders(client: TestClient) -> None:
    entries = [
        Movie(
            title="Neon Horizon",
            description="A legacy seeded movie used to verify legal sample playback URL repair.",
            release_year=2025,
            duration_minutes=100,
            poster_url="https://example.com/posters/neon.jpg",
            trailer_url="https://example.com/trailers/neon-horizon",
            maturity_rating="PG",
            language="English",
        ),
        Movie(
            title="After the Silence",
            description="A legacy seeded movie used to verify legal sample playback URL repair.",
            release_year=2025,
            duration_minutes=100,
            poster_url="https://example.com/posters/silence.jpg",
            trailer_url="https://example.com/trailers/after-the-silence",
            maturity_rating="PG",
            language="English",
        ),
        Movie(
            title="Paper Planets",
            description="A curated movie URL must not be replaced by the seed repair.",
            release_year=2025,
            duration_minutes=100,
            poster_url="https://example.com/posters/planets.jpg",
            trailer_url="https://example.org/custom-preview.mp4",
            maturity_rating="PG",
            language="English",
        ),
    ]
    with SessionLocal() as db:
        db.add_all(entries)
        db.commit()

        assert _replace_placeholder_playback_urls(db) is True
        db.commit()

        urls = {
            movie.title: movie.trailer_url
            for movie in db.scalars(select(Movie).where(Movie.title.in_([entry.title for entry in entries]))).all()
        }

    assert urls["Neon Horizon"].endswith("flower.mp4")
    assert urls["After the Silence"].endswith("sintel/trailer.mp4")
    assert urls["Paper Planets"] == "https://example.org/custom-preview.mp4"
