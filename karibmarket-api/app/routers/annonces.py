from fastapi import APIRouter, HTTPException, Depends
from app.schemas.annonce import AnnonceCreate
from app.routers.auth import get_current_user

router = APIRouter()

annonces = []

# GET ALL
@router.get("/annonces")
def get_all():
    return annonces

# GET ONE
@router.get("/annonces/{id}")
def get_one(id: int):
    for a in annonces:
        if a["id"] == id:
            return a
    raise HTTPException(404, "Introuvable")

# CREATE (PROTÉGÉ)
@router.post("/annonces")
def create(annonce: AnnonceCreate, user=Depends(get_current_user)):
    new = annonce.model_dump()
    new["id"] = len(annonces) + 1
    new["owner"] = user["id"]

    annonces.append(new)
    return new

# DELETE (PROTÉGÉ)
@router.delete("/annonces/{id}")
def delete(id: int, user=Depends(get_current_user)):
    for a in annonces:
        if a["id"] == id:

            if a["owner"] != user["id"]:
                raise HTTPException(403, "interdit")

            annonces.remove(a)
            return {"message": "supprimé"}

    raise HTTPException(404, "introuvable")