from contextlib import contextmanager

from fastapi.testclient import TestClient

from app import main


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
    assert response.json() == {"detail": "Internal Server Error"}
