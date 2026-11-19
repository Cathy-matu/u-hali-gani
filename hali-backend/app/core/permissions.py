from enum import Enum
from typing import List, Set
from fastapi import HTTPException, status


class UserRole(str, Enum):
    STUDENT = "student"
    COUNSELLOR = "counsellor"
    SUPERVISOR = "supervisor"
    UNIVERSITY_ADMIN = "university_admin"
    DEAN_OF_STUDENTS = "dean_of_students"
    RESEARCHER = "researcher"
    SUPER_ADMIN = "super_admin"


# Role Hierarchy and Matrix
ROLE_PERMISSIONS = {
    UserRole.STUDENT: {
        "checkins:create",
        "checkins:read_own",
        "assessments:submit",
        "bookings:create",
        "bookings:read_own",
        "messages:student",
        "consent:manage_own"
    },
    UserRole.COUNSELLOR: {
        "cases:read_queue",
        "cases:read_detail",
        "cases:manage_notes",
        "cases:assign",
        "briefs:generate",
        "bookings:counsellor",
        "messages:counsellor",
        "emergency:request_break_glass"
    },
    UserRole.SUPERVISOR: {
        "cases:read_queue",
        "cases:read_detail",
        "cases:supervise",
        "counsellors:manage"
    },
    UserRole.UNIVERSITY_ADMIN: {
        "analytics:read_aggregate",
        "reports:read_k_anonymous",
        "university:manage_settings"
    },
    UserRole.DEAN_OF_STUDENTS: {
        "analytics:read_aggregate",
        "reports:read_k_anonymous",
        "emergency:approve_break_glass"
    },
    UserRole.RESEARCHER: {
        "research:export_consented"
    },
    UserRole.SUPER_ADMIN: {
        "all"
    }
}


def check_permission(user_role: str, required_roles: List[UserRole]) -> bool:
    """Check if the provided role is permitted."""
    if not user_role:
        return False
    if user_role == UserRole.SUPER_ADMIN.value:
        return True
    return user_role in [r.value for r in required_roles]


def require_role(current_role: str, allowed_roles: List[UserRole]) -> None:
    """Raise HTTP 403 if role is not allowed."""
    if not check_permission(current_role, allowed_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied: role '{current_role}' is not authorized for this operation"
        )

