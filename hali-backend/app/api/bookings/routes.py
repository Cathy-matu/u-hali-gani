from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_optional, get_db
from app.models.user import User
from app.models.counsellor import CounsellorProfile, CounsellorAvailability
from app.models.booking import Booking
from app.schemas.booking import BookingCreateRequest

router = APIRouter(prefix="", tags=["Counselling Bookings"])


@router.get("/api/counsellors")
@router.get("/counsellors")
def get_counsellors_list(db: Session = Depends(get_db)):
    """List available university counsellors."""
    profiles = db.query(CounsellorProfile).all()
    if not profiles:
        return [
            {"id": 1, "name": "Dr. Amina Wekesa", "spec": "Anxiety & academic stress", "modes": ["In-person", "Audio", "Text"], "online": True},
            {"id": 2, "name": "Mr. Brian Otieno", "spec": "Relationships & loneliness", "modes": ["In-person", "Text"], "online": False},
            {"id": 3, "name": "Ms. Grace Mutua", "spec": "Sleep, mood & low motivation", "modes": ["Audio", "Text"], "online": True}
        ]

    return [
        {
            "id": str(p.id),
            "name": p.name,
            "spec": p.specialization,
            "modes": p.modes,
            "online": p.is_online
        }
        for p in profiles
    ]


@router.get("/api/slots")
@router.get("/slots")
@router.get("/api/bookings/availability")
def get_available_slots():
    """List available daily appointment slots."""
    return ["09:00", "10:30", "12:00", "14:00", "15:30"]


@router.post("/api/bookings")
@router.post("/bookings")
def book_appointment(
    payload: BookingCreateRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Book counselling session (In-person, Audio, or Text)."""
    user = current_user or db.query(User).filter(User.role == "student").first()
    if not user:
        raise HTTPException(status_code=400, detail="Student context required")

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
    c_id = counsellor.id

    booking = Booking(
        university_id=user.university_id,
        student_uuid=user.id,
        counsellor_id=c_id,
        appointment_time=datetime.now(timezone.utc),
        time_slot=payload.slot or payload.when or "14:00",
        session_type=payload.type or payload.session_type or "Audio",
        status="Requested",
        notes=payload.notes
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    return {
        "success": True,
        "message": "Appointment requested successfully",
        "data": {
            "id": str(booking.id),
            "who": payload.who or (counsellor.name if counsellor else "University Counsellor"),
            "when": payload.when or "Upcoming 14:00",
            "type": booking.session_type,
            "status": booking.status
        },
        # Direct return for frontend promise
        "id": str(booking.id),
        "who": payload.who or (counsellor.name if counsellor else "University Counsellor"),
        "when": payload.when or "Upcoming 14:00",
        "type": booking.session_type,
        "status": booking.status
    }


@router.get("/api/bookings/my")
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Get active student's bookings."""
    user = current_user or db.query(User).filter(User.role == "student").first()
    if not user:
        return {"data": []}

    bookings = db.query(Booking).filter(Booking.student_uuid == user.id).all()
    return {
        "success": True,
        "data": [
            {
                "id": str(b.id),
                "time_slot": b.time_slot,
                "session_type": b.session_type,
                "status": b.status
            }
            for b in bookings
        ]
    }

