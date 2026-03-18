# TP Scraping — Groupe 2 | Kiprix.com

Projet de web scraping orienté objet — Licence 2 Informatique, UA.  
Site scrappé : **kiprix.com** (comparateur de prix France / DOM).

---

## 🏗️ Architecture

```
tp_scraping/
├── src/
│   ├── base_scraper.py        # Classe abstraite (Membre 1)
│   ├── manager.py             # ScraperManager / Factory (Membre 1)
│   ├── analyzer.py            # DataAnalyzer / pandas (Membre 2)
│   ├── cache.py               # CacheManager (Membre 1)
│   └── scrapers/
│       └── kiprix_scraper.py  # KiprixScraper (Membre 1 + 2)
├── tests/                     # Tests unitaires (Membre 3)
├── notebooks/                 # Analyse Jupyter (Membre 2)
├── docker/                    # Dockerfile + Compose (Membre 3)
├── docs/                      # UML + Documentation PDF (Membre 3)
└── main.py                    # CLI (Membre 1)
```

---

## 🚀 Installation

```bash
python3 -m venv venv
source venv/bin/activate       # Mac/Linux
## TP Scraping — Groupe 2 — Kiprix

## 📌 Description

Projet de Programmation Orientée Objet (POO) — L2 Informatique.

Ce projet consiste à développer un scraper pour le site **Kiprix.com** afin de récupérer les produits et analyser les écarts de prix entre la France et les territoires d’outre-mer (DOM).

Le projet inclut :

- Scraping structuré et modulaire
- Gestion du cache
- Analyse statistique avec pandas
- Interface CLI avec Click
- Tests unitaires complets avec pytest
- Containerisation avec Docker

---

## 👥 Membres du groupe

- **SADI**
- **GUINDO**
- **AKONOU**

---

## 🏗 Architecture du projet


src/
│
├── base_scraper.py # Classe abstraite de scraping
├── scrapers/
│ └── kiprix_scraper.py
│
├── manager.py # Gestion des scrapers
├── cache.py # Système de cache
├── analyzer.py # Analyse des données (pandas)
├── cli.py # Interface ligne de commande
│
tests/ # Tests unitaires
Dockerfile # Containerisation


### 🔹 BaseScraper
Classe abstraite définissant :
- fetch_page()
- save_to_json()
- save_to_csv()

### 🔹 KiprixScraper
Implémentation concrète pour Kiprix.com.

### 🔹 ScraperManager
Factory pour créer dynamiquement les scrapers.

### 🔹 CacheManager
Système de cache basé sur des fichiers JSON avec expiration.

### 🔹 DataAnalyzer
Analyse statistique des données scrapées :
- Statistiques descriptives
- Export CSV / Excel

### 🔹 CLI
Interface utilisateur via Click :

```bash
python main.py scrape
python main.py analyze
python main.py cache-stats
python main.py cache-clear
```

⚙ Installation (mode classique)
1️⃣ Installer les dépendances
pip install -r requirements.txt
2️⃣ Lancer le CLI
python main.py --help

🚀 Utilisation
🔹 Scraper
python main.py scrape --pages 1 --territory gp

Territoires disponibles :

gp (Guadeloupe)

mq (Martinique)

re (Réunion)

gf (Guyane)

🔹 Analyse des données
python main.py analyze data/raw/kiprix_gp.json

Exporter :

python main.py analyze data/raw/kiprix_gp.json --export excel
python main.py analyze data/raw/kiprix_gp.json --export csv
🔹 Gestion du cache
python main.py cache-stats
python main.py cache-clear
🧪 Tests & Qualité

Lancer tous les tests :

pytest

Lancer avec couverture :

pytest --cov=src

📊 Couverture actuelle : 72%

Tous les modules principaux sont testés :

base_scraper

kiprix_scraper

manager

cache

analyzer

🐳 Docker
🔹 Build
docker build -t kiprix-app .
🔹 Exécuter
docker run kiprix-app python main.py scrape --pages 1 --territory gp

Pour sauvegarder les fichiers localement :

docker run -v ${PWD}:/app kiprix-app python main.py scrape --pages 1 --territory gp
🎯 Objectifs pédagogiques atteints

Architecture modulaire orientée objet

Tests unitaires avancés (mock, monkeypatch)

Couverture de code > 70%

Gestion de cache

Analyse de données avec pandas

Interface CLI professionnelle

Containerisation Docker

📚 Technologies utilisées

Python 3.11

requests

BeautifulSoup

pandas

pytest

click

Docker



