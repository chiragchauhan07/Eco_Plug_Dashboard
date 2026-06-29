from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health", headers={"Host": "localhost"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Application is running"
    assert "version" in data["data"]


def test_ready_endpoint() -> None:
    response = client.get("/ready", headers={"Host": "localhost"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "All services are ready"
