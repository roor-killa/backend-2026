"""
Tests des endpoints parties :
  POST   /games/
  POST   /games/{id}/join
  POST   /games/{id}/place-ships
  GET    /games/{id}
  GET    /games/{id}/board
  POST   /games/{id}/shoot
  GET    /games/{id}/shots
"""
from tests.conftest import SAMPLE_SHIPS


class TestCreateGame:

    def test_create_solo_game_easy(self, client, player_ibrahim):
        """Création d'une partie solo facile."""
        res = client.post(
            "/games/",
            params={"player_id": player_ibrahim["id"]},
            json={"mode": "solo", "difficulty": "easy"},
        )
        assert res.status_code == 201
        data = res.json()
        assert data["mode"] == "solo"
        assert data["difficulty"] == "easy"
        assert data["status"] == "placement"

    def test_create_solo_game_hard(self, client, player_ibrahim):
        """Création d'une partie solo difficile."""
        res = client.post(
            "/games/",
            params={"player_id": player_ibrahim["id"]},
            json={"mode": "solo", "difficulty": "hard"},
        )
        assert res.status_code == 201
        assert res.json()["difficulty"] == "hard"

    def test_create_multiplayer_game(self, client, player_ibrahim):
        """Création d'une partie multijoueur."""
        res = client.post(
            "/games/",
            params={"player_id": player_ibrahim["id"]},
            json={"mode": "multiplayer"},
        )
        assert res.status_code == 201
        data = res.json()
        assert data["mode"] == "multiplayer"
        assert data["status"] == "waiting"
        assert data["difficulty"] is None

    def test_create_game_invalid_mode(self, client, player_ibrahim):
        """Un mode invalide retourne 422."""
        res = client.post(
            "/games/",
            params={"player_id": player_ibrahim["id"]},
            json={"mode": "invalide"},
        )
        assert res.status_code == 422

    def test_create_game_invalid_difficulty(self, client, player_ibrahim):
        """Une difficulté invalide retourne 422."""
        res = client.post(
            "/games/",
            params={"player_id": player_ibrahim["id"]},
            json={"mode": "solo", "difficulty": "impossible"},
        )
        assert res.status_code == 422

    def test_create_game_unknown_player(self, client):
        """Un joueur inexistant retourne 404."""
        res = client.post(
            "/games/",
            params={"player_id": 9999},
            json={"mode": "solo", "difficulty": "easy"},
        )
        assert res.status_code == 404


class TestJoinGame:

    def test_join_multiplayer_game(self, client, player_ibrahim, player_mohand):
        """Un second joueur peut rejoindre une partie multijoueur."""
        game = client.post(
            "/games/",
            params={"player_id": player_ibrahim["id"]},
            json={"mode": "multiplayer"},
        ).json()

        res = client.post(
            f"/games/{game['id']}/join",
            json={"player_id": player_mohand["id"]},
        )
        assert res.status_code == 200
        assert res.json()["status"] == "placement"

    def test_join_solo_game_fails(self, client, player_ibrahim, player_mohand):
        """On ne peut pas rejoindre une partie solo."""
        game = client.post(
            "/games/",
            params={"player_id": player_ibrahim["id"]},
            json={"mode": "solo", "difficulty": "easy"},
        ).json()

        res = client.post(
            f"/games/{game['id']}/join",
            json={"player_id": player_mohand["id"]},
        )
        assert res.status_code == 400

    def test_join_same_player_twice(self, client, player_ibrahim):
        """Un joueur ne peut pas rejoindre sa propre partie."""
        game = client.post(
            "/games/",
            params={"player_id": player_ibrahim["id"]},
            json={"mode": "multiplayer"},
        ).json()

        res = client.post(
            f"/games/{game['id']}/join",
            json={"player_id": player_ibrahim["id"]},
        )
        assert res.status_code == 400


class TestPlaceShips:

    def test_place_ships_success(self, client, player_ibrahim, solo_game):
        """Placement valide des 5 bateaux."""
        res = client.post(
            f"/games/{solo_game['id']}/place-ships",
            json={
                "player_id": player_ibrahim["id"],
                "ships": SAMPLE_SHIPS,
            },
        )
        assert res.status_code == 200
        # En solo, la partie démarre dès que le joueur place ses bateaux
        assert res.json()["status"] == "playing"

    def test_place_ships_missing_boat(self, client, player_ibrahim, solo_game):
        """Il faut placer les 5 bateaux obligatoires."""
        res = client.post(
            f"/games/{solo_game['id']}/place-ships",
            json={
                "player_id": player_ibrahim["id"],
                "ships": SAMPLE_SHIPS[:3],  # Seulement 3 bateaux
            },
        )
        assert res.status_code == 422

    def test_place_ships_out_of_grid(self, client, player_ibrahim, solo_game):
        """Un bateau qui dépasse la grille est refusé."""
        invalid_ships = SAMPLE_SHIPS.copy()
        invalid_ships[0] = {"type": "carrier", "row": 0, "col": 8, "orientation": "horizontal"}
        res = client.post(
            f"/games/{solo_game['id']}/place-ships",
            json={"player_id": player_ibrahim["id"], "ships": invalid_ships},
        )
        assert res.status_code == 422

    def test_place_ships_overlap(self, client, player_ibrahim, solo_game):
        """Deux bateaux qui se chevauchent sont refusés."""
        overlapping_ships = [
            {"type": "carrier",   "row": 0, "col": 0, "orientation": "horizontal"},
            {"type": "cruiser",   "row": 0, "col": 0, "orientation": "horizontal"},  # Chevauche
            {"type": "destroyer", "row": 2, "col": 0, "orientation": "horizontal"},
            {"type": "submarine", "row": 3, "col": 0, "orientation": "horizontal"},
            {"type": "torpedo",   "row": 4, "col": 0, "orientation": "horizontal"},
        ]
        res = client.post(
            f"/games/{solo_game['id']}/place-ships",
            json={"player_id": player_ibrahim["id"], "ships": overlapping_ships},
        )
        assert res.status_code == 400

    def test_place_ships_twice(self, client, player_ibrahim, solo_game):
        """On ne peut pas placer ses bateaux deux fois."""
        payload = {"player_id": player_ibrahim["id"], "ships": SAMPLE_SHIPS}
        client.post(f"/games/{solo_game['id']}/place-ships", json=payload)
        res = client.post(f"/games/{solo_game['id']}/place-ships", json=payload)
        assert res.status_code == 400


class TestGetGame:

    def test_get_game_success(self, client, solo_game):
        """Récupération d'une partie existante."""
        res = client.get(f"/games/{solo_game['id']}")
        assert res.status_code == 200
        assert res.json()["id"] == solo_game["id"]

    def test_get_game_not_found(self, client):
        """Une partie inexistante retourne 404."""
        res = client.get("/games/9999")
        assert res.status_code == 404


class TestGetBoards:

    def test_get_boards_after_placement(self, client, player_ibrahim, solo_game):
        """Les grilles sont disponibles après le placement."""
        client.post(
            f"/games/{solo_game['id']}/place-ships",
            json={"player_id": player_ibrahim["id"], "ships": SAMPLE_SHIPS},
        )
        res = client.get(
            f"/games/{solo_game['id']}/board",
            params={"player_id": player_ibrahim["id"]},
        )
        assert res.status_code == 200
        data = res.json()
        assert "my_board" in data
        assert "enemy_board" in data
        assert len(data["my_board"]["grid"]) == 10

    def test_enemy_ships_are_hidden(self, client, player_ibrahim, solo_game):
        """Les bateaux ennemis non touchés sont masqués (valeur 0)."""
        client.post(
            f"/games/{solo_game['id']}/place-ships",
            json={"player_id": player_ibrahim["id"], "ships": SAMPLE_SHIPS},
        )
        res = client.get(
            f"/games/{solo_game['id']}/board",
            params={"player_id": player_ibrahim["id"]},
        )
        enemy_grid = res.json()["enemy_board"]["grid"]
        # Aucune case de la grille ennemie ne doit valoir 1 (bateau visible)
        all_cells = [cell for row in enemy_grid for cell in row]
        assert 1 not in all_cells


class TestShoot:

    def _start_game(self, client, player_ibrahim, solo_game):
        """Helper : place les bateaux et démarre la partie."""
        client.post(
            f"/games/{solo_game['id']}/place-ships",
            json={"player_id": player_ibrahim["id"], "ships": SAMPLE_SHIPS},
        )

    def test_shoot_miss(self, client, player_ibrahim, solo_game):
        """Un tir à l'eau retourne 'miss'."""
        self._start_game(client, player_ibrahim, solo_game)
        res = client.post(
            f"/games/{solo_game['id']}/shoot",
            json={"player_id": player_ibrahim["id"], "row": 9, "col": 9},
        )
        assert res.status_code == 200
        assert res.json()["result"] in ["miss", "hit", "sunk"]

    def test_shoot_same_cell_twice(self, client, player_ibrahim, solo_game):
        """On ne peut pas tirer deux fois sur la même case."""
        self._start_game(client, player_ibrahim, solo_game)
        payload = {"player_id": player_ibrahim["id"], "row": 9, "col": 9}
        client.post(f"/games/{solo_game['id']}/shoot", json=payload)
        res = client.post(f"/games/{solo_game['id']}/shoot", json=payload)
        assert res.status_code == 400

    def test_shoot_out_of_grid(self, client, player_ibrahim, solo_game):
        """Un tir hors grille retourne 422."""
        self._start_game(client, player_ibrahim, solo_game)
        res = client.post(
            f"/games/{solo_game['id']}/shoot",
            json={"player_id": player_ibrahim["id"], "row": 10, "col": 10},
        )
        assert res.status_code == 422

    def test_shoot_before_placement(self, client, player_ibrahim, solo_game):
        """On ne peut pas tirer avant la phase de placement."""
        res = client.post(
            f"/games/{solo_game['id']}/shoot",
            json={"player_id": player_ibrahim["id"], "row": 0, "col": 0},
        )
        assert res.status_code == 400

    def test_shoot_response_has_game_over(self, client, player_ibrahim, solo_game):
        """La réponse d'un tir contient toujours game_over."""
        self._start_game(client, player_ibrahim, solo_game)
        res = client.post(
            f"/games/{solo_game['id']}/shoot",
            json={"player_id": player_ibrahim["id"], "row": 9, "col": 9},
        )
        assert "game_over" in res.json()


class TestGetShots:

    def test_get_shots_empty(self, client, solo_game):
        """Historique vide au début de la partie."""
        res = client.get(f"/games/{solo_game['id']}/shots")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 0
        assert data["shots"] == []

    def test_get_shots_after_shoot(self, client, player_ibrahim, solo_game):
        """L'historique contient les tirs effectués."""
        client.post(
            f"/games/{solo_game['id']}/place-ships",
            json={"player_id": player_ibrahim["id"], "ships": SAMPLE_SHIPS},
        )
        client.post(
            f"/games/{solo_game['id']}/shoot",
            json={"player_id": player_ibrahim["id"], "row": 9, "col": 9},
        )
        res = client.get(f"/games/{solo_game['id']}/shots")
        assert res.status_code == 200
        # Au moins 1 tir (joueur) + éventuellement 1 tir IA
        assert res.json()["total"] >= 1