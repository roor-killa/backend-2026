from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_tables, get_settings
from app.routers import players_router, games_router, shots_router

# ── Initialisation ────────────────────────────────────
settings = get_settings()

app = FastAPI(
    title="Bataille Navale 3D — API",
    description="""
    API REST du jeu **Bataille Navale 3D**.

    ## Fonctionnalités
    - 🎮 Mode **Solo** (vs IA : facile / moyen / difficile)
    - 👥 Mode **Multijoueur**
    - 🚢 Placement des bateaux
    - 💥 Tirs avec résultat en temps réel
    - 🏆 Leaderboard

    ## Stack
    - **Backend** : FastAPI + SQLAlchemy
    - **Frontend** : Next.js + Unity WebGL
    - **BDD** : SQLite (dev) / PostgreSQL (prod)
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────
# Permet au frontend Next.js (Vercel) d'appeler l'API
origins = [origin.strip() for origin in settings.allowed_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────
app.include_router(players_router)
app.include_router(games_router)
app.include_router(shots_router)

# ── Création des tables au démarrage ─────────────────
@app.on_event("startup")
def on_startup():
    # Importer les modèles pour que SQLAlchemy les enregistre
    import app.models  # noqa: F401
    create_tables()


# ── Route de santé ────────────────────────────────────
@app.get("/", tags=["Santé"], summary="Vérification de l'API")
def health_check():
    return {
        "status": "ok",
        "app":    "Bataille Navale 3D API",
        "version": "1.0.0",
        "docs":   "/docs",
    }