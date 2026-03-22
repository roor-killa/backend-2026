
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


app = FastAPI(
    title="Scrapping",
    description="Gestion de donnée scrapping",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:80','http://localhost:3000'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {
        "message": "FastAPI marche!!",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}





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