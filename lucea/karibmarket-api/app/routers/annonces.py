# app/routers/annonces.py — version avec SQLAlchemy
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.annonce import Annonce
from app.schemas.annonce import AnnonceCreate, AnnonceUpdate, AnnonceResponse

router = APIRouter()

@router.get("/annonces", response_model=List[AnnonceResponse])
def list_annonces(
    commune: Optional[str] = Query(None),
    categorie: Optional[str] = Query(None),
    page: int = Query(1, gt=0),
    limit: int = Query(10, gt=0, le=100),
    db: Session = Depends(get_db)  # ← Injection de la session
):
    query = db.query(Annonce).filter(Annonce.actif == True)

    if commune:
        query = query.filter(Annonce.commune.ilike(f"%{commune}%"))
    if categorie:
        query = query.filter(Annonce.categorie == categorie)

    total = query.count()
    annonces = query.offset((page - 1) * limit).limit(limit).all()

    return annonces

@router.post("/annonces", response_model=AnnonceResponse, status_code=201)
def create_annonce(
    annonce_data: AnnonceCreate,
    db: Session = Depends(get_db)
):
    nouvelle_annonce = Annonce(**annonce_data.model_dump())
    db.add(nouvelle_annonce)
    db.commit()           # Sauvegarder en base
    db.refresh(nouvelle_annonce)  # Récupérer les valeurs générées (id, created_at...)
    return nouvelle_annonce

@router.get("/annonces/{annonce_id}", response_model=AnnonceResponse)
def get_annonce(annonce_id: int, db: Session = Depends(get_db)):
    annonce = db.query(Annonce).filter(Annonce.id == annonce_id).first()
    if not annonce:
        raise HTTPException(status_code=404, detail="Annonce introuvable")
    return annonce

@router.delete("/annonces/{annonce_id}", status_code=204)
def delete_annonce(annonce_id: int, db: Session = Depends(get_db)):
    annonce = db.query(Annonce).filter(Annonce.id == annonce_id).first()
    if not annonce:
        raise HTTPException(status_code=404, detail="Annonce introuvable")
    # Soft delete — on ne supprime pas vraiment de la BDD
    annonce.actif = False
    db.commit()