import pytest
from app.services.pii_redaction.redactor import PIIRedactor


def test_redact_phone_and_email():
    text = "Call me on 0722123456 or email student@university.ac.ke for the assignment."
    res = PIIRedactor.redact(text)
    assert "[PHONE]" in res["redacted_text"]
    assert "[EMAIL]" in res["redacted_text"]
    assert "0722123456" not in res["redacted_text"]
    assert "student@university.ac.ke" not in res["redacted_text"]
    assert res["redaction_count"] == 2
    assert res["redaction_applied"] is True


def test_redact_registration_number():
    text = "My reg number is CIT/00123/2021 and my exam card is ready."
    res = PIIRedactor.redact(text)
    assert "[REGISTRATION_NUMBER]" in res["redacted_text"]
    assert "CIT/00123/2021" not in res["redacted_text"]


def test_redact_sheng_hostel_and_lecturer():
    text = "Nilikuwa hostel ya XYZ na lecturer John alisema hatuna class Juja leo."
    res = PIIRedactor.redact(text)
    assert "[HOSTEL]" in res["redacted_text"]
    assert "[LECTURER]" in res["redacted_text"]
    assert "[LOCATION]" in res["redacted_text"]
    assert "hostel ya XYZ" not in res["redacted_text"]
    assert "John" not in res["redacted_text"]
    assert "Juja" not in res["redacted_text"]


def test_redact_common_names():
    text = "Kamau and Wanjiku were studying together in the library."
    res = PIIRedactor.redact(text)
    assert "[PERSON]" in res["redacted_text"]
    assert "Kamau" not in res["redacted_text"]
    assert "Wanjiku" not in res["redacted_text"]

