# Hali – Privacy-First University Wellness Operating System

Hali is an enterprise-grade, privacy-first university mental health triage and student welfare operating system integrated into university e-Learning portals (LMS) in Kenya.

Hali combines anonymous student onboarding, deterministic clinical screening, risk-based triage, human counsellor escalation, institutional welfare analytics protected by $k$-anonymity, and a dual-key emergency break-glass vault.

---

## 1. Key Architectural Guarantees

1. **Zero-PII Operational Database**:
   - The operational database **NEVER** stores student real names, registration numbers, admission numbers, student email addresses, raw LMS tokens, or unredacted emergency contact info.
   - Student uniqueness is enforced in-memory via `HMAC-SHA256(reg_no, UNIVERSITY_SALT)`.
2. **Dual-Key Break-Glass Vault**:
   - Emergency contacts are encrypted with AES-256-GCM.
   - The encryption key is split into two independent 2-of-2 secret shares ($S_1 \oplus S_2$).
   - Neither the campus counsellor nor the Dean of Students can decrypt emergency contacts independently. Both must independently authorize the disclosure under an auditable emergency protocol.
3. **Deterministic Clinical Triage Engine**:
   - Uses qualified screening instruments: PHQ-9 (depression), GAD-7 (anxiety), and AUDIT-C (alcohol pattern).
   - **Critical Clinical Rule**: Any positive response to PHQ-9 Item 9 (thoughts of self-harm or suicide) **IMMEDIATELY** triggers `RED_IMMINENT_RISK` and bypasses AI.
   - AI models are strictly prohibited from determining risk tiers or downgrading RED classifications.
4. **K-Anonymous Institutional Analytics ($k \ge 15$)**:
   - Institutional dashboards enforce `COUNT(DISTINCT user_uuid) >= 15`. Cohorts with fewer than 15 distinct students return `{"suppressed": true, "reason": "k-anonymity threshold"}` to prevent differencing attacks.
5. **AI Privacy & Sheng/Swahili PII Redaction**:
   - Text is scrubbed through a PII detection layer before reaching external AI models, replacing names, Kenyan phone numbers, emails, hostels (`hostel ya XYZ`), lecturers (`lecturer John`), and registration numbers with privacy tokens.
6. **PostgreSQL Row-Level Security (RLS)**:
   - Tenant isolation is enforced at the database engine level across all operational tables.

---

## 2. Technology Stack

- **Runtime**: Python 3.12+
- **API Framework**: FastAPI & Starlette
- **ORM & Migrations**: SQLAlchemy 2.0 & Alembic
- **Database**: PostgreSQL 16+ with PostgreSQL Row-Level Security (RLS)
- **Cache & Tasks**: Redis & Celery
- **Cryptography**: `cryptography` (AES-256-GCM), HMAC-SHA256, Argon2id
- **Testing**: Pytest & HTTPX TestClient
- **Containerization**: Docker & Docker Compose

---

## 3. Quickstart with Docker Compose

To start the complete infrastructure (Backend, PostgreSQL, Redis, Celery Worker):

```bash
# 1. Clone or unpack the project
cd hali-backend

# 2. Copy environment file
cp .env.example .env

# 3. Build and launch all services in detached mode
docker compose up -d --build

# 4. View logs
docker compose logs -f backend
```

Once running, access:
- **Interactive OpenAPI Documentation**: [http://localhost:5000/docs](http://localhost:5000/docs)
- **ReDoc API Reference**: [http://localhost:5000/redoc](http://localhost:5000/redoc)
- **Health Check Endpoint**: [http://localhost:5000/api/health](http://localhost:5000/api/health)

---

## 4. Manual Local Setup & Development

### 4.1 Prerequisites
- Python 3.12+
- PostgreSQL 16+
- Redis (optional for worker tasks)

### 4.2 Setup Steps

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env

# 4. Run database migrations
alembic upgrade head

# 5. Seed synthetic Kenyan university data
python3 scripts/seed_kenya_data.py

# 6. Start the development server on port 5000
uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
```

---

## 5. Running the Test Suite

The test suite covers unit, integration, security, and API compatibility tests:

```bash
cd hali-backend
pytest -v
```

### Test Coverage Highlights:
- **Zero-PII Storage**: Verifies that student registration numbers, names, and personal emails never appear in operational tables.
- **Dual-Key Break-Glass Vault**: Verifies that neither counsellor nor dean alone can decrypt emergency contacts, and dual approval successfully reconstructs the key.
- **Deterministic Triage**: Verifies that PHQ-9 Item 9 positive triggers `RED_IMMINENT_RISK` and cannot be downgraded.
- **K-Anonymity Suppression**: Verifies that cohorts of $n < 15$ (e.g. Theology $n=4$, Law $n=7$) are suppressed, while $n \ge 15$ cohorts return aggregate statistics.
- **Multi-Tenant Row-Level Security**: Verifies that University 1 cannot access University 2 records.
- **Sheng/Swahili PII Redaction**: Verifies code-switched text scrubbing.

---

## 6. Directory Structure

```
hali-backend/
├── app/
│   ├── main.py                     # FastAPI application entrypoint & middleware
│   ├── core/
│   │   ├── config.py               # Pydantic v2 application settings
│   │   ├── security.py             # Argon2id, JWT, HMAC-SHA256
│   │   ├── database.py             # SQLAlchemy 2.0 engine & RLS session hooks
│   │   ├── tenant.py               # Transaction-scoped tenant ContextVars
│   │   └── permissions.py          # Role hierarchy & permissions matrix
│   ├── models/                     # Normalized PostgreSQL database models
│   ├── schemas/                    # Pydantic request/response schemas
│   ├── api/                        # Modular API endpoints
│   ├── services/
│   │   ├── break_glass/            # 2-of-2 secret sharing & emergency vault
│   │   ├── triage/                 # PHQ-9, GAD-7, AUDIT-C deterministic engine
│   │   ├── pii_redaction/          # Sheng/Swahili/English PII scrubbing
│   │   ├── ai/                     # Safe AI provider & 4-bullet brief generator
│   │   ├── analytics/              # K-anonymous welfare radar (k >= 15)
│   │   ├── escalation/             # Priority human escalation workflow
│   │   └── notifications/          # Multi-channel notification dispatcher
│   ├── middleware/                 # Tenant & security headers middleware
│   ├── workers/                    # Celery app & background tasks
│   └── utils/                      # Pseudonym generator & helpers
├── alembic/                        # Database migrations & RLS policy setup
├── tests/                          # 39 Unit, integration, security, & API tests
├── scripts/
│   ├── seed_kenya_data.py          # Synthetic Kenyan university data seeder
│   └── setup_rls.sql               # PostgreSQL Row-Level Security setup script
├── docs/                           # Architecture, Threat Model, Database ERD
├── API_CONTRACTS.md                # Complete API contract specification
├── Dockerfile                      # Production multi-stage Docker image
├── docker-compose.yml              # Complete 4-service stack deployment
└── nginx.conf                      # Nginx reverse proxy configuration
```

---

## 7. Clinical Governance & Legal Disclaimer

- **Screening vs Diagnosis**: Hali provides mental health triage and screening support using standardized clinical instruments (PHQ-9, GAD-7, AUDIT-C). It does **NOT** provide medical diagnoses or prescribe medication.
- **Emergency Crisis Service**: Hali is not an emergency response hotline. High-risk presentations are directed to licensed campus counsellors and verified Kenyan national helplines:
  - **Campus Clinic Emergency**: 1199
  - **Kenya Red Cross Toll-Free**: +254 722 178 177
  - **Befrienders Kenya 24/7 Helpline**: 0900 620 800
- **External Dependencies & HSM**: In production environments, the two independent key share boundaries (`COUNSELLOR_CUSTODY_SECRET` and `DEAN_CUSTODY_SECRET`) must be integrated into independent Hardware Security Modules (HSMs) or separate cloud KMS instances with independent multi-factor custody.

