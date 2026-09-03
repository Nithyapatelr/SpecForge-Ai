"""
SpecForge AI configuration.

Loads environment variables using pydantic-settings BaseSettings.
Copy .env.example to .env and fill in your values before running.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Anthropic API key — required for classification and LLM ambiguity scoring
    anthropic_api_key: str = ""

    # SQLAlchemy database URL.
    # Defaults to a local SQLite file so the project runs with zero setup.
    database_url: str = "sqlite:///./data/specforge.db"

    # Claude model to use for API calls
    anthropic_model: str = "claude-sonnet-4-6"

    # If True, the segmenter will call the LLM for ambiguous compound-sentence
    # splits. Keep False in CI/testing so no API key is required.
    use_llm_segmentation: bool = False

    # Base URL of the running FastAPI service (used by the Streamlit dashboard)
    api_base_url: str = "http://localhost:8000"


# Module-level singleton — import `settings` everywhere instead of re-instantiating.
settings = Settings()
