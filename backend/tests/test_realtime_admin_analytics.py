import uuid
from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text
from starlette.websockets import WebSocketDisconnect

from app import main
from app.core.security import create_access_token, hash_password
from app.db.base import Base, ensure_schema_compatibility, register_models
from app.db.database import engine
from app.db.session import SessionLocal
from app.models.activity_event import ActivityEvent
from app.models.notification import Notification
from app.models.user import User
from app.services.activity_service import record_activity


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


def _create_user(
    username: str,
    email: str,
    *,
    is_admin: bool = False,
    is_active: bool = True,
    password: str = "Password123!",
) -> User:
    with SessionLocal() as db:
        user = User(
            id=uuid.uuid4(),
            username=username,
            email=email,
            hashed_password=hash_password(password),
            is_admin=is_admin,
            is_active=is_active,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        db.expunge(user)
        return user


def _auth_headers(user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(str(user.id))}"}


def _build_client(monkeypatch) -> TestClient:
    monkeypatch.setattr(main, "lifespan", no_op_lifespan)
    return TestClient(main.create_app())


def _create_genre(client: TestClient, headers: dict[str, str], name: str) -> dict:
    response = client.post("/genres", json={"name": name}, headers=headers)
    assert response.status_code == 201
    return response.json()


def _create_movie(client: TestClient, headers: dict[str, str], genre_ids: list[int], *, title: str = "Signal Drift") -> dict:
    response = client.post(
        "/movies",
        json={
            "title": title,
            "description": "A grounded sci-fi drama about a rescue signal that changes every listener who decodes it.",
            "release_year": 2026,
            "duration_minutes": 112,
            "poster_url": f"https://example.com/posters/{title.lower().replace(' ', '-')}.jpg",
            "trailer_url": f"https://example.com/trailers/{title.lower().replace(' ', '-')}",
            "maturity_rating": "PG-13",
            "language": "English",
            "genre_ids": genre_ids,
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def client(monkeypatch):
    _reset_tables()
    test_client = _build_client(monkeypatch)
    yield test_client
    test_client.close()
    _reset_tables()


def test_notifications_are_scoped_to_the_authenticated_user(client: TestClient) -> None:
    owner = _create_user("owner", "owner@example.com")
    other = _create_user("other", "other@example.com")

    with SessionLocal() as db:
        db.add_all(
            [
                Notification(user_id=owner.id, type="system_notification", title="Owner note", message="Only for owner."),
                Notification(user_id=other.id, type="system_notification", title="Other note", message="Only for other."),
            ]
        )
        db.commit()

    response = client.get("/notifications", headers=_auth_headers(owner))

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["title"] == "Owner note"


def test_notification_read_all_and_delete_behaviour(client: TestClient) -> None:
    user = _create_user("reader", "reader@example.com")

    with SessionLocal() as db:
        db.add_all(
            [
                Notification(user_id=user.id, type="system_notification", title="One", message="First"),
                Notification(user_id=user.id, type="review_interaction", title="Two", message="Second"),
            ]
        )
        db.commit()

    headers = _auth_headers(user)
    unread = client.get("/notifications/unread-count", headers=headers)
    assert unread.status_code == 200
    assert unread.json()["unread_count"] == 2

    listed = client.get("/notifications", headers=headers)
    notification_id = listed.json()[0]["id"]

    read_one = client.put(f"/notifications/{notification_id}/read", headers=headers)
    assert read_one.status_code == 200
    assert read_one.json()["is_read"] is True

    read_all = client.put("/notifications/read-all", headers=headers)
    assert read_all.status_code == 200
    assert read_all.json()["unread_count"] == 0

    deleted = client.delete(f"/notifications/{notification_id}", headers=headers)
    assert deleted.status_code == 204
    assert len(client.get("/notifications", headers=headers).json()) == 1


def test_notification_endpoints_enforce_ownership(client: TestClient) -> None:
    owner = _create_user("alpha", "alpha@example.com")
    intruder = _create_user("beta", "beta@example.com")

    with SessionLocal() as db:
        notification = Notification(
            user_id=owner.id,
            type="system_notification",
            title="Private",
            message="Do not expose.",
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        notification_id = notification.id

    response = client.put(f"/notifications/{notification_id}/read", headers=_auth_headers(intruder))

    assert response.status_code == 404


def test_admin_stats_require_admin_and_return_platform_totals(client: TestClient) -> None:
    admin = _create_user("admin", "admin@example.com", is_admin=True)
    member = _create_user("member", "member@example.com")
    headers = _auth_headers(member)
    admin_headers = _auth_headers(admin)

    genre = _create_genre(client, headers, "Thriller")
    movie = _create_movie(client, headers, [genre["id"]], title="Static Harbor")

    assert client.post(f"/favorites/{movie['id']}", headers=headers).status_code == 201
    assert client.post(f"/watchlist/{movie['id']}", headers=headers).status_code == 201
    assert client.post(f"/movies/{movie['id']}/rating", json={"rating": 5}, headers=headers).status_code == 201
    assert (
        client.post(
            f"/movies/{movie['id']}/reviews",
            json={
                "title": "Excellent",
                "body": "The pacing stays sharp while the mystery keeps widening around the harbor.",
                "rating": 5,
            },
            headers=headers,
        ).status_code
        == 201
    )
    assert client.post("/search/ai", json={"query": "thriller harbor movie"}, headers=headers).status_code == 200
    assert client.get("/recommendations", headers=headers).status_code == 200

    forbidden = client.get("/admin/stats", headers=headers)
    assert forbidden.status_code == 403

    response = client.get("/admin/stats", headers=admin_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["total_users"] == 2
    assert payload["total_movies"] == 1
    assert payload["total_reviews"] == 1
    assert payload["total_ratings"] == 1
    assert payload["total_watchlist_entries"] == 1
    assert payload["total_favorites"] == 1
    assert payload["total_ai_searches"] >= 1
    assert payload["total_recommendations_generated"] >= 1


def test_admin_can_deactivate_user_and_inactive_users_cannot_log_in(client: TestClient) -> None:
    admin = _create_user("admin2", "admin2@example.com", is_admin=True)
    member = _create_user("member2", "member2@example.com", password="Password123!")

    update = client.put(
        f"/admin/users/{member.id}/status",
        json={"is_active": False},
        headers=_auth_headers(admin),
    )
    assert update.status_code == 200
    assert update.json()["is_active"] is False

    login = client.post(
        "/auth/login",
        data={"username": member.email, "password": "Password123!"},
    )
    assert login.status_code == 403
    assert login.json()["detail"] == "This account is inactive."


def test_profile_insights_include_activity_and_genre_breakdowns(client: TestClient) -> None:
    user = _create_user("insight", "insight@example.com")
    headers = _auth_headers(user)

    drama = _create_genre(client, headers, "Drama")
    movie = _create_movie(client, headers, [drama["id"]], title="Blue Meridian")

    assert client.get(f"/movies/{movie['id']}", headers=headers).status_code == 200
    assert client.post(f"/favorites/{movie['id']}", headers=headers).status_code == 201
    assert client.post(f"/watchlist/{movie['id']}", headers=headers).status_code == 201
    assert client.post(f"/movies/{movie['id']}/rating", json={"rating": 4}, headers=headers).status_code == 201
    assert (
        client.post(
            f"/movies/{movie['id']}/reviews",
            json={
                "title": "Strong character work",
                "body": "It balances emotional detail with enough momentum to keep the investigation compelling.",
                "rating": 4,
            },
            headers=headers,
        ).status_code
        == 201
    )
    assert client.post(f"/movies/{movie['id']}/progress", json={"progress_percentage": 55}, headers=headers).status_code == 201

    response = client.get("/profile/insights", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["favorite_genres"][0]["name"] == "Drama"
    assert payload["most_viewed_genres"][0]["name"] == "Drama"
    assert payload["movies_in_progress"] == 1
    assert payload["total_reviews"] == 1
    assert {entry["event_type"] for entry in payload["recent_activity"]} >= {
        "movie_view",
        "favorite",
        "watchlist_add",
        "rating",
        "review",
        "progress_update",
    }


def test_platform_analytics_returns_aggregates_for_admin(client: TestClient) -> None:
    admin = _create_user("admin3", "admin3@example.com", is_admin=True)
    member = _create_user("member3", "member3@example.com")
    admin_headers = _auth_headers(admin)
    member_headers = _auth_headers(member)

    sci_fi = _create_genre(client, admin_headers, "Sci-Fi")
    movie = _create_movie(client, admin_headers, [sci_fi["id"]], title="Echo Grid")

    assert client.get(f"/movies/{movie['id']}", headers=member_headers).status_code == 200
    assert client.post(f"/favorites/{movie['id']}", headers=member_headers).status_code == 201
    assert client.post(f"/watchlist/{movie['id']}", headers=member_headers).status_code == 201
    assert client.post(f"/movies/{movie['id']}/rating", json={"rating": 5}, headers=member_headers).status_code == 201
    assert (
        client.post(
            f"/movies/{movie['id']}/reviews",
            json={
                "title": "Sharp and tense",
                "body": "The conspiracy stays readable while the futuristic setting keeps escalating the pressure.",
                "rating": 5,
            },
            headers=member_headers,
        ).status_code
        == 201
    )
    assert client.post("/search/ai", json={"query": "science fiction thrillers"}, headers=member_headers).status_code == 200

    response = client.get("/admin/analytics", headers=admin_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["most_viewed_movies"][0]["movie"]["id"] == movie["id"]
    assert payload["most_favorited_movies"][0]["movie"]["id"] == movie["id"]
    assert payload["most_watchlisted_movies"][0]["movie"]["id"] == movie["id"]
    assert payload["most_reviewed_movies"][0]["movie"]["id"] == movie["id"]
    assert payload["top_rated_movies"][0]["movie"]["id"] == movie["id"]
    assert payload["popular_genres"][0]["name"] == "Sci-Fi"
    assert payload["ai_search_volume"] >= 1
    assert payload["daily_active_users"]


def test_activity_metadata_sanitizes_sensitive_fields() -> None:
    _reset_tables()
    user = _create_user("sanitized", "sanitized@example.com")

    with SessionLocal() as db:
        record_activity(
            db,
            user_id=user.id,
            event_type="ai_search",
            metadata={"query": "safe", "password": "hidden", "token": "secret"},
            commit=True,
        )

    with SessionLocal() as db:
        saved = db.scalar(select(ActivityEvent).where(ActivityEvent.user_id == user.id))
        assert saved is not None
        assert saved.event_metadata["query"] == "safe"
        assert "password" not in saved.event_metadata
        assert "token" not in saved.event_metadata

    _reset_tables()


def test_websocket_rejects_invalid_tokens(client: TestClient) -> None:
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws/notifications?token=invalid-token"):
            pass


def test_websocket_delivers_notification_events(client: TestClient) -> None:
    user = _create_user("socket-user", "socket@example.com")
    headers = _auth_headers(user)
    genre = _create_genre(client, headers, "Adventure")
    movie = _create_movie(client, headers, [genre["id"]], title="North Signal")

    with client.websocket_connect(f"/ws/notifications?token={create_access_token(str(user.id))}") as websocket:
        ready_event = websocket.receive_json()
        assert ready_event["event"] == "notifications.ready"

        response = client.post(
            f"/movies/{movie['id']}/progress",
            json={"progress_percentage": 100},
            headers=headers,
        )
        assert response.status_code == 200

        notification_event = websocket.receive_json()
        assert notification_event["event"] == "notification.created"
        assert notification_event["notification"]["title"] == "Movie completed"
