from pydantic import BaseModel, field_validator

from app.utils.security import contains_pii


class CloudCartOutput(BaseModel):
    """
    Pydantic model that validates and sanitises the LLM response
    before it is returned to the caller.
    """

    response: str

    @field_validator("response")
    @classmethod
    def validate_response(cls, v: str) -> str:
        v = v.strip()

        if not v:
            raise ValueError("LLM returned an empty response.")

        if contains_pii(v):
            raise ValueError(
                "The model response appears to contain sensitive personal data (PII). "
                "The response has been suppressed for safety."
            )

        return v