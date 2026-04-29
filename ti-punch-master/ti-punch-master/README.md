# 🍹 Ti Punch Master — Desktop Edition

> Jeu de dosage de cocktails martiniquais · Version 2.0 · Avril 2026

---

## Jouer sans installation (le plus simple)

Ouvre simplement **`index.html`** dans ton navigateur web.  
Double-clique sur le fichier → le jeu démarre immédiatement.  
Aucune installation requise.

---

## Lancer comme une vraie application desktop (Electron)

### Prérequis
- [Node.js](https://nodejs.org) version 18 ou supérieure

### Étapes

```bash
# 1. Dans le dossier du jeu :
npm install

# 2. Lancer le jeu :
npm start
```

---

## Compiler un exécutable (.exe / .dmg / .AppImage)

```bash
npm install

# Windows (.exe installateur)
npm run build:win

# macOS (.dmg)
npm run build:mac

# Linux (.AppImage)
npm run build:linux

# Les 3 plateformes d'un coup
npm run build:all
```

Les fichiers compilés apparaissent dans le dossier **`dist/`**.

---

## Structure des fichiers

```
ti-punch-master/
├── index.html      → Structure HTML du jeu
├── style.css       → Styles visuels (ambiance tropicale)
├── game.js         → Logique de jeu (clients, cocktails, score)
├── main.js         → Point d'entrée Electron (app desktop)
├── package.json    → Configuration npm / electron-builder
└── README.md       → Ce fichier
```

---

## Gameplay

- **5 manches** par partie
- **8 cocktails** : Ti Punch, Mojito, Planteur, Daïquiri Fraise, Sangria, Punch Coco, Gin Tonic, Spritz
- **12 clients** martiniquais avec personnalités et dialogues uniques
- **3 sliders** par cocktail (ingrédients en centilitres)
- **Verre animé** en temps réel selon les dosages
- **Score** calculé selon l'écart au dosage cible (100 / 85 / 65 / 40 / 20 / 5 pts)
- **Classement** top 5 sauvegardé localement

---

## Système de score

| Écart total (somme des |diff| par ingrédient) | Score |
|---|---|
| 0 cl — dosage parfait | **100 pts** |
| ≤ tolérance | **85 pts** |
| ≤ tolérance × 2 | **65 pts** |
| ≤ tolérance × 3 + 1 | **40 pts** |
| ≤ tolérance × 4 + 2 | **20 pts** |
| Au-delà | **5 pts** |

Tolérance : 1 cl (Facile/Moyen) · 0,5 cl (Difficile)

---

*Ti Punch Master · Unity Desktop Edition v2.0 · Cahier des charges Avril 2026*
