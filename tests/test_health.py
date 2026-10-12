
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_health_check_returns_success():
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "nexus-api",
        "version": "0.1.0",
    }
