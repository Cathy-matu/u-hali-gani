from fastapi.testclient import TestClient


def test_get_counsellors_and_slots(client: TestClient):
    r_c = client.get("/api/counsellors")
    assert r_c.status_code == 200
    c_list = r_c.json()
    assert len(c_list) >= 3

    r_s = client.get("/api/slots")
    assert r_s.status_code == 200
    slots = r_s.json()
    assert "09:00" in slots
    assert "14:00" in slots


def test_book_appointment(client: TestClient, student_token: str):
    headers = {"Authorization": f"Bearer {student_token}"}
    payload = {
        "who": "Dr. Amina Wekesa",
        "when": "Tomorrow 10:30",
        "type": "In-person"
    }
    r = client.post("/api/bookings", json=payload, headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["who"] == "Dr. Amina Wekesa"
    assert data["type"] == "In-person"
    assert data["status"] == "Requested"


def test_send_and_receive_messages(client: TestClient, student_token: str):
    headers = {"Authorization": f"Bearer {student_token}"}
    payload = {
        "text": "Hello, I would like to speak to a counsellor about exam stress."
    }
    r = client.post("/api/messages", json=payload, headers=headers)
    assert r.status_code == 200
    assert r.json()["b"] is False

