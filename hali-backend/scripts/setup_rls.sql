-- PostgreSQL Row-Level Security (RLS) Setup Script for Hali Backend
-- Enforces tenant isolation at the database engine level.

DO $$
DECLARE
    tbl text;
    tables text[] := ARRAY[
        'users',
        'user_university_hashes',
        'checkins',
        'phq9_assessments',
        'gad7_assessments',
        'auditc_assessments',
        'risk_events',
        'escalations',
        'break_glass_vault',
        'break_glass_requests',
        'counsellor_profiles',
        'counsellor_availability',
        'student_counsellor_assignments',
        'session_notes',
        'ai_case_briefs',
        'bookings',
        'conversations',
        'messages',
        'consent_ledger',
        'audit_logs',
        'notification_events',
        'lms_anomaly_events'
    ];
BEGIN
    FOREACH tbl IN ARRAY tables LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY;', tbl);
        EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY;', tbl);
        EXECUTE format('DROP POLICY IF EXISTS tenant_isolation_%I ON %I;', tbl, tbl);
        EXECUTE format('
            CREATE POLICY tenant_isolation_%I ON %I
            FOR ALL
            USING (
                university_id = NULLIF(current_setting(''app.current_university_id'', true), '''')::uuid
                OR NULLIF(current_setting(''app.current_university_id'', true), '''') IS NULL
            )
            WITH CHECK (
                university_id = NULLIF(current_setting(''app.current_university_id'', true), '''')::uuid
                OR NULLIF(current_setting(''app.current_university_id'', true), '''') IS NULL
            );
        ', tbl, tbl);
    END LOOP;
END
$$;

