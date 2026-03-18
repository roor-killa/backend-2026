import time
from pathlib import Path
from src.cache import CacheManager


def test_cache_page_and_get_cached_page(tmp_path):
    cache = CacheManager(cache_dir=tmp_path, max_age=3600)

    url = "https://example.com"
    content = "<html>Test</html>"

    # Mettre en cache
    cache.cache_page(url, content)

    # Récupérer depuis le cache
    cached = cache.get_cached_page(url)

    assert cached == content


def test_get_cached_page_returns_none_if_not_exists(tmp_path):
    cache = CacheManager(cache_dir=tmp_path, max_age=3600)

    result = cache.get_cached_page("https://notcached.com")

    assert result is None


def test_cache_expiration(tmp_path):
    cache = CacheManager(cache_dir=tmp_path, max_age=1)

    url = "https://example.com"
    content = "<html>Test</html>"

    cache.cache_page(url, content)

    # Attendre que le cache expire
    time.sleep(2)

    result = cache.get_cached_page(url)

    assert result is None


def test_clear_all_cache(tmp_path):
    cache = CacheManager(cache_dir=tmp_path, max_age=3600)

    cache.cache_page("url1", "data1")
    cache.cache_page("url2", "data2")

    cache.clear_all_cache()

    stats = cache.get_stats()

    assert stats["total_fichiers"] == 0


def test_get_stats(tmp_path):
    cache = CacheManager(cache_dir=tmp_path, max_age=3600)

    cache.cache_page("url1", "data1")

    stats = cache.get_stats()

    assert stats["total_fichiers"] == 1
    assert isinstance(stats["taille_totale_mb"], float)
