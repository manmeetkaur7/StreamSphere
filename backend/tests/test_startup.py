from contextlib import contextmanager

from fastapi.testclient import TestClient

from app import main
from app.core.config import Settings


def test_startup_initializes_database(monkeypatch) -> None:
    calls: list[str] = []

    def fake_init_db() -> None:
        calls.append("init_db")

    monkeypatch.setattr(main, "init_db", fake_init_db)

    app = main.create_app()
    with TestClient(app):
        pass

    assert calls == ["init_db"]


def test_unhandled_exceptions_return_json_500(monkeypatch) -> None:
    @contextmanager
    def no_op_lifespan(_: object):
        yield

    monkeypatch.setattr(main, "lifespan", no_op_lifespan)

    app = main.create_app()

    @app.get("/boom")
    def boom() -> None:
        raise RuntimeError("boom")

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/boom")

    assert response.status_code == 500
    payload = response.json()
    assert payload["detail"] == "Internal Server Error"
    assert payload["error"]["code"] == "internal_server_error"


def test_production_settings_reject_insecure_defaults(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/streamsphere")
    monkeypatch.setenv("JWT_SECRET_KEY", "change-this-secret-in-production")
    monkeypatch.setenv("ALLOWED_ORIGINS", "*")

    try:
        Settings()
    except RuntimeError as exc:
        assert "Invalid production configuration" in str(exc)
    else:
        raise AssertionError("Expected insecure production settings to be rejected.")


def test_production_settings_accept_explicit_configuration(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:secret@db.example/streamsphere")
    monkeypatch.setenv("JWT_SECRET_KEY", "a-unique-production-secret")
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://app.example.com")
    monkeypatch.setenv("AI_PROVIDER", "mock")

    settings = Settings()

    assert settings.allowed_origins == ("https://app.example.com",)


def test_production_settings_require_explicit_origins(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:secret@db.example/streamsphere")
    monkeypatch.setenv("JWT_SECRET_KEY", "a-unique-production-secret")
    monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)

    try:
        Settings()
    except RuntimeError as exc:
        assert "ALLOWED_ORIGINS" in str(exc)
    else:
        raise AssertionError("Expected production origins to require explicit configuration.")
