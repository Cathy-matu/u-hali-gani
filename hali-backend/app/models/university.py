from sqlalchemy import Column, String, Boolean, Integer, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedModel


class University(TimeStampedModel):
    __tablename__ = "universities"

    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False, unique=True, index=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    domain = Column(String(255), nullable=True)
    salt = Column(String(255), nullable=False)  # Cryptographic university salt
    is_active = Column(Boolean, default=True, nullable=False)

    settings = relationship("UniversitySettings", back_populates="university", uselist=False, cascade="all, delete-orphan")
    users = relationship("User", back_populates="university", cascade="all, delete-orphan")


class UniversitySettings(TimeStampedModel):
    __tablename__ = "university_settings"

    university_id = Column(UUID(as_uuid=True), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    k_anonymity_threshold = Column(Integer, default=15, nullable=False)
    red_threshold_phq9 = Column(Integer, default=15, nullable=False)
    red_threshold_gad7 = Column(Integer, default=15, nullable=False)
    amber_threshold_phq9 = Column(Integer, default=10, nullable=False)
    amber_threshold_gad7 = Column(Integer, default=10, nullable=False)
    emergency_callback_enabled = Column(Boolean, default=True, nullable=False)
    crisis_hotlines = Column(JSON, nullable=True)

    university = relationship("University", back_populates="settings")

