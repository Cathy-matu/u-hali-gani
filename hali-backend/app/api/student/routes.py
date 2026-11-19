from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.models.user import User

router = APIRouter(prefix="", tags=["Student Profile"])


@router.get("/students/me")
@router.get("/student/me")
def get_current_student_profile(current_user: User = Depends(get_current_user)):
    """Return pseudonymous student profile (ZERO-PII)."""
    return {
        "success": True,
        "message": "Student profile retrieved",
        "data": {
            "user_uuid": str(current_user.id),
            "pseudonym": current_user.anon_handle,
            "anon_handle": current_user.anon_handle,
            "role": current_user.role,
            "faculty": current_user.faculty,
            "department": current_user.department,
            "year_of_study": current_user.year_of_study,
            "university_id": str(current_user.university_id)
        },
        # Direct fields for frontend backward compatibility
        "pseudonym": current_user.anon_handle,
        "role": current_user.role
    }


@router.get("/student/crisis-contacts")
@router.get("/help/contacts")
def get_crisis_contacts():
    """Kenyan crisis lines and campus emergency numbers."""
    contacts = [
        {"tier": 0, "label": "Campus counselling centre", "tel": "1199", "name": "Campus Clinic Emergency"},
        {"tier": 1, "label": "Kenya Red Cross Toll-Free", "tel": "+254 722 178 177", "name": "Kenya Red Cross"},
        {"tier": 2, "label": "Befrienders Kenya 24/7 Helpline", "tel": "0900 620 800", "name": "Befrienders Kenya"}
    ]
    return {
        "success": True,
        "message": "Emergency contact directory",
        "data": contacts
    }


@router.get("/student/resources")
def get_wellness_resources():
    """Psychoeducational self-guided resources."""
    return {
        "success": True,
        "data": [
            {"id": 1, "cat": "Breathing", "title": "4-6 breathing for exam nerves", "body": "Breathe in for 4 counts, out for 6. Repeat for 2 minutes. Slow exhales calm the body's stress response."},
            {"id": 2, "cat": "Stress", "title": "Break a big deadline into small steps", "body": "List the next three actions only. Start a 15-minute timer. Stopping after one round is fine."},
            {"id": 3, "cat": "Sleep", "title": "A simple wind-down routine", "body": "Dim screens 30 minutes before bed, keep a steady wake time, and write tomorrow's worries on paper."},
            {"id": 4, "cat": "Anxiety", "title": "Name it to tame it", "body": "Write what you are worried about, then split it into what you can control and what you cannot."}
        ]
    }

