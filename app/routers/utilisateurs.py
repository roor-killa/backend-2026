from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.utilisateur import User
from app.schemas.utilisateur import (
    UtilisateurCreate,
    UtilisateurResponse,
    UtilisateurUpdate,
)

router = APIRouter()

@router.get("/utilisateurs", response_model=list[UtilisateurResponse])
def list_utilisateurs(db: Session = Depends(get_db)) -> list[User]:
    return list(db.execute(select(User)).scalars().all())


@router.get("/utilisateurs/{utilisateur_id}", response_model=UtilisateurResponse)
def get_utilisateur(utilisateur_id: int, db: Session = Depends(get_db)) -> User:
    utilisateur = db.get(User, utilisateur_id)
    if utilisateur:
        return utilisateur

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Utilisateur {utilisateur_id} introuvable",
    )


@router.post(
    "/utilisateurs",
    response_model=UtilisateurResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_utilisateur(payload: UtilisateurCreate, db: Session = Depends(get_db)) -> User:
    existing_user = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet email est deja utilise",
        )

    user = User(**payload.model_dump(), actif=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/utilisateurs/{utilisateur_id}", response_model=UtilisateurResponse)
def update_utilisateur(
    utilisateur_id: int,
    payload: UtilisateurCreate,
    db: Session = Depends(get_db),
) -> User:
    utilisateur = db.get(User, utilisateur_id)
    if not utilisateur:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Utilisateur {utilisateur_id} introuvable",
        )

    existing_email = db.execute(
        select(User).where(User.email == payload.email, User.id != utilisateur_id)
    ).scalar_one_or_none()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet email est deja utilise",
        )

    for key, value in payload.model_dump().items():
        setattr(utilisateur, key, value)

    db.commit()
    db.refresh(utilisateur)
    return utilisateur


@router.patch("/utilisateurs/{utilisateur_id}", response_model=UtilisateurResponse)
def patch_utilisateur(
    utilisateur_id: int,
    modifications: UtilisateurUpdate,
    db: Session = Depends(get_db),
) -> User:
    utilisateur = db.get(User, utilisateur_id)
    if not utilisateur:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Utilisateur {utilisateur_id} introuvable",
        )

    changements = modifications.model_dump(exclude_unset=True)
    if "email" in changements:
        existing_email = db.execute(
            select(User).where(User.email == changements["email"], User.id != utilisateur_id)
        ).scalar_one_or_none()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cet email est deja utilise",
            )

    for key, value in changements.items():
        setattr(utilisateur, key, value)

    db.commit()
    db.refresh(utilisateur)
    return utilisateur


@router.delete("/utilisateurs/{utilisateur_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_utilisateur(utilisateur_id: int, db: Session = Depends(get_db)) -> None:
    utilisateur = db.get(User, utilisateur_id)
    if not utilisateur:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Utilisateur {utilisateur_id} introuvable",
        )

    db.delete(utilisateur)
    db.commit()
