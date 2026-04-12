from pathlib import Path
import importlib.util
import re
import sys
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.services.document_service import DocumentService
from app.models.utilisateur_model import Utilisateur

router = APIRouter()


class ScrapedArticleIn(BaseModel):
    title: str = ""
    author: str | None = None
    infos: str | None = None
    body: str | None = None
    photo: str | None = None
    url: str | None = None
    depth: int | None = None


class SaveScrapedArticlesIn(BaseModel):
    items: list[ScrapedArticleIn] = Field(default_factory=list)


class SavedDocumentOut(BaseModel):
    id: int
    original_name: str


def _slugify_filename(value: str, fallback: str) -> str:
    base = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    if not base:
        base = fallback
    return f"{base[:80]}.txt"


def _article_to_text(article: ScrapedArticleIn) -> str:
    title = (article.title or "Sans titre").strip()
    author = (article.author or "Auteur inconnu").strip()
    infos = (article.infos or "").strip()
    photo = (article.photo or "").strip()
    url = (article.url or "").strip()
    depth = article.depth if article.depth is not None else ""
    body = (article.body or "").strip()

    lines = [
        f"Titre: {title}",
        f"Auteur: {author}",
        f"Infos: {infos}",
        f"Photo: {photo}",
        f"URL: {url}",
        f"Profondeur: {depth}",
        "",
        body,
    ]
    return "\n".join(lines).strip() + "\n"


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


@router.post("/rci/save")
def save_scraped_rci_articles(
    payload: SaveScrapedArticlesIn,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
):
    """Persist scraped RCI items like manual document uploads, then index in background."""
    if not payload.items:
        raise HTTPException(status_code=400, detail="Aucun article à sauvegarder")

    service = DocumentService(db)
    saved_docs: list[dict[str, Any]] = []

    try:
        for idx, article in enumerate(payload.items, start=1):
            filename_hint = article.title or f"rci-article-{idx}"
            filename = _slugify_filename(filename_hint, fallback=f"rci-article-{idx}")
            content = _article_to_text(article).encode("utf-8")

            doc = service.save_from_bytes(
                content=content,
                filename=filename,
                user=current_user,
                source="rci_scrape",
            )
            background_tasks.add_task(service.index_document, doc.id)
            saved_docs.append({"id": doc.id, "original_name": doc.original_name})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erreur sauvegarde des articles: {exc}") from exc

    return {
        "message": f"{len(saved_docs)} article(s) sauvegardé(s) et indexation lancée.",
        "count": len(saved_docs),
        "documents": saved_docs,
    }