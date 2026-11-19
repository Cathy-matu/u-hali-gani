from typing import Generator
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.config import settings
from app.core.tenant import get_current_tenant_id

# Engine configuration
engine_kwargs = {
    "echo": False,
    "pool_pre_ping": True,
}

if "sqlite" not in settings.DATABASE_URL:
    engine_kwargs.update({
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
    })

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

Base = declarative_base()


def set_rls_tenant_context(db: Session, university_id: str) -> None:
    """Set transaction-local PostgreSQL RLS context variable."""
    if not university_id:
        return
    if "postgresql" in str(db.bind.url):
        try:
            # Safe parameterized execution for transaction-local setting
            db.execute(text("SELECT set_config('app.current_university_id', :uid, true)"), {"uid": str(university_id)})
        except Exception:
            pass


def get_db() -> Generator[Session, None, None]:
    """FastAPI database session dependency with tenant context enforcement."""
    db = SessionLocal()
    try:
        tenant_id = get_current_tenant_id()
        if tenant_id:
            set_rls_tenant_context(db, tenant_id)
        yield db
    finally:
        db.close()

