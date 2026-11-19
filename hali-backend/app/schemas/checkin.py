from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CheckinSubmission(BaseModel):
    user_uuid: Optional[str] = Field(None, description="Pseudonymous student UUID")
    phq9_scores: Optional[List[int]] = Field(None, description="Array of 9 scores (0-3)")
    gad7_scores: Optional[List[int]] = Field(None, description="Array of 7 scores (0-3)")
    auditc_scores: Optional[List[int]] = Field(None, description="Array of 3 scores (0-4)")
    free_text_or_transcript: Optional[str] = Field(None, description="Optional reflection text or Sheng/Swahili transcript")


class MoodCheckinRequest(BaseModel):
    sel: int = Field(..., ge=0, le=4, description="Mood selector index: 0=Great, 1=Good, 2=Okay, 3=Low, 4=Struggling")
    note: Optional[str] = Field(None, description="Optional private reflection note")


class AssessmentSubmitRequest(BaseModel):
    # Frontend flexible schema: accepts object with phq1..phq9, gad1..gad7, who1..who5
    scores: Optional[Dict[str, int]] = None
    phq9_scores: Optional[List[int]] = None
    gad7_scores: Optional[List[int]] = None
    auditc_scores: Optional[List[int]] = None
    mode: Optional[str] = "full"

