# Web Backend — Licence 2ème année
## FastAPI & Python : Construire des APIs Professionnelles

> **Université des Antilles — Département Informatique**  
> Durée totale : 32h
> Prérequis : Python (POO), bases HTTP, notions de bases de données  
> Évaluation : 40% contrôle continu — 60% projet final

---

## 🗺️ Vue d'ensemble du cours

Ce cours vous apprendra à concevoir et développer des **APIs REST professionnelles** avec **FastAPI**, un framework Python moderne, rapide et pensé pour les standards actuels de l'industrie.

À la différence de Laravel que vous avez vu en Web3, FastAPI vous expose directement aux mécanismes fondamentaux du backend : typage fort, documentation automatique, programmation asynchrone, et construction de services indépendants consommables par n'importe quel client (mobile, web, IoT).

### Fil rouge du cours

Vous allez construire **progressivement une API complète** autour d'un projet ancré dans le contexte caribéen :

> **🌺 "KaribMarket API"** — Une API de gestion de petites annonces et de commerces locaux en Martinique/Guadeloupe.  
> Chaque module ajoute une brique au projet. À la fin du semestre, votre API sera documentée, sécurisée, dockerisée et déployable.

---

## 📚 Plan du cours

| # | Module | Type | Durée |
|---|--------|------|-------|
| 1 | Fondamentaux REST & architecture backend | Cours | 2h |
| 2 | Prise en main de FastAPI | Cours + TP | 4h |
| 3 | Modélisation des données avec Pydantic | Cours + TP | 4h |
| 4 | Base de données avec SQLAlchemy & Alembic | Cours + TP | 6h |
| 5 | Authentification & Sécurité (JWT, OAuth2) | Cours + TP | 4h |
| 6 | Programmation asynchrone & performance | Cours + TP | 4h |
| 7 | Containerisation Docker | Cours + TP | 4h |
| 8 | Tests & bonnes pratiques | Cours + TP | 2h |
| 9 | Projet final — Soutenance | Projet | 2h |

---

---

# MODULE 1 — Fondamentaux REST & Architecture Backend
> ⏱ 2h Cours | Pas de TP ce module

## 1.1 Rappels HTTP et REST

### Le protocole HTTP
Le **HyperText Transfer Protocol** est la fondation de toute communication web. Une requête HTTP est composée de :

```
POST /api/v1/annonces HTTP/1.1
Host: api.karibmarket.mq
Content-Type: application/json
Authorization: Bearer <token>

{
  "titre": "Vente de mangues Julie",
  "prix": 3.50
}
```

**Les méthodes HTTP et leur sémantique :**

| Méthode | Signification | Idempotente ? | Body ? |
|---------|---------------|---------------|--------|
| `GET` | Lire une ressource | ✅ Oui | ❌ Non |
| `POST` | Créer une ressource | ❌ Non | ✅ Oui |
| `PUT` | Remplacer entièrement | ✅ Oui | ✅ Oui |
| `PATCH` | Modifier partiellement | ❌ Non | ✅ Oui |
| `DELETE` | Supprimer | ✅ Oui | ❌ Non |

> 💡 **Idempotence** : Appeler la même requête 1 ou 10 fois donne le même résultat côté serveur.

### Les codes de statut HTTP

```
2xx → Succès
  200 OK           → Réponse standard
  201 Created      → Ressource créée
  204 No Content   → Succès sans contenu (DELETE)

4xx → Erreur client
  400 Bad Request  → Requête malformée
  401 Unauthorized → Non authentifié
  403 Forbidden    → Authentifié mais non autorisé
  404 Not Found    → Ressource introuvable
  422 Unprocessable Entity → Données invalides (utilisé par FastAPI)

5xx → Erreur serveur
  500 Internal Server Error → Crash côté serveur
  503 Service Unavailable   → Serveur indisponible
```

## 1.2 Anatomie d'une API REST professionnelle

### Convention de nommage des routes

```
# ✅ BONNE pratique — noms de ressources au pluriel, noms clairs
GET    /api/v1/annonces              → liste des annonces
POST   /api/v1/annonces              → créer une annonce
GET    /api/v1/annonces/{id}         → une annonce précise
PUT    /api/v1/annonces/{id}         → remplacer une annonce
PATCH  /api/v1/annonces/{id}         → modifier partiellement
DELETE /api/v1/annonces/{id}         → supprimer

# Relations
GET    /api/v1/annonces/{id}/images  → images d'une annonce
GET    /api/v1/vendeurs/{id}/annonces → annonces d'un vendeur

# ❌ MAUVAISE pratique
GET    /getAnnonce/1
POST   /createNewAnnonce
GET    /annonce_list
```

### Versioning d'API

```
# Versioning dans l'URL (le plus courant)
/api/v1/annonces
/api/v2/annonces    ← nouvelle version avec breaking changes

# Versioning par header (plus propre mais moins lisible)
Accept: application/vnd.karibmarket.v2+json
```

### Structure d'une réponse cohérente

```json
{
  "success": true,
  "data": {
    "id": 42,
    "titre": "Vente de mangues Julie",
    "prix": 3.50,
    "localisation": "Le Lamentin, Martinique"
  },
  "meta": {
    "timestamp": "2025-03-01T10:30:00Z",
    "version": "1.0"
  }
}
```

```json
{
  "success": false,
  "error": {
    "code": "RESSOURCE_INTROUVABLE",
    "message": "L'annonce avec l'id 42 n'existe pas.",
    "details": null
  }
}
```

## 1.3 Architecture backend moderne : pourquoi des microservices ?

```
Architecture Monolithique (Laravel classique)
┌─────────────────────────────────────┐
│         Application Laravel         │
│  Auth | Annonces | Paiements | ...  │
└─────────────────────────────────────┘

Architecture Microservices / API-first
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Auth API │  │ Annonces │  │Paiements │
│ (FastAPI)│  │   API    │  │   API    │
└──────────┘  └──────────┘  └──────────┘
      ↑              ↑             ↑
      └──────────────┴─────────────┘
                     ↑
          ┌──────────┴──────────┐
          │    API Gateway /    │
          │    Frontend Next.js │
          └─────────────────────┘
```

**Avantages pour vous en tant que développeurs :**
- Chaque service est indépendant → un bug n'affecte pas le reste
- Scalable horizontalement → multiplier les instances si besoin
- Technologies différentes par service → liberté de choix
- Chaque étudiant/équipe peut travailler sur un service séparé

---

---

# MODULE 2 — Prise en main de FastAPI
> ⏱ 2h Cours + 2h TP

## 2.1 Pourquoi FastAPI ?

FastAPI est un framework web Python créé en 2019 par Sebastián Ramírez. Il se distingue par :

| Critère | FastAPI | Flask | Django REST |
|---------|---------|-------|-------------|
| Performance | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Typage & validation | Natif (Pydantic) | Manuel | Serializers |
| Documentation auto | ✅ Swagger + ReDoc | ❌ | Partielle |
| Async natif | ✅ | ❌ | Partielle |
| Courbe d'apprentissage | Douce | Très douce | Raide |

> 🏆 FastAPI est utilisé par Netflix, Uber, Microsoft, et de nombreuses startups.

## 2.2 Installation et premier projet

### Mise en place de l'environnement

```bash
# Créer le dossier projet
mkdir karibmarket-api && cd karibmarket-api

# Créer un environnement virtuel Python
python -m venv venv

# Activer l'environnement (Linux/Mac)
source venv/bin/activate

# Activer l'environnement (Windows)
venv\Scripts\activate

# Installer les dépendances
pip install fastapi uvicorn[standard]

# Sauvegarder les dépendances
pip freeze > requirements.txt
```

### Structure de projet recommandée

```
karibmarket-api/
├── app/
│   ├── __init__.py
│   ├── main.py           ← Point d'entrée
│   ├── config.py         ← Configuration
│   ├── database.py       ← Connexion BDD
│   ├── models/           ← Modèles SQLAlchemy (tables)
│   │   ├── __init__.py
│   │   ├── annonce.py
│   │   └── utilisateur.py
│   ├── schemas/          ← Schémas Pydantic (validation)
│   │   ├── __init__.py
│   │   ├── annonce.py
│   │   └── utilisateur.py
│   ├── routers/          ← Routes organisées par domaine
│   │   ├── __init__.py
│   │   ├── annonces.py
│   │   └── auth.py
│   └── services/         ← Logique métier
│       ├── __init__.py
│       └── annonce_service.py
├── tests/
│   └── test_annonces.py
├── requirements.txt
├── .env
└── docker-compose.yml
```

## 2.3 Votre première API FastAPI

### `app/main.py` — Point d'entrée

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Création de l'application
app = FastAPI(
    title="KaribMarket API",
    description="API de gestion de petites annonces caribéennes 🌺",
    version="1.0.0",
    docs_url="/docs",         # Interface Swagger (documentation interactive)
    redoc_url="/redoc"        # Interface ReDoc (documentation lisible)
)

# Configuration CORS — autorise le frontend à appeler l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # URL de votre frontend Next.js
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route de base — vérification que l'API fonctionne
@app.get("/")
def read_root():
    return {
        "message": "Bienvenue sur KaribMarket API 🌴",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Route de santé — utile pour Docker et les load balancers
@app.get("/health")
def health_check():
    return {"status": "ok"}
```

### Lancer l'application

```bash
# Mode développement avec rechargement automatique
uvicorn app.main:app --reload --port 8000

# L'API est accessible sur :
# http://localhost:8000          → API
# http://localhost:8000/docs     → Documentation Swagger interactive
# http://localhost:8000/redoc    → Documentation ReDoc
```

## 2.4 Routes avec paramètres

```python
from fastapi import FastAPI, Path, Query, HTTPException
from typing import Optional

app = FastAPI()

# Données temporaires (en attendant la base de données)
annonces_db = [
    {"id": 1, "titre": "Vente mangues Julie", "prix": 3.50, "commune": "Le Lamentin"},
    {"id": 2, "titre": "Cours de yoga plage", "prix": 25.00, "commune": "Sainte-Anne"},
    {"id": 3, "titre": "Location VTT", "prix": 15.00, "commune": "Le Morne-Rouge"},
]

# --- Paramètres de chemin (Path Parameters) ---
@app.get("/annonces/{annonce_id}")
def get_annonce(
    annonce_id: int = Path(..., gt=0, description="ID de l'annonce")
):
    """
    Récupère une annonce par son identifiant.
    - **annonce_id** : doit être un entier positif
    """
    for annonce in annonces_db:
        if annonce["id"] == annonce_id:
            return annonce
    # Si non trouvée → erreur 404 automatique
    raise HTTPException(status_code=404, detail=f"Annonce {annonce_id} introuvable")

# --- Paramètres de requête (Query Parameters) ---
@app.get("/annonces")
def list_annonces(
    commune: Optional[str] = Query(None, description="Filtrer par commune"),
    prix_max: Optional[float] = Query(None, gt=0, description="Prix maximum"),
    page: int = Query(1, gt=0, description="Numéro de page"),
    limit: int = Query(10, gt=0, le=100, description="Nombre de résultats par page")
):
    """
    Liste les annonces avec filtres et pagination.
    
    Exemples :
    - /annonces?commune=Le Lamentin
    - /annonces?prix_max=20&page=2&limit=5
    """
    resultats = annonces_db.copy()

    # Filtrage
    if commune:
        resultats = [a for a in resultats if commune.lower() in a["commune"].lower()]
    if prix_max:
        resultats = [a for a in resultats if a["prix"] <= prix_max]

    # Pagination
    total = len(resultats)
    debut = (page - 1) * limit
    fin = debut + limit

    return {
        "data": resultats[debut:fin],
        "meta": {
            "total": total,
            "page": page,
            "limit": limit,
            "pages_total": (total + limit - 1) // limit
        }
    }
```

---

## 🔧 TP 1 — Première API (2h)

### Objectif
Créer la structure du projet KaribMarket et implémenter les premières routes.

### Étapes

**Étape 1 — Setup (20 min)**
1. Créer le dossier `karibmarket-api` avec la structure vue en cours
2. Mettre en place l'environnement virtuel et installer FastAPI + uvicorn
3. Créer `app/main.py` avec la route `/` et `/health`
4. Vérifier que l'API démarre et que `/docs` est accessible

**Étape 2 — Routes de base (40 min)**

Créer dans `app/routers/annonces.py` les routes suivantes en utilisant une liste Python comme base de données temporaire :

Modifier annonces.py
Remplacer FastAPI par APIRouter et app.get(...) par router.get(...)


```python
# Données de test — À vous de compléter avec des annonces réalistes !
annonces = [
    # Insérez au minimum 5 annonces avec : id, titre, description, prix, commune, categorie
]
```

| Route | Méthode | Description |
|-------|---------|-------------|
| `/annonces` | GET | Liste avec filtre `commune` et `categorie` |
| `/annonces/{id}` | GET | Détail d'une annonce |
| `/annonces` | POST | Créer une annonce (body JSON) |
| `/annonces/{id}` | DELETE | Supprimer une annonce |

**Étape 3 — Intégration au main (20 min)**
```python
# Dans app/main.py, importer et inclure le router
from app.routers import annonces

app.include_router(
    annonces.router,
    prefix="/api/v1",
    tags=["Annonces"]  # Groupe dans la doc Swagger
)
```

Avec prefix="/api/v1", les url d'accès aux fonctions deviennent :
http://localhost:8000/api/v1/annonces
http://localhost:8000/api/v1/annonces/2


**Étape 4 — Test via Swagger (40 min)**
1. Ouvrir `http://localhost:8000/docs`
2. Tester chaque route via l'interface interactive
3. Vérifier les codes HTTP retournés (200, 404, etc.)
4. Tester les filtres de la liste

### ✅ Critères de validation
- [X] L'API démarre sans erreur
- [X] `/docs` affiche toutes les routes documentées
- [X] Un 404 est retourné pour un ID inexistant
- [X] Les filtres fonctionnent sur `/annonces`
- [ ] Un `POST` sur `/annonces` ajoute bien l'annonce à la liste

---

---

# MODULE 3 — Modélisation des données avec Pydantic
> ⏱ 2h Cours + 2h TP

## 3.1 Qu'est-ce que Pydantic ?

Pydantic est une bibliothèque de **validation et de sérialisation de données** basée sur les type hints Python. FastAPI l'utilise en interne pour tout : validation des entrées, sérialisation des sorties, documentation automatique.

```python
# Sans Pydantic — validation manuelle et fragile
def create_annonce(data: dict):
    if "titre" not in data:
        raise ValueError("titre requis")
    if not isinstance(data["prix"], (int, float)):
        raise ValueError("prix doit être un nombre")
    if data["prix"] < 0:
        raise ValueError("prix doit être positif")
    # ... etc

# Avec Pydantic — déclaratif, lisible, automatique
from pydantic import BaseModel, Field, validator

class AnnonceCreate(BaseModel):
    titre: str
    prix: float = Field(gt=0)
    # Pydantic gère tout le reste !
```

## 3.2 Schémas Pydantic — le cœur de FastAPI

### `app/schemas/annonce.py`

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enum pour les catégories d'annonces
class CategorieAnnonce(str, Enum):
    ALIMENTAIRE = "alimentaire"
    SERVICES = "services"
    LOISIRS = "loisirs"
    IMMOBILIER = "immobilier"
    VEHICULES = "vehicules"
    AUTRE = "autre"

# Schéma de BASE — champs communs
class AnnonceBase(BaseModel):
    titre: str = Field(
        ...,
        min_length=5,
        max_length=100,
        description="Titre de l'annonce",
        example="Vente de mangues Julie bio"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Description détaillée"
    )
    prix: float = Field(
        ...,
        gt=0,
        description="Prix en euros, doit être positif",
        example=3.50
    )
    commune: str = Field(
        ...,
        description="Commune en Martinique ou Guadeloupe",
        example="Le Lamentin"
    )
    categorie: CategorieAnnonce = CategorieAnnonce.AUTRE

    # Validateur personnalisé
    @validator("titre")
    def titre_ne_peut_pas_etre_vide(cls, v):
        if v.strip() == "":
            raise ValueError("Le titre ne peut pas être vide ou il ne peux pas avoir non plus que des espaces")
        return v.strip()  # On nettoie les espaces en bord

# Schéma pour la CRÉATION (entrée)
class AnnonceCreate(AnnonceBase):
    pass  # Hérite tout de AnnonceBase, rien de plus pour l'instant

# Schéma pour la MISE À JOUR partielle (PATCH)
class AnnonceUpdate(BaseModel):
    titre: Optional[str] = Field(None, min_length=5, max_length=100)
    description: Optional[str] = None
    prix: Optional[float] = Field(None, gt=0)
    commune: Optional[str] = None
    categorie: Optional[CategorieAnnonce] = None
    # Tous les champs sont optionnels pour le PATCH

# Schéma pour la RÉPONSE (sortie) — inclut les champs serveur
class AnnonceResponse(AnnonceBase):
    id: int
    actif: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Permet la conversion depuis un objet SQLAlchemy
```

## 3.3 Utilisation des schémas dans les routes

```python
# app/routers/annonces.py
from fastapi import APIRouter, HTTPException, status
from app.schemas.annonce import AnnonceCreate, AnnonceUpdate, AnnonceResponse
from typing import List
from datetime import datetime

router = APIRouter()

# Base de données simulée
annonces_db = []
compteur_id = 1

@router.post(
    "/annonces",
    response_model=AnnonceResponse,         # Schéma de réponse
    status_code=status.HTTP_201_CREATED,    # Code de statut par défaut
    summary="Créer une nouvelle annonce"
)
def create_annonce(annonce: AnnonceCreate):
    """
    Crée une nouvelle annonce dans KaribMarket.

    - **titre** : Entre 5 et 100 caractères
    - **prix** : Doit être positif (> 0)
    - **commune** : Commune de Martinique ou Guadeloupe
    - **categorie** : alimentaire, services, loisirs, immobilier, vehicules, autre
    """
    global compteur_id

    nouvelle_annonce = {
        "id": compteur_id,
        **annonce.model_dump(),     # Convertit le schéma Pydantic en dict
        "actif": True,
        "created_at": datetime.now(),
        "updated_at": None
    }

    annonces_db.append(nouvelle_annonce)
    compteur_id += 1

    return nouvelle_annonce

@router.patch(
    "/annonces/{annonce_id}",
    response_model=AnnonceResponse,
    summary="Modifier partiellement une annonce"
)
def update_annonce(annonce_id: int, modifications: AnnonceUpdate):
    for i, annonce in enumerate(annonces_db):
        if annonce["id"] == annonce_id:
            # model_dump(exclude_unset=True) → seulement les champs fournis
            changements = modifications.model_dump(exclude_unset=True)
            annonces_db[i].update(changements)
            annonces_db[i]["updated_at"] = datetime.now()
            return annonces_db[i]

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Annonce {annonce_id} introuvable"
    )
```

## 3.4 Schémas imbriqués et relations

```python
# app/schemas/utilisateur.py
from pydantic import BaseModel, EmailStr, Field
from typing import List
from app.schemas.annonce import AnnonceResponse

class UtilisateurBase(BaseModel):
    nom: str = Field(..., min_length=2, max_length=50)
    email: EmailStr  # Validation email automatique (pip install email-validator)
    telephone: Optional[str] = Field(None, pattern=r"^\+596\d{9}$")  # Format Martinique

class UtilisateurCreate(UtilisateurBase):
    mot_de_passe: str = Field(..., min_length=8)

class UtilisateurResponse(UtilisateurBase):
    id: int
    actif: bool
    # Relation : liste des annonces de cet utilisateur
    annonces: List[AnnonceResponse] = []

    class Config:
        from_attributes = True
```

---

## 🔧 TP 2 — Pydantic & Validation (2h)

### Objectif
Remplacer les dicts bruts de votre TP1 par des schémas Pydantic robustes.

### Étapes

**Étape 1 — Créer les schémas (45 min)**

Dans `app/schemas/`, créer les fichiers :
- `annonce.py` : `AnnonceBase`, `AnnonceCreate`, `AnnonceUpdate`, `AnnonceResponse`
- `utilisateur.py` : `UtilisateurBase`, `UtilisateurCreate`, `UtilisateurResponse`

**Étape 2 — Mettre à jour les routes (30 min)**

Modifier `app/routers/annonces.py` pour utiliser :
- `AnnonceCreate` comme body de POST
- `AnnonceUpdate` comme body de PATCH
- `AnnonceResponse` comme `response_model` sur toutes les routes

**Étape 3 — Tester la validation (30 min)**

Via Swagger (`/docs`), tester que l'API rejette :
- Un titre vide ou trop court
- Un prix négatif
- Une catégorie inexistante
- Un email invalide

**Étape 4 — Réponses d'erreur personnalisées (15 min)**

```python
# Dans main.py — personnaliser les messages d'erreur de validation
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    erreurs = []
    for error in exc.errors():
        erreurs.append({
            "champ": " → ".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "valeur_recue": error.get("input")
        })
    return JSONResponse(
        status_code=422,
        content={"success": False, "erreurs": erreurs}
    )
```

### ✅ Critères de validation
- [X] Un POST avec données invalides retourne un 422 clair
- [X] Les `response_model` masquent le mot de passe dans les réponses utilisateur
- [X] `PATCH /annonces/{id}` ne modifie que les champs fournis
- [X] La documentation Swagger affiche les exemples définis dans les schémas

---

---

# MODULE 4 — Base de données avec SQLAlchemy & Alembic
> ⏱ 3h Cours + 3h TP

## 4.1 SQLAlchemy — ORM pour Python

SQLAlchemy est l'ORM (Object Relational Mapper) de référence en Python. Il traduit vos classes Python en tables SQL.

```bash
pip install sqlalchemy psycopg2-binary alembic python-dotenv
```

## 4.2 Configuration de la base de données

### `app/config.py`

```python
from pydantic_settings import BaseSettings  # pip install pydantic-settings

class Settings(BaseSettings):
    # Base de données
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/karibmarket"

    # JWT (Module 5)
    SECRET_KEY: str = "changez-moi-en-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"  # Lire depuis le fichier .env

settings = Settings()
```

### `.env` (ne jamais committer en production !)

```
DATABASE_URL=postgresql://karib:karib_pass@localhost:5432/karibmarket
SECRET_KEY=une-cle-secrete-tres-longue-et-aleatoire
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```
Créer la base de données
Créer l'utilisateur et la base PostgreSQL (si pas encore fait) :

  psql postgres
  CREATE USER karib WITH PASSWORD 'karib_pass';
  CREATE DATABASE karibmarket OWNER karib;
  \q

  Ensuite relancez uvicorn app.main:app --reload.

### `app/database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Création du moteur de connexion
engine = create_engine(settings.DATABASE_URL)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe de base pour tous les modèles
Base = declarative_base()

# Dépendance FastAPI — injecte une session dans chaque requête
def get_db():
    db = SessionLocal()
    try:
        yield db  # Fournit la session
    finally:
        db.close()  # Ferme TOUJOURS la session après la requête
```

## 4.3 Modèles SQLAlchemy

### `app/models/utilisateur.py`

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    telephone = Column(String(20), nullable=True)
    hashed_password = Column(String(255), nullable=False)  # Jamais stocker le mdp en clair !
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relation : un utilisateur a plusieurs annonces
    annonces = relationship("Annonce", back_populates="proprietaire")
```

### `app/models/annonce.py`

```python
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class CategorieEnum(enum.Enum):
    alimentaire = "alimentaire"
    services = "services"
    loisirs = "loisirs"
    immobilier = "immobilier"
    vehicules = "vehicules"
    autre = "autre"

class Annonce(Base):
    __tablename__ = "annonces"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    prix = Column(Float, nullable=False)
    commune = Column(String(50), nullable=False)
    categorie = Column(SAEnum(CategorieEnum), default=CategorieEnum.autre)
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Clé étrangère vers l'utilisateur propriétaire
    proprietaire_id = Column(Integer, ForeignKey("utilisateurs.id"))
    proprietaire = relationship("Utilisateur", back_populates="annonces")
```

## 4.4 Routes avec la base de données réelle

```python
# app/routers/annonces.py — version avec SQLAlchemy
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.annonce import Annonce
from app.schemas.annonce import AnnonceCreate, AnnonceUpdate, AnnonceResponse

router = APIRouter()

@router.get("/annonces", response_model=List[AnnonceResponse])
def list_annonces(
    commune: Optional[str] = Query(None),
    categorie: Optional[str] = Query(None),
    page: int = Query(1, gt=0),
    limit: int = Query(10, gt=0, le=100),
    db: Session = Depends(get_db)  # ← Injection de la session
):
    query = db.query(Annonce).filter(Annonce.actif == True)

    if commune:
        query = query.filter(Annonce.commune.ilike(f"%{commune}%"))
    if categorie:
        query = query.filter(Annonce.categorie == categorie)

    total = query.count()
    annonces = query.offset((page - 1) * limit).limit(limit).all()

    return annonces

@router.post("/annonces", response_model=AnnonceResponse, status_code=201)
def create_annonce(
    annonce_data: AnnonceCreate,
    db: Session = Depends(get_db)
):
    nouvelle_annonce = Annonce(**annonce_data.model_dump())
    db.add(nouvelle_annonce)
    db.commit()           # Sauvegarder en base
    db.refresh(nouvelle_annonce)  # Récupérer les valeurs générées (id, created_at...)
    return nouvelle_annonce

@router.get("/annonces/{annonce_id}", response_model=AnnonceResponse)
def get_annonce(annonce_id: int, db: Session = Depends(get_db)):
    annonce = db.query(Annonce).filter(Annonce.id == annonce_id).first()
    if not annonce:
        raise HTTPException(status_code=404, detail="Annonce introuvable")
    return annonce

@router.delete("/annonces/{annonce_id}", status_code=204)
def delete_annonce(annonce_id: int, db: Session = Depends(get_db)):
    annonce = db.query(Annonce).filter(Annonce.id == annonce_id).first()
    if not annonce:
        raise HTTPException(status_code=404, detail="Annonce introuvable")
    # Soft delete — on ne supprime pas vraiment de la BDD
    annonce.actif = False
    db.commit()
```

## 4.5 Migrations avec Alembic

```bash
# Initialiser Alembic dans le projet
alembic init migrations

# Éditer migrations/env.py pour pointer vers vos modèles
# Ajouter ces lignes dans env.py :
# from app.database import Base
# from app.models import annonce, utilisateur  # Importer tous les modèles !
# target_metadata = Base.metadata

# Créer une migration automatiquement depuis vos modèles
alembic revision --autogenerate -m "creation tables initiales"

# Appliquer la migration
alembic upgrade head

# Revenir en arrière si nécessaire
alembic downgrade -1

# Voir l'historique des migrations
alembic history
```

---

## 🔧 TP 3 — Base de données réelle (3h)

### Objectif
Connecter KaribMarket API à PostgreSQL et migrer les données simulées vers une vraie base.

### Prérequis
Avoir Docker installé, ou PostgreSQL en local.

```bash
# Lancer PostgreSQL avec Docker (plus simple)
docker run --name karib-postgres \
  -e POSTGRES_USER=karib \
  -e POSTGRES_PASSWORD=karib_pass \
  -e POSTGRES_DB=karibmarket \
  -p 5432:5432 \
  -d postgres:15
```

### Étapes

**Étape 1 — Configuration (30 min)**
1. Créer le fichier `.env` avec la `DATABASE_URL`
2. Créer `app/database.py` avec le moteur SQLAlchemy
3. Vérifier la connexion : `python -c "from app.database import engine; print('Connexion OK')"`

**Étape 2 — Modèles (45 min)**
1. Créer `app/models/utilisateur.py` et `app/models/annonce.py`
2. Initialiser Alembic et configurer `env.py`
3. Créer et appliquer la première migration

**Étape 3 — Routes avec BDD (45 min)**
Mettre à jour toutes les routes pour utiliser `Session = Depends(get_db)`

**Étape 4 — Seeding (30 min)**
```python
# scripts/seed.py — peupler la base avec des données de test
from app.database import SessionLocal
from app.models.annonce import Annonce
from app.models.utilisateur import Utilisateur
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])

def seed():
    db = SessionLocal()
    try:
        # Créer des utilisateurs de test
        users = [
            Utilisateur(
                nom="Marie Dubois",
                email="marie@example.com",
                telephone="+596696123456",
                hashed_password=pwd_context.hash("password123")
            ),
        ]
        db.add_all(users)
        db.commit()

        # Créer des annonces de test
        annonces = [
            Annonce(titre="Vente mangues Julie bio", prix=3.50,
                    commune="Le Lamentin", categorie="alimentaire",
                    proprietaire_id=1),
            Annonce(titre="Cours de yoga face à la mer", prix=25.00,
                    commune="Sainte-Anne", categorie="services",
                    proprietaire_id=1),
        ]
        db.add_all(annonces)
        db.commit()
        print("✅ Base de données initialisée avec succès !")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
```

```bash
python scripts/seed.py
```

### ✅ Critères de validation
- [ ] La migration crée les tables `utilisateurs` et `annonces`
- [ ] `GET /annonces` lit depuis PostgreSQL
- [ ] `POST /annonces` persiste bien en base (vérifier avec un outil comme DBeaver ou psql)
- [ ] Le soft delete (actif=False) masque les annonces dans la liste

---

---

# MODULE 5 — Authentification & Sécurité
> ⏱ 2h Cours + 2h TP

## 5.1 Comprendre JWT (JSON Web Token)

Un JWT est un **token signé** qui prouve l'identité d'un utilisateur sans avoir à interroger la base de données à chaque requête.

```
HEADER.PAYLOAD.SIGNATURE

eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJtYXJpZUBleGFtcGxlLmNvbSIsImV4cCI6MTcwNjcxMjAwMH0.abc123
      ↑                          ↑                                                  ↑
Algorithme de                 Données                                            Signature
  signature                 (claims)                                             HMAC-SHA256
```

**Structure du payload :**
```json
{
  "sub": "marie@example.com",   // Subject — identifiant de l'utilisateur
  "exp": 1706712000,            // Expiration (timestamp Unix)
  "iat": 1706708400,            // Issued at (date d'émission)
  "role": "user"                // Claims personnalisés
}
```

> ⚠️ **Important** : Le JWT n'est pas chiffré, seulement **signé**. Ne jamais y stocker de données sensibles !

## 5.2 Implémentation

```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

### `app/services/auth_service.py`

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

# Contexte de hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(mot_de_passe: str) -> str:
    """Hacher un mot de passe — JAMAIS stocker en clair"""
    return pwd_context.hash(mot_de_passe)

def verify_password(mot_de_passe: str, hashed: str) -> bool:
    """Vérifier qu'un mot de passe correspond au hash stocké"""
    return pwd_context.verify(mot_de_passe, hashed)

def create_access_token(data: dict) -> str:
    """Créer un JWT signé"""
    payload = data.copy()
    expiration = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expiration})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> dict:
    """Décoder et vérifier un JWT"""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
```

### `app/routers/auth.py`

```python
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.utilisateur import Utilisateur
from app.schemas.utilisateur import UtilisateurCreate, UtilisateurResponse
from app.services.auth_service import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentification"])

# Schéma OAuth2 — indique à FastAPI où chercher le token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

@router.post("/register", response_model=UtilisateurResponse, status_code=201)
def register(user_data: UtilisateurCreate, db: Session = Depends(get_db)):
    # Vérifier que l'email n'existe pas déjà
    existant = db.query(Utilisateur).filter(Utilisateur.email == user_data.email).first()
    if existant:
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")

    # Créer l'utilisateur avec le mot de passe haché
    utilisateur = Utilisateur(
        nom=user_data.nom,
        email=user_data.email,
        telephone=user_data.telephone,
        hashed_password=hash_password(user_data.mot_de_passe)
    )
    db.add(utilisateur)
    db.commit()
    db.refresh(utilisateur)
    return utilisateur

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),  # Standard OAuth2 form
    db: Session = Depends(get_db)
):
    # Chercher l'utilisateur
    utilisateur = db.query(Utilisateur).filter(
        Utilisateur.email == form_data.username
    ).first()

    # Vérifier le mot de passe
    if not utilisateur or not verify_password(form_data.password, utilisateur.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Créer et retourner le token
    token = create_access_token({"sub": utilisateur.email, "id": utilisateur.id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "utilisateur": {"id": utilisateur.id, "nom": utilisateur.nom}
    }

# Dépendance réutilisable : récupère l'utilisateur connecté
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Utilisateur:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré"
        )

    utilisateur = db.query(Utilisateur).filter(
        Utilisateur.email == payload.get("sub")
    ).first()

    if not utilisateur or not utilisateur.actif:
        raise HTTPException(status_code=401, detail="Utilisateur introuvable")

    return utilisateur
```

### Protéger des routes

```python
# app/routers/annonces.py — ajouter l'authentification
from app.routers.auth import get_current_user
from app.models.utilisateur import Utilisateur

@router.post("/annonces", response_model=AnnonceResponse, status_code=201)
def create_annonce(
    annonce_data: AnnonceCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)  # ← Requiert une auth
):
    nouvelle_annonce = Annonce(
        **annonce_data.model_dump(),
        proprietaire_id=current_user.id  # Lier l'annonce à l'utilisateur connecté
    )
    db.add(nouvelle_annonce)
    db.commit()
    db.refresh(nouvelle_annonce)
    return nouvelle_annonce

@router.delete("/annonces/{annonce_id}", status_code=204)
def delete_annonce(
    annonce_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    annonce = db.query(Annonce).filter(Annonce.id == annonce_id).first()
    if not annonce:
        raise HTTPException(status_code=404, detail="Annonce introuvable")

    # Vérifier que l'utilisateur est bien le propriétaire
    if annonce.proprietaire_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez supprimer que vos propres annonces"
        )

    annonce.actif = False
    db.commit()
```

---

## 🔧 TP 4 — Authentification JWT (2h)

### Étapes

**Étape 1 — Auth service (30 min)**
Créer `app/services/auth_service.py` avec les fonctions de hachage et JWT.

**Étape 2 — Routes auth (45 min)**
Créer `app/routers/auth.py` avec `/register` et `/login`.
Tester via Swagger : s'inscrire, se connecter, récupérer le token.

**Étape 3 — Protéger les routes (30 min)**
- `POST /annonces` → requiert authentification
- `DELETE /annonces/{id}` → requiert être le propriétaire
- `GET /annonces` et `GET /annonces/{id}` → rester publics

**Étape 4 — Test du flux complet (15 min)**
1. Créer un compte → `/auth/register` [POST /api/v1/auth/register → créer un compte]
2. Se connecter → `/auth/login` → copier le token [POST /api/v1/auth/login → récupérer le token]
3. Dans Swagger, cliquer "Authorize" et coller le token [Cliquer Authorize en haut de Swagger → coller le token]
4. Créer une annonce → `POST /annonces` (doit marcher) [POST /api/v1/annonces → doit fonctionner]
5. Tenter de supprimer l'annonce d'un autre → doit retourner 403 [DELETE /api/v1/annonces/{id} d'un autre user → doit retourner 403]

### ✅ Critères de validation
- [X] Impossible de créer une annonce sans token → 401
- [X] Impossible de supprimer l'annonce d'autrui → 403
- [X] Un token expiré retourne 401
- [X] Le mot de passe n'apparaît jamais dans une réponse API

---

---

# MODULE 6 — Programmation Asynchrone & Performance
> ⏱ 2h Cours + 2h TP

## 6.1 Async/Await en Python

FastAPI supporte nativement la **programmation asynchrone** avec `async/await`. Comprendre quand et pourquoi l'utiliser est essentiel.

```python
# ❌ Synchrone — bloque pendant l'attente
def get_annonce_sync(annonce_id: int):
    time.sleep(1)  # Simule une requête BDD lente
    return {"id": annonce_id}  # Le serveur est bloqué pendant 1 seconde !

# ✅ Asynchrone — libère le thread pendant l'attente
async def get_annonce_async(annonce_id: int):
    await asyncio.sleep(1)  # Cède le contrôle pendant 1 seconde
    return {"id": annonce_id}  # D'autres requêtes peuvent être traitées entre-temps
```

**Analogie :** Imaginez un serveur de restaurant. En mode synchrone, il attend que chaque plat soit prêt avant de prendre une nouvelle commande. En mode async, il prend toutes les commandes, les transmet en cuisine, et sert au fur et à mesure.

## 6.2 Quand utiliser async ?

```python
# ✅ Utiliser async pour : I/O (réseau, BDD, fichiers)
@router.get("/annonces/{id}")
async def get_annonce(id: int):
    # Requête vers un service externe
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api-externe.com/annonces/{id}")
    return response.json()

# ✅ Opérations BDD avec asyncpg (async)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

# Pour SQLAlchemy synchrone (notre cas avec psycopg2) → pas besoin de async
# FastAPI gère ça automatiquement avec les threads
@router.get("/annonces")
def list_annonces(db: Session = Depends(get_db)):  # sync est OK ici
    return db.query(Annonce).all()
```

## 6.3 Tâches en arrière-plan (Background Tasks)

```python
from fastapi import BackgroundTasks
import smtplib
from email.mime.text import MIMEText

def envoyer_email_confirmation(email: str, titre_annonce: str):
    """Tâche qui s'exécute après avoir répondu au client"""
    print(f"📧 Envoi email de confirmation à {email} pour '{titre_annonce}'")
    # Logique d'envoi d'email ici (simulée)
    # En production : utiliser une bibliothèque comme fastapi-mail

def notifier_moderateurs(annonce_id: int):
    """Notifier les modérateurs d'une nouvelle annonce à valider"""
    print(f"🔔 Nouvelle annonce #{annonce_id} à modérer")

@router.post("/annonces", response_model=AnnonceResponse, status_code=201)
async def create_annonce(
    annonce_data: AnnonceCreate,
    background_tasks: BackgroundTasks,  # ← Injecté automatiquement
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    # Créer l'annonce
    nouvelle_annonce = Annonce(**annonce_data.model_dump(), proprietaire_id=current_user.id)
    db.add(nouvelle_annonce)
    db.commit()
    db.refresh(nouvelle_annonce)

    # Planifier des tâches qui s'exécutent APRÈS la réponse
    # L'utilisateur n'attend pas ces tâches !
    background_tasks.add_task(envoyer_email_confirmation, current_user.email, annonce_data.titre)
    background_tasks.add_task(notifier_moderateurs, nouvelle_annonce.id)

    return nouvelle_annonce  # Réponse immédiate — pas d'attente
```

## 6.4 Cache avec Redis

```bash
pip install redis fastapi-cache2
```

```python
# app/main.py — configurer le cache Redis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
import redis.asyncio as redis

@app.on_event("startup")
async def startup():
    redis_client = redis.from_url("redis://localhost:6379")
    FastAPICache.init(RedisBackend(redis_client), prefix="karibmarket-cache")

# Mettre en cache la liste des annonces (expire après 60 secondes)
@router.get("/annonces")
@cache(expire=60)  # ← Cette réponse est mise en cache 60 secondes
async def list_annonces(db: Session = Depends(get_db)):
    return db.query(Annonce).filter(Annonce.actif == True).all()
```

---

# MODULE 7 — Containerisation Docker
> ⏱ 2h Cours + 2h TP

## 7.1 Dockerfile pour FastAPI

### `Dockerfile`

```dockerfile
# Image de base Python légère
FROM python:3.11-slim

# Dossier de travail dans le conteneur
WORKDIR /app

# Copier et installer les dépendances EN PREMIER (optimise le cache Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . .

# Exposer le port
EXPOSE 8000

# Commande de démarrage
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### `.dockerignore`

```
venv/
__pycache__/
*.pyc
*.pyo
.env
.git
tests/
```

## 7.2 Docker Compose — Orchestration complète

### `docker-compose.yml`

```yaml
version: '3.9'

services:
  # L'API FastAPI
  api:
    build: .
    container_name: karibmarket-api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://karib:karib_pass@postgres:5432/karibmarket
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - .:/app  # Hot reload en développement
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    depends_on:
      postgres:
        condition: service_healthy  # Attendre que Postgres soit prêt
    networks:
      - karib-network

  # Base de données PostgreSQL
  postgres:
    image: postgres:15-alpine
    container_name: karibmarket-postgres
    environment:
      POSTGRES_USER: karib
      POSTGRES_PASSWORD: karib_pass
      POSTGRES_DB: karibmarket
    volumes:
      - postgres_data:/var/lib/postgresql/data  # Persistence des données
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U karib -d karibmarket"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - karib-network

  # Cache Redis
  redis:
    image: redis:7-alpine
    container_name: karibmarket-redis
    ports:
      - "6379:6379"
    networks:
      - karib-network

volumes:
  postgres_data:

networks:
  karib-network:
    driver: bridge
```

### Makefile pour simplifier les commandes

```makefile
# Makefile
.PHONY: start stop logs migrate seed

start:
	docker-compose up -d
	@echo "✅ KaribMarket API démarrée sur http://localhost:8000/docs"

stop:
	docker-compose down

logs:
	docker-compose logs -f api

migrate:
	docker-compose exec api alembic upgrade head
	@echo "✅ Migrations appliquées"

seed:
	docker-compose exec api python scripts/seed.py
	@echo "✅ Base de données initialisée"

shell:
	docker-compose exec api bash

build:
	docker-compose build --no-cache
```

```bash
make start    # Démarrer tout
make migrate  # Appliquer les migrations
make seed     # Peupler la base
make logs     # Voir les logs en temps réel
```

---

## 🔧 TP 5 — Dockerisation (2h)

### Étapes

**Étape 1 — Dockerfile (30 min)**
1. Créer le `Dockerfile` dans la racine du projet
2. Créer `.dockerignore`
3. Builder et tester l'image : `docker build -t karibmarket-api .`
4. Lancer le conteneur : `docker run -p 8000:8000 karibmarket-api`

**Étape 2 — Docker Compose (45 min)**
1. Créer `docker-compose.yml` avec les 3 services (api, postgres, redis)
2. `make start` → vérifier que tout démarre
3. `make migrate` → appliquer les migrations
4. `make seed` → peupler la base

**Étape 3 — Variables d'environnement (30 min)**
1. Créer `.env.example` (template sans les vraies valeurs → à committer)
2. Créer `.env` avec les vraies valeurs (à ajouter dans `.gitignore`)
3. Vérifier que l'API lit bien les variables depuis `.env`

**Étape 4 — Makefile (15 min)**
Créer le Makefile et vérifier que `make start`, `make logs`, `make migrate` fonctionnent.

### ✅ Critères de validation
- [ ] `make start` lance tout en une commande
- [ ] L'API, Postgres et Redis communiquent entre eux
- [ ] Les données persistent après `docker-compose down && docker-compose up`
- [ ] Les logs API sont accessibles via `make logs`

---

---

# MODULE 8 — Tests & Bonnes Pratiques
> ⏱ 1h Cours + 1h TP

## 8.1 Tests avec pytest

```bash
pip install pytest pytest-asyncio httpx
```

### `tests/test_annonces.py`

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

# Base de données de test séparée (SQLite en mémoire — rapide !)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)

# Override de la dépendance pour les tests
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Créer les tables de test
Base.metadata.create_all(bind=engine)

client = TestClient(app)

# --- Tests ---

def test_api_est_accessible():
    response = client.get("/")
    assert response.status_code == 200
    assert "KaribMarket" in response.json()["message"]

def test_liste_annonces_vide_au_depart():
    response = client.get("/api/v1/annonces")
    assert response.status_code == 200
    assert response.json() == []

def test_creer_annonce_sans_auth_retourne_401():
    response = client.post("/api/v1/annonces", json={
        "titre": "Test annonce",
        "prix": 10.0,
        "commune": "Fort-de-France"
    })
    assert response.status_code == 401

def test_flux_complet_inscription_connexion_annonce():
    # 1. S'inscrire
    register_resp = client.post("/api/v1/auth/register", json={
        "nom": "Test User",
        "email": "test@test.com",
        "mot_de_passe": "password123"
    })
    assert register_resp.status_code == 201

    # 2. Se connecter
    login_resp = client.post("/api/v1/auth/login", data={
        "username": "test@test.com",
        "password": "password123"
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    # 3. Créer une annonce avec le token
    create_resp = client.post(
        "/api/v1/annonces",
        json={"titre": "Mangues bio", "prix": 3.50, "commune": "Le Lamentin", "categorie": "alimentaire"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_resp.status_code == 201
    annonce = create_resp.json()
    assert annonce["titre"] == "Mangues bio"
    assert annonce["prix"] == 3.50

def test_annonce_introuvable_retourne_404():
    response = client.get("/api/v1/annonces/99999")
    assert response.status_code == 404
```

```bash
# Lancer les tests
pytest tests/ -v

# Avec couverture de code
pip install pytest-cov
pytest tests/ -v --cov=app --cov-report=html
```

---

---

# MODULE 9 — Projet Final
> ⏱ Rendu + 2h Soutenance

## Description du projet

**Par groupes de 2-3 étudiants**, développer une API REST complète sur un thème librement choisi dans le contexte caribéen.

### Thèmes suggérés

| Thème | Description |
|-------|-------------|
| 🌴 **TiTourisme** | API d'activités et hébergements touristiques en Martinique/Guadeloupe |
| 🎵 **KaribEvent** | API de gestion d'événements culturels et concerts |
| 🌿 **Marché Kréyol** | API de produits du terroir, producteurs locaux, recettes |
| 🏖️ **DébatjéNou** | API de covoiturage local avec trajet et conducteurs |
| 📚 **BiblioUA** | API de bibliothèque universitaire avec prêts et réservations |

## Livrables attendus

```
nom-groupe-projet/
├── README.md              ← Instructions de démarrage OBLIGATOIRES
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example           ← Template sans les vraies valeurs
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   └── services/
├── migrations/
├── tests/
└── scripts/
    └── seed.py
```

### `README.md` obligatoire

```markdown
# Nom du Projet API

## Description
[Courte description du projet]

## Démarrage rapide
\`\`\`bash
git clone <url>
cd <projet>
cp .env.example .env
make start
make migrate
make seed
\`\`\`
L'API est accessible sur : http://localhost:8000/docs

## Endpoints principaux
| Méthode | Route | Auth | Description |
...

## Équipe
- Prénom NOM
- Prénom NOM
```

---

---

# 📎 Annexes

## A — Commandes essentielles

```bash
# Environnement virtuel
python -m venv venv && source venv/bin/activate

# Dépendances
pip install -r requirements.txt
pip freeze > requirements.txt

# Démarrage développement
uvicorn app.main:app --reload --port 8000

# Migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1

# Tests
pytest tests/ -v
pytest tests/ --cov=app

# Docker
docker-compose up -d
docker-compose down
docker-compose logs -f api
docker-compose exec api bash
```

## B — Ressources

| Ressource | URL |
|-----------|-----|
| Documentation FastAPI | https://fastapi.tiangolo.com |
| Documentation Pydantic | https://docs.pydantic.dev |
| Documentation SQLAlchemy | https://docs.sqlalchemy.org |
| Documentation Alembic | https://alembic.sqlalchemy.org |
| JWT expliqué | https://jwt.io |
| Docker Compose | https://docs.docker.com/compose |

## C — Checklist de déploiement

Avant de soumettre votre projet :

```
Architecture
☐ Structure de dossiers propre (models/, schemas/, routers/, services/)
☐ Pas de logique dans les routes (séparation route/service)

Base de données
☐ Migrations Alembic créées et appliquées
☐ Script de seed disponible
☐ .env.example documenté

Sécurité
☐ Mots de passe hachés avec bcrypt
☐ JWT avec expiration
☐ Routes protégées de manière cohérente
☐ Variables sensibles dans .env (jamais hardcodées)

Docker
☐ docker-compose up -d fonctionne sans erreur
☐ L'API redémarre correctement si la BDD est lente à démarrer

Documentation
☐ Tous les endpoints ont un summary et description
☐ Les schémas Pydantic ont des examples
☐ README avec instructions claires

Tests
☐ Au moins 5 tests couvrant les cas principaux
☐ Tests passent avec pytest
```

---

> 📬 **Contact & questions** : Posez vos questions pendant les séances de TP ou créez une issue sur le dépôt GitHub du cours.  
> *Bonne construction d'API ! *
