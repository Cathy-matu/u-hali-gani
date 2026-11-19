"""0001_initial_schema_and_rls

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-11-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None

# Tables requiring Row-Level Security tenant isolation
RLS_TABLES = [
    "users",
    "user_university_hashes",
    "checkins",
    "phq9_assessments",
    "gad7_assessments",
    "auditc_assessments",
    "risk_events",
    "escalations",
    "break_glass_vault",
    "break_glass_requests",
    "counsellor_profiles",
    "counsellor_availability",
    "student_counsellor_assignments",
    "session_notes",
    "ai_case_briefs",
    "bookings",
    "conversations",
    "messages",
    "consent_ledger",
    "audit_logs",
    "notification_events",
    "lms_anomaly_events"
]


def upgrade() -> None:
    # 1. Universities
    op.create_table(
        "universities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), default=False, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("domain", sa.String(255), nullable=True),
        sa.Column("salt", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
    )
    op.create_index("ix_universities_code", "universities", ["code"])
    op.create_index("ix_universities_slug", "universities", ["slug"])

    # 2. University Settings
    op.create_table(
        "university_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), default=False, nullable=False),
        sa.Column("university_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("k_anonymity_threshold", sa.Integer(), default=15, nullable=False),
        sa.Column("red_threshold_phq9", sa.Integer(), default=15, nullable=False),
        sa.Column("red_threshold_gad7", sa.Integer(), default=15, nullable=False),
        sa.Column("amber_threshold_phq9", sa.Integer(), default=10, nullable=False),
        sa.Column("amber_threshold_gad7", sa.Integer(), default=10, nullable=False),
        sa.Column("emergency_callback_enabled", sa.Boolean(), default=True, nullable=False),
        sa.Column("crisis_hotlines", sa.JSON(), nullable=True),
    )

    # 3. Roles
    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), default=False, nullable=False),
        sa.Column("name", sa.String(50), unique=True, nullable=False),
        sa.Column("description", sa.String(255), nullable=True),
    )

    # 4. Users (ZERO-PII)
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), default=False, nullable=False),
        sa.Column("university_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("universities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("anon_handle", sa.String(100), nullable=False),
        sa.Column("role", sa.String(50), default="student", nullable=False),
        sa.Column("faculty", sa.String(100), nullable=True),
        sa.Column("department", sa.String(100), nullable=True),
        sa.Column("year_of_study", sa.Integer(), nullable=True),
        sa.Column("password_hash", sa.String(255), nullable=True),
        sa.Column("staff_email", sa.String(255), nullable=True, unique=True),
        sa.Column("staff_name", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
    )
    op.create_index("ix_users_university_id", "users", ["university_id"])
    op.create_index("ix_users_anon_handle", "users", ["anon_handle"])
    op.create_index("ix_users_role", "users", ["role"])
    op.create_index("ix_users_faculty", "users", ["faculty"])
    op.create_index("ix_users_department", "users", ["department"])

    # 5. User Roles
    op.create_table(
        "user_roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), default=False, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
    )

    # 6. User University Hashes
    op.create_table(
        "user_university_hashes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), default=False, nullable=False),
        sa.Column("university_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("universities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_uuid", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("user_hash", sa.String(128), nullable=False),
        sa.UniqueConstraint("university_id", "user_hash", name="uq_university_user_hash")
    )
    op.create_index("ix_user_university_hashes_user_hash", "user_university_hashes", ["user_hash"])

    # 7. Checkins
    op.create_table(
        "checkins",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), default=False, nullable=False),
        sa.Column("university_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("universities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_uuid", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mood_score", sa.Integer(), nullable=True),
        sa.Column("mood_label", sa.String(50), nullable=True),
        sa.Column("reflection_note", sa.Text(), nullable=True),
        sa.Column("checkin_type", sa.String(50), default="daily", nullable=False),
    )
    op.create_index("ix_checkins_university_id", "checkins", ["university_id"])
    op.create_index("ix_checkins_user_uuid", "checkins", ["user_uuid"])

    # 8. PHQ-9 Assessments
    op.create_table(
        "phq9_assessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), default=False, nullable=False),
        sa.Column("university_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("universities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_uuid", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("checkin_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("checkins.id", ondelete="SET NULL"), nullable=True),
        sa.Column("item_scores", sa.JSON(), nullable=False),
        sa.Column("total_score", sa.Integer(), nullable=False),
        sa.Column("item_9_score", sa.Integer(), nullable=False),
        sa.Column("severity", sa.String(50), nullable=False),
    )
    op.create_index("ix_phq9_assessments_total_score", "phq9_assessments", ["total_score"])
    op.create_index("ix_phq9_assessments_item_9_score", "phq9_assessments", ["item_9_score"])

    # 9. GAD-7 Assessments
    op.create_table(
        "gad7_assessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), default=False, nullable=False),
        sa.Column("university_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("universities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_uuid", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("checkin_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("checkins.id", ondelete="SET NULL"), nullable=True),
        sa.Column("item_scores", sa.JSON(), nullable=False),
        sa.Column("total_score", sa.Integer(), nullable=False),
        sa.Column("severity", sa.String(50), nullable=False),
    )

    # 10. AUDIT-C Assessments
    op.create_table(
        "auditc_assessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), default=False, nullable=False),
        sa.Column("university_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("universities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_uuid", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("checkin_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("checkins.id", ondelete="SET NULL"), nullable=True),
        sa.Column("item_scores", sa.JSON(), nullable=False),
        sa.Column("total_score", sa.Integer(), nullable=False),
        sa.Column("risk_level", sa.String(50), nullable=False),
    )

    # 11. Risk Events
    op.create_table(
        "risk_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), default=False, nullable=False),
        sa.Column("university_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("universities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_uuid", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("risk_level", sa.String(50), nullable=False),
        sa.Column("trigger_reason", sa.String(255), nullable=False),
        sa.Column("item9_positive", sa.Boolean(), default=False, nullable=False),
        sa.Column("phq9_score", sa.Integer(), nullable=True),
        sa.Column("gad7_score", sa.Integer(), nullable=True),
        sa.Column("auditc_score", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
    )
    op.create_index("ix_risk_events_risk_level", "risk_events", ["risk_level"])

    # 12. Escalations
    op.create_table(
        "escalations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), default=False, nullable=False),
        sa.Column("university_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("universities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("risk_event_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("risk_events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_uuid", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("escalation_tier", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), default="PENDING", nullable=False),
        sa.Column("acknowledged_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolution_notes", sa.Text(), nullable=True),
        sa.Column("idempotency_key", sa.String(128), unique=True, nullable=False),
    )
    op.create_index("ix_escalations_status", "escalations", ["status"])

    # 13. Break Glass Vault (Dual-Key)
    op.create_table(
        "break_glass_vault",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), default=False, nullable=False),
        sa.Column("university_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("universities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_uuid", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("encrypted_contact", sa.Text(), nullable=False),
        sa.Column("nonce", sa.String(64), nullable=False),
        sa.Column("authentication_tag", sa.String(64), nullable=False),
        sa.Column("counsellor_key_share_reference", sa.String(128), nullable=False),
        sa.Column("dean_admin_key_share_reference", sa.String(128), nullable=False),
    )

    # 14. Break Glass Requests
    op.create_table(
        "break_glass_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), default=False, nullable=False),
        sa.Column("university_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("universities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("vault_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("break_glass_vault.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_uuid", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("escalation_case_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("requesting_counsellor_uuid", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("approving_dean_admin_uuid", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", sa.String(50), default="PENDING_APPROVAL", nullable=False),
        sa.Column("decryption_outcome", sa.String(50), nullable=True),
        sa.Column("decrypted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )

    # 15. Counsellor Profiles
    op.create_table(
        "counsellor_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), default=False, nullable=False),
        sa.Column("university_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("universities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("specialization", sa.String(255), nullable=False),
        sa.Column("modes", sa.JSON(), nullable=False),
        sa.Column("is_online", sa.Boolean(), default=True, nullable=False),
        sa.Column("phone", sa.String(50), nullable=True),
    )

    # 16. Counsellor Availability
    op.create_table(
        "counsellor_availability",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), default=False, nullable=False),
        sa.Column("university_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("universities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("counsellor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("counsellor_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("time_slot", sa.String(50), nullable=False),
        sa.Column("is_booked", sa.Boolean(), default=False, nullable=False),
    )

    # 17. Student Counsellor Assignments
    op.create_table(
        "student_counsellor_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), default=False, nullable=False),
        sa.Column("university_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("universities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("student_uuid", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("counsellor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("counsellor_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(50), default="ACTIVE", nullable=False),
    )

    # 18. Session Notes
    op.create_table(
        "session_notes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), default=False, nullable=False),
        sa.Column("university_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("universities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("student_uuid", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("counsellor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("counsellor_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("note_content", sa.Text(), nullable=False),
    )

    # 19. AI Case Briefs
    op.create_table(
        "ai_case_briefs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), default=False, nullable=False),
        sa.Column("university_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("universities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("student_uuid", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("observations", sa.JSON(), nullable=False),
        sa.Column("suggested_topics", sa.JSON(), nullable=False),
        sa.Column("risk_level", sa.String(50), nullable=False),
    )

    # 20. Bookings
    op.create_table(
        "bookings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), default=False, nullable=False),
        sa.Column("university_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("universities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("student_uuid", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("counsellor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("counsellor_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("appointment_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("time_slot", sa.String(50), nullable=True),
        sa.Column("session_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), default="Requested", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
    )

    # 21. Conversations
    op.create_table(
        "conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), default=False, nullable=False),
        sa.Column("university_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("universities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("student_uuid", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("counsellor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("counsellor_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
    )

    # 22. Messages
    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), default=False, nullable=False),
        sa.Column("university_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("universities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sender_uuid", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sender_role", sa.String(50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), default=False, nullable=False),
    )

    # 23. Consent Ledger
    op.create_table(
        "consent_ledger",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), default=False, nullable=False),
        sa.Column("university_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("universities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_uuid", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("consent_version", sa.String(20), default="1.0", nullable=False),
        sa.Column("consent_scope", sa.String(50), nullable=False),
        sa.Column("consent_text_version", sa.String(50), default="v2026.1", nullable=False),
        sa.Column("granted", sa.Boolean(), default=False, nullable=False),
        sa.Column("granted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("withdrawn_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_consent_ledger_consent_scope", "consent_ledger", ["consent_scope"])

    # 24. Audit Logs
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), default=False, nullable=False),
        sa.Column("university_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("universities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("actor_uuid", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("actor_role", sa.String(50), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=False),
        sa.Column("resource_id", sa.String(100), nullable=True),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("ip_address_hash", sa.String(128), nullable=True),
    )
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])

    # 25. Notification Events
    op.create_table(
        "notification_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), default=False, nullable=False),
        sa.Column("university_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("universities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recipient_role", sa.String(50), nullable=False),
        sa.Column("channel", sa.String(50), default="MOCK_CHANNEL", nullable=False),
        sa.Column("status", sa.String(50), default="PENDING", nullable=False),
        sa.Column("payload_summary", sa.Text(), nullable=False),
        sa.Column("attempts", sa.Integer(), default=0, nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
    )

    # 26. LMS Anomaly Events
    op.create_table(
        "lms_anomaly_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), default=False, nullable=False),
        sa.Column("university_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("universities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_uuid", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_hash", sa.String(128), nullable=False),
        sa.Column("anomaly_type", sa.String(50), nullable=False),
        sa.Column("severity", sa.String(50), nullable=False),
        sa.Column("nudge_sent", sa.Boolean(), default=False, nullable=False),
        sa.Column("nudge_type", sa.String(50), nullable=True),
    )
    op.create_index("ix_lms_anomaly_events_user_hash", "lms_anomaly_events", ["user_hash"])

    # 27. Enable PostgreSQL Row-Level Security (RLS) policies
    bind = op.get_bind()
    if "postgresql" in bind.engine.name:
        for tbl in RLS_TABLES:
            op.execute(f"ALTER TABLE {tbl} ENABLE ROW LEVEL SECURITY;")
            op.execute(f"ALTER TABLE {tbl} FORCE ROW LEVEL SECURITY;")
            op.execute(f"""
                CREATE POLICY tenant_isolation_{tbl} ON {tbl}
                FOR ALL
                USING (
                    university_id = NULLIF(current_setting('app.current_university_id', true), '')::uuid
                    OR NULLIF(current_setting('app.current_university_id', true), '') IS NULL
                )
                WITH CHECK (
                    university_id = NULLIF(current_setting('app.current_university_id', true), '')::uuid
                    OR NULLIF(current_setting('app.current_university_id', true), '') IS NULL
                );
            """)


def downgrade() -> None:
    bind = op.get_bind()
    if "postgresql" in bind.engine.name:
        for tbl in RLS_TABLES:
            op.execute(f"DROP POLICY IF EXISTS tenant_isolation_{tbl} ON {tbl};")
            op.execute(f"ALTER TABLE {tbl} NO FORCE ROW LEVEL SECURITY;")
            op.execute(f"ALTER TABLE {tbl} DISABLE ROW LEVEL SECURITY;")

    for tbl in reversed(RLS_TABLES):
        op.drop_table(tbl)
    op.drop_table("roles")
    op.drop_table("university_settings")
    op.drop_table("universities")
