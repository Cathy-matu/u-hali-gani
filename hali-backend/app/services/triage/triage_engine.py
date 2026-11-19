import hashlib
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.triage import PHQ9Assessment, GAD7Assessment, AUDITCAssessment, RiskEvent, Escalation
from app.models.user import User
from app.services.triage.instruments import PHQ9Scorer, GAD7Scorer, AUDITCScorer

CRISIS_TEXT_KEYWORDS = {
    "die", "dead", "hurt myself", "kill myself", "suicid", "kujiua", "kujidhuru",
    "end it all", "better off dead", "hopeless", "hakuna matumaini", "give up on life"
}


class DeterministicTriageEngine:
    """
    Deterministic clinical triage engine.
    Scoring is strictly rule-based and clinical-instrument driven.
    NO LLM is permitted to determine risk categories or downgrade RED classifications.
    """

    @classmethod
    def evaluate(
        cls,
        phq9_scores: Optional[List[int]] = None,
        gad7_scores: Optional[List[int]] = None,
        auditc_scores: Optional[List[int]] = None,
        free_text: Optional[str] = None,
        item_9_score: Optional[int] = None,
        phq2_score: Optional[int] = None,
        gad2_score: Optional[int] = None,
        mode: Optional[str] = "full"
    ) -> Dict[str, Any]:
        # Handle empty lists gracefully: only score if items are provided
        phq9_res = None
        if phq9_scores is not None and len(phq9_scores) == 9:
            phq9_res = PHQ9Scorer.validate_and_score(phq9_scores)
        elif phq9_scores is not None and len(phq9_scores) > 0 and len(phq9_scores) != 9:
            raise ValueError(f"PHQ-9 requires exactly 9 items, received {len(phq9_scores)}")

        gad7_res = None
        if gad7_scores is not None and len(gad7_scores) == 7:
            gad7_res = GAD7Scorer.validate_and_score(gad7_scores)
        elif gad7_scores is not None and len(gad7_scores) > 0 and len(gad7_scores) != 7:
            raise ValueError(f"GAD-7 requires exactly 7 items, received {len(gad7_scores)}")

        auditc_res = None
        if auditc_scores is not None and len(auditc_scores) == 3:
            auditc_res = AUDITCScorer.validate_and_score(auditc_scores)
        elif auditc_scores is not None and len(auditc_scores) > 0 and len(auditc_scores) != 3:
            raise ValueError(f"AUDIT-C requires exactly 3 items, received {len(auditc_scores)}")

        risk_level = "GREEN"
        triggers = []
        is_item9_positive = False

        # 1. Critical Rule: PHQ-9 Item 9 Check (Self-harm / Suicidal ideation)
        resolved_item9 = 0
        if phq9_res:
            resolved_item9 = phq9_res["item_9_score"]
        elif item_9_score is not None:
            resolved_item9 = int(item_9_score)

        if resolved_item9 > 0:
            risk_level = "RED"
            is_item9_positive = True
            triggers.append(f"PHQ-9 Item 9 positive (score: {resolved_item9}) - Imminent Risk")

        # 2. Text-based Crisis Keyword Screening (Safety fallback)
        if free_text:
            text_lower = free_text.lower()
            if any(kw in text_lower for kw in CRISIS_TEXT_KEYWORDS):
                risk_level = "RED"
                triggers.append("Imminent crisis keywords detected in reflection text")

        # 3. RED Threshold Check
        if phq9_res and phq9_res["total_score"] >= 15:
            risk_level = "RED"
            triggers.append(f"PHQ-9 score {phq9_res['total_score']} crosses severe threshold (>=15)")

        if gad7_res and gad7_res["total_score"] >= 15:
            risk_level = "RED"
            triggers.append(f"GAD-7 score {gad7_res['total_score']} crosses severe threshold (>=15)")

        # 4. AMBER Threshold Check (if not already RED)
        if risk_level != "RED":
            # Quick short check-in thresholds (PHQ-2 >= 3 or GAD-2 >= 3)
            if phq2_score is not None and phq2_score >= 3:
                risk_level = "AMBER"
                triggers.append(f"PHQ-2 score {phq2_score} indicates moderate depressive strain (>=3)")
            if gad2_score is not None and gad2_score >= 3:
                risk_level = "AMBER"
                triggers.append(f"GAD-2 score {gad2_score} indicates moderate anxiety strain (>=3)")

            # Full check-in thresholds
            if phq9_res and phq9_res["total_score"] >= 10:
                risk_level = "AMBER"
                triggers.append(f"PHQ-9 score {phq9_res['total_score']} indicates moderate depression (>=10)")

            if gad7_res and gad7_res["total_score"] >= 10:
                risk_level = "AMBER"
                triggers.append(f"GAD-7 score {gad7_res['total_score']} indicates moderate anxiety (>=10)")

            if auditc_res and auditc_res["total_score"] >= 4:
                risk_level = "AMBER"
                triggers.append(f"AUDIT-C score {auditc_res['total_score']} indicates hazardous alcohol pattern (>=4)")

        # Recommended Action Plan
        if risk_level == "RED":
            action = {
                "bypass_ai": True,
                "human_escalation_required": True,
                "clinic_callback": True,
                "display_emergency_contacts": True,
                "message": "Immediate priority human escalation triggered. Please reach out to emergency resources or a counsellor.",
                "crisis_hotlines": settings.get_crisis_hotlines()
            }
        elif risk_level == "AMBER":
            action = {
                "bypass_ai": False,
                "human_escalation_required": False,
                "recommend_booking": True,
                "place_in_counsellor_queue": True,
                "message": "Moderate distress detected. A confidential session with a university counsellor is recommended.",
                "crisis_hotlines": settings.get_crisis_hotlines()
            }
        else:
            action = {
                "bypass_ai": False,
                "human_escalation_required": False,
                "recommend_resources": True,
                "message": "Screening within normal range. Self-guided wellbeing resources and regular check-ins available."
            }

        return {
            "risk_level": risk_level,
            "is_item9_positive": is_item9_positive,
            "triggers": triggers,
            "phq9": phq9_res,
            "gad7": gad7_res,
            "auditc": auditc_res,
            "item_9_score": resolved_item9,
            "action": action,
            "disclaimer": "Screening results only. This is not a clinical diagnosis or medical prescription."
        }

    @classmethod
    def process_and_persist(
        cls,
        db: Session,
        university_id: str,
        user_uuid: str,
        eval_result: Dict[str, Any],
        checkin_id: Optional[str] = None
    ) -> RiskEvent:
        """Persist assessment items, risk event, and trigger escalation idempotently."""
        # 1. Safely resolve user UUID
        target_user = None
        try:
            val_uuid = uuid.UUID(str(user_uuid))
            target_user = db.query(User).filter(User.id == val_uuid).first()
        except (ValueError, TypeError):
            target_user = db.query(User).filter(User.anon_handle == str(user_uuid)).first()

        if target_user:
            clean_user_id = target_user.id
            clean_univ_id = target_user.university_id
        else:
            # Fallback
            first_user = db.query(User).filter(User.role == "student").first()
            if first_user:
                clean_user_id = first_user.id
                clean_univ_id = first_user.university_id
            else:
                clean_user_id = uuid.UUID(str(user_uuid))
                clean_univ_id = uuid.UUID(str(university_id))

        # 2. Safely resolve checkin ID
        clean_checkin_id = None
        if checkin_id:
            try:
                clean_checkin_id = uuid.UUID(str(checkin_id))
            except (ValueError, TypeError):
                clean_checkin_id = None

        phq9 = eval_result.get("phq9")
        gad7 = eval_result.get("gad7")
        auditc = eval_result.get("auditc")

        if phq9:
            db.add(PHQ9Assessment(
                university_id=clean_univ_id,
                user_uuid=clean_user_id,
                checkin_id=clean_checkin_id,
                item_scores=phq9["scores"],
                total_score=phq9["total_score"],
                item_9_score=phq9["item_9_score"],
                severity=phq9["severity"]
            ))

        if gad7:
            db.add(GAD7Assessment(
                university_id=clean_univ_id,
                user_uuid=clean_user_id,
                checkin_id=clean_checkin_id,
                item_scores=gad7["scores"],
                total_score=gad7["total_score"],
                severity=gad7["severity"]
            ))

        if auditc:
            db.add(AUDITCAssessment(
                university_id=clean_univ_id,
                user_uuid=clean_user_id,
                checkin_id=clean_checkin_id,
                item_scores=auditc["scores"],
                total_score=auditc["total_score"],
                risk_level=auditc["risk_level"]
            ))

        # Create Risk Event
        risk_event = RiskEvent(
            university_id=clean_univ_id,
            user_uuid=clean_user_id,
            risk_level=eval_result["risk_level"],
            trigger_reason="; ".join(eval_result["triggers"]) if eval_result["triggers"] else "Routine Screening",
            item9_positive=eval_result["is_item9_positive"],
            phq9_score=phq9["total_score"] if phq9 else None,
            gad7_score=gad7["total_score"] if gad7 else None,
            auditc_score=auditc["total_score"] if auditc else None,
            is_active=True
        )
        db.add(risk_event)
        db.flush()

        # If RED or AMBER, create escalation event idempotently
        if eval_result["risk_level"] in ("RED", "AMBER"):
            ts_str = risk_event.created_at.strftime('%Y%m%d%H%M') if risk_event.created_at else datetime.now(timezone.utc).strftime('%Y%m%d%H%M')
            idempotency_raw = f"{str(clean_univ_id)}_{str(clean_user_id)}_{eval_result['risk_level']}_{ts_str}"
            idempotency_key = hashlib.sha256(idempotency_raw.encode()).hexdigest()

            # Prevent duplicate escalation if one exists with same key
            existing = db.query(Escalation).filter(Escalation.idempotency_key == idempotency_key).first()
            if not existing:
                escalation = Escalation(
                    university_id=clean_univ_id,
                    risk_event_id=risk_event.id,
                    user_uuid=clean_user_id,
                    escalation_tier="RED_IMMINENT_RISK" if eval_result["risk_level"] == "RED" else "AMBER_COUNSELLOR_RECOMMENDED",
                    status="PENDING",
                    idempotency_key=idempotency_key
                )
                db.add(escalation)

        db.commit()
        db.refresh(risk_event)
        return risk_event
