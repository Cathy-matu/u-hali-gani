from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_optional, get_db
from app.core.config import settings
from app.models.user import User
from app.models.audit import AuditLog
from app.services.analytics.k_anonymity import WelfareRadarService

router = APIRouter(prefix="", tags=["Institutional Welfare Analytics"])


@router.get("/api/admin/welfare-radar")
@router.get("/admin/welfare-radar")
@router.get("/api/analytics/overview")
@router.get("/analytics/overview")
def get_institutional_welfare_radar(
    faculty: Optional[str] = Query(None, description="Filter by faculty"),
    department: Optional[str] = Query(None, description="Filter by department"),
    year_of_study: Optional[int] = Query(None, description="Filter by year of study"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    K-Anonymous Institutional Welfare Radar Endpoint (k >= 15).
    Strictly enforces cohort privacy: cohorts with fewer than 15 distinct students are suppressed.
    Prevents differencing attacks and protects vulnerable student sub-populations.
    """
    univ_id = str(current_user.university_id) if current_user else settings.DEFAULT_UNIVERSITY_ID
    
    radar_data = WelfareRadarService.get_welfare_radar(
        db=db,
        university_id=univ_id,
        faculty=faculty,
        department=department,
        year_of_study=year_of_study
    )

    # Audit query access
    if current_user:
        db.add(AuditLog(
            university_id=current_user.university_id,
            actor_uuid=current_user.id,
            actor_role=current_user.role,
            action="VIEW_AGGREGATE_RADAR",
            resource_type="analytics",
            details={
                "faculty": faculty,
                "department": department,
                "year_of_study": year_of_study,
                "suppressed": radar_data.get("suppressed", False)
            }
        ))
        db.commit()

    return radar_data


@router.get("/api/admin/audit-logs")
def get_audit_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Immutable institutional security and suppression audit trail."""
    univ_id = str(current_user.university_id) if current_user else settings.DEFAULT_UNIVERSITY_ID
    logs = db.query(AuditLog).filter(
        AuditLog.university_id == univ_id
    ).order_by(AuditLog.created_at.desc()).limit(limit).all()

    return {
        "success": True,
        "data": [
            {
                "id": str(log.id),
                "timestamp": log.created_at.isoformat() if log.created_at else None,
                "action": log.action,
                "resource_type": log.resource_type,
                "actor_role": log.actor_role,
                "details": log.details
            }
            for log in logs
        ]
    }

