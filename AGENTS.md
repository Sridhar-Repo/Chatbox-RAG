# Rules for AI coding assistants working in this repo

Read this before changing code. These rules exist because assistants tend to take the shortest path, which erodes structure.

## Architecture (do not break)
- `api/` handles HTTP only: parse request, call a service, encode the response. No business logic.
- `services/` holds the logic. They take their dependencies (store, LLM, settings) in the constructor.
- `repositories/` and `llm/` wrap external systems behind the small interfaces in `base.py`.
- No module-level mutable state. Build things in `create_app()` and pass them in.
- Dependencies point downward: api → services → repositories/llm. Never the reverse.

## Do
- Add or update a test with every behaviour change. Use `tests/fakes.py`, not real Chroma or a real LLM.
- Keep functions small and typed. Prefer plain Python to a new dependency.
- Change thresholds only after running `python -m evals.run` and reading the numbers.
- Show the user-facing error text a person can act on (what happened + what to do).

## Don't
- Don't add a framework (LangChain etc.) without a written reason in the README.
- Don't commit `data/`, `.env`, uploaded documents or `node_modules`.
- Don't rewrite files wholesale to make a small change.
- Don't claim something works unless a test or a run showed it.

## Checks before finishing
`pytest` · `python -m evals.run` (if retrieval changed) · `cd frontend && npm test && npm run build`
