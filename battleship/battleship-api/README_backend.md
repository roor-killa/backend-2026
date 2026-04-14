# 🚢 Bataille Navale 3D — Backend (FastAPI)

> API REST du jeu Bataille Navale 3D — Développé avec FastAPI (Python 3.11+)

**Responsable : Ibrahim Guindo** *(Backend + BDD + Tests)*

---

## 📋 Prérequis

- Python 3.11+
- pip
- Git

---

## ⚙️ Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/votre-groupe/battleship-api.git
cd battleship-api

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate        # Linux / Mac
venv\Scripts\activate           # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Copier le fichier d'environnement
cp .env.example .env
```

---

## 🔧 Variables d'environnement

Modifier le fichier `.env` :

```env
DATABASE_URL=sqlite:///./battleship.db
# DATABASE_URL=postgresql://user:password@host:5432/battleship

SECRET_KEY=votre_cle_secrete
DEBUG=True
ALLOWED_ORIGINS=http://localhost:3000
```

---

## 🚀 Lancement

```bash
uvicorn app.main:app --reload --port 8000
```

- **API** → http://localhost:8000
- **Swagger** → http://localhost:8000/docs
- **ReDoc** → http://localhost:8000/redoc

---

## 🧪 Tests

```bash
pytest
pytest --cov=app tests/
pytest tests/test_games.py -v
```

---

## 📁 Structure du projet

```
battleship-api/
├── app/
│   ├── main.py              # Point d'entrée FastAPI + CORS
│   ├── database.py          # Config SQLAlchemy
│   ├── models/              # Modèles SQLAlchemy
│   │   ├── player.py
│   │   ├── game.py
│   │   ├── board.py
│   │   ├── ship.py
│   │   └── shot.py
│   ├── schemas/             # Schémas Pydantic
│   │   ├── player.py
│   │   ├── game.py
│   │   └── shot.py
│   ├── routers/             # Endpoints REST
│   │   ├── players.py
│   │   ├── games.py
│   │   └── shots.py
│   ├── services/            # Logique métier
│   │   ├── game_service.py
│   │   └── ai_service.py    # IA : facile / moyen / difficile
│   └── core/
│       └── constants.py     # Grille, bateaux, constantes
├── tests/
│   ├── conftest.py
│   ├── test_players.py
│   ├── test_games.py
│   └── test_ai.py
├── .env.example
├── requirements.txt
└── README.md
```

---

## 🌐 Endpoints

| Méthode | Endpoint | Description |
|---|---|---|
| `POST` | `/players` | Créer un joueur |
| `GET` | `/players/{id}` | Profil joueur |
| `GET` | `/players/leaderboard` | Classement |
| `POST` | `/games` | Créer une partie |
| `POST` | `/games/{id}/join` | Rejoindre (multijoueur) |
| `POST` | `/games/{id}/place-ships` | Placer les bateaux |
| `GET` | `/games/{id}` | État de la partie |
| `GET` | `/games/{id}/board` | Grilles |
| `POST` | `/games/{id}/shoot` | Tirer |
| `GET` | `/games/{id}/shots` | Historique tirs |

---

## ☁️ Déploiement Railway

```bash
npm install -g @railway/cli
railway login
railway init
railway add postgresql
railway up
```

Variables Railway à configurer :
- `DATABASE_URL` → fourni automatiquement
- `SECRET_KEY`
- `ALLOWED_ORIGINS` → https://battleship-front.vercel.app
- `DEBUG` → False

---

*Université des Antilles — L2 Informatique — 2026*
