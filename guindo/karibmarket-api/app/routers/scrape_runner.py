from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import subprocess
import os

from app.kiprix_database import get_kiprix_db
from app.models.kiprix.scrape_log import ScrapeLog
from app.models.kiprix.produit import Produit
from app.schemas.kiprix.scrape_log_schema import ScrapeLogResponse, ScrapeRunRequest
from app.routers.auth import get_current_user
from app.models.utilisateur import Utilisateur

router = APIRouter(
    prefix="/admin/scrape",
    tags=["Admin - Runner"]
)

# Chemin vers le projet scraper — à adapter selon ton environnement
SCRAPER_PATH = os.environ.get("SCRAPER_PATH", "/Users/user/Documents/poo-2026/groupe_scp2")
PYTHON_BIN = os.environ.get("SCRAPER_PYTHON", "/Users/user/Documents/poo-2026/groupe_scp2/venv/bin/python")


def run_scraper_task(log_id: int, territory: str, pages: int):
    """Tâche de fond : lance le scraper et met à jour le log."""
    from app.kiprix_database import KiprixSessionLocal
    from app.models.kiprix.scrape_url import ScrapeUrl
    from datetime import datetime
    db = KiprixSessionLocal()

    try:
        result = subprocess.run(
            [PYTHON_BIN, "main.py", "scrape",
             "--territory", territory,
             "--pages", str(pages),
             "--format", "db"],
            cwd=SCRAPER_PATH,
            capture_output=True,
            text=True,
            timeout=300
        )

        log = db.query(ScrapeLog).filter(ScrapeLog.id == log_id).first()
        if not log:
            return

        if result.returncode == 0:
            nb = db.query(Produit).filter(
                Produit.territory == territory.upper()
            ).count()
            log.status = "success"
            log.nb_produits = nb
            log.message = result.stdout[-500:] if result.stdout else "OK"

            # ← Mettre à jour last_scraped_at dans scrape_urls
            scrape_url = db.query(ScrapeUrl).filter(
                ScrapeUrl.url.like(f"%fr-{territory}%")
            ).first()
            if scrape_url:
                scrape_url.last_scraped_at = datetime.utcnow()
                scrape_url.nb_donnees = nb
        else:
            log.status = "error"
            log.message = result.stderr[-500:] if result.stderr else "Erreur inconnue"

        log.finished_at = datetime.utcnow()
        db.commit()

    except subprocess.TimeoutExpired:
        log = db.query(ScrapeLog).filter(ScrapeLog.id == log_id).first()
        if log:
            log.status = "error"
            log.message = "Timeout — scraping trop long (>5min)"
            log.finished_at = datetime.utcnow()
            db.commit()
    except Exception as e:
        log = db.query(ScrapeLog).filter(ScrapeLog.id == log_id).first()
        if log:
            log.status = "error"
            log.message = str(e)
            log.finished_at = datetime.utcnow()
            db.commit()
    finally:
        db.close()

@router.post("/run", response_model=ScrapeLogResponse, status_code=202)
def run_scrape(
    payload: ScrapeRunRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_kiprix_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Lance un scraping en arrière-plan et retourne le log créé."""
    territories_valides = ["gp", "mq", "re", "gf"]
    if payload.territory not in territories_valides:
        raise HTTPException(
            status_code=400,
            detail=f"Territoire invalide. Valeurs acceptées : {territories_valides}"
        )

    # Créer le log
    log = ScrapeLog(
        territory=payload.territory,
        pages=payload.pages,
        status="running"
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    # Lancer en arrière-plan
    background_tasks.add_task(
        run_scraper_task, log.id, payload.territory, payload.pages
    )

    return log


@router.get("/logs", response_model=List[ScrapeLogResponse])
def get_logs(
    db: Session = Depends(get_kiprix_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Retourne l'historique des scraping lancés."""
    return db.query(ScrapeLog).order_by(ScrapeLog.started_at.desc()).limit(50).all()


@router.get("/logs/{log_id}", response_model=ScrapeLogResponse)
def get_log(
    log_id: int,
    db: Session = Depends(get_kiprix_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Retourne le statut d'un scraping en cours ou terminé."""
    log = db.query(ScrapeLog).filter(ScrapeLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log introuvable")
    return log
