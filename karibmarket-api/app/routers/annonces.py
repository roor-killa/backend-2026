from fastapi import APIRouter, HTTPException, Path, Query, status
from typing import Optional
from datetime import datetime
from app.schemas.annonce import AnnonceCreate, AnnonceUpdate, AnnonceResponse

router = APIRouter()

annonces_db = [
    {
        "id": 1,
        "titre": "Vélo de ville en bon état",
        "description": "Vélo confortable idéal pour les déplacements en ville.",
        "prix": 120,
        "commune": "Fort-de-France",
        "categorie": "loisirs",
        "created_at": datetime.now()
    },
    {
        "id": 2,
        "titre": "Canapé 3 places",
        "description": "Canapé gris très confortable, peu utilisé.",
        "prix": 250,
        "commune": "Le Lamentin",
        "categorie": "immobilier",
        "created_at": datetime.now()
    },
    {
        "id": 3,
        "titre": "iPhone 11 128Go",
        "description": "iPhone en bon état avec chargeur et coque.",
        "prix": 400,
        "commune": "Schoelcher",
        "categorie": "autre",
        "created_at": datetime.now()
    },
    {
        "id": 4,
        "titre": "Table à manger en bois",
        "description": "Grande table en bois massif pour 6 personnes.",
        "prix": 180,
        "commune": "Ducos",
        "categorie": "immobilier",
        "created_at": datetime.now()
    },
    {
        "id": 5,
        "titre": "Guitare acoustique",
        "description": "Guitare parfaite pour débutant, vendue avec housse.",
        "prix": 90,
        "commune": "Saint-Joseph",
        "categorie": "loisirs",
        "created_at": datetime.now()
    }
]


compteur_id = 1


@router.get("/", response_model=list[AnnonceResponse])
def list_annonces():
    return annonces_db


@router.get("/{annonce_id}", response_model=AnnonceResponse)
def get_annonce(annonce_id: int = Path(..., gt=0)):

    for annonce in annonces_db:
        if annonce["id"] == annonce_id:
            return annonce

    raise HTTPException(status_code=404, detail="Annonce introuvable")


@router.post("/", response_model=AnnonceResponse, status_code=status.HTTP_201_CREATED)
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


@router.patch("/{annonce_id}", response_model=AnnonceResponse, summary="Modifier partiellement une annonce")
def update_annonce(annonce_id: int, modifications: AnnonceUpdate):
    for i, annonce in enumerate(annonces_db):
        if annonce["id"] == annonce_id:
            changements = modifications.model_dump(exclude_unset=True)
            annonces_db[i].update(changements)
            annonces_db[i]["updated_at"] = datetime.now()
            return annonces_db[i]
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Annonce {annonce_id} introuvable")


@router.delete("/{annonce_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_annonce(annonce_id: int):

    for i, annonce in enumerate(annonces_db):

        if annonce["id"] == annonce_id:
            del annonces_db[i]
            return

    raise HTTPException(status_code=404, detail="Annonce introuvable")