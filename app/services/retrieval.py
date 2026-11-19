from ..models import Hit, Turn


def select_hits(hits: list[Hit], min_best_score: float, relative_window: float) -> list[Hit]:
    """The relevance guard.

    1. If even the best chunk is weak, return nothing (the caller then refuses without asking the LLM).
    2. Otherwise keep only chunks close to the best one, so a strong answer isn't padded
       with five loosely-related passages.
    """
    ranked = sorted(hits, key=lambda h: h.score, reverse=True)
    if not ranked or ranked[0].score < min_best_score:
        return []
    floor = ranked[0].score - relative_window
    return [h for h in ranked if h.score >= floor]


def build_search_query(question: str, history: list[Turn]) -> str:
    """Short follow-ups ("and the cost?") search badly alone, so borrow the previous user question."""
    if len(question.split()) < 6:
        previous = [t.content for t in history if t.role == "user"]
        if previous:
            return f"{previous[-1]} {question}"
    return question
