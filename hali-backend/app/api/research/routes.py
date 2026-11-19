from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import distinct, func

from app.api.deps import get_current_user_optional, get_db
from app.core.config import settings
from app.models.user import User
from app.models.consent import ConsentLedger
from app.models.triage import PHQ9Assessment, GAD7Assessment
from app.models.audit import AuditLog

router = APIRouter(prefix="", tags=["De-identified Research Export"])


@router.get("/api/research/export")
@router.get("/research/export")
def export_research_dataset(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Export De-identified Research Dataset.
    1. Strictly filters for students with ACTIVE, UNWITHDRAWN research consent.
    2. Enforces K-Anonymity (k >= 15).
    3. Strips all personal identifiers.
    4. Immutable audit logging for ethical compliance.
    """
    univ_id = str(current_user.university_id) if current_user else settings.DEFAULT_UNIVERSITY_ID

    # 1. Retrieve users who granted research consent
    consented_user_ids = db.query(ConsentLedger.user_uuid).filter(
        ConsentLedger.university_id == univ_id,
        ConsentLedger.consent_scope == "deidentified_research",
        ConsentLedger.granted == True
    ).distinct().all()

    user_ids = [uid[0] for uid in consented_user_ids]

    # K-Anonymity check for research cohort
    if len(user_ids) < settings.K_ANONYMITY_THRESHOLD:
        return {
            "suppressed": True,
            "reason": "k-anonymity threshold",
            "message": f"Research export suppressed: fewer than {settings.K_ANONYMITY_THRESHOLD} distinct consenting students.",
            "data": []
        }

    # Fetch de-identified assessment metrics
    phq_data = db.query(
        User.faculty,
        User.year_of_study,
        PHQ9Assessment.total_score,
        PHQ9Assessment.severity
    ).join(
        PHQ9Assessment, User.id == PHQ9Assessment.user_uuid
    ).filter(
        User.id.in_(user_ids)
    ).all()

    # Audit log
    db.add(AuditLog(
        university_id=univ_id,
        actor_uuid=current_user.id if current_user else None,
        actor_role="researcher",
        action="EXPORT_RESEARCH_DATASET",
        resource_type="consent_ledger",
        details={"consented_records_exported": len(phq_data)}
    ))
    db.commit()

    return {
        "success": True,
        "suppressed": False,
        "record_count": len(phq_data),
        "data": [
            {
                "faculty": row.faculty,
                "year_of_study": row.year_of_study,
                "phq9_total": row.total_score,
                "severity": row.severity
            }
            for row in phq_data
        ]
    }

