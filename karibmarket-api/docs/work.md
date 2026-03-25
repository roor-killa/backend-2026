  
=== 
Lancer le projet 
Depuis le dossier karibmarket-api/ :                                                                                                                             
  # 1. Activer l'environnement virtuel                                                                                                                     
  source .venv/bin/activate                                                                                                                                                                                    
  # 2. Installer les dépendances (si pas encore fait)                                                                                                      
  pip install -r requirements.txt                                                                                                                          
                  
  # 3. Lancer le serveur
  uvicorn app.main:app --reload

  L'API sera disponible sur :
  - http://localhost:8000/docs — Swagger UI
  - http://localhost:8000/redoc — ReDoc


  === 
Structureajoutée                                                                                                                                        
   
  app/                                                                                                                                                     
  ├── database.py          # NOUVEAU — moteur, session, Base, get_db()                                                                                   
  ├── models/                                                                                                                                            
  │   ├── __init__.py      # NOUVEAU
  │   └── annonce.py       # NOUVEAU — modèle ORM (table SQL)
  ├── config.py            # MàJ — ajout import pydantic_settings
  ├── main.py              # MàJ — création des tables au démarrage
  └── routers/
      └── annonces.py      # MàJ — toutes les routes utilisent la vraie DB

  ---
  Concepts clés

  database.py
  - create_engine() — connexion à PostgreSQL via DATABASE_URL
  - SessionLocal — fabrique de sessions (1 session = 1 requête HTTP)
  - get_db() — dépendance FastAPI (pattern yield = garantit la fermeture)

  models/annonce.py
  - Hérite de Base (SQLAlchemy ORM)
  - Chaque attribut = une colonne SQL
  - server_default=func.now() = valeur par défaut côté PostgreSQL

  routers/annonces.py
  - db: Session = Depends(get_db) — injection de la session DB
  - db.add() / db.commit() / db.refresh() — cycle de vie d'un objet
  - db.query(Annonce).filter(...).offset(...).limit(...) — requêtes filtrées

Erreur lors du lancement univcorn
  Le .env est vide. De plus, il est dans app/ alors que pydantic-settings le cherche à la racine du projet (karibmarket-api/).                           
                                                                                                                                                           
  Deux choses à faire :                                                                                                           
                                                                                                                                                           
  1. Déplacer/créer le .env au bon endroit (karibmarket-api/.env) :                                                                                        
                                                                                                                                                           
  cat > .env << 'EOF'                                                                                                                                      
  DATABASE_URL=postgresql://karib:karib_pass@localhost:5432/karibmarket
  SECRET_KEY=une-cle-secrete-tres-longue-et-aleatoire
  ALGORITHM=HS256
  ACCESS_TOKEN_EXPIRE_MINUTES=30
  EOF

  2. Créer l'utilisateur et la base PostgreSQL (si pas encore fait) :

  psql postgres
  CREATE USER karib WITH PASSWORD 'karib_pass';
  CREATE DATABASE karibmarket OWNER karib;
  \q

  Ensuite relancez uvicorn app.main:app --reload.

                    Etape                   │ Status │
  ├───────────────────────────────────────────┼────────┤
  │ Docker PostgreSQL sur port 5433           │ ✅     │
  ├───────────────────────────────────────────┼────────┤
  │ .env créé à la racine                     │ ✅     │
  ├───────────────────────────────────────────┼────────┤
  │ app/models/utilisateur.py                 │ ✅     │
  ├───────────────────────────────────────────┼────────┤
  │ app/models/annonce.py (+ proprietaire_id) │ ✅     │
  ├───────────────────────────────────────────┼────────┤
  │ Alembic configuré + migration appliquée   │ ✅     │
  ├───────────────────────────────────────────┼────────┤
  │ scripts/seed.py — 2 users + 3 annonces    │ ✅     │
  └───────────────────────────────────────────┴────────┘

  Commandes utiles

  # Lancer l'API
  uvicorn app.main:app --reload

  # Nouvelle migration (après modif des modèles)
  alembic revision --autogenerate -m "description"
  alembic upgrade head

  # Repeupler la base
  python scripts/seed.py

  Le port PostgreSQL est 5433 (5432 était déjà occupé sur votre machine).


✻ Crunched for 1m 50s

❯ comment visualiser les éléments de la base de données dans VS Code. Quel est le username et le passe de la base                                          
  ⎿  ⧉ Selected 1 lines from .env in Visual Studio Code

⏺ Les identifiants sont dans votre .env :

  ┌──────────┬─────────────┐
  │  Champ   │   Valeur    │
  ├──────────┼─────────────┤
  │ Host     │ localhost   │
  ├──────────┼─────────────┤
  │ Port     │ 5433        │
  ├──────────┼─────────────┤
  │ Database │ karibmarket │
  ├──────────┼─────────────┤
  │ Username │ karib       │
  ├──────────┼─────────────┤
  │ Password │ karib_pass  │
  └──────────┴─────────────┘

  