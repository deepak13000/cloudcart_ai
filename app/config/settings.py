import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """
    Central configuration for CloudCart AI system
    """

    # ── ENVIRONMENT ─────────────────────────────────────────────
    ENV: str = os.getenv("ENV", "development")

    # ── GEMINI CONFIG ───────────────────────────────────────────
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    GEMINI_MODEL_FALLBACKS: list[str] = [
        model.strip()
        for model in os.getenv(
            "GEMINI_MODEL_FALLBACKS",
            "gemini-2.5-flash,gemini-2.0-flash,gemini-1.5-flash",
        ).split(",")
        if model.strip()
    ]
    GEMINI_TEMPERATURE: float = float(os.getenv("GEMINI_TEMPERATURE", 0))

    # ── SECURITY LIMITS ─────────────────────────────────────────
    MAX_INPUT_LENGTH: int = int(os.getenv("MAX_INPUT_LENGTH", 500))
    MIN_INPUT_LENGTH: int = int(os.getenv("MIN_INPUT_LENGTH", 2))

    # ── PROMPT CONFIG ───────────────────────────────────────────
    PROMPT_DIR: str = os.getenv("PROMPT_DIR", "prompts")
    CURRENT_PROMPT_FILE: str = os.getenv("CURRENT_PROMPT_FILE", "current.yaml")

    # ── FEATURE FLAGS ───────────────────────────────────────────
    ENABLE_INPUT_VALIDATION: bool = os.getenv("ENABLE_INPUT_VALIDATION", "true").lower() == "true"
    ENABLE_OUTPUT_VALIDATION: bool = os.getenv("ENABLE_OUTPUT_VALIDATION", "true").lower() == "true"

    # ── LOGGING ─────────────────────────────────────────────────
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


# Singleton instance
settings = Settings()