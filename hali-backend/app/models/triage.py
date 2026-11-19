from sqlalchemy import Column, String, Integer, Boolean, Text, JSON, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedModel


class PHQ9Assessment(TimeStampedModel):
    __tablename__ = "phq9_assessments"

    university_id = Column(UUID(as_uuid=True), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    checkin_id = Column(UUID(as_uuid=True), ForeignKey("checkins.id", ondelete="SET NULL"), nullable=True)

    item_scores = Column(JSON, nullable=False)  # List of 9 ints [0..3]
    total_score = Column(Integer, nullable=False, index=True)
    item_9_score = Column(Integer, nullable=False, index=True)  # Safety item: suicidal ideation
    severity = Column(String(50), nullable=False)  # Minimal, Mild, Moderate, Moderately Severe, Severe


class GAD7Assessment(TimeStampedModel):
    __tablename__ = "gad7_assessments"

    university_id = Column(UUID(as_uuid=True), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    checkin_id = Column(UUID(as_uuid=True), ForeignKey("checkins.id", ondelete="SET NULL"), nullable=True)

    item_scores = Column(JSON, nullable=False)  # List of 7 ints [0..3]
    total_score = Column(Integer, nullable=False, index=True)
    severity = Column(String(50), nullable=False)  # Minimal, Mild, Moderate, Severe


class AUDITCAssessment(TimeStampedModel):
    __tablename__ = "auditc_assessments"

    university_id = Column(UUID(as_uuid=True), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    checkin_id = Column(UUID(as_uuid=True), ForeignKey("checkins.id", ondelete="SET NULL"), nullable=True)

    item_scores = Column(JSON, nullable=False)  # List of 3 ints [0..4]
    total_score = Column(Integer, nullable=False, index=True)
    risk_level = Column(String(50), nullable=False)  # Low, Hazardous


class RiskEvent(TimeStampedModel):
    __tablename__ = "risk_events"

    university_id = Column(UUID(as_uuid=True), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    risk_level = Column(String(50), nullable=False, index=True)  # GREEN, AMBER, RED
    trigger_reason = Column(String(255), nullable=False)
    item9_positive = Column(Boolean, default=False, nullable=False)
    phq9_score = Column(Integer, nullable=True)
    gad7_score = Column(Integer, nullable=True)
    auditc_score = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    escalations = relationship("Escalation", back_populates="risk_event", cascade="all, delete-orphan")


class Escalation(TimeStampedModel):
    __tablename__ = "escalations"

    university_id = Column(UUID(as_uuid=True), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True)
    risk_event_id = Column(UUID(as_uuid=True), ForeignKey("risk_events.id", ondelete="CASCADE"), nullable=False, index=True)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    escalation_tier = Column(String(50), nullable=False, index=True)  # RED_IMMINENT_RISK, AMBER_RECOMMENDED
    status = Column(String(50), default="PENDING", nullable=False, index=True)  # PENDING, SENT, ACKNOWLEDGED, IN_PROGRESS, RESOLVED, FAILED
    
    acknowledged_by = Column(UUID(as_uuid=True), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    idempotency_key = Column(String(128), unique=True, nullable=False, index=True)

    risk_event = relationship("RiskEvent", back_populates="escalations")

