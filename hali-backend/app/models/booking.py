from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedModel


class Booking(TimeStampedModel):
    __tablename__ = "bookings"

    university_id = Column(UUID(as_uuid=True), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True)
    student_uuid = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    counsellor_id = Column(UUID(as_uuid=True), ForeignKey("counsellor_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    appointment_time = Column(DateTime(timezone=True), nullable=False, index=True)
    time_slot = Column(String(50), nullable=True)  # '14:00'
    session_type = Column(String(50), nullable=False)  # 'In-person', 'Audio', 'Text'
    status = Column(String(50), default="Requested", nullable=False, index=True)  # 'Requested', 'Confirmed', 'Completed', 'Cancelled'
    notes = Column(Text, nullable=True)

    counsellor = relationship("CounsellorProfile", back_populates="bookings")

