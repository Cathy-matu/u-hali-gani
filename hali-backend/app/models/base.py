import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Boolean, text
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


def generate_uuid():
    return uuid.uuid4()


class TimeStampedModel(Base):
    """Abstract base model with UUID primary key and audit timestamps."""
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

