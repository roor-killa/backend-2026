from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.config import settings
import httpx

router = APIRouter(tags=["Chatbot"])


class ChatbotRequest(BaseModel):
    question: str
    territory: Optional[str] = None
    provider: str = "ollama"
    model: str = "llama3"


class ChatbotResponse(BaseModel):
    answer: str
    provider: Optional[str] = None
    intent: Optional[str] = None


@router.post("/chatbot", response_model=ChatbotResponse)
def chatbot(req: ChatbotRequest):
    """Proxy vers le service scraper-api qui exécute le RAG hybride Kiprix."""
    try:
        with httpx.Client(timeout=120) as client:
            res = client.post(
                f"{settings.SCRAPER_API_URL}/chat",
                json=req.model_dump(),
            )
            res.raise_for_status()
            return res.json()
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Service chatbot indisponible (scraper-api)")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Timeout — le LLM met trop de temps à répondre")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
