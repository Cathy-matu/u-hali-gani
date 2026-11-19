from typing import Optional
from pydantic import BaseModel, Field


class MessageSendRequest(BaseModel):
    conversation_id: Optional[str] = None
    recipient_id: Optional[str] = None
    content: Optional[str] = None
    text: Optional[str] = None  # Frontend alias for text content
    t: Optional[str] = None  # Frontend alias for bubble text
    b: Optional[bool] = None


class MessageResponse(BaseModel):
    id: str
    sender_role: str
    content: str
    created_at: str

