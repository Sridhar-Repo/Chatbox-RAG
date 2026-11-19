import json

from app.llm.base import Usage
from app.llm.openai_compat import parse_stream


def line(obj):
    return "data: " + json.dumps(obj)


def test_parses_text_and_usage_and_stops_at_done():
    usage = Usage()
    lines = [
        ": keep-alive",
        line({"choices": [{"delta": {"content": "Hi "}}]}),
        line({"choices": [{"delta": {}}]}),
        line({"choices": [{"delta": {"content": "there"}}]}),
        line({"choices": [], "usage": {"prompt_tokens": 7, "completion_tokens": 2}}),
        "data: [DONE]",
        line({"choices": [{"delta": {"content": "ignored"}}]}),
    ]
    assert "".join(parse_stream(lines, usage)) == "Hi there"
    assert (usage.input_tokens, usage.output_tokens) == (7, 2)
