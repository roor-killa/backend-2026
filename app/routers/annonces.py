from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

# On importe notre base de données et nos modèles
from app.database import get_db
from app.models.annonce import Annonce
from app.models.utilisateur import Utilisateur
from app.schemas.annonce import AnnonceCreate, AnnonceUpdate, AnnonceResponse

router = APIRouter()

@router.get("/annonces", response_model=List[AnnonceResponse])
def list_annonces(
    commune: Optional[str] = Query(None),
    categorie: Optional[str] = Query(None),
    db: Session = Depends(get_db)  # On injecte la session de la base de données
):
    # On commence la requête (uniquement les annonces actives)
    query = db.query(Annonce).filter(Annonce.actif == True)

    # On applique les filtres si l'utilisateur en a envoyé
    if commune:
        query = query.filter(Annonce.commune.ilike(f"%{commune}%"))
    if categorie:
        query = query.filter(Annonce.categorie == categorie)

    return query.all()

@router.get("/annonces/{id}", response_model=AnnonceResponse)
def get_annonce(id: int, db: Session = Depends(get_db)):
    annonce = db.query(Annonce).filter(Annonce.id == id).first()
    if not annonce:
        raise HTTPException(status_code=404, detail=f"Annonce {id} introuvable")
    return annonce

@router.post("/annonces", response_model=AnnonceResponse, status_code=status.HTTP_201_CREATED)
def create_annonce(annonce_data: AnnonceCreate, db: Session = Depends(get_db)):
    # On crée une nouvelle annonce (pour l'instant, on met proprietaire_id=1 par défaut 
    # car on n'a pas encore fait l'authentification)
    nouvelle_annonce = Annonce(**annonce_data.model_dump(), proprietaire_id=1)
    
    db.add(nouvelle_annonce)
    db.commit()                   # On sauvegarde en base de données
    db.refresh(nouvelle_annonce)  # On récupère l'ID généré par Postgres
    return nouvelle_annonce

@router.patch("/annonces/{id}", response_model=AnnonceResponse)
def update_annonce(id: int, modifications: AnnonceUpdate, db: Session = Depends(get_db)):
    annonce = db.query(Annonce).filter(Annonce.id == id).first()
    if not annonce:
        raise HTTPException(status_code=404, detail=f"Annonce {id} introuvable")

    # On applique uniquement les modifications fournies
    changements = modifications.model_dump(exclude_unset=True)
    for cle, valeur in changements.items():
        setattr(annonce, cle, valeur)

    db.commit()
    db.refresh(annonce)
    return annonce

@router.delete("/annonces/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_annonce(id: int, db: Session = Depends(get_db)):
    annonce = db.query(Annonce).filter(Annonce.id == id).first()
    if not annonce:
        raise HTTPException(status_code=404, detail=f"Annonce {id} introuvable")
    
    # Soft Delete : on ne supprime pas vraiment, on la cache juste
    annonce.actif = False
    db.commit()