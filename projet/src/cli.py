"""
CLI — Interface en ligne de commande pour le projet Kiprix.

MEMBRE 1 : Ce fichier est entièrement sous ta responsabilité.

Utilisation :
    python main.py scrape --pages 5 --territory gp
    python main.py analyze data/raw/kiprix_gp.json
    python main.py cache-stats
    python main.py cache-clear
"""

import logging
import click

from .manager import ScraperManager
from .analyzer import DataAnalyzer
from .cache import CacheManager


def setup_logging(verbose: bool = False) -> None:
    """Configure le niveau de logging global."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Mode verbose (debug)')
def cli(verbose: bool) -> None:
    """TP Scraping — Groupe 2 — Kiprix.com"""
    setup_logging(verbose)


@cli.command()
@click.option('--pages', '-p', default=5, show_default=True,
              help='Nombre de pages à scraper')
@click.option('--territory', '-t', default='gp', show_default=True,
              help='Territoire DOM : gp, mq, re, gf')
@click.option('--format', '-f', 'output_format',
              type=click.Choice(['json', 'csv', 'both', 'db', 'all']), default='db',
              help='Format de sauvegarde')
def scrape(pages: int, territory: str, output_format: str) -> None:
    """Scrape les produits depuis Kiprix.com."""
    manager = ScraperManager()

    try:
        scraper = manager.create_scraper('kiprix', territory=territory)
    except ValueError as e:
        click.echo(f"Erreur : {e}", err=True)
        raise SystemExit(1)

    click.echo(f"Scraping Kiprix ({territory}) — {pages} page(s)...")
    data = scraper.scrape(max_pages=pages)

    if not data:
        click.echo("Aucune donnée récupérée.", err=True)
        raise SystemExit(1)

    base_name = f"kiprix_{territory}"

    if output_format in ('json', 'both', 'all'):
        scraper.save_to_json(f"{base_name}.json")

    if output_format in ('csv', 'both', 'all'):
        scraper.save_to_csv(f"{base_name}.csv")

    if output_format in ('db', 'all'):
        try:
            from .db_manager import DBManager
            db = DBManager()
            db.init_db()
            db.save_products(data)
            click.echo(click.style(f"✓ Données insérées dans PostgreSQL.", fg='green'))
        except Exception as e:
            click.echo(click.style(f"✗ Erreur lors de la sauvegarde en base : {e}", fg='red'))

    click.echo(click.style(f"✓ {len(data)} produits scrapés.", fg='green'))


@cli.command()
@click.argument('filepath', type=click.Path(exists=True))
@click.option('--export', '-e', type=click.Choice(['excel', 'csv', 'none']),
              default='none', help='Exporter le résultat')
def analyze(filepath: str, export: str) -> None:
    """Analyse un fichier JSON de données Kiprix."""
    analyzer = DataAnalyzer()
    analyzer.load_from_json(filepath)

    click.echo(analyzer.get_summary_report())

    if export == 'excel':
        analyzer.export_to_excel('rapport_kiprix.xlsx')
        click.echo("✓ Exporté vers data/processed/rapport_kiprix.xlsx")
    elif export == 'csv':
        analyzer.export_to_csv('rapport_kiprix.csv')
        click.echo("✓ Exporté vers data/processed/rapport_kiprix.csv")


@cli.command('cache-stats')
def cache_stats() -> None:
    """Affiche les statistiques du cache."""
    cache = CacheManager()
    stats = cache.get_stats()
    click.echo(f"Fichiers en cache : {stats['total_fichiers']}")
    click.echo(f"Taille totale     : {stats['taille_totale_mb']} Mo")


@cli.command('cache-clear')
@click.option('--all', 'clear_all', is_flag=True,
              help='Vider tout le cache (sinon: seulement les entrées expirées)')
def cache_clear(clear_all: bool) -> None:
    """Nettoie le cache."""
    cache = CacheManager()
    if clear_all:
        cache.clear_all_cache()
        click.echo("✓ Cache entièrement vidé.")
    else:
        deleted = cache.clear_old_cache()
        click.echo(f"✓ {deleted} entrées expirées supprimées.")
