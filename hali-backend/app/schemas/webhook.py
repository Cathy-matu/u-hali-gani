from typing import Optional
from pydantic import BaseModel, Field


class LMSAnomalyWebhookRequest(BaseModel):
    user_hash: str = Field(..., description="Keyed HMAC digest of student identifier from university LMS")
    anomaly_type: str = Field(..., description="Supported: LOGIN_DROP, LATE_NIGHT_SPIKE, MISSED_CAT")
    severity: str = Field(..., description="LOW, MEDIUM, HIGH")

