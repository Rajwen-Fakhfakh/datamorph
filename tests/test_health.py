from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_status_code():
    response = client.get("/health")
    assert response.status_code == 200


def test_health_response_content():
    response = client.get("/health")
    assert response.json() == {"status": "ok", "message": "Service operational"}


def test_health_wrong_method_not_allowed():
    # /health n'accepte que GET, un POST doit être rejeté
    response = client.post("/health")
    assert response.status_code == 405