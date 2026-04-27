# 🚢 Bataille Navale 3D — Frontend

Interface web du jeu Bataille Navale 3D, construite avec **Next.js 14**, **TypeScript** et **Tailwind CSS**.

**Auteur :** Mohand Sadi
**3D & Déploiement :** Junior Akonou
**Backend :** Ibrahim Guindo

---

## 📋 Prérequis

- Node.js 18+
- npm
- Le backend FastAPI doit tourner sur `http://localhost:8000` (cf. `battleship-api/`)

## ⚙️ Installation

```bash
cd battleship-front
npm install
cp .env.example .env.local
```

## 🚀 Lancement

```bash
npm run dev      # développement → http://localhost:3000
npm run build    # build de prod
npm start        # lancer la prod
```

## 📁 Structure

```
battleship-front/
├── app/
│   ├── layout.tsx           ✅ layout global
│   ├── page.tsx             ✅ accueil (placeholder)
│   ├── globals.css          ✅ styles Tailwind
│   ├── game/[id]/page.tsx   ⏳ à créer — page de jeu
│   └── leaderboard/page.tsx ⏳ à créer — classement
├── components/
│   ├── ModeSelector.tsx         ⏳
│   ├── DifficultySelector.tsx   ⏳
│   ├── ShipPlacer.tsx           ⏳
│   ├── ShotResult.tsx           ⏳
│   ├── Leaderboard.tsx          ⏳
│   └── UnityGame.tsx            ⏳ (Junior)
├── lib/
│   └── api.ts               ✅ couche API complète
└── public/unity/            ⏳ build Unity (Junior)
```

## 🌐 API disponible (`lib/api.ts`)

Toutes les fonctions retournent des Promises typées et lèvent une `ApiError` en cas d'échec.

```typescript
import { createPlayer, createGame, shoot, getLeaderboard } from "@/lib/api";

const me = await createPlayer("Mohand");
const game = await createGame("solo", "moyen");
const result = await shoot(game.id, 3, 5); // { shot, game_over, ai_shot? }
```

## ✅ Prochaines étapes

1. `components/ModeSelector.tsx` + brancher sur la page d'accueil
2. `components/DifficultySelector.tsx`
3. `app/game/[id]/page.tsx` + `ShipPlacer`
4. `components/ShotResult.tsx`
5. `app/leaderboard/page.tsx` + `Leaderboard`
6. Laisser un slot dans `app/game/[id]/page.tsx` pour `<UnityGame />` (Junior)

---

*Université des Antilles — L2 Informatique — 2026*
