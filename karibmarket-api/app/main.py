from fastapi import FastAPI
from app.schemas.annonces import router as annonces_router

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