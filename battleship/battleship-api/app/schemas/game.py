from pydantic import BaseModel, Field, model_validator
from typing import Optional
from app.core.constants import GameMode, GameStatus, Difficulty, GRID_SIZE, SHIPS


# ── Création d'une partie ──────────────────────────────
class GameCreate(BaseModel):
    mode: str = Field(
        default=GameMode.SOLO,
        description="Mode de jeu : 'solo' ou 'multiplayer'"
    )
    difficulty: Optional[str] = Field(
        default=Difficulty.EASY,
        description="Niveau IA (solo uniquement) : 'easy', 'medium', 'hard'"
    )

    @model_validator(mode="after")
    def validate_difficulty(self) -> "GameCreate":
        """En mode solo, la difficulté est obligatoire et doit être valide."""
        valid_modes = [GameMode.SOLO, GameMode.MULTIPLAYER]
        if self.mode not in valid_modes:
            raise ValueError(f"Mode invalide. Valeurs acceptées : {valid_modes}")

        if self.mode == GameMode.SOLO:
            valid_difficulties = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]
            if self.difficulty not in valid_difficulties:
                raise ValueError(f"Difficulté invalide. Valeurs acceptées : {valid_difficulties}")
        else:
            # En multijoueur, la difficulté n'a pas de sens
            self.difficulty = None
        return self


# ── Rejoindre une partie (multijoueur) ────────────────
class GameJoin(BaseModel):
    player_id: int = Field(..., description="ID du joueur qui rejoint la partie")


# ── Placement d'un bateau ─────────────────────────────
class ShipPlacement(BaseModel):
    type:        str = Field(..., description="Type de bateau (ex: 'carrier')")
    row:         int = Field(..., ge=0, lt=GRID_SIZE, description="Ligne de départ (0-9)")
    col:         int = Field(..., ge=0, lt=GRID_SIZE, description="Colonne de départ (0-9)")
    orientation: str = Field(..., description="'horizontal' ou 'vertical'")

    @model_validator(mode="after")
    def validate_ship(self) -> "ShipPlacement":
        # Vérifier que le type de bateau est valide
        if self.type not in SHIPS:
            raise ValueError(f"Type de bateau invalide. Valeurs acceptées : {list(SHIPS.keys())}")

        # Vérifier l'orientation
        if self.orientation not in ["horizontal", "vertical"]:
            raise ValueError("Orientation invalide : 'horizontal' ou 'vertical'")

        # Vérifier que le bateau reste dans la grille
        size = SHIPS[self.type]
        if self.orientation == "horizontal" and self.col + size > GRID_SIZE:
            raise ValueError(f"Le bateau dépasse la grille horizontalement")
        if self.orientation == "vertical" and self.row + size > GRID_SIZE:
            raise ValueError(f"Le bateau dépasse la grille verticalement")

        return self


# ── Placement de tous les bateaux d'un joueur ─────────
class PlaceShipsRequest(BaseModel):
    player_id: int = Field(..., description="ID du joueur qui place ses bateaux")
    ships: list[ShipPlacement] = Field(..., description="Liste des 5 bateaux à placer")

    @model_validator(mode="after")
    def validate_all_ships(self) -> "PlaceShipsRequest":
        # Vérifier que tous les types de bateaux sont présents
        types_placed = [s.type for s in self.ships]
        required = list(SHIPS.keys())

        missing = [t for t in required if t not in types_placed]
        if missing:
            raise ValueError(f"Bateaux manquants : {missing}")

        duplicates = [t for t in types_placed if types_placed.count(t) > 1]
        if duplicates:
            raise ValueError(f"Bateaux en double : {list(set(duplicates))}")

        return self


# ── Réponse d'une partie ──────────────────────────────
class GameResponse(BaseModel):
    id:           int
    mode:         str
    difficulty:   Optional[str]
    status:       str
    current_turn: Optional[int]
    winner_id:    Optional[int]

    model_config = {"from_attributes": True}


# ── Réponse des grilles ───────────────────────────────
class BoardResponse(BaseModel):
    player_id:    int
    grid:         list[list[int]]   # Grille 10x10

    model_config = {"from_attributes": True}


class BothBoardsResponse(BaseModel):
    my_board:    BoardResponse     # Ma grille (avec mes bateaux visibles)
    enemy_board: BoardResponse     # Grille ennemie (bateaux cachés)