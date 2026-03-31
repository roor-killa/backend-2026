

from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    question: str
    session_id: Optional[int] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "question": "Quels sont les délais de livraison mentionnés dans le contrat ?",
                "session_id": None
            }
        }
    }

class ChatResponse(BaseModel):
    session_id: int
    answer: str
    sources: List[str]
    chunks_used: int