from typing import Generator, Optional, List
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db, set_rls_tenant_context
from app.core.security import decode_access_token
from app.core.tenant import set_current_tenant_id, set_current_user_context
from app.core.permissions import UserRole, check_permission
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user_optional(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
    x_university_id: Optional[str] = Header(None)
) -> Optional[User]:
    """Retrieve user if token is present, otherwise return None."""
    if not auth:
        if x_university_id:
            set_current_tenant_id(x_university_id)
            set_rls_tenant_context(db, x_university_id)
        return None

    try:
        payload = decode_access_token(auth.credentials)
        user_uuid = payload.get("sub")
        role = payload.get("role")
        university_id = payload.get("university_id") or x_university_id

        if not user_uuid or not university_id:
            return None

        set_current_tenant_id(university_id)
        set_current_user_context(user_uuid, role)
        set_rls_tenant_context(db, university_id)

        user = db.query(User).filter(User.id == user_uuid).first()
        return user
    except Exception:
        return None


def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
    x_university_id: Optional[str] = Header(None)
) -> User:
    """Validate bearer JWT and return current user."""
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        payload = decode_access_token(auth.credentials)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_uuid = payload.get("sub")
    role = payload.get("role")
    university_id = payload.get("university_id") or x_university_id

    if not user_uuid or not university_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing required tenant or identity claims"
        )

    # Establish tenant context for RLS
    set_current_tenant_id(university_id)
    set_current_user_context(user_uuid, role)
    set_rls_tenant_context(db, university_id)

    user = db.query(User).filter(User.id == user_uuid).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account inactive or not found"
        )

    return user


def require_roles(allowed_roles: List[UserRole]):
    """Role-based access dependency."""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if not check_permission(current_user.role, allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role}' is not authorized for this resource"
            )
        return current_user
    return role_checker

