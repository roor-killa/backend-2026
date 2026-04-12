from app.database import SessionLocal
from app.models.document import Document


def _register_and_login(client, email: str):
    payload = {
        "nom": "Scraping User",
        "email": email,
        "telephone": "+596123456782",
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


def test_scraping_sources_requires_auth(client):
    response = client.get("/scraping/sources")
    assert response.status_code in (401, 403)


def test_scraping_rci_returns_mocked_items(client, monkeypatch):
    from app.routers import scraping as scraping_router

    _user_id, headers = _register_and_login(client, "scraping-rci@example.com")

    class FakeScraper:
        def __init__(self, max_depth: int = 1, delay: float = 1.5):
            self.max_depth = max_depth
            self.delay = delay

        def scrape(self, max_pages: int = 0):
            return [
                {
                    "title": "Article test",
                    "author": "RCI",
                    "body": "Contenu test",
                    "url": "https://rci.fm/article-test",
                }
            ]

    monkeypatch.setattr(scraping_router, "_load_rci_scraper_class", lambda: FakeScraper)

    response = client.post(
        "/scraping/rci?max_depth=1&max_pages=5&delay=1.0",
        headers=headers,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "rci"
    assert payload["count"] == 1
    assert payload["items"][0]["title"] == "Article test"


def test_scraping_rci_save_persists_article_document(client):
    user_id, headers = _register_and_login(client, "scraping-save@example.com")

    response = client.post(
        "/scraping/rci/save",
        headers=headers,
        json={
            "items": [
                {
                    "title": "Dont worry bout a thing",
                    "author": "Tori Kelly",
                    "body": "Lyrics test content",
                    "url": "https://example.com/lyrics",
                }
            ]
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 1

    db = SessionLocal()
    try:
        docs = db.query(Document).filter(Document.user_id == user_id).order_by(Document.id.desc()).all()
        assert len(docs) >= 1
        assert docs[0].source == "rci_scrape"
        assert docs[0].original_name == "dont-worry-bout-a-thing.txt"
    finally:
        db.close()


def test_scraping_rci_save_empty_payload_returns_400(client):
    _user_id, headers = _register_and_login(client, "scraping-empty@example.com")

    response = client.post(
        "/scraping/rci/save",
        headers=headers,
        json={"items": []},
    )

    assert response.status_code == 400
    assert "Aucun article" in response.json()["detail"]
