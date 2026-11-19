"""In-memory stand-ins so tests need no Chroma, no model download and no LLM server."""
from app.llm.base import Usage
from app.models import Chunk, DocumentInfo, Hit


class FakeStore:
    def __init__(self, hits: list[Hit] | None = None):
        self.docs: dict[str, list[Chunk]] = {}
        self.fixed_hits = hits          # if set, search() ignores content and returns these
        self.queries: list[str] = []

    def add_document(self, name, chunks):
        self.docs[name] = list(chunks)
        return len(chunks)

    def delete_document(self, name):
        self.docs.pop(name, None)

    def list_documents(self):
        return [DocumentInfo(n, len(c)) for n, c in sorted(self.docs.items())]

    def search(self, query, k):
        self.queries.append(query)
        if self.fixed_hits is not None:
            return self.fixed_hits[:k]
        words = set(query.lower().split())
        scored = [Hit(c, len(words & set(c.text.lower().split())) / max(1, len(words)))
                  for chunks in self.docs.values() for c in chunks]
        return sorted(scored, key=lambda h: h.score, reverse=True)[:k]


class FakeLLM:
    model = "fake-model"

    def __init__(self, tokens=("Remote work is ", "allowed [1]."), error: Exception | None = None):
        self.tokens, self.error, self.calls = tokens, error, []

    def stream(self, system, messages, usage: Usage):
        self.calls.append(messages)
        for t in self.tokens:
            yield t
        if self.error:
            raise self.error
        usage.input_tokens, usage.output_tokens = 10, 5


def hit(text="some text", score=0.8, source="a.txt", page=0) -> Hit:
    return Hit(Chunk(text, source, page), score)
