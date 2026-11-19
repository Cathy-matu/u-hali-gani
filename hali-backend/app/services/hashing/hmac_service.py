import hmac
import hashlib
from typing import Optional
from app.core.config import settings


def hash_student_reg_no(reg_no: str, university_salt: str) -> str:
    """
    Compute deterministic HMAC-SHA256 digest of student registration number.
    The raw registration number is processed in memory and NEVER persisted.
    """
    if not reg_no or not reg_no.strip():
        raise ValueError("Registration number cannot be empty")
    
    clean_reg = reg_no.strip().upper()
    digest = hmac.new(
        university_salt.encode("utf-8"),
        clean_reg.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    return digest


def get_university_salt(university_id: str) -> str:
    """Retrieve university-specific salt from secure configuration."""
    salts = settings.get_university_salts()
    salt = salts.get(str(university_id))
    if not salt:
        # Fallback to deterministic university derivation for demo/test
        salt = hmac.new(
            settings.SECRET_KEY.encode(),
            str(university_id).encode(),
            hashlib.sha256
        ).hexdigest()
    return salt

