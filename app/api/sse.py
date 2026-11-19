import json

from ..models import ChatEvent, Hit


def _source(n: int, hit: Hit) -> dict:
    return {"n": n, "source": hit.chunk.source, "page": hit.chunk.page,
            "text": hit.chunk.text, "score": round(hit.score, 2)}


def encode_sse(event: ChatEvent) -> str:
    data = [_source(i, h) for i, h in enumerate(event.data, 1)] if event.type == "sources" else event.data
    return f"data: {json.dumps({'type': event.type, 'data': data})}\n\n"
