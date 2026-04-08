from datetime import datetime
from pydantic import BaseModel
from typing import List


class DocumentOut(BaseModel):
    id: int
    user_id: int
    filename: str
    original_name: str
    file_type: str | None = None
    file_size: int | None = None
    source: str
    drive_file_id: str | None = None
    is_indexed: bool
    chunk_count: int
    collection_name: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


class DocumentListOut(BaseModel):
    count: int
    documents: List[DocumentOut]
