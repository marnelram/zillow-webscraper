"""Runtime settings loaded from environment / .env.

Secrets and model choices live here; user *preferences* (budget, weights) live in
``preferences.yaml`` and are loaded by :mod:`aptagent.config`.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="",
    )

    # Database
    neon_database_url: str = ""

    # OpenRouter LLM funnel
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    aptagent_model_cheap: str = "openai/gpt-4o-mini"
    aptagent_model_strong: str = "anthropic/claude-sonnet-4"

    # Telegram
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # Census
    census_api_key: str = ""

    # ScraperAPI (unblocks Zillow's anti-bot for the live fetcher)
    scraperapi_key: str = ""

    # Apify (managed Zillow scraper actor — handles anti-bot/proxies)
    apify_token: str = ""
    apify_zillow_actor: str = "maxcopell~zillow-scraper"

    @property
    def sqlalchemy_url(self) -> str:
        """Return the connection string with the psycopg (v3) driver for SQLAlchemy."""
        url = self.neon_database_url
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url


_settings: Settings | None = None


def get_settings() -> Settings:
    """Return a cached Settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
