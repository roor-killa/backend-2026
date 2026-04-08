from pathlib import Path
import importlib.util
import sys
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.dependencies import get_current_user
from app.models.utilisateur_model import Utilisateur

router = APIRouter()


def _load_rci_scraper_class() -> type:
    """Import RCIScraper from the local scraper package."""
    scraper_root = Path(__file__).resolve().parents[2] / "scraper"
    scraper_root_str = str(scraper_root)
    if scraper_root_str not in sys.path:
        sys.path.insert(0, scraper_root_str)

    try:
        module_path = scraper_root / "src" / "scrapers" / "rci_scraper.py"
        spec = importlib.util.spec_from_file_location("karibdocs_rci_scraper", module_path)
        if spec is None or spec.loader is None:
            raise ImportError("Impossible de construire le module RCIScraper")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        RCIScraper = getattr(module, "RCIScraper")
    except Exception as exc:  # pragma: no cover - runtime environment dependent
        raise HTTPException(
            status_code=500,
            detail=(
                "Impossible de charger le module de scraping. "
                "Vérifie les dépendances du dossier scraper (requests, beautifulsoup4, etc.)."
            ),
        ) from exc

    return RCIScraper


@router.get("/sources")
def get_scraping_sources(current_user: Utilisateur = Depends(get_current_user)):
    return {
        "sources": [
            {
                "id": "rci",
                "label": "RCI Martinique",
                "default_start_url": "https://rci.fm/martinique/infos/toutes-les-infos",
            }
        ]
    }


@router.post("/rci")
def scrape_rci(
    max_depth: int = Query(1, ge=0, le=3),
    max_pages: int = Query(10, ge=1, le=100),
    delay: float = Query(1.5, ge=0.5, le=10),
    current_user: Utilisateur = Depends(get_current_user),
):
    """Run an on-demand RCI scraping job and return collected articles."""
    scraper_cls = _load_rci_scraper_class()
    scraper = scraper_cls(max_depth=max_depth, delay=delay)

    try:
        items: list[dict[str, Any]] = scraper.scrape(max_pages=max_pages)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Erreur scraping RCI: {exc}") from exc

    return {
        "source": "rci",
        "parameters": {
            "max_depth": max_depth,
            "max_pages": max_pages,
            "delay": delay,
        },
        "count": len(items),
        "items": items,
    }