"""
Tests des endpoints joueurs :
  POST   /players/
  GET    /players/{id}
  GET    /players/leaderboard
"""


class TestCreatePlayer:

    def test_create_player_success(self, client):
        """Création d'un joueur avec un pseudo valide."""
        res = client.post("/players/", json={"pseudo": "Ibrahim"})
        assert res.status_code == 201
        data = res.json()
        assert data["pseudo"] == "Ibrahim"
        assert data["score"] == 0
        assert data["games_played"] == 0
        assert "id" in data

    def test_create_player_duplicate_pseudo(self, client):
        """Deux joueurs ne peuvent pas avoir le même pseudo."""
        client.post("/players/", json={"pseudo": "Ibrahim"})
        res = client.post("/players/", json={"pseudo": "Ibrahim"})
        assert res.status_code == 400
        assert "déjà utilisé" in res.json()["detail"]

    def test_create_player_pseudo_too_short(self, client):
        """Le pseudo doit faire au moins 3 caractères."""
        res = client.post("/players/", json={"pseudo": "ab"})
        assert res.status_code == 422

    def test_create_player_pseudo_too_long(self, client):
        """Le pseudo ne doit pas dépasser 50 caractères."""
        res = client.post("/players/", json={"pseudo": "a" * 51})
        assert res.status_code == 422

    def test_create_player_pseudo_invalid_chars(self, client):
        """Le pseudo ne doit pas contenir de caractères spéciaux."""
        res = client.post("/players/", json={"pseudo": "Ibrahim@!"})
        assert res.status_code == 422

    def test_create_player_pseudo_with_underscore(self, client):
        """Les underscores et tirets sont autorisés dans le pseudo."""
        res = client.post("/players/", json={"pseudo": "Ibrahim_99"})
        assert res.status_code == 201

    def test_create_player_missing_pseudo(self, client):
        """Le pseudo est obligatoire."""
        res = client.post("/players/", json={})
        assert res.status_code == 422


class TestGetPlayer:

    def test_get_player_success(self, client, player_ibrahim):
        """Récupération d'un joueur existant."""
        res = client.get(f"/players/{player_ibrahim['id']}")
        assert res.status_code == 200
        assert res.json()["pseudo"] == "Ibrahim"

    def test_get_player_not_found(self, client):
        """Un joueur inexistant retourne 404."""
        res = client.get("/players/9999")
        assert res.status_code == 404

    def test_get_player_invalid_id(self, client):
        """Un ID non entier retourne 422."""
        res = client.get("/players/abc")
        assert res.status_code == 422


class TestLeaderboard:

    def test_leaderboard_empty(self, client):
        """Le leaderboard est vide si aucun joueur n'existe."""
        res = client.get("/players/leaderboard")
        assert res.status_code == 200
        assert res.json() == []

    def test_leaderboard_returns_players(self, client, player_ibrahim, player_mohand):
        """Le leaderboard retourne les joueurs existants."""
        res = client.get("/players/leaderboard")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 2

    def test_leaderboard_sorted_by_score(self, client):
        """Les joueurs sont triés par score décroissant."""
        from app.database import get_db
        from app.models.player import Player

        # Créer deux joueurs avec des scores différents
        client.post("/players/", json={"pseudo": "Junior"})
        client.post("/players/", json={"pseudo": "Mohand"})

        # Modifier les scores directement en BDD
        db = next(override_get_db())
        try:
            junior = db.query(Player).filter(Player.pseudo == "Junior").first()
            mohand = db.query(Player).filter(Player.pseudo == "Mohand").first()
            junior.score = 200
            mohand.score = 100
            db.commit()
        finally:
            db.close()

        res = client.get("/players/leaderboard")
        data = res.json()
        assert data[0]["pseudo"] == "Junior"
        assert data[0]["rank"] == 1
        assert data[1]["pseudo"] == "Mohand"
        assert data[1]["rank"] == 2

    def test_leaderboard_limit(self, client):
        """Le paramètre limit fonctionne correctement."""
        for i in range(5):
            client.post("/players/", json={"pseudo": f"Joueur{i}"})

        res = client.get("/players/leaderboard?limit=3")
        assert res.status_code == 200
        assert len(res.json()) == 3

    def test_leaderboard_limit_invalid(self, client):
        """Un limit invalide retourne 422."""
        res = client.get("/players/leaderboard?limit=0")
        assert res.status_code == 422


def override_get_db():
    from tests.conftest import TestingSessionLocal
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()