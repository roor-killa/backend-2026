from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import annonces
from app.routers import auth
from app.database import engine, Base
import app.models.annonce  # noqa: F401 — enregistre le modèle auprès de Base
import app.models.utilisateur  # noqa: F401

# Création des tables en base de données au démarrage
Base.metadata.create_all(bind=engine)

# Création de l'application
app = FastAPI(
    title="KaribMarket API",
    description="API de gestion de petites annonces caribéennes 🌺",
    version="1.0.0",
    docs_url="/docs",         # Interface Swagger (documentation interactive)
    redoc_url="/redoc"        # Interface ReDoc (documentation lisible)
)

# Configuration CORS — autorise le frontend à appeler l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # URL de votre frontend Next.js
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(
    annonces.router,
    prefix="/api/v1",
    tags=["Annonces"]
)

# Route de base — vérification que l'API fonctionne
@app.get("/")
def read_root():
    return {
        "message": "Bienvenue sur KaribMarket API 🌴",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Route de santé — utile pour Docker et les load balancers
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Ma premiere fonction pour bien comprendre
@app.get("/getnumber")
def get_my_number():
    numero = "0696112233"
    return {"numero": numero}
