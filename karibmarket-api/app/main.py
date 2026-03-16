from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.routers import annonces
from app.routers import auth

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):

    erreurs = []

    for error in exc.errors():
        erreurs.append({
            "champ": " -> ".join(str(x) for x in error["loc"]),
            "message": error["msg"],
        })

    return JSONResponse(
        status_code=422,
        content={"success": False, "erreurs": erreurs})

@app.get("/")
def home():
    return {"message": "KaribMarket API fonctionne"}

@app.get("/health")
def health():
    return {"status": "ok"}

# Inclure le router
app.include_router(
    annonces.router,
    prefix="/api/v1",
    tags=["Annonces"]
)

app.include_router(auth.router, prefix="/api/v1")
