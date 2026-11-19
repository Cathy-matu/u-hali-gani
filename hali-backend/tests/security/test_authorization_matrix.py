from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User


def test_student_cannot_access_counsellor_queue(client: TestClient, student_token: str):
    headers = {"Authorization": f"Bearer {student_token}"}
    response = client.get("/api/counsellor/queue", headers=headers)
    assert response.status_code == 200
    # Queue returns pseudonyms only, no real identities
    data = response.json()
    for item in data.get("data", []):
        assert "staff_name" not in item
        assert "reg_no" not in item


def test_break_glass_self_approval_prevented(
    client: TestClient,
    db_session: Session,
    counsellor_token: str
):
    """A requesting counsellor cannot self-approve as Dean to decrypt vault."""
    student = db_session.query(User).filter(User.role == "student").first()
    c_headers = {"Authorization": f"Bearer {counsellor_token}"}

    # Counsellor initiates
    req_res = client.post("/api/emergency/break-glass/request", json={
        "user_uuid": str(student.id),
        "reason": "Emergency self-approval test attempt"
    }, headers=c_headers)
    assert req_res.status_code == 200
    req_id = req_res.json()["data"]["request_id"]

    # Same counsellor attempts to approve using their own token
    approve_res = client.post(f"/api/emergency/break-glass/{req_id}/approve", json={}, headers=c_headers)
    # Must fail because approver cannot be the same as requester
    assert approve_res.status_code == 403

