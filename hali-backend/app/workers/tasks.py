from app.workers.celery_app import celery_app
from app.core.database import SessionLocal, set_rls_tenant_context
from app.core.tenant import set_current_tenant_id, clear_tenant_context
from app.models.triage import Escalation
from app.models.audit import NotificationEvent


@celery_app.task(name="tasks.send_escalation_alert")
def send_escalation_alert(escalation_id: str, university_id: str):
    """
    Tenant-aware asynchronous worker task for RED escalation alerts.
    """
    set_current_tenant_id(university_id)
    db = SessionLocal()
    try:
        set_rls_tenant_context(db, university_id)
        esc = db.query(Escalation).filter(Escalation.id == escalation_id).first()
        if not esc:
            return {"status": "error", "message": "Escalation not found"}

        # Simulate Africa's Talking SMS / On-Duty alert
        notification = NotificationEvent(
            university_id=university_id,
            recipient_role="ON_DUTY_COUNSELLOR",
            channel="SMS",
            status="SENT",
            payload_summary=f"URGENT: Priority RED Escalation Case ID {str(esc.id)[:8]}",
            attempts=1
        )
        db.add(notification)
        db.commit()
        return {"status": "success", "escalation_id": str(esc.id)}
    finally:
        db.close()
        clear_tenant_context()

