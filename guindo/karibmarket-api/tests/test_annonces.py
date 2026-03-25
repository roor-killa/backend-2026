"""
Tests — KaribMarket API
TP8 : Tests unitaires et d'intégration avec pytest
"""

import pytest

# Le client, le moteur SQLite et les overrides sont initialisés dans conftest.py
from tests.conftest import client


# ----------------------------
# Fixtures
# ----------------------------
@pytest.fixture
def utilisateur_token():
    """Crée un utilisateur et retourne son token JWT."""
    client.post("/api/v1/auth/register", json={
        "nom": "Test User",
        "email": "test@karib.com",
        "telephone": "0696000000",
        "mot_de_passe": "password123"
    })
    response = client.post("/api/v1/auth/login", data={
        "username": "test@karib.com",
        "password": "password123"
    })
    assert response.status_code == 200, f"Login échoué : {response.json()}"
    return response.json()["access_token"]


@pytest.fixture
def headers(utilisateur_token):
    return {"Authorization": f"Bearer {utilisateur_token}"}


@pytest.fixture
def annonce_existante(headers):
    response = client.post("/api/v1/annonces", json={
        "titre": "Mangues bio",
        "description": "Mangues fraîches de Martinique",
        "prix": 3.50,
        "commune": "Le Lamentin"
    }, headers=headers)
    assert response.status_code == 201
    return response.json()


# ----------------------------
# Tests routes de base
# ----------------------------
class TestRoutesBase:

    def test_api_accessible(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "KaribMarket" in response.json()["message"]

    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


# ----------------------------
# Tests authentification
# ----------------------------
class TestAuth:

    def test_register_succes(self):
        response = client.post("/api/v1/auth/register", json={
            "nom": "Nouveau User",
            "email": "nouveau@karib.com",
            "telephone": "0696000000",
            "mot_de_passe": "password123"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "nouveau@karib.com"
        assert "hashed_password" not in data

    def test_register_email_deja_utilise(self):
        client.post("/api/v1/auth/register", json={
            "nom": "User",
            "email": "doublon@karib.com",
            "telephone": "0696000000",
            "mot_de_passe": "password123"
        })
        response = client.post("/api/v1/auth/register", json={
            "nom": "User2",
            "email": "doublon@karib.com",
            "telephone": "0696000000",
            "mot_de_passe": "password456"
        })
        assert response.status_code == 400
        assert "déjà utilisé" in response.json()["detail"]

    def test_login_succes(self):
        client.post("/api/v1/auth/register", json={
            "nom": "Login User",
            "email": "login@karib.com",
            "telephone": "0696000000",
            "mot_de_passe": "password123"
        })
        response = client.post("/api/v1/auth/login", data={
            "username": "login@karib.com",
            "password": "password123"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"

    def test_login_mauvais_mot_de_passe(self):
        client.post("/api/v1/auth/register", json={
            "nom": "User",
            "email": "wrongpass@karib.com",
            "telephone": "0696000000",
            "mot_de_passe": "correct_password"
        })
        response = client.post("/api/v1/auth/login", data={
            "username": "wrongpass@karib.com",
            "password": "wrong_password"
        })
        assert response.status_code == 401

    def test_login_utilisateur_inexistant(self):
        response = client.post("/api/v1/auth/login", data={
            "username": "inexistant@karib.com",
            "password": "password123"
        })
        assert response.status_code == 401


# ----------------------------
# Tests annonces
# ----------------------------
class TestAnnonces:

    def test_liste_annonces_accessible_sans_auth(self):
        response = client.get("/api/v1/annonces")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_creer_annonce_sans_auth_retourne_401(self):
        response = client.post("/api/v1/annonces", json={
            "titre": "Test",
            "prix": 10.0,
            "commune": "Fort-de-France"
        })
        assert response.status_code == 401

    def test_creer_annonce_avec_auth(self, headers):
        response = client.post("/api/v1/annonces", json={
            "titre": "Bananes plantain",
            "description": "Bananes fraîches",
            "prix": 2.50,
            "commune": "Sainte-Marie"
        }, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert data["titre"] == "Bananes plantain"
        assert data["prix"] == 2.50
        assert data["actif"] == True

    def test_get_annonce_existante(self, annonce_existante):
        annonce_id = annonce_existante["id"]
        response = client.get(f"/api/v1/annonces/{annonce_id}")
        assert response.status_code == 200
        assert response.json()["titre"] == "Mangues bio"

    def test_get_annonce_inexistante_retourne_404(self):
        response = client.get("/api/v1/annonces/99999")
        assert response.status_code == 404
        assert "introuvable" in response.json()["detail"]

    def test_filtrer_annonces_par_commune(self, annonce_existante):
        response = client.get("/api/v1/annonces?commune=Lamentin")
        assert response.status_code == 200
        annonces = response.json()
        for annonce in annonces:
            assert "lamentin" in annonce["commune"].lower()

    def test_pagination_annonces(self, headers):
        for i in range(5):
            client.post("/api/v1/annonces", json={
                "titre": f"Annonce {i}",
                "prix": float(i + 1),
                "commune": "Fort-de-France"
            }, headers=headers)

        response = client.get("/api/v1/annonces?page=1&limit=3")
        assert response.status_code == 200
        assert len(response.json()) <= 3

    def test_modifier_annonce_proprietaire(self, headers, annonce_existante):
        annonce_id = annonce_existante["id"]
        response = client.patch(
            f"/api/v1/annonces/{annonce_id}",
            json={"prix": 4.99},
            headers=headers
        )
        assert response.status_code == 200
        assert response.json()["prix"] == 4.99

    def test_modifier_annonce_non_proprietaire_retourne_403(self, annonce_existante):
        client.post("/api/v1/auth/register", json={
            "nom": "Autre User",
            "email": "autre@karib.com",
            "telephone": "0696000000",
            "mot_de_passe": "password123"
        })
        login = client.post("/api/v1/auth/login", data={
            "username": "autre@karib.com",
            "password": "password123"
        })
        autre_token = login.json()["access_token"]

        annonce_id = annonce_existante["id"]
        response = client.patch(
            f"/api/v1/annonces/{annonce_id}",
            json={"prix": 999.0},
            headers={"Authorization": f"Bearer {autre_token}"}
        )
        assert response.status_code == 403

    def test_supprimer_annonce_soft_delete(self, headers, annonce_existante):
        annonce_id = annonce_existante["id"]
        response = client.delete(
            f"/api/v1/annonces/{annonce_id}",
            headers=headers
        )
        assert response.status_code == 204

        liste = client.get("/api/v1/annonces")
        ids = [a["id"] for a in liste.json()]
        assert annonce_id not in ids

    def test_flux_complet(self):
        """Test du flux complet : register → login → créer → lire → modifier → supprimer"""
        r = client.post("/api/v1/auth/register", json={
            "nom": "Flux User",
            "email": "flux@karib.com",
            "telephone": "0696000000",
            "mot_de_passe": "password123"
        })
        assert r.status_code == 201

        r = client.post("/api/v1/auth/login", data={
            "username": "flux@karib.com",
            "password": "password123"
        })
        token = r.json()["access_token"]
        h = {"Authorization": f"Bearer {token}"}

        r = client.post("/api/v1/annonces", json={
            "titre": "Christophines",
            "prix": 1.50,
            "commune": "Schoelcher"
        }, headers=h)
        assert r.status_code == 201
        annonce_id = r.json()["id"]

        r = client.get(f"/api/v1/annonces/{annonce_id}")
        assert r.status_code == 200
        assert r.json()["titre"] == "Christophines"

        r = client.patch(f"/api/v1/annonces/{annonce_id}",
                         json={"prix": 1.99}, headers=h)
        assert r.status_code == 200
        assert r.json()["prix"] == 1.99

        r = client.delete(f"/api/v1/annonces/{annonce_id}", headers=h)
        assert r.status_code == 204