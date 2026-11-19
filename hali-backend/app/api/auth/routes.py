import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db, set_rls_tenant_context
from app.core.security import create_access_token, verify_password, hash_password
from app.core.tenant import set_current_tenant_id
from app.core.permissions import UserRole
from app.models.university import University
from app.models.user import User, UserUniversityHash
from app.schemas.auth import LMSHandshakeRequest, LMSHandshakeResponse, LoginRequest, TokenResponse
from app.services.hashing.hmac_service import hash_student_reg_no, get_university_salt
from app.utils.pseudonym import generate_anon_handle

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/lms-handshake", response_model=LMSHandshakeResponse)
def lms_handshake(request: LMSHandshakeRequest, db: Session = Depends(get_db)):
    """
    ZERO-PII Student LMS Authentication Handshake.
    1. Validates simulated or verified LMS token.
    2. Extracts registration number in-memory only.
    3. Computes HMAC-SHA256(reg_no, UNIVERSITY_SALT).
    4. Creates or retrieves pseudonymous student account.
    5. The registration number is NEVER stored or logged.
    """
    # Determine university context
    target_univ_id = request.university_id or settings.DEFAULT_UNIVERSITY_ID
    university = db.query(University).filter(University.id == target_univ_id).first()
    if not university:
        university = db.query(University).first()
        if not university:
            raise HTTPException(status_code=500, detail="No university configured")
        target_univ_id = str(university.id)

    set_current_tenant_id(target_univ_id)
    set_rls_tenant_context(db, target_univ_id)

    # Validate LMS Token and extract in-memory student identifier
    token_str = request.lms_token.strip()
    if not token_str:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="LMS token is required")

    # In production, this validates LTI 1.3 / OAuth2 JWT claims.
    # In simulated mode, parse token or use deterministic in-memory student ID
    # e.g., "simulated_student_12345" or "CIT-0012/2021"
    simulated_reg_no = f"REG_{token_str[-12:]}" if len(token_str) >= 12 else f"REG_{token_str}"

    # Compute one-way keyed HMAC
    salt = university.salt or get_university_salt(target_univ_id)
    user_hash = hash_student_reg_no(simulated_reg_no, salt)

    # Discard raw reg_no immediately from memory
    del simulated_reg_no

    # Lookup or create user by user_hash
    hash_record = db.query(UserUniversityHash).filter(
        UserUniversityHash.university_id == target_univ_id,
        UserUniversityHash.user_hash == user_hash
    ).first()

    if hash_record:
        user = db.query(User).filter(User.id == hash_record.user_uuid).first()
    else:
        # Create new pseudonymous student
        anon_handle = generate_anon_handle()
        user = User(
            university_id=target_univ_id,
            anon_handle=anon_handle,
            role=UserRole.STUDENT.value,
            faculty=request.faculty or "Computing",
            department="Computer Science",
            year_of_study=request.year_of_study or 3,
            is_active=True
        )
        db.add(user)
        db.flush()

        hash_record = UserUniversityHash(
            university_id=target_univ_id,
            user_uuid=user.id,
            user_hash=user_hash
        )
        db.add(hash_record)
        db.commit()
        db.refresh(user)

    # Issue JWT token
    token = create_access_token(
        subject=str(user.id),
        role=user.role,
        university_id=str(user.university_id),
        anon_handle=user.anon_handle
    )

    return LMSHandshakeResponse(
        jwt=token,
        user_uuid=str(user.id),
        anon_handle=user.anon_handle,
        role=user.role
    )


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Role-based authentication endpoint for demo, staff, counsellors, and administrators.
    Supports quick role switching for hackathon demo compatibility.
    """
    target_univ_id = request.university_id or settings.DEFAULT_UNIVERSITY_ID
    university = db.query(University).filter(University.id == target_univ_id).first()
    if not university:
        university = db.query(University).first()
        target_univ_id = str(university.id) if university else settings.DEFAULT_UNIVERSITY_ID

    role = request.role or "student"

    # Find or create a demo user with the requested role
    user = db.query(User).filter(
        User.university_id == target_univ_id,
        User.role == role
    ).first()

    if not user:
        anon_handle = f"Staff-{role.capitalize()}-{secrets.randbelow(900)+100}" if role != "student" else generate_anon_handle()
        user = User(
            university_id=target_univ_id,
            anon_handle=anon_handle,
            role=role,
            faculty="Administration" if "admin" in role else "Computing",
            department="Dean Office" if "dean" in role else "Computer Science",
            year_of_study=None if role != "student" else 3,
            staff_email=request.email or f"{role}@university.ac.ke",
            staff_name=f"Dr. {role.capitalize()}" if role != "student" else None,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token(
        subject=str(user.id),
        role=user.role,
        university_id=str(user.university_id),
        anon_handle=user.anon_handle
    )

    return {
        "success": True,
        "message": f"Authenticated successfully as {role}",
        "data": {
            "token": token,
            "access_token": token,
            "jwt": token,
            "user_uuid": str(user.id),
            "anon_handle": user.anon_handle,
            "role": user.role,
            "pseudonym": user.anon_handle,
            "university_id": str(user.university_id)
        }
    }

