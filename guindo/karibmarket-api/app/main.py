from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import redis.asyncio as redis

from app.routers import annonces, auth, prix, scrape_urls_router, scrape_runner, chatbot
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Démarrage — initialiser le cache Redis
    redis_client = redis.from_url(
        os.getenv("REDIS_URL", "redis://localhost:6379"),
        encoding="utf-8",
        decode_responses=False
    )
    FastAPICache.init(RedisBackend(redis_client), prefix="karibmarket-cache")
    print("✅ Cache Redis initialisé")
    yield
    # Arrêt — nettoyage si nécessaire
    print("🛑 Arrêt de l'application")


app = FastAPI(
    title="KaribMarket API",
    version="1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Bienvenue sur KaribMarket API"}


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(annonces.router, prefix="/api/v1", tags=["Annonces"])
app.include_router(auth.router, prefix="/api/v1")
app.include_router(prix.router, prefix="/api/v1")
app.include_router(scrape_urls_router.router, prefix="/api/v1")
app.include_router(scrape_runner.router, prefix="/api/v1")
app.include_router(chatbot.router, prefix="/api/v1")
