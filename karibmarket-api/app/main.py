from fastapi import FastAPI
from app.routers import annonces, auth

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API KaribMarket"}

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(annonces.router, prefix="/api/v1", tags=["Annonces"])
app.include_router(auth.router, prefix="/api/v1", tags=["Auth"])