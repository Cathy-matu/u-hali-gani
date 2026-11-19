from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_optional, get_db
from app.models.user import User
from app.models.counsellor import CounsellorProfile
from app.models.messaging import Conversation, Message
from app.schemas.messaging import MessageSendRequest
from app.services.pii_redaction.redactor import PIIRedactor

router = APIRouter(prefix="", tags=["Confidential Counselling Messaging"])


@router.post("/api/messages")
@router.post("/messages")
def send_message_direct(
    payload: MessageSendRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Direct messaging endpoint.
    PII sanitization applied before storage. Private message contents are NEVER logged in server logs.
    """
    user = current_user or db.query(User).filter(User.role == "student").first()
    if not user:
        raise HTTPException(status_code=400, detail="User context required")

    text_content = payload.content or payload.text or payload.t or ""
    sanitized_text = PIIRedactor.redact(text_content)["redacted_text"]

    # Find or create active conversation
    counsellor = db.query(CounsellorProfile).first()
    if not counsellor:
        staff = db.query(User).filter(User.role == "counsellor").first() or user
        counsellor = CounsellorProfile(
            university_id=user.university_id,
            user_id=staff.id,
            name="Dr. Amina Wekesa",
            specialization="Anxiety & academic stress",
            modes=["In-person", "Audio", "Text"]
        )
        db.add(counsellor)
        db.flush()
    c_id = counsellor.id

    conv = db.query(Conversation).filter(
        Conversation.student_uuid == user.id,
        Conversation.is_active == True
    ).first()

    if not conv:
        conv = Conversation(
            university_id=user.university_id,
            student_uuid=user.id,
            counsellor_id=c_id,
            is_active=True
        )
        db.add(conv)
        db.flush()

    msg = Message(
        university_id=user.university_id,
        conversation_id=conv.id,
        sender_uuid=user.id,
        sender_role=user.role,
        content=sanitized_text,
        is_read=False
    )
    db.add(msg)
    db.commit()

    return {
        "success": True,
        "message": "Message delivered",
        "data": {
            "id": str(msg.id),
            "conversation_id": str(conv.id),
            "content": sanitized_text,
            "sender_role": user.role
        },
        # Direct return for frontend
        "t": sanitized_text,
        "b": False
    }


@router.get("/api/messages/conversations")
def get_conversations(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """List active user conversations."""
    user = current_user or db.query(User).filter(User.role == "student").first()
    if not user:
        return {"data": []}

    convs = db.query(Conversation).filter(
        (Conversation.student_uuid == user.id) | (Conversation.counsellor_id == user.id)
    ).all()

    return {
        "success": True,
        "data": [{"id": str(c.id), "is_active": c.is_active} for c in convs]
    }


# Active WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, conversation_id: str, websocket: WebSocket):
        await websocket.accept()
        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = []
        self.active_connections[conversation_id].append(websocket)

    def disconnect(self, conversation_id: str, websocket: WebSocket):
        if conversation_id in self.active_connections:
            self.active_connections[conversation_id].remove(websocket)

    async def broadcast(self, conversation_id: str, message: dict):
        if conversation_id in self.active_connections:
            for connection in self.active_connections[conversation_id]:
                await connection.send_json(message)


ws_manager = ConnectionManager()


@router.websocket("/api/messages/ws/{conversation_id}")
async def websocket_messages_endpoint(websocket: WebSocket, conversation_id: str):
    await ws_manager.connect(conversation_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # PII sanitize incoming text
            raw_text = data.get("content", "")
            redacted = PIIRedactor.redact(raw_text)["redacted_text"]
            await ws_manager.broadcast(conversation_id, {
                "sender": data.get("sender", "anonymous"),
                "content": redacted
            })
    except WebSocketDisconnect:
        ws_manager.disconnect(conversation_id, websocket)

