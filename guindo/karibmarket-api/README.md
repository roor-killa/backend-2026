# KaribMarket API 🌺

API REST de gestion de petites annonces caribéennes et comparateur de prix France/DOM — Projet fil rouge du cours Web Backend L2 (Université des Antilles).

---

## 🏗️ Architecture

```
karibmarket-api/
├── app/
│   ├── main.py                          # Point d'entrée FastAPI + Redis lifespan
│   ├── config.py                        # Variables d'environnement (pydantic-settings)
│   ├── database.py                      # Connexion SQLAlchemy (karibmarket DB)
│   ├── kiprix_database.py               # Connexion SQLAlchemy (kiprix_db)
│   ├── models/
│   │   ├── annonce.py                   # Modèle Annonce + CategorieEnum
│   │   ├── utilisateur.py               # Modèle Utilisateur
│   │   └── kiprix/
│   │       ├── produit.py               # Modèle Produit (données scrapées Kiprix)
│   │       ├── scrape_url.py            # Modèle ScrapeUrl (URLs à scraper)
│   │       └── scrape_log.py            # Modèle ScrapeLog (historique scraping)
│   ├── routers/
│   │   ├── annonces.py                  # CRUD annonces (async + BackgroundTasks)
│   │   ├── auth.py                      # Register / Login JWT
│   │   ├── prix.py                      # Lecture produits Kiprix
│   │   ├── scrape_urls_router.py        # Gestion URLs à scraper (admin)
│   │   ├── scrape_runner.py             # Lancement scraper en background
│   │   └── chatbot.py                   # Chatbot RAG hybride (Ollama/OpenAI)
│   ├── schemas/
│   │   ├── annonce.py                   # Schémas Pydantic annonces
│   │   ├── utilisateur.py               # Schémas Pydantic utilisateurs
│   │   └── kiprix/
│   │       ├── produit_schema.py        # Schémas Pydantic produits
│   │       ├── scrape_url_schema.py     # Schémas Pydantic URLs
│   │       └── scrape_log_schema.py     # Schémas Pydantic logs
│   └── services/
│       ├── auth_service.py              # hash_password, JWT, decode_token
│       └── annonce_service.py
├── migrations/                          # Alembic migrations
│   └── versions/
│       └── 182244d47c62_creation_tables_initiales.py
├── scripts/seed.py                      # Données de test
├── tests/test_annonces.py               # Tests pytest (19 tests)
├── .env                                 # Variables d'environnement (ne pas committer)
├── .env.example                         # Template .env (à committer)
├── alembic.ini
├── docker-compose.yml                   # API + PostgreSQL + Redis
├── Dockerfile
├── Makefile                             # Commandes simplifiées
├── pytest.ini
└── requirements.txt
```

---

## 🚀 Installation

### Prérequis
- Python 3.12+
- Docker & Docker Compose
- Redis (via Docker)
- Ollama (pour le chatbot RAG)

### 1. Cloner et préparer l'environnement

```bash
git clone <repo>
cd karibmarket-api

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
pip install email-validator "bcrypt==4.0.1" "python-jose[cryptography]"
pip install redis fastapi-cache2
pip install ollama "sentence-transformers==3.0.0" "numpy<2"
```

### 2. Configurer les variables d'environnement

Copier `.env.example` en `.env` :

```env
DATABASE_URL=postgresql://laravel:secret@localhost:5433/karibmarket
SECRET_KEY=une-cle-secrete-tres-longue-et-aleatoire
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
KIPRIX_DATABASE_URL=postgresql://laravel:secret@localhost:5433/kiprix_db
REDIS_URL=redis://localhost:6379
SCRAPER_PATH=/chemin/vers/groupe_scp2
SCRAPER_PYTHON=/chemin/vers/groupe_scp2/venv/bin/python
```

### 3. Lancer PostgreSQL + Redis

```bash
docker compose up -d
```

Ou avec le container existant :

```bash
docker run --name karib-postgres \
  -e POSTGRES_USER=laravel \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=karibmarket \
  -p 5433:5432 \
  -d pgvector/pgvector:pg16

docker run -d --name karib-redis -p 6379:6379 redis:7-alpine
```

### 4. Appliquer les migrations

```bash
alembic upgrade head
```

### 5. Créer les tables Kiprix manuellement

```bash
docker exec -it postgres_db psql -U laravel -d kiprix_db -c "
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS scrape_urls (
    id SERIAL PRIMARY KEY,
    url TEXT NOT NULL UNIQUE,
    label VARCHAR(100),
    actif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_scraped_at TIMESTAMP,
    nb_donnees INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS scrape_logs (
    id SERIAL PRIMARY KEY,
    territory VARCHAR(10) NOT NULL,
    pages INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'running',
    nb_produits INTEGER DEFAULT 0,
    message TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP
);"
```

### 6. Lancer l'API

```bash
uvicorn app.main:app --reload --port 8000
```

### Avec Makefile

```bash
make start    # Démarre tout
make migrate  # Applique les migrations
make logs     # Voir les logs
make shell    # Accès bash au container
```

---

## 📚 Endpoints

### Authentification
| Méthode | Route | Description |
|---------|-------|-------------|
| POST | `/api/v1/auth/register` | Créer un compte |
| POST | `/api/v1/auth/login` | Connexion → token JWT |

### Annonces (async + cache Redis)
| Méthode | Route | Auth | Description |
|---------|-------|------|-------------|
| GET | `/api/v1/annonces` | Non | Liste paginée avec filtres (cache 60s) |
| POST | `/api/v1/annonces` | Oui | Créer + email/notification en background |
| GET | `/api/v1/annonces/{id}` | Non | Détail (cache 2min) |
| PATCH | `/api/v1/annonces/{id}` | Oui | Modifier (propriétaire uniquement) |
| DELETE | `/api/v1/annonces/{id}` | Oui | Soft delete (propriétaire uniquement) |

### Prix Kiprix
| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/v1/prix` | Liste produits (filtres: search, territory, page) |
| GET | `/api/v1/prix/territoires` | Territoires disponibles |
| GET | `/api/v1/prix/comparaison?search=lait` | Comparer France vs DOM |
| GET | `/api/v1/prix/{id}` | Détail produit |

### Admin — Scraping (JWT requis)
| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/v1/admin/scrape-urls/stats` | Statistiques dashboard |
| GET | `/api/v1/admin/scrape-urls` | Liste URLs enregistrées |
| POST | `/api/v1/admin/scrape-urls` | Ajouter une URL |
| PATCH | `/api/v1/admin/scrape-urls/{id}` | Modifier label/statut |
| DELETE | `/api/v1/admin/scrape-urls/{id}` | Supprimer une URL |
| POST | `/api/v1/admin/scrape/run` | Lancer un scraping (background) |
| GET | `/api/v1/admin/scrape/logs` | Historique des scraping |
| GET | `/api/v1/admin/scrape/logs/{id}` | Statut d'un scraping |

### Chatbot RAG
| Méthode | Route | Description |
|---------|-------|-------------|
| POST | `/api/v1/chatbot` | Question au RAG hybride Kiprix |
| GET | `/api/v1/chatbot/health` | Statut du RAG |

---

## ⚡ Fonctionnalités avancées

### Async/Await + Background Tasks
Toutes les routes sont `async def`. À la création d'une annonce, deux tâches s'exécutent en arrière-plan sans bloquer la réponse :
- Email de confirmation à l'utilisateur
- Notification aux modérateurs

### Cache Redis
```python
@cache(expire=60)   # Liste annonces cachée 60 secondes
@cache(expire=120)  # Détail annonce caché 2 minutes
```

### Chatbot RAG Hybride
Le chatbot combine deux stratégies selon l'intention détectée :
- **Mode analytique** (moins cher, comparer, écart...) → requête SQL directe sur `kiprix_db`
- **Mode sémantique** → recherche vectorielle via pgvector + Ollama (llama3)

---

## 🗄️ Bases de données

| Base | Contenu |
|------|---------|
| `karibmarket` | Utilisateurs, Annonces |
| `kiprix_db` | Produits scrapés, URLs, Logs, Embeddings pgvector |

---

## 🔐 Authentification

L'API utilise **JWT (JSON Web Tokens)** via `python-jose`.

```bash
# 1. Créer un compte
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"nom": "Admin", "email": "admin@karib.com", "mot_de_passe": "password123"}'

# 2. Se connecter
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=admin@karib.com&password=password123"

# 3. Utiliser le token
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/admin/scrape-urls
```

---

## 📖 Documentation interactive

- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

---

## 🧪 Tests

```bash
pytest tests/ -v
pytest tests/ -v --cov=app --cov-report=html
```

**19 tests** couvrant : routes de base, auth, CRUD annonces, pagination, filtres, sécurité (401/403), flux complet.

---

## 🔗 Intégrations avec les autres projets

Ce projet est le **moteur central** de l'architecture multi-projets.

### Avec poo-2026 (groupe_scp2) — orchestrateur + RAG

`scrape_runner.py` lance le scraper en subprocess, et `chatbot.py` importe directement le `HybridRAGEngine` :

```bash
# Scraping via subprocess
$SCRAPER_PYTHON main.py scrape --territory mq --pages 1 --format db

# RAG via import direct
from src.rag.hybrid_rag import HybridRAGEngine
engine = HybridRAGEngine(llm_provider="ollama", model="llama3")
result = engine.ask("Prix du lait en Martinique ?", territory="mq")
```

Configurer `SCRAPER_PATH` et `SCRAPER_PYTHON` dans `.env`.

### Avec web3-2026 (frontend Next.js) — fournisseur de données

Le frontend Next.js (`lib/fastapi.ts`) consomme cette API via `http://localhost:8000/api/v1` :

| Page Web3 | Endpoint consommé |
|-----------|-------------------|
| `/dashboard` | `GET /admin/scrape-urls/stats` |
| `/dashboard/prix` | `GET /prix` |
| `/dashboard/scrape` | `POST /admin/scrape/run` |
| `/dashboard/chatbot` | `POST /chatbot` |
| Gestion URLs | `GET/POST/PATCH/DELETE /admin/scrape-urls` |

Le frontend stocke un token JWT séparé (`fastapi_token` dans localStorage), distinct du token Sanctum Laravel.

### Flux global

```
kiprix.com → groupe_scp2 (subprocess) → kiprix_db → karibmarket-api → Next.js (web3)
                    ↓
             pgvector (RAG) → Ollama → chatbot Next.js
```

---

## 🐳 Docker

```bash
docker build -t karibmarket-api .
docker run -p 8000:8000 --env-file .env karibmarket-api
```

---

## 📦 Stack technique

| Technologie | Version | Usage |
|-------------|---------|-------|
| FastAPI | 0.135.1 | Framework API |
| SQLAlchemy | 2.0.48 | ORM |
| Alembic | 1.18.4 | Migrations |
| Pydantic | 2.12.5 | Validation |
| python-jose | 3.5.0 | JWT |
| passlib + bcrypt | 1.7.4 / 4.0.1 | Hashage passwords |
| Redis + fastapi-cache2 | - | Cache HTTP |
| sentence-transformers | 3.0.0 | Embeddings RAG |
| ollama | - | LLM local (llama3) |
| psycopg2-binary | 2.9.11 | Driver PostgreSQL |
| pytest | - | Tests unitaires |
| uvicorn | 0.41.0 | Serveur ASGI |