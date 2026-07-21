"""
Application configuration.

All runtime settings are pulled from environment variables so the same
codebase can move between local dev, staging, and production without
code changes. See `.env.example` in the project root for the full list.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # --- Anthropic ---
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "claude-sonnet-4-6")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2048"))

    # --- Agent behavior ---
    MAX_AGENT_STEPS: int = int(os.getenv("MAX_AGENT_STEPS", "6"))
    JSON_RETRY_ATTEMPTS: int = int(os.getenv("JSON_RETRY_ATTEMPTS", "3"))

    # --- Server ---
    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

    # --- Mock mode ---
    # When no API key is configured, the backend automatically falls back
    # to a deterministic mock agent so the full stack can be demoed and
    # the frontend/backend contract can be exercised with zero setup.
    @property
    def MOCK_MODE(self) -> bool:
        return not bool(self.ANTHROPIC_API_KEY)


settings = Settings()
