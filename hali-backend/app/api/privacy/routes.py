from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.services.pii_redaction.redactor import PIIRedactor
from app.services.ai.provider import get_ai_provider
from app.schemas.privacy import RedactionRequest, RedactionResponse

router = APIRouter(prefix="", tags=["AI Privacy & Redaction Layer"])


class AssistantMessageRequest(BaseModel):
    message: str = Field(..., description="Student message text or question")
    lang: Optional[str] = "en"  # "en" or "sw"


@router.post("/api/privacy/redact", response_model=RedactionResponse)
@router.post("/privacy/redact", response_model=RedactionResponse)
def redact_pii(request: RedactionRequest):
    """
    Dedicated PII Detection and Redaction Service.
    Replaces [PERSON], [HOSTEL], [LECTURER], [PHONE], [EMAIL], [REGISTRATION_NUMBER], [LOCATION]
    with sanitized privacy placeholders.
    """
    result = PIIRedactor.redact(request.text)
    return RedactionResponse(
        redacted_text=result["redacted_text"],
        redaction_count=result["redaction_count"],
        redaction_applied=result["redaction_applied"]
    )


@router.post("/api/privacy/assistant")
@router.post("/assistant/message")
def assistant_message(request: AssistantMessageRequest):
    """
    Safe AI Assistant Interaction.
    1. Pre-sanitizes text through PII redaction layer.
    2. Detects crisis/self-harm triggers and immediately provides human crisis referral.
    3. Provides supportive non-diagnostic psychoeducational guidance.
    """
    ai_provider = get_ai_provider()
    res = ai_provider.generate_assistant_reply(request.message, lang=request.lang or "en")
    return {
        "success": True,
        "data": res,
        # Direct reply field for frontend
        "reply": res["reply"],
        "human": res["human_escalation_triggered"]
    }

