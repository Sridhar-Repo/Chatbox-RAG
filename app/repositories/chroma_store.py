from ..models import Chunk, DocumentInfo, Hit


class ChromaVectorStore:
    """Chroma persisted on disk. It embeds text itself with all-MiniLM-L6-v2 (local, free)."""

    def __init__(self, path: str):
        import chromadb  # imported here so tests and tools that don't need Chroma can skip it

        client = chromadb.PersistentClient(path=path)
        self._col = client.get_or_create_collection("docs", metadata={"hnsw:space": "cosine"})

    def add_document(self, name: str, chunks: list[Chunk]) -> int:
        self.delete_document(name)  # re-uploading a file replaces it
        if not chunks:
            return 0
        self._col.add(
            ids=[f"{name}::{i}" for i in range(len(chunks))],
            documents=[c.text for c in chunks],
            metadatas=[{"source": c.source, "page": c.page} for c in chunks],
        )
        return len(chunks)

    def delete_document(self, name: str) -> None:
        self._col.delete(where={"source": name})

    def list_documents(self) -> list[DocumentInfo]:
        counts: dict[str, int] = {}
        for meta in self._col.get(include=["metadatas"])["metadatas"]:
            counts[meta["source"]] = counts.get(meta["source"], 0) + 1
        return [DocumentInfo(name, n) for name, n in sorted(counts.items())]

    def search(self, query: str, k: int) -> list[Hit]:
        total = self._col.count()
        if total == 0:
            return []
        res = self._col.query(query_texts=[query], n_results=min(k, total))
        return [
            Hit(Chunk(text, meta["source"], meta["page"]), score=round(1 - dist, 4))
            for text, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0])
        ]
