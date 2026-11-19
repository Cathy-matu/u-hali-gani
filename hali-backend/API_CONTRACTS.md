# Hali Backend API Contracts & Integration Guide

This document defines the REST and WebSocket API contracts for **Hali**, the privacy-first university mental health triage and student welfare operating system.

---

## 1. Authentication & Tenant Identification

Hali uses signed JSON Web Tokens (JWT) using the `HS256` algorithm.

- **Header Format**: `Authorization: Bearer <jwt_token>`
- **Optional Tenant Header**: `X-University-ID: <university_uuid>` (defaults to token claim)
- **Token Claims**:
  ```json
  {
    "sub": "3d6c1b3f-2394-4b55-a22a-89a3118cf945",
    "role": "student",
    "university_id": "11111111-1111-1111-1111-111111111111",
    "anon_handle": "calm-acacia-42",
    "iat": 1732060800,
    "exp": 1732064400,
    "jti": "8f302b1156a02b74"
  }
  ```

---

## 2. Role-Permission Matrix

| Role | Description | Key Permissions |
|---|---|---|
| `student` | Enrolled university student (pseudonymous) | Check-ins, screening, self-booking, messaging counsellor, consent management |
| `counsellor` | Campus counsellor | View priority queue, review briefs, take session notes, initiate break-glass |
| `supervisor` | Senior counsellor / supervisor | Case supervision, counsellor workload oversight |
| `university_admin` | University administrative officer | K-anonymous welfare radar ($k \ge 15$), suppression audit logs |
| `dean_of_students` | Dean of Students | K-anonymous welfare radar ($k \ge 15$), dual-key break-glass second approval |
| `researcher` | Approved academic researcher | De-identified dataset export ($k \ge 15$, active consent only) |
| `super_admin` | Technical operations | Multi-tenant university administration |

---

## 3. Core API Endpoints

### 3.1 LMS Authentication Handshake (Zero-PII)
- **Endpoint**: `POST /api/auth/lms-handshake`
- **Purpose**: Authenticates student via university LMS token without storing registration number.
- **Request Payload**:
  ```json
  {
    "lms_token": "simulated_verified_lms_token_9912",
    "faculty": "Computing",
    "year_of_study": 3
  }
  ```
- **Response Payload (200 OK)**:
  ```json
  {
    "jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user_uuid": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "anon_handle": "calm-acacia-42",
    "role": "student"
  }
  ```

---

### 3.2 Deterministic Screening & Triage
- **Endpoint**: `POST /api/checkins`
- **Purpose**: Evaluates PHQ-9, GAD-7, and AUDIT-C clinical instruments deterministically.
- **Critical Safety Rule**: Any positive response to PHQ-9 Item 9 immediately routes to `RED_IMMINENT_RISK`.
- **Request Payload**:
  ```json
  {
    "user_uuid": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "phq9_scores": [1, 1, 2, 1, 0, 1, 1, 0, 1],
    "gad7_scores": [1, 2, 1, 1, 0, 1, 0],
    "auditc_scores": [1, 0, 0],
    "free_text_or_transcript": "Stress ya exam na hostel ya Qwetu inanilemea."
  }
  ```
- **Response Payload (200 OK)**:
  ```json
  {
    "success": true,
    "message": "Screening assessment processed deterministically",
    "data": {
      "risk_level": "RED",
      "is_item9_positive": true,
      "triggers": ["PHQ-9 Item 9 positive (score: 1) - Imminent Risk"],
      "action": {
        "bypass_ai": true,
        "human_escalation_required": true,
        "clinic_callback": true,
        "display_emergency_contacts": true,
        "crisis_hotlines": [
          {"tier": 0, "name": "Campus Clinic Emergency", "phone": "1199"},
          {"tier": 1, "name": "Kenya Red Cross Toll-Free", "phone": "+254 722 178 177"},
          {"tier": 2, "name": "Befrienders Kenya 24/7 Helpline", "phone": "0900 620 800"}
        ]
      },
      "phq9": {"total_score": 8, "item_9_score": 1, "severity": "Mild"},
      "gad7": {"total_score": 6, "severity": "Mild"},
      "disclaimer": "Screening results only. This is not a clinical diagnosis or medical prescription."
    },
    "risk": "red"
  }
  ```

---

### 3.3 Counsellor Priority Queue
- **Endpoint**: `GET /api/counsellor/queue` (or `GET /api/counsellor/cases`)
- **Headers**: `Authorization: Bearer <counsellor_token>`
- **Response Payload (200 OK)**:
  ```json
  {
    "success": true,
    "data": [
      {
        "id": "Swift-Baobab-208",
        "user_uuid": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
        "anon_handle": "Swift-Baobab-208",
        "risk": "red",
        "trend": "worsening",
        "last": "Today 08:12",
        "phq": [6, 9, 12, 15],
        "gad": [5, 8, 10, 13],
        "status": "Escalated",
        "next": "Today 14:00"
      },
      {
        "id": "Calm-Mango-532",
        "user_uuid": "1b9d6bcd-bbfd-4b2d-9b5d-ab8dfbbd4bed",
        "anon_handle": "Calm-Mango-532",
        "risk": "amber",
        "trend": "worsening",
        "last": "Yesterday",
        "phq": [5, 7, 8, 10],
        "gad": [6, 7, 9, 9],
        "status": "Active",
        "next": "Fri 10:30"
      }
    ]
  }
  ```

---

### 3.4 Institutional Welfare Radar (K-Anonymous)
- **Endpoint**: `GET /api/admin/welfare-radar?faculty=Computing`
- **Rule**: If distinct cohort size is less than 15, response is strictly suppressed.
- **Suppressed Response Payload (Cohort < 15)**:
  ```json
  {
    "suppressed": true,
    "reason": "k-anonymity threshold",
    "cohort_size": null,
    "threshold_required": 15,
    "message": "Data suppressed: distinct cohort size is less than required privacy threshold (k >= 15)."
  }
  ```
- **Allowed Aggregate Response Payload (Cohort >= 15)**:
  ```json
  {
    "suppressed": false,
    "cohort_size": 45,
    "enrolled_students": 180,
    "registered_users": 45,
    "total_checkins": 210,
    "bookings_count": 34,
    "avg_phq9": 6.2,
    "avg_gad7": 5.6,
    "risk_distribution": [
      {"name": "Green", "value": 71.0, "fill": "#2F855A"},
      {"name": "Amber", "value": 22.0, "fill": "#B7791F"},
      {"name": "Red", "value": 7.0, "fill": "#C0504D"}
    ],
    "departments": [
      {"name": "Computer Science", "n": 45, "suppressed": false}
    ]
  }
  ```

---

### 3.5 Dual-Key Break-Glass Emergency Disclosure
1. **Initiate Request (Counsellor)**:
   - `POST /api/emergency/break-glass/request`
   - Request:
     ```json
     {
       "user_uuid": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
       "reason": "Imminent self-harm risk communicated; student unresponsive to emergency outreach",
       "escalation_case_id": "99b03940-1284-482a-bc91-209bf18df819"
     }
     ```
   - Response: `{"status": "PENDING_APPROVAL", "request_id": "req_8812a"}`

2. **Approve Request (Dean of Students)**:
   - `POST /api/emergency/break-glass/{request_id}/approve`
   - Reconstructs 2-of-2 secret shares: $K = S_{\text{counsellor}} \oplus S_{\text{dean}}$
   - Response:
     ```json
     {
       "success": true,
       "data": {
         "status": "APPROVED_DECRYPTED",
         "decrypted_contact": {
           "contact_name": "Mrs. Faith Kimani",
           "relationship": "Mother",
           "phone": "+254 722 334 455",
           "notes": "Emergency family contact in Eldoret"
         }
       }
     }
     ```

---

### 3.6 PII Redaction Endpoint
- **Endpoint**: `POST /api/privacy/redact`
- **Request**:
  ```json
  {
    "text": "Nilikuwa hostel ya XYZ na lecturer John alisema nipigie Kamau kwa 0722123456."
  }
  ```
- **Response**:
  ```json
  {
    "redacted_text": "Nilikuwa [HOSTEL] na [LECTURER] alisema nipigie [PERSON] kwa [PHONE].",
    "redaction_count": 4,
    "redaction_applied": true
  }
  ```

---

### 3.7 LMS Anomaly Webhook
- **Endpoint**: `POST /api/webhooks/lms-anomaly`
- **Header**: `X-LMS-Signature: sha256=<hmac>`
- **Request**:
  ```json
  {
    "user_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "anomaly_type": "LOGIN_DROP",
    "severity": "MEDIUM"
  }
  ```
- **Response**: `{"success": true, "processed": true}`

