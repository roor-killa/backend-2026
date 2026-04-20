from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import annonces
from app.routers import auth
from app.routers.admin import router as admin_router
from app.routers.prix import router as prix_router
from app.routers.chatbot import router as chatbot_router
from app.database import engine, Base
import app.models.annonce       # noqa: F401
import app.models.utilisateur   # noqa: F401
import app.models.scrape_url    # noqa: F401
import app.models.scrape_log    # noqa: F401
import app.models.produit       # noqa: F401

# Création des tables gérées par ce service (karibmarket DB)
Base.metadata.create_all(bind=engine)
# Note : la table 'produits' dans kiprix_db est créée par le projet POO

app = FastAPI(
    title="KaribMarket API",
    description="API de gestion de petites annonces caribéennes 🌺",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://nextjs_app:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(annonces.router, prefix="/api/v1", tags=["Annonces"])
app.include_router(admin_router, prefix="/api/v1")
app.include_router(prix_router, prefix="/api/v1")
app.include_router(chatbot_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": "Bienvenue sur KaribMarket API 🌴", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/getnumber")
def get_my_number():
    return {"numero": "0696112233"}
