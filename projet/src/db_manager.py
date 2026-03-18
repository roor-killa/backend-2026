import os
import logging
from typing import List, Dict
import psycopg2
from psycopg2.extras import DictCursor

class DBManager:
    """Gestionnaire de connexion et d'insertion pour PostgreSQL."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        # Valeurs par défaut pour développement local hors docker si besoin
        self.host = os.environ.get('DB_HOST', 'localhost')
        self.user = os.environ.get('DB_USER', 'laravel')
        self.password = os.environ.get('DB_PASS', 'secret')
        self.dbname = os.environ.get('DB_NAME', 'kiprix_db')
        # Si on est en local et que le port externe est 5433 (comme vu dans `docker ps`)
        self.port = os.environ.get('DB_PORT', '5432' if self.host == 'postgres_db' else '5433')
        
    def get_connection(self):
        """Retourne une connexion à la base de données."""
        try:
            return psycopg2.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                dbname=self.dbname,
                port=self.port
            )
        except Exception as e:
            self.logger.error(f"Erreur de connexion à PostgreSQL ({self.host}:{self.port}): {e}")
            raise

    def init_db(self):
        """Crée la table des produits si elle n'existe pas."""
        query = """
        CREATE TABLE IF NOT EXISTS produits (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            url TEXT,
            price_france VARCHAR(50),
            price_dom VARCHAR(50),
            difference VARCHAR(50),
            quantity_value NUMERIC(10, 4),
            quantity_unit VARCHAR(20),
            unit_reference VARCHAR(20),
            unit_price_france NUMERIC(10, 2),
            unit_price_dom NUMERIC(10, 2),
            territory VARCHAR(10),
            territory_name VARCHAR(100),
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                conn.commit()
            self.logger.info("Table 'produits' initialisée avec succès.")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation de la base : {e}")

    def save_products(self, data: List[Dict]):
        """Insère ou met à jour une liste de produits en base de données."""
        if not data:
            self.logger.warning("Aucune donnée à insérer dans PostgreSQL.")
            return

        query = """
        INSERT INTO produits (
            name, url, price_france, price_dom, difference, 
            quantity_value, quantity_unit, unit_reference,
            unit_price_france, unit_price_dom, territory, territory_name
        ) VALUES (
            %(name)s, %(url)s, %(price_france)s, %(price_dom)s, %(difference)s,
            %(quantity_value)s, %(quantity_unit)s, %(unit_reference)s,
            %(unit_price_france)s, %(unit_price_dom)s, %(territory)s, %(territory_name)s
        )
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.executemany(query, data)
                conn.commit()
            self.logger.info(f"{len(data)} produits insérés dans PostgreSQL avec succès.")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'insertion des données : {e}")

