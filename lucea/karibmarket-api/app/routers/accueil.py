from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def root():
    return {"message": "Bienvenue sur l'API KaribMarket"}