
from fastapi.testclient import TestClient
from isef01_lernzeit_manager.main import app


def test_lernzeit_erfolgreich_erstellen():
    with TestClient(app) as client:
        response = client.post(
            "/api/lernzeiten/",
            json={
                "duration": 30,
                "status": "abgeschlossen"
            }
        )

    assert response.status_code == 201
    assert response.json()["duration"] == 30
    assert response.json()["status"] == "abgeschlossen"
    assert "id" in response.json()


def test_alle_lernzeiten_abrufen():
    with TestClient(app) as client:
        response = client.get("/api/lernzeiten/")

    assert response.status_code == 200
    assert response.json() == []


def test_nicht_vorhandene_lernzeit_abrufen():
    with TestClient(app) as client:
        response = client.get("/api/lernzeiten/99999")

    assert response.status_code == 404


def test_lernzeit_erstellen_und_abrufen():
    with TestClient(app) as client:
        created = client.post(
            "/api/lernzeiten/",
            json={"duration": 45, "status": "abgeschlossen"}
        )
        assert created.status_code == 201

        lernzeit_id = created.json()["id"]
        response = client.get(f"/api/lernzeiten/{lernzeit_id}")

    assert response.status_code == 200
    assert response.json()["id"] == lernzeit_id
    assert response.json()["duration"] == 45


def test_lernzeit_bearbeiten():
    with TestClient(app) as client:
        created = client.post(
            "/api/lernzeiten/",
            json={"duration": 30, "status": "geplant"}
        )
        assert created.status_code == 201
        lernzeit_id = created.json()["id"]

        response = client.put(
            f"/api/lernzeiten/{lernzeit_id}",
            json={"duration": 60, "status": "abgeschlossen"}
        )

    assert response.status_code == 200
    assert response.json()["duration"] == 60
    assert response.json()["status"] == "abgeschlossen"


def test_lernzeit_loeschen():
    with TestClient(app) as client:
        created = client.post(
            "/api/lernzeiten/",
            json={"duration": 30}
        )
        assert created.status_code == 201
        lernzeit_id = created.json()["id"]

        deleted = client.delete(f"/api/lernzeiten/{lernzeit_id}")
        response = client.get(f"/api/lernzeiten/{lernzeit_id}")

    assert deleted.status_code == 200
    assert response.status_code == 404


def test_lernzeit_mit_negativer_dauer():
    with TestClient(app) as client:
        response = client.post(
            "/api/lernzeiten/",
            json={"duration": -30}
        )

    assert response.status_code == 422


def test_lernzeit_mit_ungueltiger_lernziel_id():
    with TestClient(app) as client:
        response = client.post(
            "/api/lernzeiten/",
            json={
                "duration": 30,
                "lernziel_id": 99999
            }
        )

    assert response.status_code == 404
