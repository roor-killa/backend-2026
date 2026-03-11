from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional, List
from datetime import datetime
from app.schemas.annonce import AnnonceCreate, AnnonceUpdate, AnnonceResponse

router = APIRouter()

annonces_db = []
compteur_id = 1

@router.get("/annonces", response_model=List[AnnonceResponse])
def list_annonces(
    commune: Optional[str] = Query(None, description="Filtrer par commune"),
    categorie: Optional[str] = Query(None, description="Filtrer par catégorie")
):
    resultats = annonces_db.copy()
    if commune:
        resultats = [a for a in resultats if commune.lower() in a["commune"].lower()]
    if categorie:
        resultats = [a for a in resultats if categorie.lower() == a["categorie"].lower()]
    return resultats

@router.get("/annonces/{id}", response_model=AnnonceResponse)
def get_annonce(id: int):
    for annonce in annonces_db:
        if annonce["id"] == id:
            return annonce
    raise HTTPException(status_code=404, detail=f"Annonce {id} introuvable")

@router.post("/annonces", response_model=AnnonceResponse, status_code=status.HTTP_201_CREATED)
def create_annonce(annonce: AnnonceCreate):
    global compteur_id
    
    nouvelle_annonce = {
        "id": compteur_id,
        **annonce.model_dump(),  # Transforme le schéma validé en dictionnaire
        "actif": True,
        "created_at": datetime.now(),
        "updated_at": None
    }
    
    annonces_db.append(nouvelle_annonce)
    compteur_id += 1
    return nouvelle_annonce

@router.patch("/annonces/{id}", response_model=AnnonceResponse)
def update_annonce(id: int, modifications: AnnonceUpdate):
    for i, annonce in enumerate(annonces_db):
        if annonce["id"] == id:
            changements = modifications.model_dump(exclude_unset=True) # Que les champs modifiés
            annonces_db[i].update(changements)
            annonces_db[i]["updated_at"] = datetime.now()
            return annonces_db[i]
            
    raise HTTPException(status_code=404, detail=f"Annonce {id} introuvable")

@router.delete("/annonces/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_annonce(id: int):
    for i, annonce in enumerate(annonces_db):
        if annonce["id"] == id:
            del annonces_db[i]
            return
    raise HTTPException(status_code=404, detail=f"Annonce {id} introuvable")