


from fastapi import APIRouter, Path, Query, HTTPException, status
from app.schemas.annonce import AnnonceCreate, AnnonceUpdate, AnnonceResponse
from typing import List
from datetime import datetime
from typing import Optional

# Création du routeur
router = APIRouter()

# Données temporaires (en attendant la base de données)
annonces_db = [
    {"id": 1, "titre": "Vente mangues Julie", "prix": 3.50, "commune": "Le Lamentin"},
    {"id": 2, "titre": "Cours de yoga plage", "prix": 25.00, "commune": "Sainte-Anne"},
    {"id": 3, "titre": "Location VTT", "prix": 15.00, "commune": "Le Morne-Rouge"},
]

compteur_id = 1

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



@router.post(
    "/annonces",
    response_model=AnnonceResponse,         # Schéma de réponse
    status_code=status.HTTP_201_CREATED,    # Code de statut par défaut
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
        **annonce.model_dump(),     # Convertit le schéma Pydantic en dict
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
def update_annonce(annonce_id: int, modifications: AnnonceUpdate):
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





from typing import List, Optional
from app.database import get_db
from app.models.annonce import Annonce
from app.schemas.annonce import AnnonceCreate, AnnonceUpdate, AnnonceResponse

router = APIRouter()

@router.get("/annonces", response_model=List[AnnonceResponse])
def list_annonces(
    commune: Optional[str] = Query(None),
    categorie: Optional[str] = Query(None),
    page: int = Query(1, gt=0),
    limit: int = Query(10, gt=0, le=100),
    db: Session = Depends(get_db)  # ← Injection de la session
):
    query = db.query(Annonce).filter(Annonce.actif == True)

    if commune:
        query = query.filter(Annonce.commune.ilike(f"%{commune}%"))
    if categorie:
        query = query.filter(Annonce.categorie == categorie)

    total = query.count()
    annonces = query.offset((page - 1) * limit).limit(limit).all()

    return annonces

@router.post("/annonces", response_model=AnnonceResponse, status_code=201)
def create_annonce(
    annonce_data: AnnonceCreate,
    db: Session = Depends(get_db)
):
    nouvelle_annonce = Annonce(**annonce_data.model_dump())
    db.add(nouvelle_annonce)
    db.commit()           # Sauvegarder en base
    db.refresh(nouvelle_annonce)  # Récupérer les valeurs générées (id, created_at...)
    return nouvelle_annonce

@router.get("/annonces/{annonce_id}", response_model=AnnonceResponse)
def get_annonce(annonce_id: int, db: Session = Depends(get_db)):
    annonce = db.query(Annonce).filter(Annonce.id == annonce_id).first()
    if not annonce:
        raise HTTPException(status_code=404, detail="Annonce introuvable")
    return annonce

@router.delete("/annonces/{annonce_id}", status_code=204)
def delete_annonce(annonce_id: int, db: Session = Depends(get_db)):
    annonce = db.query(Annonce).filter(Annonce.id == annonce_id).first()
    if not annonce:
        raise HTTPException(status_code=404, detail="Annonce introuvable")
    # Soft delete — on ne supprime pas vraiment de la BDD
    annonce.actif = False
    db.commit()