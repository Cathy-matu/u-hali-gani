import uuid
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import set_rls_tenant_context
from app.models.user import User


def test_cross_tenant_isolation_rls(db_session: Session):
    """
    PostgreSQL Row-Level Security (RLS) Tenant Isolation Test.
    A connection operating under University 1 must NEVER access University 2 records.
    """
    univ_1 = "11111111-1111-1111-1111-111111111111"
    univ_2 = "22222222-2222-2222-2222-222222222222"

    # Context 1: University 1
    set_rls_tenant_context(db_session, univ_1)
    users_u1 = db_session.query(User).filter(User.university_id == univ_1).all()
    assert len(users_u1) > 0

    # Querying University 2 records while in University 1 context must return 0 records under RLS
    users_cross = db_session.query(User).filter(User.university_id == univ_2).all()
    assert len(users_cross) == 0

    # Context 2: University 2
    set_rls_tenant_context(db_session, univ_2)
    users_u2_context = db_session.query(User).filter(User.university_id == univ_1).all()
    assert len(users_u2_context) == 0

    # Reset back to University 1
    set_rls_tenant_context(db_session, univ_1)
