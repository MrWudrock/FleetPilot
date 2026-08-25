"""analytics tables for ROI dashboard

Revision ID: 003
Revises: 002
Create Date: 2026-06-22

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: str | Sequence[str] | None = "002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

alert_severity = postgresql.ENUM("info", "warning", "critical", name="alert_severity", create_type=False)
order_status = postgresql.ENUM(
    "new", "assigned", "in_transit", "completed", "cancelled", name="order_status", create_type=False
)
savings_category = postgresql.ENUM(
    "fuel", "route", "dispatch", "maintenance", name="savings_category", create_type=False
)


def upgrade() -> None:
    alert_severity.create(op.get_bind(), checkfirst=True)
    order_status.create(op.get_bind(), checkfirst=True)
    savings_category.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "fuel_alerts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("vehicle_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("severity", alert_severity, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("acknowledged", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_fuel_alerts_organization_id"), "fuel_alerts", ["organization_id"], unique=False)
    op.create_index(op.f("ix_fuel_alerts_vehicle_id"), "fuel_alerts", ["vehicle_id"], unique=False)

    op.create_table(
        "orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_ref", sa.String(length=64), nullable=True),
        sa.Column("status", order_status, server_default="new", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_orders_created_at"), "orders", ["created_at"], unique=False)
    op.create_index(op.f("ix_orders_organization_id"), "orders", ["organization_id"], unique=False)

    op.create_table(
        "savings_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category", savings_category, nullable=False),
        sa.Column("amount_rub", sa.Float(), nullable=False),
        sa.Column("period_month", sa.Date(), nullable=False),
        sa.Column("note", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_savings_entries_organization_id"), "savings_entries", ["organization_id"], unique=False)
    op.create_index(op.f("ix_savings_entries_period_month"), "savings_entries", ["period_month"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_savings_entries_period_month"), table_name="savings_entries")
    op.drop_index(op.f("ix_savings_entries_organization_id"), table_name="savings_entries")
    op.drop_table("savings_entries")
    op.drop_index(op.f("ix_orders_organization_id"), table_name="orders")
    op.drop_index(op.f("ix_orders_created_at"), table_name="orders")
    op.drop_table("orders")
    op.drop_index(op.f("ix_fuel_alerts_vehicle_id"), table_name="fuel_alerts")
    op.drop_index(op.f("ix_fuel_alerts_organization_id"), table_name="fuel_alerts")
    op.drop_table("fuel_alerts")

    savings_category.drop(op.get_bind(), checkfirst=True)
    order_status.drop(op.get_bind(), checkfirst=True)
    alert_severity.drop(op.get_bind(), checkfirst=True)
