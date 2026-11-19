from fastapi.testclient import TestClient


def test_k_anonymity_small_cohort_suppression(client: TestClient, admin_token: str):
    """
    K-Anonymity rule: Any cohort with < 15 distinct students must be suppressed.
    """
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Department Theology has 4 students in seed data (< 15)
    r_theology = client.get("/api/admin/welfare-radar?department=Theology", headers=headers)
    assert r_theology.status_code == 200
    data_theo = r_theology.json()
    assert data_theo["suppressed"] is True
    assert data_theo["reason"] == "k-anonymity threshold"
    assert data_theo["cohort_size"] is None

    # Department Law has 7 students (< 15)
    r_law = client.get("/api/admin/welfare-radar?department=Law", headers=headers)
    assert r_law.status_code == 200
    data_law = r_law.json()
    assert data_law["suppressed"] is True
    assert data_law["reason"] == "k-anonymity threshold"


def test_k_anonymity_large_cohort_allowed(client: TestClient, admin_token: str):
    """
    Cohort with >= 15 students returns aggregate metrics.
    """
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Department Computer Science has 45 students (>= 15)
    r_cs = client.get("/api/admin/welfare-radar?department=Computer%20Science", headers=headers)
    assert r_cs.status_code == 200
    data_cs = r_cs.json()
    assert data_cs["suppressed"] is False
    assert data_cs["cohort_size"] >= 15
    assert "risk_distribution" in data_cs
    assert "avg_phq9" in data_cs
    assert "avg_gad7" in data_cs
    # Verify NO individual student identities are present
    assert "students" not in data_cs
    assert "users" not in data_cs

