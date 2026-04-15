from app.routers.players import router as players_router
from app.routers.games   import router as games_router
from app.routers.shots   import router as shots_router

__all__ = ["players_router", "games_router", "shots_router"]
