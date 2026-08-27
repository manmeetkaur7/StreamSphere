from fastapi import HTTPException

from app.core.config import get_settings
from app.core.demo import require_demo_write_access


def test_demo_mode_blocks_destructive_admin_actions(monkeypatch) -> None:
    monkeypatch.setenv("DEMO_MODE", "true")
    get_settings.cache_clear()

    try:
        require_demo_write_access()
    except HTTPException as exc:
        assert exc.status_code == 403
        assert "disabled while demo mode" in str(exc.detail)
    else:
        raise AssertionError("Expected demo mode to block the action.")
    finally:
        get_settings.cache_clear()


def test_non_demo_mode_allows_admin_actions(monkeypatch) -> None:
    monkeypatch.setenv("DEMO_MODE", "false")
    get_settings.cache_clear()

    try:
        require_demo_write_access()
    finally:
        get_settings.cache_clear()
