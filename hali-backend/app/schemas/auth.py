from typing import Optional
from pydantic import BaseModel, Field


class LMSHandshakeRequest(BaseModel):
    lms_token: str = Field(..., description="Simulated or verified LMS token containing student context")
    faculty: Optional[str] = Field(None, description="Faculty (verified against token claim in production)")
    year_of_study: Optional[int] = Field(None, description="Year of study (verified against token claim)")
    university_id: Optional[str] = Field(None, description="Target university UUID context")


class LMSHandshakeResponse(BaseModel):
    jwt: str
    user_uuid: str
    anon_handle: str
    role: str = "student"


class LoginRequest(BaseModel):
    role: Optional[str] = "student"
    email: Optional[str] = None
    password: Optional[str] = None
    university_id: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_uuid: str
    anon_handle: Optional[str] = None
    role: str
    university_id: str

