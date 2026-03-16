from fastapi import FastAPI
from app.routers import annonces

app = FastAPI(title="KaribMarket API")

@app.get("/")
def root():
    return {"message": "KaribMarket API fonctionne 🚀"}

@app.get("/health")
def health():
    return {"status": "ok"}

# Inclusion du router annonces
app.include_router(
    annonces.router,
    prefix="/api/v1",
    tags=["Annonces"]
)