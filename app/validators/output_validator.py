from pydantic import BaseModel, field_validator

from app.utils.security import contains_pii


class CloudCartOutput(BaseModel):
    response: str

    @field_validator("response")
    def validate_response(cls, v):
        v = v.strip()

        if not v:
            raise ValueError("Empty response")

        if contains_pii(v):
            raise ValueError("Possible PII detected")

        return v