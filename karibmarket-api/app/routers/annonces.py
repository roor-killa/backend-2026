from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas.annonce import (
    AnnonceCreate,
    AnnonceUpdate,
    AnnonceResponse
)
from app.database import get_db
from app.models.annonce import Annonce

router = APIRouter()


# GET liste
@router.get("/annonces")
def list_annonces(db: Session = Depends(get_db)):
    return db.query(Annonce).filter(Annonce.actif == True).all()


# GET détail
@router.get("/annonces/{id}")
def get_annonce(id: int, db: Session = Depends(get_db)):
    annonce = db.query(Annonce).filter(Annonce.id == id).first()
    if not annonce:
        raise HTTPException(status_code=404, detail="Annonce introuvable")
    return annonce


# POST créer
@router.post("/annonces", response_model=AnnonceResponse)
def create_annonce(data: AnnonceCreate, db: Session = Depends(get_db)):
    annonce = Annonce(**data.model_dump())
    db.add(annonce)
    db.commit()
    db.refresh(annonce)
    return annonce


# PATCH modifier
@router.patch("/annonces/{id}", response_model=AnnonceResponse)
def update_annonce(id: int, data: AnnonceUpdate, db: Session = Depends(get_db)):
    annonce = db.query(Annonce).filter(Annonce.id == id).first()
    if not annonce:
        raise HTTPException(status_code=404, detail="Annonce introuvable")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(annonce, key, value)
    db.commit()
    db.refresh(annonce)
    return annonce


# DELETE supprimer
@router.delete("/annonces/{id}")
def delete_annonce(id: int, db: Session = Depends(get_db)):
    annonce = db.query(Annonce).filter(Annonce.id == id).first()
    if not annonce:
        raise HTTPException(status_code=404, detail="Annonce introuvable")
    annonce.actif = False
    db.commit()
    return {"message": "Annonce supprimée"}


