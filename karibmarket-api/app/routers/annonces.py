from fastapi import APIRouter, Path, Query, HTTPException
from pydantic import BaseModel
from typing import Optional

class AnnonceCreate(BaseModel):
    titre: str
    prix: float
    commune: str

router = APIRouter()

# Données temporaires (en attendant la base de données)
annonces_db = [
    {"id": 1, "titre": "Vente mangues Julie", "prix": 3.50, "commune": "Le Lamentin"},
    {"id": 2, "titre": "Cours de yoga plage", "prix": 25.00, "commune": "Sainte-Anne"},
    {"id": 3, "titre": "Location VTT", "prix": 15.00, "commune": "Le Morne-Rouge"},
]

# --- Créer une annonce ---
@router.post("/annonces", status_code=201)
def create_annonce(annonce: AnnonceCreate):
    """
    Crée une nouvelle annonce.

    Body JSON attendu :
    ```json
    {
        "titre": "Vente mangues Julie",
        "prix": 3.50,
        "commune": "Le Lamentin"
    }
    ```
    """
    nouvel_id = max(a["id"] for a in annonces_db) + 1
    nouvelle_annonce = {"id": nouvel_id, **annonce.model_dump()}
    annonces_db.append(nouvelle_annonce)
    return nouvelle_annonce

# --- Paramètres de chemin (Path Parameters) ---
@router.get("/annonces/{annonce_id}")
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
    # Si non trouvée → erreur 404 automatique
    raise HTTPException(status_code=404, detail=f"Annonce {annonce_id} introuvable")

# --- Paramètres de requête (Query Parameters) ---
@router.get("/annonces")
def list_annonces(
    commune: Optional[str] = Query(None, description="Filtrer par commune"),
    prix_max: Optional[float] = Query(None, gt=0, description="Prix maximum"),
    page: int = Query(1, gt=0, description="Numéro de page"),
    limit: int = Query(10, gt=0, le=100, description="Nombre de résultats par page")
):
    """
    Liste les annonces avec filtres et pagination.
    
    Exemples :
    - /annonces?commune=Le Lamentin
    - /annonces?prix_max=20&page=2&limit=5
    """
    resultats = annonces_db.copy()

    # Filtrage
    if commune:
        resultats = [a for a in resultats if commune.lower() in a["commune"].lower()]
    if prix_max:
        resultats = [a for a in resultats if a["prix"] <= prix_max]

    # Pagination
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