import pytest

from app.config import Settings
from app.llm.base import LLMUnavailable
from app.models import Turn
from app.services.chat import ChatService
from app.services.errors import InvalidQuestion
from app.services.prompts import NO_ANSWER
from tests.fakes import FakeLLM, FakeStore, hit


def run(store, llm, question="How many remote days are allowed per week?", history=None):
    svc = ChatService(store, llm, Settings())
    return list(svc.answer(question, history or []))


def types(events):
    return [e.type for e in events]


def test_streams_sources_first_then_tokens_then_done():
    events = run(FakeStore([hit(score=0.8)]), FakeLLM())
    assert types(events) == ["sources", "token", "token", "done"]
    assert len(events[0].data) == 1


def test_refuses_without_calling_llm_when_best_chunk_is_weak():
    llm = FakeLLM()
    events = run(FakeStore([hit(score=0.28)]), llm)
    assert llm.calls == []
    assert events[0].data == []
    assert events[1].data == NO_ANSWER


def test_refuses_when_store_is_empty():
    llm = FakeLLM()
    events = run(FakeStore([]), llm)
    assert llm.calls == [] and events[1].data == NO_ANSWER


def test_excerpts_go_only_into_the_latest_message():
    llm = FakeLLM()
    history = [Turn("user", "earlier question"), Turn("assistant", "earlier answer")]
    run(FakeStore([hit("policy text", 0.8)]), llm, history=history)
    sent = llm.calls[0]
    assert "policy text" in sent[-1]["content"]
    assert "policy text" not in sent[0]["content"]


def test_llm_failure_becomes_error_event_with_helpful_text():
    llm = FakeLLM(tokens=(), error=LLMUnavailable("Can't reach the model. Start Ollama."))
    events = run(FakeStore([hit()]), llm)
    assert types(events) == ["sources", "error", "done"]
    assert "Ollama" in events[1].data


def test_question_validation():
    svc = ChatService(FakeStore(), FakeLLM(), Settings())
    with pytest.raises(InvalidQuestion):
        svc.check_question("   ")
    with pytest.raises(InvalidQuestion):
        svc.check_question("x" * 2000)
    assert svc.check_question("  hi  ") == "hi"
