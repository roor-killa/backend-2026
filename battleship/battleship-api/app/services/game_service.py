from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.player import Player
from app.models.game   import Game
from app.models.board  import Board, empty_grid
from app.models.ship   import Ship
from app.models.shot   import Shot
from app.schemas.game  import GameCreate, PlaceShipsRequest, ShipPlacement
from app.schemas.shot  import ShotCreate
from app.core.constants import (
    GameStatus, GameMode, ShotResult, SHIPS, GRID_SIZE
)


# ═══════════════════════════════════════════════════════
# JOUEURS
# ═══════════════════════════════════════════════════════

def create_player(db: Session, pseudo: str) -> Player:
    """Crée un nouveau joueur. Lève 400 si le pseudo est déjà pris."""
    existing = db.query(Player).filter(Player.pseudo == pseudo).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Le pseudo '{pseudo}' est déjà utilisé."
        )
    player = Player(pseudo=pseudo)
    db.add(player)
    db.commit()
    db.refresh(player)
    return player


def get_player(db: Session, player_id: int) -> Player:
    """Retourne un joueur par son ID. Lève 404 si introuvable."""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Joueur {player_id} introuvable."
        )
    return player


def get_leaderboard(db: Session, limit: int = 10) -> list[dict]:
    """Retourne les meilleurs joueurs triés par score décroissant."""
    players = (
        db.query(Player)
        .order_by(Player.score.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "rank":         rank + 1,
            "id":           p.id,
            "pseudo":       p.pseudo,
            "score":        p.score,
            "games_played": p.games_played,
        }
        for rank, p in enumerate(players)
    ]


# ═══════════════════════════════════════════════════════
# PARTIES
# ═══════════════════════════════════════════════════════

def create_game(db: Session, data: GameCreate, player_id: int) -> Game:
    """
    Crée une nouvelle partie.
    - Solo     : crée la partie + le board du joueur + place les bateaux de l'IA
    - Multi    : crée la partie en attente d'un second joueur
    """
    # Vérifier que le joueur existe
    player = get_player(db, player_id)

    game = Game(
        mode=data.mode,
        difficulty=data.difficulty,
        status=GameStatus.PLACEMENT,
        current_turn=player_id,
    )
    db.add(game)
    db.flush()  # Pour obtenir game.id sans commit

    # Créer le board du joueur
    board = Board(game_id=game.id, player_id=player_id)
    db.add(board)
    db.flush()

    if data.mode == GameMode.MULTIPLAYER:
        # En attente du second joueur
        game.status = GameStatus.WAITING

    db.commit()
    db.refresh(game)
    return game


def join_game(db: Session, game_id: int, player_id: int) -> Game:
    """
    Permet à un second joueur de rejoindre une partie multijoueur.
    """
    game = _get_game_or_404(db, game_id)

    if game.mode != GameMode.MULTIPLAYER:
        raise HTTPException(400, "Cette partie n'est pas en mode multijoueur.")
    if game.status != GameStatus.WAITING:
        raise HTTPException(400, "Cette partie n'est plus disponible.")

    # Vérifier que le joueur n'est pas déjà dans la partie
    existing_board = (
        db.query(Board)
        .filter(Board.game_id == game_id, Board.player_id == player_id)
        .first()
    )
    if existing_board:
        raise HTTPException(400, "Vous êtes déjà dans cette partie.")

    # Créer le board du second joueur
    board = Board(game_id=game_id, player_id=player_id)
    db.add(board)

    # Passer en phase de placement
    game.status = GameStatus.PLACEMENT
    db.commit()
    db.refresh(game)
    return game


def place_ships(db: Session, game_id: int, data: PlaceShipsRequest) -> Game:
    """
    Place les bateaux d'un joueur sur sa grille.
    Vérifie les chevauchements et démarre la partie si les deux joueurs ont placé.
    """
    game = _get_game_or_404(db, game_id)

    if game.status != GameStatus.PLACEMENT:
        raise HTTPException(400, "Ce n'est pas la phase de placement.")

    board = (
        db.query(Board)
        .filter(Board.game_id == game_id, Board.player_id == data.player_id)
        .first()
    )
    if not board:
        raise HTTPException(404, "Board introuvable pour ce joueur dans cette partie.")

    # Vérifier que le joueur n'a pas déjà placé ses bateaux
    if db.query(Ship).filter(Ship.board_id == board.id).count() > 0:
        raise HTTPException(400, "Vous avez déjà placé vos bateaux.")

    # Calculer les positions de chaque bateau et vérifier les chevauchements
    occupied: set[tuple] = set()
    ships_to_add = []

    for ship_data in data.ships:
        positions = _compute_positions(ship_data)

        # Vérifier les chevauchements
        for pos in positions:
            if tuple(pos) in occupied:
                raise HTTPException(
                    400,
                    f"Le bateau '{ship_data.type}' chevauche un autre bateau."
                )
            occupied.add(tuple(pos))

        ship = Ship(
            board_id=board.id,
            type=ship_data.type,
            positions=positions,
            orientation=ship_data.orientation,
        )
        ships_to_add.append(ship)

        # Mettre à jour la grille : marquer les cases occupées avec 1
        grid = [row[:] for row in board.grid]  # Copie profonde
        for r, c in positions:
            grid[r][c] = 1
        board.grid = grid

    for ship in ships_to_add:
        db.add(ship)

    # Vérifier si les deux joueurs ont placé leurs bateaux → démarrer la partie
    all_boards = db.query(Board).filter(Board.game_id == game_id).all()
    all_placed = all(
        db.query(Ship).filter(Ship.board_id == b.id).count() == len(SHIPS)
        for b in all_boards
    )
    if all_placed:
        game.status = GameStatus.PLAYING

    db.commit()
    db.refresh(game)
    return game


def get_game(db: Session, game_id: int) -> Game:
    return _get_game_or_404(db, game_id)


def get_boards(db: Session, game_id: int, requesting_player_id: int) -> dict:
    """
    Retourne les deux grilles.
    - Ma grille    : avec mes bateaux visibles (valeur 1)
    - Grille ennemie : bateaux masqués (les 1 sont remplacés par 0)
    """
    _get_game_or_404(db, game_id)

    boards = db.query(Board).filter(Board.game_id == game_id).all()
    if not boards:
        raise HTTPException(404, "Aucun board trouvé pour cette partie.")

    my_board = next((b for b in boards if b.player_id == requesting_player_id), None)
    enemy_board = next((b for b in boards if b.player_id != requesting_player_id), None)

    if not my_board:
        raise HTTPException(403, "Vous n'êtes pas dans cette partie.")

    # Masquer les bateaux ennemis non touchés
    masked_grid = None
    if enemy_board:
        masked_grid = [
            [cell if cell != 1 else 0 for cell in row]
            for row in enemy_board.grid
        ]

    return {
        "my_board": {
            "player_id": my_board.player_id,
            "grid": my_board.grid,
        },
        "enemy_board": {
            "player_id": enemy_board.player_id if enemy_board else None,
            "grid": masked_grid,
        } if enemy_board else None,
    }


# ═══════════════════════════════════════════════════════
# TIRS
# ═══════════════════════════════════════════════════════

def process_shot(db: Session, game_id: int, data: ShotCreate) -> dict:
    """
    Traite un tir d'un joueur.
    Retourne le résultat et indique si la partie est terminée.
    """
    game = _get_game_or_404(db, game_id)

    if game.status != GameStatus.PLAYING:
        raise HTTPException(400, "La partie n'est pas en cours.")
    if game.current_turn != data.player_id:
        raise HTTPException(400, "Ce n'est pas votre tour.")

    # Vérifier que la case n'a pas déjà été jouée
    already_shot = (
        db.query(Shot)
        .filter(
            Shot.game_id == game_id,
            Shot.player_id == data.player_id,
            Shot.row == data.row,
            Shot.col == data.col,
        )
        .first()
    )
    if already_shot:
        raise HTTPException(400, "Vous avez déjà tiré sur cette case.")

    # Trouver le board ennemi
    enemy_board = (
        db.query(Board)
        .filter(Board.game_id == game_id, Board.player_id != data.player_id)
        .first()
    )
    if not enemy_board:
        raise HTTPException(404, "Board ennemi introuvable.")

    # Calculer le résultat du tir
    result, sunk_ship = _evaluate_shot(db, enemy_board, data.row, data.col)

    # Enregistrer le tir
    shot = Shot(
        game_id=game_id,
        player_id=data.player_id,
        row=data.row,
        col=data.col,
        result=result,
    )
    db.add(shot)

    # Mettre à jour la grille ennemie
    grid = [row[:] for row in enemy_board.grid]
    grid[data.row][data.col] = 2 if result in [ShotResult.HIT, ShotResult.SUNK] else 3
    enemy_board.grid = grid

    # Vérifier si la partie est terminée
    game_over = False
    winner_id = None

    all_ships = db.query(Ship).filter(Ship.board_id == enemy_board.id).all()
    if all(ship.is_sunk for ship in all_ships):
        game_over = True
        winner_id = data.player_id
        game.status = GameStatus.FINISHED
        game.winner_id = winner_id

        # Mettre à jour les stats du gagnant
        winner = get_player(db, winner_id)
        winner.score += 100
        winner.games_played += 1

        # Mettre à jour les stats du perdant
        loser = get_player(db, enemy_board.player_id)
        loser.games_played += 1
    else:
        # Passer le tour à l'autre joueur
        game.current_turn = enemy_board.player_id

    db.commit()
    db.refresh(shot)

    return {
        "id":         shot.id,
        "game_id":    game_id,
        "player_id":  data.player_id,
        "row":        data.row,
        "col":        data.col,
        "result":     result,
        "created_at": shot.created_at,
        "game_over":  game_over,
        "winner_id":  winner_id,
    }


def get_shots(db: Session, game_id: int) -> dict:
    """Retourne l'historique complet des tirs d'une partie."""
    _get_game_or_404(db, game_id)
    shots = db.query(Shot).filter(Shot.game_id == game_id).all()
    return {"shots": shots, "total": len(shots)}


# ═══════════════════════════════════════════════════════
# HELPERS PRIVÉS
# ═══════════════════════════════════════════════════════

def _get_game_or_404(db: Session, game_id: int) -> Game:
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Partie {game_id} introuvable."
        )
    return game


def _compute_positions(ship: ShipPlacement) -> list[list[int]]:
    """Calcule la liste des cases [row, col] occupées par un bateau."""
    size = SHIPS[ship.type]
    if ship.orientation == "horizontal":
        return [[ship.row, ship.col + i] for i in range(size)]
    else:
        return [[ship.row + i, ship.col] for i in range(size)]


def _evaluate_shot(
    db: Session, enemy_board: Board, row: int, col: int
) -> tuple[str, Ship | None]:
    """
    Évalue le résultat d'un tir sur le board ennemi.
    Retourne (résultat, bateau_coulé_ou_None).
    """
    # Chercher si une case d'un bateau correspond aux coordonnées
    ships = db.query(Ship).filter(Ship.board_id == enemy_board.id).all()

    for ship in ships:
        if [row, col] in ship.positions:
            # Vérifier si toutes les autres cases du bateau sont déjà touchées
            shots_on_ship = (
                db.query(Shot)
                .filter(
                    Shot.game_id == enemy_board.game_id,
                    Shot.row.in_([p[0] for p in ship.positions]),
                    Shot.col.in_([p[1] for p in ship.positions]),
                    Shot.result.in_([ShotResult.HIT, ShotResult.SUNK]),
                )
                .all()
            )
            # +1 pour le tir actuel
            hits = len(shots_on_ship) + 1

            if hits == len(ship.positions):
                # Toutes les cases touchées → coulé !
                ship.is_sunk = True
                return ShotResult.SUNK, ship
            else:
                return ShotResult.HIT, None

    return ShotResult.MISS, None