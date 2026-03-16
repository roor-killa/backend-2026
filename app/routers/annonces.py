from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.annonce import Annonce
from app.models.utilisateur import Utilisateur
from app.routers.auth import get_current_user
from app.schemas.annonce import (
    AnnonceCreate,
    AnnonceResponse,
    AnnonceUpdate,
    CategorieAnnonce,
)

router = APIRouter()


@router.get("/annonces", response_model=list[AnnonceResponse])
def list_annonces(
    commune: str | None = Query(default=None),
    categorie: CategorieAnnonce | None = Query(default=None),
    page: int = Query(default=1, gt=0),
    limit: int = Query(default=10, gt=0, le=100),
    db: Session = Depends(get_db),
) -> list[Annonce]:
    query = select(Annonce).where(Annonce.actif.is_(True))

    if commune:
        query = query.where(Annonce.commune.ilike(f"%{commune}%"))

    if categorie:
        query = query.where(Annonce.categorie == categorie)

    query = query.offset((page - 1) * limit).limit(limit)
    return list(db.execute(query).scalars().all())


@router.get("/annonces/{annonce_id}", response_model=AnnonceResponse)
def get_annonce(annonce_id: int, db: Session = Depends(get_db)) -> Annonce:
    annonce = db.get(Annonce, annonce_id)
    if annonce and annonce.actif:
        return annonce

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Annonce {annonce_id} introuvable",
    )


@router.post(
    "/annonces",
    response_model=AnnonceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_annonce(
    payload: AnnonceCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
) -> Annonce:
    nouvelle_annonce = Annonce(
        **payload.model_dump(),
        proprietaire_id=current_user.id,
        actif=True,
        created_at=datetime.utcnow(),
        updated_at=None,
    )
    db.add(nouvelle_annonce)
    db.commit()
    db.refresh(nouvelle_annonce)
    return nouvelle_annonce


@router.patch("/annonces/{annonce_id}", response_model=AnnonceResponse)
def update_annonce(
    annonce_id: int,
    modifications: AnnonceUpdate,
    db: Session = Depends(get_db),
) -> Annonce:
    annonce = db.get(Annonce, annonce_id)
    if annonce and annonce.actif:
        changements = modifications.model_dump(exclude_unset=True)
        for key, value in changements.items():
            setattr(annonce, key, value)
        annonce.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(annonce)
        return annonce

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Annonce {annonce_id} introuvable",
    )


@router.delete(
    "/annonces/{annonce_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_annonce(
    annonce_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
) -> None:
    annonce = db.get(Annonce, annonce_id)
    if annonce and annonce.actif:
        if annonce.proprietaire_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous ne pouvez supprimer que vos propres annonces",
            )
        annonce.actif = False
        annonce.updated_at = datetime.utcnow()
        db.commit()
        return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Annonce {annonce_id} introuvable",
    )
