def _register_and_login(client, email: str):
    payload = {
        "nom": "Document User",
        "email": email,
        "telephone": "+596123456780",
        "mot_de_passe": "password123",
    }
    register = client.post("/auth/register", json=payload)
    assert register.status_code == 201

    login = client.post(
        "/auth/login",
        data={"username": email, "password": "password123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_upload_list_and_delete_document_flow(client):
    headers = _register_and_login(client, "docs-flow@example.com")

    upload = client.post(
        "/documents/upload",
        headers=headers,
        files={"file": ("cours.txt", b"Contenu de cours", "text/plain")},
    )
    assert upload.status_code == 201
    uploaded_doc = upload.json()
    assert uploaded_doc["original_name"] == "cours.txt"
    assert uploaded_doc["source"] == "upload"

    listing = client.get("/documents/", headers=headers)
    assert listing.status_code == 200
    list_data = listing.json()
    assert list_data["count"] == 1
    assert list_data["documents"][0]["id"] == uploaded_doc["id"]

    deletion = client.delete(f"/documents/{uploaded_doc['id']}", headers=headers)
    assert deletion.status_code == 200
    assert deletion.json()["message"] == "Document supprimé avec succès"

    after_delete = client.get("/documents/", headers=headers)
    assert after_delete.status_code == 200
    assert after_delete.json()["count"] == 0


def test_upload_rejects_unsupported_type(client):
    headers = _register_and_login(client, "docs-invalid@example.com")

    response = client.post(
        "/documents/upload",
        headers=headers,
        files={"file": ("payload.bin", b"\x00\x01\x02", "application/json")},
    )

    assert response.status_code == 400
    assert "Type non supporté" in response.json()["detail"]
