"""
ScraperManager — Gestionnaire de scrapers (Pattern Factory).

MEMBRE 1 : Ce fichier est entièrement sous ta responsabilité.
"""

from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base_scraper import BaseScraper
from .scrapers import KiprixScraper


class ScraperManager:
    """
    Gestionnaire de scrapers utilisant le Pattern Factory.

    Centralise la création et l'exécution des scrapers.
    Supporte le scraping séquentiel et parallèle (threading).

    Example:
        >>> manager = ScraperManager()
        >>> scraper = manager.create_scraper('kiprix', territory='gp')
        >>> data = scraper.scrape(max_pages=5)
    """

    # Dictionnaire de mapping nom → classe (Pattern Factory)
    SCRAPERS: Dict[str, type] = {
        'kiprix': KiprixScraper,
    }

    def create_scraper(self, name: str, **kwargs) -> BaseScraper:
        """
        Crée et retourne une instance du scraper demandé (Factory).

        Args:
            name: Identifiant du scraper (ex: 'kiprix').
            **kwargs: Arguments passés au constructeur du scraper.

        Returns:
            Instance du scraper correspondant.

        Raises:
            ValueError: Si le nom du scraper est inconnu.

        Example:
            >>> mgr = ScraperManager()
            >>> scraper = mgr.create_scraper('kiprix', territory='mq')
        """
        scraper_class = self.SCRAPERS.get(name)
        if scraper_class is None:
            raise ValueError(
                f"Scraper '{name}' inconnu. "
                f"Scrapers disponibles : {list(self.SCRAPERS.keys())}"
            )
        return scraper_class(**kwargs)

    def scrape_all(
        self,
        max_pages: int = 5,
        parallel: bool = False,
        max_workers: int = 2
    ) -> Dict[str, List[Dict]]:
        """
        Lance tous les scrapers et retourne un dict de résultats.

        Args:
            max_pages: Nombre de pages par scraper.
            parallel: Si True, utilise ThreadPoolExecutor pour paralléliser.
            max_workers: Nombre de threads (utilisé seulement si parallel=True).

        Returns:
            Dictionnaire {nom_scraper: liste_de_données}.
        """
        if parallel:
            return self._scrape_parallel(max_pages, max_workers)
        return self._scrape_sequential(max_pages)

    def _scrape_sequential(self, max_pages: int) -> Dict[str, List[Dict]]:
        """Lance les scrapers un par un, dans l'ordre."""
        results = {}
        for name in self.SCRAPERS:
            scraper = self.create_scraper(name)
            results[name] = scraper.scrape(max_pages=max_pages)
        return results

    def _scrape_parallel(
        self, max_pages: int, max_workers: int
    ) -> Dict[str, List[Dict]]:
        """Lance les scrapers en parallèle avec ThreadPoolExecutor."""
        results = {}

        def run_scraper(name: str):
            scraper = self.create_scraper(name)
            return name, scraper.scrape(max_pages=max_pages)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(run_scraper, name): name
                for name in self.SCRAPERS
            }
            for future in as_completed(futures):
                try:
                    name, data = future.result()
                    results[name] = data
                except Exception as e:
                    name = futures[future]
                    results[name] = []

        return results
