from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.shot import ShotCreate, ShotResponse, ShotHistoryResponse
from app.services.game_service import process_shot, get_shots, get_game
from app.services.ai_service import ai_shoot
from app.models.game import Game
from app.core.constants import GameMode, GameStatus

router = APIRouter(
    prefix="/games",
    tags=["Tirs"],
)


@router.post(
    "/{game_id}/shoot",
    response_model=ShotResponse,
    summary="Effectuer un tir",
    description="""
    Tire sur une case de la grille ennemie.
    - Retourne le résultat : **miss** (à l'eau), **hit** (touché), **sunk** (coulé)
    - Si `game_over` est `true`, la partie est terminée
    - En mode **solo**, l'IA joue automatiquement après le tir du joueur
    """,
)
def endpoint_shoot(
    game_id: int,
    data: ShotCreate,
    db: Session = Depends(get_db),
):
    # Tir du joueur humain
    result = process_shot(db, game_id, data)

    # En mode solo et partie non terminée → l'IA joue immédiatement
    if not result["game_over"]:
        game = get_game(db, game_id)

        if game.mode == GameMode.SOLO and game.status == GameStatus.PLAYING:
            # Récupérer le joueur IA et la difficulté
            from app.models.board import Board
            from app.models.player import Player

            ai_board = (
                db.query(Board)
                .join(Player, Player.id == Board.player_id)
                .filter(Board.game_id == game_id, Player.pseudo == "IA")
                .first()
            )

            if ai_board and game.current_turn == ai_board.player_id:
                ai_shot_data = ai_shoot(
                    db,
                    game_id,
                    ai_board.player_id,
                    game.difficulty,
                )
                # Traiter le tir de l'IA (résultat ignoré côté réponse,
                # le client verra la mise à jour au prochain GET /board)
                process_shot(db, game_id, ai_shot_data)

    return result


@router.get(
    "/{game_id}/shots",
    response_model=ShotHistoryResponse,
    summary="Historique des tirs",
    description="Retourne tous les tirs effectués dans une partie.",
)
def endpoint_get_shots(
    game_id: int,
    db: Session = Depends(get_db),
):
    return get_shots(db, game_id)