from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import TimeStampedModel


class ConsentLedger(TimeStampedModel):
    """
    Versioned, immutable-audit consent ledger.
    Supports:
    1. aggregate_stats
    2. deidentified_research
    3. recontact_studies
    """
    __tablename__ = "consent_ledger"

    university_id = Column(UUID(as_uuid=True), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    consent_version = Column(String(20), default="1.0", nullable=False)
    consent_scope = Column(String(50), nullable=False, index=True)  # 'aggregate_stats', 'deidentified_research', 'recontact_studies'
    consent_text_version = Column(String(50), default="v2026.1", nullable=False)
    
    granted = Column(Boolean, default=False, nullable=False, index=True)
    granted_at = Column(DateTime(timezone=True), nullable=True)
    withdrawn_at = Column(DateTime(timezone=True), nullable=True)

