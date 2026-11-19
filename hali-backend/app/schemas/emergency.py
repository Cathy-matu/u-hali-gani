from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class BreakGlassStoreRequest(BaseModel):
    contact_name: str = Field(..., description="Emergency contact full name")
    relationship: str = Field(..., description="e.g. Parent, Guardian, Sibling")
    phone: str = Field(..., description="Emergency contact phone number")
    notes: Optional[str] = None


class BreakGlassInitiateRequest(BaseModel):
    user_uuid: str = Field(..., description="Target student pseudonymous UUID")
    reason: str = Field(..., min_length=10, description="Detailed clinical emergency justification")
    escalation_case_id: Optional[str] = None


class BreakGlassApproveRequest(BaseModel):
    approval_notes: Optional[str] = None

