from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import Optional, List

router = APIRouter()

# --- "Base de données" temporaire ---
annonces = [
    {
        "id": 1,
        "titre": "Vente mangues Julie",
        "description": "Mangues locales, récolte du jour",
        "prix": 3.50,
        "commune": "Le Lamentin",
        "categorie": "alimentaire",
    },
    {
        "id": 2,
        "titre": "Cours de yoga plage",
        "description": "Séance au coucher du soleil",
        "prix": 25.00,
        "commune": "Sainte-Anne",
        "categorie": "services",
    },
    {
        "id": 3,
        "titre": "Location VTT",
        "description": "VTT tout terrain, journée ou demi-journée",
        "prix": 15.00,
        "commune": "Le Morne-Rouge",
        "categorie": "loisirs",
    },
    {
        "id": 4,
        "titre": "Studio à louer",
        "description": "Proche centre-ville, meublé",
        "prix": 550.00,
        "commune": "Fort-de-France",
        "categorie": "immobilier",
    },
    {
        "id": 5,
        "titre": "Vente scooter",
        "description": "125cc, bon état",
        "prix": 1200.00,
        "commune": "Le Robert",
        "categorie": "vehicules",
    },
]

next_id = 6


class AnnonceCreate(BaseModel):
    titre: str = Field(..., min_length=5, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    prix: float = Field(..., gt=0)
    commune: str = Field(..., min_length=2, max_length=50)
    categorie: str = Field(..., min_length=3, max_length=30)


@router.get("/annonces")
def list_annonces(
    commune: Optional[str] = Query(None),
    categorie: Optional[str] = Query(None),
):
    resultats = annonces

    if commune:
        resultats = [a for a in resultats if commune.lower() in a["commune"].lower()]
    if categorie:
        resultats = [a for a in resultats if categorie.lower() == a["categorie"].lower()]

    return {"data": resultats, "meta": {"total": len(resultats)}}


@router.get("/annonces/{annonce_id}")
def get_annonce(annonce_id: int):
    for a in annonces:
        if a["id"] == annonce_id:
            return a
    raise HTTPException(status_code=404, detail="Annonce introuvable")


@router.post("/annonces", status_code=status.HTTP_201_CREATED)
def create_annonce(payload: AnnonceCreate):
    global next_id
    nouvelle = {"id": next_id, **payload.model_dump()}
    annonces.append(nouvelle)
    next_id += 1
    return nouvelle


@router.delete("/annonces/{annonce_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_annonce(annonce_id: int):
    for i, a in enumerate(annonces):
        if a["id"] == annonce_id:
            annonces.pop(i)
            return
    raise HTTPException(status_code=404, detail="Annonce introuvable")
