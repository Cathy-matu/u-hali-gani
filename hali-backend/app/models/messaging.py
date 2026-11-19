from sqlalchemy import Column, String, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedModel


class Conversation(TimeStampedModel):
    __tablename__ = "conversations"

    university_id = Column(UUID(as_uuid=True), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True)
    student_uuid = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    counsellor_id = Column(UUID(as_uuid=True), ForeignKey("counsellor_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(TimeStampedModel):
    __tablename__ = "messages"

    university_id = Column(UUID(as_uuid=True), ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_uuid = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    sender_role = Column(String(50), nullable=False)  # 'student' or 'counsellor'
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")

