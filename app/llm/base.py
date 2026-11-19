from dataclasses import dataclass
from typing import Iterator, Protocol


class LLMError(Exception):
    """Anything that went wrong talking to the model. The message is safe to show the user."""


class ModelNotFound(LLMError):
    pass


class LLMUnavailable(LLMError):
    pass


@dataclass
class Usage:
    input_tokens: int | None = None
    output_tokens: int | None = None


class LLMClient(Protocol):
    model: str

    def stream(self, system: str, messages: list[dict], usage: Usage) -> Iterator[str]:
        """Yield text pieces as they are generated; fill `usage` when the model reports it."""
        ...
