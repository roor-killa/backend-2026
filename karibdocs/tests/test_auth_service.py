def _valid_user_payload(email: str):
    return {
        "nom": "Alice Martin",
        "email": email,
        "telephone": "+596123456789",
        "mot_de_passe": "password123",
    }


def test_health_check_route(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "KaribDocs"


def test_register_then_login_success(client):
    register_response = client.post("/auth/register", json=_valid_user_payload("alice@example.com"))
    assert register_response.status_code == 201
    body = register_response.json()
    assert body["email"] == "alice@example.com"
    assert body["actif"] is True

    login_response = client.post(
        "/auth/login",
        data={"username": "alice@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200
    login_body = login_response.json()
    assert login_body["token_type"] == "bearer"
    assert "access_token" in login_body
    assert login_body["utilisateur"]["nom"] == "Alice Martin"

def test_register_duplicate_email_returns_400(client):
    payload = _valid_user_payload("duplicate@example.com")
    first = client.post("/auth/register", json=payload)
    second = client.post("/auth/register", json=payload)

    assert first.status_code == 201
    assert second.status_code == 400
    assert second.json()["detail"] == "Cet email est déjà utilisé"
