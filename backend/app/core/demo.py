from fastapi import HTTPException, status

from app.core.config import get_settings


def require_demo_write_access() -> None:
    """Keep public demo environments safe from irreversible admin actions."""
    if get_settings().demo_mode:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This administrative action is disabled while demo mode is enabled.",
        )
