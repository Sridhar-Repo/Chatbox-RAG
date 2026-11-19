from app.models import Turn
from app.services.retrieval import build_search_query, select_hits
from tests.fakes import hit


def test_weak_best_chunk_means_refuse():
    assert select_hits([hit(score=0.28), hit(score=0.2)], 0.40, 0.25) == []


def test_no_hits():
    assert select_hits([], 0.40, 0.25) == []


def test_keeps_only_chunks_near_the_best_one():
    hits = [hit(score=0.65), hit(score=0.41), hit(score=0.38), hit(score=0.34)]
    kept = select_hits(hits, 0.40, 0.25)
    assert [h.score for h in kept] == [0.65, 0.41]


def test_unsorted_input_is_handled():
    kept = select_hits([hit(score=0.5), hit(score=0.9)], 0.40, 0.25)
    assert kept[0].score == 0.9


def test_short_followup_borrows_previous_question():
    history = [Turn("user", "How does the pricing plan work?"), Turn("assistant", "It is monthly.")]
    assert "pricing plan" in build_search_query("and the cost?", history)


def test_long_question_is_left_alone():
    q = "What is the notice period for termination of employment?"
    assert build_search_query(q, [Turn("user", "earlier")]) == q
