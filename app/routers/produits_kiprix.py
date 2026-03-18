from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.produit_kiprix import ProduitKiprix
from app.schemas.produit_kiprix import (
    ProduitKiprixImportRequest,
    ProduitKiprixImportResponse,
    ProduitKiprixResponse,
)
from app.services.kiprix_import_service import import_kiprix_products

router = APIRouter()


@router.get("/produits-kiprix", response_model=list[ProduitKiprixResponse])
def list_produits_kiprix(
    territory: str | None = Query(default=None),
    q: str | None = Query(default=None, description="Recherche par nom de produit"),
    page: int = Query(default=1, gt=0),
    limit: int = Query(default=20, gt=0, le=100),
    db: Session = Depends(get_db),
) -> list[ProduitKiprix]:
    query = select(ProduitKiprix)

    if territory:
        query = query.where(ProduitKiprix.territory == territory)

    if q:
        query = query.where(ProduitKiprix.name.ilike(f"%{q}%"))

    query = query.order_by(ProduitKiprix.id.desc()).offset((page - 1) * limit).limit(limit)
    return list(db.execute(query).scalars().all())


@router.get("/produits-kiprix/{produit_id}", response_model=ProduitKiprixResponse)
def get_produit_kiprix(produit_id: int, db: Session = Depends(get_db)) -> ProduitKiprix:
    produit = db.get(ProduitKiprix, produit_id)
    if not produit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produit Kiprix {produit_id} introuvable",
        )
    return produit


@router.post(
    "/produits-kiprix/import",
    response_model=ProduitKiprixImportResponse,
    status_code=status.HTTP_201_CREATED,
)
def import_produits_kiprix(
    payload: ProduitKiprixImportRequest,
    db: Session = Depends(get_db),
) -> ProduitKiprixImportResponse:
    try:
        result = import_kiprix_products(
            db=db,
            territory=payload.territory,
            max_pages=payload.max_pages,
        )
        return ProduitKiprixImportResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur import Kiprix: {exc}",
        ) from exc
