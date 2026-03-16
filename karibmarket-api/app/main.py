from fastapi import FastAPI

app = FastAPI(
    title="KaribMarket API",
    description="API de petites annonces",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "message": "Bienvenue sur KaribMarket API 🌴",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {"status": "ok"}