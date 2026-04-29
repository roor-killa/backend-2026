# 🍹 Ti Punch Master — Full Project
## FastAPI Backend + Unity Desktop Edition
### Version 2.0 · Martinique 2026

---

## Structure du projet

```
tipunch-full/
├── backend/                        ← Serveur FastAPI (Python)
│   ├── main.py                     ← Application FastAPI (routes)
│   ├── models.py                   ← Schémas Pydantic
│   ├── requirements.txt            ← Dépendances Python
│   └── data/
│       ├── clients.json            ← 12 clients + recettes
│       └── leaderboard.json        ← Classement (auto-créé)
│
└── unity/
    └── Assets/
        ├── Scripts/
        │   ├── GameManager.cs      ← Singleton, flux de jeu
        │   ├── ScoringAPI.cs       ← HTTP UnityWebRequest ↔ FastAPI
        │   ├── UIController.cs     ← UI Canvas (sliders, feedback, HUD)
        │   ├── GlassController.cs  ← Verre animé + shader params
        │   ├── ClientManager.cs    ← Animations & réactions clients
        │   ├── CocktailDatabase.cs ← 8 cocktails embarqués (C#)
        │   ├── LeaderboardScene.cs ← Contrôleur scène classement
        │   └── OfflineData.cs      ← Données mode offline
        └── Shaders/
            └── LiquidShader.shader ← Shader HLSL liquide animé
```

---

## 1. Lancer le Backend FastAPI

### Prérequis
- Python 3.11+

### Installation

```bash
cd backend
pip install -r requirements.txt
```

### Démarrage

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Le serveur démarre sur **http://localhost:8000**

### Documentation interactive

Ouvre **http://localhost:8000/docs** dans ton navigateur pour tester
toutes les routes via Swagger UI (auto-généré par FastAPI).

### Routes disponibles

| Méthode | Endpoint       | Description                        |
|---------|----------------|------------------------------------|
| GET     | `/`            | Statut API                         |
| GET     | `/clients`     | Liste des 12 clients + recettes    |
| GET     | `/clients/{id}`| Un client spécifique               |
| POST    | `/score`       | Calcule le score d'un service      |
| GET     | `/leaderboard` | Top 5 des meilleurs scores         |
| POST    | `/leaderboard` | Enregistre un score de fin partie  |
| DELETE  | `/leaderboard` | Remet le classement à zéro         |

### Exemple de test manuel

```bash
# Tester le score d'un ti punch
curl -X POST http://localhost:8000/score \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "madeleine",
    "cocktail": "tipunch",
    "dosages": {"rhum": 5, "citron": 3, "sucre": 2}
  }'

# Réponse attendue :
# {"score": 85, "feedback": "Très bon, bravo ! ...", "target": {...}, ...}
```

---

## 2. Intégrer les scripts dans Unity

### Prérequis Unity
- Unity 2022 LTS (ou supérieur)
- TextMeshPro (installé via Package Manager)
- Newtonsoft.Json *(optionnel — JsonUtility est utilisé par défaut)*

### Étapes d'intégration

#### A. Copier les fichiers
1. Copie tout le contenu de `unity/Assets/` dans ton projet Unity `Assets/`
2. Le shader `LiquidShader.shader` va dans `Assets/Shaders/`

#### B. Configurer les scènes
Crée 3 scènes dans `Assets/Scenes/` :
- **MainMenu** — Menu principal
- **GameScene** — Gameplay principal
- **Leaderboard** — Classement final

Dans **Build Settings** (Ctrl+Shift+B), ajoute les 3 scènes dans cet ordre.

#### C. Configurer le GameManager (GameScene)
1. Crée un GameObject vide `GameManager` dans la scène GameScene
2. Attache les scripts : `GameManager`, `ScoringAPI`, `UIController`,
   `GlassController`, `ClientManager`
3. Dans l'inspecteur de `GameManager`, assigne :
   - `uiController` → ton UIController
   - `clientManager` → ton ClientManager
   - `scoringAPI` → ton ScoringAPI
   - `glassController` → ton GlassController

#### D. Configurer ScoringAPI
Dans l'inspecteur de `ScoringAPI` :
- `baseUrl` = `http://localhost:8000`  *(développement)*
- `timeoutSecs` = `5`
- `playerName` = nom du joueur (ou champ UI)

#### E. Configurer le verre (GlassController)
1. Crée 3 Mesh Renderers pour les couches de liquide (fond, milieu, haut)
2. Crée un Material par couche avec le shader `TiPunchMaster/LiquidFill`
3. Assigne les 3 renderers à `liquidLayers[0,1,2]`
4. Connecte les Particle Systems (`bubblesPS`, `splashPS`) et l'`Animator`

#### F. Configurer l'UI Canvas (UIController)
Dans l'inspecteur de `UIController`, assigne tous les champs :
- `clientAvatarImage`, `clientNameText`, `clientDialogueText`, `difficultyBadgeText`
- `cocktailLabelText`, `scoreText`, `mancheDotsParent`, `mancheDotPrefab`
- `slidersParent`, `sliderGroupPrefab`
- `serveButton`, `feedbackPanel`, `nextClientButton`
- Bouton "Servir" → `OnClick()` → `UIController.OnServeButtonClicked()`
- Bouton "Client suivant" → `OnClick()` → `UIController.OnNextClientClicked()`

#### G. Scène Leaderboard
1. Attache `LeaderboardScene.cs` à un GameObject dans la scène Leaderboard
2. Assigne `finalScoreText`, `leaderboardParent`, `leaderboardRowPrefab`, etc.

---

## 3. Système de score (cahier des charges §5.3)

| Écart total (Σ|diff| par ingrédient) | Score |
|---------------------------------------|-------|
| 0 cl — dosage parfait                 | **100 pts** |
| ≤ tolérance                           | **85 pts**  |
| ≤ tolérance × 2                       | **65 pts**  |
| ≤ tolérance × 3 + 1                   | **40 pts**  |
| ≤ tolérance × 4 + 2                   | **20 pts**  |
| Au-delà                               | **5 pts**   |

Tolérance : `1.0 cl` (Facile/Moyen) · `0.5 cl` (Difficile)

Score maximum par partie : **500 pts** (5 manches × 100 pts)

---

## 4. Mode offline

Si le serveur FastAPI est inaccessible (timeout 5s) :
- Les clients sont chargés depuis `OfflineData.cs` (embarqué)
- Le score est calculé localement dans `ScoringAPI.CalculateScoreLocally()`
- Le classement n'est pas soumis au serveur
- Un banner "Mode offline" s'affiche dans l'UI

---

## 5. Ajouter un nouveau cocktail

**Backend** — `data/clients.json` : ajouter un client avec la recette  
**Unity** — `CocktailDatabase.cs` : ajouter une entrée dans `_db`  
**Unity** — `OfflineData.cs` : ajouter la recette dans `OfflineRecipes.Get()`

Temps estimé : < 30 minutes (data-driven, pas de code à modifier)

---

*Ti Punch Master · Unity Desktop Edition v2.0 · Cahier des charges Avril 2026*
