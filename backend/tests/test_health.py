from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] in {"ok", "degraded"}
    assert payload["environment"]
    assert payload["version"]
    assert isinstance(payload["uptime_seconds"], int)
    assert payload["database"]["status"] == "ok"
    assert payload["redis"]["status"] in {"ok", "degraded"}


def test_cors_allows_frontend_origin() -> None:
    response = client.get(
        "/health",
        headers={"Origin": "http://localhost:3000"},
    )

    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
