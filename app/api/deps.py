from fastapi import Request

from ..services.chat import ChatService
from ..services.documents import DocumentService


def get_document_service(request: Request) -> DocumentService:
    return request.app.state.documents


def get_chat_service(request: Request) -> ChatService:
    return request.app.state.chat
