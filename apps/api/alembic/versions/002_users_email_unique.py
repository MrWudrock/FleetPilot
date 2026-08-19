"""global unique email for login

Revision ID: 002
Revises: 001
Create Date: 2026-06-22

"""

from collections.abc import Sequence

from alembic import op

revision: str = "002"
down_revision: str | Sequence[str] | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint("uq_users_org_email", "users", type_="unique")
    op.create_index("ix_users_email_unique", "users", ["email"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_email_unique", table_name="users")
    op.create_unique_constraint("uq_users_org_email", "users", ["organization_id", "email"])
