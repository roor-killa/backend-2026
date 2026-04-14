from pydantic import BaseModel, Field


class ScoreSubmitRequest(BaseModel):
    user_id: int
    value: int = Field(ge=0)
    combo_max: int = Field(ge=0)


class ScoreItem(BaseModel):
    username: str
    score: int
