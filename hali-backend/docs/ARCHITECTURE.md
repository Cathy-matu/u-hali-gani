# Hali Architecture & System Design

Hali is a privacy-first university mental health triage and student welfare operating system designed for deployment within university e-Learning portals (LMS) in Kenya.

---

## 1. Zero-PII Authentication Handshake Pipeline

```mermaid
sequenceDiagram
    autonumber
    actor Student
    participant LMS as University LMS Portal
    participant Handshake as POST /api/auth/lms-handshake
    participant Memory as Volatile In-Memory Processor
    participant DB as Operational Database (Zero-PII)

    Student->>LMS: Login to University Portal
    LMS->>Handshake: Launch Hali with signed LMS Token
    Handshake->>Memory: Validate token signature, claims & expiration
    Memory->>Memory: Extract Student Reg No in volatile RAM only
    Memory->>Memory: Compute HMAC-SHA256(reg_no, UNIVERSITY_SALT)
    Memory->>Memory: Discard raw LMS token & Reg No
    Memory->>DB: Query or create UserUniversityHash(user_hash)
    DB-->>Memory: Return pseudonymous student (e.g. calm-acacia-42)
    Memory-->>Student: Issue signed session JWT (Pseudonym only)
```

---

## 2. Dual-Key Break-Glass Vault Architecture

```mermaid
flowchart TD
    subgraph Enrollment["Emergency Contact Enrollment"]
        ContactData["Student Optional Emergency Contact"]
        GenKey["Generate 256-bit AES Key (K)"]
        Split["2-of-2 Secret Split: K = S1 ⊕ S2"]
        AES["Encrypt Contact Data with AES-256-GCM (K)"]
        VaultDB[("break_glass_vault Table<br/>(Ciphertext, Nonce, Tag, Ref IDs)")]
        CounsellorCustody[("Counsellor Key Custody Boundary<br/>(Protected S1)")]
        DeanCustody[("Dean Admin Key Custody Boundary<br/>(Protected S2)")]

        ContactData --> GenKey
        GenKey --> Split
        GenKey --> AES
        AES --> VaultDB
        Split -->|Share 1| CounsellorCustody
        Split -->|Share 2| DeanCustody
    end

    subgraph EmergencyFlow["Dual-Authorization Emergency Disclosure"]
        CounsellorReq["1. Counsellor Initiates Request<br/>(Clinical Justification)"]
        DeanApprove["2. Dean of Students Reviews & Approves"]
        Reconstruct["3. Reconstruct K = S1 ⊕ S2"]
        Decrypt["4. Decrypt AES-256-GCM & Verify Tag"]
        AuditLog[("Immutable Audit Log<br/>(Timestamp, Approvers, Outcome)")]
        DisclosedView["Emergency Contact Displayed to Authorized Clinic"]

        CounsellorReq --> DeanApprove
        DeanApprove --> Reconstruct
        CounsellorCustody -.->|Retrieve S1| Reconstruct
        DeanCustody -.->|Retrieve S2| Reconstruct
        VaultDB -.->|Fetch Ciphertext| Decrypt
        Reconstruct --> Decrypt
        Decrypt --> AuditLog
        Decrypt --> DisclosedView
    end
```

---

## 3. Deterministic Triage State Machine

```mermaid
stateDiagram-v2
    [*] --> SubmittedScreening: POST /api/checkins
    SubmittedScreening --> Item9Check: Evaluate PHQ-9 Item 9
    
    Item9Check --> RED_IMMINENT_RISK: Item 9 > 0 (Positive)
    Item9Check --> ScoreEvaluation: Item 9 == 0

    ScoreEvaluation --> RED_IMMINENT_RISK: PHQ-9 >= 15 OR GAD-7 >= 15
    ScoreEvaluation --> AMBER_MODERATE: PHQ-9 >= 10 OR GAD-7 >= 10 OR AUDIT-C >= 4
    ScoreEvaluation --> GREEN_ROUTINE: All scores sub-threshold

    state RED_IMMINENT_RISK {
        [*] --> BypassAI
        BypassAI --> ClinicCallbackWorkflow
        ClinicCallbackWorkflow --> DisplayKenyanHotlines
        DisplayKenyanHotlines --> HighPriorityCounsellorQueue
    }

    state AMBER_MODERATE {
        [*] --> RecommendHumanCounsellor
        RecommendHumanCounsellor --> QueueForFollowup
    }

    state GREEN_ROUTINE {
        [*] --> PsychoeducationalResources
        PsychoeducationalResources --> SelfGuidedCheckins
    }
```

---

## 4. Multi-Tenant Row-Level Security (RLS)

All 22 operational tables in Hali enforce PostgreSQL Row-Level Security:
- `university_id` is mandatory and foreign-keyed to `universities.id`.
- The application executes `SELECT set_config('app.current_university_id', :uid, true)` per database transaction.
- Rows where `university_id != app.current_university_id` are invisible to SQL queries, even if application code omits an explicit tenant filter.
- Connection role `hali_app` does not have `BYPASSRLS` privileges.

