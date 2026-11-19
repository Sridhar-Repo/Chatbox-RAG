from evals.run import evaluate
from app.models import Chunk
from tests.fakes import FakeStore

DATA = [
    {"q": "remote days allowed", "expect": ["three days"]},
    {"q": "capital of france", "expect": None},
]


def store():
    s = FakeStore()
    s.add_document("p.md", [Chunk("remote days allowed is three days a week", "p.md")])
    return s


def test_counts_recall_and_refusals():
    r = evaluate(store(), DATA, k=5, min_best=0.4, window=0.25)
    assert r == {"recall": 1.0, "refused": 1.0}


def test_too_strict_threshold_hurts_recall():
    r = evaluate(store(), DATA, k=5, min_best=1.01, window=0.25)
    assert r["recall"] == 0.0
