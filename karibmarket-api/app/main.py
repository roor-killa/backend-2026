from fastapi import FastAPI
from app.routers.annonces import router as annonces_router

app = FastAPI()

app.include_router(
    annonces_router,
    prefix="/annonces",
    tags=["Annonces"]
)