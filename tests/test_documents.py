import pytest

from app.config import Settings
from app.services.documents import DocumentService
from app.services.errors import EmptyDocument, FileTooLarge, UnsupportedFileType
from tests.fakes import FakeStore


def make(**overrides):
    store = FakeStore()
    return store, DocumentService(store, Settings(**overrides))


def test_ingest_text_file():
    store, svc = make()
    assert svc.ingest("notes.md", b"First paragraph.\n\nSecond paragraph.") >= 1
    assert [d.name for d in svc.list()] == ["notes.md"]


def test_rejects_unknown_extension():
    _, svc = make()
    with pytest.raises(UnsupportedFileType):
        svc.ingest("virus.exe", b"x")


def test_rejects_big_file():
    _, svc = make(max_upload_mb=1)
    with pytest.raises(FileTooLarge):
        svc.ingest("big.txt", b"x" * (1024 * 1024 + 1))


def test_rejects_empty_text():
    _, svc = make()
    with pytest.raises(EmptyDocument):
        svc.ingest("empty.txt", b"   \n\n  ")


def test_folder_parts_in_filename_are_dropped():
    store, svc = make()
    svc.ingest("../../etc/notes.txt", b"hello there")
    assert list(store.docs) == ["notes.txt"]


def test_reupload_replaces_and_delete_removes():
    store, svc = make()
    svc.ingest("a.txt", b"old text")
    svc.ingest("a.txt", b"new text")
    assert store.docs["a.txt"][0].text == "new text"
    svc.delete("a.txt")
    assert svc.list() == []
