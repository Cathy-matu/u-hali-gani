from fastapi.testclient import TestClient


def test_routine_green_checkin(client: TestClient, student_token: str):
    headers = {"Authorization": f"Bearer {student_token}"}
    payload = {
        "phq9_scores": [0, 0, 1, 0, 1, 0, 0, 1, 0],
        "gad7_scores": [0, 1, 0, 0, 1, 0, 0],
        "auditc_scores": [1, 0, 0],
        "free_text_or_transcript": "Feeling okay today, just finishing an assignment."
    }

    response = client.post("/api/checkins", json=payload, headers=headers)
    assert response.status_code == 200
    res = response.json()
    assert res["data"]["risk_level"] == "GREEN"
    assert res["data"]["action"]["bypass_ai"] is False


def test_amber_routing_moderate_anxiety(client: TestClient, student_token: str):
    headers = {"Authorization": f"Bearer {student_token}"}
    payload = {
        "phq9_scores": [1, 1, 1, 1, 1, 1, 1, 0, 0],  # 7
        "gad7_scores": [2, 2, 2, 1, 2, 1, 1],         # 11 (Moderate >= 10)
        "auditc_scores": [1, 0, 0]
    }

    response = client.post("/api/checkins", json=payload, headers=headers)
    assert response.status_code == 200
    res = response.json()
    assert res["data"]["risk_level"] == "AMBER"
    assert res["data"]["action"]["recommend_booking"] is True


def test_critical_rule_phq9_item9_triggers_red_imminent_risk(client: TestClient, student_token: str):
    headers = {"Authorization": f"Bearer {student_token}"}
    # Even with sub-threshold total score (PHQ-9 total 5), Item 9 = 1 MUST trigger RED!
    payload = {
        "phq9_scores": [0, 0, 1, 1, 1, 0, 1, 0, 1],  # Item 9 is positive!
        "gad7_scores": [0, 0, 0, 0, 0, 0, 0],
        "auditc_scores": [0, 0, 0]
    }

    response = client.post("/api/checkins", json=payload, headers=headers)
    assert response.status_code == 200
    res = response.json()
    assert res["data"]["risk_level"] == "RED"
    assert res["data"]["is_item9_positive"] is True
    assert res["data"]["action"]["bypass_ai"] is True
    assert res["data"]["action"]["human_escalation_required"] is True
    assert res["data"]["action"]["clinic_callback"] is True
    assert len(res["data"]["action"]["crisis_hotlines"]) > 0


def test_invalid_score_submission_rejected(client: TestClient, student_token: str):
    headers = {"Authorization": f"Bearer {student_token}"}
    payload = {
        "phq9_scores": [1, 2, 3],  # Incomplete
        "gad7_scores": [1, 2, 3, 4, 5, 6, 7]
    }
    response = client.post("/api/checkins", json=payload, headers=headers)
    assert response.status_code == 422


def test_quick_checkin_item9_red_frontend_format(client: TestClient):
    """Verify frontend short mode with Item 9 triggers RED immediately."""
    payload = {
        "phq1": 1,
        "phq2": 1,
        "gad1": 0,
        "gad2": 1,
        "phq9": 2  # Safety item positive
    }
    response = client.post("/api/assessments", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["risk"] == "red"
    assert res["data"]["is_item9_positive"] is True


def test_arbitrary_string_user_uuid_handled(client: TestClient):
    """Verify non-UUID strings like 'uuid' or handles do not cause 500 error."""
    payload = {
        "user_uuid": "uuid",
        "phq9_scores": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        "gad7_scores": [0, 0, 0, 0, 0, 0, 0]
    }
    response = client.post("/api/checkins", json=payload)
    assert response.status_code == 200

