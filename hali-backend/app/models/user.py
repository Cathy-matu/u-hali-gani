from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedModel


class Role(TimeStampedModel):
    __tablename__ = "roles"

    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)


class User(TimeStampedModel):
    """
    ZERO-PII Student Account & Staff Account Model.
    For students: NO real name, NO registration number, NO personal email.
    Pseudonymous handle only.
    """
    __tablename__ = "users"

    university_id = Column(UUID(as_uuid=True), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True)
    anon_handle = Column(String(100), nullable=False, index=True)
    role = Column(String(50), default="student", nullable=False, index=True)
    
    # Demographics (pseudonymous cohort dimensions for k-anonymity analytics)
    faculty = Column(String(100), nullable=True, index=True)
    department = Column(String(100), nullable=True, index=True)
    year_of_study = Column(Integer, nullable=True, index=True)

    # Authentication fields
    # Students use LMS handshake; staff/counsellors may have argon2 hashed credentials
    password_hash = Column(String(255), nullable=True)
    staff_email = Column(String(255), nullable=True, unique=True)  # Strictly for staff accounts only
    staff_name = Column(String(255), nullable=True)  # Strictly for staff accounts only
    is_active = Column(Boolean, default=True, nullable=False)

    university = relationship("University", back_populates="users")
    university_hash = relationship("UserUniversityHash", back_populates="user", uselist=False, cascade="all, delete-orphan")
    checkins = relationship("Checkin", back_populates="user", cascade="all, delete-orphan")
    vault_record = relationship("BreakGlassVault", back_populates="user", uselist=False, cascade="all, delete-orphan")
    counsellor_profile = relationship("CounsellorProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")


class UserRole(TimeStampedModel):
    __tablename__ = "user_roles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)


class UserUniversityHash(TimeStampedModel):
    """
    One-way keyed HMAC digest of student registration number.
    Ensures single student account per student registration number without storing PII.
    """
    __tablename__ = "user_university_hashes"

    university_id = Column(UUID(as_uuid=True), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    user_hash = Column(String(128), nullable=False, index=True)

    user = relationship("User", back_populates="university_hash")

    __table_args__ = (
        UniqueConstraint("university_id", "user_hash", name="uq_university_user_hash"),
    )

