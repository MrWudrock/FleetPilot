"""ops UI: maintenance tasks + organization settings

Revision ID: 006
Revises: 005
Create Date: 2026-07-17

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "006"
down_revision: str | Sequence[str] | None = "005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

maintenance_kind = postgresql.ENUM(
    "to",
    "repair",
    "inspection",
    name="maintenance_kind",
    create_type=False,
)
maintenance_status = postgresql.ENUM(
    "planned",
    "overdue",
    "in_progress",
    "done",
    name="maintenance_status",
    create_type=False,
)


def upgrade() -> None:
    maintenance_kind.create(op.get_bind(), checkfirst=True)
    maintenance_status.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "organizations",
        sa.Column(
            "settings",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
    )

    op.create_table(
        "maintenance_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("vehicle_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("kind", maintenance_kind, nullable=False),
        sa.Column("status", maintenance_status, server_default="planned", nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("mileage_km", sa.Float(), nullable=True),
        sa.Column("estimated_cost_rub", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_maintenance_tasks_organization_id"), "maintenance_tasks", ["organization_id"])
    op.create_index(op.f("ix_maintenance_tasks_vehicle_id"), "maintenance_tasks", ["vehicle_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_maintenance_tasks_vehicle_id"), table_name="maintenance_tasks")
    op.drop_index(op.f("ix_maintenance_tasks_organization_id"), table_name="maintenance_tasks")
    op.drop_table("maintenance_tasks")
    op.drop_column("organizations", "settings")
    maintenance_status.drop(op.get_bind(), checkfirst=True)
    maintenance_kind.drop(op.get_bind(), checkfirst=True)
