from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_status_code():
    response = client.get("/Health")
    assert response.status_code == 200


def test_health_response_content():
    response = client.get("/Health")
    assert response.json() == {"message": "Hello, World!"}


def test_health_wrong_method_not_allowed():
    # /Health n'accepte que GET, un POST doit être rejeté
    response = client.post("/Health")
    assert response.status_code == 405