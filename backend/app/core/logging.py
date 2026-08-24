import json
import logging
import sys
from time import perf_counter
from uuid import uuid4

from fastapi import Request

from app.core.config import get_settings
from app.services.metrics import get_metrics_registry


def configure_logging() -> None:
    settings = get_settings()
    root_logger = logging.getLogger()
    if root_logger.handlers:
        root_logger.setLevel(settings.log_level)
        return

    logging.basicConfig(
        level=settings.log_level,
        format="%(message)s",
        stream=sys.stdout,
    )


async def structured_logging_middleware(request: Request, call_next):
    settings = get_settings()
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    request.state.request_id = request_id
    started_at = perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception:
        duration_ms = round((perf_counter() - started_at) * 1000, 2)
        get_metrics_registry().observe_latency(duration_ms)
        get_metrics_registry().increment("http.requests.errors")
        raise

    duration_ms = round((perf_counter() - started_at) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    get_metrics_registry().observe_latency(duration_ms)
    if status_code >= 400:
        get_metrics_registry().increment("http.requests.errors")

    if settings.structured_logging_enabled:
        logging.getLogger("streamsphere.request").info(
            json.dumps(
                {
                    "event": "http_request",
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "client_ip": request.client.host if request.client else "unknown",
                }
            )
        )

    return response
