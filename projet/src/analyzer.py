"""
DataAnalyzer — Analyse statistique des données Kiprix.

MEMBRE 2 : Ce fichier est entièrement sous ta responsabilité.
"""

import re
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

import pandas as pd


class DataAnalyzer:
    """
    Analyse les données scrapées depuis kiprix.com avec pandas.

    Fournit des statistiques descriptives, des analyses de tendances
    de prix et des exports multi-formats.

    Attributes:
        df (pd.DataFrame): DataFrame contenant les données chargées.

    Example:
        >>> analyzer = DataAnalyzer()
        >>> analyzer.load_from_json('data/raw/kiprix_gp.json')
        >>> stats = analyzer.descriptive_stats()
        >>> analyzer.export_to_excel('rapport_kiprix.xlsx')
    """

    def __init__(self) -> None:
        self.df: Optional[pd.DataFrame] = None
        self.logger = logging.getLogger(self.__class__.__name__)

    def load_from_json(self, filepath: str) -> None:
        """
        Charge un fichier JSON dans le DataFrame.

        Args:
            filepath: Chemin vers le fichier JSON (ex: 'data/raw/kiprix_gp.json').

        Raises:
            FileNotFoundError: Si le fichier n'existe pas.
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Fichier introuvable : {filepath}")
        self.df = pd.read_json(filepath)
        self.logger.info(f"Chargé {len(self.df)} entrées depuis {filepath}")

    def descriptive_stats(self) -> Dict[str, Any]:
        """
        Retourne des statistiques descriptives sur les données chargées.

        Returns:
            Dictionnaire avec : total, colonnes, valeurs_manquantes,
            valeurs_uniques par colonne.

        TODO MEMBRE 2 :
            Enrichir avec des stats supplémentaires si pertinent.
        """
        if self.df is None or self.df.empty:
            return {"erreur": "Aucune donnée chargée."}

        return {
            'total': len(self.df),
            'colonnes': list(self.df.columns),
            'valeurs_manquantes': self.df.isnull().sum().to_dict(),
            'valeurs_uniques': {
                col: self.df[col].nunique()
                for col in self.df.columns
                if self.df[col].dtype == object
            }
        }

    def detect_price_trends(self) -> Dict[str, Any]:
        """
        Analyse les écarts de prix entre France et DOM.

        Nettoie la colonne 'difference' (ex: "+ 45,81%" → 45.81)
        et calcule des statistiques par territoire.

        Returns:
            Dict avec moyenne, max, min, médiane des écarts.
        """
        if self.df is None or self.df.empty:
            return {"erreur": "Aucune donnée chargée."}

        if 'difference' not in self.df.columns:
            return {"erreur": "Colonne 'difference' absente des données."}

        def _parse_difference(value: Any) -> Optional[float]:
            import pandas as pd
            if pd.isna(value):
                return None
            match = re.search(r'([+-]?\s*\d+[\d\s.,]*)\s*%', str(value))
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

        working_df = self.df.copy()
        working_df['difference_numeric'] = working_df['difference'].apply(_parse_difference)
        working_df = working_df.dropna(subset=['difference_numeric'])

        if working_df.empty:
            return {"erreur": "Impossible d'extraire des valeurs numériques depuis 'difference'."}

        metrics = {
            'moyenne': round(float(working_df['difference_numeric'].mean()), 2),
            'max': round(float(working_df['difference_numeric'].max()), 2),
            'min': round(float(working_df['difference_numeric'].min()), 2),
            'mediane': round(float(working_df['difference_numeric'].median()), 2),
            'count': int(working_df['difference_numeric'].count()),
        }

        if 'territory' in working_df.columns:
            grouped = (
                working_df.groupby('territory')['difference_numeric']
                .agg(['count', 'mean', 'max', 'min', 'median'])
                .round(2)
            )
            metrics['par_territoire'] = {
                territory: {
                    'count': int(values['count']),
                    'moyenne': float(values['mean']),
                    'max': float(values['max']),
                    'min': float(values['min']),
                    'mediane': float(values['median']),
                }
                for territory, values in grouped.to_dict(orient='index').items()
            }

        return metrics

    def export_to_excel(self, filename: str) -> None:
        """
        Exporte le DataFrame vers un fichier Excel dans data/processed/.

        Args:
            filename: Nom du fichier (ex: 'rapport_kiprix.xlsx').
        """
        if self.df is None:
            self.logger.error("Aucune donnée à exporter.")
            return
        path = Path("data/processed") / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        self.df.to_excel(path, index=False)
        self.logger.info(f"Exporté Excel : {path}")

    def export_to_csv(self, filename: str) -> None:
        """
        Exporte le DataFrame vers un fichier CSV dans data/processed/.

        Args:
            filename: Nom du fichier (ex: 'rapport_kiprix.csv').
        """
        if self.df is None:
            self.logger.error("Aucune donnée à exporter.")
            return
        path = Path("data/processed") / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        self.df.to_csv(path, index=False, encoding='utf-8')
        self.logger.info(f"Exporté CSV : {path}")

    def get_summary_report(self) -> str:
        """
        Génère un rapport texte lisible sur les données.

        TODO MEMBRE 2 - Enrichir ce rapport avec :
            - Le résultat de detect_price_trends()
            - Les top 5 produits les plus chers en DOM
            - La répartition par territoire

        Returns:
            Rapport formaté en chaîne de caractères.
        """
        stats = self.descriptive_stats()
        trends = self.detect_price_trends()
        lines = [
            "=" * 40,
            "  RAPPORT DONNÉES KIPRIX",
            "=" * 40,
            f"Total produits    : {stats.get('total', 0)}",
            f"Colonnes          : {stats.get('colonnes', [])}",
            "",
            "Valeurs manquantes :",
        ]
        for col, count in stats.get('valeurs_manquantes', {}).items():
            lines.append(f"  {col:<20} {count}")

        lines.extend(["", "Tendances des écarts de prix (%) :"])
        if 'erreur' in trends:
            lines.append(f"  {trends['erreur']}")
        else:
            lines.append(f"  Moyenne            : {trends.get('moyenne', 0)}")
            lines.append(f"  Médiane            : {trends.get('mediane', 0)}")
            lines.append(f"  Maximum            : {trends.get('max', 0)}")
            lines.append(f"  Minimum            : {trends.get('min', 0)}")
            lines.append(f"  Échantillons       : {trends.get('count', 0)}")

        if self.df is not None and not self.df.empty and 'price_dom' in self.df.columns:
            dom_prices = (
                self.df.assign(
                    price_dom_num=self.df['price_dom'].astype(str)
                    .str.replace('\u00a0', '', regex=False)
                    .str.replace('€', '', regex=False)
                    .str.replace(' ', '', regex=False)
                    .str.replace(',', '.', regex=False)
                )
            )

            dom_prices['price_dom_num'] = pd.to_numeric(dom_prices['price_dom_num'], errors='coerce')
            top_dom = dom_prices.dropna(subset=['price_dom_num']).nlargest(5, 'price_dom_num')

            lines.extend(["", "Top 5 produits les plus chers en DOM :"])
            if top_dom.empty:
                lines.append("  Données de prix DOM insuffisantes.")
            else:
                for _, row in top_dom.iterrows():
                    product_name = row.get('name', 'Produit inconnu')
                    territory = row.get('territory', 'n/a')
                    price = row.get('price_dom_num', 0)
                    lines.append(f"  - {product_name} ({territory}) : {price:.2f} €")

        if self.df is not None and not self.df.empty and 'territory' in self.df.columns:
            territory_counts = self.df['territory'].value_counts(dropna=False)
            lines.extend(["", "Répartition par territoire :"])
            for territory, count in territory_counts.items():
                territory_label = territory if pd.notna(territory) else 'inconnu'
                lines.append(f"  {territory_label:<20} {int(count)}")

        if (
            self.df is not None
            and not self.df.empty
            and 'unit_price_france' in self.df.columns
            and 'unit_price_dom' in self.df.columns
        ):
            upf = pd.to_numeric(self.df['unit_price_france'], errors='coerce')
            upd = pd.to_numeric(self.df['unit_price_dom'], errors='coerce')
            lines.extend(["", "Prix unitaires (si quantité détectée) :"])
            lines.append(f"  France — moyenne   : {round(float(upf.dropna().mean()), 2) if upf.notna().any() else 'n/a'}")
            lines.append(f"  DOM — moyenne      : {round(float(upd.dropna().mean()), 2) if upd.notna().any() else 'n/a'}")
            lines.append(f"  Produits couverts  : {int(upd.notna().sum())}")

        lines.append("=" * 40)
        return "\n".join(lines)
