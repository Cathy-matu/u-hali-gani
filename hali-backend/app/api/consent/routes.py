from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_optional, get_db
from app.models.user import User
from app.models.consent import ConsentLedger
from app.schemas.consent import ConsentUpdateRequest, ConsentWithdrawRequest

router = APIRouter(prefix="", tags=["Research Consent Ledger"])


@router.get("/api/consent")
@router.get("/consent")
def get_user_consent(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Retrieve active student research consent ledger."""
    user = current_user or db.query(User).filter(User.role == "student").first()
    if not user:
        return {"research": False, "recontact": False}

    records = db.query(ConsentLedger).filter(
        ConsentLedger.user_uuid == user.id,
        ConsentLedger.university_id == user.university_id
    ).all()

    consent_map = {r.consent_scope: r.granted for r in records}

    return {
        "success": True,
        "data": {
            "aggregate_stats": consent_map.get("aggregate_stats", True),
            "deidentified_research": consent_map.get("deidentified_research", False),
            "recontact_studies": consent_map.get("recontact_studies", False),
            # Frontend compatibility flags:
            "research": consent_map.get("deidentified_research", False),
            "recontact": consent_map.get("recontact_studies", False)
        },
        # Direct root keys for frontend
        "research": consent_map.get("deidentified_research", False),
        "recontact": consent_map.get("recontact_studies", False)
    }


@router.post("/api/consent")
@router.put("/api/consent")
@router.put("/consent")
def update_user_consent(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Update or grant versioned research consent.
    Accepts specific scope or frontend dictionary {research: bool, recontact: bool}.
    """
    user = current_user or db.query(User).filter(User.role == "student").first()
    if not user:
        raise HTTPException(status_code=400, detail="Student context required")

    # Map frontend keys if present
    scopes_to_update = {}
    if "research" in payload:
        scopes_to_update["deidentified_research"] = bool(payload["research"])
    if "recontact" in payload:
        scopes_to_update["recontact_studies"] = bool(payload["recontact"])
    if "scope" in payload:
        scopes_to_update[payload["scope"]] = bool(payload.get("granted", True))

    now = datetime.now(timezone.utc)
    for scope, granted in scopes_to_update.items():
        record = db.query(ConsentLedger).filter(
            ConsentLedger.user_uuid == user.id,
            ConsentLedger.consent_scope == scope
        ).first()

        if record:
            record.granted = granted
            if granted:
                record.granted_at = now
                record.withdrawn_at = None
            else:
                record.withdrawn_at = now
        else:
            record = ConsentLedger(
                university_id=user.university_id,
                user_uuid=user.id,
                consent_version="1.0",
                consent_scope=scope,
                consent_text_version="v2026.1",
                granted=granted,
                granted_at=now if granted else None,
                withdrawn_at=now if not granted else None
            )
            db.add(record)

    db.commit()
    return {
        "success": True,
        "message": "Consent ledger updated",
        "data": payload
    }


@router.post("/api/consent/withdraw")
@router.post("/consent/withdraw")
def withdraw_consent(
    payload: ConsentWithdrawRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Explicitly withdraw research consent."""
    user = current_user or db.query(User).filter(User.role == "student").first()
    if not user:
        raise HTTPException(status_code=400, detail="Student context required")

    record = db.query(ConsentLedger).filter(
        ConsentLedger.user_uuid == user.id,
        ConsentLedger.consent_scope == payload.scope
    ).first()

    if record:
        record.granted = False
        record.withdrawn_at = datetime.now(timezone.utc)
        db.commit()

    return {
        "success": True,
        "message": f"Consent for '{payload.scope}' withdrawn successfully"
    }

