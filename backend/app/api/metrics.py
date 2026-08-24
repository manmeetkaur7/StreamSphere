from fastapi import APIRouter

from app.services.metrics import get_metrics_registry

router = APIRouter(tags=["health"])


@router.get("/metrics", summary="Read lightweight application metrics")
def get_metrics() -> dict[str, float | int]:
    return get_metrics_registry().snapshot()
