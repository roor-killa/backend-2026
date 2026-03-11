from fastapi import FastAPI
from app.routers import annonces

app = FastAPI(
    title="KaribMarket API",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "Bienvenue sur KaribMarket API 🌴"}

@app.get("/health")
def health():
    return {"status": "ok"}

# Ajouter le router annonces
app.include_router(
    annonces.router,
    prefix="/api/v1",
    tags=["Annonces"]
)