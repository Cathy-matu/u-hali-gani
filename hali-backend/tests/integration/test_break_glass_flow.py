from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.audit import AuditLog


def test_full_break_glass_dual_key_protocol(
    client: TestClient,
    db_session: Session,
    counsellor_token: str,
    dean_token: str
):
    student = db_session.query(User).filter(User.role == "student").first()
    assert student is not None

    # Step 1: Store emergency contact in vault
    store_payload = {
        "contact_name": "Mrs. Faith Kimani",
        "relationship": "Mother",
        "phone": "+254 722 334 455",
        "notes": "Emergency family contact in Eldoret"
    }
    r_store = client.post("/api/emergency/vault", json=store_payload)
    assert r_store.status_code == 200

    # Step 2: Counsellor initiates emergency break-glass request
    counsellor_headers = {"Authorization": f"Bearer {counsellor_token}"}
    req_payload = {
        "user_uuid": str(student.id),
        "reason": "Student presented with imminent crisis and self-harm intent requiring immediate welfare check",
        "escalation_case_id": None
    }
    r_req = client.post("/api/emergency/break-glass/request", json=req_payload, headers=counsellor_headers)
    assert r_req.status_code == 200
    req_id = r_req.json()["data"]["request_id"]
    assert r_req.json()["data"]["status"] == "PENDING_APPROVAL"

    # Step 3: Dean of Students approves and triggers dual-key reconstruction
    dean_headers = {"Authorization": f"Bearer {dean_token}"}
    r_approve = client.post(f"/api/emergency/break-glass/{req_id}/approve", json={}, headers=dean_headers)
    assert r_approve.status_code == 200
    res_data = r_approve.json()["data"]

    assert res_data["status"] == "APPROVED_DECRYPTED"
    assert res_data["decrypted_contact"]["contact_name"] == "Mrs. Faith Kimani"
    assert res_data["decrypted_contact"]["phone"] == "+254 722 334 455"

    # Step 4: Verify audit log recorded
    audit_event = db_session.query(AuditLog).filter(
        AuditLog.action == "BREAK_GLASS_APPROVED_AND_DECRYPTED"
    ).order_by(AuditLog.created_at.desc()).first()
    assert audit_event is not None
    assert audit_event.details["outcome"] == "SUCCESS"

