# 🗂️ Architecture complète — Bataille Navale 3D

> Document de référence pour la répartition des fichiers entre les membres du groupe.

---

## 👥 Répartition finale

```
Ibrahim Guindo  →  Backend complet (FastAPI + BDD + Tests + IA)
Mohand Sadi     →  Frontend (Next.js — pages, composants, appels API)
Junior Akonou   →  3D (Unity WebGL + JS Bridge) + Déploiement Vercel
```

---

## 🔵 Ibrahim Guindo — Backend + BDD + Tests

### Dépôt : `battleship-api/`

| Fichier | Rôle | Action |
|---|---|---|
| `app/main.py` | Point d'entrée FastAPI + CORS | Créer |
| `app/database.py` | Config SQLAlchemy, engine, session | Créer |
| `app/models/__init__.py` | Init module models | Créer |
| `app/models/player.py` | Modèle SQLAlchemy Player | Créer |
| `app/models/game.py` | Modèle SQLAlchemy Game | Créer |
| `app/models/board.py` | Modèle SQLAlchemy Board | Créer |
| `app/models/ship.py` | Modèle SQLAlchemy Ship | Créer |
| `app/models/shot.py` | Modèle SQLAlchemy Shot | Créer |
| `app/schemas/__init__.py` | Init module schemas | Créer |
| `app/schemas/player.py` | Schémas Pydantic joueur | Créer |
| `app/schemas/game.py` | Schémas Pydantic partie | Créer |
| `app/schemas/shot.py` | Schémas Pydantic tir | Créer |
| `app/routers/__init__.py` | Init module routers | Créer |
| `app/routers/players.py` | Endpoints `/players` | Créer |
| `app/routers/games.py` | Endpoints `/games` | Créer |
| `app/routers/shots.py` | Endpoints `/games/{id}/shoot` | Créer |
| `app/services/__init__.py` | Init module services | Créer |
| `app/services/game_service.py` | Logique placement, tirs, victoire | Créer |
| `app/services/ai_service.py` | IA solo (facile / moyen / difficile) | Créer |
| `app/core/__init__.py` | Init module core | Créer |
| `app/core/constants.py` | Grille, bateaux, constantes | Créer |
| `tests/__init__.py` | Init module tests | Créer |
| `tests/conftest.py` | Fixtures Pytest (client test, BDD test) | Créer |
| `tests/test_players.py` | Tests endpoints joueurs | Créer |
| `tests/test_games.py` | Tests endpoints parties | Créer |
| `tests/test_ai.py` | Tests logique IA (3 niveaux) | Créer |
| `.env.example` | Template variables d'environnement | Créer |
| `requirements.txt` | Dépendances Python | Créer |
| `README.md` | Documentation backend | Créer |

### Endpoints à implémenter

```python
# routers/players.py
POST   /players                  → créer un joueur
GET    /players/{id}             → profil joueur
GET    /players/leaderboard      → classement

# routers/games.py
POST   /games                    → créer une partie (mode + difficulté)
POST   /games/{id}/join          → rejoindre (multijoueur)
POST   /games/{id}/place-ships   → placer les bateaux
GET    /games/{id}               → état complet
GET    /games/{id}/board         → grilles des deux joueurs

# routers/shots.py
POST   /games/{id}/shoot         → tirer sur une case
GET    /games/{id}/shots         → historique des tirs
```

### Modèles SQLAlchemy

```python
Player  →  id, pseudo, score, games_played, created_at
Game    →  id, mode, difficulty, status, current_turn, winner_id, created_at
Board   →  id, game_id, player_id, grid (JSON)
Ship    →  id, board_id, type, positions (JSON), is_sunk
Shot    →  id, game_id, player_id, row, col, result, created_at
```

### IA à implémenter dans `ai_service.py`

```
Facile    → tir aléatoire sur cases non jouées
Moyen     → après touché, cible cases adjacentes (haut/bas/gauche/droite)
Difficile → carte de probabilités : calcule pour chaque case vide la
            probabilité qu'un bateau s'y trouve, tire sur la case max
```

---

## 🟡 Mohand Sadi — Frontend (Next.js)

### Dépôt : `battleship-front/`

| Fichier | Rôle | Action |
|---|---|---|
| `app/layout.tsx` | Layout global (police, metadata, fond) | Créer |
| `app/page.tsx` | Page d'accueil — choix solo/multijoueur | Créer |
| `app/game/[id]/page.tsx` | Page de jeu — grille 3D + interface tirs | Créer |
| `app/leaderboard/page.tsx` | Page classement des joueurs | Créer |
| `components/ModeSelector.tsx` | Sélection mode solo / multijoueur | Créer |
| `components/DifficultySelector.tsx` | Sélection niveau IA (facile/moyen/difficile) | Créer |
| `components/ShipPlacer.tsx` | Interface placement des bateaux | Créer |
| `components/ShotResult.tsx` | Affichage résultat tir (touché/coulé/eau) | Créer |
| `components/Leaderboard.tsx` | Tableau classement | Créer |
| `lib/api.ts` | Toutes les fonctions d'appel API FastAPI | Créer |
| `.env.example` | Template variables d'environnement | Créer |
| `package.json` | Dépendances Node.js | Créer |
| `README.md` | Documentation frontend | Créer |

### Fonctions API à implémenter dans `lib/api.ts`

```typescript
createPlayer(pseudo)              → POST /players
getPlayer(id)                     → GET  /players/{id}
getLeaderboard()                  → GET  /players/leaderboard
createGame(mode, difficulty?)     → POST /games
joinGame(id)                      → POST /games/{id}/join
placeShips(id, ships)             → POST /games/{id}/place-ships
getGame(id)                       → GET  /games/{id}
getBoard(id)                      → GET  /games/{id}/board
shoot(id, row, col)               → POST /games/{id}/shoot
getShots(id)                      → GET  /games/{id}/shots
```

---

## 🟢 Junior Akonou — Unity WebGL 3D + Déploiement

### Dépôt : `battleship-front/` (dossier unity + intégration)

| Fichier | Rôle | Action |
|---|---|---|
| `components/UnityGame.tsx` | Intégration Unity WebGL dans Next.js | Créer |
| `public/unity/` | Build Unity WebGL exporté | Exporter depuis Unity |
| `public/unity/Build/game.loader.js` | Loader Unity WebGL | Généré par Unity |
| `public/unity/Build/game.data` | Données du jeu | Généré par Unity |
| `public/unity/Build/game.framework.js` | Framework Unity WebGL | Généré par Unity |
| `public/unity/Build/game.wasm` | Code compilé WebAssembly | Généré par Unity |

### Projet Unity (dépôt ou dossier séparé `unity-project/`)

| Fichier Unity (C#) | Rôle | Action |
|---|---|---|
| `Assets/Scripts/GameManager.cs` | Reçoit données de Next.js, orchestre la scène | Créer |
| `Assets/Scripts/GridController.cs` | Gestion et affichage de la grille 3D | Créer |
| `Assets/Scripts/ShipController.cs` | Placement et animation des bateaux 3D | Créer |
| `Assets/Scripts/ShotEffect.cs` | Animations explosion (touché) et splash (eau) | Créer |
| `Assets/Scripts/JSBridge.cs` | Communication JavaScript ↔ Unity | Créer |

### JS Bridge à implémenter

```typescript
// Next.js → Unity (envoyer résultat d'un tir)
unityInstance.SendMessage('GameManager', 'OnShotResult', JSON.stringify({
  row: 3, col: 5, result: 'hit' // 'hit' | 'miss' | 'sunk'
}));

// Unity → Next.js (joueur a cliqué une case)
// Dans JSBridge.cs (C#)
Application.ExternalCall("onCellSelected", row, col);
```

### Déploiement Vercel

```bash
# Installer Vercel CLI
npm install -g vercel

# Déployer
vercel --prod

# Variable à configurer sur Vercel :
# NEXT_PUBLIC_API_URL = https://battleship-api.railway.app
```

---

## 🔗 Schéma d'interaction complet

```
┌─────────────────────────────────────────────────────────────────┐
│  MOHAND SADI (Next.js)          JUNIOR AKONOU (Unity WebGL)     │
│                                                                  │
│  app/page.tsx                   Assets/Scripts/GameManager.cs   │
│  app/game/[id]/page.tsx  ◄────► Assets/Scripts/GridController   │
│  components/ShipPlacer   JS     Assets/Scripts/ShipController   │
│  components/ShotResult  Bridge  Assets/Scripts/ShotEffect.cs    │
│  components/UnityGame ◄──────► Assets/Scripts/JSBridge.cs       │
│  lib/api.ts                                                      │
│       │                                                          │
└───────┼──────────────────────────────────────────────────────────┘
        │ HTTP / JSON (Axios)
┌───────┼──────────────────────────────────────────────────────────┐
│  IBRAHIM GUINDO (FastAPI + BDD)   │                              │
│                                   ▼                              │
│  app/main.py                                                     │
│  app/routers/players.py  ──► app/services/game_service.py       │
│  app/routers/games.py    ──► app/services/ai_service.py         │
│  app/routers/shots.py         (facile / moyen / difficile)       │
│  app/models/  ◄──────────── app/database.py                     │
│  app/schemas/                                                    │
│  tests/  (Pytest + HTTPX)                                        │
│       │                                                          │
│       ▼                                                          │
│  PostgreSQL (Railway)                                            │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📦 Branches Git recommandées

```
main                      → version stable, déployée
├── develop               → intégration commune
│   ├── feature/backend   → Ibrahim (models, schemas, routers, services, tests)
│   ├── feature/frontend  → Mohand (pages, composants, lib/api.ts)
│   └── feature/unity     → Junior (Unity WebGL, UnityGame.tsx, déploiement)
```

**Workflow :**
1. Chacun travaille sur sa branche `feature/`
2. Pull Request vers `develop` pour intégration
3. Revue croisée avant merge
4. `develop` → `main` pour les déploiements

---

## ✅ Checklist de démarrage

### Ibrahim
- [ ] Créer le dépôt `battleship-api` sur GitHub
- [ ] Initialiser FastAPI + Uvicorn
- [ ] Configurer CORS (`ALLOWED_ORIGINS`)
- [ ] Créer les modèles SQLAlchemy (5 modèles)
- [ ] Créer les schémas Pydantic
- [ ] Implémenter les routers (players, games, shots)
- [ ] Implémenter `game_service.py`
- [ ] Implémenter `ai_service.py` (3 niveaux)
- [ ] Écrire les tests Pytest
- [ ] Déployer sur Railway + configurer PostgreSQL

### Mohand
- [ ] Créer le dépôt `battleship-front` sur GitHub
- [ ] Initialiser Next.js 14 + TypeScript + Tailwind CSS
- [ ] Créer `lib/api.ts` avec tous les appels API
- [ ] Développer `app/page.tsx` (accueil)
- [ ] Développer `app/game/[id]/page.tsx` (jeu)
- [ ] Développer `app/leaderboard/page.tsx` (classement)
- [ ] Développer les composants (ShipPlacer, ShotResult, etc.)

### Junior
- [ ] Créer le projet Unity (Unity 2022 LTS)
- [ ] Modéliser la grille 3D et les bateaux
- [ ] Implémenter les animations (explosion, splash, victoire)
- [ ] Implémenter `JSBridge.cs` pour la communication
- [ ] Exporter en WebGL et copier dans `public/unity/`
- [ ] Créer `components/UnityGame.tsx` dans Next.js
- [ ] Tester l'intégration Unity ↔ Next.js
- [ ] Déployer sur Vercel

---

*Université des Antilles — L2 Informatique — 2026*
