from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
import os

router = APIRouter(
    prefix="/chatbot",
    tags=["Chatbot RAG"]
)

SCRAPER_PATH = os.environ.get("SCRAPER_PATH", "/Users/user/Documents/poo-2026/groupe_scp2")
PYTHON_BIN = os.environ.get("SCRAPER_PYTHON", "/Users/user/Documents/poo-2026/groupe_scp2/venv/bin/python")


class ChatRequest(BaseModel):
    question: str
    territory: Optional[str] = None
    provider: str = "ollama"
    model: str = "llama3"


class ChatResponse(BaseModel):
    answer: str
    provider: Optional[str] = None
    sources: list = []
    intent: Optional[str] = None


@router.post("", response_model=ChatResponse)
async def ask_chatbot(payload: ChatRequest):
    """Pose une question au RAG Kiprix hybride."""

    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="La question ne peut pas être vide")

    try:
        # Ajouter le projet scraper au path Python
        if SCRAPER_PATH not in sys.path:
            sys.path.insert(0, SCRAPER_PATH)

        from src.rag.hybrid_rag import HybridRAGEngine

        engine = HybridRAGEngine(
            llm_provider=payload.provider,
            model=payload.model
        )

        result = engine.ask(
            question=payload.question,
            territory=payload.territory
        )

        return ChatResponse(
            answer=result.get("answer", "Aucune réponse générée."),
            provider=result.get("provider"),
            sources=result.get("sources", []),
            intent=result.get("intent")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def chatbot_health():
    """Vérifie que le RAG est disponible."""
    try:
        if SCRAPER_PATH not in sys.path:
            sys.path.insert(0, SCRAPER_PATH)

        from src.rag.rag_database import RAGDatabase
        db = RAGDatabase()
        count = db.count_embeddings()
        return {"status": "ok", "embeddings": count}
    except Exception as e:
        return {"status": "error", "details": str(e)}