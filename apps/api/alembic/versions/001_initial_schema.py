"""initial schema v1

Revision ID: 001
Revises:
Create Date: 2026-06-22

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

user_role = postgresql.ENUM(
    "admin",
    "dispatcher",
    "fleet_manager",
    "driver",
    "viewer",
    name="user_role",
    create_type=False,
)
vehicle_status = postgresql.ENUM(
    "active",
    "inactive",
    "maintenance",
    name="vehicle_status",
    create_type=False,
)
integration_provider = postgresql.ENUM(
    "omnicomm",
    "stavtrack",
    "mss_glonass",
    "master_tms",
    name="integration_provider",
    create_type=False,
)
integration_status = postgresql.ENUM(
    "pending",
    "active",
    "error",
    "disabled",
    name="integration_status",
    create_type=False,
)


def upgrade() -> None:
    user_role.create(op.get_bind(), checkfirst=True)
    vehicle_status.create(op.get_bind(), checkfirst=True)
    integration_provider.create(op.get_bind(), checkfirst=True)
    integration_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_organizations_slug"), "organizations", ["slug"], unique=True)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("role", user_role, server_default="viewer", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "email", name="uq_users_org_email"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=False)
    op.create_index(op.f("ix_users_organization_id"), "users", ["organization_id"], unique=False)

    op.create_table(
        "vehicles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("plate", sa.String(length=16), nullable=False),
        sa.Column("external_ids", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("capacity_kg", sa.Float(), nullable=True),
        sa.Column("brand", sa.String(length=100), nullable=True),
        sa.Column("model", sa.String(length=100), nullable=True),
        sa.Column("status", vehicle_status, server_default="active", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "plate", name="uq_vehicles_org_plate"),
    )
    op.create_index(op.f("ix_vehicles_organization_id"), "vehicles", ["organization_id"], unique=False)

    op.create_table(
        "integrations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", integration_provider, nullable=False),
        sa.Column("credentials_enc", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("status", integration_status, server_default="pending", nullable=False),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "provider", name="uq_integrations_org_provider"),
    )
    op.create_index(op.f("ix_integrations_organization_id"), "integrations", ["organization_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_integrations_organization_id"), table_name="integrations")
    op.drop_table("integrations")
    op.drop_index(op.f("ix_vehicles_organization_id"), table_name="vehicles")
    op.drop_table("vehicles")
    op.drop_index(op.f("ix_users_organization_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_organizations_slug"), table_name="organizations")
    op.drop_table("organizations")

    integration_status.drop(op.get_bind(), checkfirst=True)
    integration_provider.drop(op.get_bind(), checkfirst=True)
    vehicle_status.drop(op.get_bind(), checkfirst=True)
    user_role.drop(op.get_bind(), checkfirst=True)
