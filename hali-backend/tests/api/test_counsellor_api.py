from fastapi.testclient import TestClient


def test_counsellor_queue_ordering(client: TestClient, counsellor_token: str):
    headers = {"Authorization": f"Bearer {counsellor_token}"}
    response = client.get("/api/counsellor/queue", headers=headers)
    assert response.status_code == 200
    cases = response.json().get("data", [])
    assert len(cases) > 0

    # Verify severity ordering: RED before AMBER, AMBER before GREEN
    ranks = {"red": 0, "amber": 1, "green": 2}
    seen_ranks = [ranks[c["risk"]] for c in cases if c["risk"] in ranks]
    assert seen_ranks == sorted(seen_ranks), "Counsellor queue must be ordered by risk severity (RED first)"


def test_generate_pre_session_brief(client: TestClient, counsellor_token: str):
    headers = {"Authorization": f"Bearer {counsellor_token}"}
    queue_res = client.get("/api/counsellor/queue", headers=headers)
    first_case = queue_res.json()["data"][0]

    brief_res = client.post(f"/api/counsellor/briefs/{first_case['id']}/generate", headers=headers)
    assert brief_res.status_code == 200
    brief_data = brief_res.json()["data"]
    assert "summary" in brief_data
    assert len(brief_data["observations"]) == 4
    assert len(brief_data["topics"]) == 4
    assert "disclaimer" in brief_data

