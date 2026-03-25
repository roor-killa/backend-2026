

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routeurs.annonces import router as annonces_router
from app.routeurs.auth import router as auth_router
from app.database import Base, engine
from app import models  # noqa: F401


from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import redis.asyncio as redis


# Création de l'application
app = FastAPI(
    title="KaribMarket API",
    description="API de gestion de petites annonces caribéennes 🌺",
    version="1.0.0",
    docs_url="/docs",         # Interface Swagger (documentation interactive)
    redoc_url="/redoc"        # Interface ReDoc (documentation lisible)
)

# Crée les tables si elles n'existent pas encore
Base.metadata.create_all(bind=engine)

# Enregistrement des routeurs
app.include_router(annonces_router)
app.include_router(auth_router)

# Configuration CORS — autorise le frontend à appeler l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # URL de votre frontend Next.js
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route de base — vérification que l'API fonctionne
@app.get("/")
def read_root():
    return {
        "message": "Bienvenue sur KaribMarket API 🌴",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Route de santé — utile pour Docker et les load balancers
@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.on_event("startup")
async def startup():
    redis_client = redis.from_url("redis://localhost:6379")
    FastAPICache.init(RedisBackend(redis_client), prefix="karibmarket-cache")