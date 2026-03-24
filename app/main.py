from fastapi import FastAPI
from app.routers import annonces, auth
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import redis.asyncio as redis

# Création de l'application FastAPI
app = FastAPI(
    title="KaribMarket API",
    description="API de gestion de petites annonces caribéennes 🌺",
    version="1.0.0"
)

@app.on_event("startup")
async def startup():
    redis_client = redis.from_url("redis://localhost:6379")
    FastAPICache.init(RedisBackend(redis_client), prefix="karibmarket-cache")
    
# On connecte le fichier annonces.py à notre application principale
app.include_router(
    annonces.router,
    prefix="/api/v1",
    tags=["Annonces"]
)

# On connecte le fichier auth.py pour l'authentification
app.include_router(
    auth.router,
    prefix="/api/v1",
    tags=["Authentification"]
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