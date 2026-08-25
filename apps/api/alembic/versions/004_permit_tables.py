"""permit agent tables

Revision ID: 004
Revises: 003
Create Date: 2026-06-23

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "004"
down_revision: str | Sequence[str] | None = "003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

permit_request_status = postgresql.ENUM(
    "draft",
    "analyzing",
    "ready",
    "approved",
    "submitted",
    "rejected",
    name="permit_request_status",
    create_type=False,
)


def upgrade() -> None:
    op.execute("ALTER TYPE integration_provider ADD VALUE IF NOT EXISTS 'rosdor_monitoring'")
    op.execute("ALTER TYPE savings_category ADD VALUE IF NOT EXISTS 'permit'")

    permit_request_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "permit_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("vehicle_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("origin", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("destination", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("waypoints", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("cargo", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("status", permit_request_status, server_default="draft", nullable=False),
        sa.Column("analysis", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("risk_score", sa.Float(), nullable=True),
        sa.Column("external_permit_number", sa.String(length=64), nullable=True),
        sa.Column("dispatcher_notes", sa.Text(), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["approved_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_permit_requests_created_at"), "permit_requests", ["created_at"], unique=False)
    op.create_index(op.f("ix_permit_requests_order_id"), "permit_requests", ["order_id"], unique=False)
    op.create_index(op.f("ix_permit_requests_organization_id"), "permit_requests", ["organization_id"], unique=False)
    op.create_index(op.f("ix_permit_requests_vehicle_id"), "permit_requests", ["vehicle_id"], unique=False)

    op.create_table(
        "permit_audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("permit_request_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("provider", sa.String(length=64), server_default="fleetpilot", nullable=False),
        sa.Column("request_payload", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("response_summary", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["permit_request_id"], ["permit_requests.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_permit_audit_logs_created_at"), "permit_audit_logs", ["created_at"], unique=False)
    op.create_index(op.f("ix_permit_audit_logs_organization_id"), "permit_audit_logs", ["organization_id"], unique=False)
    op.create_index(op.f("ix_permit_audit_logs_permit_request_id"), "permit_audit_logs", ["permit_request_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_permit_audit_logs_permit_request_id"), table_name="permit_audit_logs")
    op.drop_index(op.f("ix_permit_audit_logs_organization_id"), table_name="permit_audit_logs")
    op.drop_index(op.f("ix_permit_audit_logs_created_at"), table_name="permit_audit_logs")
    op.drop_table("permit_audit_logs")
    op.drop_index(op.f("ix_permit_requests_vehicle_id"), table_name="permit_requests")
    op.drop_index(op.f("ix_permit_requests_organization_id"), table_name="permit_requests")
    op.drop_index(op.f("ix_permit_requests_order_id"), table_name="permit_requests")
    op.drop_index(op.f("ix_permit_requests_created_at"), table_name="permit_requests")
    op.drop_table("permit_requests")
    permit_request_status.drop(op.get_bind(), checkfirst=True)
