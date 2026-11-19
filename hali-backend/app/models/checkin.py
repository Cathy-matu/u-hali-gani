from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedModel


class Checkin(TimeStampedModel):
    __tablename__ = "checkins"

    university_id = Column(UUID(as_uuid=True), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    mood_score = Column(Integer, nullable=True)  # 0 to 4
    mood_label = Column(String(50), nullable=True)  # 'Struggling', 'Low', 'Okay', 'Good', 'Great'
    reflection_note = Column(Text, nullable=True)  # PII-sanitized note
    checkin_type = Column(String(50), default="daily", nullable=False)  # 'daily', 'mood', 'assessment_checkin'

    user = relationship("User", back_populates="checkins")

