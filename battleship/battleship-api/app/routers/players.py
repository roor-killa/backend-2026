from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.player import PlayerCreate, PlayerResponse, LeaderboardEntry
from app.services.game_service import create_player, get_player, get_leaderboard

router = APIRouter(
    prefix="/players",
    tags=["Joueurs"],
)


@router.post(
    "/",
    response_model=PlayerResponse,
    status_code=201,
    summary="Créer un joueur",
    description="Crée un nouveau joueur avec un pseudo unique.",
)
def endpoint_create_player(
    data: PlayerCreate,
    db: Session = Depends(get_db),
):
    return create_player(db, data.pseudo)


@router.get(
    "/leaderboard",
    response_model=list[LeaderboardEntry],
    summary="Classement général",
    description="Retourne les meilleurs joueurs triés par score décroissant.",
)
def endpoint_leaderboard(
    limit: int = Query(default=10, ge=1, le=100, description="Nombre de joueurs à retourner"),
    db: Session = Depends(get_db),
):
    return get_leaderboard(db, limit)


@router.get(
    "/{player_id}",
    response_model=PlayerResponse,
    summary="Profil d'un joueur",
    description="Retourne le profil d'un joueur par son ID.",
)
def endpoint_get_player(
    player_id: int,
    db: Session = Depends(get_db),
):
    return get_player(db, player_id)