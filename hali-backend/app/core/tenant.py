import uuid
from contextvars import ContextVar
from typing import Optional

# Thread-local / Asyncio ContextVar for tenant isolation
_current_tenant_id: ContextVar[Optional[str]] = ContextVar("current_tenant_id", default=None)
_current_user_id: ContextVar[Optional[str]] = ContextVar("current_user_id", default=None)
_current_role: ContextVar[Optional[str]] = ContextVar("current_role", default=None)


def set_current_tenant_id(tenant_id: Optional[str]) -> None:
    """Set the active tenant context."""
    if tenant_id:
        # Validate UUID format
        try:
            uuid.UUID(str(tenant_id))
        except ValueError:
            raise ValueError(f"Invalid tenant UUID format: {tenant_id}")
    _current_tenant_id.set(str(tenant_id) if tenant_id else None)


def get_current_tenant_id() -> Optional[str]:
    """Retrieve the active tenant ID from context."""
    return _current_tenant_id.get()


def set_current_user_context(user_id: Optional[str], role: Optional[str]) -> None:
    """Set current user and role context."""
    _current_user_id.set(str(user_id) if user_id else None)
    _current_role.set(str(role) if role else None)


def get_current_user_id() -> Optional[str]:
    return _current_user_id.get()


def get_current_role() -> Optional[str]:
    return _current_role.get()


def clear_tenant_context() -> None:
    """Clear all context variables."""
    _current_tenant_id.set(None)
    _current_user_id.set(None)
    _current_role.set(None)

