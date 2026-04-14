# 🚢 Bataille Navale 3D — Frontend (Next.js + Unity WebGL)

> Interface web du jeu Bataille Navale 3D

**Frontend (Next.js) : Mohand Sadi**
**3D & Déploiement (Unity WebGL) : Junior Akonou**

---

## 📋 Prérequis

- Node.js 18+
- npm ou yarn
- Git
- Unity 2022 LTS *(Junior uniquement, pour le projet 3D)*

---

## ⚙️ Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/votre-groupe/battleship-front.git
cd battleship-front

# 2. Installer les dépendances
npm install

# 3. Copier le fichier d'environnement
cp .env.example .env.local
```

---

## 🔧 Variables d'environnement

Modifier `.env.local` :

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
# NEXT_PUBLIC_API_URL=https://battleship-api.railway.app
```

---

## 🚀 Lancement

```bash
npm run dev     # Développement → http://localhost:3000
npm run build   # Build production
npm start       # Lancer en production
```

> ⚠️ Le backend FastAPI doit tourner sur http://localhost:8000

---

## 📁 Structure du projet

```
battleship-front/
│
│  ── MOHAND SADI ──────────────────────────────
├── app/
│   ├── layout.tsx               # Layout global
│   ├── page.tsx                 # Accueil (choix mode)
│   ├── game/[id]/page.tsx       # Page de jeu
│   └── leaderboard/page.tsx     # Classement
├── components/
│   ├── ModeSelector.tsx         # Solo / Multijoueur
│   ├── DifficultySelector.tsx   # Facile / Moyen / Difficile
│   ├── ShipPlacer.tsx           # Placement des bateaux
│   ├── ShotResult.tsx           # Résultat tir
│   └── Leaderboard.tsx          # Tableau classement
├── lib/
│   └── api.ts                   # Appels API FastAPI (Axios)
│
│  ── JUNIOR AKONOU ─────────────────────────────
├── components/
│   └── UnityGame.tsx            # Intégration Unity WebGL
├── public/
│   └── unity/                   # Build Unity WebGL exporté
│       └── Build/
│           ├── game.loader.js
│           ├── game.data
│           ├── game.framework.js
│           └── game.wasm
│
├── .env.example
├── package.json
└── README.md
```

---

## 🎮 Intégration Unity WebGL *(Junior)*

### Exporter depuis Unity

1. Ouvrir le projet Unity (`unity-project/`)
2. `File > Build Settings > WebGL > Build`
3. Copier le dossier de build dans `public/unity/`

### JS Bridge

**Next.js → Unity** (envoyer résultat d'un tir) :
```typescript
unityInstance.SendMessage('GameManager', 'OnShotResult', JSON.stringify({
  row: 3, col: 5, result: 'hit'
}));
```

**Unity → Next.js** (joueur clique une case) :
```csharp
// JSBridge.cs (C#)
Application.ExternalCall("onCellSelected", row, col);
```

---

## 🌐 Appels API disponibles *(lib/api.ts — Mohand)*

```typescript
const API = process.env.NEXT_PUBLIC_API_URL;

createPlayer(pseudo)              // POST /players
getPlayer(id)                     // GET  /players/{id}
getLeaderboard()                  // GET  /players/leaderboard
createGame(mode, difficulty?)     // POST /games
joinGame(id)                      // POST /games/{id}/join
placeShips(id, ships)             // POST /games/{id}/place-ships
getGame(id)                       // GET  /games/{id}
getBoard(id)                      // GET  /games/{id}/board
shoot(id, row, col)               // POST /games/{id}/shoot
getShots(id)                      // GET  /games/{id}/shots
```

---

## ☁️ Déploiement Vercel *(Junior)*

```bash
npm install -g vercel
vercel login
vercel --prod
```

Variable à configurer sur Vercel :
- `NEXT_PUBLIC_API_URL` → https://battleship-api.railway.app

---

*Université des Antilles — L2 Informatique — 2026*
