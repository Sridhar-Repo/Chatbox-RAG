import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """All tunables in one place. Defaults here; override with environment variables."""

    data_dir: str = "./data"
    frontend_dist: str = "frontend/dist"

    # Any OpenAI-compatible endpoint works. Default: Ollama on this machine (free, local).
    llm_base_url: str = "http://localhost:11434/v1"
    llm_model: str = "llama3.2"
    llm_api_key: str = "ollama"  # Ollama ignores it; hosted free tiers need a real one

    # Retrieval + relevance guard (scores are cosine similarity, 0..1, higher = closer).
    top_k: int = 5
    min_best_score: float = 0.40   # refuse if even the best chunk is below this
    relative_window: float = 0.25  # keep only chunks within this distance of the best one

    chunk_size: int = 800
    chunk_overlap: int = 100
    max_upload_mb: int = 10
    max_question_chars: int = 1000
    history_turns: int = 6
    allowed_ext: tuple[str, ...] = (".pdf", ".txt", ".md")

    @classmethod
    def from_env(cls) -> "Settings":
        e = os.getenv
        return cls(
            data_dir=e("DATA_DIR", cls.data_dir),
            frontend_dist=e("FRONTEND_DIST", cls.frontend_dist),
            llm_base_url=e("LLM_BASE_URL", cls.llm_base_url).rstrip("/"),
            llm_model=e("LLM_MODEL", cls.llm_model),
            llm_api_key=e("LLM_API_KEY", cls.llm_api_key),
            top_k=int(e("TOP_K", cls.top_k)),
            min_best_score=float(e("MIN_BEST_SCORE", cls.min_best_score)),
            relative_window=float(e("RELATIVE_WINDOW", cls.relative_window)),
            chunk_size=int(e("CHUNK_SIZE", cls.chunk_size)),
            chunk_overlap=int(e("CHUNK_OVERLAP", cls.chunk_overlap)),
            max_upload_mb=int(e("MAX_UPLOAD_MB", cls.max_upload_mb)),
        )
