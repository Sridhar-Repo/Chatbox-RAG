from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import StreamingResponse
from starlette.concurrency import run_in_threadpool

from ..models import Turn
from ..services.chat import ChatService
from ..services.documents import DocumentService
from .deps import get_chat_service, get_document_service
from .schemas import ChatRequest
from .sse import encode_sse

router = APIRouter(prefix="/api")


@router.get("/docs")
def list_documents(svc: DocumentService = Depends(get_document_service)):
    return [{"name": d.name, "chunks": d.chunks} for d in svc.list()]


@router.post("/upload")
async def upload(file: UploadFile = File(...), svc: DocumentService = Depends(get_document_service)):
    data = await file.read()
    # Embedding is CPU-heavy; run it off the event loop so other requests keep working.
    chunks = await run_in_threadpool(svc.ingest, file.filename or "", data)
    return {"name": file.filename, "chunks": chunks}


@router.delete("/docs/{name}")
def delete_document(name: str, svc: DocumentService = Depends(get_document_service)):
    svc.delete(name)
    return {"ok": True}


@router.post("/chat")
def chat(req: ChatRequest, svc: ChatService = Depends(get_chat_service)):
    question = svc.check_question(req.question)  # fail with a proper 400 before streaming starts
    history = [Turn(t.role, t.content) for t in req.history]
    events = (encode_sse(e) for e in svc.answer(question, history))
    return StreamingResponse(events, media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
