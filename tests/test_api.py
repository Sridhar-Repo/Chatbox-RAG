import json

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from app.config import Settings  # noqa: E402
from app.main import create_app  # noqa: E402
from tests.fakes import FakeLLM, FakeStore  # noqa: E402


def make_client():
    app = create_app(Settings(frontend_dist="does-not-exist"), store=FakeStore(), llm=FakeLLM())
    return TestClient(app)


def read_events(response):
    return [json.loads(f[6:]) for f in response.text.split("\n\n") if f.startswith("data: ")]


def test_health():
    assert make_client().get("/health").json() == {"ok": True}


def test_upload_list_chat_delete_round_trip():
    c = make_client()
    r = c.post("/api/upload", files={"file": ("policy.txt", b"remote days allowed per week is three")})
    assert r.status_code == 200
    assert c.get("/api/docs").json() == [{"name": "policy.txt", "chunks": 1}]

    r = c.post("/api/chat", json={"question": "how many remote days allowed per week"})
    kinds = [e["type"] for e in read_events(r)]
    assert kinds[0] == "sources" and kinds[-1] == "done" and "token" in kinds
    assert read_events(r)[0]["data"][0]["source"] == "policy.txt"

    c.delete("/api/docs/policy.txt")
    assert c.get("/api/docs").json() == []


def test_bad_extension_is_400_with_message():
    r = make_client().post("/api/upload", files={"file": ("virus.exe", b"x")})
    assert r.status_code == 400 and "PDF" in r.json()["detail"]


def test_empty_question_is_400():
    assert make_client().post("/api/chat", json={"question": "  "}).status_code == 400
