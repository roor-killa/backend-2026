from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter()

annonces = [
    {
        "id": 1,
        "titre": "Vente mangues bio",
        "description": "Mangues fraîches récoltées du jour",
        "prix": 4.50,
        "commune": "Le Lamentin",
        "categorie": "Alimentation"
    },
    {
        "id": 2,
        "titre": "Cours de surf",
        "description": "Cours débutant et intermédiaire",
        "prix": 35.00,
        "commune": "Sainte-Anne",
        "categorie": "Sport"
    },
    {
        "id": 3,
        "titre": "Location voiture",
        "description": "Citadine économique",
        "prix": 45.00,
        "commune": "Fort-de-France",
        "categorie": "Transport"
    },
    {
        "id": 4,
        "titre": "Cours de guitare",
        "description": "Professeur expérimenté",
        "prix": 20.00,
        "commune": "Ducos",
        "categorie": "Éducation"
    },
    {
        "id": 5,
        "titre": "Massage relaxant",
        "description": "Massage à domicile",
        "prix": 60.00,
        "commune": "Le Robert",
        "categorie": "Bien-être"
    }
]


class AnnonceCreate(BaseModel):
    titre: str = Field(..., min_length=3, max_length=100, description="Titre de l'annonce")
    prix: float = Field(..., gt=0, description="Prix de l'annonce")
    commune: str = Field(..., min_length=2, max_length=50, description="Commune de l'annonce")
    categorie: str = Field(..., min_length=2, max_length=50, description="Catégorie de l'annonce")
# --- Endpoint GET par ID ---
@router.get("/{annonce_id}")
def get_annonce(annonce_id: int = Path(..., gt=0, description="ID de l'annonce")):
    for annonce in annonces:
        if annonce["id"] == annonce_id:
            return annonce
    raise HTTPException(status_code=404, detail=f"Annonce {annonce_id} introuvable")

# --- Endpoint GET avec filtres ---
@router.get("/")
def list_annonces(
    commune: Optional[str] = Query(None, description="Filtrer par commune"),
    prix_max: Optional[float] = Query(None, gt=0, description="Prix maximum"),
    page: int = Query(1, gt=0, description="Numéro de page"),
    limit: int = Query(10, gt=0, le=100, description="Nombre de résultats par page")
):
    resultats = annonces.copy()
    if commune:
        resultats = [a for a in resultats if commune.lower() in a["commune"].lower()]
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

# --- Endpoint POST pour créer une annonce ---
@router.post("/", status_code=201)
def create_annonce(annonce: AnnonceCreate):
    # Génère un nouvel ID
    new_id = max(a["id"] for a in annonces) + 1 if annonces else 1
    nouvelle_annonce = annonce.dict()
    nouvelle_annonce["id"] = new_id
    annonces.append(nouvelle_annonce)
    return {"message": "Annonce créée avec succès", "annonce": nouvelle_annonce}


@router.delete("/{annonce_id}", status_code=204)
def delete_annonce(annonce_id: int = Path(..., gt=0, description="ID de l'annonce à supprimer")):
    for i, annonce in enumerate(annonces):
        if annonce["id"] == annonce_id:
            del annonces[i]
            return
    raise HTTPException(status_code=404, detail=f"Annonce {annonce_id} introuvable")