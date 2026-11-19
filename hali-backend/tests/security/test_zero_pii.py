from sqlalchemy.orm import Session
from app.models.user import User, UserUniversityHash
from app.core.database import set_rls_tenant_context


def test_zero_pii_no_student_names_or_reg_numbers(db_session: Session):
    """
    CRITICAL SECURITY INVARIANT:
    The operational database must NEVER store student real names, registration numbers,
    admission numbers, or raw email addresses for students.
    """
    set_rls_tenant_context(db_session, "11111111-1111-1111-1111-111111111111")
    students = db_session.query(User).filter(User.role == "student").all()
    assert len(students) > 0

    for s in students:
        # 1. Real names and student emails must be strictly NULL
        assert s.staff_email is None, f"Student {s.id} has persisted email!"
        assert s.staff_name is None, f"Student {s.id} has persisted real name!"

        # 2. Handle must be pseudonymous (e.g. 'calm-acacia-42')
        assert "-" in s.anon_handle
        assert not s.anon_handle.startswith("CIT/")
        assert not s.anon_handle.startswith("SC211")

    # 3. UserUniversityHash stores one-way HMAC-SHA256 only (64 hex characters)
    hashes = db_session.query(UserUniversityHash).all()
    for h in hashes:
        assert len(h.user_hash) == 64
        # Must be valid hexadecimal string
        int(h.user_hash, 16)
