import json
import logging
import time
from typing import Iterator

from ..config import Settings
from ..llm.base import LLMClient, LLMError, Usage
from ..models import ChatEvent, Hit, Turn
from ..repositories.base import VectorStore
from .errors import InvalidQuestion
from .prompts import NO_ANSWER, SYSTEM_PROMPT, build_messages
from .retrieval import build_search_query, select_hits

log = logging.getLogger("docchat.chat")


def _ms(since: float) -> int:
    return int((time.perf_counter() - since) * 1000)


class ChatService:
    """Retrieve -> guard -> prompt -> stream. Emits ChatEvents; knows nothing about HTTP."""

    def __init__(self, store: VectorStore, llm: LLMClient, settings: Settings):
        self._store = store
        self._llm = llm
        self._s = settings

    def check_question(self, question: str) -> str:
        q = question.strip()
        if not q:
            raise InvalidQuestion("Ask a question first.")
        if len(q) > self._s.max_question_chars:
            raise InvalidQuestion(f"Keep questions under {self._s.max_question_chars} characters.")
        return q

    def _retrieve(self, question: str, history: list[Turn]) -> tuple[list[Hit], list[Hit]]:
        raw = self._store.search(build_search_query(question, history), self._s.top_k)
        return raw, select_hits(raw, self._s.min_best_score, self._s.relative_window)

    def answer(self, question: str, history: list[Turn]) -> Iterator[ChatEvent]:
        t0 = time.perf_counter()
        raw, hits = self._retrieve(question, history)
        top_raw = max((h.score for h in raw), default=None)

        yield ChatEvent("sources", hits)  # sent first so the UI can show evidence while the answer streams

        if not hits:  # guardrail: nothing relevant enough, don't even call the LLM
            log.info(json.dumps({"event": "chat", "llm_called": False, "kept": 0, "top_score": top_raw}))
            yield ChatEvent("token", NO_ANSWER)
            yield ChatEvent("done")
            return

        messages = build_messages(history[-self._s.history_turns:], question, hits)
        usage, first_token_ms = Usage(), None
        try:
            for text in self._llm.stream(SYSTEM_PROMPT, messages, usage):
                if first_token_ms is None:
                    first_token_ms = _ms(t0)
                yield ChatEvent("token", text)
        except LLMError as exc:
            log.warning("llm error: %s", exc)
            yield ChatEvent("error", str(exc))
        except Exception:
            log.exception("unexpected failure while answering")
            yield ChatEvent("error", "Something went wrong while answering.")
        else:
            log.info(json.dumps({
                "event": "chat", "llm_called": True, "model": self._llm.model, "kept": len(hits),
                "top_score": top_raw, "first_token_ms": first_token_ms, "total_ms": _ms(t0),
                "input_tokens": usage.input_tokens, "output_tokens": usage.output_tokens,
            }))
        yield ChatEvent("done")
