from fastapi import APIRouter, HTTPException, Depends, Query, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import time

from app.database import get_db
from app.models.annonce import Annonce
from app.models.utilisateur import Utilisateur
from app.schemas.annonce import AnnonceCreate, AnnonceUpdate, AnnonceResponse
from fastapi_cache.decorator import cache

# On importe notre videur !
from app.routers.auth import get_current_user

def envoyer_email_confirmation(email: str, titre_annonce: str):
    print(f"⏳ [Arrière-plan] Préparation de l'email pour {email}...")
    time.sleep(3) # On simule un processus qui prend 3 secondes
    print(f"✅ [Arrière-plan] EMAIL ENVOYÉ avec succès à {email} pour l'annonce '{titre_annonce}' !")

router = APIRouter()

# 🟢 ROUTE PUBLIQUE : Tout le monde peut voir les annonces
@router.get("/annonces", response_model=List[AnnonceResponse])
@cache(expire=60)
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
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db),
    utilisateur_actuel: Utilisateur = Depends(get_current_user) # Le videur est ici !
):
    # On utilise le vrai ID de l'utilisateur connecté
    nouvelle_annonce = Annonce(**annonce_data.model_dump(), proprietaire_id=utilisateur_actuel.id)
    db.add(nouvelle_annonce)
    db.commit()
    db.refresh(nouvelle_annonce)
    
    background_tasks.add_task(envoyer_email_confirmation, utilisateur_actuel.email, nouvelle_annonce.titre)

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

    import time # (Si tu ne l'as plus en haut du fichier)

@router.get("/test-cache")
@cache(expire=60)
def test_du_cache():
    return {"heure_exacte": time.time()}