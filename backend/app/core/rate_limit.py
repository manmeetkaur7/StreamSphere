from fastapi import Request

from app.core.config import get_settings
from app.core.errors import error_response
from app.services.cache import get_rate_limit_service


async def rate_limit_middleware(request: Request, call_next):
    settings = get_settings()
    if not settings.rate_limit_enabled or request.url.path in settings.rate_limit_exempt_paths:
        return await call_next(request)

    identifier = request.client.host if request.client else "unknown"
    key = f"rate-limit:{identifier}:{request.url.path}"
    current_count = get_rate_limit_service().hit(key, settings.rate_limit_window_seconds)

    if current_count > settings.rate_limit_requests:
        response = error_response(
            request,
            status_code=429,
            code="rate_limited",
            message="Rate limit exceeded. Please retry shortly.",
        )
        response.headers["X-RateLimit-Limit"] = str(settings.rate_limit_requests)
        response.headers["X-RateLimit-Remaining"] = "0"
        response.headers["Retry-After"] = str(settings.rate_limit_window_seconds)
        return response

    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(settings.rate_limit_requests)
    response.headers["X-RateLimit-Remaining"] = str(
        max(settings.rate_limit_requests - current_count, 0)
    )
    return response
