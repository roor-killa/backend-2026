

import json
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator
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


class ChatSessionResponse(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatMessageResponse(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    sources: List[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("sources", mode="before")
    @classmethod
    def parse_sources(cls, value):
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return [str(item) for item in parsed]
            except json.JSONDecodeError:
                pass
        return []