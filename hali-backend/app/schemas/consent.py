from typing import Optional
from pydantic import BaseModel, Field


class ConsentUpdateRequest(BaseModel):
    scope: Optional[str] = "deidentified_research"  # 'aggregate_stats', 'deidentified_research', 'recontact_studies'
    granted: Optional[bool] = True
    consent_version: Optional[str] = "1.0"
    # Frontend compatibility fields:
    research: Optional[bool] = None
    recontact: Optional[bool] = None


class ConsentWithdrawRequest(BaseModel):
    scope: str = Field(..., description="Consent scope to withdraw")

