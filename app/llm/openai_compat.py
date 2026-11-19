import json
from typing import Iterable, Iterator

import httpx

from .base import LLMError, LLMUnavailable, ModelNotFound, Usage


def parse_stream(lines: Iterable[str], usage: Usage) -> Iterator[str]:
    """Read an OpenAI-style server-sent-event stream and yield the text pieces."""
    for line in lines:
        if not line.startswith("data: "):
            continue
        data = line[6:]
        if data == "[DONE]":
            return
        chunk = json.loads(data)
        if chunk.get("usage"):
            usage.input_tokens = chunk["usage"].get("prompt_tokens")
            usage.output_tokens = chunk["usage"].get("completion_tokens")
        for choice in chunk.get("choices", []):
            text = choice.get("delta", {}).get("content")
            if text:
                yield text


class OpenAICompatClient:
    """Works with Ollama, LM Studio, Groq, OpenRouter... anything speaking /chat/completions."""

    def __init__(self, base_url: str, model: str, api_key: str = "ollama",
                 timeout: float = 120.0, max_tokens: int = 800, temperature: float = 0.2):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._headers = {"Authorization": f"Bearer {api_key}"}
        self._timeout = timeout
        self._max_tokens = max_tokens
        self._temperature = temperature

    def stream(self, system: str, messages: list[dict], usage: Usage) -> Iterator[str]:
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system}] + messages,
            "stream": True,
            "max_tokens": self._max_tokens,
            "temperature": self._temperature,  # low = stick to the excerpts
            "stream_options": {"include_usage": True},
        }
        try:
            with httpx.stream("POST", f"{self.base_url}/chat/completions", json=payload,
                              headers=self._headers, timeout=self._timeout) as r:
                if r.status_code != 200:
                    r.read()
                    self._raise_for_status(r.status_code, r.text)
                yield from parse_stream(r.iter_lines(), usage)
        except httpx.ConnectError as exc:
            raise LLMUnavailable(
                f"Can't reach the model at {self.base_url}. "
                f"If you use Ollama, start it and run: ollama pull {self.model}") from exc
        except httpx.TimeoutException as exc:
            raise LLMError("The model took too long to respond. Try a smaller model.") from exc
        except httpx.HTTPError as exc:
            raise LLMError(f"Network error while talking to the model: {exc}") from exc

    def _raise_for_status(self, status: int, body: str) -> None:
        if status == 404:
            raise ModelNotFound(
                f"Model '{self.model}' isn't installed. If you use Ollama, run: ollama pull {self.model}")
        raise LLMError(f"The model server returned {status}: {body[:200]}")
