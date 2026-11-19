import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.config import settings
from app.core.database import SessionLocal, get_db
from app.core.security import create_access_token
from app.core.tenant import set_current_tenant_id, clear_tenant_context
from app.main import app
from app.models.university import University
from app.models.user import User


@pytest.fixture(scope="session")
def db_session():
    """Provides test database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def client():
    """FastAPI TestClient fixture."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def default_university(db_session: Session):
    univ = db_session.query(University).filter(
        University.id == settings.DEFAULT_UNIVERSITY_ID
    ).first()
    if not univ:
        univ = db_session.query(University).first()
    return univ


@pytest.fixture
def student_token(default_university: University, db_session: Session):
    student = db_session.query(User).filter(
        User.university_id == default_university.id,
        User.role == "student"
    ).first()
    return create_access_token(
        subject=str(student.id),
        role="student",
        university_id=str(default_university.id),
        anon_handle=student.anon_handle
    )


@pytest.fixture
def counsellor_token(default_university: University, db_session: Session):
    counsellor = db_session.query(User).filter(
        User.university_id == default_university.id,
        User.role == "counsellor"
    ).first()
    return create_access_token(
        subject=str(counsellor.id),
        role="counsellor",
        university_id=str(default_university.id),
        anon_handle=counsellor.anon_handle
    )


@pytest.fixture
def dean_token(default_university: University, db_session: Session):
    dean = db_session.query(User).filter(
        User.university_id == default_university.id,
        User.role == "dean_of_students"
    ).first()
    return create_access_token(
        subject=str(dean.id),
        role="dean_of_students",
        university_id=str(default_university.id),
        anon_handle=dean.anon_handle
    )


@pytest.fixture
def admin_token(default_university: University, db_session: Session):
    admin = db_session.query(User).filter(
        User.university_id == default_university.id,
        User.role == "university_admin"
    ).first()
    return create_access_token(
        subject=str(admin.id),
        role="university_admin",
        university_id=str(default_university.id),
        anon_handle=admin.anon_handle
    )

