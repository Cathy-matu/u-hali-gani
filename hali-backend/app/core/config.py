import json
from typing import Dict, List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PROJECT_NAME: str = "Hali University Wellness OS"
    API_V1_PREFIX: str = "/api"
    PORT: int = 5000
    HOST: str = "0.0.0.0"

    # Security & Tokens
    SECRET_KEY: str = "insecure_dev_jwt_secret_key_change_in_production_please_min_32_bytes"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Operational Database
    DATABASE_URL: str = "postgresql://hali_app:hali_secure_app_password@/hali_db?host=/tmp&port=54329"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_ENABLE_RLS: bool = True

    # Redis & Celery
    REDIS_URL: str = "unix:///tmp/redis.sock?db=0"
    CELERY_BROKER_URL: str = "redis+socket:///tmp/redis.sock"
    CELERY_RESULT_BACKEND: str = "redis+socket:///tmp/redis.sock"

    # Multi-Tenancy & University Hashing Salts
    DEFAULT_UNIVERSITY_ID: str = "11111111-1111-1111-1111-111111111111"
    UNIVERSITY_SALTS_JSON: str = '{"11111111-1111-1111-1111-111111111111": "kenya_tu_super_secret_salt_2026_x7a", "22222222-2222-2222-2222-222222222222": "nairobi_rv_super_secret_salt_2026_q9b"}'

    # LMS Webhook
    LMS_WEBHOOK_SECRET: str = "whsec_kenya_lms_anomaly_verified_secret_key_992"

    # Dual-Key Break-Glass Custody Secrets
    COUNSELLOR_CUSTODY_SECRET: str = "counsellor_custody_master_key_share_boundary_sec_1"
    DEAN_CUSTODY_SECRET: str = "dean_admin_custody_master_key_share_boundary_sec_2"

    # Crisis Hotlines
    KENYA_CRISIS_HOTLINES: str = json.dumps([
        {"tier": 0, "name": "Campus Clinic Emergency", "phone": "1199"},
        {"tier": 1, "name": "Kenya Red Cross Toll-Free", "phone": "+254 722 178 177"},
        {"tier": 2, "name": "Befrienders Kenya 24/7 Helpline", "phone": "0900 620 800"}
    ])

    # AI Integration
    AI_PROVIDER: str = "mock"  # "mock", "openai", "gemini", "claude"
    AI_API_KEY: Optional[str] = None
    AI_MODEL_NAME: str = "mock-hali-ai"

    # K-Anonymity
    K_ANONYMITY_THRESHOLD: int = 15

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "*"]

    def get_university_salts(self) -> Dict[str, str]:
        try:
            return json.loads(self.UNIVERSITY_SALTS_JSON)
        except Exception:
            return {self.DEFAULT_UNIVERSITY_ID: "default_salt_do_not_use_in_prod"}

    def get_crisis_hotlines(self) -> List[dict]:
        try:
            return json.loads(self.KENYA_CRISIS_HOTLINES)
        except Exception:
            return [
                {"tier": 0, "name": "Campus Clinic", "phone": "1199"},
                {"tier": 1, "name": "Red Cross", "phone": "+254 722 178 177"},
                {"tier": 2, "name": "Befrienders Kenya", "phone": "0900 620 800"}
            ]


settings = Settings()

