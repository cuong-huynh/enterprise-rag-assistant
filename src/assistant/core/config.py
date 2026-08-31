from pathlib import Path

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

    erp_mode: str = "mock"  # "mock" | "odoo"
    mock_odoo_db_path: Path = _REPO_ROOT / "data" / "mock_odoo.sqlite"


settings = Settings()
