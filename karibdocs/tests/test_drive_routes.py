from app.services.auth_service import create_access_token


def _register_and_login(client, email: str):
    payload = {
        "nom": "Drive User",
        "email": email,
        "telephone": "+596123456781",
        "mot_de_passe": "password123",
    }
    register = client.post("/auth/register", json=payload)
    assert register.status_code == 201

    login = client.post(
        "/auth/login",
        data={"username": email, "password": "password123"},
    )
    assert login.status_code == 200
    body = login.json()
    return body["utilisateur"]["id"], {"Authorization": f"Bearer {body['access_token']}"}


def test_drive_connect_returns_auth_url(client, monkeypatch):
    from app.services import drive_service as drive_service_module

    _user_id, headers = _register_and_login(client, "drive-connect@example.com")

    monkeypatch.setattr(
        drive_service_module.DriveService,
        "get_auth_url",
        lambda self, state=None: f"https://fake-oauth.local/auth?state={state}",
    )

    response = client.get("/drive/connect", headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert "auth_url" in payload
    assert "state" in payload
    assert payload["state"] in payload["auth_url"]


def test_drive_oauth_callback_then_list_files(client, monkeypatch):
    from app.services import drive_service as drive_service_module

    user_id, headers = _register_and_login(client, "drive-callback@example.com")

    monkeypatch.setattr(
        drive_service_module.DriveService,
        "exchange_code",
        lambda self, code: {
            "token": f"token-{code}",
            "refresh_token": "refresh-token",
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": "client-id",
            "client_secret": "client-secret",
            "scopes": ["drive.readonly"],
        },
    )
    monkeypatch.setattr(
        drive_service_module.DriveService,
        "list_files",
        lambda self, credentials, folder_id=None: [
            {"id": "abc", "name": "notes.pdf", "mimeType": "application/pdf"}
        ],
    )

    state = create_access_token({"sub": str(user_id), "purpose": "drive_oauth"})
    callback = client.get(f"/drive/oauth/callback?code=ok123&state={state}")

    assert callback.status_code == 200
    assert callback.json()["message"] == "Google Drive connecté avec succès"

    files = client.get("/drive/files", headers=headers)
    assert files.status_code == 200
    files_payload = files.json()
    assert files_payload["count"] == 1
    assert files_payload["files"][0]["name"] == "notes.pdf"


def test_drive_files_returns_400_when_not_connected(client):
    _user_id, headers = _register_and_login(client, "drive-missing-cred@example.com")
    response = client.get("/drive/files", headers=headers)

    assert response.status_code == 400
    assert "Google Drive non connecté" in response.json()["detail"]
