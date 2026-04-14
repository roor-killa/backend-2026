# Cahier des Charges — Bataille Navale 3D

**Université des Antilles — UFR Sciences, Technologies et Environnement**
Licence 2 Informatique — Cours Backend Web

---

| Champ | Valeur |
|---|---|
| **Groupe** | Ibrahim Guindo, Mohand Sadi, Junior Akonou |
| **Niveau** | Licence 2 Informatique |
| **Technologies** | FastAPI • Unity WebGL • Next.js |
| **Date** | Avril 2026 |

---

## 1. Présentation du projet

### 1.1 Contexte

Dans le cadre du cours de Backend Web (Licence 2 Informatique, Université des Antilles), ce projet de groupe de trois étudiants consiste à concevoir et développer une application web de jeu en ligne basée sur le framework FastAPI (Python). Le jeu choisi est la **Bataille Navale 3D**, combinant un backend FastAPI robuste, une interface web Next.js et un rendu 3D Unity WebGL intégré dans le navigateur.

### 1.2 Description du jeu

La Bataille Navale est un jeu de stratégie dans lequel chaque joueur dispose d'une grille de 10x10 cases sur laquelle il place ses bateaux. L'objectif est de couler tous les bateaux adverses avant que les siens ne soient détruits. La dimension 3D apportée par Unity WebGL rend l'expérience visuelle immersive : mer animée, bateaux modélisés, explosions et effets de touché.

### 1.3 Objectifs pédagogiques

- Maîtriser la conception d'une API REST avec FastAPI
- Appliquer les bonnes pratiques de structuration d'un projet Python
- Gérer l'état d'une session de jeu côté serveur
- Intégrer un moteur 3D (Unity WebGL) dans une application web Next.js
- Documenter une API avec Swagger / OpenAPI
- Travailler en équipe avec Git et une organisation claire des responsabilités

---

## 2. Fonctionnalités

### 2.1 Modes de jeu

L'application propose deux modes de jeu distincts, sélectionnables à la création d'une partie :

| Mode | Solo (vs IA) | Multijoueur |
|---|---|---|
| **Description** | Le joueur affronte une IA contrôlée par le serveur | Deux joueurs s'affrontent en temps réel |
| **Gestion** | 1 session, 1 joueur | 1 session, 2 joueurs |
| **IA** | Oui (niveaux : facile, moyen, difficile) | Non |
| **Rendu 3D** | Unity WebGL intégré | Unity WebGL intégré |

### 2.2 Fonctionnalités principales

#### Gestion des joueurs
- Création d'un joueur avec un pseudo
- Consultation du profil et du score
- Classement général (leaderboard)

#### Gestion des parties
- Création d'une partie (mode solo ou multijoueur)
- Rejoindre une partie existante (mode multijoueur)
- Placement des bateaux sur la grille 3D
- Déroulement des tours de jeu
- Détection automatique de fin de partie

#### Rendu 3D (Unity WebGL)
- Grille de jeu modélisée en 3D avec mer animée
- Bateaux 3D positionnés selon les données de l'API
- Animations d'explosion lors d'un touché
- Animations de splash lors d'un tir à l'eau
- Communication Unity ↔ Next.js via JavaScript Bridge

#### IA (mode Solo)

| Niveau | Comportement |
|---|---|
| 🟢 **Facile** | Tirs aléatoires sur les cases non jouées |
| 🟡 **Moyen** | Après un touché, cible les cases adjacentes |
| 🔴 **Difficile** | Algorithme de chasse par carte de probabilités — calcule les cases les plus susceptibles de contenir un bateau et cible en priorité les zones à haute densité |

---

## 3. Architecture technique

### 3.1 Vue d'ensemble

Le projet adopte une architecture trois tiers : un backend FastAPI sur Railway, un frontend Next.js sur Vercel intégrant un build Unity WebGL, et une base de données PostgreSQL.

```
Unity WebGL (3D) <--JS Bridge--> Next.js (Vercel) <--HTTP/JSON--> FastAPI (Railway) <--> PostgreSQL
```

### 3.2 Stack technologique

#### Backend — Ibrahim Guindo

| Composant | Technologie |
|---|---|
| Framework API | FastAPI (Python 3.11+) |
| Validation | Pydantic v2 |
| Serveur ASGI | Uvicorn |
| Documentation API | Swagger UI (intégré FastAPI) |
| Déploiement | Railway |

#### Base de données & Tests — Mohand Sadi

| Composant | Technologie |
|---|---|
| ORM | SQLAlchemy |
| BDD développement | SQLite |
| BDD production | PostgreSQL |
| Tests | Pytest + HTTPX |
| Versioning | Git / GitHub |

#### Frontend & 3D — Junior Akonou

| Composant | Technologie |
|---|---|
| Framework web | Next.js 14 (React) |
| Langage | TypeScript |
| Styles | Tailwind CSS |
| Moteur 3D | Unity WebGL |
| Requêtes API | Axios |
| Déploiement | Vercel |

### 3.3 Structure des dépôts

#### Backend — `battleship-api/`

```
battleship-api/
├── app/
│   ├── main.py              # Point d'entrée FastAPI + CORS
│   ├── database.py          # Configuration SQLAlchemy
│   ├── models/              # Modèles SQLAlchemy
│   ├── schemas/             # Schémas Pydantic
│   ├── routers/             # Endpoints (players, games, shots)
│   ├── services/            # Logique métier + IA
│   └── core/                # Constantes (grille, bateaux)
├── tests/
├── requirements.txt
└── README.md
```

#### Frontend — `battleship-front/`

```
battleship-front/
├── app/
│   ├── page.tsx             # Accueil (choix du mode)
│   ├── game/[id]/page.tsx   # Page de jeu
│   └── leaderboard/page.tsx # Classement
├── components/
│   ├── UnityGame.tsx        # Intégration Unity WebGL
│   ├── ShipPlacer.tsx       # Placement des bateaux
│   └── ShotResult.tsx       # Résultat des tirs
├── lib/
│   └── api.ts               # Appels API FastAPI
├── public/
│   └── unity/               # Build Unity WebGL exporté
└── README.md
```

### 3.4 Déploiement

| Environnement | Service | URL cible |
|---|---|---|
| Backend (prod) | Railway | https://battleship-api.railway.app |
| Frontend (prod) | Vercel | https://battleship-front.vercel.app |
| Backend (dev) | Uvicorn local | http://localhost:8000 |
| Frontend (dev) | Next.js local | http://localhost:3000 |
| Docs API | Swagger UI | http://localhost:8000/docs |

---

## 4. Endpoints de l'API REST

### 4.1 Joueurs

| Méthode | Endpoint | Description |
|---|---|---|
| `POST` | `/players` | Créer un nouveau joueur |
| `GET` | `/players/{id}` | Consulter le profil d'un joueur |
| `GET` | `/players/leaderboard` | Classement général |

### 4.2 Parties

| Méthode | Endpoint | Description |
|---|---|---|
| `POST` | `/games` | Créer une partie (solo ou multijoueur) |
| `POST` | `/games/{id}/join` | Rejoindre une partie (multijoueur) |
| `POST` | `/games/{id}/place-ships` | Placer ses bateaux sur la grille |
| `GET` | `/games/{id}` | État complet de la partie |
| `GET` | `/games/{id}/board` | Afficher les grilles |

### 4.3 Tirs

| Méthode | Endpoint | Description |
|---|---|---|
| `POST` | `/games/{id}/shoot` | Effectuer un tir sur une case |
| `GET` | `/games/{id}/shots` | Historique de tous les tirs |

---

## 5. Modèle de données

### 5.1 Entités principales

| Entité | Champs principaux | Description |
|---|---|---|
| `Player` | id, pseudo, score, games_played | Représente un joueur |
| `Game` | id, mode, status, current_turn, winner_id | Une partie en cours ou terminée |
| `Board` | id, game_id, player_id, grid (JSON) | Grille d'un joueur dans une partie |
| `Ship` | id, board_id, type, positions (JSON), is_sunk | Un bateau placé sur une grille |
| `Shot` | id, game_id, player_id, row, col, result | Un tir effectué (touché/coulé/eau) |

### 5.2 Bateaux disponibles

| Bateau | Taille (cases) | Quantité |
|---|---|---|
| Porte-avions | 5 | 1 |
| Croiseur | 4 | 1 |
| Destroyer | 3 | 1 |
| Sous-marin | 3 | 1 |
| Torpilleur | 2 | 1 |

---

## 6. Règles du jeu

### 6.1 Phase de placement

- Chaque joueur place ses 5 bateaux sur sa grille 3D de 10x10
- Les bateaux peuvent être placés horizontalement ou verticalement
- Les bateaux ne peuvent pas se chevaucher ni sortir de la grille
- En mode solo, l'IA place ses bateaux automatiquement

### 6.2 Phase de jeu

- Les joueurs tirent à tour de rôle en sélectionnant une case sur la grille 3D
- Résultats possibles : **À l'eau**, **Touché**, **Coulé** — avec animations Unity correspondantes
- Le tour passe au joueur suivant après chaque tir

### 6.3 Condition de victoire

- La partie se termine lorsque tous les bateaux d'un joueur sont coulés
- Le vainqueur est déclaré avec animation de victoire dans Unity
- Le score du vainqueur est mis à jour via l'API FastAPI

---

## 7. Répartition des tâches

### 7.1 Ibrahim Guindo — Responsable Backend

- Initialisation du projet FastAPI et configuration Uvicorn
- Mise en place du CORS pour la communication avec Next.js
- Développement des routers : players, games, shots
- Implémentation de la logique métier (placement, tirs, détection victoire)
- Développement de l'IA solo (niveaux facile, moyen et difficile)
- Déploiement du backend sur Railway
- Rédaction du README backend

### 7.2 Mohand Sadi — Responsable Base de données & Tests

- Conception et implémentation des modèles SQLAlchemy
- Définition des schémas Pydantic (requêtes et réponses)
- Configuration de SQLite (développement) et PostgreSQL (production)
- Écriture des migrations de base de données
- Rédaction des tests unitaires et d'intégration avec Pytest + HTTPX
- Validation des endpoints via Swagger UI
- Gestion du dépôt Git (branches, pull requests, résolution de conflits)

### 7.3 Junior Akonou — Responsable Frontend & 3D

- Initialisation du projet Next.js 14 avec TypeScript et Tailwind CSS
- Développement des pages : accueil, jeu, leaderboard
- Intégration du build Unity WebGL dans Next.js via composant `UnityGame.tsx`
- Mise en place du JavaScript Bridge Unity ↔ Next.js
- Développement des composants : placement bateaux, résultats tirs
- Connexion au backend FastAPI via Axios (`lib/api.ts`)
- Déploiement du frontend sur Vercel

### 7.4 Tableau récapitulatif

| Membre | Pôle | Livrables principaux |
|---|---|---|
| Ibrahim Guindo | Backend | API FastAPI complète, IA (3 niveaux), déploiement Railway |
| Mohand Sadi | BDD + Tests | Modèles SQLAlchemy, PostgreSQL, suite de tests Pytest |
| Junior Akonou | Frontend + 3D | Interface Next.js, intégration Unity WebGL, déploiement Vercel |

---

## 8. Contraintes et exigences

### 8.1 Exigences fonctionnelles

- L'API doit retourner des réponses JSON avec codes HTTP appropriés (200, 201, 400, 404, 422)
- Toutes les données entrantes doivent être validées avec Pydantic
- La documentation Swagger doit être accessible à `/docs`
- L'état de la partie doit être persisté en base de données
- Le build Unity WebGL doit communiquer avec Next.js via JavaScript Bridge
- L'IA difficile doit utiliser une carte de probabilités pour optimiser ses tirs

### 8.2 Exigences non fonctionnelles

- Le code doit être organisé en modules distincts (routers, services, models)
- Des tests unitaires doivent couvrir la logique métier principale
- Le projet doit être versionné sur Git avec des commits réguliers par membre
- Un fichier README.md doit documenter l'installation dans chaque dépôt
- Le CORS doit être correctement configuré côté FastAPI

---

## 9. Planning prévisionnel

| Phase | Responsable(s) | Tâches | Livrable |
|---|---|---|---|
| Phase 1 | Tous | Setup des dépôts Git, environnements de développement | 2 dépôts initialisés |
| Phase 2 | Mohand + Ibrahim | Modèles SQLAlchemy, schémas Pydantic, configuration BDD | Modèle de données |
| Phase 3 | Ibrahim | Endpoints API, logique de jeu, IA (3 niveaux) | API complète |
| Phase 4 | Mohand | Tests unitaires et d'intégration, validation endpoints | Suite de tests |
| Phase 5 | Junior | Interface Next.js, intégration Unity WebGL, JS Bridge | Frontend jouable |
| Phase 6 | Tous | CORS, déploiement Railway + Vercel, README, tests finaux | Version déployée |

---

## 10. Conclusion

Ce projet de Bataille Navale 3D constitue une application full-stack ambitieuse et complète, développée par un groupe de trois étudiants de Licence 2 Informatique. La combinaison FastAPI (backend), PostgreSQL (base de données), Next.js (interface web) et Unity WebGL (rendu 3D) illustre une architecture professionnelle moderne avec une séparation claire des responsabilités.

Chaque membre du groupe apporte une contribution distincte et complémentaire : **Ibrahim Guindo** sur le backend et la logique métier (incluant l'IA à trois niveaux), **Mohand Sadi** sur la persistance des données et la qualité du code, et **Junior Akonou** sur l'expérience utilisateur et le rendu 3D. Le déploiement sur Railway et Vercel permettra de présenter une application pleinement fonctionnelle et accessible en ligne.

---

*Université des Antilles — UFR Sciences, Technologies et Environnement — Licence 2 Informatique*
