from typing import Optional, List
from pydantic import BaseModel, Field


class BookingCreateRequest(BaseModel):
    counsellor_id: Optional[str] = None
    who: Optional[str] = None  # Counsellor name (frontend format)
    when: Optional[str] = None  # e.g. 'Tomorrow 14:00'
    appointment_time: Optional[str] = None
    session_type: Optional[str] = "Audio"  # In-person, Audio, Text
    type: Optional[str] = None  # Frontend alias
    slot: Optional[str] = None
    notes: Optional[str] = None


class BookingResponse(BaseModel):
    id: str
    who: str
    when: str
    type: str
    status: str

