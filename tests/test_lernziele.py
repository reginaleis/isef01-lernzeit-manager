
from fastapi.testclient import TestClient
from isef01_lernzeit_manager.main import app


def test_lernziel_mit_leerem_titel():
    with TestClient(app) as client:
        response = client.post(
            "/api/lernziele/",
            json={
                "title": "",
                "module_id": "test-modul"
            }
        )

    assert response.status_code == 422


def test_lernziel_ohne_titel():
    with TestClient(app) as client:
        response = client.post(
            "/api/lernziele/",
            json={"module_id": "test-modul"}
        )

    assert response.status_code == 422


def test_lernziel_ohne_modul_id():
    with TestClient(app) as client:
        response = client.post(
            "/api/lernziele/",
            json={"title": "SQL lernen"}
        )

    assert response.status_code == 422


def test_lernziel_mit_negativer_lernzeit():
    with TestClient(app) as client:
        response = client.post(
            "/api/lernziele/",
            json={
                "title": "SQL lernen",
                "module_id": "test-modul",
                "accumulated_study_time": -10
            }
        )

    assert response.status_code == 422


def test_lernziel_erfolgreich_erstellen():
    with TestClient(app) as client:
        response = client.post(
            "/api/lernziele/",
            json={
                "title": "pytest-Tests schreiben",
                "description": "Automatisierte Tests erstellen",
                "module_id": "ISEF01"
            }
        )

    assert response.status_code == 201
    assert response.json()["title"] == "pytest-Tests schreiben"
    assert response.json()["module_id"] == "ISEF01"


def test_lernziel_erstellen_und_abrufen():
    with TestClient(app) as client:

        # 1. Lernziel erstellen
        create_response = client.post(
            "/api/lernziele/",
            json={
                "title": "SQL lernen",
                "description": "SELECT und JOIN üben",
                "module_id": "ISEF01"
            }
        )

        assert create_response.status_code == 201

        # 2. ID des erstellten Lernziels auslesen
        lernziel_id = create_response.json()["id"]

        # 3. Lernziel erneut über die API abrufen
        get_response = client.get(
            f"/api/lernziele/{lernziel_id}"
        )

        # 4. Ergebnis überprüfen
        assert get_response.status_code == 200
        assert get_response.json()["id"] == lernziel_id
        assert get_response.json()["title"] == "SQL lernen"
        assert get_response.json()["module_id"] == "ISEF01"


def test_lernziel_bearbeiten():
    with TestClient(app) as client:
        # 1. Lernziel erstellen
        create_response = client.post(
            "/api/lernziele/",
            json={
                "title": "SQL lernen",
                "module_id": "ISEF01"
            }
        )

        assert create_response.status_code == 201
        lernziel_id = create_response.json()["id"]

        # 2. Lernziel bearbeiten
        update_response = client.put(
            f"/api/lernziele/{lernziel_id}",
            json={
                "title": "SQL und Datenbanken lernen"
            }
        )

        assert update_response.status_code == 200
        assert update_response.json()["title"] == "SQL und Datenbanken lernen"

        # 3. Lernziel erneut abrufen
        get_response = client.get(
            f"/api/lernziele/{lernziel_id}"
        )

        assert get_response.status_code == 200
        assert get_response.json()["title"] == "SQL und Datenbanken lernen"
        assert get_response.json()["module_id"] == "ISEF01"


def test_lernziel_loeschen():
    with TestClient(app) as client:
        # 1. Lernziel erstellen
        create_response = client.post(
            "/api/lernziele/",
            json={
                "title": "SQL lernen",
                "module_id": "ISEF01"
            }
        )

        assert create_response.status_code == 201
        lernziel_id = create_response.json()["id"]

        # 2. Lernziel löschen
        delete_response = client.delete(
            f"/api/lernziele/{lernziel_id}"
        )

        assert delete_response.status_code == 200

        # 3. Überprüfen, ob das Lernziel entfernt wurde
        get_response = client.get(
            f"/api/lernziele/{lernziel_id}"
        )

        assert get_response.status_code == 404
