"""
CacheManager — Système de cache pour éviter les requêtes redondantes.

MEMBRE 1 : Ce fichier est entièrement sous ta responsabilité.
"""

import hashlib
import json
import time
import logging
from pathlib import Path
from typing import Optional


class CacheManager:
    """
    Système de cache basé sur des fichiers avec expiration par timestamp.

    Évite de re-scraper des pages récemment visitées en stockant leur
    contenu HTML sur le disque avec une durée de vie configurable.

    Attributes:
        cache_dir (Path): Dossier de stockage du cache.
        max_age (int): Durée de vie du cache en secondes.

    Example:
        >>> cache = CacheManager(max_age=3600)
        >>> content = cache.get_cached_page(url)
        >>> if not content:
        ...     content = scraper.fetch_raw(url)
        ...     cache.cache_page(url, content)
    """

    def __init__(self, cache_dir: str = "data/cache", max_age: int = 3600) -> None:
        """
        Initialise le cache.

        Args:
            cache_dir: Dossier où stocker les fichiers cache.
            max_age: Durée de vie en secondes (défaut: 1 heure).
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_age = max_age
        self.logger = logging.getLogger(self.__class__.__name__)

    def _url_to_hash(self, url: str) -> str:
        """Convertit une URL en hash MD5 pour nommer le fichier cache."""
        return hashlib.md5(url.encode()).hexdigest()

    def get_cached_page(self, url: str) -> Optional[str]:
        """
        Retourne le contenu mis en cache si encore valide.

        Args:
            url: URL de la page à vérifier.

        Returns:
            Contenu HTML en cache, ou None si absent/expiré.
        """
        cache_file = self.cache_dir / f"{self._url_to_hash(url)}.json"

        if not cache_file.exists():
            return None

        # Vérifier si le cache est encore valide
        age = time.time() - cache_file.stat().st_mtime
        if age > self.max_age:
            self.logger.debug(f"Cache expiré pour : {url}")
            cache_file.unlink()
            return None

        with open(cache_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.logger.debug(f"Cache hit : {url}")
        return data.get('content')

    def cache_page(self, url: str, content: str) -> None:
        """
        Sauvegarde le contenu HTML d'une page dans le cache.

        Args:
            url: URL de la page.
            content: Contenu HTML à mettre en cache.
        """
        cache_file = self.cache_dir / f"{self._url_to_hash(url)}.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({'url': url, 'content': content}, f)
        self.logger.debug(f"Mis en cache : {url}")

    def clear_old_cache(self) -> int:
        """
        Supprime les entrées de cache expirées.

        Returns:
            Nombre de fichiers supprimés.
        """
        deleted = 0
        for cache_file in self.cache_dir.glob("*.json"):
            age = time.time() - cache_file.stat().st_mtime
            if age > self.max_age:
                cache_file.unlink()
                deleted += 1
        self.logger.info(f"{deleted} fichiers cache supprimés.")
        return deleted

    def clear_all_cache(self) -> None:
        """Supprime tout le cache."""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
        self.logger.info("Cache entièrement vidé.")

    def get_stats(self) -> dict:
        """
        Retourne les statistiques du cache.

        Returns:
            Dict avec : total_fichiers, taille_totale_mb.
        """
        files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in files)
        return {
            'total_fichiers': len(files),
            'taille_totale_mb': round(total_size / (1024 * 1024), 2)
        }
