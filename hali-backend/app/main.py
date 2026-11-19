from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.middleware.tenant import TenantMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware

# Import routers
from app.api.auth.routes import router as auth_router
from app.api.student.routes import router as student_router
from app.api.checkins.routes import router as checkins_router
from app.api.counsellor.routes import router as counsellor_router
from app.api.admin.routes import router as admin_router
from app.api.research.routes import router as research_router
from app.api.emergency.routes import router as emergency_router
from app.api.consent.routes import router as consent_router
from app.api.bookings.routes import router as bookings_router
from app.api.messages.routes import router as messages_router
from app.api.privacy.routes import router as privacy_router
from app.api.webhooks.routes import router as webhooks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    yield
    # Shutdown actions


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Privacy-First University Mental Health Triage & Student Welfare Operating System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 1. CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Custom Security & Tenancy Middlewares
app.add_middleware(TenantMiddleware)
app.add_middleware(SecurityHeadersMiddleware)


# Health check
@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "hali-backend",
        "environment": settings.ENVIRONMENT,
        "zero_pii_enforced": True,
        "k_anonymity_threshold": settings.K_ANONYMITY_THRESHOLD
    }


# Include Routers
app.include_router(auth_router, prefix="/api")
app.include_router(student_router)
app.include_router(checkins_router)
app.include_router(counsellor_router)
app.include_router(admin_router)
app.include_router(research_router)
app.include_router(emergency_router)
app.include_router(consent_router)
app.include_router(bookings_router)
app.include_router(messages_router)
app.include_router(privacy_router)
app.include_router(webhooks_router)

