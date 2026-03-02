from fastapi import FastAPI
from app.routers import annonces

app = FastAPI()

@app.get("/")
def home():
    return {"message": "KaribMarket API fonctionne"}

@app.get("/health")
def health():
    return {"status": "ok"}

# Inclure le router
app.include_router(
    annonces.router,
    prefix="/api/v1",
    tags=["Annonces"]
)
