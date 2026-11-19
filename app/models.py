"""Plain data types shared by every layer. No framework imports here."""
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Chunk:
    text: str
    source: str
    page: int = 0  # 0 = no page info (txt/md)


@dataclass(frozen=True)
class Hit:
    chunk: Chunk
    score: float  # cosine similarity, 0..1


@dataclass(frozen=True)
class DocumentInfo:
    name: str
    chunks: int


@dataclass(frozen=True)
class Turn:
    role: str  # "user" | "assistant"
    content: str


@dataclass(frozen=True)
class ChatEvent:
    """What the chat service emits. The API layer decides how to put it on the wire."""
    type: str  # "sources" | "token" | "error" | "done"
    data: Any = None
