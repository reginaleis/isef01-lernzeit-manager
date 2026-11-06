
from fastapi.testclient import TestClient
from isef01_lernzeit_manager.main import app

def test_health_check():
    with TestClient(app) as client:
        response = client.get("/api/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}