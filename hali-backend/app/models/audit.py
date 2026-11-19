from sqlalchemy import Column, String, Integer, Text, JSON, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import TimeStampedModel


class AuditLog(TimeStampedModel):
    __tablename__ = "audit_logs"

    university_id = Column(UUID(as_uuid=True), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True)
    actor_uuid = Column(UUID(as_uuid=True), nullable=True, index=True)
    actor_role = Column(String(50), nullable=True)

    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(100), nullable=True)
    details = Column(JSON, nullable=True)
    ip_address_hash = Column(String(128), nullable=True)


class NotificationEvent(TimeStampedModel):
    __tablename__ = "notification_events"

    university_id = Column(UUID(as_uuid=True), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True)
    recipient_role = Column(String(50), nullable=False)
    channel = Column(String(50), default="MOCK_CHANNEL", nullable=False)  # SMS, EMAIL, WEB_PUSH, CLINIC_CALLBACK
    status = Column(String(50), default="PENDING", nullable=False, index=True)  # PENDING, SENT, ACKNOWLEDGED, FAILED
    
    payload_summary = Column(Text, nullable=False)  # Nonce/sanitized summary
    attempts = Column(Integer, default=0, nullable=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)

