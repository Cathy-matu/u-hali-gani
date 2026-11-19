# Hali Threat Model & Security Architecture

## 1. Threat Modeling Methodology

This threat model uses the **STRIDE** methodology (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) evaluated against university health and LMS integration scenarios in Kenya.

---

## 2. Attack Surfaces and Mitigations

### 2.1 Spoofing (Student Identity & LMS Tokens)
- **Threat**: An attacker attempts to forge LMS tokens to access another student's mental health check-ins or submit malicious screening data.
- **Mitigation**:
  - LMS tokens are cryptographically verified against the university's public keys / LMS secret before processing.
  - The LMS handshake validates token signature, expiration, issuer, and university context.
  - Client-supplied demographic fields (`faculty`, `year_of_study`) are rejected if not corroborated by verified token claims.

### 2.2 Information Disclosure (Database Breach & PII Exfiltration)
- **Threat**: An attacker dumps the operational database and attempts to identify students seeking mental health counselling or dean-level disciplinary cases.
- **Mitigation**:
  - **Zero-PII Architecture**: The operational database contains zero student real names, zero registration numbers, zero student admission numbers, and zero student email addresses.
  - **Keyed HMAC Digest**: Student uniqueness is enforced via `HMAC-SHA256(reg_no, UNIVERSITY_SALT)`. Without the university-specific salt (stored in HSM / secret manager), raw registration numbers cannot be reversed from the database dump.
  - **Dual-Key Break-Glass Vault**: Emergency contacts are encrypted with AES-256-GCM. The encryption key is split into two independent 2-of-2 secret shares stored in distinct key custody boundaries. Dumping the database reveals only ciphertext, nonce, and authentication tag.

### 2.3 Information Disclosure (Differencing Attacks on Institutional Analytics)
- **Threat**: A university administrator or departmental head queries aggregate reports with overlapping filters (e.g. comparing Department of Law Year 4 before and after a specific student's check-in) to reconstruct individual student mental health scores.
- **Mitigation**:
  - **Strict K-Anonymity ($k \ge 15$)**: The database query strictly applies `HAVING COUNT(DISTINCT user_uuid) >= 15`. Any cohort with fewer than 15 distinct students returns `{"suppressed": true, "reason": "k-anonymity threshold"}`.
  - **Complementary Cell Suppression**: When small departmental cells exist, individual cell counts are suppressed to prevent subtraction from faculty totals.
  - **Query Audit Logging**: All aggregate queries, including applied filters and suppression triggers, are immutably logged in `audit_logs`.

### 2.4 Elevation of Privilege (Insider Threat / Rogue Counsellor or Administrator)
- **Threat**: A rogue counsellor attempts to unmask a student's emergency contact, or a rogue dean attempts to bypass clinical governance.
- **Mitigation**:
  - **Threshold Dual-Key Access**: Decryption of `break_glass_vault` requires two cryptographic shares ($S_1 \oplus S_2$). Neither counsellor nor dean can decrypt independently.
  - **Strict Separation of Custody**: Requester UUID cannot equal Approver UUID. Self-approval is rejected by cryptographic and business logic checks.
  - **Immutable Audit Logging**: Every break-glass initiation, approval, failed attempt, and denial creates an immutable record in `audit_logs`.

### 2.5 Tampering & Cross-Tenant Data Leakage
- **Threat**: A tenant administrator from University A attempts to query or tamper with data belonging to University B.
- **Mitigation**:
  - **PostgreSQL Row-Level Security (RLS)**: Enforced directly in PostgreSQL engine via `ALTER TABLE ... FORCE ROW LEVEL SECURITY`. Every operational record has a `university_id` foreign key.
  - **Transaction-Scoped Tenant Context**: Every query sets `app.current_university_id` on the database session. Queries attempting to read across tenant boundaries return 0 rows.
  - **Non-Bypass Application Role**: The application connects using a restricted PostgreSQL role (`hali_app`) without `BYPASSRLS` privileges.

### 2.6 AI Therapy Boundary & Hallucination Threat
- **Threat**: An LLM generates inaccurate clinical diagnoses, recommends medication changes, or downgrades a severe suicidal risk to a routine coping exercise.
- **Mitigation**:
  - **Deterministic Clinical Triage Engine**: Scoring and risk classification are strictly deterministic (PHQ-9, GAD-7, AUDIT-C). LLMs are forbidden from classifying risk tiers or downgrading classifications.
  - **Critical PHQ-9 Item 9 Rule**: Any positive score on Item 9 (thoughts of self-harm or suicide) automatically triggers `RED_IMMINENT_RISK` and bypasses AI completely.
  - **Pre-Processing PII Redaction**: All text is sanitized through `PIIRedactor` before reaching any AI provider. Personal names, Kenyan phone numbers, emails, hostels, lecturers, and registration numbers are replaced with privacy tokens.

