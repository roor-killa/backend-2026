# from fastapi import FastAPI
# from app.routers import annonces
# from app.routers import auth
# from app.routers import prix
# from app.routers import scrape_urls_router

# app = FastAPI(
#     title="KaribMarket API",
#     version="1.0"
# )

# @app.get("/")
# def root():
#     return {"message": "Bienvenue sur KaribMarket API"}

# @app.get("/health")
# def health():
#     return {"status": "ok"}

# app.include_router(
#     annonces.router,
#     prefix="/api/v1",
#     tags=["Annonces"]
# )

# app.include_router(
#     auth.router,
#     prefix="/api/v1"
# )

# app.include_router(
#     prix.router, 
#     prefix="/api/v1"
# )

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import annonces, auth, prix, scrape_urls_router
from app.routers import scrape_runner

app = FastAPI(
    title="KaribMarket API",
    version="1.0"
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