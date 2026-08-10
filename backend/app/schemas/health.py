from typing import Literal

from pydantic import BaseModel


class HealthDependencyStatus(BaseModel):
    status: Literal["ok", "degraded", "unavailable"]
    backend: str
    detail: str


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded", "unavailable"]
    environment: str
    version: str
    uptime_seconds: int
    database: HealthDependencyStatus
    redis: HealthDependencyStatus
