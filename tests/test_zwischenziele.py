
from fastapi.testclient import TestClient
from isef01_lernzeit_manager.main import app


def test_zwischenziel_erfolgreich_erstellen():
    with TestClient(app) as client:
        # Zuerst ein Lernziel erstellen
        lernziel = client.post(
            "/api/lernziele/",
            json={
                "title": "Datenbanken lernen",
                "module_id": "ISEF01"
            }
        )
        assert lernziel.status_code == 201
        lernziel_id = lernziel.json()["id"]

        # Zwischenziel erstellen
        response = client.post(
            "/api/zwischenziele/",
            json={
                "title": "SQL Grundlagen",
                "lernziel_id": lernziel_id
            }
        )

    assert response.status_code == 201
    assert response.json()["title"] == "SQL Grundlagen"
    assert response.json()["lernziel_id"] == lernziel_id
    assert "id" in response.json()


def test_zwischenziel_erstellen_und_abrufen():
    with TestClient(app) as client:
        lernziel = client.post(
            "/api/lernziele/",
            json={
                "title": "Python lernen",
                "module_id": "ISEF01"
            }
        )
        assert lernziel.status_code == 201

        created = client.post(
            "/api/zwischenziele/",
            json={
                "title": "FastAPI verstehen",
                "lernziel_id": lernziel.json()["id"]
            }
        )
        assert created.status_code == 201

        zwischenziel_id = created.json()["id"]

        response = client.get(
            f"/api/zwischenziele/{zwischenziel_id}"
        )

    assert response.status_code == 200
    assert response.json()["id"] == zwischenziel_id
    assert response.json()["title"] == "FastAPI verstehen"


def test_nicht_vorhandenes_zwischenziel_abrufen():
    with TestClient(app) as client:
        response = client.get("/api/zwischenziele/99999")

    assert response.status_code == 404


def test_zwischenziel_bearbeiten():
    with TestClient(app) as client:
        lernziel = client.post(
            "/api/lernziele/",
            json={"title": "Python lernen", "module_id": "ISEF01"}
        )
        assert lernziel.status_code == 201

        created = client.post(
            "/api/zwischenziele/",
            json={
                "title": "Python Grundlagen",
                "lernziel_id": lernziel.json()["id"]
            }
        )
        assert created.status_code == 201
        zwischenziel_id = created.json()["id"]

        response = client.put(
            f"/api/zwischenziele/{zwischenziel_id}",
            json={"title": "FastAPI Grundlagen", "status": "in_progress"}
        )

    assert response.status_code == 200
    assert response.json()["title"] == "FastAPI Grundlagen"
    assert response.json()["status"] == "in_progress"


def test_zwischenziel_loeschen():
    with TestClient(app) as client:
        lernziel = client.post(
            "/api/lernziele/",
            json={"title": "Datenbanken", "module_id": "ISEF01"}
        )
        assert lernziel.status_code == 201

        created = client.post(
            "/api/zwischenziele/",
            json={
                "title": "SQL lernen",
                "lernziel_id": lernziel.json()["id"]
            }
        )
        assert created.status_code == 201
        zwischenziel_id = created.json()["id"]

        deleted = client.delete(f"/api/zwischenziele/{zwischenziel_id}")
        response = client.get(f"/api/zwischenziele/{zwischenziel_id}")

    assert deleted.status_code == 200
    assert response.status_code == 404


def test_zwischenziel_ohne_titel():
    with TestClient(app) as client:
        response = client.post(
            "/api/zwischenziele/",
            json={"lernziel_id": 1}
        )

    assert response.status_code == 422


def test_zwischenziel_mit_leerem_titel():
    with TestClient(app) as client:
        response = client.post(
            "/api/zwischenziele/",
            json={"title": "", "lernziel_id": 1}
        )

    assert response.status_code == 422


def test_zwischenziel_mit_negativer_lernzeit():
    with TestClient(app) as client:
        response = client.post(
            "/api/zwischenziele/",
            json={
                "title": "SQL lernen",
                "lernziel_id": 1,
                "accumulated_study_time": -30
            }
        )

    assert response.status_code == 422


def test_zwischenziel_mit_ungueltiger_lernziel_id():
    with TestClient(app) as client:
        response = client.post(
            "/api/zwischenziele/",
            json={
                "title": "SQL lernen",
                "lernziel_id": 99999
            }
        )

    assert response.status_code == 404


def test_zwischenziel_mit_ungueltigem_datumsbereich():
    with TestClient(app) as client:
        response = client.post(
            "/api/zwischenziele/",
            json={
                "title": "SQL lernen",
                "lernziel_id": 1,
                "start_date": "2026-11-20",
                "end_date": "2026-11-10"
            }
        )

    assert response.status_code == 422


def test_zwischenziele_nach_lernziel_filtern():
    with TestClient(app) as client:
        lernziel1 = client.post(
            "/api/lernziele/",
            json={"title": "Python", "module_id": "ISEF01"}
        )
        lernziel2 = client.post(
            "/api/lernziele/",
            json={"title": "Datenbanken", "module_id": "ISEF01"}
        )

        assert lernziel1.status_code == 201
        assert lernziel2.status_code == 201

        id1 = lernziel1.json()["id"]
        id2 = lernziel2.json()["id"]

        for title, lernziel_id in [
            ("FastAPI lernen", id1),
            ("SQL lernen", id2)
        ]:
            created = client.post(
                "/api/zwischenziele/",
                json={"title": title, "lernziel_id": lernziel_id}
            )
            assert created.status_code == 201

        response = client.get(
            "/api/zwischenziele/",
            params={"lernziel_id": id1}
        )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "FastAPI lernen"
    assert response.json()[0]["lernziel_id"] == id1


def test_zwischenziele_mit_ungueltigem_datumsfilter():
    with TestClient(app) as client:
        response = client.get(
            "/api/zwischenziele/",
            params={
                "from_date": "2026-11-20",
                "to_date": "2026-11-10"
            }
        )

    assert response.status_code == 400


def test_zwischenziel_mit_lernzeiten_nicht_loeschbar():
    with TestClient(app) as client:
        lernziel = client.post(
            "/api/lernziele/",
            json={"title": "Python lernen", "module_id": "ISEF01"}
        )
        assert lernziel.status_code == 201
        lernziel_id = lernziel.json()["id"]

        zwischenziel = client.post(
            "/api/zwischenziele/",
            json={
                "title": "FastAPI lernen",
                "lernziel_id": lernziel_id
            }
        )
        assert zwischenziel.status_code == 201
        zwischenziel_id = zwischenziel.json()["id"]

        lernzeit = client.post(
            "/api/lernzeiten/",
            json={
                "zwischenziel_id": zwischenziel_id,
                "duration": 30,
                "status": "abgeschlossen"
            }
        )
        assert lernzeit.status_code == 201

        response = client.delete(
            f"/api/zwischenziele/{zwischenziel_id}"
        )

        # Zwischenziel muss weiterhin vorhanden sein
        existing = client.get(
            f"/api/zwischenziele/{zwischenziel_id}"
        )

    assert response.status_code == 409
    assert existing.status_code == 200
