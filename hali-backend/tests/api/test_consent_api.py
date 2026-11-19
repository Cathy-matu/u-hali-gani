from fastapi.testclient import TestClient


def test_consent_lifecycle(client: TestClient, student_token: str):
    headers = {"Authorization": f"Bearer {student_token}"}

    # 1. Update consent (frontend dict style)
    r_update = client.put("/api/consent", json={"research": True, "recontact": False}, headers=headers)
    assert r_update.status_code == 200

    # 2. Retrieve consent
    r_get = client.get("/api/consent", headers=headers)
    assert r_get.status_code == 200
    data = r_get.json()
    assert data["research"] is True
    assert data["recontact"] is False

    # 3. Withdraw consent
    r_withdraw = client.post("/api/consent/withdraw", json={"scope": "deidentified_research"}, headers=headers)
    assert r_withdraw.status_code == 200

    # 4. Verify withdrawal
    r_verify = client.get("/api/consent", headers=headers)
    assert r_verify.status_code == 200
    assert r_verify.json()["research"] is False

