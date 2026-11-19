from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedModel


class BreakGlassVault(TimeStampedModel):
    """
    Dual-key encrypted emergency identity vault.
    Stored logically and cryptographically separated from student records.
    Neither counsellor nor dean alone can decrypt.
    """
    __tablename__ = "break_glass_vault"

    university_id = Column(UUID(as_uuid=True), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # AES-256-GCM Encrypted payload & authentication fields
    encrypted_contact = Column(Text, nullable=False)  # Base64 ciphertext
    nonce = Column(String(64), nullable=False)  # Base64 GCM IV
    authentication_tag = Column(String(64), nullable=False)  # Base64 GCM auth tag

    # External key share custody references (Two-of-Two Threshold)
    counsellor_key_share_reference = Column(String(128), nullable=False)
    dean_admin_key_share_reference = Column(String(128), nullable=False)

    user = relationship("User", back_populates="vault_record")
    requests = relationship("BreakGlassRequest", back_populates="vault", cascade="all, delete-orphan")


class BreakGlassRequest(TimeStampedModel):
    """
    Immutable audit trail for emergency disclosure requests.
    Requires dual human authorization (Counsellor + Dean of Students).
    """
    __tablename__ = "break_glass_requests"

    university_id = Column(UUID(as_uuid=True), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True)
    vault_id = Column(UUID(as_uuid=True), ForeignKey("break_glass_vault.id", ondelete="CASCADE"), nullable=False, index=True)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    escalation_case_id = Column(UUID(as_uuid=True), nullable=True)

    requesting_counsellor_uuid = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    approving_dean_admin_uuid = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    
    reason = Column(Text, nullable=False)
    status = Column(String(50), default="PENDING_APPROVAL", nullable=False, index=True)  # PENDING_APPROVAL, APPROVED_DECRYPTED, REJECTED, EXPIRED
    decryption_outcome = Column(String(50), nullable=True)  # SUCCESS, FAILED, ACCESS_DENIED
    decrypted_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    vault = relationship("BreakGlassVault", back_populates="requests")

