from pydantic import BaseModel, field_validator

from app.config.settings import settings
from app.utils.security import detect_prompt_injection, sanitize_input


class CloudCartInput(BaseModel):
    user_query: str

    @field_validator("user_query")
    def validate_query(cls, v):
        v = sanitize_input(v)

        if len(v) < settings.MIN_INPUT_LENGTH:
            raise ValueError("Query too short")
        if len(v) > settings.MAX_INPUT_LENGTH:
            raise ValueError("Query too long")

        if detect_prompt_injection(v):
            raise ValueError("Prompt injection detected")

        return v