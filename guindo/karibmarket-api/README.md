# KaribMarket API 🌺

API REST de gestion de petites annonces caribéennes — Projet fil rouge du cours Web Backend L2 (Université des Antilles).

---

## 🚀 Installation

```bash
# Créer et activer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

## 🗄️ Base de données

```bash
# Lancer PostgreSQL via Docker
docker run --name karib-postgres \
  -e POSTGRES_USER=karib \
  -e POSTGRES_PASSWORD=karib_pass \
  -e POSTGRES_DB=karibmarket \
  -p 5434:5432 \
  -d postgres:15

# Appliquer les migrations
alembic upgrade head
```

## ▶️ Lancer l'API

```bash
uvicorn app.main:app --reload --port 8000
```

- **http://localhost:8000/docs** — Swagger UI
- **http://localhost:8000/redoc** — ReDoc

---

## 🔗 Intégration Kiprix (base de données externe)

L'API se connecte également à la base de données **Kiprix** (projet de scraping POO) pour exposer les données scrapées en tant qu'endpoints REST.

**Base de données** : `kiprix_db` sur `localhost:5433` (conteneur `postgres_db`)  
**Table** : `produits` — comparaison des prix France / DOM (Martinique, Guadeloupe, Réunion, Guyane)

```bash
# Variable d'environnement nécessaire dans .env
KIPRIX_DATABASE_URL=postgresql://laravel:secret@localhost:5433/kiprix_db
```

**Endpoints disponibles** : `GET /api/v1/kiprix/produits` avec filtres `territory` et pagination.

---

## 📚 Avancement des TPs

| TP | Module | Statut |
|----|--------|--------|
| TP1 | Prise en main FastAPI | ✅ |
| TP2 | Pydantic & Validation | ✅ |
| TP3 | SQLAlchemy & Alembic | ✅ |
| TP4 | Authentification JWT | ✅ |
