import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine)


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# --- Tests ---

def test_api_est_accessible(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "KaribMarket" in response.json()["message"]


def test_liste_annonces_vide_au_depart(client):
    response = client.get("/api/v1/annonces")
    assert response.status_code == 200
    body = response.json()
    assert body["data"] == []
    assert body["meta"]["total"] == 0


def test_creer_annonce_sans_auth_retourne_401(client):
    response = client.post("/api/v1/annonces", json={
        "titre": "Test annonce",
        "prix": 10.0,
        "commune": "Fort-de-France"
    })
    assert response.status_code == 401


def test_flux_complet_inscription_connexion_annonce(client):
    # 1. S'inscrire
    register_resp = client.post("/api/v1/auth/register", json={
        "nom": "Test User",
        "email": "test@test.com",
        "mot_de_passe": "password123"
    })
    assert register_resp.status_code == 201

    # 2. Se connecter
    login_resp = client.post("/api/v1/auth/login", data={
        "username": "test@test.com",
        "password": "password123"
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    # 3. Créer une annonce avec le token
    create_resp = client.post(
        "/api/v1/annonces",
        json={"titre": "Mangues bio", "prix": 3.50, "commune": "Le Lamentin", "categorie": "alimentaire"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_resp.status_code == 201
    annonce = create_resp.json()
    assert annonce["titre"] == "Mangues bio"
    assert annonce["prix"] == 3.50


def test_annonce_introuvable_retourne_404(client):
    response = client.get("/api/v1/annonces/99999")
    assert response.status_code == 404
