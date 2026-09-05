from datetime import date
from typing import Any
from pydantic import BaseModel, Field

class CopilotRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    language: str = "English"
    store_id: int | None = None

class CopilotResponse(BaseModel):
    intent: str
    answer: str
    numbers: list[dict[str, Any]]
    calculation: str
    data_period: str
    assumptions: list[str]
    data_sufficiency: str
    details: list[dict[str, Any]] = []

class TranslateRequest(BaseModel):
    text: str
    language: str
