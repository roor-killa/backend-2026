from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.annonce import Annonce
from app.schemas.annonce import AnnonceCreate, AnnonceUpdate, AnnonceResponse

router = APIRouter()


# ----------------------------
# CREATE annonce
# ----------------------------
@router.post("/annonces", response_model=AnnonceResponse, status_code=status.HTTP_201_CREATED)
def create_annonce(
        annonce: AnnonceCreate,
        db: Session = Depends(get_db)
):
    nouvelle_annonce = Annonce(**annonce.model_dump())

    db.add(nouvelle_annonce)
    db.commit()
    db.refresh(nouvelle_annonce)

    return nouvelle_annonce


# ----------------------------
# LIST annonces
# ----------------------------
@router.get("/annonces", response_model=List[AnnonceResponse])
def list_annonces(
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
# GET annonce par id
# ----------------------------
@router.get("/annonces/{annonce_id}", response_model=AnnonceResponse)
def get_annonce(annonce_id: int, db: Session = Depends(get_db)):

    annonce = db.query(Annonce).filter(Annonce.id == annonce_id).first()

    if not annonce:
        raise HTTPException(
            status_code=404,
            detail="Annonce introuvable"
        )

    return annonce


# ----------------------------
# UPDATE annonce
# ----------------------------
@router.patch("/annonces/{annonce_id}", response_model=AnnonceResponse)
def update_annonce(
        annonce_id: int,
        modifications: AnnonceUpdate,
        db: Session = Depends(get_db)
):

    annonce = db.query(Annonce).filter(Annonce.id == annonce_id).first()

    if not annonce:
        raise HTTPException(
            status_code=404,
            detail="Annonce introuvable"
        )

    changements = modifications.model_dump(exclude_unset=True)

    for champ, valeur in changements.items():
        setattr(annonce, champ, valeur)

    db.commit()
    db.refresh(annonce)

    return annonce


# ----------------------------
# DELETE annonce (soft delete)
# ----------------------------
@router.delete("/annonces/{annonce_id}", status_code=204)
def delete_annonce(annonce_id: int, db: Session = Depends(get_db)):

    annonce = db.query(Annonce).filter(Annonce.id == annonce_id).first()

    if not annonce:
        raise HTTPException(
            status_code=404,
            detail="Annonce introuvable"
        )

    annonce.actif = False
    db.commit()