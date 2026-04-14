# Word Drop Rhythm Game

## Cahier des charges

### 1. Contexte et vision
Créer un jeu de rythme et de frappe clavier où le joueur contrôle un canon placé en bas au centre de l’écran. Des astéroïdes tombent depuis le haut, chacun affichant une lettre ou un mot. Le joueur doit appuyer sur la touche correspondante pour tirer et détruire l’astéroïde au bon timing.

Objectifs produit :
- Proposer une expérience arcade rapide, lisible et satisfaisante.
- Mélanger rythme musical, vitesse de frappe et précision.
- Permettre des parties courtes, rejouables, avec score et progression.

### 2. Objectifs fonctionnels
1. Gameplay principal
- Canon fixe en bas-centre.
- Astéroïdes générés en haut, chute vers le bas.
- Chaque astéroïde porte une lettre (MVP), puis des mots (version avancée).
- Appui clavier correct = tir + destruction si timing valide.
- Appui incorrect = pénalité légère (ex : perte de combo).
- Astéroïde qui atteint le bas = perte de vie.

2. Système de rythme
- Synchronisation du spawn avec le BPM de la musique.
- Fenêtres de timing : Perfect / Good / Miss.
- Multiplicateur de score basé sur le combo.

3. Progression
- Difficulté croissante (vitesse, densité, complexité lettres/mots).
- Niveaux ou vagues.
- Déblocage de cosmétiques (thèmes, canon, effets).

4. Backend
- Authentification joueur.
- Sauvegarde scores, statistiques, progression.
- Classements globaux et hebdomadaires.
- Historique des parties.

### 3. Public cible
- Joueurs casual et compétitifs.
- Contrôle clavier (PC).
- Sessions de 3 à 10 minutes.

### 4. Plateformes et technologies
- Moteur jeu : Godot 4.x.
- Backend API : FastAPI.
- Base de données : PostgreSQL.
- Conteneurisation : Docker + Docker Compose.

### 5. Périmètre fonctionnel détaillé
#### 5.1 MVP gameplay
- Menu principal : Jouer, Options, Classement, Quitter.
- Boucle de jeu : spawn, saisie clavier, tir, score, combo, vies.
- Fin de partie : score final, précision, combo max, astéroïdes détruits.
- Envoi score vers backend si connecté.

#### 5.2 MVP backend
- Création de compte / connexion.
- Endpoint de soumission de score.
- Endpoint leaderboard.
- Endpoint profil/statistiques.

#### 5.3 Features recommandées pour une bonne expérience
- Calibration latence audio/clavier.
- Tutoriel interactif court (60 à 90 secondes).
- Accessibilité :
  - Remap clavier.
  - Mode daltonien.
  - Taille de police configurable.
  - Option réduction des effets visuels.
- Qualité de vie :
  - Pause / reprise.
  - Réglages audio séparés (musique, SFX, UI).
  - Feedback clair des erreurs de frappe.
- Anti-frustration :
  - Difficulté adaptative légère.
  - Protection au début de manche.

### 6. Exigences non fonctionnelles
- Performance : 60 FPS stable, chargements rapides.
- Réseau : jouable hors ligne (score sync quand connexion dispo).
- Sécurité : JWT, hash de mot de passe (Argon2/bcrypt), validation stricte.
- Fiabilité : logs, gestion d’erreurs propre, reprise réseau.

### 7. Architecture technique
1. Client Godot
- Input Manager
- Spawn Manager
- Rhythm/Audio Manager
- Scoring/Combo System
- UI Manager
- API Client

2. Backend FastAPI
- Routes API
- Services métier
- Repositories DB
- Auth

3. PostgreSQL
- Tables minimales :
  - users
  - game_sessions
  - scores
  - player_stats
  - leaderboards (vue ou vue matérialisée en option)

4. Docker
- Services :
  - game-backend
  - postgres
  - pgadmin (dev optionnel)
  - reverse proxy (prod optionnel)

### 8. API cible (exemple)
- POST /auth/register
- POST /auth/login
- GET /profile/me
- POST /scores/submit
- GET /leaderboard/global
- GET /leaderboard/weekly
- GET /stats/me

### 9. Qualité et tests
- Backend : tests unitaires + tests API.
- Gameplay : timing windows, stress test spawn, précision input.
- Critères MVP : partie complète sans crash, score sync OK, leaderboard OK.

### 10. Livrables
- Build jeu Godot (Windows).
- Source client + backend.
- Stack Docker complète.
- Schéma DB + docs techniques.
- Plan de tests.

---

## Structure recommandée (clean architecture projet)

```text
jeu/
├─ README.md
├─ .env.example
├─ docker-compose.yml
├─ docker-compose.dev.yml
├─ docker-compose.prod.yml
├─ docs/
│  ├─ cahier-des-charges.md
│  ├─ architecture.md
│  ├─ api-spec.md
│  └─ game-design.md
├─ infra/
│  ├─ nginx/
│  │  └─ default.conf
│  ├─ postgres/
│  │  └─ init/
│  └─ scripts/
│     ├─ backup-db.sh
│     └─ restore-db.sh
├─ game/
│  ├─ project.godot
│  ├─ icon.svg
│  ├─ assets/
│  │  ├─ audio/
│  │  ├─ fonts/
│  │  ├─ sprites/
│  │  └─ vfx/
│  ├─ scenes/
│  │  ├─ main/
│  │  ├─ gameplay/
│  │  ├─ ui/
│  │  └─ effects/
│  ├─ scripts/
│  │  ├─ core/
│  │  ├─ gameplay/
│  │  ├─ ui/
│  │  ├─ services/
│  │  └─ utils/
│  ├─ autoload/
│  │  ├─ game_state.gd
│  │  ├─ audio_manager.gd
│  │  └─ api_client.gd
│  └─ tests/
│     ├─ unit/
│     └─ integration/
├─ backend/
│  ├─ Dockerfile
│  ├─ pyproject.toml
│  ├─ alembic.ini
│  ├─ alembic/
│  │  ├─ env.py
│  │  └─ versions/
│  ├─ app/
│  │  ├─ main.py
│  │  ├─ api/
│  │  │  ├─ deps.py
│  │  │  └─ v1/
│  │  │     ├─ auth.py
│  │  │     ├─ scores.py
│  │  │     ├─ leaderboard.py
│  │  │     └─ stats.py
│  │  ├─ core/
│  │  │  ├─ config.py
│  │  │  ├─ security.py
│  │  │  └─ logging.py
│  │  ├─ db/
│  │  │  ├─ session.py
│  │  │  ├─ base.py
│  │  │  └─ models/
│  │  ├─ schemas/
│  │  ├─ services/
│  │  ├─ repositories/
│  │  └─ tests/
│  │     ├─ unit/
│  │     └─ integration/
│  └─ requirements/
│     ├─ base.txt
│     ├─ dev.txt
│     └─ prod.txt
└─ .github/
   └─ workflows/
      ├─ backend-ci.yml
      └─ release.yml
```

### Règles d’organisation recommandées
- Séparer strictement `game/`, `backend/`, `infra/`, `docs/`.
- Versionner les migrations DB avec Alembic.
- Garder les variables sensibles hors Git (`.env`, secrets CI).
- Maintenir des dossiers de tests dédiés côté jeu et backend.
- Versionner l’API (`/api/v1/...`) dès le départ.
- Centraliser les scripts d’exploitation (backup/restore, seed, reset).

### Convention de branches (recommandée)
- `main` : stable production.
- `develop` : intégration continue.
- `feature/<nom>` : nouvelles fonctionnalités.
- `fix/<nom>` : corrections.

### Definition of Done (DoD)
Une tâche est terminée si :
- Code + tests passent en CI.
- Documentation mise à jour dans `docs/`.
- Pas de régression gameplay/API.
- Build Docker reproductible.
