from typing import Literal

from pydantic import BaseModel, Field


class TurnIn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=4000)


class ChatRequest(BaseModel):
    question: str
    history: list[TurnIn] = Field(default_factory=list, max_length=20)
