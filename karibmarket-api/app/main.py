from fastapi import FastAPI
from app.routers import annonces, health, accueil
from app.routers.annonces import router as annonces_router

app = FastAPI(
    title="KaribMarket API",
    description="API de petites annonces pour Martinique et Guadeloupe",
    version="1.0.0",
)

app.include_router(
    annonces_router,
    prefix="/annonces",
    tags=["Annonces"]
)

app.include_router(
    annonces.router,
    prefix="/api/v1",
    tags=["Annonces"]
)

app.include_router(health.router)

app.include_router(accueil.router)