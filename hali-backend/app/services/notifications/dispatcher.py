from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.audit import NotificationEvent


class NotificationDispatcher:
    @staticmethod
    def dispatch_alert(
        db: Session,
        university_id: str,
        recipient_role: str,
        channel: str,
        summary: str
    ) -> NotificationEvent:
        event = NotificationEvent(
            university_id=university_id,
            recipient_role=recipient_role,
            channel=channel,
            status="SENT",
            payload_summary=summary,
            attempts=1,
            sent_at=datetime.now(timezone.utc)
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

