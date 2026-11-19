from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import TimeStampedModel


class LMSAnomalyEvent(TimeStampedModel):
    __tablename__ = "lms_anomaly_events"

    university_id = Column(UUID(as_uuid=True), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user_hash = Column(String(128), nullable=False, index=True)

    anomaly_type = Column(String(50), nullable=False)  # 'LOGIN_DROP', 'LATE_NIGHT_SPIKE', 'MISSED_CAT'
    severity = Column(String(50), nullable=False)  # 'LOW', 'MEDIUM', 'HIGH'
    nudge_sent = Column(Boolean, default=False, nullable=False)
    nudge_type = Column(String(50), nullable=True)

