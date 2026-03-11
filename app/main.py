from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.database import init_db
from app.routers import annonces, utilisateurs

app = FastAPI(title="KaribMarket API", version="1.0.0")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    erreurs = []
    for error in exc.errors():
        erreurs.append(
            {
                "champ": " -> ".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "valeur_recue": error.get("input"),
            }
        )

    return JSONResponse(
        status_code=422,
        content={"success": False, "erreurs": erreurs},
    )


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Bienvenue sur KaribMarket API"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(
    annonces.router,
    prefix="/api/v1",
    tags=["Annonces"],
)

app.include_router(
    utilisateurs.router,
    prefix="/api/v1",
    tags=["Utilisateurs"],
)
