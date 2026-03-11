from fastapi import APIRouter, Path, Query, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.schemas.annonce import AnnonceCreate, AnnonceUpdate, AnnonceResponse
from app.models.annonce import Annonce
import app.models.utilisateur  # noqa: F401 — nécessaire pour résoudre la relation ORM
from app.database import get_db
from typing import Optional, List

router = APIRouter()


@router.post(
    "/annonces",
    response_model=AnnonceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer une nouvelle annonce"
)
def create_annonce(annonce: AnnonceCreate, db: Session = Depends(get_db)):
    """
    Crée une nouvelle annonce dans KaribMarket.

    - **titre** : Entre 5 et 100 caractères
    - **prix** : Doit être positif (> 0)
    - **commune** : Commune de Martinique ou Guadeloupe
    - **categorie** : alimentaire, services, loisirs, immobilier, vehicules, autre
    """
    nouvelle_annonce = Annonce(**annonce.model_dump())
    db.add(nouvelle_annonce)
    db.commit()
    db.refresh(nouvelle_annonce)
    return nouvelle_annonce


@router.patch(
    "/annonces/{annonce_id}",
    response_model=AnnonceResponse,
    summary="Modifier partiellement une annonce"
)
def update_annonce(
    annonce_id: int = Path(..., gt=0, description="ID de l'annonce"),
    modifications: AnnonceUpdate = ...,
    db: Session = Depends(get_db)
):
    annonce = db.get(Annonce, annonce_id)
    if not annonce:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Annonce {annonce_id} introuvable"
        )

    changements = modifications.model_dump(exclude_unset=True)
    for champ, valeur in changements.items():
        setattr(annonce, champ, valeur)

    db.commit()
    db.refresh(annonce)
    return annonce


@router.get(
    "/annonces/{annonce_id}",
    response_model=AnnonceResponse,
    summary="Récupérer une annonce par son ID"
)
def get_annonce(
    annonce_id: int = Path(..., gt=0, description="ID de l'annonce"),
    db: Session = Depends(get_db)
):
    """
    Récupère une annonce par son identifiant.
    - **annonce_id** : doit être un entier positif
    """
    annonce = db.get(Annonce, annonce_id)
    if not annonce:
        raise HTTPException(status_code=404, detail=f"Annonce {annonce_id} introuvable")
    return annonce


@router.delete("/annonces/{annonce_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_annonce(
    annonce_id: int = Path(..., gt=0, description="ID de l'annonce à supprimer"),
    db: Session = Depends(get_db)
):
    """
    Supprime une annonce par son identifiant.
    """
    annonce = db.get(Annonce, annonce_id)
    if not annonce:
        raise HTTPException(status_code=404, detail=f"Annonce {annonce_id} introuvable")
    db.delete(annonce)
    db.commit()


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
    limit: int = Query(10, gt=0, le=100, description="Nombre de résultats par page"),
    db: Session = Depends(get_db)
):
    """
    Liste les annonces avec filtres et pagination.

    Exemples :
    - /annonces?commune=Le Lamentin
    - /annonces?prix_max=20&page=2&limit=5
    - /annonces?categorie=alimentaire
    """
    query = db.query(Annonce)

    if commune:
        query = query.filter(Annonce.commune.ilike(f"%{commune}%"))
    if categorie:
        query = query.filter(Annonce.categorie == categorie)
    if prix_max:
        query = query.filter(Annonce.prix <= prix_max)

    total = query.count()
    resultats = query.offset((page - 1) * limit).limit(limit).all()

    return {
        "data": [AnnonceResponse.model_validate(a) for a in resultats],
        "meta": {
            "total": total,
            "page": page,
            "limit": limit,
            "pages_total": (total + limit - 1) // limit
        }
    }
