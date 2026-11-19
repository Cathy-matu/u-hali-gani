from sqlalchemy import Column, String, Boolean, Integer, Text, JSON, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedModel


class CounsellorProfile(TimeStampedModel):
    __tablename__ = "counsellor_profiles"

    university_id = Column(UUID(as_uuid=True), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    name = Column(String(255), nullable=False)
    specialization = Column(String(255), nullable=False)
    modes = Column(JSON, nullable=False)  # ['In-person', 'Audio', 'Text']
    is_online = Column(Boolean, default=True, nullable=False)
    phone = Column(String(50), nullable=True)

    user = relationship("User", back_populates="counsellor_profile")
    availabilities = relationship("CounsellorAvailability", back_populates="counsellor", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="counsellor", cascade="all, delete-orphan")


class CounsellorAvailability(TimeStampedModel):
    __tablename__ = "counsellor_availability"

    university_id = Column(UUID(as_uuid=True), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True)
    counsellor_id = Column(UUID(as_uuid=True), ForeignKey("counsellor_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    day_of_week = Column(Integer, nullable=False)  # 0=Monday .. 6=Sunday
    time_slot = Column(String(50), nullable=False)  # '09:00', '10:30', '12:00', '14:00', '15:30'
    is_booked = Column(Boolean, default=False, nullable=False)

    counsellor = relationship("CounsellorProfile", back_populates="availabilities")


class StudentCounsellorAssignment(TimeStampedModel):
    __tablename__ = "student_counsellor_assignments"

    university_id = Column(UUID(as_uuid=True), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True)
    student_uuid = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    counsellor_id = Column(UUID(as_uuid=True), ForeignKey("counsellor_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), default="ACTIVE", nullable=False)


class SessionNote(TimeStampedModel):
    __tablename__ = "session_notes"

    university_id = Column(UUID(as_uuid=True), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True)
    student_uuid = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    counsellor_id = Column(UUID(as_uuid=True), ForeignKey("counsellor_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    note_content = Column(Text, nullable=False)


class AICaseBrief(TimeStampedModel):
    """
    AI-generated pre-session brief.
    MUST be generated from PII-redacted text only.
    Contains non-diagnostic clinical summary draft for counsellor review.
    """
    __tablename__ = "ai_case_briefs"

    university_id = Column(UUID(as_uuid=True), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True)
    student_uuid = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    summary = Column(Text, nullable=False)
    observations = Column(JSON, nullable=False)
    suggested_topics = Column(JSON, nullable=False)
    risk_level = Column(String(50), nullable=False)

