from typing import List, Optional
from pydantic import BaseModel, Field


class RedactionRequest(BaseModel):
    text: str = Field(..., description="Text containing potential PII or code-switched notes")


class RedactionResponse(BaseModel):
    redacted_text: str
    redaction_count: int
    redaction_applied: bool

