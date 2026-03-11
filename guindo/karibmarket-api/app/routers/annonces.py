from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime

from app.schemas.annonce import (
    AnnonceCreate,
    AnnonceUpdate,
    AnnonceResponse
)

router = APIRouter()

annonces_db = []
compteur_id = 1


# ----------------------------
# CREATE annonce
# ----------------------------
@router.post(
    "/annonces",
    response_model=AnnonceResponse,
    status_code=status.HTTP_201_CREATED
)
def create_annonce(annonce: AnnonceCreate):

    global compteur_id

    nouvelle_annonce = {
        "id": compteur_id,
        **annonce.model_dump(),
        "actif": True,
        "created_at": datetime.now(),
        "updated_at": None
    }

    annonces_db.append(nouvelle_annonce)
    compteur_id += 1

    return nouvelle_annonce


# ----------------------------
# LIST annonces
# ----------------------------
@router.get("/annonces", response_model=List[AnnonceResponse])
def list_annonces():

    return annonces_db


# ----------------------------
# GET annonce par id
# ----------------------------
@router.get("/annonces/{annonce_id}", response_model=AnnonceResponse)
def get_annonce(annonce_id: int):

    for annonce in annonces_db:
        if annonce["id"] == annonce_id:
            return annonce

    raise HTTPException(
        status_code=404,
        detail="Annonce introuvable"
    )


# ----------------------------
# UPDATE annonce
# ----------------------------
@router.patch("/annonces/{annonce_id}", response_model=AnnonceResponse)
def update_annonce(annonce_id: int, modifications: AnnonceUpdate):

    for annonce in annonces_db:

        if annonce["id"] == annonce_id:

            changements = modifications.model_dump(exclude_unset=True)

            annonce.update(changements)
            annonce["updated_at"] = datetime.now()

            return annonce

    raise HTTPException(
        status_code=404,
        detail="Annonce introuvable"
    )


# ----------------------------
# DELETE annonce
# ----------------------------
@router.delete("/annonces/{annonce_id}")
def delete_annonce(annonce_id: int):

    for i, annonce in enumerate(annonces_db):

        if annonce["id"] == annonce_id:

            annonces_db.pop(i)

            return {"message": "Annonce supprimée"}

    raise HTTPException(
        status_code=404,
        detail="Annonce introuvable"
    )