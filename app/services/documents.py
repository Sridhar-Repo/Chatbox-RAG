from pathlib import Path

from ..config import Settings
from ..models import Chunk, DocumentInfo
from ..repositories.base import VectorStore
from .chunking import chunk_text
from .errors import EmptyDocument, FileTooLarge, UnreadableFile, UnsupportedFileType
from .extraction import extract_pages


class DocumentService:
    """Upload, list and delete documents. Knows nothing about HTTP or about which database is used."""

    def __init__(self, store: VectorStore, settings: Settings):
        self._store = store
        self._s = settings

    def ingest(self, filename: str, data: bytes) -> int:
        name = Path(filename).name  # drop any folder parts a client might send
        if Path(name).suffix.lower() not in self._s.allowed_ext:
            raise UnsupportedFileType("Only PDF, TXT and MD files are supported.")
        if len(data) > self._s.max_upload_mb * 1024 * 1024:
            raise FileTooLarge(f"File is larger than {self._s.max_upload_mb} MB.")
        try:
            pages = extract_pages(name, data)
        except Exception as exc:
            raise UnreadableFile("Couldn't read that file. Is it corrupted or password-protected?") from exc

        chunks = [
            Chunk(piece, name, page or 0)
            for page, text in pages
            for piece in chunk_text(text, self._s.chunk_size, self._s.chunk_overlap)
        ]
        if not chunks:
            raise EmptyDocument("No text found. Scanned PDFs need OCR first.")
        return self._store.add_document(name, chunks)

    def list(self) -> list[DocumentInfo]:
        return self._store.list_documents()

    def delete(self, name: str) -> None:
        self._store.delete_document(name)
