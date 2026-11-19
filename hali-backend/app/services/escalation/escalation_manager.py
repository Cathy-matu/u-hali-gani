from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.triage import Escalation, RiskEvent
from app.models.audit import AuditLog, NotificationEvent


class EscalationManager:
    @staticmethod
    def acknowledge_escalation(
        db: Session,
        escalation_id: str,
        counsellor_uuid: str,
        university_id: str
    ) -> Escalation:
        esc = db.query(Escalation).filter(
            Escalation.id == escalation_id,
            Escalation.university_id == university_id
        ).first()

        if not esc:
            raise ValueError("Escalation record not found")

        esc.status = "ACKNOWLEDGED"
        esc.acknowledged_by = counsellor_uuid
        esc.acknowledged_at = datetime.now(timezone.utc)

        db.add(AuditLog(
            university_id=university_id,
            actor_uuid=counsellor_uuid,
            actor_role="counsellor",
            action="ESCALATION_ACKNOWLEDGED",
            resource_type="escalation",
            resource_id=str(esc.id),
            details={"status": "ACKNOWLEDGED"}
        ))
        db.commit()
        db.refresh(esc)
        return esc

    @staticmethod
    def resolve_escalation(
        db: Session,
        escalation_id: str,
        counsellor_uuid: str,
        resolution_notes: str,
        university_id: str
    ) -> Escalation:
        esc = db.query(Escalation).filter(
            Escalation.id == escalation_id,
            Escalation.university_id == university_id
        ).first()

        if not esc:
            raise ValueError("Escalation record not found")

        esc.status = "RESOLVED"
        esc.resolved_at = datetime.now(timezone.utc)
        esc.resolution_notes = resolution_notes

        db.add(AuditLog(
            university_id=university_id,
            actor_uuid=counsellor_uuid,
            actor_role="counsellor",
            action="ESCALATION_RESOLVED",
            resource_type="escalation",
            resource_id=str(esc.id),
            details={"status": "RESOLVED"}
        ))
        db.commit()
        db.refresh(esc)
        return esc

