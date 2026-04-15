from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.game import (
    GameCreate, GameJoin, PlaceShipsRequest,
    GameResponse, BothBoardsResponse
)
from app.services import (
    create_game, join_game, place_ships,
    get_game, get_boards, ai_place_ships, ai_shoot
)
from app.services.game_service import process_shot
from app.schemas.shot import ShotCreate
from app.models.board import Board
from app.models.player import Player
from app.core.constants import GameMode, GameStatus

router = APIRouter(
    prefix="/games",
    tags=["Parties"],
)


@router.post(
    "/",
    response_model=GameResponse,
    status_code=201,
    summary="Créer une partie",
    description="Crée une nouvelle partie en mode solo ou multijoueur.",
)
def endpoint_create_game(
    data: GameCreate,
    player_id: int = Query(..., description="ID du joueur qui crée la partie"),
    db: Session = Depends(get_db),
):
    game = create_game(db, data, player_id)

    # En mode solo : l'IA place ses bateaux immédiatement
    if data.mode == GameMode.SOLO:
        # Créer un joueur IA fictif s'il n'existe pas
        ai_player = db.query(Player).filter(Player.pseudo == "IA").first()
        if not ai_player:
            ai_player = Player(pseudo="IA", score=0, games_played=0)
            db.add(ai_player)
            db.flush()

        # Créer le board de l'IA
        ai_board = Board(game_id=game.id, player_id=ai_player.id)
        db.add(ai_board)
        db.flush()

        # Placer les bateaux de l'IA aléatoirement
        ai_place_ships(db, ai_board)
        db.commit()
        db.refresh(game)

    return game


@router.post(
    "/{game_id}/join",
    response_model=GameResponse,
    summary="Rejoindre une partie",
    description="Permet à un second joueur de rejoindre une partie multijoueur.",
)
def endpoint_join_game(
    game_id: int,
    data: GameJoin,
    db: Session = Depends(get_db),
):
    return join_game(db, game_id, data.player_id)


@router.post(
    "/{game_id}/place-ships",
    response_model=GameResponse,
    summary="Placer les bateaux",
    description="Place les 5 bateaux d'un joueur sur sa grille.",
)
def endpoint_place_ships(
    game_id: int,
    data: PlaceShipsRequest,
    db: Session = Depends(get_db),
):
    return place_ships(db, game_id, data)


@router.get(
    "/{game_id}",
    response_model=GameResponse,
    summary="État d'une partie",
    description="Retourne l'état complet d'une partie (statut, tour, gagnant...).",
)
def endpoint_get_game(
    game_id: int,
    db: Session = Depends(get_db),
):
    return get_game(db, game_id)


@router.get(
    "/{game_id}/board",
    summary="Grilles de jeu",
    description="Retourne les deux grilles. Les bateaux ennemis non touchés sont masqués.",
)
def endpoint_get_boards(
    game_id: int,
    player_id: int = Query(..., description="ID du joueur qui consulte les grilles"),
    db: Session = Depends(get_db),
):
    return get_boards(db, game_id, player_id)