from fastapi.exceptions import RequestValidationError
from app.routers import annonces, health, accueil
from fastapi.responses import JSONResponse
from fastapi import FastAPI


app = FastAPI(
    title="KaribMarket API",
    description="API de petites annonces pour Martinique et Guadeloupe",
    version="1.0.0",
)

app.include_router(
    annonces.router,
    prefix="/annonces",
    tags=["Annonces"]
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    erreurs = []
    for error in exc.errors():
        erreurs.append({
            "champ": " → ".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "valeur_recue": error.get("input")
        })
    return JSONResponse(
        status_code=422,
        content={"success": False, "erreurs": erreurs}
    )


app.include_router(health.router)
app.include_router(accueil.router)