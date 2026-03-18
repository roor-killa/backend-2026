from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.kiprix_database import get_kiprix_db
from app.models.kiprix.produit import Produit
from app.schemas.kiprix.produit_schema import ProduitResponse, ProduitListResponse

router = APIRouter(
    prefix="/prix",
    tags=["Prix Kiprix"]
)


@router.get("", response_model=ProduitListResponse)
def list_produits(
    search: Optional[str] = Query(None, description="Recherche par nom de produit"),
    territory: Optional[str] = Query(None, description="Filtrer par territoire ex: MQ, GP, RE"),
    page: int = Query(1, gt=0),
    limit: int = Query(20, gt=0, le=100),
    db: Session = Depends(get_kiprix_db)
):
    query = db.query(Produit)

    if search:
        query = query.filter(Produit.name.ilike(f"%{search}%"))

    if territory:
        query = query.filter(Produit.territory == territory.upper())

    total = query.count()
    produits = query.offset((page - 1) * limit).limit(limit).all()

    return ProduitListResponse(
        total=total,
        page=page,
        limit=limit,
        resultats=produits
    )


@router.get("/territoires", response_model=list[str])
def list_territoires(db: Session = Depends(get_kiprix_db)):
    """Retourne la liste des territoires disponibles dans les données scrapées"""
    resultats = db.query(Produit.territory).distinct().filter(
        Produit.territory.isnot(None)
    ).all()
    return [r.territory for r in resultats]


@router.get("/comparaison", response_model=list[ProduitResponse])
def comparer_prix(
    search: str = Query(..., description="Nom du produit à comparer"),
    db: Session = Depends(get_kiprix_db)
):
    """Compare les prix France vs DOM pour un produit donné"""
    produits = db.query(Produit).filter(
        Produit.name.ilike(f"%{search}%")
    ).order_by(Produit.territory).all()

    if not produits:
        raise HTTPException(status_code=404, detail="Aucun produit trouvé")

    return produits


@router.get("/{produit_id}", response_model=ProduitResponse)
def get_produit(produit_id: int, db: Session = Depends(get_kiprix_db)):
    produit = db.query(Produit).filter(Produit.id == produit_id).first()
    if not produit:
        raise HTTPException(status_code=404, detail="Produit introuvable")
    return produit
