from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.kiprix_database import get_kiprix_db
from app.models.kiprix.scrape_url import ScrapeUrl
from app.models.kiprix.produit import Produit
from app.schemas.kiprix.scrape_url_schema import (
    ScrapeUrlCreate, ScrapeUrlUpdate, ScrapeUrlResponse, DashboardStats
)
from app.routers.auth import get_current_user
from app.models.utilisateur import Utilisateur

router = APIRouter(
    prefix="/admin/scrape-urls",
    tags=["Admin - Scraping"]
)


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_kiprix_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Statistiques globales pour le dashboard"""
    total_urls = db.query(ScrapeUrl).count()
    urls_actives = db.query(ScrapeUrl).filter(ScrapeUrl.actif == True).count()
    total_donnees = db.query(Produit).count()

    derniere = db.query(Produit.scraped_at).order_by(
        Produit.scraped_at.desc()
    ).first()

    return DashboardStats(
        total_urls=total_urls,
        urls_actives=urls_actives,
        total_donnees=total_donnees,
        derniere_maj=derniere[0] if derniere else None
    )


@router.get("", response_model=List[ScrapeUrlResponse])
def list_scrape_urls(
    db: Session = Depends(get_kiprix_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Liste toutes les URLs enregistrées"""
    return db.query(ScrapeUrl).order_by(ScrapeUrl.created_at.desc()).all()


@router.post("", response_model=ScrapeUrlResponse, status_code=201)
def add_scrape_url(
    payload: ScrapeUrlCreate,
    db: Session = Depends(get_kiprix_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Ajoute une nouvelle URL à scraper"""
    existante = db.query(ScrapeUrl).filter(
        ScrapeUrl.url == str(payload.url)
    ).first()

    if existante:
        raise HTTPException(
            status_code=400,
            detail="Cette URL est déjà enregistrée"
        )

    scrape_url = ScrapeUrl(
        url=str(payload.url),
        label=payload.label
    )

    db.add(scrape_url)
    db.commit()
    db.refresh(scrape_url)

    return scrape_url


@router.patch("/{url_id}", response_model=ScrapeUrlResponse)
def update_scrape_url(
    url_id: int,
    payload: ScrapeUrlUpdate,
    db: Session = Depends(get_kiprix_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Modifie le label ou le statut d'une URL"""
    scrape_url = db.query(ScrapeUrl).filter(ScrapeUrl.id == url_id).first()

    if not scrape_url:
        raise HTTPException(status_code=404, detail="URL introuvable")

    for champ, valeur in payload.model_dump(exclude_unset=True).items():
        setattr(scrape_url, champ, valeur)

    db.commit()
    db.refresh(scrape_url)

    return scrape_url


@router.delete("/{url_id}", status_code=204)
def delete_scrape_url(
    url_id: int,
    db: Session = Depends(get_kiprix_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Supprime une URL"""
    scrape_url = db.query(ScrapeUrl).filter(ScrapeUrl.id == url_id).first()

    if not scrape_url:
        raise HTTPException(status_code=404, detail="URL introuvable")

    db.delete(scrape_url)
    db.commit()
