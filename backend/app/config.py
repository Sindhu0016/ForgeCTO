from functools import lru_cache
from pathlib import Path
import os

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_ROOT_ENV = Path(__file__).resolve().parents[2] / ".env"
_BACKEND_ENV = Path(__file__).resolve().parents[1] / ".env"


class Settings(BaseSettings):
    """Loads API keys and runtime settings from the project root .env file."""

    model_config = SettingsConfigDict(
        env_file=(str(_ROOT_ENV), str(_BACKEND_ENV), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # auto | gemini | openai  (auto prefers Gemini when its key is set)
    llm_provider: str = "auto"
    openai_api_key: str = ""
    gemini_api_key: str = ""
    tavily_api_key: str = ""
    database_url: str = "postgresql+asyncpg://cto:cto@localhost:5432/cto_agent"
    github_token: str = ""
    github_repo: str = ""
    cors_origins: str = (
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:3000,http://127.0.0.1:3000"
    )
    rate_limit_per_minute: int = 10
    seed_on_startup: bool = True
    node_timeout_seconds: int = 120
    max_node_retries: int = 2
    # OpenAI models
    planner_model: str = "gpt-4o-mini"
    docs_model: str = "gpt-4o-mini"
    heavy_model: str = "gpt-4o"
    # Gemini models (free-tier friendly)
    gemini_planner_model: str = "gemini-2.0-flash"
    gemini_docs_model: str = "gemini-2.0-flash"
    gemini_heavy_model: str = "gemini-2.0-flash"

    @field_validator(
        "openai_api_key",
        "gemini_api_key",
        "tavily_api_key",
        "github_token",
        "llm_provider",
        mode="before",
    )
    @classmethod
    def strip_quotes(cls, v: object) -> object:
        if isinstance(v, str):
            return v.strip().strip('"').strip("'")
        return v

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @staticmethod
    def _is_real_key(key: str, placeholders: set[str]) -> bool:
        key = (key or "").strip()
        if not key or len(key) < 20:
            return False
        lowered = key.lower()
        if lowered in placeholders:
            return False
        for prefix in ("sk-your", "your-", "changeme", "paste_"):
            if lowered.startswith(prefix):
                return False
        return True

    @property
    def openai_configured(self) -> bool:
        return self._is_real_key(
            self.openai_api_key,
            {"sk-placeholder", "your-openai-key", "changeme"},
        )

    @property
    def gemini_configured(self) -> bool:
        return self._is_real_key(
            self.gemini_api_key,
            {"your-gemini-key", "changeme", "aiza-your-key"},
        )

    @property
    def active_llm_provider(self) -> str | None:
        """Resolved provider used for live agent runs."""
        pref = (self.llm_provider or "auto").lower()
        if pref == "gemini":
            return "gemini" if self.gemini_configured else None
        if pref == "openai":
            return "openai" if self.openai_configured else None
        # auto: prefer free Gemini, then OpenAI
        if self.gemini_configured:
            return "gemini"
        if self.openai_configured:
            return "openai"
        return None

    @property
    def llm_configured(self) -> bool:
        return self.active_llm_provider is not None


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if settings.openai_configured:
        os.environ["OPENAI_API_KEY"] = settings.openai_api_key
    if settings.gemini_configured:
        os.environ["GOOGLE_API_KEY"] = settings.gemini_api_key
        os.environ["GEMINI_API_KEY"] = settings.gemini_api_key
    if settings.tavily_api_key:
        os.environ["TAVILY_API_KEY"] = settings.tavily_api_key
    return settings


def reload_settings() -> Settings:
    get_settings.cache_clear()
    return get_settings()
