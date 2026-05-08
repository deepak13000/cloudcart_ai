from pydantic import BaseModel, field_validator

from app.config.settings import settings
from app.utils.security import detect_prompt_injection, sanitize_input


class CloudCartInput(BaseModel):
    """
    Pydantic model that sanitises and validates every user query
    before it reaches the LLM.
    """

    user_query: str

    @field_validator("user_query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        # 1. Sanitise whitespace / strip
        v = sanitize_input(v)

        # 2. Length guards
        if len(v) < settings.MIN_INPUT_LENGTH:
            raise ValueError(
                f"Query too short (min {settings.MIN_INPUT_LENGTH} characters)."
            )
        if len(v) > settings.MAX_INPUT_LENGTH:
            raise ValueError(
                f"Query too long (max {settings.MAX_INPUT_LENGTH} characters)."
            )

        # 3. Prompt-injection detection
        if detect_prompt_injection(v):
            raise ValueError(
                "Your message was flagged as a potential prompt-injection attempt. "
                "Please rephrase your question."
            )

        return v