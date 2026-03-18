# Guide d'Équipe - Projet Kiprix (Groupe 2)

## 🎯 Focus Unique : Kiprix.com

Comme convenu, tout le groupe travaille exclusivement sur le site **kiprix.com**. L'objectif est d'avoir le scraper le plus complet et robuste possible pour ce site.

---

## 👥 Répartition des Missions

### 👤 Guindo : Lead Développeur & Architecte
**Vos tâches :**
- Maintenir et améliorer `BaseScraper.py` (cœur du système).
- Gérer la logique de navigation et pagination dans `kiprix_scraper.py`.
- Assurer le bon fonctionnement du `ScraperManager` et du système de cache.
- Développer et enrichir l'interface en ligne de commande (`cli.py`).

### 👤 Akonou : Analyste de Données & Features
**Vos tâches :**
- Enrichir l'extraction dans `kiprix_scraper.py` (récupérer les images, les catégories précises, les stocks si disponibles).
- Développer les algorithmes d'analyse dans `analyzer.py` (calcul des écarts de prix, détection des promos).
- Créer un **Notebook Jupyter** pour visualiser les résultats (graphiques de distribution des prix).
- Gérer les exports multi-formats (Excel stylisé).

### 👤 Sadi : Qualité, DevOps & Documentation
**Vos tâches :**
- Écrire les **tests unitaires** avec `pytest` pour atteindre > 70% de couverture.
- Configurer l'environnement **Docker** pour que le scraper tourne partout.
- Produire la documentation technique finale (Diagramme UML, Rapport PDF).
- S'assurer du respect des règles éthiques (User-Agent, délais entre requêtes).

---

## 🛠️ Commandes Utiles

### Pour tester le scraper
```bash
python main.py scrape --pages 3 --territory gp
```

### Pour lancer les tests
```bash
pytest tests/
```

### Pour générer un rapport
```bash
python main.py analyze data/raw/kiprix_gp.json
```

---

## 📅 Objectifs de la Semaine
1. **Guindo** : S'assurer que la pagination fonctionne sur 10+ pages.
2. **Akonou** : Commencer les premiers graphiques sur les prix en Martinique vs France.
3. **Sadi** : Initialiser la suite de tests pour le scraper de base.
