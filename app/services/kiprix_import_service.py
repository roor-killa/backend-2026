from pathlib import Path
from typing import Any, TypedDict

import requests
import json
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.produit_kiprix import ProduitKiprix


class KiprixImportResult(TypedDict):
    territoire: str
    pages: int
    produits_scrapes: int
    produits_ajoutes: int
    produits_mis_a_jour: int


def _build_scraper() -> Any:
    project_root = Path(__file__).resolve().parents[2]
    import sys

    if str(project_root) not in sys.path:
        sys.path.append(str(project_root))

    from projet.src.scrapers.kiprix_scraper import KiprixScraper

    return KiprixScraper


def _scrape_without_selenium(territory: str, max_pages: int) -> list[dict[str, Any]]:
    KiprixScraper = _build_scraper()
    scraper = KiprixScraper(territory=territory, delay=0)

    products: list[dict[str, Any]] = []
    base_url = f"https://www.kiprix.com/fr-{territory}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
    }

    session = requests.Session()
    session.headers.update(headers)

    for page_num in range(1, max_pages + 1):
        url = f"{base_url}/produits" if page_num == 1 else f"{base_url}/produits?page={page_num}"
        response = session.get(url, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        page_items = scraper.parse(soup)
        if not page_items:
            break
        products.extend(page_items)

    return products


def _load_local_products(territory: str) -> list[dict[str, Any]]:
    project_root = Path(__file__).resolve().parents[2]
    raw_dir = project_root / "projet" / "data" / "raw"

    candidates = [raw_dir / f"kiprix_{territory}.json"]
    if raw_dir.exists():
        candidates.extend(sorted(raw_dir.glob("*.json")))

    for file_path in candidates:
        if not file_path.exists():
            continue
        try:
            with file_path.open("r", encoding="utf-8") as file_obj:
                data = json.load(file_obj)
            if isinstance(data, list) and data:
                return data
        except Exception:
            continue

    raise RuntimeError(
        "Impossible de scraper Kiprix en ligne et aucun fichier local de produits n'a ete trouve "
        "dans projet/data/raw/*.json"
    )


def import_kiprix_products(db: Session, territory: str = "mq", max_pages: int = 1) -> KiprixImportResult:
    try:
        products = _scrape_without_selenium(territory=territory, max_pages=max_pages)
    except Exception:
        products = _load_local_products(territory=territory)

    inserted = 0
    updated = 0

    for item in products:
        existing = db.execute(
            select(ProduitKiprix).where(
                ProduitKiprix.url == item.get("url", ""),
                ProduitKiprix.territory == item.get("territory", territory),
            )
        ).scalar_one_or_none()

        payload = {
            "name": item.get("name", ""),
            "url": item.get("url", ""),
            "price_france": item.get("price_france"),
            "price_dom": item.get("price_dom"),
            "difference": item.get("difference"),
            "quantity_value": item.get("quantity_value"),
            "quantity_unit": item.get("quantity_unit"),
            "unit_reference": item.get("unit_reference"),
            "unit_price_france": item.get("unit_price_france"),
            "unit_price_dom": item.get("unit_price_dom"),
            "territory": item.get("territory", territory),
            "territory_name": item.get("territory_name"),
        }

        if existing:
            for key, value in payload.items():
                setattr(existing, key, value)
            updated += 1
        else:
            db.add(ProduitKiprix(**payload))
            inserted += 1

    db.commit()

    return {
        "territoire": territory,
        "pages": max_pages,
        "produits_scrapes": len(products),
        "produits_ajoutes": inserted,
        "produits_mis_a_jour": updated,
    }
