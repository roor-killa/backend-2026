"""
KiprixScraper — Scraper pour kiprix.com.

RESPONSABILITÉS :
- MEMBRE 1 : méthodes __init__, scrape(), parse() — navigation et extraction de base
- MEMBRE 2 : méthodes avancées get_products_by_category(), get_average_price_difference(),
             scrape_all_territories() — analyse et enrichissement des données
"""

import re
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup

from ..base_scraper import BaseScraper


# ============================================================
# MEMBRE 1 — Navigation, pagination et extraction de base
# ============================================================

class KiprixScraper(BaseScraper):
    """
    Scraper pour kiprix.com — comparateur de prix entre la France et les DOM.

    kiprix.com permet de comparer les prix des produits alimentaires
    entre la France métropolitaine et les territoires d'outre-mer (Guadeloupe,
    Martinique, etc.).

    Attributes:
        territory (str): Code du territoire (ex: 'gp' pour Guadeloupe, 'mq' pour Martinique).

    Example:
        >>> scraper = KiprixScraper(territory='gp')
        >>> data = scraper.scrape(max_pages=5)
        >>> scraper.save_to_json('kiprix_gp.json')
    """

    # Territoires disponibles sur le site
    TERRITORIES = {
        'gp': 'Guadeloupe',
        'mq': 'Martinique',
        're': 'La Réunion',
        'gf': 'Guyane',
    }

    def __init__(self, territory: str = 'gp', delay: float = 1.5) -> None:
        """
        Initialise le scraper Kiprix pour un territoire donné.

        Args:
            territory: Code du territoire DOM (défaut: 'gp' pour Guadeloupe).
            delay: Délai entre les requêtes en secondes.

        Raises:
            ValueError: Si le code territoire n'est pas reconnu.
        """
        if territory not in self.TERRITORIES:
            raise ValueError(
                f"Territoire '{territory}' invalide. "
                f"Choisir parmi : {list(self.TERRITORIES.keys())}"
            )
        base_url = f"https://www.kiprix.com/fr-{territory}"
        super().__init__(base_url, delay)
        self.territory = territory

    def scrape(self, max_pages: int = 10) -> List[Dict]:
        """
        Scrape les pages de produits Kiprix avec gestion de la pagination.

        Parcourt les pages une par une jusqu'à max_pages ou jusqu'à
        ce qu'une page retourne 0 produits (fin du catalogue).

        Args:
            max_pages: Nombre maximum de pages à scraper.

        Returns:
            Liste de dictionnaires, un par produit trouvé.
        """
        self.data = []

        for page_num in range(1, max_pages + 1):
            # Construction de l'URL paginée
            if page_num == 1:
                url = f"{self.base_url}/produits"
            else:
                url = f"{self.base_url}/produits?page={page_num}"

            soup = self.fetch_page(url)
            if not soup:
                self.logger.warning(f"Page {page_num} inaccessible, arrêt.")
                break

            items = self.parse(soup)

            # Si la page est vide, on a atteint la fin du catalogue
            if not items:
                self.logger.info(f"Fin du catalogue à la page {page_num}.")
                break

            self.data.extend(items)
            self.logger.info(f"Page {page_num} : {len(items)} produits. Total : {len(self.data)}")

        return self.data

    def parse(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Extrait les données produits depuis une page de résultats Kiprix.

        Sélecteurs identifiés sur le site (classes Tailwind CSS) :
        - Card produit : div.group.relative.bg-gray-100
        - Nom : h3 a
        - Prix France / DOM : p.text-gray-900 (1er et 2ème)
        - Écart % : span.text-red-600

        Args:
            soup: HTML de la page parsé par BeautifulSoup.

        Returns:
            Liste de dicts avec les clés : name, url, price_france,
            price_dom, difference, territory.
        """
        items = []

        cards = soup.select('div.group.relative.bg-gray-100')

        for card in cards:
            try:
                # Nom et URL du produit
                link_elem = card.select_one('h3 a')
                if not link_elem:
                    continue

                name = link_elem.get_text(strip=True)
                href = link_elem.get('href', '')
                url = f"https://www.kiprix.com{href}" if href.startswith('/') else href

                # Prix France et prix DOM
                prices = card.find_all('p', class_='text-gray-900')
                price_france = prices[0].get_text(strip=True) if len(prices) > 0 else ""
                price_dom = prices[1].get_text(strip=True) if len(prices) > 1 else ""

                # Écart en pourcentage (ex: "+ 45,81%")
                diff_elem = card.select_one('span.text-red-600')
                difference = diff_elem.get_text(strip=True) if diff_elem else ""

                quantity_value, quantity_unit, quantity_base, unit_reference = self._extract_quantity_from_name(name)
                price_france_num = self._parse_price_to_float(price_france)
                price_dom_num = self._parse_price_to_float(price_dom)

                unit_price_france = (
                    round(price_france_num / quantity_base, 2)
                    if price_france_num is not None and quantity_base not in (None, 0)
                    else None
                )
                unit_price_dom = (
                    round(price_dom_num / quantity_base, 2)
                    if price_dom_num is not None and quantity_base not in (None, 0)
                    else None
                )

                items.append({
                    'name': name,
                    'url': url,
                    'price_france': price_france,
                    'price_dom': price_dom,
                    'difference': difference,
                    'quantity_value': quantity_value,
                    'quantity_unit': quantity_unit,
                    'unit_reference': unit_reference,
                    'unit_price_france': unit_price_france,
                    'unit_price_dom': unit_price_dom,
                    'territory': self.territory,
                    'territory_name': self.TERRITORIES[self.territory],
                })

            except Exception as e:
                self.logger.warning(f"Erreur parsing card : {e}")

        return items

    @staticmethod
    def _parse_price_to_float(price_text: str) -> Optional[float]:
        """Convertit un prix texte (ex: '4,95 €') en float (4.95)."""
        match = re.search(r'([0-9]+(?:[\s\u00a0]?[0-9]{3})*(?:[.,][0-9]+)?)', str(price_text))
        if not match:
            return None

        cleaned = (
            match.group(1)
            .replace(' ', '')
            .replace('\u00a0', '')
            .replace(',', '.')
        )
        try:
            return float(cleaned)
        except ValueError:
            return None

    @staticmethod
    def _extract_quantity_from_name(name: str) -> Tuple[Optional[float], Optional[str], Optional[float], Optional[str]]:
        """
        Extrait la quantité depuis le nom produit.

        Returns:
            (quantity_value, quantity_unit, quantity_base, unit_reference)
            - quantity_base: quantité convertie en kg/L (base pour prix unitaire)
            - unit_reference: '€/kg' ou '€/L'
        """
        text = str(name).lower().replace('µ', 'u')
        match = re.search(r'(\d+(?:[.,]\d+)?)\s*(kg|g|mg|l|ml|cl)\b', text)
        if not match:
            return None, None, None, None

        quantity_value = float(match.group(1).replace(',', '.'))
        quantity_unit = match.group(2)

        if quantity_unit == 'kg':
            return quantity_value, quantity_unit, quantity_value, '€/kg'
        if quantity_unit == 'g':
            return quantity_value, quantity_unit, quantity_value / 1000, '€/kg'
        if quantity_unit == 'mg':
            return quantity_value, quantity_unit, quantity_value / 1_000_000, '€/kg'
        if quantity_unit == 'l':
            return quantity_value, quantity_unit, quantity_value, '€/L'
        if quantity_unit == 'cl':
            return quantity_value, quantity_unit, quantity_value / 100, '€/L'
        if quantity_unit == 'ml':
            return quantity_value, quantity_unit, quantity_value / 1000, '€/L'

        return quantity_value, quantity_unit, None, None

    # ============================================================
    # MEMBRE 2 — Méthodes d'analyse avancée
    # ============================================================

    def get_products_by_category(self, category: str) -> List[Dict]:
        """
        Filtre les produits par catégorie.

        La catégorie est déduite de l'URL du produit
        (ex: 'epicerie-sucree' trouvé dans l'URL → correspond).

        Args:
            category: Catégorie à filtrer (ex: 'epicerie-sucree').

        Returns:
            Liste des produits dont l'URL contient la catégorie.
        """
        if not self.data:
            self.logger.warning("Aucune donnée — lancez d'abord scrape().")
            return []

        filtered = [
            p for p in self.data
            if category.lower() in p.get('url', '').lower()
        ]
        self.logger.info(f"Catégorie '{category}' : {len(filtered)} produits trouvés.")
        return filtered

    def get_average_price_difference(self) -> float:
        """
        Calcule l'écart de prix moyen (%) entre la France et le DOM.

        Extrait le float depuis la colonne 'difference'
        (ex: "+ 45,81%" → 45.81) et retourne la moyenne.

        Returns:
            Moyenne des écarts en pourcentage (float), ou 0.0 si aucune donnée.
        """
        if not self.data:
            self.logger.warning("Aucune donnée — lancez d'abord scrape().")
            return 0.0

        valeurs = []
        for p in self.data:
            diff_str = p.get('difference', '')
            match = re.search(r'(\d+(?:[,\.]\d+)?)', diff_str.replace(',', '.'))
            if match:
                try:
                    valeurs.append(float(match.group(1)))
                except ValueError:
                    pass

        if not valeurs:
            return 0.0

        moyenne = sum(valeurs) / len(valeurs)
        self.logger.info(f"Écart moyen France/DOM : {round(moyenne, 2)}%")
        return round(moyenne, 2)

    def scrape_all_territories(self, max_pages: int = 5) -> List[Dict]:
        """
        Scrape tous les territoires disponibles et fusionne les résultats.

        Boucle sur self.TERRITORIES, crée une instance KiprixScraper
        pour chaque territoire, scrape max_pages pages et fusionne tout.

        Args:
            max_pages: Pages à scraper par territoire.

        Returns:
            Liste combinée de tous les produits de tous les territoires.
        """
        all_data = []

        for code, nom in self.TERRITORIES.items():
            self.logger.info(f"Scraping du territoire : {nom} ({code})")
            try:
                scraper = KiprixScraper(territory=code, delay=self.delay)
                data = scraper.scrape(max_pages=max_pages)
                all_data.extend(data)
                self.logger.info(f"  → {len(data)} produits récupérés ({nom})")
            except Exception as e:
                self.logger.error(f"Erreur sur le territoire {code} : {e}")

        self.data = all_data
        self.logger.info(f"Total multi-territoire : {len(all_data)} produits")
        return all_data
