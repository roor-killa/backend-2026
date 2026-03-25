
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from fastapi_cache.decorator import cache
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.annonce import Annonce, CategorieEnum
from app.schemas.annonce import (
    AnnonceCreate,
    AnnonceResponse,
    AnnonceUpdate,
    CategorieAnnonce,
)

from app.routeurs.auth import get_current_user
from app.models.utilisateur import Utilisateur

router = APIRouter()


def to_model_categorie(categorie: CategorieAnnonce) -> CategorieEnum:
    return CategorieEnum(categorie.value)

def envoyer_email_confirmation(email: str, titre_annonce: str):
    """Tâche qui s'exécute après avoir répondu au client"""
    print(f"📧 Envoi email de confirmation à {email} pour '{titre_annonce}'")
    # Logique d'envoi d'email ici (simulée)
    # En production : utiliser une bibliothèque comme fastapi-mail

def notifier_moderateurs(annonce_id: int):
    """Notifier les modérateurs d'une nouvelle annonce à valider"""
    print(f"🔔 Nouvelle annonce #{annonce_id} à modérer")


@router.get("/annonces", response_model=List[AnnonceResponse])
@cache(expire=60)  # ← Cette réponse est mise en cache 60 secondes
async def list_annonces(
    commune: Optional[str] = Query(None),
    categorie: Optional[CategorieAnnonce] = Query(None),
    page: int = Query(1, gt=0),
    limit: int = Query(10, gt=0, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Annonce).filter(Annonce.actif.is_(True))

    if commune:
        query = query.filter(Annonce.commune.ilike(f"%{commune}%"))
    if categorie:
        query = query.filter(Annonce.categorie == to_model_categorie(categorie))

    return query.offset((page - 1) * limit).limit(limit).all()


@router.post(
    "/annonces",
    response_model=AnnonceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_annonce(
    annonce_data: AnnonceCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)  # ← Requiert une auth
):  
    payload = annonce_data.model_dump()
    payload["categorie"] = to_model_categorie(annonce_data.categorie)

    nouvelle_annonce = Annonce(
        **annonce_data.model_dump(),
        proprietaire_id=current_user.id  # Lier l'annonce à l'utilisateur connecté
    )
    db.add(nouvelle_annonce)
    db.commit()
    db.refresh(nouvelle_annonce)

    background_tasks.add_task(envoyer_email_confirmation, current_user.email, annonce_data.titre)
    background_tasks.add_task(notifier_moderateurs, nouvelle_annonce.id)

    return nouvelle_annonce


@router.get("/annonces/{annonce_id}", response_model=AnnonceResponse)
def get_annonce(annonce_id: int, db: Session = Depends(get_db)):
    annonce = db.query(Annonce).filter(Annonce.id == annonce_id).first()
    if not annonce or not annonce.actif:
        raise HTTPException(status_code=404, detail="Annonce introuvable")
    return annonce


@router.patch("/annonces/{annonce_id}", response_model=AnnonceResponse)
def update_annonce(
    annonce_id: int,
    modifications: AnnonceUpdate,
    db: Session = Depends(get_db),
):
    annonce = db.query(Annonce).filter(Annonce.id == annonce_id).first()
    if not annonce or not annonce.actif:
        raise HTTPException(status_code=404, detail="Annonce introuvable")

    changements = modifications.model_dump(exclude_unset=True)
    if "categorie" in changements and changements["categorie"] is not None:
        changements["categorie"] = to_model_categorie(changements["categorie"])

    for champ, valeur in changements.items():
        setattr(annonce, champ, valeur)

    db.commit()
    db.refresh(annonce)
    return annonce


@router.delete("/annonces/{annonce_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_annonce(annonce_id: int, db: Session = Depends(get_db), current_user: Utilisateur = Depends(get_current_user)):
    annonce = db.query(Annonce).filter(Annonce.id == annonce_id).first()
    if not annonce or not annonce.actif:
        raise HTTPException(status_code=404, detail="Annonce introuvable")
    
    if annonce.proprietaire_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez supprimer que vos propres annonces"
        )

    annonce.actif = False
    db.commit()