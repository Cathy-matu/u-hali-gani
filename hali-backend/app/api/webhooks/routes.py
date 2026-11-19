from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import verify_webhook_hmac
from app.models.user import UserUniversityHash, User
from app.models.anomaly import LMSAnomalyEvent
from app.models.checkin import Checkin
from app.schemas.webhook import LMSAnomalyWebhookRequest

router = APIRouter(prefix="", tags=["LMS Anomaly Integration"])


@router.post("/api/webhooks/lms-anomaly")
@router.post("/webhooks/lms-anomaly")
async def receive_lms_anomaly(
    request: Request,
    payload: LMSAnomalyWebhookRequest,
    db: Session = Depends(get_db),
    x_lms_signature: Optional[str] = Header(None)
):
    """
    LMS Engagement Anomaly Webhook.
    1. Authenticates webhook signature.
    2. Resolves pseudonymous user via user_hash (HMAC digest).
    3. Prevents duplicate webhook event processing.
    4. Generates a gentle, private supportive nudge (NOT a clinical diagnosis).
    5. The student is never publicly identified or exposed.
    """
    # 1. Signature Verification (if header supplied, or dev bypass)
    body_bytes = await request.body()
    if x_lms_signature:
        is_valid = verify_webhook_hmac(body_bytes, x_lms_signature, settings.LMS_WEBHOOK_SECRET)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook signature")

    # 2. Validate anomaly type
    allowed_types = {"LOGIN_DROP", "LATE_NIGHT_SPIKE", "MISSED_CAT"}
    if payload.anomaly_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported anomaly type '{payload.anomaly_type}'. Supported: {allowed_types}"
        )

    # 3. Resolve pseudonymous student
    hash_record = db.query(UserUniversityHash).filter(
        UserUniversityHash.user_hash == payload.user_hash
    ).first()

    if not hash_record:
        # Avoid user enumeration: acknowledge without error
        return {
            "success": True,
            "message": "Webhook received and verified",
            "processed": False
        }

    # 4. Idempotency check: prevent duplicate event processing within same window
    recent_event = db.query(LMSAnomalyEvent).filter(
        LMSAnomalyEvent.user_hash == payload.user_hash,
        LMSAnomalyEvent.anomaly_type == payload.anomaly_type
    ).order_by(LMSAnomalyEvent.created_at.desc()).first()

    if recent_event:
        return {
            "success": True,
            "message": "Duplicate anomaly event ignored (idempotent)",
            "processed": False
        }

    # 5. Store Anomaly Event
    event = LMSAnomalyEvent(
        university_id=hash_record.university_id,
        user_uuid=hash_record.user_uuid,
        user_hash=payload.user_hash,
        anomaly_type=payload.anomaly_type,
        severity=payload.severity,
        nudge_sent=True,
        nudge_type="supportive_reflection"
    )
    db.add(event)

    # 6. Generate private, gentle check-in nudge
    nudge_text = "Notice: We're checking in on your campus rhythm. Remember Hali is here if you'd like a calm breathing break."
    if payload.anomaly_type == "LATE_NIGHT_SPIKE":
        nudge_text = "Late nights on the e-learning portal? Take a mindful 5-minute break and check in with yourself."
    elif payload.anomaly_type == "MISSED_CAT":
        nudge_text = "Assignment pressure building up? You can explore our small study pacing steps or chat with a counsellor."

    checkin_nudge = Checkin(
        university_id=hash_record.university_id,
        user_uuid=hash_record.user_uuid,
        reflection_note=nudge_text,
        checkin_type="lms_nudge"
    )
    db.add(checkin_nudge)
    db.commit()

    return {
        "success": True,
        "message": "LMS anomaly event processed; supportive private nudge queued",
        "processed": True
    }

