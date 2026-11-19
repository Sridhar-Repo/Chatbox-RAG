"""Retrieval + guard evaluation. No LLM needed.

    python -m evals.run                    # uses sample_docs/ and evals/dataset.jsonl
    python -m evals.run --docs my_docs/ --data my_questions.jsonl

For every threshold it reports:
  recall   - of the answerable questions, how many had the answer text in the chunks we kept
  refused  - of the unanswerable questions, how many we correctly refused (higher = safer)
Pick the threshold where both are acceptable. Add your own documents and questions to make it meaningful.
"""
import argparse
import json
import tempfile
from pathlib import Path

from app.config import Settings
from app.repositories.base import VectorStore
from app.services.retrieval import select_hits


def evaluate(store: VectorStore, dataset: list[dict], k: int, min_best: float, window: float) -> dict:
    found = answerable = refused = unanswerable = 0
    for item in dataset:
        kept = select_hits(store.search(item["q"], k), min_best, window)
        if item["expect"] is None:
            unanswerable += 1
            refused += not kept
        else:
            answerable += 1
            text = " ".join(h.chunk.text.lower() for h in kept)
            found += any(kw.lower() in text for kw in item["expect"])
    return {
        "recall": found / answerable if answerable else None,
        "refused": refused / unanswerable if unanswerable else None,
    }


def main() -> None:
    from app.repositories.chroma_store import ChromaVectorStore
    from app.services.documents import DocumentService

    ap = argparse.ArgumentParser()
    ap.add_argument("--docs", default="sample_docs")
    ap.add_argument("--data", default="evals/dataset.jsonl")
    args = ap.parse_args()

    settings = Settings()
    with tempfile.TemporaryDirectory() as tmp:  # throwaway index, never touches ./data
        store = ChromaVectorStore(tmp)
        svc = DocumentService(store, settings)
        for f in sorted(Path(args.docs).iterdir()):
            if f.suffix.lower() in settings.allowed_ext:
                svc.ingest(f.name, f.read_bytes())
        dataset = [json.loads(line) for line in Path(args.data).read_text().splitlines() if line.strip()]

        print("\nBest chunk score per question (what the guard sees):")
        for item in dataset:
            hits = store.search(item["q"], settings.top_k)
            best = max((h.score for h in hits), default=0)
            kind = "answerable  " if item["expect"] else "unanswerable"
            print(f"  {best:.2f}  {kind}  {item['q']}")

        print(f"\n{'min_best':>8}  {'recall':>7}  {'refused':>8}")
        for t in (0.20, 0.30, 0.35, 0.40, 0.45, 0.50, 0.60):
            r = evaluate(store, dataset, settings.top_k, t, settings.relative_window)
            print(f"{t:>8.2f}  {r['recall']:>7.0%}  {r['refused']:>8.0%}")


if __name__ == "__main__":
    main()
