import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .api.errors import domain_error_handler
from .api.routes import router
from .config import Settings
from .llm.base import LLMClient
from .llm.openai_compat import OpenAICompatClient
from .repositories.base import VectorStore
from .repositories.chroma_store import ChromaVectorStore
from .services.chat import ChatService
from .services.documents import DocumentService
from .services.errors import DomainError


def create_app(settings: Settings | None = None, store: VectorStore | None = None,
               llm: LLMClient | None = None) -> FastAPI:
    """App factory. Dependencies are built here and passed in, so tests can swap in fakes.

    Run with:  uvicorn app.main:create_app --factory
    """
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
    settings = settings or Settings.from_env()
    store = store if store is not None else ChromaVectorStore(settings.data_dir)
    llm = llm if llm is not None else OpenAICompatClient(
        settings.llm_base_url, settings.llm_model, settings.llm_api_key)

    app = FastAPI(title="Chat with your docs")
    app.state.documents = DocumentService(store, settings)
    app.state.chat = ChatService(store, llm, settings)
    app.add_exception_handler(DomainError, domain_error_handler)
    app.include_router(router)

    @app.get("/health")
    def health():
        return {"ok": True}

    dist = Path(settings.frontend_dist)
    if dist.is_dir():  # production: serve the built React app from the same container
        app.mount("/", StaticFiles(directory=dist, html=True), name="web")
    else:
        @app.get("/")
        def no_frontend():
            return {"message": "API is running. Start the UI with: cd frontend && npm run dev"}

    return app
