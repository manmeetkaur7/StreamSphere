from fastapi import Request

from app.core.config import get_settings


async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    settings = get_settings()
    if not settings.security_headers_enabled:
        return response

    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Content-Security-Policy", settings.content_security_policy)
    return response
