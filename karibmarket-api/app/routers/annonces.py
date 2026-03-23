from fastapi import APIRouter, HTTPException
from typing import Optional, List
from app.schemas.annonce import AnnonceCreate, AnnonceResponse, AnnonceUpdate

router = APIRouter()

annonces = []
compteur_id = 1

@router.get("/annonces", response_model=List[AnnonceResponse])
def get_annonces(commune: Optional[str] = None, categorie: Optional[str] = None):

    results = annonces

    if commune:
        results = [a for a in results if a["commune"] == commune]

    if categorie:
        results = [a for a in results if a["categorie"] == categorie]

    return results


@router.get("/annonces/{id}", response_model=AnnonceResponse)
def get_annonce(id: int):
    for annonce in annonces:
        if annonce["id"] == id:
            return annonce
    raise HTTPException(status_code=404, detail="Annonce introuvable")


@router.post("/annonces", response_model=AnnonceResponse, status_code=201)
def create_annonce(annonce: AnnonceCreate):
    global compteur_id

    new_annonce = {
        "id": compteur_id,
        **annonce.model_dump()
    }

    annonces.append(new_annonce)
    compteur_id += 1

    return new_annonce


@router.patch("/annonces/{id}", response_model=AnnonceResponse)
def update_annonce(id: int, data: AnnonceUpdate):

    for annonce in annonces:
        if annonce["id"] == id:
            annonce.update(data.model_dump(exclude_unset=True))
            return annonce

    raise HTTPException(status_code=404, detail="Annonce introuvable")


@router.delete("/annonces/{id}")
def delete_annonce(id: int):

    for annonce in annonces:
        if annonce["id"] == id:
            annonces.remove(annonce)
            return {"message": "Supprimé"}

    raise HTTPException(status_code=404, detail="Annonce introuvable")