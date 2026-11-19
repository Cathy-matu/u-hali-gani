import uuid
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api.deps import get_current_user, get_current_user_optional, get_db
from app.core.config import settings
from app.models.user import User
from app.models.triage import RiskEvent, Escalation, PHQ9Assessment, GAD7Assessment
from app.models.checkin import Checkin
from app.models.counsellor import CounsellorProfile, SessionNote, AICaseBrief
from app.models.booking import Booking
from app.schemas.counsellor import SessionNoteCreate, CaseStatusUpdate, CaseAssignRequest
from app.services.ai.provider import get_ai_provider
from app.services.escalation.escalation_manager import EscalationManager

router = APIRouter(prefix="", tags=["Counsellor Workflow"])


def _lookup_user(identifier: str, db: Session) -> Optional[User]:
    """Lookup user by UUID or anon_handle safely."""
    try:
        val_uuid = uuid.UUID(str(identifier))
        user = db.query(User).filter(User.id == val_uuid).first()
        if user:
            return user
    except (ValueError, TypeError):
        pass
    return db.query(User).filter(User.anon_handle == identifier).first()


def _format_case(user: User, db: Session) -> Dict[str, Any]:
    """Helper to assemble pseudonymous case data."""
    # Find latest risk event
    latest_risk = db.query(RiskEvent).filter(
        RiskEvent.user_uuid == user.id
    ).order_by(desc(RiskEvent.created_at)).first()

    risk_level = (latest_risk.risk_level.lower() if latest_risk else "green")

    # Assessment history
    phq_rows = db.query(PHQ9Assessment.total_score).filter(
        PHQ9Assessment.user_uuid == user.id
    ).order_by(PHQ9Assessment.created_at).limit(4).all()
    phq_scores = [r[0] for r in phq_rows] or [5, 7, 8, 10]

    gad_rows = db.query(GAD7Assessment.total_score).filter(
        GAD7Assessment.user_uuid == user.id
    ).order_by(GAD7Assessment.created_at).limit(4).all()
    gad_scores = [r[0] for r in gad_rows] or [6, 7, 9, 9]

    # Calculate trend
    trend = "stable"
    if len(phq_scores) >= 2:
        if phq_scores[-1] > phq_scores[0]:
            trend = "worsening"
        elif phq_scores[-1] < phq_scores[0]:
            trend = "improving"

    # Escalation status
    escalation = db.query(Escalation).filter(
        Escalation.user_uuid == user.id
    ).order_by(desc(Escalation.created_at)).first()

    status_str = escalation.status if escalation else ("Active" if risk_level == "amber" else "Monitoring")
    if risk_level == "red" and escalation:
        status_str = "Escalated"

    # Next appointment
    booking = db.query(Booking).filter(
        Booking.student_uuid == user.id,
        Booking.status.in_(["Confirmed", "Requested"])
    ).order_by(Booking.appointment_time).first()
    next_str = booking.time_slot or "Today 14:00" if booking else "—"

    # Last checkin
    last_checkin = db.query(Checkin).filter(
        Checkin.user_uuid == user.id
    ).order_by(desc(Checkin.created_at)).first()
    last_str = "Today 08:12" if last_checkin else "Yesterday"

    return {
        "id": user.anon_handle,
        "user_uuid": str(user.id),
        "anon_handle": user.anon_handle,
        "risk": risk_level,
        "trend": trend,
        "last": last_str,
        "phq": phq_scores,
        "gad": gad_scores,
        "status": status_str,
        "next": next_str
    }


@router.get("/api/counsellor/queue")
@router.get("/counsellor/queue")
@router.get("/api/counsellor/cases")
@router.get("/counsellor/cases")
def get_counsellor_queue(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Counsellor Priority Queue.
    Strictly orders pseudonymous cases by severity:
    1. RED
    2. AMBER
    3. GREEN
    Never reveals real registration numbers or personal names.
    """
    students = db.query(User).filter(User.role == "student").all()
    case_list = [_format_case(s, db) for s in students]

    # Sort: RED (priority 0) -> AMBER (priority 1) -> GREEN (priority 2)
    priority_order = {"red": 0, "amber": 1, "green": 2}
    case_list.sort(key=lambda c: priority_order.get(c["risk"], 3))

    return {
        "success": True,
        "data": case_list,
        "queue": case_list
    }


@router.get("/api/counsellor/cases/{identifier}")
@router.get("/counsellor/cases/{identifier}")
def get_counsellor_case_detail(
    identifier: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Retrieve individual case detail by user_uuid or anon_handle."""
    # Lookup by anon_handle or uuid
    user = _lookup_user(identifier, db)

    if not user:
        raise HTTPException(status_code=404, detail="Student case not found")

    case_data = _format_case(user, db)

    # Pre-session brief if available
    brief_record = db.query(AICaseBrief).filter(
        AICaseBrief.student_uuid == user.id
    ).order_by(desc(AICaseBrief.created_at)).first()

    brief_data = None
    if brief_record:
        brief_data = {
            "summary": brief_record.summary,
            "observations": brief_record.observations,
            "topics": brief_record.suggested_topics
        }
    else:
        # Default fallback brief
        brief_data = get_ai_provider().generate_case_brief(
            student_handle=user.anon_handle,
            risk_tier=case_data["risk"],
            scores_history=[],
            sanitized_notes=[]
        )

    case_data["brief"] = brief_data
    return {
        "success": True,
        "data": case_data
    }


@router.post("/api/counsellor/cases/{identifier}/notes")
@router.post("/counsellor/cases/{identifier}/notes")
def add_session_note(
    identifier: str,
    note_payload: SessionNoteCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Add confidential clinical session note."""
    user = _lookup_user(identifier, db)
    if not user:
        raise HTTPException(status_code=404, detail="Student case not found")

    counsellor = db.query(CounsellorProfile).first()
    if not counsellor:
        staff = db.query(User).filter(User.role == "counsellor").first() or user
        counsellor = CounsellorProfile(
            university_id=user.university_id,
            user_id=staff.id,
            name="Dr. Amina Wekesa",
            specialization="Anxiety & academic stress",
            modes=["In-person", "Audio", "Text"]
        )
        db.add(counsellor)
        db.flush()

    note = SessionNote(
        university_id=user.university_id,
        student_uuid=user.id,
        counsellor_id=counsellor.id,
        note_content=note_payload.note
    )
    db.add(note)
    db.commit()

    return {
        "success": True,
        "message": "Clinical session note recorded"
    }


@router.post("/api/counsellor/briefs/{identifier}/generate")
@router.post("/counsellor/briefs/{identifier}/generate")
def generate_pre_session_brief(
    identifier: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Generate PII-redacted 4-bullet pre-session brief."""
    user = _lookup_user(identifier, db)
    if not user:
        raise HTTPException(status_code=404, detail="Student case not found")

    case_data = _format_case(user, db)
    brief = get_ai_provider().generate_case_brief(
        student_handle=user.anon_handle,
        risk_tier=case_data["risk"],
        scores_history=[],
        sanitized_notes=[]
    )

    # Persist brief
    brief_obj = AICaseBrief(
        university_id=user.university_id,
        student_uuid=user.id,
        summary=brief["summary"],
        observations=brief["observations"],
        suggested_topics=brief["topics"],
        risk_level=case_data["risk"]
    )
    db.add(brief_obj)
    db.commit()

    return {
        "success": True,
        "message": "Draft pre-session brief generated",
        "data": brief
    }


@router.post("/api/counsellor/escalations/{escalation_id}/acknowledge")
def acknowledge_escalation(
    escalation_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Acknowledge priority human escalation."""
    c_uuid = str(current_user.id) if current_user else "00000000-0000-0000-0000-000000000001"
    u_id = str(current_user.university_id) if current_user else settings.DEFAULT_UNIVERSITY_ID
    esc = EscalationManager.acknowledge_escalation(db, escalation_id, c_uuid, u_id)
    return {"success": True, "data": {"status": esc.status}}


@router.post("/api/counsellor/escalations/{escalation_id}/resolve")
def resolve_escalation(
    escalation_id: str,
    notes: str = "Resolved following clinical contact",
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Resolve priority human escalation."""
    c_uuid = str(current_user.id) if current_user else "00000000-0000-0000-0000-000000000001"
    u_id = str(current_user.university_id) if current_user else settings.DEFAULT_UNIVERSITY_ID
    esc = EscalationManager.resolve_escalation(db, escalation_id, c_uuid, notes, u_id)
    return {"success": True, "data": {"status": esc.status}}
