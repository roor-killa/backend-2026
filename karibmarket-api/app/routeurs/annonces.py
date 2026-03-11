


from fastapi import APIRouter, Path, Query, HTTPException
from typing import Optional

# Création du routeur
router = APIRouter()

# Données temporaires (en attendant la base de données)
annonces_db = [
    {"id": 1, "titre": "Vente mangues Julie", "prix": 3.50, "commune": "Le Lamentin"},
    {"id": 2, "titre": "Cours de yoga plage", "prix": 25.00, "commune": "Sainte-Anne"},
    {"id": 3, "titre": "Location VTT", "prix": 15.00, "commune": "Le Morne-Rouge"},
]

# --- Paramètres de chemin (Path Parameters) ---
@router.get("api/v1/annonces/{annonce_id}")
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
@router.get("api/v1/annonces")
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