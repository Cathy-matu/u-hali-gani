import sys
import os
import uuid
import secrets
from datetime import datetime, timedelta, timezone

# Add parent path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import SessionLocal
from app.core.config import settings
from app.models.university import University, UniversitySettings
from app.models.user import User, Role, UserRole, UserUniversityHash
from app.models.checkin import Checkin
from app.models.triage import PHQ9Assessment, GAD7Assessment, AUDITCAssessment, RiskEvent, Escalation
from app.models.counsellor import (
    CounsellorProfile,
    CounsellorAvailability,
    StudentCounsellorAssignment,
    SessionNote,
    AICaseBrief
)
from app.models.booking import Booking
from app.models.messaging import Conversation, Message
from app.models.consent import ConsentLedger
from app.models.audit import AuditLog, NotificationEvent
from app.models.anomaly import LMSAnomalyEvent
from app.services.hashing.hmac_service import hash_student_reg_no, get_university_salt
from app.services.break_glass.vault_service import BreakGlassVaultService
from app.utils.pseudonym import generate_anon_handle


def seed_database():
    db = SessionLocal()
    print("Starting Synthetic Kenyan University Data Seeding...")

    try:
        # 1. Seed Roles
        roles_data = [
            ("student", "Pseudonymous University Student"),
            ("counsellor", "Licensed Campus Counsellor"),
            ("supervisor", "Clinical Mental Health Supervisor"),
            ("university_admin", "Institutional Administrator"),
            ("dean_of_students", "Dean of Students"),
            ("researcher", "Authorized Welfare Researcher"),
            ("super_admin", "System Operations Administrator")
        ]
        role_map = {}
        for r_name, r_desc in roles_data:
            role = db.query(Role).filter(Role.name == r_name).first()
            if not role:
                role = Role(name=r_name, description=r_desc)
                db.add(role)
                db.flush()
            role_map[r_name] = role

        # 2. Seed Universities (Multi-Tenant Isolation)
        univ_1_id = uuid.UUID("11111111-1111-1111-1111-111111111111")
        univ_2_id = uuid.UUID("22222222-2222-2222-2222-222222222222")

        u1 = db.query(University).filter(University.id == univ_1_id).first()
        if not u1:
            u1 = University(
                id=univ_1_id,
                name="Mount Kenya Technical University",
                code="MKTU",
                slug="mktu",
                domain="mktu.ac.ke",
                salt="kenya_tu_super_secret_salt_2026_x7a",
                is_active=True
            )
            db.add(u1)
            db.flush()

            u1_settings = UniversitySettings(
                university_id=u1.id,
                k_anonymity_threshold=15,
                red_threshold_phq9=15,
                red_threshold_gad7=15,
                amber_threshold_phq9=10,
                amber_threshold_gad7=10,
                emergency_callback_enabled=True,
                crisis_hotlines=settings.get_crisis_hotlines()
            )
            db.add(u1_settings)

        u2 = db.query(University).filter(University.id == univ_2_id).first()
        if not u2:
            u2 = University(
                id=univ_2_id,
                name="Nairobi Rift Valley University",
                code="NRVU",
                slug="nrvu",
                domain="nrvu.ac.ke",
                salt="nairobi_rv_super_secret_salt_2026_q9b",
                is_active=True
            )
            db.add(u2)
            db.flush()

            u2_settings = UniversitySettings(
                university_id=u2.id,
                k_anonymity_threshold=15,
                red_threshold_phq9=15,
                red_threshold_gad7=15,
                amber_threshold_phq9=10,
                amber_threshold_gad7=10,
                emergency_callback_enabled=True,
                crisis_hotlines=settings.get_crisis_hotlines()
            )
            db.add(u2_settings)

        # 3. Seed Campus Counsellors
        counsellors_data = [
            ("Dr. Amina Wekesa", "Anxiety & academic stress", ["In-person", "Audio", "Text"], True, "+254 700 000 001"),
            ("Mr. Brian Otieno", "Relationships & loneliness", ["In-person", "Text"], False, "+254 700 000 002"),
            ("Ms. Grace Mutua", "Sleep, mood & low motivation", ["Audio", "Text"], True, "+254 700 000 003")
        ]

        counsellor_profiles = []
        for name, spec, modes, online, phone in counsellors_data:
            c_user = db.query(User).filter(User.staff_name == name).first()
            if not c_user:
                c_user = User(
                    university_id=univ_1_id,
                    anon_handle=f"Staff-{name.split()[-1]}-{secrets.randbelow(800)+100}",
                    role="counsellor",
                    staff_name=name,
                    staff_email=f"{name.split()[-1].lower()}@mktu.ac.ke",
                    is_active=True
                )
                db.add(c_user)
                db.flush()

            c_prof = db.query(CounsellorProfile).filter(CounsellorProfile.user_id == c_user.id).first()
            if not c_prof:
                c_prof = CounsellorProfile(
                    university_id=univ_1_id,
                    user_id=c_user.id,
                    name=name,
                    specialization=spec,
                    modes=modes,
                    is_online=online,
                    phone=phone
                )
                db.add(c_prof)
                db.flush()
            counsellor_profiles.append(c_prof)

        # 4. Seed Institutional Staff (Dean & University Admin)
        dean_user = db.query(User).filter(User.role == "dean_of_students").first()
        if not dean_user:
            dean_user = User(
                university_id=univ_1_id,
                anon_handle="Dean-Office-001",
                role="dean_of_students",
                staff_name="Prof. David Omwamba",
                staff_email="dean.students@mktu.ac.ke",
                is_active=True
            )
            db.add(dean_user)
            db.flush()

        admin_user = db.query(User).filter(User.role == "university_admin").first()
        if not admin_user:
            admin_user = User(
                university_id=univ_1_id,
                anon_handle="Admin-Central-001",
                role="university_admin",
                staff_name="Dr. Sarah Nduta",
                staff_email="admin.welfare@mktu.ac.ke",
                is_active=True
            )
            db.add(admin_user)
            db.flush()

        # 5. Seed Synthetic Pseudonymous Students (Cohorts with k >= 15 and k < 15)
        # Cohorts to demonstrate K-Anonymity suppression:
        cohort_distribution = [
            ("Computing", "Computer Science", 45),     # k >= 15: ALLOWED
            ("Business", "Business Administration", 32), # k >= 15: ALLOWED
            ("Health Sciences", "Nursing", 24),        # k >= 15: ALLOWED
            ("Law", "Law", 7),                          # k < 15: SUPPRESSED
            ("Theology", "Theology", 4),                # k < 15: SUPPRESSED
            ("Education", "Education", 6)               # k < 15: SUPPRESSED
        ]

        total_students = []
        salt_u1 = u1.salt

        for faculty, dept, count in cohort_distribution:
            for i in range(count):
                handle = generate_anon_handle()
                simulated_reg = f"SYNTH_{dept[:3].upper()}_{i}_{secrets.token_hex(4)}"
                u_hash = hash_student_reg_no(simulated_reg, salt_u1)

                student = User(
                    university_id=univ_1_id,
                    anon_handle=handle,
                    role="student",
                    faculty=faculty,
                    department=dept,
                    year_of_study=(i % 4) + 1,
                    is_active=True
                )
                db.add(student)
                db.flush()

                hash_rec = UserUniversityHash(
                    university_id=univ_1_id,
                    user_uuid=student.id,
                    user_hash=u_hash
                )
                db.add(hash_rec)
                total_students.append(student)

        # 6. Seed Detailed Cases (GREEN, AMBER, RED)
        # Assign risk events, checkins, assessments, and bookings
        primary_counsellor = counsellor_profiles[0]

        # Case 1: RED - Swift-Baobab-208 (PHQ-9 Item 9 positive)
        s_red = total_students[0]
        s_red.anon_handle = "Swift-Baobab-208"
        db.add(s_red)

        phq_red = PHQ9Assessment(
            university_id=univ_1_id,
            user_uuid=s_red.id,
            item_scores=[2, 2, 2, 2, 1, 2, 1, 1, 2],  # Item 9 = 2 (Positive!)
            total_score=15,
            item_9_score=2,
            severity="Moderately Severe"
        )
        gad_red = GAD7Assessment(
            university_id=univ_1_id,
            user_uuid=s_red.id,
            item_scores=[2, 2, 2, 2, 2, 2, 1],
            total_score=13,
            severity="Moderate"
        )
        risk_red = RiskEvent(
            university_id=univ_1_id,
            user_uuid=s_red.id,
            risk_level="RED",
            trigger_reason="PHQ-9 Item 9 positive (score: 2) - Imminent Risk",
            item9_positive=True,
            phq9_score=15,
            gad7_score=13,
            is_active=True
        )
        db.add(phq_red)
        db.add(gad_red)
        db.add(risk_red)
        db.flush()

        esc_red = Escalation(
            university_id=univ_1_id,
            risk_event_id=risk_red.id,
            user_uuid=s_red.id,
            escalation_tier="RED_IMMINENT_RISK",
            status="PENDING",
            idempotency_key=f"esc_{s_red.id}_red"
        )
        db.add(esc_red)

        # Emergency contact in break-glass vault for Swift-Baobab-208
        BreakGlassVaultService.store_emergency_contact(
            db=db,
            university_id=str(univ_1_id),
            user_uuid=str(s_red.id),
            contact_data={
                "contact_name": "Mrs. Tabitha Baobab",
                "relationship": "Mother",
                "phone": "+254 711 999 888",
                "notes": "Emergency family contact in Nakuru"
            }
        )

        # Case 2: AMBER - Calm-Mango-532 (Moderate anxiety & stress)
        s_amber = total_students[1]
        s_amber.anon_handle = "Calm-Mango-532"
        db.add(s_amber)

        phq_amber = PHQ9Assessment(
            university_id=univ_1_id,
            user_uuid=s_amber.id,
            item_scores=[1, 1, 1, 2, 1, 1, 1, 1, 0],
            total_score=9,
            item_9_score=0,
            severity="Mild"
        )
        gad_amber = GAD7Assessment(
            university_id=univ_1_id,
            user_uuid=s_amber.id,
            item_scores=[2, 2, 2, 1, 1, 2, 1],
            total_score=11,
            severity="Moderate"
        )
        risk_amber = RiskEvent(
            university_id=univ_1_id,
            user_uuid=s_amber.id,
            risk_level="AMBER",
            trigger_reason="GAD-7 score 11 indicates moderate anxiety (>=10)",
            item9_positive=False,
            phq9_score=9,
            gad7_score=11,
            is_active=True
        )
        db.add(phq_amber)
        db.add(gad_amber)
        db.add(risk_amber)

        # Case 3: GREEN - Bright-Savanna-774 (Sub-threshold coping)
        s_green = total_students[2]
        s_green.anon_handle = "Bright-Savanna-774"
        db.add(s_green)

        phq_green = PHQ9Assessment(
            university_id=univ_1_id,
            user_uuid=s_green.id,
            item_scores=[0, 1, 0, 1, 0, 0, 1, 0, 0],
            total_score=3,
            item_9_score=0,
            severity="Minimal"
        )
        gad_green = GAD7Assessment(
            university_id=univ_1_id,
            user_uuid=s_green.id,
            item_scores=[0, 1, 0, 1, 0, 1, 0],
            total_score=3,
            severity="Minimal"
        )
        risk_green = RiskEvent(
            university_id=univ_1_id,
            user_uuid=s_green.id,
            risk_level="GREEN",
            trigger_reason="Routine Screening - Normal Range",
            item9_positive=False,
            phq9_score=3,
            gad7_score=3,
            is_active=True
        )
        db.add(phq_green)
        db.add(gad_green)
        db.add(risk_green)

        # 7. Seed Sample Bookings & Messages
        now = datetime.now(timezone.utc)
        booking1 = Booking(
            university_id=univ_1_id,
            student_uuid=s_red.id,
            counsellor_id=primary_counsellor.id,
            appointment_time=now + timedelta(hours=3),
            time_slot="14:00",
            session_type="Audio",
            status="Confirmed"
        )
        booking2 = Booking(
            university_id=univ_1_id,
            student_uuid=s_amber.id,
            counsellor_id=primary_counsellor.id,
            appointment_time=now + timedelta(days=2),
            time_slot="10:30",
            session_type="In-person",
            status="Requested"
        )
        db.add(booking1)
        db.add(booking2)

        # 8. Seed Research Consent Entries
        for student in total_students[:35]:
            db.add(ConsentLedger(
                university_id=univ_1_id,
                user_uuid=student.id,
                consent_scope="deidentified_research",
                consent_version="1.0",
                granted=True,
                granted_at=now
            ))

        db.commit()
        print(f"Successfully seeded database with {len(total_students)} synthetic students across 6 faculties!")
        print("Universities created: MKTU (MKTU) and NRVU (NRVU)")
        print("Demonstration cohorts configured for k=15 suppression tests.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

