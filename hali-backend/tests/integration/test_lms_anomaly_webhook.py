from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import UserUniversityHash
from app.models.anomaly import LMSAnomalyEvent


def test_lms_anomaly_webhook_processes_supportive_nudge(client: TestClient, db_session: Session):
    hash_rec = db_session.query(UserUniversityHash).first()
    assert hash_rec is not None

    # Clear prior anomaly events for this test hash to ensure clean idempotent run
    db_session.query(LMSAnomalyEvent).filter(
        LMSAnomalyEvent.user_hash == hash_rec.user_hash
    ).delete()
    db_session.commit()

    payload = {
        "user_hash": hash_rec.user_hash,
        "anomaly_type": "LATE_NIGHT_SPIKE",
        "severity": "MEDIUM"
    }

    response = client.post("/api/webhooks/lms-anomaly", json=payload)
    assert response.status_code == 200
    assert response.json()["processed"] is True

    # Duplicate submission is handled idempotently
    response_dup = client.post("/api/webhooks/lms-anomaly", json=payload)
    assert response_dup.status_code == 200
    assert response_dup.json()["processed"] is False
    assert "Duplicate anomaly event ignored" in response_dup.json()["message"]


def test_unsupported_anomaly_type_rejected(client: TestClient):
    payload = {
        "user_hash": "dummy_hash_123",
        "anomaly_type": "CLINICAL_DEPRESSION_DETECTED",  # LMS cannot diagnose
        "severity": "HIGH"
    }
    response = client.post("/api/webhooks/lms-anomaly", json=payload)
    assert response.status_code == 400
