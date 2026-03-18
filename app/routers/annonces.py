from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.annonce import Annonce
from app.models.utilisateur import Utilisateur
from app.schemas.annonce import AnnonceCreate, AnnonceUpdate, AnnonceResponse

# On importe notre videur !
from app.routers.auth import get_current_user

router = APIRouter()

# 🟢 ROUTE PUBLIQUE : Tout le monde peut voir les annonces
@router.get("/annonces", response_model=List[AnnonceResponse])
def list_annonces(
    commune: Optional[str] = Query(None),
    categorie: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Annonce).filter(Annonce.actif == True)
    if commune:
        query = query.filter(Annonce.commune.ilike(f"%{commune}%"))
    if categorie:
        query = query.filter(Annonce.categorie == categorie)
    return query.all()

# 🟢 ROUTE PUBLIQUE : Tout le monde peut voir une annonce spécifique
@router.get("/annonces/{id}", response_model=AnnonceResponse)
def get_annonce(id: int, db: Session = Depends(get_db)):
    annonce = db.query(Annonce).filter(Annonce.id == id).first()
    if not annonce:
        raise HTTPException(status_code=404, detail=f"Annonce {id} introuvable")
    return annonce

# 🔴 ROUTE PROTÉGÉE : Il faut être connecté pour créer une annonce !
@router.post("/annonces", response_model=AnnonceResponse, status_code=status.HTTP_201_CREATED)
def create_annonce(
    annonce_data: AnnonceCreate, 
    db: Session = Depends(get_db),
    utilisateur_actuel: Utilisateur = Depends(get_current_user) # Le videur est ici !
):
    # On utilise le vrai ID de l'utilisateur connecté
    nouvelle_annonce = Annonce(**annonce_data.model_dump(), proprietaire_id=utilisateur_actuel.id)
    db.add(nouvelle_annonce)
    db.commit()
    db.refresh(nouvelle_annonce)
    return nouvelle_annonce

# 🔴 ROUTE PROTÉGÉE : Il faut être connecté
@router.patch("/annonces/{id}", response_model=AnnonceResponse)
def update_annonce(
    id: int, 
    modifications: AnnonceUpdate, 
    db: Session = Depends(get_db),
    utilisateur_actuel: Utilisateur = Depends(get_current_user) # Le videur est ici !
):
    annonce = db.query(Annonce).filter(Annonce.id == id).first()
    if not annonce:
        raise HTTPException(status_code=404, detail="Annonce introuvable")
    
    # Petite sécurité bonus : on vérifie que l'utilisateur modifie SA propre annonce
    if annonce.proprietaire_id != utilisateur_actuel.id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez modifier que vos propres annonces")

    changements = modifications.model_dump(exclude_unset=True)
    for cle, valeur in changements.items():
        setattr(annonce, cle, valeur)

    db.commit()
    db.refresh(annonce)
    return annonce

# 🔴 ROUTE PROTÉGÉE : Il faut être connecté
@router.delete("/annonces/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_annonce(
    id: int, 
    db: Session = Depends(get_db),
    utilisateur_actuel: Utilisateur = Depends(get_current_user) # Le videur est ici !
):
    annonce = db.query(Annonce).filter(Annonce.id == id).first()
    if not annonce:
        raise HTTPException(status_code=404, detail="Annonce introuvable")
    
    if annonce.proprietaire_id != utilisateur_actuel.id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez supprimer que vos propres annonces")
    
    annonce.actif = False
    db.commit()