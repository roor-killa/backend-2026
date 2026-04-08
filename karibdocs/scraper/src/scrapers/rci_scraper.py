"""Scraper pour rci.fm — articles d'actualité Martinique.

Cible : https://rci.fm/martinique/infos/toutes-les-infos
Explore les liens internes au domaine rci.fm jusqu'à une profondeur
configurable, en récoltant titres et paragraphes de chaque page visitée.

Sortie : fichier JSON dans scraper/data/raw/
"""

import logging
import time
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag

from src.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

# Répertoire de sortie par défaut (scraper/data/raw/)
_DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"


class RCIScraper(BaseScraper):
    """Scraper récursif pour le site rci.fm (actualités Martinique).

    Parcourt les pages à partir de l'URL de départ, suit les liens
    internes au domaine rci.fm sans doublon, et extrait les titres
    et paragraphes de chaque page visitée.

    Attributes:
        start_url: URL de la page d'entrée du scraping.
        max_depth: Profondeur maximale de suivi des liens (0 = page de départ uniquement).
        visited: Ensemble des URLs déjà visitées (évite les doublons).
        domain: Domaine autorisé pour le suivi des liens.
    """

    BASE_URL = "https://rci.fm"
    START_PATH = "/martinique/infos/toutes-les-infos"

    def __init__(
        self,
        max_depth: int = 1,
        delay: float = 1.5,
        start_url: str | None = None,
    ) -> None:
        """Initialise le scraper RCI.

        Args:
            max_depth: Profondeur maximale de crawl (0 = page de départ seule).
            delay: Pause en secondes entre chaque requête (rate limiting).
            start_url: URL de départ (par défaut : toutes-les-infos Martinique).
        """
        super().__init__(self.BASE_URL, delay=delay)
        self.start_url: str = start_url or (self.BASE_URL + self.START_PATH)
        self.max_depth: int = max_depth
        self.visited: set[str] = set()
        self.domain: str = urlparse(self.BASE_URL).netloc  # "rci.fm"

    # ------------------------------------------------------------------
    # Helpers — filtrage et normalisation des liens
    # ------------------------------------------------------------------

    def _normalize_url(self, url: str) -> str:
        """Supprime le fragment (#...) et le slash terminal pour normaliser.

        Args:
            url: URL brute.

        Returns:
            URL nettoyée.
        """
        parsed = urlparse(url)
        # Recompose sans fragment
        clean = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        return clean.rstrip("/")

    def _is_valid_link(self, url: str) -> bool:
        """Vérifie qu'un lien est interne au domaine rci.fm et pas un fichier binaire.

        Args:
            url: URL absolue à tester.

        Returns:
            True si le lien doit être suivi.
        """
        parsed = urlparse(url)
        # Même domaine (ou sous-domaine)
        if self.domain not in parsed.netloc:
            return False
        # Exclure les fichiers non-HTML
        skip_ext = (".pdf", ".jpg", ".jpeg", ".png", ".gif", ".mp3", ".mp4", ".zip")
        if parsed.path.lower().endswith(skip_ext):
            return False
        # Exclure les ancres vides ou javascript
        if not parsed.scheme.startswith("http"):
            return False
        return True

    @staticmethod
    def _looks_like_article(url: str) -> bool:
        """Heuristique : les URLs d'articles RCI ont 4+ segments de chemin.

        Ex: /martinique/infos/Faits-divers/Mon-Article  → True
            /martinique/infos/culture                    → False
        """
        path = urlparse(url).path.strip("/")
        return len(path.split("/")) >= 4

    def _extract_links(self, soup: BeautifulSoup, current_url: str) -> list[str]:
        """Extrait les liens internes, articles en priorité.

        Les liens qui ressemblent à des pages article (4+ segments)
        sont placés en tête de liste pour que le crawl DFS les
        atteigne avant les pages de navigation / catégorie.

        Args:
            soup: Page parsée.
            current_url: URL de la page en cours (résolution des relatifs).

        Returns:
            Liste d'URLs absolues, normalisées et dédupliquées.
        """
        seen: set[str] = set()
        article_links: list[str] = []
        other_links: list[str] = []
        for a_tag in soup.find_all("a", href=True):
            href = str(a_tag["href"])
            absolute = urljoin(current_url, href)
            normalized = self._normalize_url(absolute)
            if normalized in seen or normalized in self.visited:
                continue
            if self._is_valid_link(normalized):
                seen.add(normalized)
                if self._looks_like_article(normalized):
                    article_links.append(normalized)
                else:
                    other_links.append(normalized)
        # Articles first so DFS prioritises real content
        return article_links + other_links

    # ------------------------------------------------------------------
    # Parsing — extraction du contenu d'un article
    # ------------------------------------------------------------------

    def _is_article_page(self, soup: BeautifulSoup) -> bool:
        """Détecte si la page est un article (vs. listing / preview)."""
        return soup.find("h1", attrs={"itemprop": "name"}) is not None

    def parse(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        """Extrait les données structurées d'un article RCI.

        Sélecteurs utilisés :
            - titre  : <h1 itemprop="name">
            - auteur : [itemprop="author"]
            - infos  : 3ᵉ élément .info (index 2)
            - corps  : [property="schema:text"] (texte concaténé)

        Args:
            soup: Page HTML parsée.

        Returns:
            Liste contenant un unique dictionnaire article,
            ou liste vide si la page n'est pas un article.
        """
        if not self._is_article_page(soup):
            return []

        # --- Titre ---
        title_tag = soup.find("h1", attrs={"itemprop": "name"})
        title = title_tag.get_text(strip=True) if title_tag else ""

        # --- Auteur ---
        author_tag = soup.find(attrs={"itemprop": "author"})
        author = author_tag.get_text(strip=True) if author_tag else ""

        # --- Image ---
        photo_tag = soup.find("img", attrs={"itemprop": "image"})
        photo = photo_tag.get("src") if photo_tag else ""

        # --- Infos (date / catégorie — 3ᵉ élément .info) ---
        infos_elems = soup.find_all(attrs={"class": "info"})
        infos = infos_elems[2].get_text(strip=True) if len(infos_elems) > 2 else ""

        # --- Corps de l'article ---
        contenu_elems = soup.find_all(attrs={"property": "schema:text"})
        body = "".join(elem.get_text(strip=True) for elem in contenu_elems)

        if not title and not body:
            return []

        return [{
            "title": title,
            "author": author,
            "photo": photo,
            "infos": infos,
            "body": body,
        }]

    # ------------------------------------------------------------------
    # Crawl récursif
    # ------------------------------------------------------------------

    def _crawl(self, url: str, depth: int, max_pages: int) -> None:
        """Parcourt récursivement les pages jusqu'à la profondeur demandée.

        Args:
            url: URL à visiter.
            depth: Profondeur actuelle (0 = page de départ).
            max_pages: Nombre maximum total de pages à visiter (0 = illimité).
        """
        # Conditions d'arrêt
        normalized = self._normalize_url(url)
        if normalized in self.visited:
            return
        if depth > self.max_depth:
            return
        if max_pages and len(self.visited) >= max_pages:
            return

        # Marquer comme visitée
        self.visited.add(normalized)
        logger.info("Crawl [profondeur=%d] %s", depth, normalized)

        # Récupérer la page (utilise fetch_page de BaseScraper avec rate limiting)
        soup = self.fetch_page(normalized)
        if soup is None:
            return

        # Extraire le contenu (uniquement les vraies pages article)
        entries = self.parse(soup)
        for entry in entries:
            entry["url"] = normalized
            entry["depth"] = depth
            self.data.append(entry)
            self._notify("parse", {"url": normalized, "count": len(entries)})

        # Si on n'a pas atteint la profondeur max, suivre les liens
        if depth < self.max_depth:
            child_links = self._extract_links(soup, normalized)
            for link in child_links:
                if max_pages and len(self.visited) >= max_pages:
                    break
                self._crawl(link, depth + 1, max_pages)

    # ------------------------------------------------------------------
    # Interface publique (méthodes abstraites implémentées)
    # ------------------------------------------------------------------

    def scrape(self, max_pages: int = 0) -> list[dict[str, Any]]:
        """Lance le scraping récursif à partir de la page de départ.

        Args:
            max_pages: Nombre maximum de pages à visiter (0 = illimité,
                       la profondeur max_depth reste respectée).

        Returns:
            Liste des entrées collectées (self.data).
        """
        start_time = time.time()
        logger.info(
            "Démarrage RCIScraper — profondeur=%d, max_pages=%d, url=%s",
            self.max_depth, max_pages, self.start_url,
        )

        self.data.clear()
        self.visited.clear()

        self._crawl(self.start_url, depth=0, max_pages=max_pages)

        duration = time.time() - start_time
        self._notify("done", {"total": len(self.data), "duration": duration})
        logger.info(
            "RCIScraper terminé — %d articles, %d pages visitées en %.1fs",
            len(self.data), len(self.visited), duration,
        )
        return self.data

    def to_document(self, item: dict[str, Any]) -> dict[str, Any]:
        """Normalise une entrée brute vers le schéma commun `documents`.

        Args:
            item: Dictionnaire issu de parse().

        Returns:
            Dictionnaire conforme au schéma `documents`.
        """
        return {
            "source": "rci",
            "doc_type": "article",
            "title": item.get("title", ""),
            "content": item.get("body", ""),
            "url": item.get("url"),
            "published_at": None,
            "metadata": {
                "author": item.get("author", ""),
                "photo": item.get("photo", ""),
                "infos": item.get("infos", ""),
                "depth": item.get("depth", 0),
            },
        }


# ------------------------------------------------------------------
# Point d'entrée en ligne de commande
# ------------------------------------------------------------------

def main() -> None:
    """Exécute le scraper RCI et sauvegarde les résultats en JSON."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Scraper RCI.fm — articles d'actualité Martinique"
    )
    parser.add_argument(
        "-d", "--depth",
        type=int,
        default=1,
        help="Profondeur maximale de crawl (défaut : 1)",
    )
    parser.add_argument(
        "-m", "--max-pages",
        type=int,
        default=0,
        help="Nombre maximum de pages à visiter, 0 = illimité (défaut : 0)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.5,
        help="Délai entre les requêtes en secondes (défaut : 1.5)",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Chemin du fichier JSON de sortie (défaut : data/raw/rci_raw.json)",
    )
    args = parser.parse_args()

    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    )

    # Instanciation et lancement
    scraper = RCIScraper(max_depth=args.depth, delay=args.delay)

    from src.observers import LogObserver
    scraper.attach(LogObserver("RCI"))

    scraper.scrape(max_pages=args.max_pages)

    # Sauvegarde
    output_path = Path(args.output) if args.output else _DEFAULT_OUTPUT_DIR / "rci_raw.json"
    scraper.save_to_json(output_path)
    scraper.save_to_csv(output_path.with_suffix(".csv"))
    print(f"✓ {len(scraper.data)} articles sauvegardés → {output_path}")


if __name__ == "__main__":
    main()
