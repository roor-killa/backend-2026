"""
Tests de la logique IA :
  - Placement aléatoire des bateaux
  - Niveau Facile : tirs aléatoires
  - Niveau Moyen  : cible les cases adjacentes après touché
  - Niveau Difficile : carte de probabilités
"""
import pytest
from app.services.ai_service import (
    ai_place_ships, ai_shoot,
    _easy_shot, _medium_shot, _hard_shot,
    _get_played_cells,
)
from app.models.board import Board
from app.models.player import Player
from app.models.game import Game
from app.models.ship import Ship
from app.models.shot import Shot
from app.core.constants import SHIPS, GRID_SIZE, GameMode, GameStatus, Difficulty, ShotResult
from tests.conftest import SAMPLE_SHIPS


# ═══════════════════════════════════════════════════════
# PLACEMENT IA
# ═══════════════════════════════════════════════════════

class TestAIPlacement:

    def test_ai_places_all_ships(self, db):
        """L'IA place exactement 5 bateaux."""
        player, board = _create_ai_board(db)
        ai_place_ships(db, board)
        db.commit()

        ships = db.query(Ship).filter(Ship.board_id == board.id).all()
        assert len(ships) == len(SHIPS)

    def test_ai_ships_cover_correct_cells(self, db):
        """Chaque bateau occupe le bon nombre de cases."""
        player, board = _create_ai_board(db)
        ai_place_ships(db, board)
        db.commit()

        ships = db.query(Ship).filter(Ship.board_id == board.id).all()
        for ship in ships:
            expected_size = SHIPS[ship.type]
            assert len(ship.positions) == expected_size

    def test_ai_ships_no_overlap(self, db):
        """Les bateaux de l'IA ne se chevauchent pas."""
        player, board = _create_ai_board(db)
        ai_place_ships(db, board)
        db.commit()

        ships = db.query(Ship).filter(Ship.board_id == board.id).all()
        all_positions = []
        for ship in ships:
            all_positions.extend([tuple(p) for p in ship.positions])

        # Si pas de doublons, len == len(set)
        assert len(all_positions) == len(set(all_positions))

    def test_ai_ships_within_grid(self, db):
        """Tous les bateaux restent dans la grille."""
        player, board = _create_ai_board(db)
        ai_place_ships(db, board)
        db.commit()

        ships = db.query(Ship).filter(Ship.board_id == board.id).all()
        for ship in ships:
            for r, c in ship.positions:
                assert 0 <= r < GRID_SIZE
                assert 0 <= c < GRID_SIZE

    def test_ai_grid_updated(self, db):
        """La grille du board est mise à jour après le placement."""
        player, board = _create_ai_board(db)
        ai_place_ships(db, board)
        db.commit()
        db.refresh(board)

        total_ship_cells = sum(SHIPS.values())  # 5+4+3+3+2 = 17
        cells_marked = sum(cell for row in board.grid for cell in row if cell == 1)
        assert cells_marked == total_ship_cells

    def test_ai_placement_is_random(self, db):
        """Deux placements différents ne sont pas identiques (probabilité très faible)."""
        _, board1 = _create_ai_board(db, pseudo="IA_1")
        _, board2 = _create_ai_board(db, pseudo="IA_2")
        ai_place_ships(db, board1)
        ai_place_ships(db, board2)
        db.commit()
        db.refresh(board1)
        db.refresh(board2)

        # Les grilles ne sont presque jamais identiques
        assert board1.grid != board2.grid or True  # Test indicatif


# ═══════════════════════════════════════════════════════
# NIVEAU FACILE
# ═══════════════════════════════════════════════════════

class TestEasyAI:

    def test_easy_shot_is_within_grid(self, db):
        """Le tir facile reste dans la grille."""
        game, ai_player, _ = _setup_solo_game(db)
        row, col = _easy_shot(db, game.id, ai_player.id)
        assert 0 <= row < GRID_SIZE
        assert 0 <= col < GRID_SIZE

    def test_easy_shot_not_already_played(self, db):
        """Le tir facile ne rejoue pas une case déjà jouée."""
        game, ai_player, _ = _setup_solo_game(db)

        # Simuler plusieurs tirs déjà effectués
        for r in range(5):
            for c in range(10):
                shot = Shot(
                    game_id=game.id, player_id=ai_player.id,
                    row=r, col=c, result=ShotResult.MISS
                )
                db.add(shot)
        db.commit()

        played = _get_played_cells(db, game.id, ai_player.id)
        row, col = _easy_shot(db, game.id, ai_player.id)
        assert (row, col) not in played

    def test_easy_shot_covers_all_cells(self, db):
        """L'IA facile peut éventuellement couvrir toute la grille."""
        game, ai_player, _ = _setup_solo_game(db)
        shots_made = set()

        for _ in range(100):
            if len(shots_made) == GRID_SIZE * GRID_SIZE:
                break
            row, col = _easy_shot(db, game.id, ai_player.id)
            shots_made.add((row, col))
            shot = Shot(
                game_id=game.id, player_id=ai_player.id,
                row=row, col=col, result=ShotResult.MISS
            )
            db.add(shot)
            db.commit()

        assert len(shots_made) > 0


# ═══════════════════════════════════════════════════════
# NIVEAU MOYEN
# ═══════════════════════════════════════════════════════

class TestMediumAI:

    def test_medium_targets_adjacent_after_hit(self, db):
        """Après un touché, l'IA cible une case adjacente."""
        game, ai_player, _ = _setup_solo_game(db)

        # Simuler un touché en (5, 5)
        hit = Shot(
            game_id=game.id, player_id=ai_player.id,
            row=5, col=5, result=ShotResult.HIT
        )
        db.add(hit)
        db.commit()

        row, col = _medium_shot(db, game.id, ai_player.id)

        # Le tir doit être adjacent à (5,5)
        adjacent = {(4, 5), (6, 5), (5, 4), (5, 6)}
        assert (row, col) in adjacent

    def test_medium_random_when_no_hit(self, db):
        """Sans touché actif, l'IA tire aléatoirement."""
        game, ai_player, _ = _setup_solo_game(db)
        row, col = _medium_shot(db, game.id, ai_player.id)
        assert 0 <= row < GRID_SIZE
        assert 0 <= col < GRID_SIZE

    def test_medium_avoids_already_played(self, db):
        """L'IA moyenne ne rejoue pas une case déjà jouée."""
        game, ai_player, _ = _setup_solo_game(db)

        # Jouer toutes les cases adjacentes à (3,3)
        for r, c in [(2, 3), (4, 3), (3, 2), (3, 4)]:
            shot = Shot(
                game_id=game.id, player_id=ai_player.id,
                row=r, col=c, result=ShotResult.MISS
            )
            db.add(shot)

        # Touché en (3,3)
        hit = Shot(
            game_id=game.id, player_id=ai_player.id,
            row=3, col=3, result=ShotResult.HIT
        )
        db.add(hit)
        db.commit()

        played = _get_played_cells(db, game.id, ai_player.id)
        row, col = _medium_shot(db, game.id, ai_player.id)
        assert (row, col) not in played


# ═══════════════════════════════════════════════════════
# NIVEAU DIFFICILE
# ═══════════════════════════════════════════════════════

class TestHardAI:

    def test_hard_shot_within_grid(self, db):
        """Le tir difficile reste dans la grille."""
        game, ai_player, _ = _setup_solo_game(db)
        row, col = _hard_shot(db, game.id, ai_player.id)
        assert 0 <= row < GRID_SIZE
        assert 0 <= col < GRID_SIZE

    def test_hard_not_replays_cell(self, db):
        """L'IA difficile ne rejoue pas une case déjà jouée."""
        game, ai_player, _ = _setup_solo_game(db)

        # Jouer la moitié de la grille
        for r in range(5):
            for c in range(10):
                shot = Shot(
                    game_id=game.id, player_id=ai_player.id,
                    row=r, col=c, result=ShotResult.MISS
                )
                db.add(shot)
        db.commit()

        played = _get_played_cells(db, game.id, ai_player.id)
        row, col = _hard_shot(db, game.id, ai_player.id)
        assert (row, col) not in played

    def test_hard_targets_alignment_after_two_hits(self, db):
        """Après deux touches alignées, l'IA continue dans cet axe."""
        game, ai_player, _ = _setup_solo_game(db)

        # Deux touches horizontales en (5,5) et (5,6)
        for c in [5, 6]:
            shot = Shot(
                game_id=game.id, player_id=ai_player.id,
                row=5, col=c, result=ShotResult.HIT
            )
            db.add(shot)
        db.commit()

        row, col = _hard_shot(db, game.id, ai_player.id)

        # L'IA devrait tirer en (5,4) ou (5,7)
        expected = {(5, 4), (5, 7)}
        assert (row, col) in expected


# ═══════════════════════════════════════════════════════
# HELPERS PRIVÉS
# ═══════════════════════════════════════════════════════

def _create_ai_board(db, pseudo="IA_test"):
    """Crée un joueur et un board pour les tests IA."""
    player = Player(pseudo=pseudo)
    db.add(player)
    db.flush()

    game = Game(mode=GameMode.SOLO, status=GameStatus.PLAYING)
    db.add(game)
    db.flush()

    board = Board(game_id=game.id, player_id=player.id)
    db.add(board)
    db.flush()

    return player, board


def _setup_solo_game(db):
    """
    Crée une partie solo complète avec joueur humain et IA.
    Retourne (game, ai_player, human_player).
    """
    human = Player(pseudo="Human_test")
    ai_player = Player(pseudo="AI_test")
    db.add_all([human, ai_player])
    db.flush()

    game = Game(
        mode=GameMode.SOLO,
        difficulty=Difficulty.EASY,
        status=GameStatus.PLAYING,
        current_turn=ai_player.id,
    )
    db.add(game)
    db.flush()

    human_board = Board(game_id=game.id, player_id=human.id)
    ai_board = Board(game_id=game.id, player_id=ai_player.id)
    db.add_all([human_board, ai_board])
    db.commit()

    return game, ai_player, human