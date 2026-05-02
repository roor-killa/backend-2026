from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .api import users, scores, leaderboard, shop
from .utils.exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    InsufficientFundsError,
    UserNotFoundError,
    InvalidQuantityError,
    InsufficientShieldsError,
)

app = FastAPI(title="Rhythm Game API", debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(scores.router)
app.include_router(leaderboard.router)
app.include_router(shop.router)


@app.exception_handler(UserAlreadyExistsError)
async def user_exists_handler(request: Request, exc: UserAlreadyExistsError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(InvalidCredentialsError)
async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsError):
    return JSONResponse(status_code=401, content={"detail": str(exc)})


@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(request: Request, exc: UserNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(InsufficientFundsError)
async def insufficient_funds_handler(request: Request, exc: InsufficientFundsError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(InvalidQuantityError)
async def invalid_quantity_handler(request: Request, exc: InvalidQuantityError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(InsufficientShieldsError)
async def insufficient_shields_handler(request: Request, exc: InsufficientShieldsError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.get("/health")
async def health():
    return {"status": "ok"}
