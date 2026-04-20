from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database_kiprix import get_kiprix_db
from app.models.produit import Produit
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

router = APIRouter(tags=["Prix Kiprix"])


class ProduitResponse(BaseModel):
    id: int
    name: Optional[str]
    price_france: Optional[str]
    price_dom: Optional[str]
    difference: Optional[str]
    territory: Optional[str]
    territory_name: Optional[str]
    scraped_at: Optional[datetime]

    model_config = {"from_attributes": True}


@router.get("/prix")
def get_prix(
    search: Optional[str] = Query(None, description="Recherche dans le nom du produit"),
    territory: Optional[str] = Query(None, description="Code territoire: gp, mq, re, gf"),
    page: int = Query(1, gt=0),
    limit: int = Query(20, gt=0, le=100),
    db: Session = Depends(get_kiprix_db),
):
    query = db.query(Produit)

    if search:
        query = query.filter(Produit.name.ilike(f"%{search}%"))
    if territory:
        query = query.filter(Produit.territory == territory)

    total = query.count()
    resultats = (
        query.order_by(Produit.scraped_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "resultats": [ProduitResponse.model_validate(p) for p in resultats],
    }
