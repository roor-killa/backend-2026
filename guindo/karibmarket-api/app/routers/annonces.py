from fastapi import APIRouter, HTTPException, Depends, status, Query, BackgroundTasks
from fastapi_cache.decorator import cache
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.database import get_db
from app.models.annonce import Annonce
from app.schemas.annonce import AnnonceCreate, AnnonceUpdate, AnnonceResponse
from app.routers.auth import get_current_user
from app.models.utilisateur import Utilisateur

router = APIRouter()
logger = logging.getLogger(__name__)


# ----------------------------
# Background Tasks
# ----------------------------
def envoyer_email_confirmation(email: str, titre_annonce: str):
    """Simule l'envoi d'un email de confirmation après création d'annonce."""
    logger.info(f"📧 Email de confirmation envoyé à {email} pour '{titre_annonce}'")


def notifier_moderateurs(annonce_id: int, titre: str):
    """Notifie les modérateurs d'une nouvelle annonce à valider."""
    logger.info(f"🔔 Nouvelle annonce #{annonce_id} '{titre}' à modérer")


# ----------------------------
# CREATE annonce (async + BackgroundTasks)
# ----------------------------
@router.post("/annonces", response_model=AnnonceResponse, status_code=status.HTTP_201_CREATED)
async def create_annonce(
    annonce: AnnonceCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    nouvelle_annonce = Annonce(
        **annonce.model_dump(),
        proprietaire_id=current_user.id
    )

    db.add(nouvelle_annonce)
    db.commit()
    db.refresh(nouvelle_annonce)

    background_tasks.add_task(
        envoyer_email_confirmation,
        current_user.email,
        annonce.titre
    )
    background_tasks.add_task(
        notifier_moderateurs,
        nouvelle_annonce.id,
        annonce.titre
    )

    return nouvelle_annonce


# ----------------------------
# LIST annonces (async + cache Redis 60s)
# ----------------------------
@router.get("/annonces", response_model=List[AnnonceResponse])
@cache(expire=60)  # ← Mise en cache 60 secondes
async def list_annonces(
    commune: Optional[str] = Query(None),
    categorie: Optional[str] = Query(None),
    page: int = Query(1, gt=0),
    limit: int = Query(10, gt=0, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Annonce).filter(Annonce.actif == True)

    if commune:
        query = query.filter(Annonce.commune.ilike(f"%{commune}%"))

    if categorie:
        query = query.filter(Annonce.categorie == categorie)

    annonces = query.offset((page - 1) * limit).limit(limit).all()

    return annonces


# ----------------------------
# GET annonce par id (async)
# ----------------------------
@router.get("/annonces/{annonce_id}", response_model=AnnonceResponse)
@cache(expire=120)  # ← Cache 2 minutes
async def get_annonce(annonce_id: int, db: Session = Depends(get_db)):

    annonce = db.query(Annonce).filter(Annonce.id == annonce_id).first()

    if not annonce:
        raise HTTPException(status_code=404, detail="Annonce introuvable")

    return annonce


# ----------------------------
# UPDATE annonce (async)
# ----------------------------
@router.patch("/annonces/{annonce_id}", response_model=AnnonceResponse)
async def update_annonce(
        annonce_id: int,
        modifications: AnnonceUpdate,
        db: Session = Depends(get_db),
        current_user: Utilisateur = Depends(get_current_user)
):
    annonce = db.query(Annonce).filter(Annonce.id == annonce_id).first()

    if not annonce:
        raise HTTPException(status_code=404, detail="Annonce introuvable")

    if annonce.proprietaire_id != current_user.id:
        raise HTTPException(status_code=403, detail="Non autorisé")

    changements = modifications.model_dump(exclude_unset=True)
    for champ, valeur in changements.items():
        setattr(annonce, champ, valeur)

    db.commit()
    db.refresh(annonce)

    return annonce


# ----------------------------
# DELETE annonce (soft delete, async)
# ----------------------------
@router.delete("/annonces/{annonce_id}", status_code=204)
async def delete_annonce(
    annonce_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    annonce = db.query(Annonce).filter(Annonce.id == annonce_id).first()

    if not annonce:
        raise HTTPException(status_code=404, detail="Annonce introuvable")

    if annonce.proprietaire_id != current_user.id:
        raise HTTPException(status_code=403, detail="Non autorisé")

    annonce.actif = False
    db.commit()