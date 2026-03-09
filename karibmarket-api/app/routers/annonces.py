from fastapi import APIRouter, Path, Query, HTTPException, status
from app.schemas.annonce import AnnonceCreate, AnnonceUpdate, AnnonceResponse
from typing import Optional, List
from datetime import datetime

router = APIRouter()

# Base de données simulée
annonces_db = [
    {
        "id": 1,
        "titre": "Vente mangues Julie",
        "description": None,
        "prix": 3.50,
        "commune": "Le Lamentin",
        "categorie": "alimentaire",
        "actif": True,
        "created_at": datetime.now(),
        "updated_at": None
    },
    {
        "id": 2,
        "titre": "Cours de yoga plage",
        "description": None,
        "prix": 25.00,
        "commune": "Sainte-Anne",
        "categorie": "services",
        "actif": True,
        "created_at": datetime.now(),
        "updated_at": None
    },
    {
        "id": 3,
        "titre": "Location VTT",
        "description": None,
        "prix": 15.00,
        "commune": "Le Morne-Rouge",
        "categorie": "loisirs",
        "actif": True,
        "created_at": datetime.now(),
        "updated_at": None
    },
]
compteur_id = 4


@router.post(
    "/annonces",
    response_model=AnnonceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer une nouvelle annonce"
)
def create_annonce(annonce: AnnonceCreate):
    """
    Crée une nouvelle annonce dans KaribMarket.

    - **titre** : Entre 5 et 100 caractères
    - **prix** : Doit être positif (> 0)
    - **commune** : Commune de Martinique ou Guadeloupe
    - **categorie** : alimentaire, services, loisirs, immobilier, vehicules, autre
    """
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


@router.patch(
    "/annonces/{annonce_id}",
    response_model=AnnonceResponse,
    summary="Modifier partiellement une annonce"
)
def update_annonce(
    annonce_id: int = Path(..., gt=0, description="ID de l'annonce"),
    modifications: AnnonceUpdate = ...
):
    for i, annonce in enumerate(annonces_db):
        if annonce["id"] == annonce_id:
            # model_dump(exclude_unset=True) → seulement les champs fournis
            changements = modifications.model_dump(exclude_unset=True)
            annonces_db[i].update(changements)
            annonces_db[i]["updated_at"] = datetime.now()
            return annonces_db[i]

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Annonce {annonce_id} introuvable"
    )


@router.get(
    "/annonces/{annonce_id}",
    response_model=AnnonceResponse,
    summary="Récupérer une annonce par son ID"
)
def get_annonce(
    annonce_id: int = Path(..., gt=0, description="ID de l'annonce")
):
    """
    Récupère une annonce par son identifiant.
    - **annonce_id** : doit être un entier positif
    """
    for annonce in annonces_db:
        if annonce["id"] == annonce_id:
            return annonce
    raise HTTPException(status_code=404, detail=f"Annonce {annonce_id} introuvable")


@router.delete("/annonces/{annonce_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_annonce(
    annonce_id: int = Path(..., gt=0, description="ID de l'annonce à supprimer")
):
    """
    Supprime une annonce par son identifiant.
    """
    for i, annonce in enumerate(annonces_db):
        if annonce["id"] == annonce_id:
            annonces_db.pop(i)
            return
    raise HTTPException(status_code=404, detail=f"Annonce {annonce_id} introuvable")


@router.get(
    "/annonces",
    response_model=dict,
    summary="Lister les annonces avec filtres et pagination"
)
def list_annonces(
    commune: Optional[str] = Query(None, description="Filtrer par commune"),
    categorie: Optional[str] = Query(None, description="Filtrer par catégorie"),
    prix_max: Optional[float] = Query(None, gt=0, description="Prix maximum"),
    page: int = Query(1, gt=0, description="Numéro de page"),
    limit: int = Query(10, gt=0, le=100, description="Nombre de résultats par page")
):
    """
    Liste les annonces avec filtres et pagination.

    Exemples :
    - /annonces?commune=Le Lamentin
    - /annonces?prix_max=20&page=2&limit=5
    - /annonces?categorie=alimentaire
    """
    resultats = annonces_db.copy()

    if commune:
        resultats = [a for a in resultats if commune.lower() in a["commune"].lower()]
    if categorie:
        resultats = [a for a in resultats if a["categorie"] == categorie]
    if prix_max:
        resultats = [a for a in resultats if a["prix"] <= prix_max]

    total = len(resultats)
    debut = (page - 1) * limit
    fin = debut + limit

    return {
        "data": resultats[debut:fin],
        "meta": {
            "total": total,
            "page": page,
            "limit": limit,
            "pages_total": (total + limit - 1) // limit
        }
    }
