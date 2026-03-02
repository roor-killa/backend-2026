from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import annonces
# Création de l'application
app = FastAPI(
    title="KaribMarket API",
    description="API de gestion de petites annonces caribéennes 🌺",
    version="1.0.0",
    docs_url="/docs",         # Interface Swagger (documentation interactive)
    redoc_url="/redoc"        # Interface ReDoc (documentation lisible)
)

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


app.include_router(
    annonces.router,
    prefix="/api/v1",
    tags=["Annonces"]  # Groupe dans la doc Swagger
)