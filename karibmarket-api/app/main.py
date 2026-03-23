from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routers import annonces, auth

app = FastAPI(title="KaribMarket API")

@app.get("/")
def root():
    return {"message": "KaribMarket API 🚀"}

@app.get("/health")
def health():
    return {"status": "ok"}

# Routers
app.include_router(annonces.router, prefix="/api/v1", tags=["Annonces"])
app.include_router(auth.router, prefix="/api/v1", tags=["Auth"])

# Gestion erreurs validation
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    erreurs = []
    for error in exc.errors():
        erreurs.append({
            "champ": " → ".join(str(x) for x in error["loc"]),
            "message": error["msg"]
        })
    return JSONResponse(status_code=422, content={"erreurs": erreurs})