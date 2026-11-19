from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CounsellorCaseSummary(BaseModel):
    id: str  # Anon handle or display ID (e.g. 'Swift-Baobab-208')
    user_uuid: str
    risk: str  # 'red', 'amber', 'green'
    trend: str  # 'worsening', 'improving', 'stable'
    last: str  # 'Today 08:12'
    phq: List[int]
    gad: List[int]
    status: str  # 'Escalated', 'Active', 'Monitoring'
    next: str  # 'Today 14:00', '—'
    brief: Optional[Dict[str, Any]] = None


class SessionNoteCreate(BaseModel):
    note: str = Field(..., min_length=2)


class CaseStatusUpdate(BaseModel):
    status: str


class CaseAssignRequest(BaseModel):
    counsellor_id: str

