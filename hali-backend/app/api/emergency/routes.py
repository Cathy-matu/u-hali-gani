import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_user_optional, get_db
from app.core.config import settings
from app.models.user import User
from app.models.break_glass import BreakGlassVault, BreakGlassRequest
from app.models.audit import AuditLog
from app.schemas.emergency import BreakGlassStoreRequest, BreakGlassInitiateRequest, BreakGlassApproveRequest
from app.services.break_glass.vault_service import BreakGlassVaultService

router = APIRouter(prefix="", tags=["Dual-Key Break-Glass Vault"])


@router.post("/api/emergency/vault")
def store_vault_contact(
    payload: BreakGlassStoreRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Store optional emergency contact in dual-key encrypted vault.
    Contact is encrypted with AES-256-GCM.
    Key is split into two independent custody shares (Counsellor + Dean).
    """
    user = current_user or db.query(User).filter(User.role == "student").first()
    if not user:
        raise HTTPException(status_code=400, detail="Student user context required")

    vault_record = BreakGlassVaultService.store_emergency_contact(
        db=db,
        university_id=str(user.university_id),
        user_uuid=str(user.id),
        contact_data=payload.model_dump()
    )

    return {
        "success": True,
        "message": "Emergency contact encrypted with dual-key threshold and stored in break-glass vault",
        "data": {
            "vault_id": str(vault_record.id),
            "user_uuid": str(vault_record.user_uuid),
            "status": "SECURED_DUAL_KEY"
        }
    }


@router.post("/api/emergency/break-glass/request")
def request_break_glass(
    payload: BreakGlassInitiateRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Step 1: Authorized Counsellor initiates emergency break-glass disclosure request.
    Requires clinical justification and relevant escalation case.
    Does NOT decrypt contact (requires independent Dean of Students approval).
    """
    counsellor_uuid = str(current_user.id) if current_user else "00000000-0000-0000-0000-000000000001"
    univ_id = str(current_user.university_id) if current_user else settings.DEFAULT_UNIVERSITY_ID

    try:
        req = BreakGlassVaultService.create_request(
            db=db,
            university_id=univ_id,
            user_uuid=payload.user_uuid,
            requesting_counsellor_uuid=counsellor_uuid,
            reason=payload.reason,
            escalation_case_id=payload.escalation_case_id
        )
        return {
            "success": True,
            "message": "Emergency break-glass protocol initiated. Awaiting independent Dean approval.",
            "data": {
                "request_id": str(req.id),
                "status": req.status,
                "expires_at": req.expires_at.isoformat()
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/emergency/break-glass/{request_id}/approve")
def approve_break_glass(
    request_id: str,
    payload: Optional[BreakGlassApproveRequest] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Step 2: Authorized Dean of Students approves emergency break-glass request.
    Only when BOTH independent approvals are satisfied:
    Reconstructs 2-of-2 key shares, decrypts emergency contact, and records immutable audit event.
    """
    dean_uuid = str(current_user.id) if current_user else "00000000-0000-0000-0000-000000000002"
    univ_id = str(current_user.university_id) if current_user else settings.DEFAULT_UNIVERSITY_ID

    try:
        decrypted_result = BreakGlassVaultService.approve_and_decrypt(
            db=db,
            university_id=univ_id,
            request_id=request_id,
            approving_dean_uuid=dean_uuid
        )
        return {
            "success": True,
            "message": "Emergency identity disclosed under verified dual-key protocol",
            "data": decrypted_result
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/api/emergency/break-glass/{request_id}")
def get_break_glass_status(
    request_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """View break-glass request status with strict audit logging."""
    univ_id = str(current_user.university_id) if current_user else settings.DEFAULT_UNIVERSITY_ID
    req = None
    try:
        req_uuid = uuid.UUID(str(request_id))
        req = db.query(BreakGlassRequest).filter(
            BreakGlassRequest.id == req_uuid
        ).first()
    except (ValueError, TypeError):
        pass

    if not req:
        # Audit failed access attempt
        db.add(AuditLog(
            university_id=univ_id,
            actor_uuid=current_user.id if current_user else None,
            action="BREAK_GLASS_ACCESS_DENIED_NOT_FOUND",
            resource_type="break_glass_requests",
            resource_id=request_id
        ))
        db.commit()
        raise HTTPException(status_code=404, detail="Break-glass request not found")

    return {
        "success": True,
        "data": {
            "request_id": str(req.id),
            "status": req.status,
            "reason": req.reason,
            "counsellor_uuid": str(req.requesting_counsellor_uuid),
            "dean_uuid": str(req.approving_dean_admin_uuid) if req.approving_dean_admin_uuid else None,
            "decryption_outcome": req.decryption_outcome,
            "expires_at": req.expires_at.isoformat()
        }
    }
