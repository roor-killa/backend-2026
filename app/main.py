from fastapi import FastAPI
from app.routers import annonces

# Création de l'application FastAPI
app = FastAPI(
    title="KaribMarket API",
    description="API de gestion de petites annonces caribéennes 🌺",
    version="1.0.0"
)

# On connecte le fichier annonces.py à notre application principale
app.include_router(
    annonces.router,
    prefix="/api/v1",
    tags=["Annonces"]
)

# Route d'accueil basique
@app.get("/")
def read_root():
    return {
        "message": "Bienvenue sur KaribMarket API 🌴",
        "docs": "Va sur /docs pour voir la documentation interactive !"
    }

# Route de vérification de santé
@app.get("/health")
def health_check():
    return {"status": "ok"}