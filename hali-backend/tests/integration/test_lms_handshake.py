from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User, UserUniversityHash


def test_lms_handshake_creates_pseudonymous_student(client: TestClient, db_session: Session):
    payload = {
        "lms_token": "verified_lms_student_session_token_xyz_881",
        "faculty": "Computing",
        "year_of_study": 3
    }

    response = client.post("/api/auth/lms-handshake", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "jwt" in data
    assert "user_uuid" in data
    assert "anon_handle" in data
    assert data["role"] == "student"

    # Verify student exists in DB under pseudonymous handle
    user = db_session.query(User).filter(User.id == data["user_uuid"]).first()
    assert user is not None
    assert user.anon_handle == data["anon_handle"]
    # Verify ZERO-PII: staff_email, staff_name are None
    assert user.staff_email is None
    assert user.staff_name is None


def test_lms_handshake_prevents_duplicate_accounts(client: TestClient):
    payload = {
        "lms_token": "verified_token_for_same_student_repeat_test",
        "faculty": "Computing",
        "year_of_study": 2
    }

    # First request
    r1 = client.post("/api/auth/lms-handshake", json=payload)
    assert r1.status_code == 200
    d1 = r1.json()

    # Second request with same student token
    r2 = client.post("/api/auth/lms-handshake", json=payload)
    assert r2.status_code == 200
    d2 = r2.json()

    # Must resolve to same pseudonymous user UUID
    assert d1["user_uuid"] == d2["user_uuid"]
    assert d1["anon_handle"] == d2["anon_handle"]

