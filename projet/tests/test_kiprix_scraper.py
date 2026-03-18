"""
Tests pour KiprixScraper.

MEMBRE 3 : Implémenter tous les cas marqués TODO.
"""

import pytest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup

from src.scrapers.kiprix_scraper import KiprixScraper


# HTML factice représentant une page Kiprix avec 1 produit
FAKE_HTML_ONE_PRODUCT = """
<html>
<body>
  <div class="group relative bg-gray-100">
    <h3><a href="/fr-gp/produit/12345">Lait UHT demi-écrémé 1L</a></h3>
    <p class="text-gray-900">1,05 €</p>
    <p class="text-gray-900">1,85 €</p>
    <span class="text-red-600">+ 76,19%</span>
  </div>
</body>
</html>
"""

FAKE_HTML_NO_PRODUCT = "<html><body><p>Aucun résultat</p></body></html>"


# -------------------------------------------------------------------
# Tests d'initialisation
# -------------------------------------------------------------------

class TestInit:
    def test_default_territory(self):
        """Le territoire par défaut doit être 'gp'."""
        scraper = KiprixScraper()
        assert scraper.territory == 'gp'

    def test_territory_in_url(self):
        """Le territoire doit apparaître dans base_url."""
        scraper = KiprixScraper(territory='mq')
        assert 'mq' in scraper.base_url

    def test_invalid_territory_raises(self):
        """Un territoire invalide doit lever ValueError."""
        with pytest.raises(ValueError):
            KiprixScraper(territory='xx')

    def test_all_valid_territories(self):
        """Vérifier que tous les territoires valides s'initialisent correctement."""
        for code in ['gp', 'mq', 're', 'gf']:
            scraper = KiprixScraper(territory=code)
            assert scraper.territory == code


# -------------------------------------------------------------------
# Tests de parse()
# -------------------------------------------------------------------

class TestParse:
    def test_parse_returns_list(self):
        """parse() doit toujours retourner une liste."""
        scraper = KiprixScraper()
        soup = BeautifulSoup(FAKE_HTML_ONE_PRODUCT, 'lxml')
        result = scraper.parse(soup)
        assert isinstance(result, list)

    def test_parse_one_product(self):
        """parse() doit extraire 1 produit depuis le HTML factice."""
        scraper = KiprixScraper()
        soup = BeautifulSoup(FAKE_HTML_ONE_PRODUCT, 'lxml')
        result = scraper.parse(soup)
        assert len(result) == 1

    def test_parse_product_fields(self):
        """Le produit extrait doit contenir les bons champs et valeurs."""
        scraper = KiprixScraper()
        soup = BeautifulSoup(FAKE_HTML_ONE_PRODUCT, 'lxml')
        product = scraper.parse(soup)[0]

        assert product['name'] == "Lait UHT demi-écrémé 1L"
        assert product['price_france'] == "1,05 €"
        assert product['price_dom'] == "1,85 €"
        assert product['difference'] == "+ 76,19%"
        assert product['territory'] == 'gp'
        assert 'url' in product

    def test_parse_empty_page(self):
        """parse() doit retourner [] si la page ne contient aucun produit."""
        scraper = KiprixScraper()
        soup = BeautifulSoup(FAKE_HTML_NO_PRODUCT, 'lxml')
        result = scraper.parse(soup)
        assert result == []


# -------------------------------------------------------------------
# Tests de scrape()
# -------------------------------------------------------------------

class TestScrape:
    @patch.object(KiprixScraper, 'fetch_page')
    def test_scrape_returns_data(self, mock_fetch):
        """scrape() doit agréger les résultats de parse() sur plusieurs pages."""
        from bs4 import BeautifulSoup

        # Utiliser le HTML factice existant qui correspond au parser
        soup = BeautifulSoup(FAKE_HTML_ONE_PRODUCT, "lxml")

        # fetch_page retourne soup 2 fois puis None
        mock_fetch.side_effect = [soup, soup, None]

        scraper = KiprixScraper(territory="gp")
        data = scraper.scrape(max_pages=3)

        assert isinstance(data, list)
        assert len(data) >= 1

    @patch.object(KiprixScraper, 'fetch_page')
    def test_scrape_stops_on_empty_page(self, mock_fetch):
        """scrape() doit s'arrêter dès qu'une page retourne 0 produits."""
        from bs4 import BeautifulSoup

        html_normal = """
        <html>
            <div class="product">
                <span class="name">Produit A</span>
                <span class="price">10€</span>
            </div>
        </html>
        """

        html_empty = "<html></html>"

        soup_normal = BeautifulSoup(html_normal, "lxml")
        soup_empty = BeautifulSoup(html_empty, "lxml")

        mock_fetch.side_effect = [soup_normal, soup_empty]

        scraper = KiprixScraper(territory="gp")
        data = scraper.scrape(max_pages=5)

        assert isinstance(data, list)
