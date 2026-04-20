from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db, SessionLocal
from app.database_kiprix import get_kiprix_db
from app.models.scrape_url import ScrapeUrl
from app.models.scrape_log import ScrapeLog
from app.models.produit import Produit
from app.schemas.scrape_url import ScrapeUrlCreate, ScrapeUrlUpdate, ScrapeUrlResponse
from app.schemas.scrape_log import ScrapeRunRequest, ScrapeLogResponse
from app.config import settings
from datetime import datetime, timezone
from typing import List
import httpx

router = APIRouter(prefix="/admin", tags=["Admin"])


# ── Stats ────────────────────────────────────────────────────────

@router.get("/scrape-urls/stats")
def get_stats(
    db: Session = Depends(get_db),
    kiprix_db: Session = Depends(get_kiprix_db),
):
    total_urls = db.query(func.count(ScrapeUrl.id)).scalar() or 0
    urls_actives = db.query(func.count(ScrapeUrl.id)).filter(ScrapeUrl.actif == True).scalar() or 0
    try:
        total_donnees = kiprix_db.query(func.count(Produit.id)).scalar() or 0
        derniere_maj = kiprix_db.query(func.max(Produit.scraped_at)).scalar()
    except Exception:
        # kiprix_db peut être vide si le scraper n'a jamais tourné
        total_donnees = 0
        derniere_maj = None

    return {
        "total_urls": total_urls,
        "urls_actives": urls_actives,
        "total_donnees": total_donnees,
        "derniere_maj": derniere_maj,
    }


# ── Scrape URLs CRUD ─────────────────────────────────────────────

@router.get("/scrape-urls", response_model=List[ScrapeUrlResponse])
def list_scrape_urls(db: Session = Depends(get_db)):
    return db.query(ScrapeUrl).order_by(ScrapeUrl.created_at.desc()).all()


@router.post("/scrape-urls", response_model=ScrapeUrlResponse, status_code=201)
def add_scrape_url(data: ScrapeUrlCreate, db: Session = Depends(get_db)):
    url_obj = ScrapeUrl(url=data.url, label=data.label)
    db.add(url_obj)
    db.commit()
    db.refresh(url_obj)
    return url_obj


@router.patch("/scrape-urls/{url_id}", response_model=ScrapeUrlResponse)
def update_scrape_url(url_id: int, data: ScrapeUrlUpdate, db: Session = Depends(get_db)):
    url_obj = db.get(ScrapeUrl, url_id)
    if not url_obj:
        raise HTTPException(status_code=404, detail="URL introuvable")
    if data.actif is not None:
        url_obj.actif = data.actif
    if data.label is not None:
        url_obj.label = data.label
    db.commit()
    db.refresh(url_obj)
    return url_obj


@router.delete("/scrape-urls/{url_id}", status_code=204)
def delete_scrape_url(url_id: int, db: Session = Depends(get_db)):
    url_obj = db.get(ScrapeUrl, url_id)
    if not url_obj:
        raise HTTPException(status_code=404, detail="URL introuvable")
    db.delete(url_obj)
    db.commit()


# ── Scrape Logs ──────────────────────────────────────────────────

@router.get("/scrape/logs", response_model=List[ScrapeLogResponse])
def list_scrape_logs(db: Session = Depends(get_db)):
    return db.query(ScrapeLog).order_by(ScrapeLog.started_at.desc()).limit(50).all()


@router.get("/scrape/logs/{log_id}", response_model=ScrapeLogResponse)
def get_scrape_log(log_id: int, db: Session = Depends(get_db)):
    log = db.get(ScrapeLog, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log introuvable")
    return log


def _do_scrape(log_id: int, territory: str, pages: int):
    """Tâche de fond : appelle le service scraper-api (projet POO) et met à jour le log."""
    db = SessionLocal()
    try:
        with httpx.Client(timeout=600) as client:
            res = client.post(
                f"{settings.SCRAPER_API_URL}/scrape",
                json={"territory": territory, "pages": pages},
            )
            data = res.json()

        log = db.get(ScrapeLog, log_id)
        if log:
            log.status = data.get("status", "error")
            log.nb_produits = data.get("nb_produits", 0)
            log.message = data.get("message") or None
            log.finished_at = datetime.now(timezone.utc)
            db.commit()
    except Exception as e:
        log = db.get(ScrapeLog, log_id)
        if log:
            log.status = "error"
            log.message = str(e)[:500]
            log.finished_at = datetime.now(timezone.utc)
            db.commit()
    finally:
        db.close()


@router.post("/scrape/run", response_model=ScrapeLogResponse, status_code=201)
def run_scrape(
    req: ScrapeRunRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    log = ScrapeLog(
        territory=req.territory,
        pages=req.pages,
        status="running",
        started_at=datetime.now(timezone.utc),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    background_tasks.add_task(_do_scrape, log.id, req.territory, req.pages)
    return log
