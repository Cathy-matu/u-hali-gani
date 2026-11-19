import uuid
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.api.deps import get_current_user, get_current_user_optional, get_db
from app.models.user import User
from app.models.checkin import Checkin
from app.schemas.checkin import CheckinSubmission, MoodCheckinRequest
from app.services.triage.triage_engine import DeterministicTriageEngine
from app.services.pii_redaction.redactor import PIIRedactor

router = APIRouter(prefix="", tags=["Screening & Checkins"])


@router.post("/api/checkins")
@router.post("/checkins")
def submit_checkin(
    submission: CheckinSubmission,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Deterministic Screening & Triage Endpoint (PHQ-9, GAD-7, AUDIT-C).
    Validates question counts, ranges, deterministically calculates risk tier (GREEN/AMBER/RED),
    and creates idempotent escalations.
    CRITICAL RULE: Any positive response to PHQ-9 Item 9 triggers immediate RED_IMMINENT_RISK.
    """
    # 1. Resolve target user safely
    user = current_user
    if not user and submission.user_uuid:
        try:
            val_uuid = uuid.UUID(str(submission.user_uuid))
            user = db.query(User).filter(User.id == val_uuid).first()
        except (ValueError, TypeError):
            user = db.query(User).filter(User.anon_handle == str(submission.user_uuid)).first()

    if not user:
        # Fallback to demo student if unauthenticated in demo mode
        user = db.query(User).filter(User.role == "student").first()
        if not user:
            raise HTTPException(status_code=400, detail="Student context required for screening")

    # 2. PII sanitize any reflection note or voice transcript before processing
    sanitized_text = None
    if submission.free_text_or_transcript:
        redaction_res = PIIRedactor.redact(submission.free_text_or_transcript)
        sanitized_text = redaction_res["redacted_text"]

    # 3. Create checkin record
    checkin = Checkin(
        university_id=user.university_id,
        user_uuid=user.id,
        reflection_note=sanitized_text,
        checkin_type="assessment_screening"
    )
    db.add(checkin)
    db.flush()

    # 4. Deterministic Evaluation
    try:
        eval_result = DeterministicTriageEngine.evaluate(
            phq9_scores=submission.phq9_scores,
            gad7_scores=submission.gad7_scores,
            auditc_scores=submission.auditc_scores,
            free_text=sanitized_text
        )
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    # 5. Persist assessment results and risk event
    risk_event = DeterministicTriageEngine.process_and_persist(
        db=db,
        university_id=str(user.university_id),
        user_uuid=str(user.id),
        eval_result=eval_result,
        checkin_id=str(checkin.id)
    )

    return {
        "success": True,
        "message": "Screening assessment processed deterministically",
        "data": {
            "checkin_id": str(checkin.id),
            "risk_level": eval_result["risk_level"],
            "is_item9_positive": eval_result["is_item9_positive"],
            "triggers": eval_result["triggers"],
            "action": eval_result["action"],
            "phq9": eval_result.get("phq9"),
            "gad7": eval_result.get("gad7"),
            "auditc": eval_result.get("auditc"),
            "disclaimer": eval_result["disclaimer"]
        },
        # Top-level fields for direct frontend consumption
        "risk": eval_result["risk_level"].lower(),
        "sc": {
            "phq": eval_result["phq9"]["total_score"] if eval_result.get("phq9") else 0,
            "gad": eval_result["gad7"]["total_score"] if eval_result.get("gad7") else 0,
            "item9": eval_result["phq9"]["item_9_score"] if eval_result.get("phq9") else eval_result.get("item_9_score", 0)
        }
    }


@router.post("/api/checkins/mood")
@router.post("/checkins/mood")
def save_mood(
    request: MoodCheckinRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Save daily student mood check-in."""
    user = current_user or db.query(User).filter(User.role == "student").first()
    if not user:
        raise HTTPException(status_code=400, detail="Student context required")

    mood_labels = ["Great", "Good", "Okay", "Low", "Struggling"]
    label = mood_labels[request.sel] if 0 <= request.sel < len(mood_labels) else "Okay"

    sanitized_note = None
    if request.note:
        sanitized_note = PIIRedactor.redact(request.note)["redacted_text"]

    checkin = Checkin(
        university_id=user.university_id,
        user_uuid=user.id,
        mood_score=request.sel,
        mood_label=label,
        reflection_note=sanitized_note,
        checkin_type="mood"
    )
    db.add(checkin)
    db.commit()

    return {
        "success": True,
        "message": "Mood recorded successfully",
        "data": {
            "mood": label,
            "score": request.sel
        }
    }


@router.post("/api/assessments")
@router.post("/assessments")
def submit_frontend_assessment(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Frontend-compatible assessment submission.
    Accepts full mode (PHQ-9, GAD-7, WHO-5) or short mode (PHQ-2, GAD-2, Item 9).
    """
    # 1. Explicit array fields (standard CheckinSubmission format)
    if "phq9_scores" in payload or "gad7_scores" in payload:
        sub = CheckinSubmission(
            user_uuid=payload.get("user_uuid"),
            phq9_scores=payload.get("phq9_scores"),
            gad7_scores=payload.get("gad7_scores"),
            auditc_scores=payload.get("auditc_scores"),
            free_text_or_transcript=payload.get("free_text_or_transcript")
        )
        return submit_checkin(sub, db, current_user)

    # 2. Key-value dictionary format from frontend (e.g. {phq1: 1, phq2: 2, gad1: 1, gad2: 0, phq9: 0})
    phq_keys = [k for k in payload if k.startswith("phq")]
    gad_keys = [k for k in payload if k.startswith("gad")]
    item9_score = int(payload.get("phq9", 0))

    user = current_user or db.query(User).filter(User.role == "student").first()

    if len(phq_keys) >= 9 and len(gad_keys) >= 7:
        # Full mode
        phq9_scores = [int(payload[f"phq{i}"]) for i in range(1, 10)]
        gad7_scores = [int(payload[f"gad{i}"]) for i in range(1, 8)]
        submission = CheckinSubmission(
            user_uuid=str(user.id) if user else None,
            phq9_scores=phq9_scores,
            gad7_scores=gad7_scores
        )
        return submit_checkin(submission, db, current_user)
    else:
        # Short mode (PHQ-2, GAD-2, and Item 9)
        phq1 = int(payload.get("phq1", 0))
        phq2 = int(payload.get("phq2", 0))
        gad1 = int(payload.get("gad1", 0))
        gad2 = int(payload.get("gad2", 0))

        eval_res = DeterministicTriageEngine.evaluate(
            item_9_score=item9_score,
            phq2_score=phq1 + phq2,
            gad2_score=gad1 + gad2,
            mode="short"
        )

        checkin = Checkin(
            university_id=user.university_id if user else uuid.UUID(settings.DEFAULT_UNIVERSITY_ID),
            user_uuid=user.id if user else uuid.UUID("00000000-0000-0000-0000-000000000001"),
            checkin_type="quick_checkin"
        )
        db.add(checkin)
        db.flush()

        if user:
            DeterministicTriageEngine.process_and_persist(
                db=db,
                university_id=str(user.university_id),
                user_uuid=str(user.id),
                eval_result=eval_res,
                checkin_id=str(checkin.id)
            )

        return {
            "success": True,
            "message": "Quick screening assessment processed",
            "data": eval_res,
            "risk": eval_res["risk_level"].lower(),
            "sc": {
                "phq": phq1 + phq2,
                "gad": gad1 + gad2,
                "item9": item9_score,
                "phq2": phq1 + phq2,
                "gad2": gad1 + gad2
            }
        }
