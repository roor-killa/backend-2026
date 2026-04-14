from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.api.v1.leaderboard import router as leaderboard_router
from app.api.v1.scores import router as scores_router
from app.api.v1.stats import router as stats_router
from app.core.logging import configure_logging
from app.db.base import Base
from app.db import models  # noqa: F401
from app.db.session import engine

configure_logging()

app = FastAPI(title="Word Drop Backend", version="0.1.0")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth_router, prefix="/api/v1")
app.include_router(scores_router, prefix="/api/v1")
app.include_router(leaderboard_router, prefix="/api/v1")
app.include_router(stats_router, prefix="/api/v1")
