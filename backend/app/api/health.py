from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.health import HealthResponse
from app.services.health_service import application_health

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Check API health and dependencies",
    description=(
        "Reports application status, PostgreSQL connectivity, Redis/cache status, "
        "uptime, deployment environment, and the running API version."
    ),
    responses={
        200: {"description": "Application is healthy or degraded with an active fallback."},
        503: {"description": "A required dependency such as the database is unavailable."},
    },
)
def health_check(
    response: Response,
    db: Session = Depends(get_db),
) -> HealthResponse:
    payload = application_health(db)
    if payload["status"] == "unavailable":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return HealthResponse.model_validate(payload)
