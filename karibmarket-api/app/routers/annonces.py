from fastapi import APIRouter, HTTPException

router = APIRouter()

# Base de données temporaire
annonces = [
    {"id": 1, "titre": "Mangues bio", "description": "Mangues fraîches", "prix": 3.5, "commune": "Le Lamentin", "categorie": "alimentaire"},
    {"id": 2, "titre": "Cours de yoga", "description": "Yoga sur la plage", "prix": 25, "commune": "Sainte-Anne", "categorie": "services"},
]

# GET liste
@router.get("/annonces")
def list_annonces():
    return annonces

# GET détail
@router.get("/annonces/{id}")
def get_annonce(id: int):
    for annonce in annonces:
        if annonce["id"] == id:
            return annonce
    raise HTTPException(status_code=404, detail="Annonce introuvable")

# POST créer
@router.post("/annonces")
def create_annonce(annonce: dict):
    annonces.append(annonce)
    return {"message": "Annonce ajoutée", "data": annonce}

# DELETE supprimer
@router.delete("/annonces/{id}")
def delete_annonce(id: int):
    for annonce in annonces:
        if annonce["id"] == id:
            annonces.remove(annonce)
            return {"message": "Annonce supprimée"}
    raise HTTPException(status_code=404, detail="Annonce introuvable")
