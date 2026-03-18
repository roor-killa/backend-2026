"""
BaseScraper — Classe abstraite commune à tous les scrapers.

MEMBRE 1 : Ce fichier est entièrement sous ta responsabilité.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import requests
import json
import csv
import logging
from pathlib import Path
from bs4 import BeautifulSoup

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    logging.warning("Selenium et/ou webdriver-manager ne sont pas installés.")


class BaseScraper(ABC):
    """
    Classe abstraite définissant le contrat de base pour tous les scrapers.

    Attributes:
        base_url (str): URL de base du site à scraper.
        delay (float): Délai (en secondes) entre chaque requête (rate limiting).
        headers (dict): En-têtes HTTP envoyés avec chaque requête.
        data (List[Dict]): Données collectées lors du scraping.
        logger (Logger): Logger propre à chaque sous-classe.
    """

    def __init__(self, base_url: str, delay: float = 1.5) -> None:
        """
        Initialise le scraper avec l'URL de base et les paramètres communs.

        Args:
            base_url: URL racine du site cible.
            delay: Temps d'attente entre les requêtes (en secondes).
        """
        self.base_url = base_url
        self.delay = delay
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
                      'image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        self.data: List[Dict] = []
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Configure et retourne un logger nommé d'après la sous-classe."""
        logger = logging.getLogger(self.__class__.__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    def _get_driver(self):
        """Crée et retourne une instance de Selenium WebDriver.
        Fonctionne en local (télécharge Chrome) et dans Docker (utilise Chromium installé).
        """
        if not hasattr(self, '_driver') or self._driver is None:
            import os
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service

            options = Options()
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument(f'user-agent={self.headers["User-Agent"]}')

            # En Docker, Chromium est déjà installé dans le container
            chrome_bin = os.environ.get('CHROME_BIN')
            chromedriver_path = os.environ.get('CHROMEDRIVER_PATH')

            if chrome_bin and chromedriver_path:
                # Mode Docker : utiliser les binaires installés
                options.binary_location = chrome_bin
                self._driver = webdriver.Chrome(
                    service=Service(chromedriver_path),
                    options=options
                )
            else:
                # Mode local : télécharger automatiquement via webdriver-manager
                from webdriver_manager.chrome import ChromeDriverManager
                self._driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    options=options
                )
        return self._driver


    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Récupère une page web et retourne un objet BeautifulSoup.
        Utilise Selenium pour contourner les protections anti-bot (Cloudflare).

        Args:
            url: URL complète de la page à récupérer.

        Returns:
            Objet BeautifulSoup si succès, None sinon.
        """
        import time; time.sleep(self.delay)
        try:
            self.logger.info(f"Fetching (Selenium): {url}")
            driver = self._get_driver()
            driver.get(url)
            
            # Attendre que la page charge (Cloudflare peut prendre qq secondes)
            import time; time.sleep(2)
            
            html = driver.page_source
            if "Cloudflare" in html or "Just a moment" in driver.title:
                self.logger.warning(f"Bloqué par Cloudflare sur : {url}")
                return None
                
            return BeautifulSoup(html, 'lxml')
            
        except Exception as e:
            self.logger.error(f"Erreur Selenium sur {url}: {e}")
            return None

    def save_to_json(self, filename: str) -> None:
        """
        Sauvegarde self.data en JSON dans data/raw/.

        Args:
            filename: Nom du fichier (ex: 'kiprix_gp.json').
        """
        path = Path("data/raw") / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        self.logger.info(f"Sauvegardé: {path} ({len(self.data)} entrées)")

    def save_to_csv(self, filename: str) -> None:
        """
        Sauvegarde self.data en CSV dans data/raw/.

        Args:
            filename: Nom du fichier (ex: 'kiprix_gp.csv').
        """
        if not self.data:
            self.logger.warning("Aucune donnée à sauvegarder.")
            return
        path = Path("data/raw") / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.data[0].keys())
            writer.writeheader()
            writer.writerows(self.data)
        self.logger.info(f"Sauvegardé: {path}")

    @abstractmethod
    def scrape(self, max_pages: int = 1) -> List[Dict]:
        """
        Méthode principale de scraping — à implémenter dans chaque sous-classe.

        Args:
            max_pages: Nombre maximum de pages à scraper.

        Returns:
            Liste de dictionnaires contenant les données extraites.
        """
        pass

    @abstractmethod
    def parse(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Extrait les données structurées depuis le HTML d'une page.

        Args:
            soup: Objet BeautifulSoup de la page à parser.

        Returns:
            Liste de dictionnaires avec les données de la page.
        """
        pass
