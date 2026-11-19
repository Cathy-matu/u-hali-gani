import pytest
from app.services.hashing.hmac_service import hash_student_reg_no


def test_hmac_deterministic():
    salt = "salt_alpha_2026"
    h1 = hash_student_reg_no("CIT/0012/2021", salt)
    h2 = hash_student_reg_no("cit/0012/2021  ", salt)
    assert h1 == h2
    assert len(h1) == 64  # SHA-256 hex string


def test_hmac_university_isolation():
    salt_a = "university_a_salt"
    salt_b = "university_b_salt"
    reg = "SC211-0042/2020"

    h_a = hash_student_reg_no(reg, salt_a)
    h_b = hash_student_reg_no(reg, salt_b)

    assert h_a != h_b


def test_hmac_empty_reg_raises():
    with pytest.raises(ValueError, match="cannot be empty"):
        hash_student_reg_no("", "salt")

