from fastapi import FastAPI
from app.routers import annonces
from app.routers import auth

app = FastAPI(
    title="KaribMarket API",
    version="1.0"
)

@app.get("/")
def root():
    return {"message": "Bienvenue sur KaribMarket API"}

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(
    annonces.router,
    prefix="/api/v1",
    tags=["Annonces"]
)

app.include_router(
    auth.router,
    prefix="/api/v1"
)