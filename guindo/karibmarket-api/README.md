# KaribMarket API 🌺

API REST de gestion de petites annonces caribéennes et comparateur de prix France/DOM — Projet fil rouge du cours Web Backend L2 (Université des Antilles).

---

## 🏗️ Architecture

```
karibmarket-api/
├── app/
│   ├── main.py                        # Point d'entrée FastAPI
│   ├── config.py                      # Variables d'environnement (pydantic-settings)
│   ├── database.py                    # Connexion SQLAlchemy (karibmarket DB)
│   ├── kiprix_database.py             # Connexion SQLAlchemy (kiprix_db)
│   ├── models/
│   │   ├── annonce.py                 # Modèle Annonce + CategorieEnum
│   │   ├── utilisateur.py             # Modèle Utilisateur
│   │   └── kiprix/
│   │       ├── produit.py             # Modèle Produit (données scrapées)
│   │       ├── scrape_url.py          # Modèle ScrapeUrl (URLs à scraper)
│   │       └── scrape_log.py          # Modèle ScrapeLog (historique scraping)
│   ├── routers/
│   │   ├── annonces.py                # CRUD annonces
│   │   ├── auth.py                    # Register / Login JWT
│   │   ├── prix.py                    # Lecture produits Kiprix
│   │   ├── scrape_urls_router.py      # Gestion URLs à scraper (admin)
│   │   └── scrape_runner.py           # Lancement scraper en background
│   ├── schemas/
│   │   ├── annonce.py                 # Schémas Pydantic annonces
│   │   ├── utilisateur.py             # Schémas Pydantic utilisateurs
│   │   └── kiprix/
│   │       ├── produit_schema.py      # Schémas Pydantic produits
│   │       ├── scrape_url_schema.py   # Schémas Pydantic URLs
│   │       └── scrape_log_schema.py   # Schémas Pydantic logs
│   └── services/
│       ├── auth_service.py            # hash_password, JWT, decode_token
│       └── annonce_service.py
├── migrations/                        # Alembic migrations
│   └── versions/
│       └── 182244d47c62_creation_tables_initiales.py
├── scripts/
│   └── seed.py                        # Données de test
├── tests/
│   └── test_annonces.py
├── .env                               # Variables d'environnement (ne pas committer)
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## 🚀 Installation

### Prérequis
- Python 3.12+
- Docker & Docker Compose
- PostgreSQL (via Docker)

### 1. Cloner et préparer l'environnement

```bash
git clone <repo>
cd karibmarket-api

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
pip install email-validator
pip install "bcrypt==4.0.1"
pip install "python-jose[cryptography]"
```

### 2. Configurer les variables d'environnement

Créer un fichier `.env` à la racine :

```env
DATABASE_URL=postgresql://laravel:secret@localhost:5433/karibmarket
SECRET_KEY=une-cle-secrete-tres-longue-et-aleatoire
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
KIPRIX_DATABASE_URL=postgresql://laravel:secret@localhost:5433/kiprix_db
SCRAPER_PATH=/chemin/vers/groupe_scp2
SCRAPER_PYTHON=/chemin/vers/groupe_scp2/venv/bin/python
```

### 3. Lancer PostgreSQL

```bash
docker-compose up -d
```

Ou avec le container existant :

```bash
docker run --name karib-postgres \
  -e POSTGRES_USER=laravel \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=karibmarket \
  -p 5433:5432 \
  -d postgres:16-alpine
```

### 4. Appliquer les migrations

```bash
alembic upgrade head
```

### 5. Créer les tables Kiprix manuellement

```bash
docker exec -it postgres_db psql -U laravel -d kiprix_db -c "
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

---

## 📚 Endpoints

### Authentification
| Méthode | Route | Description |
|---------|-------|-------------|
| POST | `/api/v1/auth/register` | Créer un compte |
| POST | `/api/v1/auth/login` | Connexion → token JWT |

### Annonces
| Méthode | Route | Description | Auth |
|---------|-------|-------------|------|
| GET | `/api/v1/annonces` | Liste paginée avec filtres | Non |
| POST | `/api/v1/annonces` | Créer une annonce | Oui |
| GET | `/api/v1/annonces/{id}` | Détail annonce | Non |
| PATCH | `/api/v1/annonces/{id}` | Modifier annonce | Oui |
| DELETE | `/api/v1/annonces/{id}` | Soft delete | Oui |

### Prix Kiprix
| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/v1/prix` | Liste produits scrapés (filtres: search, territory, page) |
| GET | `/api/v1/prix/territoires` | Liste des territoires disponibles |
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
| POST | `/api/v1/admin/scrape/run` | Lancer un scraping |
| GET | `/api/v1/admin/scrape/logs` | Historique des scraping |
| GET | `/api/v1/admin/scrape/logs/{id}` | Statut d'un scraping |

---

## 🗄️ Bases de données

Le projet utilise **deux bases PostgreSQL** :

| Base | Contenu |
|------|---------|
| `karibmarket` | Utilisateurs, Annonces |
| `kiprix_db` | Produits scrapés, URLs, Logs |

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
| psycopg2-binary | 2.9.11 | Driver PostgreSQL |
| uvicorn | 0.41.0 | Serveur ASGI |
