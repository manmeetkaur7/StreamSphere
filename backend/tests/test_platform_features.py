import json
from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient
from redis.exceptions import RedisError

from app import main
from app.core.config import get_settings
from app.db.session import get_db
from app.services.cache import CacheService, InMemoryCacheBackend, reset_runtime_services

_NO_OVERRIDE = object()


@contextmanager
def no_op_lifespan(_: object):
    yield


@pytest.fixture(autouse=True)
def reset_runtime_state():
    get_settings.cache_clear()
    reset_runtime_services()
    yield
    get_settings.cache_clear()
    reset_runtime_services()


def _build_app(monkeypatch, *, db_override=_NO_OVERRIDE):
    monkeypatch.setattr(main, "lifespan", no_op_lifespan)
    app = main.create_app()
    if db_override is not _NO_OVERRIDE:
        app.dependency_overrides[get_db] = lambda: db_override
    return app


def test_health_endpoint_reports_dependency_details(monkeypatch) -> None:
    app = _build_app(monkeypatch, db_override=object())
    monkeypatch.setattr(
        "app.api.health.application_health",
        lambda _db: {
            "status": "ok",
            "environment": "test",
            "version": "1.2.3",
            "uptime_seconds": 42,
            "database": {
                "status": "ok",
                "backend": "postgresql",
                "detail": "Database connection succeeded.",
            },
            "redis": {
                "status": "ok",
                "backend": "redis",
                "detail": "Redis cache is available.",
            },
        },
    )

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["environment"] == "test"
    assert payload["version"] == "1.2.3"
    assert payload["database"]["status"] == "ok"
    assert payload["redis"]["backend"] == "redis"
    client.close()


def test_health_endpoint_returns_503_for_required_dependency_failure(monkeypatch) -> None:
    app = _build_app(monkeypatch, db_override=object())
    monkeypatch.setattr(
        "app.api.health.application_health",
        lambda _db: {
            "status": "unavailable",
            "environment": "test",
            "version": "1.2.3",
            "uptime_seconds": 7,
            "database": {
                "status": "unavailable",
                "backend": "postgresql",
                "detail": "Database connection failed.",
            },
            "redis": {
                "status": "degraded",
                "backend": "memory",
                "detail": "Redis unavailable; using fallback.",
            },
        },
    )

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 503
    assert response.json()["status"] == "unavailable"
    client.close()


def test_cache_service_falls_back_to_in_memory_when_primary_backend_fails() -> None:
    class BrokenBackend:
        backend_name = "redis"

        def get(self, _key: str) -> str | None:
            raise RedisError("redis down")

        def set(self, _key: str, _value: str, _ttl_seconds: int) -> None:
            raise RedisError("redis down")

        def delete(self, _key: str) -> None:
            raise RedisError("redis down")

        def ping(self) -> bool:
            raise RedisError("redis down")

    cache = CacheService(primary_backend=BrokenBackend(), fallback_backend=InMemoryCacheBackend())

    cache.set_json("summary", {"status": "cached"}, ttl_seconds=30)

    assert cache.get_json("summary") == {"status": "cached"}
    assert cache.backend_name == "memory"


def test_rate_limit_blocks_requests_over_threshold(monkeypatch) -> None:
    monkeypatch.setenv("RATE_LIMIT_REQUESTS", "2")
    monkeypatch.setenv("RATE_LIMIT_WINDOW_SECONDS", "60")
    app = _build_app(monkeypatch)

    @app.get("/limited")
    def limited() -> dict[str, str]:
        return {"status": "ok"}

    client = TestClient(app)
    assert client.get("/limited").status_code == 200
    assert client.get("/limited").status_code == 200
    blocked = client.get("/limited")

    assert blocked.status_code == 429
    assert blocked.json()["detail"] == "Rate limit exceeded. Please retry shortly."
    client.close()


def test_rate_limit_headers_are_exposed(monkeypatch) -> None:
    monkeypatch.setenv("RATE_LIMIT_REQUESTS", "3")
    monkeypatch.setenv("RATE_LIMIT_WINDOW_SECONDS", "60")
    app = _build_app(monkeypatch)

    @app.get("/headers-check")
    def headers_check() -> dict[str, str]:
        return {"status": "ok"}

    client = TestClient(app)
    response = client.get("/headers-check")

    assert response.status_code == 200
    assert response.headers["x-ratelimit-limit"] == "3"
    assert response.headers["x-ratelimit-remaining"] == "2"
    client.close()


def test_structured_logging_emits_json_request_log(monkeypatch, caplog) -> None:
    app = _build_app(monkeypatch)

    @app.get("/logging-check")
    def logging_check() -> dict[str, str]:
        return {"status": "ok"}

    client = TestClient(app)
    with caplog.at_level("INFO", logger="streamsphere.request"):
        response = client.get("/logging-check")

    assert response.status_code == 200
    assert "x-request-id" in response.headers

    log_record = next(record for record in caplog.records if record.name == "streamsphere.request")
    payload = json.loads(log_record.message)
    assert payload["event"] == "http_request"
    assert payload["path"] == "/logging-check"
    assert payload["status_code"] == 200
    client.close()


def test_openapi_contains_production_metadata(monkeypatch) -> None:
    app = _build_app(monkeypatch)
    client = TestClient(app)

    response = client.get("/openapi.json")

    assert response.status_code == 200
    payload = response.json()
    assert payload["info"]["title"] == "StreamSphere API"
    assert "AI-assisted discovery" in payload["info"]["description"]
    assert {tag["name"] for tag in payload["tags"]} >= {"health", "admin", "search"}
    client.close()


def test_movies_trending_route_is_not_shadowed_by_movie_detail(monkeypatch) -> None:
    app = _build_app(monkeypatch)
    client = TestClient(app)

    response = client.get("/movies/trending")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    client.close()
