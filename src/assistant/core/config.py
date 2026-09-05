from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Enterprise RAG Assistant"
    app_version: str = "0.1.0"
    debug: bool = False

    # LLM_MODE controls whether we call a real LLM or return a mocked response.
    # Use "mock" locally and in CI to avoid burning quota.
    llm_mode: str = "mock"  # "mock" | "real"
    openai_api_key: str = ""
    # OpenAI-compatible endpoint (OpenAI default; override for Gemini, NVIDIA NIM, etc.)
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"

    # EMBED_MODE controls document/query embeddings (separate from LLM_MODE).
    embed_mode: str = "mock"  # "mock" | "api"
    embed_model: str = "text-embedding-004"
    embed_batch_size: int = 32

    erp_mode: str = "mock"  # "mock" | "odoo"
    mock_odoo_db_path: Path = _REPO_ROOT / "data" / "mock_odoo.sqlite"

    odoo_url: str = "http://localhost:8069"
    odoo_db: str = "odoo"
    odoo_username: str = "admin"
    odoo_password: str = "admin"

    # --- Storage (override in Docker via env / volumes) ---
    chroma_persist_dir: Path = Field(
        default=_REPO_ROOT / "data" / "processed" / "chroma",
        alias="CHROMA_PERSIST_DIR",
    )
    ingest_inbox_dir: Path = Field(
        default=_REPO_ROOT / "data" / "ingest" / "inbox",
        alias="INGEST_INBOX_DIR",
    )

    # --- Ingest queue (P5) ---
    ingest_mode: str = Field(default="sync", alias="INGEST_MODE")  # "sync" | "queue"
    redis_url: str = Field(default="", alias="REDIS_URL")


settings = Settings()
