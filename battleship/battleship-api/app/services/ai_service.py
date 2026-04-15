import random
from sqlalchemy.orm import Session

from app.models.board  import Board
from app.models.ship   import Ship
from app.models.shot   import Shot
from app.schemas.shot  import ShotCreate
from app.core.constants import Difficulty, ShotResult, SHIPS, GRID_SIZE


# ═══════════════════════════════════════════════════════
# POINT D'ENTRÉE PRINCIPAL
# ═══════════════════════════════════════════════════════

def ai_place_ships(db: Session, board: Board) -> None:
    """
    Place aléatoirement les bateaux de l'IA sur son board.
    Appelé automatiquement à la création d'une partie solo.
    """
    occupied: set[tuple] = set()
    grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]

    for ship_type, size in SHIPS.items():
        placed = False
        attempts = 0

        while not placed and attempts < 200:
            attempts += 1
            orientation = random.choice(["horizontal", "vertical"])

            if orientation == "horizontal":
                row = random.randint(0, GRID_SIZE - 1)
                col = random.randint(0, GRID_SIZE - size)
                positions = [[row, col + i] for i in range(size)]
            else:
                row = random.randint(0, GRID_SIZE - size)
                col = random.randint(0, GRID_SIZE - 1)
                positions = [[row + i, col] for i in range(size)]

            # Vérifier qu'aucune case n'est déjà occupée
            if all(tuple(p) not in occupied for p in positions):
                for p in positions:
                    occupied.add(tuple(p))
                    grid[p[0]][p[1]] = 1

                ship = Ship(
                    board_id=board.id,
                    type=ship_type,
                    positions=positions,
                    orientation=orientation,
                )
                db.add(ship)
                placed = True

    board.grid = grid
    db.flush()


def ai_shoot(db: Session, game_id: int, ai_player_id: int, difficulty: str) -> ShotCreate:
    """
    Calcule le prochain tir de l'IA selon le niveau de difficulté.
    Retourne un ShotCreate prêt à être traité par game_service.process_shot().
    """
    if difficulty == Difficulty.EASY:
        row, col = _easy_shot(db, game_id, ai_player_id)
    elif difficulty == Difficulty.MEDIUM:
        row, col = _medium_shot(db, game_id, ai_player_id)
    else:
        row, col = _hard_shot(db, game_id, ai_player_id)

    return ShotCreate(player_id=ai_player_id, row=row, col=col)


# ═══════════════════════════════════════════════════════
# NIVEAU FACILE — Tirs aléatoires
# ═══════════════════════════════════════════════════════

def _easy_shot(db: Session, game_id: int, ai_player_id: int) -> tuple[int, int]:
    """Tire aléatoirement sur une case non encore jouée."""
    played = _get_played_cells(db, game_id, ai_player_id)

    available = [
        (r, c)
        for r in range(GRID_SIZE)
        for c in range(GRID_SIZE)
        if (r, c) not in played
    ]
    return random.choice(available)


# ═══════════════════════════════════════════════════════
# NIVEAU MOYEN — Cible les cases adjacentes après touché
# ═══════════════════════════════════════════════════════

def _medium_shot(db: Session, game_id: int, ai_player_id: int) -> tuple[int, int]:
    """
    Si l'IA a touché un bateau non coulé, cible les cases adjacentes.
    Sinon, tire aléatoirement.
    """
    played = _get_played_cells(db, game_id, ai_player_id)
    hit_cells = _get_hit_cells(db, game_id, ai_player_id)

    if hit_cells:
        # Chercher les cases adjacentes non jouées autour des touches
        candidates = set()
        for r, c in hit_cells:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if (
                    0 <= nr < GRID_SIZE
                    and 0 <= nc < GRID_SIZE
                    and (nr, nc) not in played
                ):
                    candidates.add((nr, nc))

        if candidates:
            return random.choice(list(candidates))

    # Pas de touché actif → tir aléatoire
    return _easy_shot(db, game_id, ai_player_id)


# ═══════════════════════════════════════════════════════
# NIVEAU DIFFICILE — Carte de probabilités
# ═══════════════════════════════════════════════════════

def _hard_shot(db: Session, game_id: int, ai_player_id: int) -> tuple[int, int]:
    """
    Algorithme de chasse par carte de probabilités.

    Principe :
    1. Pour chaque bateau non coulé, on calcule toutes les positions
       possibles où il pourrait encore se trouver (cases libres, non jouées).
    2. Chaque case reçoit un score = nombre de positions possibles qui la couvrent.
    3. L'IA tire sur la case avec le score le plus élevé.

    Si un bateau est en cours de touche (hit sans sunk), on restreint
    la recherche aux cases alignées avec les touches existantes.
    """
    played = _get_played_cells(db, game_id, ai_player_id)
    hit_cells = _get_hit_cells(db, game_id, ai_player_id)
    shots = _get_all_shots(db, game_id, ai_player_id)

    # Cases manquées
    miss_cells = {(s.row, s.col) for s in shots if s.result == ShotResult.MISS}

    # Bateaux déjà coulés → on les retire de la liste
    enemy_board = _get_enemy_board(db, game_id, ai_player_id)
    sunk_ships = db.query(Ship).filter(
        Ship.board_id == enemy_board.id,
        Ship.is_sunk == True
    ).all()
    sunk_types = [s.type for s in sunk_ships]

    remaining_ships = {
        ship_type: size
        for ship_type, size in SHIPS.items()
        if ship_type not in sunk_types
    }

    # Si un bateau est touché mais pas coulé → mode chasse alignée
    if hit_cells:
        return _hunt_aligned(hit_cells, played, miss_cells)

    # Construire la carte de probabilités
    prob_map = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]

    for ship_type, size in remaining_ships.items():
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                # Essai horizontal
                if c + size <= GRID_SIZE:
                    positions = [(r, c + i) for i in range(size)]
                    if _positions_valid(positions, played, miss_cells):
                        for pr, pc in positions:
                            prob_map[pr][pc] += 1

                # Essai vertical
                if r + size <= GRID_SIZE:
                    positions = [(r + i, c) for i in range(size)]
                    if _positions_valid(positions, played, miss_cells):
                        for pr, pc in positions:
                            prob_map[pr][pc] += 1

    # Trouver la case avec le score maximum parmi les cases non jouées
    best_score = -1
    best_cells = []

    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if (r, c) not in played and prob_map[r][c] > best_score:
                best_score = prob_map[r][c]
                best_cells = [(r, c)]
            elif (r, c) not in played and prob_map[r][c] == best_score:
                best_cells.append((r, c))

    if best_cells:
        return random.choice(best_cells)

    # Fallback : tir aléatoire
    return _easy_shot(db, game_id, ai_player_id)


def _hunt_aligned(
    hit_cells: set,
    played: set,
    miss_cells: set
) -> tuple[int, int]:
    """
    Quand un bateau est partiellement touché, tire dans l'alignement
    des touches existantes (horizontal ou vertical).
    """
    hits = list(hit_cells)

    # Déterminer si les touches sont alignées horizontalement ou verticalement
    rows = {h[0] for h in hits}
    cols = {h[1] for h in hits}

    candidates = []

    if len(rows) == 1:
        # Alignement horizontal → chercher à gauche et à droite
        r = list(rows)[0]
        min_c = min(cols)
        max_c = max(cols)
        for c in [min_c - 1, max_c + 1]:
            if 0 <= c < GRID_SIZE and (r, c) not in played:
                candidates.append((r, c))

    if len(cols) == 1:
        # Alignement vertical → chercher en haut et en bas
        c = list(cols)[0]
        min_r = min(rows)
        max_r = max(rows)
        for r in [min_r - 1, max_r + 1]:
            if 0 <= r < GRID_SIZE and (r, c) not in played:
                candidates.append((r, c))

    if not candidates:
        # Chercher dans toutes les directions autour des touches
        for r, c in hits:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE and (nr, nc) not in played:
                    candidates.append((nr, nc))

    if candidates:
        return random.choice(candidates)

    # Fallback
    available = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if (r, c) not in played]
    return random.choice(available)


# ═══════════════════════════════════════════════════════
# HELPERS PRIVÉS
# ═══════════════════════════════════════════════════════

def _get_played_cells(db: Session, game_id: int, player_id: int) -> set[tuple]:
    """Retourne toutes les cases déjà jouées par un joueur."""
    shots = db.query(Shot).filter(
        Shot.game_id == game_id,
        Shot.player_id == player_id
    ).all()
    return {(s.row, s.col) for s in shots}


def _get_hit_cells(db: Session, game_id: int, player_id: int) -> set[tuple]:
    """Retourne les cases touchées mais dont le bateau n'est pas encore coulé."""
    shots = db.query(Shot).filter(
        Shot.game_id == game_id,
        Shot.player_id == player_id,
        Shot.result == ShotResult.HIT
    ).all()
    return {(s.row, s.col) for s in shots}


def _get_all_shots(db: Session, game_id: int, player_id: int):
    """Retourne tous les tirs d'un joueur dans une partie."""
    return db.query(Shot).filter(
        Shot.game_id == game_id,
        Shot.player_id == player_id
    ).all()


def _get_enemy_board(db: Session, game_id: int, ai_player_id: int) -> Board:
    """Retourne le board du joueur humain (opposé à l'IA)."""
    return db.query(Board).filter(
        Board.game_id == game_id,
        Board.player_id != ai_player_id
    ).first()


def _positions_valid(
    positions: list[tuple],
    played: set,
    miss_cells: set
) -> bool:
    """
    Vérifie qu'un ensemble de positions est valide pour placer un bateau :
    - Aucune case jouée (miss)
    - Toutes les cases dans la grille
    """
    return all(
        0 <= r < GRID_SIZE
        and 0 <= c < GRID_SIZE
        and (r, c) not in miss_cells
        for r, c in positions
    )