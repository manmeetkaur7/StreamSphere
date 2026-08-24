"""baseline schema

Revision ID: 20260821_0001
Revises:
Create Date: 2026-08-21 10:00:00
"""

from typing import Sequence

from alembic import op

from app.db.base import Base, register_models

# revision identifiers, used by Alembic.
revision = "20260821_0001"
down_revision = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    register_models()
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    register_models()
    Base.metadata.drop_all(bind=op.get_bind())
