from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.tenant import set_current_tenant_id, clear_tenant_context
from app.core.security import decode_access_token
from app.core.config import settings


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware that establishes tenant context for the request lifecycle.
    Extracts university context from authorization JWT or X-University-ID header.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            # 1. Check Authorization Bearer Token
            auth_header = request.headers.get("Authorization")
            tenant_id = None

            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                try:
                    payload = decode_access_token(token)
                    tenant_id = payload.get("university_id")
                except Exception:
                    pass

            # 2. Check X-University-ID header if not found in token
            if not tenant_id:
                tenant_id = request.headers.get("X-University-ID") or settings.DEFAULT_UNIVERSITY_ID

            set_current_tenant_id(tenant_id)

            response = await call_next(request)
            return response
        finally:
            clear_tenant_context()

