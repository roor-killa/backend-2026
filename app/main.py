from fastapi import FastAPI

from app.routers import annonces

app = FastAPI(title="KaribMarket API", version="1.0.0")


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Bienvenue sur KaribMarket API"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(
    annonces.router,
    prefix="/api/v1",
    tags=["Annonces"],
)
