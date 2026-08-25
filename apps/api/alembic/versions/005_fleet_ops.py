"""fleet ops: order details + wialon/transmanager enum values

Revision ID: 005
Revises: 004
Create Date: 2026-07-17

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "005"
down_revision: str | Sequence[str] | None = "004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE integration_provider ADD VALUE IF NOT EXISTS 'wialon'")
    op.execute("ALTER TYPE integration_provider ADD VALUE IF NOT EXISTS 'transmanager'")
    op.add_column(
        "orders",
        sa.Column(
            "details",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("orders", "details")
    # PostgreSQL cannot easily remove enum values
